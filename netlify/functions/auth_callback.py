"""
Netlify serverless function for OAuth callback handling.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api'))

from flask import Flask, request, redirect, session, jsonify
from flask_cors import CORS
from flask_session import Session
from utils.auth import init_auth
from utils.db import get_user_by_email, create_user, log_audit
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
# Import google after init_auth
from utils.auth import google


@app.route('/', methods=['GET'])
@app.route('/.netlify/functions/auth_callback', methods=['GET'])
@app.route('/api/auth/callback', methods=['GET'])
def auth_callback():
    """Handle OAuth callback."""
    try:
        # Get the token - this validates the state automatically
        token = google.authorize_access_token()
        
        if not token:
            return jsonify({'error': 'Failed to get access token from Google'}), 400
        
        # Get user info from Google - use full URL
        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        resp = google.get(userinfo_url, token=token)
        
        if resp.status_code != 200:
            return jsonify({'error': f'Failed to get user info: {resp.status_code}'}), 400
        
        user_info = resp.json()
        
        if not user_info or not user_info.get('email'):
            return jsonify({'error': 'Email not provided by Google'}), 400
        
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')
        sub = user_info.get('sub')
        
        # Get or create user
        user = get_user_by_email(email)
        if not user:
            user_id = create_user(
                email=email,
                name=name,
                picture=picture,
                oauth_provider='google',
                oauth_id=sub
            )
        else:
            user_id = user['user_id']
        
        # Set session data - CRITICAL: Must set before redirect
        session['user_id'] = user_id
        session['email'] = email
        session['name'] = name
        session['picture'] = picture
        session.permanent = True
        session.modified = True
        
        # Log login
        log_audit(
            user_id=user_id,
            action='login',
            resource_type='user',
            resource_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # Get redirect URI from session (set during login)
        redirect_uri = session.pop('oauth_redirect_uri', FRONTEND_URL)
        if redirect_uri.startswith('/'):
            redirect_uri = FRONTEND_URL + redirect_uri
        
        # Create redirect response
        return redirect(redirect_uri)
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        # If it's a state mismatch, provide helpful error
        if 'mismatching_state' in error_msg or 'MismatchingStateError' in error_trace:
            return jsonify({
                'error': 'Session expired or cookies not enabled. Please try again.',
                'details': 'The OAuth state parameter doesn\'t match. This usually means:\n1. Cookies are disabled\n2. Session storage failed\n3. You\'re using a different browser/session\n\nPlease clear cookies and try again, or use the same browser window.',
                'traceback': error_trace
            }), 400
        
        return jsonify({
            'error': error_msg,
            'traceback': error_trace
        }), 500


# Netlify serverless function handler
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

