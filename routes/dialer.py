from flask import Blueprint, render_template, request, jsonify, session
from app import db
from models_multi_user import User as MultiUser, MultiUserCallLog
from utils.twilio_helpers import twilio_client
from twilio.twiml.voice_response import VoiceResponse
import logging
from datetime import datetime
import re

dialer_bp = Blueprint('dialer', __name__)

def format_phone_number(phone):
    """Format phone number for display"""
    if not phone:
        return ""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

def normalize_phone_number(phone):
    """Normalize phone number to E.164 format"""
    if not phone:
        return None
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    # Add country code if missing
    if len(digits) == 10:
        digits = '1' + digits
    elif len(digits) == 11 and digits.startswith('1'):
        pass
    else:
        return None
    return '+' + digits

@dialer_bp.route('/dialer/<int:user_id>')
def dialer_interface(user_id):
    """Web-based dialer interface"""
    user = MultiUser.query.get_or_404(user_id)
    
    # Get recent call history
    recent_calls = MultiUserCallLog.query.filter_by(user_id=user_id)\
        .order_by(MultiUserCallLog.created_at.desc())\
        .limit(10).all()
    
    return render_template('multi_user/dialer.html', 
                         user=user,
                         recent_calls=recent_calls,
                         format_phone=format_phone_number)

@dialer_bp.route('/dialer/<int:user_id>/call', methods=['POST'])
def initiate_call(user_id):
    """Initiate an outgoing call through Google Voice/Twilio"""
    user = MultiUser.query.get_or_404(user_id)
    
    data = request.get_json()
    to_number = data.get('to_number')
    
    if not to_number:
        return jsonify({'error': 'Phone number is required'}), 400
    
    # Normalize the phone number
    normalized_to = normalize_phone_number(to_number)
    if not normalized_to:
        return jsonify({'error': 'Invalid phone number format'}), 400
    
    try:
        client = twilio_client()
        
        # Debug logging
        logging.info(f"Making call - From: {user.google_voice_number}, To: {user.real_phone_number}")
        
        # Get available verified numbers from Twilio
        try:
            outgoing_caller_ids = client.outgoing_caller_ids.list()
            verified_numbers = [caller_id.phone_number for caller_id in outgoing_caller_ids]
            logging.info(f"Available verified numbers: {verified_numbers}")
        except Exception as e:
            logging.error(f"Failed to get verified numbers: {e}")
            verified_numbers = []
        
        # Try to find a verified number to use
        from_number = None
        if user.google_voice_number in verified_numbers:
            from_number = user.google_voice_number
            logging.info(f"Using Google Voice number: {from_number}")
        elif verified_numbers:
            from_number = verified_numbers[0]  # Use first available verified number
            logging.info(f"Google Voice number not available, using: {from_number}")
        else:
            # If no verified numbers, provide clear guidance
            return jsonify({
                'error': 'No verified phone numbers found in Twilio account. Please verify your Google Voice number in the Twilio Console.',
                'error_type': 'no_verified_numbers'
            }), 400
        
        # Create a call that first calls the user, then dials out to target when user answers
        import os
        public_url = os.environ.get('PUBLIC_APP_URL', f"https://{request.host}")
        webhook_url = f"{public_url}/dialer/{user_id}/dial_target?target={normalized_to}&from_number={from_number}"
        logging.info(f"Using webhook URL: {webhook_url}")
        
        call = client.calls.create(
            to=user.real_phone_number,  # Call user first
            from_=from_number,  # Show Google Voice number as caller ID to user
            url=webhook_url,
            method='POST'
        )
        
        # Log the call
        call_log = MultiUserCallLog()
        call_log.user_id = user_id
        call_log.from_number = user.google_voice_number
        call_log.to_number = normalized_to
        call_log.direction = 'outbound'
        call_log.status = 'initiated'
        call_log.twilio_call_sid = call.sid
        db.session.add(call_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'call_sid': call.sid,
            'message': 'Calling your phone now - answer to place the call'
        })
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Call initiation error: {e}")
        
        # Handle specific Twilio errors
        if "21210" in error_msg or "not yet verified" in error_msg:
            return jsonify({
                'error': 'Google Voice number not verified in Twilio. Please complete verification first.',
                'error_type': 'twilio_verification'
            }), 400
        elif "21211" in error_msg or "Invalid 'To' Phone Number" in error_msg:
            return jsonify({
                'error': 'Invalid phone number format. Please check the number and try again.',
                'error_type': 'invalid_number'
            }), 400
        else:
            return jsonify({
                'error': f'Call failed: {error_msg}',
                'error_type': 'general'
            }), 500

@dialer_bp.route('/dialer/<int:user_id>/dial_target', methods=['POST'])
def dial_target(user_id):
    """TwiML to dial the target number when user answers"""
    user = MultiUser.query.get_or_404(user_id)
    target_number = request.args.get('target')
    from_number = request.args.get('from_number')
    
    response = VoiceResponse()
    
    # Play a brief message to the user
    response.say("Placing your call now...", voice='alice')
    
    # Dial the target number
    dial = response.dial(
        caller_id=from_number,  # Show Google Voice number as caller ID to target
        timeout=30
    )
    dial.number(target_number)
    
    # If call doesn't connect
    response.say("Call could not be completed. Please try again later.", voice='alice')
    
    return str(response), 200, {'Content-Type': 'application/xml'}

@dialer_bp.route('/dialer/<int:user_id>/status', methods=['POST'])
def call_status(user_id):
    """Handle call status updates"""
    call_sid = request.form.get('CallSid')
    call_status = request.form.get('CallStatus')
    
    # Update call log
    call_log = MultiUserCallLog.query.filter_by(twilio_call_sid=call_sid).first()
    if call_log:
        call_log.status = call_status
        call_log.updated_at = datetime.utcnow()
        db.session.commit()
    
    return '', 200

@dialer_bp.route('/dialer/<int:user_id>/history')
def call_history(user_id):
    """Get call history for user"""
    user = MultiUser.query.get_or_404(user_id)
    
    calls = MultiUserCallLog.query.filter_by(user_id=user_id)\
        .order_by(MultiUserCallLog.created_at.desc())\
        .limit(50).all()
    
    call_data = []
    for call in calls:
        call_data.append({
            'id': call.id,
            'to_number': format_phone_number(call.to_number),
            'from_number': format_phone_number(call.from_number),
            'direction': call.direction,
            'status': call.status,
            'created_at': call.created_at.strftime('%m/%d/%Y %I:%M %p'),
            'duration': call.duration_seconds if call.duration_seconds else 0
        })
    
    return jsonify(call_data)