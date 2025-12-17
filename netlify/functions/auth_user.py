"""
Netlify serverless function for getting current user info.
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api'))

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from utils.auth import init_auth, get_current_user
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


@app.route('/.netlify/functions/auth_user', methods=['GET'])
@app.route('/api/auth/user', methods=['GET'])
@app.route('/api/auth/me', methods=['GET'])
def get_user():
    """Get current user info."""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify(user), 200


# Netlify serverless function handler
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

