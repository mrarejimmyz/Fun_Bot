# Pump.fun Trading Bot

A high-performance trading bot for the pump.fun platform on Solana blockchain, designed to monitor for new token launches, analyze trading opportunities, and execute trades with robust risk management.

## Features

- **Market Monitoring**: Automatically detects new token launches on pump.fun
- **Trading Strategy**: Implements sophisticated algorithms for token selection and timing
- **Risk Management**: Protects your capital with stop-loss, take-profit, and diversification rules
- **Performance Tracking**: Records and analyzes trading history and performance metrics
- **Multi-blockchain Support**: Primary support for Solana with extensibility for Base blockchain

## Requirements

- Python 3.10+
- Solana wallet with private key
- RPC endpoints for Solana (and optionally Base)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pump_fun_bot.git
cd pump_fun_bot
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your environment:
```bash
cp .env.example .env
```

5. Edit the `.env` file with your wallet private key and RPC endpoints.

## Configuration

The bot can be configured through the `.env` file:

```
# Solana RPC URL - Replace with your preferred RPC provider
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Base RPC URL - Replace with your preferred RPC provider
BASE_RPC_URL=https://mainnet.base.org

# Wallet private key - Replace with your actual private key when using the bot
# WARNING: Keep this secure and never share it
WALLET_PRIVATE_KEY=your_private_key_here

# Log level
LOG_LEVEL=INFO
```

Additional configuration options are available in `config/config.py`:

- `PUMP_FUN_PROGRAM_ID`: The program ID for pump.fun on Solana
- `MAX_ALLOCATION_PER_TOKEN`: Maximum percentage of wallet to allocate per token
- `STOP_LOSS_PERCENTAGE`: Percentage drop that triggers stop loss
- `TAKE_PROFIT_PERCENTAGE`: Percentage gain that triggers take profit
- `COOLDOWN_PERIOD`: Waiting period after token detection before analysis
- `BLACKLISTED_TERMS`: Terms in token names to automatically skip
- `PRIORITY_FEE`: Transaction priority fee for faster execution

## Usage

1. Start the bot:
```bash
python src/bot_controller.py
```

2. Monitor the logs:
```bash
tail -f pump_fun_bot.log
```

3. To stop the bot, press Ctrl+C in the terminal where it's running.

## Architecture

The bot consists of several key components:

1. **Blockchain Connection**: Manages connections to Solana and Base blockchains
2. **Market Analyzer**: Monitors for new tokens and analyzes their potential
3. **Trading Strategy**: Makes buy/sell decisions based on analysis
4. **Transaction Executor**: Handles the actual buying and selling of tokens
5. **Risk Manager**: Implements safeguards to prevent losses
6. **Bot Controller**: Integrates all components and manages the overall operation

## Testing

Run the test suite to verify functionality:

```bash
./run_tests.sh
```

## Security Considerations

- **Private Key Security**: Your private key is stored in the `.env` file. Keep this file secure and never share it.
- **Risk Management**: The bot implements several risk management features, but cryptocurrency trading is inherently risky. Only use funds you can afford to lose.
- **Error Handling**: The bot includes error handling to prevent unexpected behavior, but should be monitored during operation.

## Disclaimer

This bot is provided for educational and research purposes only. Use at your own risk. The developers are not responsible for any financial losses incurred through the use of this software.

## License

MIT License
