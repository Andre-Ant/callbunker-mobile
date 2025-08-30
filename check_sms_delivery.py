#!/usr/bin/env python3
"""
Quick SMS delivery checker for CallBunker
"""
import os
from twilio.rest import Client
import time

# Twilio setup
client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))

def check_recent_messages():
    """Check status of recent SMS messages"""
    print("📱 CallBunker SMS Status Check")
    print("=" * 40)
    
    try:
        messages = client.messages.list(limit=5)
        
        for msg in messages:
            print(f"Message ID: {msg.sid}")
            print(f"From: {msg.from_}")
            print(f"To: {msg.to}")
            print(f"Status: {msg.status}")
            print(f"Body: {msg.body[:50]}...")
            print(f"Date: {msg.date_created}")
            if msg.error_code:
                print(f"Error: {msg.error_code} - {msg.error_message}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error checking messages: {e}")

if __name__ == "__main__":
    check_recent_messages()