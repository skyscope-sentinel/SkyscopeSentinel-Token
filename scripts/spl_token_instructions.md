# Instructions for SKYSCOPESENTINEL (SKYSCOPE) SPL Token Creation Script

This document provides instructions and explanations for using the `create_skyscope_token.sh` script to create the SKYSCOPESENTINEL (SKYSCOPE) SPL token on the Solana blockchain.

## 1. Overview

The `create_skyscope_token.sh` script is a **template and outline** of Solana Command Line Interface (CLI) commands. It is designed to guide you through the process of:

*   Generating necessary cryptographic keypairs.
*   Creating the SKYSCOPE token mint (the definition of the token).
*   Creating a treasury/genesis token account.
*   Minting the initial supply of SKYSCOPE tokens to the treasury account.
*   Creating an associated token account for the owner (Miss Casey Jay Topojani).
*   Transferring an initial allocation of 50,000 SKYSCOPE tokens to the owner's wallet.
*   Optionally, disabling future minting to create a fixed supply.
*   Optionally, adding token metadata using Metaplex (conceptual outline).

**IMPORTANT:** The script itself contains **commented-out commands**. You must manually review, edit (if necessary, especially keypair paths or specific addresses if you deviate from the script's flow), and uncomment these commands before execution. It is highly recommended to execute commands one by one or in small, logical groups to monitor their output and manage any potential errors.

## 2. Prerequisites

Before you begin, ensure you have the following:

*   **Solana CLI Installed:** You need the Solana CLI tools installed on your system. If you haven't installed them, follow the official documentation: [Install Solana CLI Tools](https://docs.solana.com/cli/install-solana-cli-tools).
*   **Solana CLI Configuration:**
    *   Your Solana CLI must be configured to connect to your desired Solana cluster (e.g., Mainnet-beta, Devnet, Testnet). You can check your current configuration with `solana config get`.
    *   For initial testing, **it is strongly recommended to use Devnet or Testnet.** You can set your cluster URL with `solana config set --url <CLUSTER_URL>`. For example, for Devnet: `solana config set --url https://api.devnet.solana.com`.
*   **Fee-Payer Wallet:** You need a Solana wallet configured in your CLI that will pay the transaction fees (rent and gas) for these operations. This is often referred to as your "default fee-payer."
    *   Ensure this wallet has a sufficient SOL balance. You can get free SOL for Devnet/Testnet from a faucet (e.g., `solana airdrop 2 YOUR_WALLET_ADDRESS --url https://api.devnet.solana.com`).
    *   You can check your default address with `solana address` and balance with `solana balance`.
*   **Bash Shell:** The script is intended to be run in a bash shell environment (common on Linux and macOS; available on Windows via WSL or Git Bash).

## 3. Understanding the Script Variables

The script starts by defining several important variables:

*   `TOKEN_NAME`: "SKYSCOPESENTINEL"
*   `TOKEN_SYMBOL`: "SKYSCOPE"
*   `TOKEN_DECIMALS`: 9 (This is a common precision for SPL tokens, allowing for fine divisibility).
*   `INITIAL_SUPPLY_RAW`: 1,000,000,000 (The total number of tokens to be minted, excluding decimals. For 1 billion tokens, this is the value).
*   `OWNER_WALLET_ADDRESS`: "AZCaMLfq6k4hTA6AXTgjBMmjYsYFqPaCFv6Rh2QHEXuA" (The recipient of the initial 50,000 SKYSCOPE tokens).
*   `OWNER_TOKEN_ALLOCATION_RAW`: 50,000 (The number of tokens for the owner, excluding decimals).
*   `TOKEN_MINT_KEYPAIR_PATH`: `./skyscope_mint_keypair.json` (Path where the keypair for the token mint itself will be saved. This keypair *is* the token mint's address).
*   `TOKEN_MINT_AUTHORITY_KEYPAIR_PATH`: `./skyscope_mint_authority_keypair.json` (Path for a dedicated mint authority keypair. The script currently assumes your default CLI wallet acts as the mint authority for simplicity, but you can adapt it to use a separate keypair).

## 4. Step-by-Step Execution Guide

**Navigate to the `scripts` directory before running commands if your keypairs are being saved there.**

Open the `create_skyscope_token.sh` script in a text editor.

### Step 1: Generate Keypair for the Token Mint
*   **Command (example):** `solana-keygen new --outfile ./skyscope_mint_keypair.json`
*   **Purpose:** This creates a new Solana keypair (public key and private key). The public key of this keypair will become the unique address (identifier) of your SKYSCOPE token mint.
*   **Action:** Uncomment the `solana-keygen new ...` command.
*   **Output:** Note the public key (Token Mint Address) that is generated. The script attempts to capture this, but verify it. **Securely back up this keypair file.** Losing it means losing control over aspects of the token if you haven't transferred authorities.

### Step 2: Create the SKYSCOPE Token
*   **Command (example):** `spl-token create-token ./skyscope_mint_keypair.json --decimals 9`
*   **Purpose:** This command registers your token on the Solana blockchain using the keypair generated in Step 1 as the token's unique ID. It sets the number of decimal places for your token. The wallet currently configured as your Solana CLI default will be set as the initial **mint authority** for this token.
*   **Action:**
    *   Uncomment the `spl-token create-token ...` command.
    *   **Crucially, capture the Token Mint Address** output by this command. This is the official on-chain address of your SKYSCOPE token.
    *   Update the `TOKEN_MINT_ADDRESS="YOUR_SKYSCOPE_TOKEN_MINT_ADDRESS_HERE"` line in the script with the actual mint address if you plan to run subsequent commands from the script or for your records.
*   **Note:** If you used `solana-keygen new --outfile some_file.json` in step 1, then `some_file.json` *is* the mint address for the `create-token` command. If `create-token` generates a new keypair for you (by not providing one), it will display the mint address.

### Step 3: Create Treasury/Genesis Token Account
*   **Command (example):** `spl-token create-account YOUR_SKYSCOPE_TOKEN_MINT_ADDRESS_HERE`
*   **Purpose:** This creates an Associated Token Account (ATA) linked to your default CLI wallet that can hold SKYSCOPE tokens. This account will initially receive all minted tokens.
*   **Action:**
    *   Replace `YOUR_SKYSCOPE_TOKEN_MINT_ADDRESS_HERE` with the actual Token Mint Address from Step 2.
    *   Uncomment the command.
    *   The script attempts to find this new account address. Note the `TREASURY_TOKEN_ACCOUNT_ADDRESS`.

### Step 4: Mint Initial Supply
*   **Command (example):** `spl-token mint YOUR_SKYSCOPE_TOKEN_MINT_ADDRESS_HERE 1000000000 TREASURY_TOKEN_ACCOUNT_ADDRESS`
*   **Purpose:** This mints the `INITIAL_SUPPLY_RAW` (e.g., 1 billion) SKYSCOPE tokens and places them into the `TREASURY_TOKEN_ACCOUNT_ADDRESS`. The mint authority (your default CLI wallet) signs this.
*   **Action:**
    *   Replace placeholders with your actual Token Mint Address and Treasury Token Account Address.
    *   Uncomment and execute.

### Step 5: Create Owner's SKYSCOPE Token Account
*   **Command (example):** `solana spl-token create-associated-token-account --owner AZCaMLfq6k4hTA6AXTgjBMmjYsYFqPaCFv6Rh2QHEXuA --mint YOUR_SKYSCOPE_TOKEN_MINT_ADDRESS_HERE`
*   **Purpose:** This creates an Associated Token Account for the owner's wallet (`$OWNER_WALLET_ADDRESS`) so they can receive SKYSCOPE tokens. Your default CLI wallet will pay the fee for this.
*   **Action:**
    *   Replace `YOUR_SKYSCOPE_TOKEN_MINT_ADDRESS_HERE` with your actual Token Mint Address.
    *   Uncomment and execute.
    *   Note the `OWNER_SKYSCOPE_ACCOUNT_ADDRESS` that is determined by the script (it's a predictable address based on owner and mint).

### Step 6: Transfer Tokens to Owner
*   **Command (example):** `spl-token transfer YOUR_SKYSCOPE_TOKEN_MINT_ADDRESS_HERE 50000 OWNER_SKYSCOPE_ACCOUNT_ADDRESS --from TREASURY_TOKEN_ACCOUNT_ADDRESS --allow-unfunded-recipient --fund-recipient`
*   **Purpose:** Transfers `OWNER_TOKEN_ALLOCATION_RAW` (e.g., 50,000) SKYSCOPE tokens from your treasury account to the owner's SKYSCOPE token account. The `--fund-recipient` flag can create the owner's ATA if it doesn't exist and your fee-payer wallet pays for its rent, which is redundant if Step 5 was successful but harmless.
*   **Action:**
    *   Replace placeholders with your actual Token Mint Address, Owner's SKYSCOPE Account Address, and Treasury Token Account Address.
    *   Uncomment and execute.

### Step 7: (Optional) Disable Future Minting
*   **Command (example):** `spl-token authorize YOUR_SKYSCOPE_TOKEN_MINT_ADDRESS_HERE mint --disable`
*   **Purpose:** **This is an IRREVERSIBLE action.** It revokes the mint authority, meaning no more SKYSCOPE tokens can ever be created for this specific token mint. This is how you create a fixed supply.
*   **Action:**
    *   If you are certain you want a fixed supply, uncomment this command after replacing the placeholder.
    *   The script includes a confirmation prompt. Type `yes` to proceed if uncommented.

### Step 8: (Optional) Add Token Metadata
*   **Purpose:** To make your token appear with a name, symbol, logo, and description in wallets and explorers, you need to add metadata using the Metaplex Token Metadata standard.
*   **Action:** This step is more complex and requires:
    1.  Preparing a JSON metadata file (an example structure is in the script).
    2.  Uploading your token logo (e.g., PNG) and the JSON metadata file to permanent, decentralized storage like Arweave or IPFS. You will get URLs for these.
    3.  Using the Metaplex CLI tools (e.g., `mpl-token-metadata create-metadata-accounts` or newer commands) to associate this metadata with your Token Mint Address.
*   **Note:** The script provides a placeholder comment. You will need to install Metaplex tools and consult their latest documentation ([Metaplex Docs](https://docs.metaplex.com/)) for the exact commands, as they can change.

## 5. Important Considerations

*   **Security:**
    *   **Keypair Management:** Securely back up all generated keypair files (especially `skyscope_mint_keypair.json` and any authority keypairs). Losing them can mean losing control.
    *   **Authorities:** Understand who holds the mint authority and freeze authority. For a truly decentralized token, mint authority is often disabled after initial minting, or transferred to a DAO-controlled address.
*   **Testing:** **ALWAYS perform these steps on Solana Devnet or Testnet first.** This allows you to debug and understand the process without risking real funds or creating a permanent token on Mainnet-beta prematurely.
*   **Fees:** All these transactions incur SOL fees (for transaction processing and rent for account storage). Ensure your fee-paying wallet is adequately funded.
*   **Idempotency:** Some commands (like `create-token` or `create-account`) will fail if the resource already exists. Other commands (like `mint` or `transfer`) can be run multiple times if not managed carefully (though minting requires authority).
*   **Mainnet Deployment:** When ready for Mainnet-beta, ensure your Solana CLI is configured for the Mainnet URL (`https://api.mainnet-beta.solana.com`) and that your fee-paying wallet has real SOL. The process is identical, but the stakes are real.

## 6. Troubleshooting

*   **Check Balances:** `solana balance YOUR_WALLET_ADDRESS`
*   **Check Config:** `solana config get`
*   **Explorer:** Use a Solana explorer (e.g., [explorer.solana.com](https://explorer.solana.com/), [solscan.io](https://solscan.io/), [solanabeach.io](https://solanabeach.io/)) to check the status of your token mint, accounts, and transactions. Remember to select the correct network (Mainnet, Devnet, Testnet) on the explorer.
*   **Verbose Output:** Add `--verbose` to Solana CLI commands for more detailed output if you encounter errors.

This script and these instructions should provide a solid foundation for creating your SKYSCOPE SPL token. Proceed carefully and always double-check addresses and commands.
