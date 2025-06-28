# SKYSCOPE Kaspa Miner - User Manual (v0.2.0 - Python kHeavyHash Edition)

## 1. Introduction

Welcome to SKYSCOPE Miner! This Python-based command-line application provides a **functional implementation for mining Kaspa (KAS) using your CPU**. It features a from-the-ground-up Python version of the kHeavyHash algorithm and introduces the "skyscope-hash-Q" engine—a conceptual framework for exploring RAM-assisted CPU mining.

This tool is primarily designed for:
*   **Educational Purposes:** Understanding the kHeavyHash algorithm and the process of PoW mining in Python.
*   **Research & Development:** Experimenting with CPU resource utilization (cores and RAM via "skyscope-hash-Q") and its theoretical impact on hashing.
*   **Functional CPU Mining:** Yes, it can find real Kaspa blocks if run long enough against a very low difficulty (like on a private testnet or if you get extremely lucky on mainnet over geological timescales).

**Project Visionary:** Miss Casey Jay Topojani, Skyscope Sentinel Intelligence
**Contact:** skyscopesentinel@gmail.com
**GitHub:** [https://github.com/skyscope-sentinel](https://github.com/skyscope-sentinel) (Conceptual Link - will be active when public)
**ABN:** 11287984779

## 2. IMPORTANT DISCLAIMERS & Performance Expectations

*   **PYTHON PERFORMANCE LIMITATIONS:** The kHeavyHash algorithm implemented in this miner is written **entirely in Python**. Python, being an interpreted language, is **significantly slower** for computationally intensive tasks like Proof-of-Work hashing compared to optimized implementations in C, C++, or Rust. **Do NOT expect competitive hashrates against miners written in these languages.** This tool is for functionality, learning, and conceptual exploration, not high-performance mining on the main Kaspa network.
*   **"skyscope-hash-Q" is CONCEPTUAL for Python:** The "skyscope-hash-Q" RAM utilization feature allows you to configure RAM percentage. However, its ability to provide a tangible performance boost to the *Python-based* kHeavyHash is highly speculative and primarily serves as an R&D framework. Significant speedups from RAM interaction typically require low-level algorithmic design not fully realizable in pure Python for existing PoW algorithms.
*   **Software Status:** This is a developmental version. While functional, it's intended for users comfortable with experimental software.
*   **Use at Your Own Risk:** Cryptocurrency mining can be resource-intensive. Understand the risks, including hardware utilization and market volatility.

## 3. Prerequisites

Before running SKYSCOPE Miner, please ensure you have:

*   **Python:** Python 3.8 or newer installed. Download from [python.org](https://www.python.org/).
*   **Python Dependencies:**
    *   `psutil`: For system information (CPU/RAM).
    *   `pysha3`: For Keccak hashing functions used within kHeavyHash.
    ```bash
    pip install psutil pysha3
    ```
*   **`kaspad` Node (Kaspa Full Node):**
    *   You **must** have a Kaspa full node (`kaspad`) running, fully synced, and accessible. SKYSCOPE Miner connects to this node to get work and submit solutions.
    *   This can be the Go version (standard) or a Rust version (e.g., rusty-kaspa v0.15.0+).
    *   **gRPC Interface:** Ensure `kaspad`'s gRPC interface is enabled (i.e., not started with `--nogrpc`) and listening on a known IP and port.
        *   Default Mainnet gRPC port: `16110`
        *   Default Testnet gRPC port: `16210`
        *   Check your `kaspad` configuration or startup logs for the exact `--rpclisten` address.
    *   **Sync Status:** For reliable mining (especially solo), your `kaspad` node **must be fully synced** with the Kaspa network.
    *   **`--enable-unsynced-mining` (Kaspad Flag):** If you run your `kaspad` with this flag, it *might* provide block templates even when not fully synced. However, this is primarily for testing, and mining on an unsynced node can lead to orphaned blocks (wasted work). SKYSCOPE Miner will generally expect a synced node.

## 4. Installation / Getting the Miner

*   **Coming Soon:** SKYSCOPE Miner will eventually be available for download from the project's GitHub releases page.
*   **Manual Setup (Current):**
    1.  Clone or download the project files from the repository.
    2.  Ensure you have Python and the listed dependencies installed.
    3.  The main script is `skyscope_miner/skyscope_miner.py`.

## 5. Configuration & Running the Miner

SKYSCOPE Miner is configured via command-line arguments.

### 5.1. Command-Line Arguments:

*   `kaspa_address` (Required): Your Kaspa wallet address where mining rewards will be sent (after dev fee and initial owner allocation period).
*   `--node-url` (Optional): URL of your `kaspad` node's gRPC interface (e.g., `localhost:16110`, `127.0.0.1:16210`).
    *   If not provided, the miner will attempt to **auto-detect** a local `kaspad` on default ports (`127.0.0.1:16110`, then `127.0.0.1:16210`).
*   `--cpu-cores` (Optional): Number of CPU cores to use for mining.
    *   Default: `0` (uses all available logical cores, though Python's GIL limits true parallelism for CPU-bound tasks in one process). For this Python version, it primarily affects the conceptual hashrate calculation in simulations/display. A future version with multiprocessing would leverage this more directly.
*   `--ram-percent` (Optional): Percentage of system RAM to conceptually make available for the "skyscope-hash-Q" engine.
    *   Default: `0` (no explicit RAM interaction beyond standard Python usage).
    *   Choices: `0`, `25`, `50`, `75`, `80`.
    *   **Note:** The actual performance impact of this setting on the Python kHeavyHash is part of ongoing R&D and likely minimal. High values might impact system stability.
*   `--dev-fee-address` (Optional): The Kaspa address for the 10% developer fee.
    *   Default: `kaspa:qqggvdrxjqdgwql4aac8hg0pq2v4z5p46l86f98hq7ax29k7x55v7sycs9kvm`
*   `--owner-address` (Optional): Owner's Kaspa address for the initial KAS allocation target.
    *   Default: `kaspa:qqggvdrxjqdgwql4aac8hg0pq2v4z5p46l86f98hq7ax29k7x55v7sycs9kvm` (Currently same as dev fee address).
*   `--owner-target-usd` (Optional): Target USD value of KAS for the one-time owner's allocation.
    *   Default: `50000.0` USD.
*   `--kas-price-usd` (Optional): Initial KAS price in USD used for calculating the KAS amount for the owner's USD target. This should be updated if the price changes significantly for accurate tracking.
    *   Default: `0.10` USD.
*   `--log-level` (Optional): Set the logging level for console output.
    *   Default: `INFO`
    *   Choices: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
*   `--retry-delay` (Optional): Delay in seconds before retrying `kaspad` connection or getting a new job after an error.
    *   Default: `10` seconds.
*   `--nonce-iterations-per-job` (Optional): Maximum number of nonces to try per block template before requesting a new one. Due to Python's hashing speed, keep this reasonably low for testing, or high if you intend to let it run for a very long time on a single job.
    *   Default: `50000`.
*   `--hashes-per-display-update` (Optional): Update the display stats roughly every N hashes.
    *   Default: `50`. (Lower this for faster updates if your H/s is very low).

### 5.2. Example Command:

```bash
python skyscope_miner/skyscope_miner.py kaspa:yourkaspaaddress --cpu-cores 4 --ram-percent 50
```
(This will use auto-detect for the kaspad node.)

To specify a node:
```bash
python skyscope_miner/skyscope_miner.py kaspa:yourkaspaaddress --node-url 192.168.1.100:16110
```

### 5.3. Running the Miner:

1.  Open your terminal or command prompt.
2.  Navigate to the directory containing the `skyscope_miner` sub-directory (i.e., the project root).
3.  Execute the script: `python -m skyscope_miner.skyscope_miner [YOUR_ARGUMENTS]`
    Or, if inside the `skyscope_miner` directory: `python skyscope_miner.py [YOUR_ARGUMENTS]` (ensure Python can find the modules). For simplicity, running from project root with `-m` is often more reliable for module resolution.

## 6. Understanding the Output (CLI Dashboard)

The miner displays a dashboard in your terminal:

*   **Header:** Miner name, visionary details.
*   **Configuration Summary:** Key parameters being used.
*   **Live Stats:**
    *   `Uptime`: Miner running duration.
    *   `Kaspad Status`: `Connected` (and to which URL) or `Disconnected`. Node version if available.
    *   `Errors`: Count of critical errors.
    *   `Hashrate (H/s)`: Your estimated mining speed in Hashes per second (will be low for Python).
    *   `Accepted Shares`: Valid solutions accepted by the network (for solo, this means blocks found).
    *   `Rejected/Stale Shares`: Invalid/late solutions.
    *   `Current Difficulty`: Target difficulty from the network.
    *   `Current Height`: Current block height/blue score from the network.
    *   `Last Block Template`: Time since new work was received.
*   **Earnings Overview:**
    *   `Virtual SKYSCOPE Mined`: Visual metric of mining effort/efficiency.
    *   `Net KAS Mined (User)`: KAS allocated to your wallet (after fees/owner period).
    *   `Dev Fee Paid (10%)`: Cumulative KAS for developer fee.
    *   `Owner Allocation Paid`: KAS paid towards the owner's USD target.
    *   `Owner Target Remaining`: KAS still needed for owner's target.
*   **Log Messages:** Important events, warnings, or errors.

Press `Ctrl+C` to stop the miner gracefully.

## 7. "skyscope-hash-Q" Conceptual RAM Feature

You can specify `--ram-percent` to allocate a percentage of your system RAM. In the current Python version of SKYSCOPE Miner, this setting primarily serves as a **configuration for the conceptual "skyscope-hash-Q" engine.** The Python kHeavyHash implementation itself does not yet leverage this RAM in a way that demonstrably boosts performance. This feature is for:
*   **Future R&D:** Exploring how RAM might be used in lower-level or redesigned hashing algorithms.
*   **Simulation:** Allowing the display and internal logic to account for this conceptual resource allocation.

## 8. Fee Structure & Owner's Allocation

*   **Developer Fee:** A 10% fee on all gross KAS rewards is sent to the SKYSCOPE project wallet to support development.
*   **Owner's Allocation:** The first 50,000 USD worth of KAS (calculated at the current `--kas-price-usd`, after the dev fee) mined by the collective effort of users is allocated to the project visionary's wallet. Once this one-time target is met globally by the miner's reward system (this needs clarification - if it's per miner instance or global), all subsequent net rewards (after dev fee) go to the user's mining address. The `RewardsManager` module handles this logic.

## 9. Troubleshooting

*   **Cannot connect to `kaspad` / Auto-detect fails:**
    *   Ensure `kaspad` is running, fully synced, and its gRPC port is open. Use `kaspad --rpclisten=0.0.0.0:16110` (or your desired IP) to ensure it's listening externally if miner is on a different machine or in Docker.
    *   Specify the correct `--node-url` if it's not `127.0.0.1:16110` or `127.0.0.1:16210`.
    *   Check firewalls.
*   **Very Low Hashrate:** This is expected with the Python kHeavyHash implementation. This miner is for functionality and learning, not speed records.
*   **"Node not synced" messages:** Wait for your `kaspad` to fully sync. You can check `kaspad` logs. (Or run `kaspad` with `--enable-unsynced-mining` for testing, with caution).
*   **Address Errors:** Double-check your Kaspa wallet addresses start with `kaspa:` and are correct.

For further assistance, please check the GitHub issues page or contact support.

Thank you for exploring SKYSCOPE Miner!
