"""
Demo routes to showcase both CallBunker systems
"""
from flask import Blueprint, render_template
from models import Tenant
from models_multi_user import User, TwilioPhonePool
from app import db

demo_bp = Blueprint('demo', __name__, url_prefix='/demo')

@demo_bp.route('/systems')
def compare_systems():
    """Compare personal vs business CallBunker systems"""
    
    # Get current system stats
    personal_tenants = Tenant.query.count()
    business_users = User.query.count()
    available_slots = TwilioPhonePool.query.filter_by(is_assigned=False).count()
    
    return render_template('demo/systems_comparison.html',
                         personal_tenants=personal_tenants,
                         business_users=business_users,
                         available_slots=available_slots)