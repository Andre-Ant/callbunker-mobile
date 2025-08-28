"""
Multi-User Voice Handling - Each user has their own Twilio number
"""
from flask import Blueprint, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from models_multi_user import User, UserWhitelist, UserFailLog, UserBlocklist
from routes.multi_user import get_user_by_twilio_number, normalize_phone
from utils.twilio_helpers import xml_response
from urllib.parse import quote
from datetime import datetime, timedelta
from app import db
import re

multi_user_voice_bp = Blueprint('multi_user_voice', __name__, url_prefix='/multi/voice')

def normalize_speech(speech_text):
    """Normalize speech input for comparison"""
    if not speech_text:
        return ""
    return re.sub(r'[^\w\s]', '', speech_text.lower().strip())

def is_user_blocked(user, caller_number):
    """Check if caller is temporarily blocked for this user"""
    blocked = UserBlocklist.query.filter_by(
        user_id=user.id,
        caller_number=caller_number
    ).filter(UserBlocklist.unblock_at > datetime.utcnow()).first()
    
    if blocked:
        remaining = (blocked.unblock_at - datetime.utcnow()).total_seconds()
        return max(0, int(remaining / 60))  # Minutes remaining
    return None

def is_caller_whitelisted(user, caller_number):
    """Check if caller is whitelisted for this user"""
    return UserWhitelist.query.filter_by(
        user_id=user.id,
        caller_number=caller_number
    ).first() is not None

def auto_whitelist_caller(user, caller_number, custom_pin=None):
    """Add caller to user's whitelist after successful authentication"""
    existing = UserWhitelist.query.filter_by(
        user_id=user.id,
        caller_number=caller_number
    ).first()
    
    if existing:
        return  # Already whitelisted
    
    whitelist_entry = UserWhitelist(
        user_id=user.id,
        caller_number=caller_number,
        custom_pin=custom_pin,
        allows_verbal=False
    )
    
    db.session.add(whitelist_entry)
    try:
        db.session.commit()
        print(f"Auto-whitelisted caller {caller_number} for user {user.id}")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to auto-whitelist caller: {e}")

def note_failure_and_maybe_block(user, caller_number):
    """Record authentication failure and block if necessary"""
    # Record failure
    failure = UserFailLog(
        user_id=user.id,
        caller_number=caller_number
    )
    db.session.add(failure)
    
    # Count recent failures
    cutoff_time = datetime.utcnow() - timedelta(seconds=user.rl_window_sec)
    recent_failures = UserFailLog.query.filter_by(
        user_id=user.id,
        caller_number=caller_number
    ).filter(UserFailLog.failure_time > cutoff_time).count()
    
    # Block if too many failures
    if recent_failures >= user.rl_max_attempts:
        unblock_time = datetime.utcnow() + timedelta(minutes=user.rl_block_minutes)
        
        # Remove existing block and add new one
        UserBlocklist.query.filter_by(
            user_id=user.id,
            caller_number=caller_number
        ).delete()
        
        block = UserBlocklist(
            user_id=user.id,
            caller_number=caller_number,
            unblock_at=unblock_time
        )
        db.session.add(block)
        print(f"Blocked caller {caller_number} for user {user.id} until {unblock_time}")
    
    db.session.commit()

def clear_failures(user, caller_number):
    """Clear authentication failures for successful caller"""
    UserFailLog.query.filter_by(
        user_id=user.id,
        caller_number=caller_number
    ).delete()
    
    UserBlocklist.query.filter_by(
        user_id=user.id,
        caller_number=caller_number
    ).delete()
    
    db.session.commit()

@multi_user_voice_bp.route('/incoming/<phone_number>', methods=['POST'])
def voice_incoming(phone_number):
    """Handle incoming calls to a specific user's Twilio number"""
    # Normalize the phone number from URL
    twilio_number = f"+1{normalize_phone(phone_number)}" if len(normalize_phone(phone_number)) == 10 else f"+{normalize_phone(phone_number)}"
    
    print(f"MULTI-USER INCOMING CALL to {twilio_number} - Form data: {dict(request.form)}")
    
    # Find the user assigned to this Twilio number
    user = get_user_by_twilio_number(twilio_number)
    if not user:
        print(f"No user found for Twilio number {twilio_number}")
        vr = VoiceResponse()
        vr.say("This CallBunker number is not currently assigned. Please contact support.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    if not user.is_active:
        print(f"User {user.id} account is inactive")
        vr = VoiceResponse()
        vr.say("This account is currently inactive. Please contact support.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    from_number = request.form.get("From", "").strip()
    forwarded_from = request.form.get("ForwardedFrom", "").strip()
    caller_digits = normalize_phone(from_number)
    
    print(f"User: {user.name} ({user.id}), From: {from_number}, ForwardedFrom: {forwarded_from}")
    
    # CHECK FOR GOOGLE VOICE OTP VERIFICATION CALLS
    google_voice_verification_numbers = [
        '12024558888',  # Google Voice verification service
        '18005551234',  # Another Google verification number
    ]
    
    if caller_digits in google_voice_verification_numbers:
        print(f"GOOGLE VOICE OTP VERIFICATION for user {user.id} - forwarding to {user.real_phone_number}")
        vr = VoiceResponse()
        vr.say("This is your Google Voice verification call. Connecting now.", voice="polly.Joanna")
        vr.dial(f"+1{user.real_phone_number}" if len(user.real_phone_number) == 10 else user.real_phone_number, timeout=30)
        return xml_response(vr)
    
    # Check for Google Voice forwarded call
    if forwarded_from == f"+1{user.google_voice_number}" or forwarded_from == user.google_voice_number:
        print(f"Google Voice forwarded call detected for user {user.id}")
        # This is a Google Voice forwarded call - proceed with authentication
    elif not forwarded_from:
        # Direct call to CallBunker number - not expected in Google Voice setup
        print(f"Direct call to CallBunker number for user {user.id}")
        vr = VoiceResponse()
        vr.say(f"Hello {user.name}. This is your CallBunker screening number. Please have callers dial your Google Voice number instead.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    # Check if caller is blocked
    block_remaining = is_user_blocked(user, caller_digits)
    if block_remaining is not None:
        vr = VoiceResponse()
        vr.say(f"Sorry, this number is temporarily blocked for {block_remaining} more minutes due to repeated failed attempts. Goodbye.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    # Check if caller is whitelisted
    if is_caller_whitelisted(user, caller_digits):
        print(f"WHITELISTED CALLER: {caller_digits} calling user {user.id} - bypassing authentication")
        clear_failures(user, caller_digits)
        return connect_call(user, from_number)
    
    # Require authentication
    print(f"AUTHENTICATION REQUIRED for caller {caller_digits} to user {user.id}")
    vr = VoiceResponse()
    vr.pause(length=1)
    
    gather = Gather(
        input="speech dtmf",
        num_digits=4,
        action=url_for('multi_user_voice.verify_auth', user_id=user.id, attempts=0),
        method="POST",
        timeout=8,
        speech_timeout="auto",
        finish_on_key=""
    )
    gather.say(f"Hello, you've reached {user.name}'s call screening service. Please enter your four digit pin, or say your verbal code.", voice="alice", rate="slow")
    vr.append(gather)
    
    vr.say("No input received. This call will now end.", voice="polly.Joanna")
    vr.hangup()
    
    return xml_response(vr)

@multi_user_voice_bp.route('/verify/<int:user_id>/<int:attempts>', methods=['POST'])
def verify_auth(user_id, attempts):
    """Verify PIN or verbal authentication for specific user"""
    user = User.query.get_or_404(user_id)
    
    from_number = request.form.get("From", "").strip()
    caller_digits = normalize_phone(from_number)
    pressed = request.form.get("Digits")
    speech = request.form.get("SpeechResult")
    
    print(f"VERIFY AUTH for user {user.id}: PIN={pressed}, Speech={speech}, Attempt={attempts}")
    
    # Check if caller is blocked
    block_remaining = is_user_blocked(user, caller_digits)
    if block_remaining is not None:
        vr = VoiceResponse()
        vr.say("Sorry, this number is now blocked. Goodbye.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    # Verify PIN
    if pressed and len(pressed) == 4 and pressed == user.pin:
        clear_failures(user, caller_digits)
        auto_whitelist_caller(user, caller_digits, pressed if pressed != user.pin else None)
        return connect_call(user, from_number)
    
    # Verify verbal code
    if speech:
        said = normalize_speech(speech)
        expected = normalize_speech(user.verbal_code)
        
        if said == expected:
            clear_failures(user, caller_digits)
            auto_whitelist_caller(user, caller_digits)
            return connect_call(user, from_number)
    
    # Authentication failed
    note_failure_and_maybe_block(user, caller_digits)
    
    # Check retry limit
    next_attempts = attempts + 1
    if next_attempts >= user.retry_limit:
        vr = VoiceResponse()
        vr.say("Maximum authentication attempts exceeded. Goodbye.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    # Allow retry
    vr = VoiceResponse()
    gather = Gather(
        input="speech dtmf",
        num_digits=4,
        action=url_for('multi_user_voice.verify_auth', user_id=user.id, attempts=next_attempts),
        method="POST",
        timeout=8,
        speech_timeout="auto",
        finish_on_key=""
    )
    gather.say("Incorrect code. Please try again with your four digit pin, or say your verbal code clearly.", voice="polly.Joanna")
    vr.append(gather)
    
    vr.say("No input received. Goodbye.", voice="polly.Joanna")
    vr.hangup()
    
    return xml_response(vr)

def connect_call(user, original_caller_number):
    """Connect authenticated call to user's real phone"""
    vr = VoiceResponse()
    vr.say("Connecting your call now.", voice="polly.Joanna")
    
    # Use original caller's number as caller ID to avoid spam warnings
    forward_to = f"+1{user.real_phone_number}" if len(user.real_phone_number) == 10 else user.real_phone_number
    
    print(f"CONNECTING: User {user.id} call from {original_caller_number} to {forward_to}")
    
    vr.dial(
        forward_to,
        timeout=30,
        caller_id=original_caller_number,  # Preserve original caller ID
        action=url_for('multi_user_voice.call_complete')
    )
    
    return xml_response(vr)

@multi_user_voice_bp.route('/call_complete', methods=['POST'])
def call_complete():
    """Handle call completion"""
    vr = VoiceResponse()
    vr.hangup()
    return xml_response(vr)

# Import url_for at the top level to avoid circular imports
from flask import url_for