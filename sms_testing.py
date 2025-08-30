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
    Send SMS through CallBunker privacy protection using Google Voice
    """
    try:
        # Send message using available Twilio number
        message = client.messages.create(
            body=f"[CallBunker Protected] {message_body}",
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        
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