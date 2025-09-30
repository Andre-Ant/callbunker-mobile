"""
CallBunker Phone Pool Admin Dashboard
Monitor and manage phone number provisioning
"""
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for, session
from models_multi_user import TwilioPhonePool, User
from utils.phone_provisioning import phone_provisioning
from app import db
from datetime import datetime
from functools import wraps
import logging
import os

logger = logging.getLogger(__name__)

phone_admin_bp = Blueprint('phone_admin', __name__, url_prefix='/admin/phones')

def require_admin_auth(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for admin session
        if not session.get('admin_authenticated'):
            # Check for API key in header or query param
            api_key = request.headers.get('X-Admin-API-Key') or request.args.get('api_key')
            admin_api_key = os.environ.get('ADMIN_API_KEY')
            
            if not admin_api_key or api_key != admin_api_key:
                return jsonify({'error': 'Unauthorized - Admin authentication required'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@phone_admin_bp.route('/dashboard')
@require_admin_auth
def dashboard():
    """Phone pool monitoring dashboard"""
    pool_status = phone_provisioning.get_pool_status()
    
    # Get recent assignments
    recent_assignments = TwilioPhonePool.query.filter_by(is_assigned=True).order_by(
        TwilioPhonePool.assigned_at.desc()
    ).limit(10).all()
    
    # Get available numbers
    available_numbers = TwilioPhonePool.query.filter_by(is_assigned=False).order_by(
        TwilioPhonePool.created_at.desc()
    ).all()
    
    return render_template('admin/phone_dashboard.html',
                         pool_status=pool_status,
                         recent_assignments=recent_assignments,
                         available_numbers=available_numbers)

@phone_admin_bp.route('/api/status')
@require_admin_auth
def api_status():
    """Get pool status as JSON"""
    pool_status = phone_provisioning.get_pool_status()
    return jsonify(pool_status)

@phone_admin_bp.route('/api/purchase', methods=['POST'])
@require_admin_auth
def api_purchase():
    """Purchase phone numbers"""
    data = request.get_json() or {}
    count = int(data.get('count', 1))
    area_code = data.get('area_code')
    
    if count < 1 or count > 50:
        return jsonify({'error': 'Count must be between 1 and 50'}), 400
    
    try:
        purchased = phone_provisioning.purchase_batch(count=count, area_code=area_code)
        
        new_status = phone_provisioning.get_pool_status()
        
        return jsonify({
            'success': True,
            'purchased_count': len(purchased),
            'purchased_numbers': [p.phone_number for p in purchased],
            'new_status': new_status
        })
    except Exception as e:
        logger.error(f"Purchase failed: {e}")
        return jsonify({'error': str(e)}), 500

@phone_admin_bp.route('/api/replenish', methods=['POST'])
@require_admin_auth
def api_replenish():
    """Trigger pool replenishment"""
    try:
        result = phone_provisioning.check_and_replenish()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Replenishment failed: {e}")
        return jsonify({'error': str(e)}), 500

@phone_admin_bp.route('/api/configure-webhooks', methods=['POST'])
@require_admin_auth
def api_configure_webhooks():
    """Configure webhooks for all numbers"""
    try:
        result = phone_provisioning.configure_all_webhooks()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Webhook configuration failed: {e}")
        return jsonify({'error': str(e)}), 500

@phone_admin_bp.route('/api/numbers')
@require_admin_auth
def api_numbers():
    """Get all phone numbers in pool"""
    numbers = TwilioPhonePool.query.order_by(TwilioPhonePool.created_at.desc()).all()
    
    return jsonify([
        {
            'id': n.id,
            'phone_number': n.phone_number,
            'is_assigned': n.is_assigned,
            'assigned_to_user_id': n.assigned_to_user_id,
            'webhook_configured': n.webhook_configured,
            'created_at': n.created_at.isoformat() if n.created_at else None,
            'assigned_at': n.assigned_at.isoformat() if n.assigned_at else None,
        }
        for n in numbers
    ])

@phone_admin_bp.route('/cron/auto-replenish', methods=['POST', 'GET'])
@require_admin_auth
def cron_auto_replenish():
    """
    Scheduled job endpoint for automatic pool replenishment
    
    Can be called by:
    - Replit scheduled deployments
    - External cron services (like cron-job.org)
    - UptimeRobot monitoring
    
    Example cron schedule: Call every 4 hours
    """
    try:
        logger.info("Automatic replenishment cron job triggered")
        
        result = phone_provisioning.check_and_replenish()
        
        response = {
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'result': result
        }
        
        logger.info(f"Cron job completed: {response}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Cron job failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
