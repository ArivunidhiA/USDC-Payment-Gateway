"""
Netlify serverless function for getting current user info.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import utils
# From netlify/functions/auth_user/index.py, go up 3 levels to reach api/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../api'))

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from utils.auth import init_auth, get_current_user
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


@app.route('/', methods=['GET'])
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

