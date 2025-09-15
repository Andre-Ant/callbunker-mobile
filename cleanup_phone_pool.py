#!/usr/bin/env python3
"""
Clean up phone pool - remove fake numbers and keep only real Twilio numbers
"""
import os
import sys
from app import app, db
from models_multi_user import TwilioPhonePool
from utils.twilio_helpers import twilio_client

def get_real_twilio_numbers():
    """Get actual phone numbers from Twilio account"""
    try:
        client = twilio_client()
        numbers = client.incoming_phone_numbers.list()
        real_numbers = [number.phone_number for number in numbers]
        print(f"Found {len(real_numbers)} real Twilio numbers:")
        for num in real_numbers:
            print(f"  {num}")
        return real_numbers
    except Exception as e:
        print(f"Error fetching Twilio numbers: {e}")
        return []

def cleanup_phone_pool():
    """Remove fake numbers and keep only real Twilio numbers"""
    with app.app_context():
        print("Cleaning up phone pool...")
        
        # Get real numbers from Twilio
        real_numbers = get_real_twilio_numbers()
        if not real_numbers:
            print("No real Twilio numbers found - aborting cleanup")
            return
        
        # Get current pool numbers
        current_numbers = TwilioPhonePool.query.all()
        print(f"\nCurrent pool has {len(current_numbers)} numbers:")
        
        removed_count = 0
        kept_count = 0
        
        for pool_number in current_numbers:
            if pool_number.phone_number in real_numbers:
                print(f"  KEEP: {pool_number.phone_number} (real Twilio number)")
                kept_count += 1
            else:
                print(f"  REMOVE: {pool_number.phone_number} (fake/test number)")
                
                # Don't remove if assigned to a user - just flag it
                if pool_number.is_assigned:
                    print(f"    WARNING: {pool_number.phone_number} is assigned to user but not in Twilio!")
                else:
                    db.session.delete(pool_number)
                    removed_count += 1
        
        # Commit changes
        db.session.commit()
        
        print(f"\nCleanup complete:")
        print(f"  Kept: {kept_count} real numbers")
        print(f"  Removed: {removed_count} fake numbers")
        
        # Show final status
        total = TwilioPhonePool.query.count()
        available = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        assigned = TwilioPhonePool.query.filter_by(is_assigned=True).count()
        
        print(f"\nFinal status: {total} total, {available} available, {assigned} assigned")
        
        if available == 0:
            print("WARNING: No available numbers left! Consider adding more Twilio numbers.")

if __name__ == "__main__":
    cleanup_phone_pool()