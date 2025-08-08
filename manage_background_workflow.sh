#!/bin/bash

# LinkedIn Background Workflow Management Script
# This script provides easy commands to manage the background workflow system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_SCRIPT="$SCRIPT_DIR/background_workflow_system.py"
PID_FILE="$SCRIPT_DIR/background_workflow.pid"
LOG_FILE="$SCRIPT_DIR/background_workflow.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Function to check if workflow is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            # Process not running, remove stale PID file
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start the workflow
start_workflow() {
    print_info "Starting LinkedIn Background Workflow System..."
    
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_warning "Workflow is already running (PID: $pid)"
        return 1
    fi
    
    # Start the workflow in background
    nohup python3 "$WORKFLOW_SCRIPT" start > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Wait a moment for the process to start
    sleep 2
    
    # Check if it started successfully
    if is_running; then
        print_status "Background workflow started successfully (PID: $pid)"
        print_info "Logs are being written to: $LOG_FILE"
        print_info "Email schedule: 9 AM, 10 AM, 11 AM UK time"
        return 0
    else
        print_error "Failed to start background workflow"
        print_info "Check logs at: $LOG_FILE"
        return 1
    fi
}

# Function to stop the workflow
stop_workflow() {
    print_info "Stopping LinkedIn Background Workflow System..."
    
    if ! is_running; then
        print_warning "Workflow is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    
    # Send SIGTERM for graceful shutdown
    kill -TERM "$pid" 2>/dev/null
    
    # Wait for graceful shutdown
    local count=0
    while [ $count -lt 30 ] && is_running; do
        sleep 1
        ((count++))
    done
    
    # Force kill if still running
    if is_running; then
        print_warning "Process didn't stop gracefully, forcing termination..."
        kill -KILL "$pid" 2>/dev/null
        sleep 1
    fi
    
    if ! is_running; then
        print_status "Background workflow stopped successfully"
        return 0
    else
        print_error "Failed to stop background workflow"
        return 1
    fi
}

# Function to restart the workflow
restart_workflow() {
    print_info "Restarting LinkedIn Background Workflow System..."
    
    stop_workflow
    sleep 2
    start_workflow
}

# Function to show status
show_status() {
    print_info "LinkedIn Background Workflow System Status"
    echo "================================================"
    
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_status "Status: Running (PID: $pid)"
        
        # Show recent logs
        if [ -f "$LOG_FILE" ]; then
            echo ""
            print_info "Recent logs (last 10 lines):"
            echo "--------------------------------"
            tail -n 10 "$LOG_FILE"
        fi
    else
        print_error "Status: Not running"
    fi
    
    echo ""
    print_info "Email Schedule:"
    echo "  • Email 1: 9:00 AM UK time"
    echo "  • Email 2: 10:00 AM UK time" 
    echo "  • Email 3: 11:00 AM UK time"
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_info "Showing background workflow logs:"
        echo "====================================="
        tail -f "$LOG_FILE"
    else
        print_error "Log file not found: $LOG_FILE"
    fi
}

# Function to show help
show_help() {
    echo "LinkedIn Background Workflow Management Script"
    echo "============================================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the background workflow system"
    echo "  stop      - Stop the background workflow system"
    echo "  restart   - Restart the background workflow system"
    echo "  status    - Show current status and recent logs"
    echo "  logs      - Show live logs (follow mode)"
    echo "  help      - Show this help message"
    echo ""
    echo "Features:"
    echo "  • Sends 3 daily emails at 1-hour intervals"
    echo "  • Continuous email monitoring"
    echo "  • AI-powered content generation"
    echo "  • RAG-enhanced learning"
    echo "  • Client feedback processing"
    echo ""
    echo "Files:"
    echo "  Script: $WORKFLOW_SCRIPT"
    echo "  PID File: $PID_FILE"
    echo "  Log File: $LOG_FILE"
}

# Main script logic
case "${1:-help}" in
    start)
        start_workflow
        ;;
    stop)
        stop_workflow
        ;;
    restart)
        restart_workflow
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 