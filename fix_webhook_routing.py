#!/usr/bin/env python3
"""
Fix webhook routing to distinguish between OTP verification and regular calls
"""
import os
from twilio.rest import Client

def update_twilio_webhook():
    """Update Twilio webhook to use regular incoming endpoint instead of OTP-only"""
    
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    public_url = os.environ.get('PUBLIC_APP_URL', 'https://your-repl.replit.app')
    
    if not account_sid or not auth_token:
        print("❌ Missing Twilio credentials")
        return False
    
    client = Client(account_sid, auth_token)
    callbunker_number = "+16316417727"
    
    # Use the regular incoming endpoint that handles both OTP and regular calls
    regular_webhook_url = f"{public_url}/voice/incoming"
    
    try:
        phone_numbers = client.incoming_phone_numbers.list(phone_number=callbunker_number)
        
        if not phone_numbers:
            print(f"❌ Phone number {callbunker_number} not found")
            return False
        
        # Update to use regular incoming endpoint
        phone_numbers[0].update(voice_url=regular_webhook_url)
        
        print(f"✅ Webhook updated to regular incoming endpoint!")
        print(f"📞 Phone Number: {callbunker_number}")
        print(f"🔗 New Webhook URL: {regular_webhook_url}")
        print(f"🎯 Now handles:")
        print(f"   • Regular calls: PIN/verbal authentication")
        print(f"   • OTP verification: Direct forwarding")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update webhook: {e}")
        return False

if __name__ == "__main__":
    update_twilio_webhook()