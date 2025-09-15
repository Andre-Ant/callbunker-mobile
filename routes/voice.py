import re
from datetime import datetime
from urllib.parse import quote
from flask import Blueprint, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from app import db
from models import Tenant, Whitelist
from utils.twilio_helpers import xml_response, get_tenant_or_404, get_tenant_by_real_number
from utils.rate_limiting import is_blocked, note_failure_and_maybe_block, clear_failures
from utils.auth import norm_digits, norm_speech

voice_bp = Blueprint('voice', __name__)

def caller_expected_pin(tenant, caller_digits):
    """Get the expected PIN for a caller - either custom or tenant default"""
    normalized_caller = norm_digits(caller_digits)
    
    # First try the normalized format (without +)
    whitelist_entry = Whitelist.query.filter_by(
        screening_number=tenant.screening_number,
        number=normalized_caller
    ).filter(Whitelist.pin.isnot(None)).first()
    
    # If not found, try the original format (with +) for legacy data
    if not whitelist_entry:
        whitelist_entry = Whitelist.query.filter_by(
            screening_number=tenant.screening_number,
            number=f"+{normalized_caller}"
        ).filter(Whitelist.pin.isnot(None)).first()
    
    return whitelist_entry.pin if whitelist_entry else tenant.current_pin

def is_caller_whitelisted_verbal(tenant, caller_digits):
    """Check if caller is whitelisted for verbal authentication"""
    normalized_caller = norm_digits(caller_digits)
    
    # First try the normalized format (without +)
    whitelist_entry = Whitelist.query.filter_by(
        screening_number=tenant.screening_number,
        number=normalized_caller,
        verbal=True
    ).first()
    
    # If not found, try the original format (with +) for legacy data
    if not whitelist_entry:
        whitelist_entry = Whitelist.query.filter_by(
            screening_number=tenant.screening_number,
            number=f"+{normalized_caller}",
            verbal=True
        ).first()
    
    return bool(whitelist_entry)

def is_caller_whitelisted_bypass(tenant, caller_digits):
    """Check if caller is whitelisted and should bypass authentication entirely"""
    normalized_caller = norm_digits(caller_digits)
    
    # First try the normalized format (without +)
    whitelist_entry = Whitelist.query.filter_by(
        screening_number=tenant.screening_number,
        number=normalized_caller
    ).first()
    
    # If not found, try the original format (with +) for legacy data
    if not whitelist_entry:
        whitelist_entry = Whitelist.query.filter_by(
            screening_number=tenant.screening_number,
            number=f"+{normalized_caller}"
        ).first()
    
    return bool(whitelist_entry)

def auto_whitelist_caller(tenant, caller_digits, custom_pin=None):
    """Automatically add caller to whitelist after successful authentication"""
    # Normalize caller digits to match storage format
    normalized_caller = norm_digits(caller_digits)
    
    # Check if already whitelisted
    existing = Whitelist.query.filter_by(
        screening_number=tenant.screening_number,
        number=normalized_caller
    ).first()
    
    if existing:
        return  # Already whitelisted
    
    # Add to whitelist
    whitelist_entry = Whitelist(
        screening_number=tenant.screening_number,
        number=normalized_caller,
        pin=custom_pin,
        verbal=False  # Default to PIN-only for auto-whitelisted numbers
    )
    
    db.session.add(whitelist_entry)
    try:
        db.session.commit()
        print(f"Auto-whitelisted caller {normalized_caller} for tenant {tenant.screening_number}")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to auto-whitelist caller: {e}")

def tenant_forward_mode(tenant):
    """Get the forward mode for a tenant"""
    return (tenant.forward_mode or "bridge").strip().lower()

def on_verified(tenant, forwarded_from=None):
    """Handle successful verification - forward the call"""
    mode = tenant_forward_mode(tenant)
    vr = VoiceResponse()
    
    # Forward to the tenant's configured destination number
    forward_to_number = tenant.forward_to
    print(f"ON_VERIFIED: Forwarding to {forward_to_number} in {mode} mode for tenant {tenant.screening_number}")
    
    if mode == "voicemail":
        vr.say("Thank you for verification. Please leave your message after the tone.", voice="polly.Joanna")
        vr.record(
            timeout=30,
            max_length=120,
            transcribe=True,
            action="/voice/voicemail_complete"
        )
    else:  # bridge mode
        # For carrier forwarding, we need special handling to prevent loops
        if forward_to_number == tenant.screening_number:
            # This is carrier forwarding - user forwards their phone to CallBunker
            # We can't forward back to the same number that's forwarding to us!
            vr.say("Your call has been verified. However, call forwarding is creating a loop. Please disable call forwarding on your phone and call back directly, or contact support.", voice="polly.Joanna")
            vr.hangup()
        else:
            # Normal forwarding to a different number
            # Use the original caller's number as caller ID to avoid spam warnings
            from flask import request
            from_number = request.form.get("From", "").strip()
            caller_id = from_number  # Show the actual caller's number
            print(f"Using original caller number {caller_id} as caller ID")
            
            # Direct dial without any pre/post messages to avoid TwiML execution issues
            dial = vr.dial(
                forward_to_number,
                timeout=25,
                hangup_on_star=True,
                caller_id=caller_id
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
    Twilio posts here when a call hits the shared screening number.
    Routes calls to the appropriate system (multi-user or legacy).
    """
    # Debug logging to see what Twilio sends
    print(f"WEBHOOK CALLED - Form data: {dict(request.form)}")
    
    to_number = request.form.get("To", "").strip()  # Shared screening number
    # Ensure proper E.164 format
    if to_number and not to_number.startswith('+'):
        to_number = '+' + to_number
    forwarded_from = request.form.get("ForwardedFrom", "").strip()  # User's real number
    from_digits = norm_digits(request.form.get("From", ""))
    from_number = request.form.get("From", "").strip()
    
    print(f"To: {to_number}, ForwardedFrom: {forwarded_from}, From: {from_digits}")
    
    # CHECK FOR MULTI-USER SYSTEM CALLS
    # If this is a call to a number assigned to a user in the multi-user system, redirect there
    try:
        from models_multi_user import User
        user = User.query.filter_by(assigned_twilio_number=to_number).first()
        if user:
            print(f"MULTI-USER CALL DETECTED: {to_number} belongs to user {user.id} ({user.name})")
            print(f"Redirecting to multi-user voice system...")
            # Strip +1 from phone number for the URL
            phone_for_url = to_number.replace('+1', '').replace('+', '')
            redirect_url = f"/multi/voice/incoming/{phone_for_url}"
            
            # Forward the request to the multi-user system using TwiML redirect
            vr = VoiceResponse()
            vr.redirect(redirect_url, method="POST")
            return xml_response(vr)
    except Exception as e:
        print(f"Error checking for multi-user calls: {e}")
        # Continue with old system as fallback
    
    
    # LOOP DETECTION: If the call is coming FROM CallBunker number, it's a loop
    if from_number == "+16316417727":
        print("LOOP DETECTED: Call is from CallBunker itself, terminating to prevent infinite loop")
        vr = VoiceResponse()
        vr.say("Loop detected. Call terminated.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    # For the legacy single-user system, handle forwarded calls
    if not forwarded_from:
        # When ForwardedFrom is missing, resolve tenant by screening number (To)
        try:
            tenant = get_tenant_or_404(to_number)
            print(f"Call to screening number {to_number} without ForwardedFrom - using tenant configuration")
        except:
            # No tenant configured for this screening number
            vr = VoiceResponse()
            vr.say("This is a call screening service. To use this service, please set up call forwarding from your phone to this number.", voice="polly.Joanna")
            vr.hangup()
            return xml_response(vr)
    else:
        # Look up tenant by the ForwardedFrom number (user's real number)
        tenant = get_tenant_by_real_number(forwarded_from)
    

    
    # Check if caller is blocked
    remaining = is_blocked(tenant, from_digits)
    if remaining is not None:
        vr = VoiceResponse()
        vr.say("Sorry, this number is temporarily blocked due to repeated failed attempts. Goodbye.", voice="polly.Joanna")
        vr.hangup()
        return xml_response(vr)
    
    # Check if caller is whitelisted and should bypass authentication
    is_whitelisted = is_caller_whitelisted_bypass(tenant, from_digits)
    print(f"WHITELIST CHECK: Caller {from_digits}, Whitelisted: {is_whitelisted}")
    
    if is_whitelisted:
        # Clear any existing failures since this is a trusted caller
        clear_failures(tenant, from_digits)
        print(f"BYPASS AUTH: Caller {from_digits} is whitelisted, connecting directly")
        # Skip authentication and connect directly
        return on_verified(tenant, forwarded_from)
    
    print(f"AUTH REQUIRED: Caller {from_digits} not whitelisted, starting authentication")
    
    # Start verification process
    vr = VoiceResponse()
    verify_url = f"/voice/verify?attempts=0&to={quote(to_number or '')}&forwarded_from={quote(forwarded_from or '')}"
    print(f"GENERATING AUTH PROMPT: Verify URL = {verify_url}")
    
    # Add a brief pause to ensure audio channel is ready
    vr.pause(length=1)
    
    gather = Gather(
        input="speech dtmf",
        num_digits=4,
        action=verify_url,
        method="POST",
        timeout=8,  # Increased timeout
        speech_timeout="auto",
        finish_on_key=""
    )
    # Use a different voice and slower speech for better delivery
    gather.say("Please enter your four digit pin, or say your verbal code.", voice="alice", rate="slow")
    vr.append(gather)
    # Fallback if no input received - terminate call completely
    vr.say("No input received. This call will now end.", voice="polly.Joanna")
    vr.hangup()
    
    twiml_response = vr.to_xml()
    print(f"SENDING TWIML AUTH RESPONSE: {twiml_response}")
    return xml_response(vr)

@voice_bp.route('/retry', methods=['GET', 'POST'])
def voice_retry():
    """Handle retry attempts for failed verification (deprecated - now handled in verify endpoint)"""
    # This endpoint is deprecated in the new call forwarding model
    # All retry logic is now handled in the verify endpoint
    vr = VoiceResponse()
    vr.say("Invalid request. Goodbye.", voice="polly.Joanna")
    vr.hangup()
    return xml_response(vr)
    
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
    # This retry endpoint is deprecated

@voice_bp.route('/verify', methods=['POST'])
def voice_verify():
    """Handle PIN and verbal code verification"""
    to_number = request.args.get("to") or request.form.get("To")  # Shared screening number
    forwarded_from = request.args.get("forwarded_from") or request.form.get("ForwardedFrom")  # User's real number
    
    # Fix phone number formatting for tenant lookup
    if forwarded_from and not forwarded_from.startswith('+'):
        forwarded_from = '+' + forwarded_from.strip()
    
    from_digits = norm_digits(request.form.get("From", ""))
    attempts = int(request.args.get("attempts", request.form.get("attempts", 0)))
    pressed = request.form.get("Digits")
    speech = request.form.get("SpeechResult")
    
    # Handle forwarded calls for legacy single-user system
    if not forwarded_from:
        # When ForwardedFrom is missing, resolve tenant by screening number (To)
        if not to_number:
            vr = VoiceResponse()
            vr.say("Invalid request. Goodbye.", voice="polly.Joanna")
            vr.hangup()
            return xml_response(vr)
        try:
            tenant = get_tenant_or_404(to_number)
            print(f"Verify call to screening number {to_number} without ForwardedFrom - using tenant configuration")
        except:
            vr = VoiceResponse()
            vr.say("Invalid request. Goodbye.", voice="polly.Joanna")
            vr.hangup()
            return xml_response(vr)
    else:
        # Use the ForwardedFrom as the tenant lookup
        tenant = get_tenant_by_real_number(forwarded_from)
    
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
        # Auto-whitelist after successful PIN entry
        auto_whitelist_caller(tenant, from_digits, pressed if pressed != tenant.current_pin else None)
        return on_verified(tenant, forwarded_from)
    
    # Check verbal verification
    if speech:
        said = norm_speech(speech)
        
        # Exact match only
        if said == accepted_verbal:
            clear_failures(tenant, from_digits)
            # Auto-whitelist after successful verbal authentication
            auto_whitelist_caller(tenant, from_digits, None)
            return on_verified(tenant, forwarded_from)
        
        # Check whitelist verbal authentication
        if is_caller_whitelisted_verbal(tenant, from_digits) and said == accepted_verbal:
            clear_failures(tenant, from_digits)
            return on_verified(tenant, forwarded_from)
    
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
        action=f"/voice/verify?attempts={next_attempts}&to={quote(to_number or '')}&forwarded_from={quote(forwarded_from or '')}",
        method="POST",
        timeout=12,  # Increased timeout for better speech recognition
        speech_timeout=4,  # Longer speech timeout
        finish_on_key=""
    )
    gather.say("Incorrect code. Please try again with your four digit pin, or say your verbal code clearly.", voice="polly.Joanna")
    vr.append(gather)
    # Simple fallback - just hang up if no input
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
