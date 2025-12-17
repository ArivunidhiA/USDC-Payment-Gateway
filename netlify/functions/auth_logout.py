"""
Netlify serverless function for user logout.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api'))

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from utils.auth import init_auth
from utils.db import log_audit
import serverless_wsgi

app = Flask(__name__)

# SECURITY: Require SECRET_KEY
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
if not FLASK_SECRET_KEY:
    raise ValueError("FLASK_SECRET_KEY environment variable is required")
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

# Session configuration for serverless
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_COOKIE_NAME'] = 'usdc_gateway_session'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_DOMAIN'] = None

# Initialize session
Session(app)

# CORS configuration for production
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
IS_PRODUCTION = os.getenv('ENV') == 'production' or os.getenv('NETLIFY') == 'true'
allowed_origins = [FRONTEND_URL]
if not IS_PRODUCTION:
    allowed_origins.extend(['http://localhost:5173', 'http://127.0.0.1:5173'])

CORS(app, 
     supports_credentials=True,
     origins=allowed_origins,
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Type'])

# Initialize auth (must be after Session and CORS)
init_auth(app)


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

