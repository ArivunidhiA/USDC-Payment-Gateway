"""
Netlify serverless function for checking payment status.
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api'))

from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.db import get_payment, get_recent_payments
import serverless_wsgi

app = Flask(__name__)
CORS(app)


@app.route('/.netlify/functions/check_status/<payment_id>', methods=['GET'])
@app.route('/api/check_status/<payment_id>', methods=['GET'])
def check_status(payment_id):
    payment = get_payment(payment_id)
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    return jsonify(payment), 200


# Netlify serverless function handler
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

