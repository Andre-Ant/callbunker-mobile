import os
from flask import Response, abort
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from models import Tenant
import uuid

def xml_response(vr: VoiceResponse) -> Response:
    """Convert TwiML VoiceResponse to Flask Response"""
    return Response(vr.to_xml(), mimetype="application/xml")

def twilio_client() -> Client:
    """Get configured Twilio client"""
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    
    if not sid or not token:
        raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set")
    
    return Client(sid, token)

def public_app_url() -> str:
    """Get the public URL for this application"""
    url = os.getenv("PUBLIC_APP_URL")
    if not url:
        raise ValueError("PUBLIC_APP_URL environment variable not set")
    return url.rstrip("/")

def get_tenant_or_404(screening_number: str) -> Tenant:
    """Get tenant by screening number or return 404"""
    tenant = Tenant.query.get(screening_number)
    if not tenant:
        abort(404, description=f"Unknown screening number: {screening_number}")
    return tenant

def get_tenant_by_real_number(real_number: str) -> Tenant:
    """Get tenant by their real phone number (ForwardedFrom)"""
    if not real_number:
        abort(404, "Missing real number")
    
    # Normalize phone number format
    if not real_number.startswith('+'):
        real_number = '+' + real_number.strip()
    
    tenant = Tenant.query.get(real_number)
    if not tenant:
        abort(404, f"No user found for number: {real_number}. Please register this number in the CallBunker system.")
    
    return tenant

def generate_voice_access_token(user_id: int) -> str:
    """Generate Twilio Voice Access Token for mobile app calling"""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    api_key = os.environ.get("TWILIO_API_KEY") 
    api_secret = os.environ.get("TWILIO_API_SECRET")
    
    # Use environment vars if available, otherwise use account SID/token
    if not api_key or not api_secret:
        # For now, use account SID and token (less secure but works)
        api_key = account_sid
        api_secret = os.environ.get("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not api_secret:
        raise ValueError("Twilio credentials not properly configured")
    
    # Create unique identity for this user
    identity = f"callbunker_user_{user_id}"
    
    # Create access token
    access_token = AccessToken(account_sid, api_key, api_secret, identity=identity)
    
    # Create Voice grant
    voice_grant = VoiceGrant(
        outgoing_application_sid=None,  # We'll handle calls via REST API
        incoming_allow=True  # Allow incoming calls to this identity
    )
    
    # Add the grant to the token
    access_token.add_grant(voice_grant)
    
    return access_token.to_jwt()
