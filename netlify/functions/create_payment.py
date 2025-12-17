"""
Netlify serverless function for creating payment requests.
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api'))

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
from utils.db import create_payment
from utils.chain_config import get_all_chains
import serverless_wsgi

app = Flask(__name__)

# CORS configuration for production
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
CORS(app, 
     supports_credentials=True,
     origins=[FRONTEND_URL, 'http://localhost:5173', 'http://127.0.0.1:5173'],
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Type'])


@app.route('/.netlify/functions/create_payment', methods=['POST'])
@app.route('/api/create_payment', methods=['POST'])
def create_payment_handler():
    data = request.json
    
    # Validate required fields
    required = ['amount', 'source_chain', 'dest_chain', 'recipient_address']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate chains
    if data['source_chain'] not in get_all_chains():
        return jsonify({'error': 'Invalid source chain'}), 400
    
    if data['dest_chain'] not in get_all_chains():
        return jsonify({'error': 'Invalid destination chain'}), 400
    
    # Generate unique payment ID
    payment_id = str(uuid.uuid4())
    
    # Store in database
    create_payment(
        payment_id=payment_id,
        amount=float(data['amount']),
        source_chain=data['source_chain'],
        dest_chain=data['dest_chain'],
        sender=data.get('sender_address', 'unknown'),
        recipient=data['recipient_address']
    )
    
    return jsonify({
        'payment_id': payment_id,
        'status': 'created',
        'next_step': 'Call /api/initiate_transfer with burn transaction'
    }), 201


# Netlify serverless function handler
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

