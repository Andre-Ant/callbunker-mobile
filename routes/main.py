from flask import Blueprint, render_template, redirect, url_for
from utils.auth import require_admin_web

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard - redirect to admin"""
    return redirect(url_for('admin.admin_home'))

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "CallBunker"}, 200
