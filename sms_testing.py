import os
from twilio.rest import Client
from flask import Flask, request, jsonify
from flask_cors import CORS

# Twilio credentials
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
GOOGLE_VOICE_NUMBER = "+16179421250"  # Your Google Voice number

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_protected_sms(to_number, message_body):
    """
    Send SMS through CallBunker privacy protection using Google Voice
    """
    try:
        # Send message using Google Voice number as sender
        message = client.messages.create(
            body=f"[CallBunker Protected] {message_body}",
            from_=GOOGLE_VOICE_NUMBER,
            to=to_number
        )
        
        return {
            "success": True,
            "message_sid": message.sid,
            "status": message.status,
            "from_number": GOOGLE_VOICE_NUMBER,
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