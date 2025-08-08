#!/usr/bin/env python3
"""
Railway startup script - runs both health server and main workflow
"""

import threading
import time
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def start_health_server():
    """Start the health check server"""
    from health_server import start_health_server
    start_health_server()

def start_main_workflow():
    """Start the main LinkedIn agent workflow"""
    from automated_workflow import AutomatedWorkflow
    workflow = AutomatedWorkflow()
    workflow.start_automated_workflow()

def main():
    """Start both services"""
    print("🚀 Starting LinkedIn Agent on Railway...")
    
    # Start health server in a separate thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    print("✅ Health server started")
    
    # Give health server time to start
    time.sleep(2)
    
    # Start main workflow
    print("🔄 Starting main workflow...")
    start_main_workflow()

if __name__ == '__main__':
    main() 