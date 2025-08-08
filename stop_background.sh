#!/bin/bash

# LinkedIn Agent Background Stopper
# This script stops the LinkedIn content generation system

echo "🛑 Stopping LinkedIn Agent Background Process"
echo "============================================="

PID_FILE="linkedin_agent.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ No PID file found. LinkedIn Agent may not be running."
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  Process $PID is not running. Cleaning up PID file."
    rm -f "$PID_FILE"
    exit 0
fi

echo "🔄 Stopping process $PID..."

# Try graceful shutdown first
kill $PID

# Wait up to 10 seconds for graceful shutdown
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✅ LinkedIn Agent stopped gracefully"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if still running
echo "⚠️  Force stopping process..."
kill -9 $PID

if ! ps -p $PID > /dev/null 2>&1; then
    echo "✅ LinkedIn Agent force stopped"
    rm -f "$PID_FILE"
else
    echo "❌ Failed to stop LinkedIn Agent"
    exit 1
fi 