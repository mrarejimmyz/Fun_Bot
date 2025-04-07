#!/bin/bash

# Stop script for pump.fun trading bot
# This script finds and stops the running bot process

# Find the PID of the running bot
BOT_PID=$(pgrep -f "python src/bot_controller.py")

if [ -z "$BOT_PID" ]; then
    echo "No running pump.fun trading bot found."
    exit 0
fi

echo "Stopping pump.fun trading bot (PID: $BOT_PID)..."

# Send SIGTERM to allow graceful shutdown
kill -15 $BOT_PID

# Wait for process to terminate
for i in {1..10}; do
    if ! ps -p $BOT_PID > /dev/null; then
        echo "Bot stopped successfully."
        exit 0
    fi
    echo "Waiting for bot to stop... ($i/10)"
    sleep 1
done

# If process is still running after 10 seconds, force kill
if ps -p $BOT_PID > /dev/null; then
    echo "Bot is not responding. Forcing termination..."
    kill -9 $BOT_PID
    echo "Bot terminated."
fi

exit 0
