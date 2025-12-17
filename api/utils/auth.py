"""
OAuth2 authentication module using Google OAuth.

Handles user authentication, session management, and protected routes.
"""

import os
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from authlib.integrations.flask_client import OAuth
from .db import get_user_by_email, create_user

# Initialize OAuth
oauth = OAuth()

# Google OAuth configuration
# Note: authlib automatically handles state for CSRF protection
# The state is stored in the session by default
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


def init_auth(app):
    """Initialize OAuth with Flask app."""
    oauth.init_app(app)
    return oauth


def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current logged-in user from session."""
    if 'user_id' not in session:
        return None
    return {
        'user_id': session.get('user_id'),
        'email': session.get('email'),
        'name': session.get('name'),
        'picture': session.get('picture')
    }


def handle_google_callback():
    """Handle Google OAuth callback and create/login user."""
    from flask import request
    try:
        token = google.authorize_access_token()
        # Get user info from Google - use full URL
        # Google's userinfo endpoint
        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        resp = google.get(userinfo_url, token=token)
        user_info = resp.json()
        
        if not user_info:
            return None, 'Failed to get user info'
        
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')
        sub = user_info.get('sub')  # Google user ID
        
        if not email:
            return None, 'Email not provided by Google'
        
        # Get or create user
        user = get_user_by_email(email)
        if not user:
            # Create new user
            user_id = create_user(
                email=email,
                name=name,
                picture=picture,
                oauth_provider='google',
                oauth_id=sub
            )
        else:
            user_id = user['user_id']
        
        # Set session
        session['user_id'] = user_id
        session['email'] = email
        session['name'] = name
        session['picture'] = picture
        session.permanent = True
        
        return {
            'user_id': user_id,
            'email': email,
            'name': name,
            'picture': picture
        }, None
        
    except Exception as e:
        return None, str(e)

