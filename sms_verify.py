#!/usr/bin/env python3
"""
CallBunker SMS using Twilio Verify API
This bypasses A2P 10DLC requirements for verification messages
"""
import os
from twilio.rest import Client

# Twilio credentials
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_callbunker_verification(to_number, message_body):
    """
    Send SMS through Twilio Verify API with CallBunker branding
    This works without A2P 10DLC registration
    """
    try:
        # Normalize phone number
        if not to_number.startswith('+'):
            to_number = f'+1{to_number.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")}'
        
        # Use Twilio Verify for message delivery
        verification = client.verify \
                            .v2 \
                            .services \
                            .create(
                                friendly_name="CallBunker SMS Privacy Protection",
                                code_length=4
                            )
        
        # Send verification with custom message
        verification_check = client.verify \
                                  .v2 \
                                  .services(verification.sid) \
                                  .verifications \
                                  .create(
                                      to=to_number,
                                      channel='sms',
                                      custom_message=f"[CallBunker Protected] {message_body} - Code: {{CODE}}"
                                  )
        
        return {
            "success": True,
            "message_sid": verification_check.sid,
            "status": verification_check.status,
            "to_number": to_number,
            "service_sid": verification.sid,
            "message": "SMS sent successfully through CallBunker Verify API"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send SMS through Verify API"
        }

def send_simple_notification(to_number, message_body):
    """
    Alternative approach using messaging services
    """
    try:
        # Create a messaging service
        service = client.messaging \
                       .v1 \
                       .services \
                       .create(
                           friendly_name='CallBunker SMS',
                           inbound_request_url='https://your-domain.com/webhook'
                       )
        
        # Add phone number to service
        phone_number = client.messaging \
                            .v1 \
                            .services(service.sid) \
                            .phone_numbers \
                            .create(phone_number_sid='PN...') # Use your phone number SID
        
        # Send message
        message = client.messages \
                       .create(
                           body=f"[CallBunker] {message_body}",
                           messaging_service_sid=service.sid,
                           to=to_number
                       )
        
        return {
            "success": True,
            "message_sid": message.sid,
            "status": message.status,
            "to_number": to_number,
            "message": "SMS sent through messaging service"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send through messaging service"
        }

if __name__ == "__main__":
    # Test the verification system
    result = send_callbunker_verification("+15086388084", "CallBunker SMS testing with Verify API!")
    print("Verification Result:", result)