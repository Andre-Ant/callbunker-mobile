import re
from datetime import datetime
from flask import Blueprint, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from app import db
from models import Tenant, Whitelist
from utils.twilio_helpers import xml_response, get_tenant_or_404
from utils.rate_limiting import is_blocked, note_failure_and_maybe_block, clear_failures
from utils.auth import norm_digits, norm_speech

voice_bp = Blueprint('voice', __name__)

def caller_expected_pin(tenant, caller_digits):
    """Get the expected PIN for a caller - either custom or tenant default"""
    whitelist_entry = Whitelist.query.filter_by(
        screening_number=tenant.screening_number,
        number=caller_digits
    ).filter(Whitelist.pin.isnot(None)).first()
    
    return whitelist_entry.pin if whitelist_entry else tenant.current_pin

def is_caller_whitelisted_verbal(tenant, caller_digits):
    """Check if caller is whitelisted for verbal authentication"""
    whitelist_entry = Whitelist.query.filter_by(
        screening_number=tenant.screening_number,
        number=caller_digits,
        verbal=True
    ).first()
    
    return bool(whitelist_entry)

def tenant_forward_mode(tenant):
    """Get the forward mode for a tenant"""
    return (tenant.forward_mode or "bridge").strip().lower()

def on_verified(tenant):
    """Handle successful verification - forward the call"""
    mode = tenant_forward_mode(tenant)
    vr = VoiceResponse()
    
    if mode == "voicemail":
        vr.say("Thank you for verification. Please leave your message after the tone.", voice="polly.Joanna")
        vr.record(
            timeout=30,
            max_length=120,
            transcribe=True,
            action="/voice/voicemail_complete"
        )
    else:  # bridge mode
        vr.say("Connecting your call now.", voice="polly.Joanna")
        dial = vr.dial(
            tenant.forward_to,
            timeout=30,
            hangup_on_star=True,
            action="/voice/call_complete"
        )
    
    return xml_response(vr)

def voicemail_prompt(to_number):
    """Handle voicemail prompt for unverified callers"""
    vr = VoiceResponse()
    vr.say("Sorry, you could not be verified. Please leave a message after the tone.", voice="polly.Joanna")
    vr.record(
        timeout=30,
        max_length=120,
        transcribe=True,
        action=f"/voice/voicemail_complete?to={to_number}"
    )
    return xml_response(vr)

@voice_bp.route('/incoming', methods=['POST'])
def voice_incoming():
    """
    Twilio posts here when a call hits ANY screening number.
    We identify tenant by the 'To' number.
    """
    to_number = request.form.get("To", "").strip()
    from_digits = norm_digits(request.form.get("From", ""))
    
    tenant = get_tenant_or_404(to_number)
    
    # Check if caller is blocked
    remaining = is_blocked(tenant, from_digits)
    if remaining is not None:
        vr = VoiceResponse()
        vr.say("Sorry, this number is temporarily blocked due to repeated failed attempts. Goodbye.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    # Start verification process
    vr = VoiceResponse()
    gather = Gather(
        input="speech dtmf",
        num_digits=4,
        action=f"/voice/verify?attempts=0&to={to_number}",
        method="POST",
        timeout=6,
        speech_timeout="auto",
        finish_on_key=""
    )
    gather.say("Please enter your four digit pin, or say your verbal code.", voice="polly.Joanna")
    vr.append(gather)
    # Fallback if no input received - terminate call completely
    vr.say("No input received. This call will now end.", voice="polly.Joanna")
    vr.hangup()
    return xml_response(vr)

@voice_bp.route('/retry', methods=['GET', 'POST'])
def voice_retry():
    """Handle retry attempts for failed verification"""
    if request.method == 'POST':
        form_data = request.form
        attempts = int(form_data.get("attempts", 0))
        to_number = form_data.get("to") or form_data.get("To")
        from_digits = norm_digits(form_data.get("From", ""))
    else:
        attempts = int(request.args.get("attempts", 0))
        to_number = request.args.get("to")
        from_digits = ""
    
    # Fix phone number formatting for tenant lookup
    if to_number and not to_number.startswith('+'):
        to_number = '+' + to_number.strip()
    
    if not to_number:
        vr = VoiceResponse()
        vr.say("Invalid request. Goodbye.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    tenant = get_tenant_or_404(to_number)
    
    # Check if caller is blocked
    if from_digits:
        remaining = is_blocked(tenant, from_digits)
        if remaining is not None:
            vr = VoiceResponse()
            vr.say("Sorry, this number is temporarily blocked due to repeated failed attempts. Goodbye.", voice="polly.Joanna")
            vr.hangup()
            return xml_response(vr)
    
    # Check if max attempts reached
    if attempts >= tenant.retry_limit:
        return voicemail_prompt(to_number)
    
    next_attempts = attempts + 1
    vr = VoiceResponse()
    gather = Gather(
        input="speech dtmf",
        num_digits=4,
        action=f"/voice/verify?attempts={next_attempts}&to={to_number}",
        method="POST",
        timeout=6,
        speech_timeout="auto",
    )
    gather.say("Incorrect code. Please try again with your four digit pin, or say your verbal code.", voice="polly.Joanna")
    vr.append(gather)
    # Fallback if no input received
    vr.say("No input received. Goodbye.", voice="polly.Joanna")
    vr.hangup()
    return xml_response(vr)

@voice_bp.route('/verify', methods=['POST'])
def voice_verify():
    """Handle PIN and verbal code verification"""
    to_number = request.args.get("to") or request.form.get("To")
    # Fix phone number formatting for tenant lookup
    if to_number and not to_number.startswith('+'):
        to_number = '+' + to_number.strip()
    
    from_digits = norm_digits(request.form.get("From", ""))
    attempts = int(request.args.get("attempts", request.form.get("attempts", 0)))
    pressed = request.form.get("Digits")
    speech = request.form.get("SpeechResult")
    
    if not to_number:
        vr = VoiceResponse()
        vr.say("Invalid request. Goodbye.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    tenant = get_tenant_or_404(to_number)
    
    # Check if caller is blocked
    remaining = is_blocked(tenant, from_digits)
    if remaining is not None:
        vr = VoiceResponse()
        vr.say("Sorry, this number is temporarily blocked due to repeated failed attempts. Goodbye.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    expected_pin = caller_expected_pin(tenant, from_digits)
    accepted_verbal = tenant.verbal_code.strip().lower()
    
    # Check PIN verification
    if pressed and len(pressed) == 4 and pressed == expected_pin:
        clear_failures(tenant, from_digits)
        return on_verified(tenant)
    
    # Check verbal verification
    if speech:
        said = norm_speech(speech)
        
        # Exact match only
        if said == accepted_verbal:
            clear_failures(tenant, from_digits)
            return on_verified(tenant)
        
        # Check whitelist verbal authentication
        if is_caller_whitelisted_verbal(tenant, from_digits) and said == accepted_verbal:
            clear_failures(tenant, from_digits)
            return on_verified(tenant)
    
    # Verification failed
    note_failure_and_maybe_block(tenant, from_digits)
    
    # Check if max attempts reached
    next_attempts = attempts + 1
    if next_attempts >= tenant.retry_limit:
        return voicemail_prompt(to_number)
    
    # Create retry response directly
    vr = VoiceResponse()
    gather = Gather(
        input="speech dtmf", 
        num_digits=4,
        action=f"/voice/verify?attempts={next_attempts}&to={to_number}",
        method="POST",
        timeout=6,
        speech_timeout="auto",
        finish_on_key=""
    )
    gather.say("Incorrect code. Please try again with your four digit pin, or say your verbal code.", voice="polly.Joanna")
    vr.append(gather)
    # Fallback if no input received
    vr.say("No input received. Goodbye.", voice="polly.Joanna")
    vr.hangup()
    return xml_response(vr)

@voice_bp.route('/call_complete', methods=['POST'])
def call_complete():
    """Handle call completion or hangup"""
    call_status = request.form.get('DialCallStatus')
    
    vr = VoiceResponse()
    if call_status in ['completed', 'busy', 'no-answer', 'failed', 'canceled']:
        # Call ended normally, just hang up
        vr.hangup()
    else:
        # Unexpected status, hang up safely
        vr.hangup()
    
    return xml_response(vr)

@voice_bp.route('/voicemail_complete', methods=['POST'])
def voicemail_complete():
    """Handle voicemail completion"""
    vr = VoiceResponse()
    vr.say("Thank you for your message. Goodbye.", voice="polly.Joanna")
    vr.hangup()
    return xml_response(vr)
