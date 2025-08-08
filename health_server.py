#!/usr/bin/env python3
"""
Simple health check server for Railway deployment
"""

from flask import Flask, jsonify
import threading
import os

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy",
        "service": "linkedin-agent",
        "environment": os.getenv('ENVIRONMENT', 'production')
    })

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "LinkedIn Agent is running",
        "status": "operational"
    })

def start_health_server():
    """Start the health check server in a separate thread"""
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    start_health_server() 