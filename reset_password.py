#!/usr/bin/env python3
"""
Password reset utility for CallBunker users
"""
import os
import sys
from werkzeug.security import generate_password_hash
from app import app, db
from models_multi_user import User

def reset_user_password(email, new_password):
    """Reset password for a specific user"""
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"Error: No user found with email {email}")
            return False
        
        # Generate new password hash
        password_hash = generate_password_hash(new_password)
        
        # Update user
        user.password_hash = password_hash
        db.session.commit()
        
        print(f"Password updated successfully for {user.name} ({email})")
        print(f"New password: {new_password}")
        return True

def list_users():
    """List all users in the system"""
    with app.app_context():
        users = User.query.all()
        print("Current users:")
        for user in users:
            print(f"  {user.email} - {user.name} - {user.assigned_twilio_number}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python reset_password.py list")
        print("  python reset_password.py reset <email> <new_password>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_users()
    elif command == "reset":
        if len(sys.argv) != 4:
            print("Usage: python reset_password.py reset <email> <new_password>")
            sys.exit(1)
        email = sys.argv[2]
        password = sys.argv[3]
        reset_user_password(email, password)
    else:
        print("Unknown command. Use 'list' or 'reset'")
        sys.exit(1)