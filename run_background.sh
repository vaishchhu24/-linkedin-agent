#!/bin/bash

# LinkedIn Agent Background Runner
# This script runs the LinkedIn content generation system in the background

echo "🚀 Starting LinkedIn Agent in Background Mode"
echo "=============================================="

# Set the working directory
cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
mkdir -p logs

# Get current timestamp for log file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/linkedin_agent_${TIMESTAMP}.log"
PID_FILE="linkedin_agent.pid"

echo "📝 Log file: $LOG_FILE"
echo "🆔 PID file: $PID_FILE"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  LinkedIn Agent is already running (PID: $PID)"
        echo "   To stop it, run: kill $PID"
        echo "   Or use: ./stop_background.sh"
        exit 1
    else
        echo "🧹 Cleaning up stale PID file"
        rm -f "$PID_FILE"
    fi
fi

# Start the system in background
echo "🔄 Starting system..."
nohup python3 final_integrated_system.py > "$LOG_FILE" 2>&1 &

# Save PID
echo $! > "$PID_FILE"

echo "✅ LinkedIn Agent started successfully!"
echo "📊 PID: $(cat $PID_FILE)"
echo "📝 Logs: $LOG_FILE"
echo ""
echo "🔍 To monitor logs: tail -f $LOG_FILE"
echo "🛑 To stop: ./stop_background.sh"
echo "📊 To check status: ./check_status.sh"
echo ""
echo "🌐 System is now running in background mode!"
echo "   - Sends daily emails at 10 AM UK time"
echo "   - Monitors for replies every 5 minutes"
echo "   - Processes feedback and revises posts"
echo "   - Learns from approved posts only" 