"""
Creates a new payment request.

Generates unique payment ID and stores initial payment data.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from utils.db import create_payment
from utils.chain_config import get_all_chains

app = Flask(__name__)
CORS(app)


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


if __name__ == '__main__':
    app.run()

# Export for Vercel serverless
handler = app

