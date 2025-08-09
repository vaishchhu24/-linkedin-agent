#!/usr/bin/env python3
"""
Debug version of Flask app to identify health check issues
"""

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health():
    """Simple health check"""
    return jsonify({"status": "healthy"})

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({"message": "LinkedIn Agent Debug Mode"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Starting debug Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 