#!/bin/bash

# Setup script for pump.fun trading bot
# This script creates a virtual environment and installs dependencies

# Change to the bot directory
cd "$(dirname "$0")"

echo "Setting up pump.fun trading bot..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Please make sure python3-venv is installed."
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install solana web3 python-dotenv base58 requests pandas numpy matplotlib

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your wallet private key and RPC endpoints."
fi

# Make start and stop scripts executable
chmod +x start_bot.sh
chmod +x stop_bot.sh

echo "Setup complete! You can now edit the .env file and run ./start_bot.sh to start the bot."

# Deactivate virtual environment
deactivate
