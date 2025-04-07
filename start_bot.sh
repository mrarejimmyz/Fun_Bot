#!/bin/bash

# Start script for fun trading bot
# This script activates the virtual environment and starts the bot

# Change to the bot directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Configuration file .env not found. Please create it from .env.example."
    exit 1
fi

# Start the bot
echo "Starting fun trading bot..."
python src/bot_controller.py

# Deactivate virtual environment on exit
deactivate
