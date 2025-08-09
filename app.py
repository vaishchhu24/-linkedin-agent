#!/usr/bin/env python3
"""
Main Flask app for Railway deployment
Handles health checks and runs LinkedIn agent
"""

from flask import Flask, jsonify
import threading
import time
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Global flag to track if agent is running
agent_running = False

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy",
        "agent_running": agent_running,
        "service": "linkedin-agent"
    })

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "LinkedIn Agent is running",
        "status": "operational",
        "agent_running": agent_running
    })

def start_linkedin_agent():
    """Start the LinkedIn agent in background"""
    global agent_running
    try:
        from automated_workflow import AutomatedWorkflow
        workflow = AutomatedWorkflow()
        agent_running = True
        workflow.start_automated_workflow()
    except Exception as e:
        print(f"Error starting LinkedIn agent: {e}")
        agent_running = False

def start_agent_thread():
    """Start LinkedIn agent in a separate thread"""
    agent_thread = threading.Thread(target=start_linkedin_agent, daemon=True)
    agent_thread.start()
    print("✅ LinkedIn agent thread started")

if __name__ == '__main__':
    # Start LinkedIn agent in background
    start_agent_thread()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 