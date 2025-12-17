"""
Netlify serverless function for user logout.
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api'))

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from utils.auth import init_auth
from utils.db import log_audit
import serverless_wsgi

app = Flask(__name__)

# Initialize auth
init_auth(app)

# CORS configuration for production
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
CORS(app, 
     supports_credentials=True,
     origins=[FRONTEND_URL, 'http://localhost:5173', 'http://127.0.0.1:5173'],
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Type'])


@app.route('/.netlify/functions/auth_logout', methods=['POST'])
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user."""
    user_id = session.get('user_id')
    if user_id:
        log_audit(
            user_id=user_id,
            action='logout',
            resource_type='user',
            resource_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
    
    # Clear session
    session.clear()
    
    return jsonify({'message': 'Logged out successfully'}), 200


# Netlify serverless function handler
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

