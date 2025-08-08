#!/bin/bash

# LinkedIn Agent Status Checker
# This script checks the status of the LinkedIn content generation system

echo "📊 LinkedIn Agent Status Check"
echo "============================="

PID_FILE="linkedin_agent.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ LinkedIn Agent is NOT running"
    echo "   To start: ./run_background.sh"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
    echo "✅ LinkedIn Agent is RUNNING"
    echo "📊 PID: $PID"
    echo "⏰ Started: $(ps -o lstart= -p $PID)"
    echo "💾 Memory: $(ps -o rss= -p $PID | awk '{print $1/1024 " MB"}')"
    echo "⏱️  CPU Time: $(ps -o time= -p $PID)"
    
    # Check recent logs
    echo ""
    echo "📝 Recent Log Activity:"
    if [ -d "logs" ]; then
        LATEST_LOG=$(ls -t logs/linkedin_agent_*.log 2>/dev/null | head -1)
        if [ -n "$LATEST_LOG" ]; then
            echo "   Latest log: $LATEST_LOG"
            echo "   Last 3 lines:"
            tail -3 "$LATEST_LOG" | sed 's/^/   /'
        else
            echo "   No log files found"
        fi
    fi
    
    echo ""
    echo "🔍 To monitor logs: tail -f logs/linkedin_agent_*.log"
    echo "🛑 To stop: ./stop_background.sh"
    
else
    echo "❌ LinkedIn Agent is NOT running (stale PID file)"
    echo "🧹 Cleaning up stale PID file"
    rm -f "$PID_FILE"
    echo "   To start: ./run_background.sh"
fi 