from flask import Blueprint, render_template, redirect, url_for, make_response
from utils.auth import require_admin_web

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard - redirect to TextNow signup"""
    return redirect(url_for('main.signup'))

@main_bp.route('/signup')
def signup():
    """Main signup page - now redirects to Google Voice setup"""
    response = make_response(redirect(url_for('admin.google_voice_setup')))
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
