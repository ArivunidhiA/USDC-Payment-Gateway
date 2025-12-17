"""
Returns current payment status.

Frontend polls this endpoint for real-time updates.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.db import get_payment, get_recent_payments

app = Flask(__name__)
CORS(app)


@app.route('/api/check_status/<payment_id>', methods=['GET'])
def check_status(payment_id):
    payment = get_payment(payment_id)
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    return jsonify(payment), 200


@app.route('/api/recent_payments', methods=['GET'])
def recent_payments():
    """Get recent payment history."""
    limit = request.args.get('limit', 50, type=int)
    payments = get_recent_payments(limit)
    
    return jsonify({'payments': payments}), 200


if __name__ == '__main__':
    app.run()

# Export for Vercel serverless
handler = app

