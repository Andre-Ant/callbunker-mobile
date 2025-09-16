from flask import Blueprint, render_template, redirect, url_for, make_response
from utils.auth import require_admin_web

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Root page - redirect to multi-user login"""
    return redirect(url_for('multi_user.login'))

@main_bp.route('/dashboard')
def dashboard():
    """Main dashboard - redirect to multi-user list"""
    return redirect(url_for('multi_user.user_list'))

@main_bp.route('/signup')
def signup():
    """Main signup page - redirect to multi-user signup"""
    response = make_response(redirect(url_for('multi_user.signup')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@main_bp.route('/carrier-forwarding')
def carrier_forwarding():
    """Better approach: Forward from existing phone number"""
    return render_template('carrier_forwarding.html')

@main_bp.route('/how-it-works')
def how_it_works():
    """Visual walkthrough of how CallBunker works with TextNow"""
    response = make_response(render_template('how_it_works_simple.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "CallBunker"}, 200

# Temporary bridge routes for /multi URLs until deployment is updated
@main_bp.route('/multi')
@main_bp.route('/multi/')
def multi_index():
    """Handle /multi requests - redirect to login"""
    return redirect(url_for('multi_user.login'))

@main_bp.route('/multi/login')
def multi_login_redirect():
    """Handle /multi/login requests - redirect to actual login"""
    return redirect(url_for('multi_user.login'))

@main_bp.route('/multi/test')
def multi_test_redirect():
    """Handle /multi/test requests - redirect to actual test page"""
    return redirect(url_for('multi_user.test_page'))

@main_bp.route('/multi/debug-auth')
def multi_debug_redirect():
    """Handle /multi/debug-auth requests - redirect to actual debug page"""
    return redirect(url_for('multi_user.debug_auth'))

@main_bp.route('/multi/signup')
def multi_signup_redirect():
    """Handle /multi/signup requests - redirect to actual signup page"""
    return redirect(url_for('multi_user.signup'))
