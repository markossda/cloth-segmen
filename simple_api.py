#!/usr/bin/env python3
"""
Simple API Test - Just Flask basics
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'Simple Test API',
        'status': 'running',
        'version': '1.0.0',
        'message': 'Flask is working!'
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'message': 'All systems operational'
    }), 200

@app.route('/test', methods=['POST'])
def test_endpoint():
    try:
        data = request.get_json()
        return jsonify({
            'success': True,
            'received': data,
            'message': 'Test endpoint working'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"💡 Simple server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)