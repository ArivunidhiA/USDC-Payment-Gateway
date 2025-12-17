"""
Netlify serverless function for getting recent payments.
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api'))

from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.db import get_recent_payments
import serverless_wsgi

app = Flask(__name__)
CORS(app)


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

