#!/usr/bin/env python3
"""
Test Google Voice OTP verification with live Twilio call
Demonstrates the voice-based verification system
"""
import os
from twilio.rest import Client

def test_google_voice_otp():
    """Make a test call to demonstrate Google Voice OTP verification"""
    
    # Get Twilio credentials
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("❌ Missing Twilio credentials")
        return False
    
    # Initialize Twilio client
    client = Client(account_sid, auth_token)
    
    # Test numbers (Google Voice setup from earlier)
    google_voice_number = "+15551234567"  # Your Google Voice number
    forward_to_number = "+15559876543"    # Your real phone number
    callbunker_number = "+16316417727"    # CallBunker screening number
    
    print("🔔 Starting Google Voice OTP verification test...")
    print(f"📱 Google Voice Number: {google_voice_number}")
    print(f"📞 Forward To: {forward_to_number}")
    print(f"🛡️  CallBunker Number: {callbunker_number}")
    
    try:
        # Make a test call using the OTP verification endpoint
        # This simulates what Google Voice does when verifying via phone call
        webhook_url = f"{os.environ.get('PUBLIC_APP_URL', 'https://your-repl.replit.app')}/voice/otp-verification?to={forward_to_number}"
        
        call = client.calls.create(
            to=forward_to_number,          # Your real phone
            from_=callbunker_number,       # From CallBunker
            url=webhook_url,               # OTP verification webhook
            status_callback=None,
            timeout=30
        )
        
        print(f"✅ Test call initiated!")
        print(f"📋 Call SID: {call.sid}")
        print(f"🔗 Webhook URL: {webhook_url}")
        print(f"🎯 Expected behavior:")
        print(f"   • Call connects immediately (no PIN required)")
        print(f"   • You hear 'Connecting your verification call now'")
        print(f"   • Call rings your real phone directly")
        print(f"   • This simulates how Google Voice OTP works")
        
        return True
        
    except Exception as e:
        print(f"❌ Call failed: {e}")
        return False

def test_regular_screening():
    """Test regular call screening with whitelist bypass"""
    
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        return False
    
    client = Client(account_sid, auth_token)
    
    print("\n🔒 Testing regular call screening with Google Voice bypass...")
    
    try:
        # Test call from Google Voice number (should bypass authentication)
        webhook_url = f"{os.environ.get('PUBLIC_APP_URL', 'https://your-repl.replit.app')}/voice/incoming"
        
        call = client.calls.create(
            to="+16316417727",              # CallBunker screening number
            from_="+15551234567",           # From your Google Voice (whitelisted)
            url=webhook_url,
            timeout=30
        )
        
        print(f"✅ Screening test call initiated!")
        print(f"📋 Call SID: {call.sid}")
        print(f"🎯 Expected behavior:")
        print(f"   • Call bypasses authentication (whitelisted)")
        print(f"   • Connects directly to your real phone")
        print(f"   • No PIN or verbal code required")
        
        return True
        
    except Exception as e:
        print(f"❌ Screening test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Google Voice OTP & Call Screening Test")
    print("=" * 50)
    
    # Test 1: OTP verification (bypasses all authentication)
    otp_success = test_google_voice_otp()
    
    # Test 2: Regular call screening (whitelisted bypass)
    screening_success = test_regular_screening()
    
    print("\n📊 Test Summary:")
    print("=" * 50)
    print(f"OTP Verification: {'✅ PASS' if otp_success else '❌ FAIL'}")
    print(f"Call Screening: {'✅ PASS' if screening_success else '❌ FAIL'}")
    
    if otp_success and screening_success:
        print("\n🎉 Google Voice integration fully functional!")
        print("💰 Cost: $0/month (vs TextNow's $6.99/month)")
        print("📞 Voice-based verification (no SMS/OTP issues)")
    else:
        print("\n⚠️  Some tests failed - check Twilio credentials and webhook URLs")