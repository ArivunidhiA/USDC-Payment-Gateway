"""
Netlify serverless function for getting recent payments.
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api'))

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from utils.db import get_recent_payments
import serverless_wsgi

app = Flask(__name__)

# CORS configuration for production
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
CORS(app, 
     supports_credentials=True,
     origins=[FRONTEND_URL, 'http://localhost:5173', 'http://127.0.0.1:5173'],
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Type'])


@app.route('/.netlify/functions/recent_payments', methods=['GET'])
@app.route('/api/recent_payments', methods=['GET'])
def recent_payments():
    """Get recent payment history."""
    limit = request.args.get('limit', 50, type=int)
    payments = get_recent_payments(limit)
    
    return jsonify({'payments': payments}), 200


# Netlify serverless function handler
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

