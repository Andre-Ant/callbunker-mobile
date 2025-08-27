from flask import Blueprint, render_template, redirect, url_for
from utils.auth import require_admin_web

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard - redirect to admin"""
    return redirect(url_for('admin.admin_home'))

@main_bp.route('/signup')
def signup():
    """Simple user signup page"""
    return render_template('simple_onboarding.html')

@main_bp.route('/carrier-forwarding')
def carrier_forwarding():
    """Better approach: Forward from existing phone number"""
    return render_template('carrier_forwarding.html')

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "CallBunker"}, 200
