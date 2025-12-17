"""
Handles the actual USDC burn and attestation fetching.

This is called after user approves transaction in their wallet.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.cctp_handler import CCTPHandler
from utils.db import get_payment, update_payment
import threading

app = Flask(__name__)
CORS(app)


def process_transfer_async(payment_id, burn_tx_hash, source_chain, dest_chain):
    """
    Background task to fetch attestation and complete transfer.
    Runs in separate thread to avoid blocking API response.
    """
    try:
        handler = CCTPHandler(source_chain, dest_chain)
        
        # Wait for burn confirmation
        update_payment(payment_id, status='burning', burn_tx_hash=burn_tx_hash)
        
        # Fetch attestation from Circle
        update_payment(payment_id, status='fetching_attestation')
        attestation = handler.fetch_attestation(burn_tx_hash)
        
        # Mark as ready for minting
        update_payment(
            payment_id, 
            status='ready_to_mint',
            metadata=str(attestation)
        )
        
    except Exception as e:
        update_payment(payment_id, status='failed', metadata=str(e))


@app.route('/api/initiate_transfer', methods=['POST'])
def initiate_transfer():
    data = request.json
    
    if 'payment_id' not in data or 'burn_tx_hash' not in data:
        return jsonify({'error': 'Missing payment_id or burn_tx_hash'}), 400
    
    # Fetch payment details
    payment = get_payment(data['payment_id'])
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    # Start background processing
    thread = threading.Thread(
        target=process_transfer_async,
        args=(
            data['payment_id'],
            data['burn_tx_hash'],
            payment['source_chain'],
            payment['dest_chain']
        )
    )
    thread.start()
    
    return jsonify({
        'status': 'processing',
        'message': 'Transfer initiated. Poll /api/check_status for updates.'
    }), 202


if __name__ == '__main__':
    app.run()

# Export for Vercel serverless
handler = app

