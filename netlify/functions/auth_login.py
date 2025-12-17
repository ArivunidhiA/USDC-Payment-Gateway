"""
Netlify serverless function for OAuth login initiation.
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api'))

from flask import Flask, request, redirect, session
from flask_cors import CORS
from utils.auth import init_auth, google
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


@app.route('/.netlify/functions/auth_login', methods=['GET'])
@app.route('/api/auth/login', methods=['GET'])
def login():
    """Initiate Google OAuth login."""
    # Store frontend URL in session for after OAuth callback
    requested_redirect = request.args.get('redirect_uri')
    if requested_redirect:
        if requested_redirect.startswith('/'):
            frontend_url = FRONTEND_URL + requested_redirect
        else:
            frontend_url = requested_redirect
    else:
        frontend_url = FRONTEND_URL
    
    session['oauth_redirect_uri'] = frontend_url
    session.permanent = True
    session.modified = True
    
    # OAuth redirect URI must match exactly what's in Google Cloud Console
    callback_url = request.url_root.rstrip('/') + '/api/auth/callback'
    return google.authorize_redirect(callback_url)


# Netlify serverless function handler
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

