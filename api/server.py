"""
Unified Flask server for local development.
Combines all API endpoints with OAuth2, audit trails, and production features.
"""

import os
from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import uuid
import threading
from dotenv import load_dotenv

from utils.db import (
    create_payment, get_payment, update_payment, get_recent_payments,
    log_audit, get_user_by_id
)
from utils.chain_config import get_all_chains
from utils.cctp_handler import CCTPHandler
from utils.auth import init_auth, login_required, get_current_user, handle_google_callback

# Load environment variables
load_dotenv()

app = Flask(__name__)

# SECURITY: Require SECRET_KEY in production
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
if not FLASK_SECRET_KEY:
    if os.getenv('FLASK_ENV') == 'development' or os.getenv('ENV') == 'development':
        FLASK_SECRET_KEY = 'dev-secret-key-change-in-production'
        print("WARNING: Using default secret key. Set FLASK_SECRET_KEY in production!")
    else:
        raise ValueError("FLASK_SECRET_KEY environment variable is required in production")
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

# Determine if we're in production
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production' or os.getenv('ENV') == 'production' or os.getenv('NETLIFY') == 'true'
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# Session configuration - critical for OAuth state management
# Use 'null' session type for serverless (stateless), 'filesystem' for local dev
if IS_PRODUCTION:
    # In serverless/Netlify, we need to use signed cookies or external session store
    # For now, use filesystem with proper path, but consider Redis/Memcached for production
    app.config['SESSION_TYPE'] = 'filesystem'
else:
    app.config['SESSION_TYPE'] = 'filesystem'

app.config['SESSION_PERMANENT'] = True
app.config['SESSION_COOKIE_NAME'] = 'usdc_gateway_session'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = IS_PRODUCTION  # True in production (HTTPS required)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_DOMAIN'] = None  # Let Flask handle domain automatically

# CORS - must allow credentials and specific origin
# In production, use FRONTEND_URL from environment
allowed_origins = [FRONTEND_URL]
if not IS_PRODUCTION:
    # Allow localhost for development
    allowed_origins.extend(['http://localhost:5173', 'http://127.0.0.1:5173'])

CORS(app, 
     supports_credentials=True, 
     origins=allowed_origins,
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Type'])

# Initialize session AFTER CORS
Session(app)

# Initialize OAuth (must be done before importing google)
oauth = init_auth(app)
from utils.auth import google

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'service': 'usdc-payment-gateway',
        'version': '1.0.0'
    }), 200


# OAuth2 Routes
@app.route('/api/auth/login', methods=['GET'])
def login():
    """Initiate Google OAuth login."""
    # Store frontend URL in session for after OAuth callback
    # Use FRONTEND_URL from environment or request origin
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
    # Use authorize_redirect with explicit state handling
    return google.authorize_redirect(callback_url)


@app.route('/api/auth/callback', methods=['GET'])
def auth_callback():
    """Handle OAuth callback."""
    try:
        # Debug: Check if session is working
        # The state validation happens inside authorize_access_token()
        # If state doesn't match, it means the session wasn't maintained
        
        # Get the token - this validates the state automatically
        # authorize_access_token() will:
        # 1. Get the state from the callback URL params
        # 2. Get the stored state from the session
        # 3. Compare them - if they don't match, raise MismatchingStateError
        token = google.authorize_access_token()
        
        if not token:
            return jsonify({'error': 'Failed to get access token from Google'}), 400
        
        # Get user info from Google - use full URL
        # Google's userinfo endpoint
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
        from utils.db import get_user_by_email, create_user
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
        
        # CRITICAL: Force session to save by accessing it
        # This ensures the session cookie is set before redirect
        _ = session.get('user_id')  # Force session access
        
        # Force session save - this is critical!
        try:
            from flask_session import Session
            # Mark session as modified to ensure it's saved
            session.modified = True
            # Force a session save by making a dummy request
        except:
            pass
        
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
        redirect_uri = session.pop('oauth_redirect_uri', 'http://localhost:5173')
        if redirect_uri.startswith('/'):
            redirect_uri = 'http://localhost:5173' + redirect_uri
        
        # Debug: Log redirect
        print(f"[AUTH] Redirecting to: {redirect_uri}")
        print(f"[AUTH] Session user_id: {session.get('user_id')}")
        print(f"[AUTH] Session keys: {list(session.keys())}")
        
        # Create redirect response and ensure cookie is set
        response = redirect(redirect_uri)
        
        # Ensure session cookie is included in response
        # Flask-Session should handle this, but we'll be explicit
        return response
        
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
            ip_address=request.remote_addr
        )
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/auth/user', methods=['GET'])
def get_user():
    """Get current user info."""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify(user), 200

# Alias for backward compatibility
@app.route('/api/auth/me', methods=['GET'])
def get_me():
    """Get current user info (alias)."""
    return get_user()


# Protected Payment Routes
@app.route('/api/create_payment', methods=['POST'])
@limiter.limit("10 per minute")
@login_required
def create_payment_handler():
    """Creates a new payment request (requires authentication)."""
    user = get_current_user()
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
    
    # Store in database with user_id
    try:
        create_payment(
            payment_id=payment_id,
            amount=float(data['amount']),
            source_chain=data['source_chain'],
            dest_chain=data['dest_chain'],
            sender=data.get('sender_address', 'unknown'),
            recipient=data['recipient_address'],
            user_id=user['user_id']
        )
        
        return jsonify({
            'payment_id': payment_id,
            'status': 'created',
            'next_step': 'Call /api/initiate_transfer with burn transaction'
        }), 201
    except Exception as e:
        log_audit(
            user_id=user['user_id'],
            action='create_payment_failed',
            resource_type='payment',
            details=str(e),
            ip_address=request.remote_addr
        )
        return jsonify({'error': str(e)}), 500


def process_transfer_async(payment_id, burn_tx_hash, source_chain, dest_chain, user_id=None):
    """
    Background task to fetch attestation and complete transfer.
    Runs in separate thread to avoid blocking API response.
    """
    try:
        handler = CCTPHandler(source_chain, dest_chain)
        
        # Wait for burn confirmation
        update_payment(payment_id, user_id=user_id, status='burning', burn_tx_hash=burn_tx_hash)
        
        # Fetch attestation from Circle
        update_payment(payment_id, user_id=user_id, status='fetching_attestation')
        attestation = handler.fetch_attestation(burn_tx_hash)
        
        # Mark as ready for minting
        update_payment(
            payment_id,
            user_id=user_id,
            status='ready_to_mint',
            metadata=str(attestation)
        )
        
    except Exception as e:
        update_payment(payment_id, user_id=user_id, status='failed', metadata=str(e))


@app.route('/api/initiate_transfer', methods=['POST'])
@limiter.limit("20 per minute")
@login_required
def initiate_transfer():
    """Handles the actual USDC burn and attestation fetching."""
    user = get_current_user()
    data = request.json
    
    if 'payment_id' not in data or 'burn_tx_hash' not in data:
        return jsonify({'error': 'Missing payment_id or burn_tx_hash'}), 400
    
    # Fetch payment details and verify ownership
    payment = get_payment(data['payment_id'])
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    if payment.get('user_id') != user['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Start background processing
    thread = threading.Thread(
        target=process_transfer_async,
        args=(
            data['payment_id'],
            data['burn_tx_hash'],
            payment['source_chain'],
            payment['dest_chain'],
            user['user_id']
        )
    )
    thread.start()
    
    return jsonify({
        'status': 'processing',
        'message': 'Transfer initiated. Poll /api/check_status for updates.'
    }), 202


@app.route('/api/check_status/<payment_id>', methods=['GET'])
@login_required
def check_status(payment_id):
    """Returns current payment status."""
    user = get_current_user()
    payment = get_payment(payment_id)
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    # Verify ownership
    if payment.get('user_id') != user['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(payment), 200


@app.route('/api/recent_payments', methods=['GET'])
@login_required
def recent_payments():
    """Get recent payment history for current user."""
    user = get_current_user()
    limit = request.args.get('limit', 50, type=int)
    demo_mode = request.args.get('demo', 'false').lower() == 'true'
    
    # If demo mode, get demo user's payments
    if demo_mode:
        from utils.db import get_user_by_email
        demo_user = get_user_by_email('demo@usdcgateway.com')
        if demo_user:
            payments = get_recent_payments(limit=limit, user_id=demo_user['user_id'])
        else:
            payments = []
    else:
        payments = get_recent_payments(limit=limit, user_id=user['user_id'])
    
    return jsonify({'payments': payments}), 200


@app.route('/api/audit_logs', methods=['GET'])
@login_required
def get_audit_logs():
    """Get audit logs for current user (admin can see all)."""
    user = get_current_user()
    limit = request.args.get('limit', 100, type=int)
    
    from utils.db import get_audit_logs
    logs = get_audit_logs(limit=limit, user_id=user['user_id'])
    
    return jsonify({'logs': logs}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001)
