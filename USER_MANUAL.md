# fun Trading Bot - User Manual

## Introduction

The fun Trading Bot is an automated trading system designed to monitor the fun platform for new token launches, analyze trading opportunities, and execute trades with robust risk management. This user manual provides detailed instructions on how to set up, configure, and operate the bot.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the Bot](#running-the-bot)
4. [Monitoring and Management](#monitoring-and-management)
5. [Understanding Bot Behavior](#understanding-bot-behavior)
6. [Troubleshooting](#troubleshooting)
7. [Security Best Practices](#security-best-practices)

## Installation

### System Requirements

- Linux-based operating system (Ubuntu 20.04+ recommended)
- Python 3.10 or higher
- Internet connection
- Solana wallet with SOL for trading

### Installation Steps

1. **Download the Bot**

   Clone the repository or extract the provided zip file to your desired location:

   ```bash
   git clone https://github.com/yourusername/pump_fun_bot.git
   cd pump_fun_bot
   ```

2. **Run the Setup Script**

   Execute the setup script to create a virtual environment and install dependencies:

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   This script will:

   - Create a Python virtual environment
   - Install all required dependencies
   - Create a template .env file
   - Make the start and stop scripts executable

3. **Configure Your Environment**

   Edit the `.env` file with your specific settings:

   ```bash
   nano .env
   ```

   See the [Configuration](#configuration) section for details on required settings.

## Configuration

### Environment Variables

The bot uses environment variables stored in the `.env` file for sensitive configuration:

| Variable           | Description                      | Example                             |
| ------------------ | -------------------------------- | ----------------------------------- |
| SOLANA_RPC_URL     | URL for Solana RPC node          | https://api.mainnet-beta.solana.com |
| BASE_RPC_URL       | URL for Base blockchain RPC node | https://mainnet.base.org            |
| WALLET_PRIVATE_KEY | Your Solana wallet private key   | 5Kd...your_private_key              |
| LOG_LEVEL          | Logging verbosity                | INFO                                |

### Bot Configuration

Additional configuration options are available in `config/config.py`:

| Setting                  | Description                     | Default         |
| ------------------------ | ------------------------------- | --------------- |
| PUMP_FUN_PROGRAM_ID      | Program ID for fun on Solana    | pump...         |
| MAX_ALLOCATION_PER_TOKEN | Maximum wallet % per token      | 0.1 (10%)       |
| STOP_LOSS_PERCENTAGE     | Stop loss trigger threshold     | 0.15 (15%)      |
| TAKE_PROFIT_PERCENTAGE   | Take profit trigger threshold   | 0.3 (30%)       |
| COOLDOWN_PERIOD          | Wait time after token detection | 15 seconds      |
| BLACKLISTED_TERMS        | Terms to avoid in token names   | ["scam", "rug"] |
| PRIORITY_FEE             | Transaction priority fee        | 10000           |

You can modify these settings to adjust the bot's trading strategy and risk management.

## Running the Bot

### Starting the Bot

To start the bot, use the provided start script:

```bash
./start_bot.sh
```

The bot will begin monitoring the fun platform for new token launches and execute trades according to your configuration.

### Stopping the Bot

To stop the bot, use the provided stop script:

```bash
./stop_bot.sh
```

This will gracefully terminate the bot, allowing it to complete any pending operations.

## Monitoring and Management

### Log Files

The bot generates detailed logs in the `pump_fun_bot.log` file. You can monitor these logs in real-time:

```bash
tail -f pump_fun_bot.log
```

### Performance Tracking

The bot maintains records of all trades in the `data/trade_history.json` file. You can analyze this file to evaluate the bot's performance.

### Wallet Balance

To check your current wallet balance:

```bash
python -c "from src.transaction_executor import TransactionExecutor; import asyncio; executor = TransactionExecutor(); print(asyncio.run(executor.get_wallet_balance()))"
```

## Understanding Bot Behavior

### Token Selection Criteria

The bot evaluates new tokens based on several factors:

1. **Creator Reputation**: Tokens from known creators receive higher scores
2. **Initial Liquidity**: Higher initial liquidity is preferred
3. **Token Name and Symbol**: Avoids suspicious naming patterns
4. **Trading Volume**: Early trading activity is analyzed
5. **Bonding Curve Parameters**: Evaluates the token's price curve

### Trading Strategy

The bot employs a multi-faceted trading strategy:

1. **Entry Timing**: Aims to enter positions early in a token's lifecycle
2. **Position Sizing**: Allocates capital based on token score and risk assessment
3. **Exit Conditions**: Uses stop-loss and take-profit mechanisms
4. **Portfolio Diversification**: Limits exposure to any single token

### Risk Management

The bot implements several risk management features:

1. **Stop Loss**: Automatically sells if a token drops below threshold
2. **Take Profit**: Secures gains when targets are reached
3. **Allocation Limits**: Prevents overexposure to any single token
4. **Blacklisting**: Avoids tokens with suspicious characteristics
5. **Gas Fee Optimization**: Adjusts transaction fees based on network conditions

## Troubleshooting

### Common Issues

1. **Connection Errors**

   - Verify your RPC URLs are correct and accessible
   - Check your internet connection
   - Ensure the RPC provider hasn't changed their endpoint

2. **Transaction Failures**

   - Verify your wallet has sufficient SOL for transactions
   - Check that your private key is correctly formatted
   - Increase the PRIORITY_FEE if network is congested

3. **Bot Not Starting**
   - Ensure all dependencies are installed
   - Check the log file for specific errors
   - Verify Python version is 3.10 or higher

### Error Messages

| Error                            | Possible Cause                         | Solution                             |
| -------------------------------- | -------------------------------------- | ------------------------------------ |
| "No wallet private key provided" | Missing or invalid private key in .env | Add correct private key to .env file |
| "Failed to connect to Solana"    | RPC URL issue or network problem       | Check RPC URL and network status     |
| "Insufficient balance"           | Not enough SOL in wallet               | Add SOL to your wallet               |

## Security Best Practices

1. **Private Key Protection**

   - Never share your .env file or private key
   - Use a dedicated wallet for the bot with limited funds
   - Consider running the bot on a secure, dedicated server

2. **Regular Monitoring**

   - Check the bot's performance regularly
   - Monitor your wallet balance
   - Review trade history for unexpected behavior

3. **Risk Management**

   - Start with small amounts until you're comfortable with the bot
   - Regularly withdraw profits to a separate wallet
   - Never invest more than you can afford to lose

4. **Updates and Maintenance**
   - Check for updates to the bot software
   - Monitor for changes to the fun platform
   - Update your RPC endpoints if performance degrades

---

## Disclaimer

This bot is provided for educational and research purposes only. Use at your own risk. The developers are not responsible for any financial losses incurred through the use of this software. Cryptocurrency trading involves significant risk and may not be suitable for all investors.
