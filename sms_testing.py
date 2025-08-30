import os
from twilio.rest import Client
from flask import Flask, request, jsonify
from flask_cors import CORS

# Twilio credentials
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Get the first available Twilio number
def get_twilio_number():
    try:
        numbers = client.incoming_phone_numbers.list()
        if numbers:
            return numbers[0].phone_number
        else:
            return None
    except:
        return None

TWILIO_PHONE_NUMBER = get_twilio_number() or "+16179421250"  # Fallback to Google Voice

def send_protected_sms(to_number, message_body):
    """
    Send SMS through CallBunker privacy protection using Twilio
    """
    try:
        # Normalize phone numbers
        if not to_number.startswith('+'):
            to_number = f'+1{to_number.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")}'
        
        # Try different approaches for better delivery
        delivery_attempts = [
            {"from_": "+18339424234", "label": "toll-free"},  # Toll-free number
            {"from_": "+16316417727", "label": "10DLC"},      # 10DLC number
        ]
        
        last_error = None
        
        for attempt in delivery_attempts:
            try:
                message = client.messages.create(
                    body=f"[CallBunker] {message_body}",
                    from_=attempt["from_"],
                    to=to_number
                )
                
                # If successful, break out of loop
                if message.sid:
                    print(f"SMS sent successfully using {attempt['label']} number: {attempt['from_']}")
                    break
                    
            except Exception as e:
                last_error = e
                print(f"Failed with {attempt['label']} number {attempt['from_']}: {e}")
                continue
        
        # If we get here, use the last successful message or raise the last error
        if 'message' not in locals():
            raise last_error or Exception("All delivery attempts failed")
        
        return {
            "success": True,
            "message_sid": message.sid,
            "status": message.status,
            "from_number": TWILIO_PHONE_NUMBER,
            "to_number": to_number,
            "message": "SMS sent successfully through CallBunker privacy protection"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send SMS"
        }

def get_sms_status(message_sid):
    """
    Check the delivery status of a sent message
    """
    try:
        message = client.messages(message_sid).fetch()
        return {
            "success": True,
            "status": message.status,
            "date_sent": str(message.date_sent),
            "error_code": message.error_code,
            "error_message": message.error_message
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }