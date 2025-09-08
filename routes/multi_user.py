"""
CallBunker Business Routes - Each user gets their own Twilio number
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from models_multi_user import User, TwilioPhonePool, UserWhitelist
from app import db
from utils.twilio_helpers import twilio_client
import re

multi_user_bp = Blueprint('multi_user', __name__, url_prefix='/multi')

@multi_user_bp.route('/')
def user_list():
    """List all users for easy dashboard access"""
    users = User.query.all()
    return render_template('multi_user/user_list.html', 
                         users=users,
                         format_phone=format_phone_display)

def normalize_phone(phone):
    """Normalize phone number to digits only"""
    return re.sub(r'[^\d]', '', phone)

def format_phone_display(phone):
    """Format phone for display: (555) 123-4567"""
    digits = normalize_phone(phone)
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
    return phone

@multi_user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """New user signup with Google Voice integration"""
    if request.method == 'GET':
        # Check available Twilio numbers
        available_numbers = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        return render_template('multi_user/signup.html', available_numbers=available_numbers)
    
    try:
        # Get form data
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        google_voice_number = normalize_phone(request.form.get('google_voice_number', '').strip())
        real_phone_number = normalize_phone(request.form.get('real_phone_number', '').strip())
        
        # Check available numbers for template
        available_numbers = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        
        # Validation
        if not all([email, name, google_voice_number, real_phone_number]):
            flash('All fields are required', 'error')
            return render_template('multi_user/signup.html', available_numbers=available_numbers)
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('multi_user/signup.html', available_numbers=available_numbers)
        
        # Check if Google Voice number already registered
        if User.query.filter_by(google_voice_number=google_voice_number).first():
            flash('Google Voice number already registered', 'error')
            return render_template('multi_user/signup.html', available_numbers=available_numbers)
        
        # Get next available Twilio number with database lock to prevent race conditions
        available_twilio = TwilioPhonePool.query.filter_by(is_assigned=False).with_for_update().first()
        if not available_twilio:
            flash('No CallBunker numbers available. Please contact support.', 'error')
            return render_template('multi_user/signup.html', available_numbers=0)
        
        # Create new user
        user = User(
            email=email,
            name=name,
            google_voice_number=google_voice_number,
            real_phone_number=real_phone_number,
            assigned_twilio_number=available_twilio.phone_number,
            pin=request.form.get('pin', '1122').strip(),
            verbal_code=request.form.get('verbal_code', 'open sesame').strip()
        )
        
        # Mark Twilio number as assigned and save everything in one transaction
        available_twilio.is_assigned = True
        
        db.session.add(user)
        db.session.flush()  # Get user.id without committing
        
        available_twilio.assigned_to_user_id = user.id
        db.session.commit()
        
        flash(f'Account created! Your Defense Number is {format_phone_display(user.assigned_twilio_number)}', 'success')
        return redirect(url_for('multi_user.user_dashboard', user_id=user.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Registration failed: {str(e)}', 'error')
        available_numbers = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        return render_template('multi_user/signup.html', available_numbers=available_numbers)

@multi_user_bp.route('/user/<int:user_id>/dashboard')
def user_dashboard(user_id):
    """Individual user dashboard"""
    user = User.query.get_or_404(user_id)
    
    # Get user statistics
    whitelist_count = UserWhitelist.query.filter_by(user_id=user_id).count()
    
    return render_template('multi_user/dashboard.html', 
                         user=user, 
                         whitelist_count=whitelist_count,
                         format_phone=format_phone_display)

@multi_user_bp.route('/admin/phone-pool')
def admin_phone_pool():
    """Admin view of Twilio phone number pool"""
    phones = TwilioPhonePool.query.all()
    return render_template('multi_user/admin_pool.html', phones=phones, format_phone=format_phone_display)

@multi_user_bp.route('/admin/add-twilio-number', methods=['POST'])
def add_twilio_number():
    """Add new Twilio number to the pool"""
    try:
        phone_number = request.form.get('phone_number', '').strip()
        monthly_cost = float(request.form.get('monthly_cost', 1.00))
        
        # Normalize phone number
        normalized = normalize_phone(phone_number)
        if len(normalized) != 10 and len(normalized) != 11:
            return jsonify({'success': False, 'message': 'Invalid phone number format'})
        
        # Add to pool
        pool_entry = TwilioPhonePool(
            phone_number=f"+1{normalized}" if len(normalized) == 10 else f"+{normalized}",
            monthly_cost=monthly_cost
        )
        
        db.session.add(pool_entry)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Added {format_phone_display(pool_entry.phone_number)} to pool'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# API Endpoints for Mobile App  
@multi_user_bp.route('/lookup-user', methods=['POST'])
def lookup_user():
    """Look up user ID by email for demo purposes"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({'user_id': user.id, 'name': user.name})
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/contacts', methods=['GET'])
def api_get_contacts(user_id):
    """Get trusted contacts for mobile app"""
    user = User.query.get_or_404(user_id)
    contacts = UserWhitelist.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': contact.id,
        'phone_number': contact.caller_number,
        'display_name': format_phone_display(contact.caller_number),
        'custom_pin': contact.custom_pin,
        'created_at': contact.created_at.isoformat() if contact.created_at else None
    } for contact in contacts])

@multi_user_bp.route('/user/<int:user_id>/contacts', methods=['POST'])
def api_add_contact(user_id):
    """Add trusted contact for mobile app"""
    user = User.query.get_or_404(user_id)
    
    try:
        data = request.get_json()
        phone_number = normalize_phone(data.get('phone_number', ''))
        custom_pin = data.get('custom_pin', '').strip()
        
        if len(phone_number) < 10:
            return jsonify({'error': 'Invalid phone number'}), 400
        
        # Check if already exists
        existing = UserWhitelist.query.filter_by(
            user_id=user_id, 
            caller_number=phone_number
        ).first()
        if existing:
            return jsonify({'error': 'Contact already exists'}), 400
        
        contact = UserWhitelist(
            user_id=user_id,
            caller_number=phone_number,
            custom_pin=custom_pin
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'id': contact.id,
            'phone_number': contact.caller_number,
            'display_name': format_phone_display(contact.caller_number),
            'custom_pin': contact.custom_pin
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/contacts/<int:contact_id>', methods=['DELETE'])
def api_delete_contact(user_id, contact_id):
    """Delete trusted contact for mobile app"""
    user = User.query.get_or_404(user_id)
    contact = UserWhitelist.query.filter_by(id=contact_id, user_id=user_id).first_or_404()
    
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/calls', methods=['GET'])
def api_get_calls(user_id):
    """Get call history for mobile app"""
    user = User.query.get_or_404(user_id)
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # For now, return empty list - call logging will be implemented with actual calls
    return jsonify([])

@multi_user_bp.route('/user/<int:user_id>/calls/<int:call_id>/complete', methods=['POST'])
def api_complete_call(user_id, call_id):
    """Complete a call for mobile app"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # For now, just return success - call logging will be implemented
    return jsonify({'success': True, 'call_id': call_id})

@multi_user_bp.route('/user/<int:user_id>/calls/<int:call_id>/status', methods=['GET'])
def api_get_call_status(user_id, call_id):
    """Get call status for mobile app"""
    user = User.query.get_or_404(user_id)
    
    # For now, return basic status - will be enhanced with real call data
    return jsonify({'call_id': call_id, 'status': 'completed'})

def get_user_by_twilio_number(twilio_number):
    """Helper to find user by their assigned Twilio number"""
    return User.query.filter_by(assigned_twilio_number=twilio_number).first()

def setup_twilio_webhook(phone_number):
    """Configure Twilio webhook for a phone number"""
    try:
        client = twilio_client()
        # Update the phone number's webhook URL
        # This would point to /multi/voice/incoming/{phone_number}
        webhook_url = f"{request.url_root}multi/voice/incoming/{normalize_phone(phone_number)}"
        
        # Find and update the Twilio phone number
        numbers = client.incoming_phone_numbers.list()
        for number in numbers:
            if number.phone_number == phone_number:
                number.update(voice_url=webhook_url, voice_method='POST')
                return True
        return False
    except Exception as e:
        print(f"Failed to configure Twilio webhook for {phone_number}: {e}")
        return False
@multi_user_bp.route('/contact-support')
def contact_support():
    """Support contact page for users needing help"""
    return render_template('multi_user/contact_support.html')
