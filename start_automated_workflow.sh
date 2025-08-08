#!/bin/bash

# Automated LinkedIn Content Workflow Startup Script
# This script starts the automated workflow that sends daily emails at 10 AM UK time
# and processes replies immediately

echo "🚀 Starting Automated LinkedIn Content Workflow"
echo "================================================"
echo "📧 Client: Sam Eaton"
echo "📧 Email: vaishnavisingh24011@gmail.com"
echo "⏰ Schedule: Daily at 10:00 AM UK time"
echo "🔄 Reply monitoring: Continuous"
echo "================================================"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python3 -c "import apscheduler" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing APScheduler..."
    pip3 install apscheduler
fi

# Start the automated workflow
echo "🚀 Starting automated workflow..."
echo "🛑 Press Ctrl+C to stop the system"
echo ""

python3 automated_workflow.py 