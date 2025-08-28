#!/usr/bin/env python3
"""
Setup script to populate the Twilio phone pool for multi-user CallBunker
"""
import os
import sys
from app import app, db
from models_multi_user import TwilioPhonePool

def add_phone_to_pool(phone_number, monthly_cost=1.00):
    """Add a phone number to the pool"""
    # Normalize phone number
    digits_only = ''.join(filter(str.isdigit, phone_number))
    
    if len(digits_only) == 10:
        normalized = f"+1{digits_only}"
    elif len(digits_only) == 11 and digits_only.startswith('1'):
        normalized = f"+{digits_only}"
    else:
        print(f"Invalid phone number format: {phone_number}")
        return False
    
    # Check if already exists
    existing = TwilioPhonePool.query.filter_by(phone_number=normalized).first()
    if existing:
        print(f"Phone number {normalized} already in pool")
        return False
    
    # Add to pool
    pool_entry = TwilioPhonePool(
        phone_number=normalized,
        monthly_cost=monthly_cost
    )
    
    db.session.add(pool_entry)
    db.session.commit()
    
    print(f"Added {normalized} to phone pool (${monthly_cost}/month)")
    return True

def main():
    """Setup initial phone pool"""
    with app.app_context():
        print("Setting up Twilio phone pool...")
        
        # Add some example numbers (replace with your actual Twilio numbers)
        phones_to_add = [
            "+16316417728",  # Second CallBunker number for multi-user
            "+16316417729",  # Third number
            "+16316417730",  # Fourth number
        ]
        
        added_count = 0
        for phone in phones_to_add:
            if add_phone_to_pool(phone):
                added_count += 1
        
        print(f"\nSetup complete! Added {added_count} phone numbers to pool.")
        
        # Show current pool status
        total = TwilioPhonePool.query.count()
        available = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        assigned = TwilioPhonePool.query.filter_by(is_assigned=True).count()
        
        print(f"Pool status: {total} total, {available} available, {assigned} assigned")

if __name__ == "__main__":
    main()