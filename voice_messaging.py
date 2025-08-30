#!/usr/bin/env python3
"""
CallBunker Voice Messaging System
Uses Twilio Programmable Voice with Text-to-Speech for privacy-protected messaging
"""
import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

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

CALLBUNKER_VOICE_NUMBER = get_twilio_number() or "+16316417727"

def send_voice_message(to_number, message_body):
    """
    Send voice message through CallBunker privacy protection using Text-to-Speech
    This bypasses A2P 10DLC requirements and works immediately
    """
    try:
        # Normalize phone number
        if not to_number.startswith('+'):
            to_number = f'+1{to_number.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")}'
        
        # Create TwiML for the voice message
        twiml_message = f"""
        <Response>
            <Say voice="Polly.Joanna">
                Hello! You have a new CallBunker protected message: {message_body}. 
                This message was sent anonymously through CallBunker privacy protection. 
                Your sender's real number remains completely hidden.
            </Say>
            <Pause length="1"/>
            <Say voice="Polly.Joanna">
                Thank you for using CallBunker privacy messaging. Goodbye!
            </Say>
        </Response>
        """
        
        # Make the call with TTS message
        call = client.calls.create(
            twiml=twiml_message,
            to=to_number,
            from_=CALLBUNKER_VOICE_NUMBER
        )
        
        return {
            "success": True,
            "call_sid": call.sid,
            "status": call.status,
            "from_number": CALLBUNKER_VOICE_NUMBER,
            "to_number": to_number,
            "message": "Voice message sent successfully through CallBunker privacy protection",
            "delivery_method": "voice_tts"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send voice message"
        }

def get_voice_message_status(call_sid):
    """
    Get the status of a voice message call
    """
    try:
        call = client.calls(call_sid).fetch()
        
        return {
            "success": True,
            "call_sid": call.sid,
            "status": call.status,
            "duration": call.duration,
            "start_time": call.start_time.isoformat() if call.start_time else None,
            "end_time": call.end_time.isoformat() if call.end_time else None,
            "from_number": call.from_formatted,
            "to_number": call.to_formatted
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get voice message status"
        }

def create_voice_webhook_response(message_body):
    """
    Create TwiML response for webhook-based voice messages
    """
    response = VoiceResponse()
    
    # Add greeting and message
    response.say(
        f"Hello! You have a new CallBunker protected message: {message_body}. "
        f"This message was sent anonymously through CallBunker privacy protection. "
        f"Your sender's real number remains completely hidden.",
        voice='Polly.Joanna'
    )
    
    response.pause(length=1)
    
    response.say(
        "Thank you for using CallBunker privacy messaging. Goodbye!",
        voice='Polly.Joanna'
    )
    
    return str(response)

if __name__ == "__main__":
    # Test the voice messaging system
    result = send_voice_message("+15086388084", "This is a test of CallBunker voice messaging! Your privacy is fully protected.")
    print("Voice Message Result:", result)