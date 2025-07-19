#!/usr/bin/env python3
"""Minimal Flask test - no security middleware"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, send_file
import config

# Create minimal Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key-for-development'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Minimal Flask is running'})

@app.route('/upload', methods=['POST'])
def upload_test():
    return jsonify({'success': False, 'message': 'Upload disabled in minimal mode'})

if __name__ == '__main__':
    print("🧪 Starting MINIMAL Flask Test Server...")
    print("📡 URL: http://localhost:9000")
    print("🔧 All security middleware DISABLED for testing")
    print("")
    
    # Minimal Flask with no middleware
    app.run(debug=True, host='127.0.0.1', port=9000, threaded=True)
