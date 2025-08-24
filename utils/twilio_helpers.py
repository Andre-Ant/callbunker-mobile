import os
from flask import Response, abort
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from models import Tenant

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
