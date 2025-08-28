from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app import db
from models import Tenant
from models_multi_user import User
import re

tutorial_bp = Blueprint('tutorial', __name__)

def format_phone_display(phone):
    """Format phone for display: (555) 123-4567"""
    if not phone:
        return phone
    digits = re.sub(r'[^\d]', '', phone)
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
    return phone

@tutorial_bp.route('/personal')
def personal_tutorial():
    """Interactive tutorial for personal CallBunker system"""
    # Get the main tenant (shared system)
    tenant = Tenant.query.filter_by(screening_number='+16316417727').first()
    
    if not tenant:
        flash('Personal system not configured. Please contact support.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('tutorial/personal.html', 
                         tenant=tenant,
                         format_phone=format_phone_display)

@tutorial_bp.route('/multi-user/<int:user_id>')
def multi_user_tutorial(user_id):
    """Interactive tutorial for multi-user CallBunker system"""
    user = User.query.get_or_404(user_id)
    
    return render_template('tutorial/multi_user.html', 
                         user=user,
                         format_phone=format_phone_display)

@tutorial_bp.route('/step-progress', methods=['POST'])
def update_step_progress():
    """Track user progress through tutorial steps"""
    try:
        step_id = request.json.get('step_id')
        completed = request.json.get('completed', False)
        
        # Store in session for now (could be database later)
        if 'tutorial_progress' not in session:
            session['tutorial_progress'] = {}
        
        session['tutorial_progress'][step_id] = completed
        session.modified = True
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@tutorial_bp.route('/test-call', methods=['POST'])
def initiate_test_call():
    """Provide test call instructions"""
    try:
        system_type = request.json.get('system_type')  # 'personal' or 'multi-user'
        user_id = request.json.get('user_id')
        
        if system_type == 'personal':
            tenant = Tenant.query.filter_by(screening_number='+16316417727').first()
            if not tenant:
                return jsonify({'success': False, 'error': 'Personal system not found'})
            
            response = {
                'success': True,
                'call_number': '(617) 942-1250',  # User's Google Voice
                'pin': tenant.current_pin,
                'verbal_code': tenant.verbal_code,
                'callbunker_number': format_phone_display(tenant.screening_number),
                'instructions': 'Call your Google Voice number. You\'ll be asked for authentication.'
            }
        
        elif system_type == 'multi-user' and user_id:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'})
            
            response = {
                'success': True,
                'call_number': format_phone_display(user.google_voice_number),
                'pin': user.pin,
                'verbal_code': user.verbal_code,
                'callbunker_number': format_phone_display(user.assigned_twilio_number),
                'instructions': 'Call your Google Voice number. You\'ll be asked for authentication.'
            }
        
        else:
            return jsonify({'success': False, 'error': 'Invalid system type or missing user ID'})
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})