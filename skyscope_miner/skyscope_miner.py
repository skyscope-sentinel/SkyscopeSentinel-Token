#!/usr/bin/env python3

import argparse
import time
import sys
import os
import threading
import signal
import logging

# Project module imports
try:
    from . import core_utils
    from .kaspa_connector import KaspaConnector, KaspaNodeError, KaspaBlockSubmissionError
    from .hashing_logic import SkyscopeHashQ
    from .display_manager import DisplayManager
    from .rewards_manager import RewardsManager
except ImportError:
    # Fallback for direct execution if modules are not found in current path
    # print("Warning: Relative import failed. Attempting import assuming script is in project root or skyscope_miner is in PYTHONPATH.")
    import core_utils
    from kaspa_connector import KaspaConnector, KaspaNodeError, KaspaBlockSubmissionError
    from hashing_logic import SkyscopeHashQ
    from display_manager import DisplayManager
    from rewards_manager import RewardsManager

# --- Constants ---
# This is a placeholder. Actual Kaspa block reward varies and is complex to determine without full node logic.
# For solo mining, the miner gets the full block reward + transaction fees found in the block.
# The GetBlockTemplate response *should* provide enough info to calculate it, or the coinbase tx.
# For now, we simulate a fixed reward when a block is "found" by our Python hasher.
CONCEPTUAL_KAS_BLOCK_REWARD = 100.0

# --- Logging Setup ---
logger = logging.getLogger(__name__) # Use __name__ for module-level logger

# --- Global state for graceful shutdown ---
shutdown_event = threading.Event()

def signal_handler(sig, frame):
    """Handles Ctrl+C and other termination signals for graceful shutdown."""
    logger.info("Termination signal received. Initiating graceful shutdown...")
    shutdown_event.set()

def print_header():
    """Prints the miner header."""
    bright_cyan = "\033[96m"
    yellow = "\033[93m"
    reset_color = "\033[0m"
    header = f"""
{bright_cyan}===================================================================={reset_color}
          {bright_cyan}SKYSCOPE KASPA MINER - v0.2.0 (Python Edition){reset_color}
{bright_cyan}===================================================================={reset_color}
  {yellow}Project by: Miss Casey Jay Topojani, Skyscope Sentinel Intelligence{reset_color}
  {yellow}ABN: 11287984779 | Email: skyscopesentinel@gmail.com{reset_color}
  {yellow}GitHub: https://github.com/skyscope-sentinel{reset_color} (Conceptual)
{bright_cyan}--------------------------------------------------------------------{reset_color}"""
    print(header)

def print_config(args, cpu_info_dict, ram_info_dict, conceptual_ram_alloc_info, kaspad_resolved_url):
    """Prints the effective mining configuration."""
    bright_cyan = "\033[96m"
    reset_color = "\033[0m"
    config_str = f"""
  Mining Configuration:
  ---------------------
  Kaspa Wallet (User):    {args.kaspa_address}
  Kaspad Node URL:        {args.node_url if args.node_url else f"Auto-Detect (Using: {kaspad_resolved_url if kaspad_resolved_url else 'Not Detected Yet'})"}
  CPU Cores Detected:     {cpu_info_dict['total_cores_detected']}
  CPU Cores To Use:       {cpu_info_dict['cores_to_use']}
  RAM for skyscope-hash-Q: {args.ram_percent}% (Conceptual: {conceptual_ram_alloc_info.get('allocated_gb_conceptual',0):.2f} GB)

  Fee & Allocation:
  -----------------
  Dev Fee (10%) Address:  {args.dev_fee_address}
  Owner Allocation Addr:  {args.owner_address}
  Owner Target:           ${args.owner_target_usd:,.2f} worth of KAS (at ${args.kas_price_usd:.4f}/KAS)

{bright_cyan}--------------------------------------------------------------------{reset_color}"""
    print(config_str)

def mining_worker_thread_func(worker_id: int, args, kaspad_conn: KaspaConnector, hasher: SkyscopeHashQ, display_mgr: DisplayManager, reward_mgr: RewardsManager):
    """
    The core logic for a single mining thread/process.
    """
    logger.info(f"Worker-{worker_id}: Started.")

    while not shutdown_event.is_set():
        display_mgr.update_stat("kaspad_connected", kaspad_conn.connected)
        if not kaspad_conn.connected:
            logger.warning(f"Worker-{worker_id}: Kaspad disconnected. Main loop should handle reconnection attempt.")
            display_mgr.print_dashboard() # Update display with disconnected status
            if shutdown_event.wait(args.retry_delay / 2): break # Check shutdown during wait
            continue

        # Get new block template
        logger.debug(f"Worker-{worker_id}: Requesting block template...")
        block_template = kaspad_conn.get_block_template(args.kaspa_address)
        display_mgr.update_stat("kaspad_connected", kaspad_conn.connected) # Update after call

        if block_template:
            display_mgr.update_stat("last_block_template_time", time.time())
            display_mgr.update_stat("current_difficulty", block_template.get("target_difficulty_str", "N/A")[:16]+"...")
            display_mgr.update_stat("current_height", block_template.get("height", "N/A"))
            logger.info(f"Worker-{worker_id}: New job {block_template.get('job_id')} received. Height: {block_template.get('height')}")

            solution = hasher.mine_block(block_template,
                                         target_nonce_range=args.nonce_iterations_per_job,
                                         hashes_per_update=args.hashes_per_display_update)

            if shutdown_event.is_set(): break

            if solution:
                logger.info(f"Worker-{worker_id}: Solution found for job {solution.get('job_id')}! Nonce: {solution.get('nonce')}")
                if kaspad_conn.submit_block(solution["header_with_nonce_hex"], solution.get("job_id")):
                    display_mgr.increment_stat("accepted_shares")

                    # Process rewards (this is conceptual for solo mining block find)
                    payouts = reward_mgr.process_mined_reward(CONCEPTUAL_KAS_BLOCK_REWARD) # Use placeholder reward
                    for p in payouts: logger.info(f"Conceptual Payout: {p['amount_kas']:.4f} KAS to {p['type']} ({p['address'][:15]}...)")

                    display_mgr.log_message(f"Worker-{worker_id}: Solution ACCEPTED by network!", "SUCCESS")
                else:
                    display_mgr.increment_stat("rejected_shares")
                    display_mgr.increment_stat("errors")
                    display_mgr.log_message(f"Worker-{worker_id}: Solution REJECTED by network. Error: {kaspad_conn.last_error_message}", "ERROR")
            # No solution found in nonce range, or an error in mine_block, just loop for new job

            # Update aggregated display stats (main thread might do this based on worker reports)
            # For single conceptual worker, direct update is fine for now
            current_hr_hs = hasher.get_session_hashrate()
            display_mgr.update_stat("hashrate_mhs", current_hr_hs / 1_000_000)

            stats = reward_mgr.get_cumulative_stats()
            display_mgr.update_stat("total_kas_mined_net_user", stats['cumulative_user_net_kas'])
            display_mgr.update_stat("dev_fee_kas_cumulative", stats['cumulative_dev_fee_kas'])
            display_mgr.update_stat("owner_kas_cumulative", stats['cumulative_owner_allocation_kas'])
            owner_target_kas = stats['owner_allocation_target_kas']
            display_mgr.update_stat("owner_kas_target_remaining", max(0, (owner_target_kas if isinstance(owner_target_kas, (int,float)) else float('inf')) - stats['cumulative_owner_allocation_kas']))
            display_mgr.update_stat("virtual_skyscope_mined", stats['total_gross_kas_processed'] * 100) # Virtual SKYSCOPE based on total gross KAS processed

        else: # No block template
            display_mgr.increment_stat("errors")
            logger.warning(f"Worker-{worker_id}: Failed to get block template. Error: {kaspad_conn.last_error_message}. Retrying after delay...")
            if shutdown_event.wait(args.retry_delay): break

    logger.info(f"Worker-{worker_id}: Stopping.")


def main_mining_orchestrator(args, kaspad_conn: KaspaConnector, hasher: SkyscopeHashQ, display_mgr: DisplayManager, reward_mgr: RewardsManager):
    """Main orchestrator for the mining loop and display updates."""
    logger.info("Starting SKYSCOPE Kaspa Miner Orchestrator...")

    # Initial connection and status check
    if not kaspad_conn.check_node_status(retry_attempts=3): # More retries for initial connect
        display_mgr.log_message(f"CRITICAL: Could not connect/verify kaspad at {kaspad_conn.resolved_node_url or 'auto-detected location'}. Error: {kaspad_conn.last_error_message}", "CRITICAL")
        return

    display_mgr.set_kaspad_connected(True)
    display_mgr.update_stat("node_version", kaspad_conn.node_info.get("server_version", "N/A"))
    logger.info(f"Successfully connected to kaspad. Node: {kaspad_conn.resolved_node_url}, Version: {kaspad_conn.node_info.get('server_version', 'N/A')}, Synced: {kaspad_conn.node_info.get('is_synced')}")

    # --- For this version, run a single conceptual worker in the main thread ---
    # In a real app, you'd spawn `args.cpu_cores` threads or processes.
    # Each would call a modified mining_worker_thread_func or similar.
    # Stats would be aggregated via thread-safe queues or shared memory.

    # This loop replaces the direct call to mining_worker_thread_func to allow periodic display updates
    # even if mining_worker_thread_func blocks for a long time (due to Python hashing slowness).
    # A more robust solution would use threading for hashing and a separate thread for display updates.

    last_display_update_time = 0
    while not shutdown_event.is_set():
        mining_worker_thread_func(0, args, kaspad_conn, hasher, display_mgr, reward_mgr, args.kaspa_address) # Simplified call

        # If mining_worker_thread_func returns (e.g. after one job attempt), update display and loop or sleep
        current_time = time.time()
        if current_time - last_display_update_time > display_mgr.print_interval:
            display_mgr.print_dashboard(force_print=True) # Force print as worker might not have
            last_display_update_time = current_time

        if shutdown_event.is_set():
            break
        # Small delay before fetching next job if previous one finished quickly or failed
        time.sleep(0.1)

    logger.info("Main mining orchestrator loop finished.")


def main():
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(
        description="SKYSCOPE Miner: Python-based CPU Miner for Kaspa (kHeavyHash).",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=f"""
Example CLI:
  python skyscope_miner.py kaspa:yourwalletaddress --cpu-cores 0 --ram-percent 25

Notes:
- This miner uses a Python implementation of kHeavyHash, which will be significantly
  slower than optimized C/C++/Rust miners. It's for functional demonstration.
- The 'skyscope-hash-Q' RAM boost is a conceptual feature; its performance impact
  in this Python version is illustrative and part of ongoing R&D.
- Ensure kaspad is running, synced, and accessible. Default auto-detection targets 127.0.0.1:{KaspaConnector.DEFAULT_KASPAD_PORT}.
"""
    )
    parser.add_argument( "kaspa_address", help="Your Kaspa wallet address for receiving mining rewards.")
    parser.add_argument( "--node-url", default=None, type=str, help=f"URL of kaspad (e.g., localhost:{KaspaConnector.DEFAULT_KASPAD_PORT}). Default: Auto-Detect")
    parser.add_argument( "--cpu-cores", type=int, default=0, help="Number of CPU cores for mining. (0 for all available - default: %(default)s)")
    parser.add_argument( "--ram-percent", type=int, choices=[0, 25, 50, 75, 80], default=0, help="Conceptual RAM % for skyscope-hash-Q. (default: %(default)s)")
    parser.add_argument( "--dev-fee-address", type=str, default="kaspa:qqggvdrxjqdgwql4aac8hg0pq2v4z5p46l86f98hq7ax29k7x55v7sycs9kvm", help="Developer fee Kaspa address.")
    parser.add_argument( "--owner-address", type=str, default="kaspa:qqggvdrxjqdgwql4aac8hg0pq2v4z5p46l86f98hq7ax29k7x55v7sycs9kvm", help="Owner's KAS address for allocation.") # Same as dev for now
    parser.add_argument( "--owner-target-usd", type=float, default=50000.0, help="Target USD value for owner's KAS allocation. Default: %(default)s USD.")
    parser.add_argument( "--kas-price-usd", type=float, default=0.10, help="Initial KAS price in USD for owner allocation. Default: %(default)s USD.")
    parser.add_argument( "--log-level", type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help="Logging level. Default: %(default)s")
    parser.add_argument( "--retry-delay", type=int, default=10, help="Delay (s) before kaspad connection/job retries. Default: %(default)s s.")
    parser.add_argument( "--nonce-iterations-per-job", type=int, default=50000, help="Max nonce iterations per template before refresh. Default: %(default)s (low for Python).") # Kept low for Python
    parser.add_argument( "--hashes-per-display-update", type=int, default=50, help="Update display roughly every N hashes. Default: %(default)s.") # Lower for Python

    args = parser.parse_args()
    args.resolved_kaspad_url = args.node_url # Will be updated by connector if auto-detected

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO),
                        format='%(asctime)s - %(levelname)s - [%(threadName)s] %(filename)s:%(lineno)d - %(message)s')

    print_header()

    try:
        cpu_info = core_utils.get_cpu_info(args.cpu_cores)
        ram_info = core_utils.get_ram_info()
        conceptual_ram_alloc = core_utils.allocate_ram_for_mining_conceptual(ram_info, args.ram_percent)
    except Exception as e:
        logger.critical(f"Error initializing system utilities (CPU/RAM): {e}. Ensure psutil is installed.", exc_info=True)
        sys.exit(1)

    # Initialize KaspaConnector, attempting auto-detection if node_url is None
    kaspad_conn = KaspaConnector(args.node_url, user_agent=f"SKYSCOPEMiner/{args.log_level}") # Pass user_agent
    if not kaspad_conn.resolved_node_url: # If node_url was None, find_and_connect needs to run
        if not kaspad_conn.find_and_connect_local_kaspad():
            logger.critical(f"Failed to auto-detect and connect to local kaspad. {kaspad_conn.last_error_message}")
            # No need to print config if we can't even resolve kaspad URL
            sys.exit(1)
    args.resolved_kaspad_url = kaspad_conn.resolved_node_url # Store resolved URL back into args for display

    print_config(args, cpu_info, ram_info, conceptual_ram_alloc, args.resolved_kaspad_url)

    try:
        display_mgr = DisplayManager(args.kaspa_address)
        reward_mgr = RewardsManager(
            user_kaspa_address=args.kaspa_address,
            dev_fee_address=args.dev_fee_address,
            owner_kaspa_address=args.owner_address,
            owner_allocation_target_usd=args.owner_target_usd
        )
        reward_mgr.update_kas_usd_price(args.kas_price_usd)

        hasher = SkyscopeHashQ(cpu_info, args.ram_percent, conceptual_ram_alloc)
    except ValueError as e:
        logger.critical(f"Configuration Error for miner components: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error initializing miner components: {e}", exc_info=True)
        sys.exit(1)

    try:
        main_mining_orchestrator(args, kaspad_conn, hasher, display_mgr, reward_mgr)
    except KeyboardInterrupt:
        logger.info("SKYSCOPE Miner stopped by user (main context).")
    except Exception as e:
        logger.critical(f"A critical error occurred in the main mining orchestrator: {e}", exc_info=True)
    finally:
        logger.info("SKYSCOPE Miner shutting down completely.")
        shutdown_event.set() # Ensure all threads know to stop
        if 'kaspad_conn' in locals() and kaspad_conn:
            kaspad_conn.close()

if __name__ == "__main__":
    main()
