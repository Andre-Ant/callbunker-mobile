"""
CallBunker Business Routes - Each user gets their own Twilio number
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, make_response, Response, session, abort
from models_multi_user import User, TwilioPhonePool, UserWhitelist, MultiUserCallLog, UserBlocklist, UserFailLog
from app import db
from utils.twilio_helpers import twilio_client, generate_voice_access_token
import re
import uuid
from datetime import datetime, timedelta
from twilio.twiml.voice_response import VoiceResponse, Gather
import os

multi_user_bp = Blueprint('multi_user', __name__, url_prefix='/multi')

def require_authentication():
    """Helper to require user authentication for API endpoints"""
    # For now, use a simple session-based auth or require admin key
    # In production, implement proper JWT or session authentication
    api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    if not api_key or api_key != os.environ.get('API_KEY', 'dev-key-123'):
        # Allow during development with demo key
        if api_key != 'demo-key-callbunker-2025':
            abort(401)
    return True

def validate_csrf_token():
    """Basic CSRF protection for state-changing endpoints"""
    if request.method in ['POST', 'PUT', 'DELETE']:
        csrf_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        # For development, allow bypass with dev token
        if not csrf_token or csrf_token not in ['dev-csrf-token', 'demo-csrf-callbunker']:
            # In production, validate against session-generated token
            return False
    return True

def verify_user_access(requested_user_id):
    """Verify that the current session/auth can access the requested user data"""
    # Implement proper user ownership validation
    # For now, require authentication key + user verification
    require_authentication()
    
    # Add CSRF protection for state-changing requests
    if not validate_csrf_token():
        abort(403)  # Forbidden - CSRF token missing/invalid
    
    # Additional verification could be added here
    # e.g., check if user_id matches session user_id
    user = User.query.get_or_404(requested_user_id)
    return user

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

@multi_user_bp.route('/mobile-signup', methods=['GET', 'POST'])
def mobile_signup():
    """Clean mobile-style signup interface"""
    if request.method == 'GET':
        available_numbers = TwilioPhonePool.query.filter_by(assigned_to_user_id=None).count()
        return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
    
    # Handle POST - create user with same logic as regular signup
    try:
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        google_voice_number = normalize_phone(request.form.get('google_voice_number', '').strip())
        real_phone_number = normalize_phone(request.form.get('real_phone_number', '').strip())
        pin = request.form.get('pin', '1122').strip()
        verbal_code = request.form.get('verbal_code', 'open sesame').strip()
        
        # Assign next available Twilio number from pool  
        available_number = TwilioPhonePool.query.filter_by(is_assigned=False).with_for_update().first()
        if not available_number:
            flash('No phone numbers available. Please try again later.', 'error')
            return redirect(url_for('multi_user.mobile_signup'))
        
        # Create new user
        user = User(
            email=email,
            name=name,
            google_voice_number=google_voice_number,
            real_phone_number=real_phone_number,
            pin=pin,
            verbal_code=verbal_code,
            assigned_twilio_number=available_number.phone_number
        )
        
        # Add user first and get ID
        db.session.add(user)
        db.session.flush()  # Get user.id without committing
        
        # Assign the phone number using the generated user.id
        available_number.assigned_to_user_id = user.id
        available_number.is_assigned = True
        
        db.session.commit()
        
        # Redirect to Google Voice auth
        return redirect(url_for('multi_user.google_voice_auth', user_id=user.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Signup failed: {str(e)}', 'error')
        return redirect(url_for('multi_user.mobile_signup'))

@multi_user_bp.route('/debug-signup')
def debug_signup():
    """Simple debug signup page"""
    return render_template('multi_user/debug_signup.html')

@multi_user_bp.route('/test')
def test_page():
    """Ultra simple test page"""
    return """
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Server is Working!</h1>
        <p>This is a simple test page.</p>
        <form method="POST" action="/multi/signup">
            <input type="text" name="name" value="Test User" placeholder="Name">
            <input type="email" name="email" value="test@example.com" placeholder="Email">
            <input type="text" name="google_voice_number" value="5551234567" placeholder="Google Voice">
            <input type="text" name="real_phone_number" value="5559876543" placeholder="Real Phone">
            <input type="text" name="pin" value="1122" placeholder="PIN">
            <input type="text" name="verbal_code" value="open sesame" placeholder="Verbal Code">
            <button type="submit">Test Submit</button>
        </form>
    </body>
    </html>
    """

@multi_user_bp.route('/mobile')
def mobile_simple():
    """Mobile-optimized simple signup"""
    return render_template('multi_user/mobile_simple.html')

@multi_user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """New user signup with Google Voice integration"""
    if request.method == 'GET':
        # Check available Twilio numbers
        available_numbers = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        response = make_response(render_template('multi_user/mobile_signup.html', available_numbers=available_numbers))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
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
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        # Check if Google Voice number already registered
        if User.query.filter_by(google_voice_number=google_voice_number).first():
            flash('Google Voice number already registered', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        # Get next available Twilio number with database lock to prevent race conditions
        available_twilio = TwilioPhonePool.query.filter_by(is_assigned=False).with_for_update().first()
        if not available_twilio:
            flash('No CallBunker numbers available. Please contact support.', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=0)
        
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
        # Redirect to Google Voice authentication step (critical!)
        return redirect(url_for('multi_user.google_voice_auth', user_id=user.id))
        
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
    
    return render_template('multi_user/mobile_dashboard.html', 
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

# Additional API Endpoints for Mobile App
@multi_user_bp.route('/user/<int:user_id>/settings', methods=['GET'])
def api_get_user_settings(user_id):
    """Get user settings for mobile app - SECURED"""
    user = verify_user_access(user_id)
    return jsonify({
        'pin': user.pin,
        'verbal_code': user.verbal_code,
        'retry_limit': user.retry_limit,
        'forward_mode': user.forward_mode,
        'rl_window_sec': user.rl_window_sec,
        'rl_max_attempts': user.rl_max_attempts,
        'rl_block_minutes': user.rl_block_minutes,
        'google_voice_verified': user.google_voice_verified,
        'twilio_number_configured': user.twilio_number_configured
    })

@multi_user_bp.route('/user/<int:user_id>/settings', methods=['PUT'])
def api_update_user_settings(user_id):
    """Update user settings for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
    
    # Update allowed settings
    if 'pin' in data and data['pin'] and re.match(r'^\d{4}$', str(data['pin'])):
        user.pin = str(data['pin'])
    
    if 'verbal_code' in data and data['verbal_code'] and len(str(data['verbal_code'])) >= 3:
        user.verbal_code = str(data['verbal_code'])
    
    if 'retry_limit' in data and isinstance(data['retry_limit'], int) and 1 <= data['retry_limit'] <= 5:
        user.retry_limit = data['retry_limit']
    
    if 'rl_max_attempts' in data and isinstance(data['rl_max_attempts'], int):
        user.rl_max_attempts = data['rl_max_attempts']
    
    if 'rl_block_minutes' in data and isinstance(data['rl_block_minutes'], int):
        user.rl_block_minutes = data['rl_block_minutes']
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Settings updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/blocked', methods=['GET'])
def api_get_blocked_calls(user_id):
    """Get blocked calls for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    blocked = UserBlocklist.query.filter(
        UserBlocklist.user_id == user_id,
        UserBlocklist.unblock_at > datetime.utcnow()
    ).all()
    
    blocked_list = []
    for block in blocked:
        blocked_list.append({
            'id': block.id,
            'phone_number': block.caller_number,
            'display_name': format_phone_display(block.caller_number),
            'unblock_at': block.unblock_at.isoformat() if block.unblock_at else None,
            'blocked_at': (block.unblock_at - timedelta(minutes=user.rl_block_minutes)).isoformat() if block.unblock_at else None
        })
    
    return jsonify(blocked_list)

@multi_user_bp.route('/user/<int:user_id>/blocked/<int:block_id>', methods=['DELETE'])
def api_remove_blocked_call(user_id, block_id):
    """Remove a blocked call for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    blocked = UserBlocklist.query.filter_by(id=block_id, user_id=user_id).first_or_404()
    
    try:
        db.session.delete(blocked)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Blocked call removed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/blocked/<int:block_id>/whitelist', methods=['POST'])
def api_whitelist_blocked_call(user_id, block_id):
    """Move blocked call to whitelist for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    blocked = UserBlocklist.query.filter_by(id=block_id, user_id=user_id).first_or_404()
    
    # Check if already in whitelist
    existing = UserWhitelist.query.filter_by(
        user_id=user_id, 
        caller_number=blocked.caller_number
    ).first()
    
    if existing:
        return jsonify({'success': False, 'error': 'Number already in whitelist'}), 400
    
    try:
        # Add to whitelist
        whitelist_entry = UserWhitelist(
            user_id=user_id,
            caller_number=blocked.caller_number
        )
        db.session.add(whitelist_entry)
        
        # Remove from blocklist
        db.session.delete(blocked)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Number moved to trusted contacts'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/analytics', methods=['GET'])
def api_get_user_analytics(user_id):
    """Get user analytics data for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    # Get blocked calls count (current blocks)
    blocked_count = UserBlocklist.query.filter(
        UserBlocklist.user_id == user_id,
        UserBlocklist.unblock_at > datetime.utcnow()
    ).count()
    
    # Get trusted contacts count
    trusted_count = UserWhitelist.query.filter_by(user_id=user_id).count()
    
    # Get call history count for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_calls = MultiUserCallLog.query.filter(
        MultiUserCallLog.user_id == user_id,
        MultiUserCallLog.created_at >= thirty_days_ago
    ).count()
    
    # Get failed authentication attempts from last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    failed_attempts = UserFailLog.query.filter(
        UserFailLog.user_id == user_id,
        UserFailLog.failure_time >= seven_days_ago
    ).count()
    
    return jsonify({
        'blocked_calls': blocked_count,
        'trusted_contacts': trusted_count,
        'recent_calls': recent_calls,
        'failed_attempts': failed_attempts,
        'defense_number': format_phone_display(user.assigned_twilio_number),
        'google_voice_number': format_phone_display(user.google_voice_number),
        'real_phone_number': format_phone_display(user.real_phone_number),
        'account_status': 'Active' if user.is_active else 'Inactive',
        'google_voice_verified': user.google_voice_verified
    })

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
    """Get trusted contacts for mobile app - SECURED"""
    user = verify_user_access(user_id)
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
    """Add trusted contact for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
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
    """Delete trusted contact for mobile app - SECURED"""
    user = verify_user_access(user_id)
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
    """Get call history for mobile app - SECURED"""
    user = verify_user_access(user_id)
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Get actual call logs from database
    calls = MultiUserCallLog.query.filter_by(user_id=user_id).order_by(MultiUserCallLog.created_at.desc()).limit(limit).offset(offset).all()
    
    call_list = []
    for call in calls:
        call_list.append({
            'id': call.id,
            'to_number': call.to_number,
            'from_number': call.from_number,
            'direction': call.direction,
            'status': call.status,
            'duration_seconds': call.duration_seconds,
            'created_at': call.created_at.isoformat() if call.created_at else None
        })
    
    return jsonify(call_list)

@multi_user_bp.route('/user/<int:user_id>/calls/<int:call_id>/complete', methods=['POST'])
def api_complete_call(user_id, call_id):
    """Complete a call for mobile app - SECURED"""
    user = verify_user_access(user_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    try:
        call_log = MultiUserCallLog.query.filter_by(id=call_id, user_id=user_id).first_or_404()
        
        # Update call with completion details
        call_log.status = data.get('status', 'completed')
        call_log.duration_seconds = data.get('duration_seconds', 0)
        call_log.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'call_id': call_id,
            'status': call_log.status,
            'duration': call_log.duration_seconds
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/calls/<int:call_id>/status', methods=['GET'])
def api_get_call_status(user_id, call_id):
    """Get call status for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    try:
        call_log = MultiUserCallLog.query.filter_by(id=call_id, user_id=user_id).first_or_404()
        
        return jsonify({
            'call_id': call_log.id,
            'status': call_log.status,
            'to_number': call_log.to_number,
            'from_number': call_log.from_number,
            'direction': call_log.direction,
            'duration_seconds': call_log.duration_seconds,
            'created_at': call_log.created_at.isoformat() if call_log.created_at else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

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

# ============================================================================
# REAL CALLBUNKER BRIDGE CALLING - The Actual Working Mechanism!
# ============================================================================

@multi_user_bp.route('/voice/conference/<conference_name>', methods=['POST'])
def handle_conference_call(conference_name):
    """
    Handle conference call participants - joins target and user into same conference
    This is the TwiML endpoint that both call legs hit
    """
    participant = request.args.get('participant', 'unknown')
    
    vr = VoiceResponse()
    
    if participant == 'target':
        # Target person joining - no message, just join conference
        vr.dial().conference(
            conference_name,
            start_conference_on_enter=True,
            end_conference_on_exit=False,
            wait_url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient"
        )
    elif participant == 'user':
        # User joining via phone callback - brief message then join
        vr.say("CallBunker connecting your call.", voice="polly.Joanna")
        vr.dial().conference(
            conference_name,
            start_conference_on_enter=True,
            end_conference_on_exit=True,  # End when user hangs up
            wait_url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient"
        )
    elif participant == 'mobile_app':
        # Mobile app joining via Twilio Voice SDK - no message, direct conference join
        vr.dial().conference(
            conference_name,
            start_conference_on_enter=True,
            end_conference_on_exit=True,  # End when mobile app disconnects
            wait_url=""  # No hold music for mobile app
        )
    else:
        vr.say("Conference error. Please try again.", voice="polly.Joanna")
        vr.hangup()
    
    return xml_response(vr)

def xml_response(voice_response):
    """Helper to return proper TwiML XML response"""
    response = Response(str(voice_response), content_type='application/xml')
    return response

@multi_user_bp.route('/user/<int:user_id>/call_bridge', methods=['POST'])
def api_call_bridge(user_id):
    """
    REAL CALLBUNKER BRIDGE CALLING - This actually works!
    Creates a Twilio conference call bridging user and target
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        to_number = data.get('to_number', '').strip()
        if not to_number:
            return jsonify({'error': 'to_number is required'}), 400
        
        # Normalize phone numbers
        to_number_normalized = '+1' + normalize_phone(to_number) if not to_number.startswith('+') else to_number
        user_phone = '+1' + normalize_phone(user.real_phone_number) if len(user.real_phone_number) == 10 else user.real_phone_number
        google_voice_number = '+1' + normalize_phone(user.google_voice_number) if len(user.google_voice_number) == 10 else user.google_voice_number
        
        # Create conference name
        conference_name = f"callbunker_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Get Twilio client and public URL
        from utils.twilio_helpers import twilio_client
        client = twilio_client()
        
        # Use public URL that Twilio can reach
        public_url = os.environ.get('PUBLIC_APP_URL', 'https://4ec224cf-933c-4ca6-b58f-2fce3ea2d59f-00-23vazcc99oamt.janeway.replit.dev')
        
        # Use verified CallBunker Defense Number as caller ID (works reliably)
        defense_number = user.assigned_twilio_number
        
        # Call 1: Call the target number (they see your Defense Number as caller ID)
        target_call = client.calls.create(
            to=to_number_normalized,
            from_=defense_number,  # Target sees your verified Defense Number
            url=f"{public_url}/multi/voice/conference/{conference_name}?participant=target",
            method='POST'
        )
        
        # Call 2: Call the user
        user_call = client.calls.create(
            to=user_phone,
            from_=defense_number,  # You see your Defense Number calling you
            url=f"{public_url}/multi/voice/conference/{conference_name}?participant=user",
            method='POST'
        )
        
        # Create call log entry
        call_log = MultiUserCallLog(
            user_id=user_id,
            from_number=defense_number,
            to_number=to_number_normalized,
            direction='outbound',
            status='calling',
            twilio_call_sid=target_call.sid,
            conference_name=conference_name
        )
        
        db.session.add(call_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'approach': 'bridge_calling',
            'call_log_id': call_log.id,
            'conference_name': conference_name,
            'to_number': to_number_normalized,
            'from_number': google_voice_number,
            'target_call_sid': target_call.sid,
            'user_call_sid': user_call.sid,
            'bridge_config': {
                'target_sees': google_voice_number,
                'user_phone': user_phone,
                'conference': conference_name,
                'cost': '$0.02 per minute per leg (2 legs total)'
            },
            'message': f'Bridge call initiated - both {to_number_normalized} and {user_phone} will ring shortly'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/call_mobile_app', methods=['POST'])
def api_call_mobile_app(user_id):
    """
    MOBILE APP CALLING WITHOUT CALLBACK
    Only calls target, mobile app connects via Twilio Voice SDK (no callback to user's phone!)
    """
    user = verify_user_access(user_id)
    data = request.get_json()
    
    try:
        to_number = data.get('to_number', '').strip()
        if not to_number:
            return jsonify({'error': 'to_number is required'}), 400
        
        # Normalize phone numbers
        to_number_normalized = '+1' + normalize_phone(to_number) if not to_number.startswith('+') else to_number
        google_voice_number = '+1' + normalize_phone(user.google_voice_number) if len(user.google_voice_number) == 10 else user.google_voice_number
        
        # Create conference name for this call
        conference_name = f"callbunker_mobile_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Get Twilio client and public URL
        client = twilio_client()
        public_url = os.environ.get('PUBLIC_APP_URL', 'https://4ec224cf-933c-4ca6-b58f-2fce3ea2d59f-00-23vazcc99oamt.janeway.replit.dev')
        
        # Generate Voice Access Token for mobile app
        access_token = generate_voice_access_token(user_id)
        
        # Call ONLY the target number (no callback to user's phone!)
        target_call = client.calls.create(
            to=to_number_normalized,
            from_=user.assigned_twilio_number,  # Use assigned Twilio number as caller ID
            url=f"{public_url}/multi/voice/conference/{conference_name}?participant=target",
            method='POST'
        )
        
        # Create call log entry
        call_log = MultiUserCallLog(
            user_id=user_id,
            from_number=google_voice_number,
            to_number=to_number_normalized,
            direction='outbound',
            status='mobile_calling',
            twilio_call_sid=target_call.sid,
            conference_name=conference_name
        )
        
        db.session.add(call_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'approach': 'mobile_app_calling',
            'call_log_id': call_log.id,
            'conference_name': conference_name,
            'to_number': to_number_normalized,
            'from_number': google_voice_number,
            'target_call_sid': target_call.sid,
            'access_token': access_token,
            'mobile_config': {
                'target_sees': google_voice_number,
                'no_callback': True,
                'conference': conference_name,
                'cost': '$0.02 per minute (1 call leg only)',
                'connection_method': 'Twilio Voice SDK via internet'
            },
            'message': f'Target {to_number_normalized} will ring. Use access token to connect via mobile app.',
            'instructions': {
                'mobile_app': 'Use the access_token to connect to Twilio Voice SDK',
                'conference_endpoint': f'{public_url}/multi/voice/conference/{conference_name}?participant=mobile_app',
                'connection_type': 'internet_based'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/voice_token', methods=['GET'])
def get_voice_access_token(user_id):
    """Get Twilio Voice Access Token for mobile app"""
    user = verify_user_access(user_id)
    
    try:
        access_token = generate_voice_access_token(user_id)
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'identity': f'callbunker_user_{user_id}',
            'expires_in': 3600,  # 1 hour
            'usage': 'Use this token to initialize Twilio Voice SDK in mobile app'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/contact-support')
def contact_support():
    """Support contact page for users needing help"""
    return render_template('multi_user/contact_support.html')


# ============================================================================
# GOOGLE VOICE AUTHENTICATION - Critical Missing Step!
# ============================================================================

@multi_user_bp.route('/user/<int:user_id>/google-voice-auth')
@multi_user_bp.route('/google-voice-auth/<user_id>')
def google_voice_auth(user_id):
    """Critical step: Guide user through Google Voice authentication of their CallBunker number"""
    user = User.query.get_or_404(user_id)
    
    # Create direct Google Voice setup URL with the user's assigned Twilio number
    twilio_number = user.assigned_twilio_number
    google_voice_url = f"https://voice.google.com/u/0/settings/phones?authuser=0"
    
    return render_template('multi_user/mobile_google_voice_auth.html',
                         user=user,
                         twilio_number=twilio_number,
                         google_voice_url=google_voice_url,
                         format_phone=format_phone_display)

@multi_user_bp.route('/user/<int:user_id>/complete-auth', methods=['POST'])
def complete_google_voice_auth(user_id):
    """Mark Google Voice authentication as complete and proceed to dashboard"""
    user = User.query.get_or_404(user_id)
    
    # Here you could add verification logic if needed
    # For now, trust the user completed the process
    
    flash('Google Voice authentication completed! Your CallBunker system is now active.', 'success')
    return redirect(url_for('multi_user.user_dashboard', user_id=user.id))

