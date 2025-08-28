#!/usr/bin/env python3
"""
Configure Twilio webhook for Google Voice OTP verification
Sets up +16316417727 to handle verification calls from Google Voice
"""
import os
from twilio.rest import Client

def setup_twilio_webhook():
    """Configure Twilio to use OTP verification endpoint for CallBunker number"""
    
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    public_url = os.environ.get('PUBLIC_APP_URL', 'https://your-repl.replit.app')
    
    if not account_sid or not auth_token:
        print("❌ Missing Twilio credentials")
        return False
    
    client = Client(account_sid, auth_token)
    callbunker_number = "+16316417727"
    
    # Configure the webhook URL for OTP verification
    otp_webhook_url = f"{public_url}/voice/otp-verification"
    
    try:
        # Get the phone number resource
        phone_numbers = client.incoming_phone_numbers.list(phone_number=callbunker_number)
        
        if not phone_numbers:
            print(f"❌ Phone number {callbunker_number} not found in account")
            return False
        
        phone_number_sid = phone_numbers[0].sid
        
        # Update the webhook URL
        phone_numbers[0].update(voice_url=otp_webhook_url)
        
        print(f"✅ Twilio webhook configured successfully!")
        print(f"📞 Phone Number: {callbunker_number}")
        print(f"🔗 Webhook URL: {otp_webhook_url}")
        print(f"📋 Phone Number SID: {phone_number_sid}")
        
        print(f"\n🎯 Setup Complete:")
        print(f"   • When Google Voice calls {callbunker_number} for verification")
        print(f"   • Twilio will POST to {otp_webhook_url}")
        print(f"   • Call will forward directly to +15086388084")
        print(f"   • You'll receive the Google Voice verification call")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to configure webhook: {e}")
        return False

def test_otp_verification():
    """Test the OTP verification endpoint"""
    import requests
    
    public_url = os.environ.get('PUBLIC_APP_URL', 'http://localhost:5000')
    test_url = f"{public_url}/voice/otp-verification"
    
    # Simulate Google Voice calling for verification
    test_data = {
        'From': '+18005551234',  # Google Voice verification service
        'To': '+16316417727',    # CallBunker number
        'CallSid': 'test-otp-verification'
    }
    
    try:
        response = requests.post(test_url, data=test_data)
        print(f"\n🧪 OTP Verification Test:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200 and "This is your Google Voice verification call" in response.text:
            print("✅ OTP verification endpoint working correctly!")
            return True
        else:
            print("❌ OTP verification endpoint not responding correctly")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Google Voice OTP Verification Setup")
    print("=" * 50)
    
    # Setup webhook
    webhook_success = setup_twilio_webhook()
    
    # Test endpoint
    test_success = test_otp_verification()
    
    print(f"\n📊 Setup Summary:")
    print("=" * 50)
    print(f"Webhook Configuration: {'✅ SUCCESS' if webhook_success else '❌ FAILED'}")
    print(f"Endpoint Test: {'✅ SUCCESS' if test_success else '❌ FAILED'}")
    
    if webhook_success and test_success:
        print(f"\n🎉 Google Voice OTP verification ready!")
        print(f"💡 Next Steps:")
        print(f"   1. Add +16316417727 to your Google Voice account")
        print(f"   2. Google Voice will call this number for verification")
        print(f"   3. You'll receive the call on +15086388084")
        print(f"   4. Enter the verification code Google provides")
    else:
        print(f"\n⚠️  Setup incomplete - check errors above")