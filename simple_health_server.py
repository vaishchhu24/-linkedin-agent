#!/usr/bin/env python3
"""
Simple health check server for Railway
"""

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/')
def root():
    return jsonify({"message": "LinkedIn Agent Running"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port) 