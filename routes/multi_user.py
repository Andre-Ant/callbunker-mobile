"""
CallBunker Business Routes - Each user gets their own Twilio number
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from models_multi_user import User, TwilioPhonePool, UserWhitelist
from app import db
from utils.twilio_helpers import twilio_client
import re

multi_user_bp = Blueprint('multi_user', __name__, url_prefix='/multi')

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
        
        # Validation
        if not all([email, name, google_voice_number, real_phone_number]):
            flash('All fields are required', 'error')
            return render_template('multi_user/signup.html')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('multi_user/signup.html')
        
        # Check if Google Voice number already registered
        if User.query.filter_by(google_voice_number=google_voice_number).first():
            flash('Google Voice number already registered', 'error')
            return render_template('multi_user/signup.html')
        
        # Get next available Twilio number
        available_twilio = TwilioPhonePool.query.filter_by(is_assigned=False).first()
        if not available_twilio:
            flash('No CallBunker numbers available. Please contact support.', 'error')
            return render_template('multi_user/signup.html')
        
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
        
        # Mark Twilio number as assigned
        available_twilio.is_assigned = True
        available_twilio.assigned_to_user_id = user.id
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created! Your CallBunker number is {format_phone_display(user.assigned_twilio_number)}', 'success')
        return redirect(url_for('multi_user.user_dashboard', user_id=user.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Registration failed: {str(e)}', 'error')
        return render_template('multi_user/signup.html')

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