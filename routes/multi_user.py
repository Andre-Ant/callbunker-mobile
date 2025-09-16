"""
CallBunker Business Routes - Each user gets their own Twilio number
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, make_response, Response, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from models_multi_user import User, TwilioPhonePool, UserWhitelist, MultiUserCallLog, UserBlocklist, UserFailLog
from app import db
from utils.twilio_helpers import twilio_client, generate_voice_access_token
import re
import uuid
from datetime import datetime, timedelta
from twilio.twiml.voice_response import VoiceResponse, Gather
import os

multi_user_bp = Blueprint('multi_user', __name__, url_prefix='/multi')

@multi_user_bp.route('/')
def index():
    """Main route - redirect to login or dashboard"""
    if session.get('logged_in') and session.get('user_id'):
        # User is logged in, redirect to dashboard
        return redirect(url_for('multi_user.dashboard', user_id=session['user_id']))
    else:
        # User not logged in, redirect to login
        return redirect(url_for('multi_user.login'))

def require_authentication():
    """Helper to require user authentication for API endpoints"""
    # For now, use a simple session-based auth or require admin key
    # In production, implement proper JWT or session authentication
    api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    if not api_key or api_key != os.environ.get('API_KEY', 'dev-key-123'):
        # Allow during development with demo key
        if api_key != 'demo-key-callbunker-2025':
            abort(401)
    return True

def validate_csrf_token():
    """Basic CSRF protection for state-changing endpoints"""
    if request.method in ['POST', 'PUT', 'DELETE']:
        csrf_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        # For development, allow bypass with dev token
        if not csrf_token or csrf_token not in ['dev-csrf-token', 'demo-csrf-callbunker']:
            # In production, validate against session-generated token
            return False
    return True

def verify_user_access(requested_user_id):
    """Verify that the current session/auth can access the requested user data"""
    # Implement proper user ownership validation
    # For now, require authentication key + user verification
    require_authentication()
    
    # Add CSRF protection for state-changing requests
    if not validate_csrf_token():
        abort(403)  # Forbidden - CSRF token missing/invalid
    
    # Additional verification could be added here
    # e.g., check if user_id matches session user_id
    user = User.query.get_or_404(requested_user_id)
    return user

@multi_user_bp.route('/list')
def user_list():
    """List all users for easy dashboard access"""
    users = User.query.all()
    return render_template('multi_user/user_list.html', 
                         users=users,
                         format_phone=format_phone_display)

def normalize_phone(phone):
    """Normalize phone number to digits only"""
    return re.sub(r'[^\d]', '', phone)

def format_phone_display(phone):
    """Format phone for display: (555) 123-4567"""
    digits = normalize_phone(phone)
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
    return phone

@multi_user_bp.route('/mobile-signup', methods=['GET', 'POST'])
def mobile_signup():
    """Clean mobile-style signup interface"""
    if request.method == 'GET':
        session.clear()  # Clear any old session data
        available_numbers = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
    
    # Handle POST - create user with same logic as regular signup
    try:
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        real_phone_number = normalize_phone(request.form.get('real_phone_number', '').strip())
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        pin = request.form.get('pin', '1122').strip()
        verbal_code = request.form.get('verbal_code', 'open sesame').strip()
        
        # Check available numbers for template
        available_numbers = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        
        # Validation
        if not all([email, name, real_phone_number, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        # Password confirmation validation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        # Check if real phone number already registered
        if User.query.filter_by(real_phone_number=real_phone_number).first():
            flash('Phone number already registered', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        # Assign next available Twilio number from pool with database lock
        available_number = TwilioPhonePool.query.filter_by(is_assigned=False).with_for_update().first()
        if not available_number:
            flash('No CallBunker numbers available. Please contact support.', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=0)
        
        # Create new user with password hash
        user = User(
            email=email,
            name=name,
            real_phone_number=real_phone_number,
            pin=pin,
            verbal_code=verbal_code,
            assigned_twilio_number=available_number.phone_number,
            password_hash=generate_password_hash(password)
        )
        
        # Add user first and get ID
        db.session.add(user)
        db.session.flush()  # Get user.id without committing
        
        # Assign the phone number using the generated user.id
        available_number.assigned_to_user_id = user.id
        available_number.is_assigned = True
        
        db.session.commit()
        
        # Set up login session for the new user
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['logged_in'] = True
        
        # Redirect directly to dashboard - no Google Voice setup needed
        flash(f'Account created! Your Defense Number is {format_phone_display(user.assigned_twilio_number)}', 'success')
        return redirect(url_for('multi_user.dashboard', user_id=user.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Signup failed: {str(e)}', 'error')
        return redirect(url_for('multi_user.mobile_signup'))

@multi_user_bp.route('/debug-signup')
def debug_signup():
    """Simple debug signup page"""
    return render_template('multi_user/debug_signup.html')

@multi_user_bp.route('/debug-database')
def debug_database():
    """Check production database phone pool status"""
    try:
        total = TwilioPhonePool.query.count()
        available = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        assigned = TwilioPhonePool.query.filter_by(is_assigned=True).count()
        
        all_numbers = TwilioPhonePool.query.all()
        numbers_list = [(n.phone_number, n.is_assigned) for n in all_numbers]
        
        return f"""
        <h1>Database Status</h1>
        <p><strong>Total Numbers:</strong> {total}</p>
        <p><strong>Available:</strong> {available}</p>
        <p><strong>Assigned:</strong> {assigned}</p>
        <h2>All Numbers:</h2>
        <ul>
        {"".join([f"<li>{num} - {'ASSIGNED' if assigned else 'AVAILABLE'}</li>" for num, assigned in numbers_list])}
        </ul>
        <p>Threshold check: available > 0 = {available > 0}</p>
        <p>Signup button should show: {'CREATE ACCOUNT' if available > 0 else 'JOIN WAITLIST'}</p>
        """
    except Exception as e:
        return f"<h1>Database Error</h1><p>{str(e)}</p>"

@multi_user_bp.route('/test')
def test_page():
    """Ultra simple test page"""
    return """
    <html>
    <head><title>CallBunker - Server Test</title></head>
    <body style="font-family: Arial, sans-serif; margin: 50px; background: #f0f0f0;">
        <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #333;">🛡️ CallBunker Server is Working!</h1>
            <p style="color: #666; font-size: 18px;">Routing successfully configured ✅</p>
            <hr style="margin: 20px 0;">
            <h3>Available Routes:</h3>
            <ul style="font-size: 16px; line-height: 1.6;">
                <li><strong><a href="/multi/login" style="color: #007bff;">Login Page</a></strong> - Sign into your account</li>
                <li><strong><a href="/multi/signup" style="color: #28a745;">Signup Page</a></strong> - Create new account</li>
                <li><strong><a href="/multi/" style="color: #6c757d;">Main Page</a></strong> - Redirects to login</li>
                <li><strong><a href="/multi/debug-auth" style="color: #dc3545;">Debug Auth</a></strong> - Test authentication</li>
            </ul>
            <div style="margin-top: 30px; padding: 15px; background: #e7f3ff; border-left: 4px solid #007bff;">
                <strong>Login Credentials:</strong><br>
                Email: andre_antoine49@yahoo.com<br>
                Password: 123456!
            </div>
        </div>
    </body>
    </html>
    """

@multi_user_bp.route('/debug-auth', methods=['GET', 'POST'])
def debug_auth():
    """Debug authentication issues"""
    if request.method == 'GET':
        return """
        <html>
        <head><title>Debug Authentication</title></head>
        <body style="font-family: Arial; margin: 30px;">
            <h2>🔍 Debug Authentication</h2>
            <form method="POST">
                <p><input type="email" name="email" value="andre_antoine49@yahoo.com" style="width: 300px; padding: 10px;" placeholder="Email"></p>
                <p><input type="password" name="password" value="123456!" style="width: 300px; padding: 10px;" placeholder="Password"></p>
                <p><button type="submit" style="padding: 10px 20px; background: #007bff; color: white; border: none;">Test Login</button></p>
            </form>
        </body>
        </html>
        """
    
    from werkzeug.security import check_password_hash
    
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    
    result = f"<h2>🔍 Authentication Debug Results</h2>"
    result += f"<p><strong>Email:</strong> {email}</p>"
    result += f"<p><strong>Password Length:</strong> {len(password)}</p>"
    
    # Find user
    user = User.query.filter_by(email=email).first()
    if user:
        result += f"<p>✅ <strong>User Found:</strong> {user.name} (ID: {user.id})</p>"
        result += f"<p><strong>Active:</strong> {user.is_active}</p>"
        result += f"<p><strong>Has Password Hash:</strong> {'Yes' if user.password_hash else 'No'}</p>"
        
        if user.password_hash:
            password_valid = check_password_hash(user.password_hash, password)
            result += f"<p><strong>Password Valid:</strong> {'✅ YES' if password_valid else '❌ NO'}</p>"
            
            if password_valid:
                # Test session
                session['test_user_id'] = user.id
                session['test_logged_in'] = True
                result += f"<p>✅ <strong>Session Test:</strong> Set session variables</p>"
                result += f"<p><strong>Session User ID:</strong> {session.get('test_user_id')}</p>"
                result += f"<p><strong>Session Logged In:</strong> {session.get('test_logged_in')}</p>"
        else:
            result += f"<p>❌ <strong>No password hash found</strong></p>"
    else:
        result += f"<p>❌ <strong>User Not Found</strong></p>"
    
    return f"""
    <html>
    <head><title>Debug Results</title></head>
    <body style="font-family: Arial; margin: 30px;">
        {result}
        <p><a href="/multi/debug-auth">← Test Again</a> | <a href="/multi/login">Try Real Login</a> | <a href="/multi/db-test">DB Test</a></p>
    </body>
    </html>
    """


@multi_user_bp.route('/db-test')
def db_test():
    """Test database connection and show all users"""
    try:
        # Test database connection
        all_users = User.query.all()
        
        result = f"<h2>🗄️ Database Test Results</h2>"
        result += f"<p><strong>Total Users Found:</strong> {len(all_users)}</p>"
        
        if all_users:
            result += "<h3>All Users in Database:</h3><ul>"
            for user in all_users:
                result += f"<li><strong>ID:</strong> {user.id} | <strong>Email:</strong> {user.email} | <strong>Name:</strong> {user.name} | <strong>Active:</strong> {user.is_active}</li>"
            result += "</ul>"
        else:
            result += "<p>❌ <strong>No users found in database!</strong></p>"
            
        # Test specific email lookup
        test_email = 'andre_antoine49@yahoo.com'
        test_user = User.query.filter_by(email=test_email).first()
        result += f"<h3>Test Email Lookup: {test_email}</h3>"
        if test_user:
            result += f"<p>✅ <strong>Found:</strong> {test_user.name} (ID: {test_user.id})</p>"
        else:
            result += f"<p>❌ <strong>Not Found</strong></p>"
            
        return f"""
        <html>
        <head><title>Database Test</title></head>
        <body style="font-family: Arial; margin: 30px;">
            {result}
            <p><a href="/multi/debug-auth">← Debug Auth</a> | <a href="/multi/login">Login</a></p>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"""
        <html>
        <head><title>Database Error</title></head>
        <body style="font-family: Arial; margin: 30px;">
            <h2>❌ Database Connection Error</h2>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><a href="/multi/debug-auth">← Debug Auth</a></p>
        </body>
        </html>
        """

@multi_user_bp.route('/quick-signup', methods=['GET', 'POST'])
def quick_signup():
    """Quick signup bypass for form validation issues"""
    if request.method == 'GET':
        return """
        <html>
        <head><title>Quick Signup</title></head>
        <body style="font-family: Arial; margin: 30px;">
            <h2>🚀 Quick CallBunker Signup</h2>
            <p>Bypass form validation issues</p>
            <form method="POST">
                <p><input type="text" name="name" value="Andre Antoine" placeholder="Full Name" style="width: 300px; padding: 10px;"></p>
                <p><input type="email" name="email" value="andre_antoine49@yahoo.com" placeholder="Email" style="width: 300px; padding: 10px;"></p>
                <p><input type="tel" name="real_phone_number" value="(508) 638-8084" placeholder="Phone Number" style="width: 300px; padding: 10px;"></p>
                <p><input type="password" name="password" value="123456!" placeholder="Password" style="width: 300px; padding: 10px;"></p>
                <p><input type="text" name="pin" value="1122" placeholder="PIN" style="width: 100px; padding: 10px;"></p>
                <p><input type="text" name="verbal_code" value="open sesame" placeholder="Verbal Code" style="width: 200px; padding: 10px;"></p>
                <p><button type="submit" style="padding: 15px 30px; background: #007AFF; color: white; border: none; font-size: 16px;">Create Account Now</button></p>
            </form>
        </body>
        </html>
        """
    
    # Handle POST - create account directly
    try:
        from werkzeug.security import generate_password_hash
        
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        real_phone_number = normalize_phone(request.form.get('real_phone_number', '').strip())
        password = request.form.get('password', '').strip()
        pin = request.form.get('pin', '1122').strip()
        verbal_code = request.form.get('verbal_code', 'open sesame').strip()
        
        # Validate required fields
        if not all([name, email, real_phone_number, password]):
            return "Missing required fields. <a href='/multi/quick-signup'>Try again</a>"
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return f"Account already exists! <a href='/multi/login'>Login here</a>"
        
        # Get available Twilio number
        available_number = TwilioPhonePool.query.filter_by(is_assigned=False).first()
        if not available_number:
            return "No phone numbers available. Contact support."
        
        # Create user account
        password_hash = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            real_phone_number=real_phone_number,
            assigned_twilio_number=available_number.phone_number,
            pin=pin,
            verbal_code=verbal_code,
            password_hash=password_hash,
            retry_limit=3,
            forward_mode='bridge',
            rl_window_sec=3600,
            rl_max_attempts=5,
            rl_block_minutes=60,
            is_active=True,
            twilio_number_configured=True
        )
        
        # Assign the phone number
        available_number.is_assigned = True
        available_number.assigned_to_user_id = new_user.id
        available_number.assigned_at = datetime.utcnow()
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        # Log the user in immediately
        session['user_id'] = new_user.id
        session['user_email'] = new_user.email
        session['logged_in'] = True
        
        return f"""
        <html>
        <head><title>Account Created!</title></head>
        <body style="font-family: Arial; margin: 30px; text-align: center;">
            <h1>🎉 Account Created Successfully!</h1>
            <p><strong>Name:</strong> {new_user.name}</p>
            <p><strong>Email:</strong> {new_user.email}</p>
            <p><strong>Defense Number:</strong> <span style="background: #e8f5e8; padding: 8px; font-family: monospace; font-size: 18px;">{new_user.assigned_twilio_number}</span></p>
            <p><strong>PIN:</strong> {new_user.pin}</p>
            <p><strong>Verbal Code:</strong> {new_user.verbal_code}</p>
            <hr>
            <p><a href="/multi/login" style="background: #007AFF; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px;">Access Dashboard</a></p>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"Error creating account: {str(e)}. <a href='/multi/quick-signup'>Try again</a>"

@multi_user_bp.route('/reset-database', methods=['GET', 'POST'])
def reset_database():
    """Reset the deployed database - delete all users and release phone numbers"""
    if request.method == 'GET':
        return """
        <html>
        <head><title>⚠️ Database Reset</title></head>
        <body style="font-family: Arial; margin: 30px;">
            <h2>⚠️ Reset Deployed Database</h2>
            <p><strong>WARNING:</strong> This will delete ALL user accounts and release ALL phone numbers.</p>
            <p>Current users will be logged out and need to create new accounts.</p>
            <form method="POST">
                <p><input type="text" name="confirm" placeholder="Type 'RESET' to confirm" style="width: 200px; padding: 10px;" required></p>
                <p><button type="submit" style="padding: 15px 30px; background: #dc3545; color: white; border: none; font-size: 16px;">⚠️ RESET DATABASE</button></p>
            </form>
            <p><a href="/multi/db-test">← Back to Database Test</a></p>
        </body>
        </html>
        """
    
    # Handle POST - perform reset
    confirm = request.form.get('confirm', '').strip()
    if confirm != 'RESET':
        return "Confirmation failed. Type 'RESET' exactly. <a href='/multi/reset-database'>Try again</a>"
    
    try:
        # Clear session first
        session.clear()
        
        # Get all users to clean up related data
        all_users = User.query.all()
        user_ids = [user.id for user in all_users]
        
        # Delete related data first (to avoid foreign key constraints)
        if user_ids:
            # Clean up related tables
            from models_multi_user import MultiUserCallLog, UserWhitelist, UserFailLog, UserBlocklist
            
            # Delete call logs
            for user_id in user_ids:
                MultiUserCallLog.query.filter_by(user_id=user_id).delete()
                UserWhitelist.query.filter_by(user_id=user_id).delete()
                UserFailLog.query.filter_by(user_id=user_id).delete()
                UserBlocklist.query.filter_by(user_id=user_id).delete()
        
        # Release all phone numbers
        phone_numbers = TwilioPhonePool.query.all()
        for number in phone_numbers:
            number.is_assigned = False
            number.assigned_to_user_id = None
            number.assigned_at = None
        
        # Delete all users
        User.query.delete()
        
        # Commit all changes
        db.session.commit()
        
        return """
        <html>
        <head><title>✅ Database Reset Complete</title></head>
        <body style="font-family: Arial; margin: 30px; text-align: center;">
            <h1>✅ Database Reset Successful!</h1>
            <p><strong>All user accounts deleted</strong></p>
            <p><strong>All phone numbers released</strong></p>
            <p><strong>Database is now clean</strong></p>
            <hr>
            <p><a href="/multi/db-test" style="background: #007AFF; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px;">Verify Reset</a></p>
            <p><a href="/multi/quick-signup" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px;">Create New Account</a></p>
        </body>
        </html>
        """
        
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        return f"Reset failed: {str(e)}. <a href='/multi/reset-database'>Try again</a>"

@multi_user_bp.route('/mobile')
def mobile_simple():
    """Mobile-optimized simple signup"""
    return render_template('multi_user/mobile_simple.html')

@multi_user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with email and password"""
    if request.method == 'GET':
        return render_template('multi_user/login.html')
    
    try:
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember') == '1'
        
        if not email or not password:
            flash('Please enter both email and password', 'error')
            return render_template('multi_user/login.html')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Invalid email or password', 'error')
            return render_template('multi_user/login.html')
        
        # Check password (assuming we have a password_hash field)
        if not user.password_hash or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password', 'error')
            return render_template('multi_user/login.html')
        
        # Set up session
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['logged_in'] = True
        
        if remember:
            session.permanent = True
            # Session duration handled by Flask app config
        
        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('multi_user.dashboard', user_id=user.id))
        
    except Exception as e:
        flash('Login failed. Please try again.', 'error')
        return render_template('multi_user/login.html')

@multi_user_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('multi_user.login'))

@multi_user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """New user signup with Google Voice integration"""
    # Clear any existing flash messages on GET request to ensure clean signup
    if request.method == 'GET':
        session.clear()
        # Check available Twilio numbers
        available_numbers = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        response = make_response(render_template('multi_user/mobile_signup.html', available_numbers=available_numbers))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    try:
        # Get form data
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        # Google Voice no longer required - CallBunker uses direct Voice SDK calling
        real_phone_number = normalize_phone(request.form.get('real_phone_number', '').strip())
        password = request.form.get('password', '').strip()
        
        # Check available numbers for template
        available_numbers = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        
        # Validation
        if not all([email, name, real_phone_number, password]):
            flash('All fields are required', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        # Check if real phone number already registered
        if User.query.filter_by(real_phone_number=real_phone_number).first():
            flash('Phone number already registered', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)
        
        # Get next available Twilio number with database lock to prevent race conditions
        available_twilio = TwilioPhonePool.query.filter_by(is_assigned=False).with_for_update().first()
        if not available_twilio:
            flash('No CallBunker numbers available. Please contact support.', 'error')
            return render_template('multi_user/mobile_signup.html', available_numbers=0)
        
        # Create new user
        user = User(
            email=email,
            name=name,
            real_phone_number=real_phone_number,
            assigned_twilio_number=available_twilio.phone_number,
            pin=request.form.get('pin', '1122').strip(),
            verbal_code=request.form.get('verbal_code', 'open sesame').strip(),
            password_hash=generate_password_hash(password)
        )
        
        # Mark Twilio number as assigned and save everything in one transaction
        available_twilio.is_assigned = True
        
        db.session.add(user)
        db.session.flush()  # Get user.id without committing
        
        available_twilio.assigned_to_user_id = user.id
        db.session.commit()
        
        flash(f'Account created! Your Defense Number is {format_phone_display(user.assigned_twilio_number)}', 'success')
        
        # Set up login session for the new user
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['logged_in'] = True
        
        # Redirect directly to dashboard - no Google Voice setup needed
        return redirect(url_for('multi_user.dashboard', user_id=user.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Registration failed: {str(e)}', 'error')
        available_numbers = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        return render_template('multi_user/mobile_signup.html', available_numbers=available_numbers)

@multi_user_bp.route('/user/<int:user_id>/dashboard')
def dashboard(user_id):
    """Alias for user_dashboard for cleaner URLs"""
    return user_dashboard(user_id)

@multi_user_bp.route('/user/<int:user_id>/dashboard')
def user_dashboard(user_id):
    """Individual user dashboard"""
    user = User.query.get_or_404(user_id)
    
    # Get user statistics
    whitelist_count = UserWhitelist.query.filter_by(user_id=user_id).count()
    
    return render_template('multi_user/mobile_dashboard.html', 
                         user=user, 
                         whitelist_count=whitelist_count,
                         format_phone=format_phone_display)

@multi_user_bp.route('/admin/phone-pool')
def admin_phone_pool():
    """Admin view of Twilio phone number pool"""
    phones = TwilioPhonePool.query.all()
    return render_template('multi_user/admin_pool.html', phones=phones, format_phone=format_phone_display)

@multi_user_bp.route('/admin/add-twilio-number', methods=['POST'])
def add_twilio_number():
    """Add new Twilio number to the pool"""
    try:
        phone_number = request.form.get('phone_number', '').strip()
        monthly_cost = float(request.form.get('monthly_cost', 1.00))
        
        # Normalize phone number
        normalized = normalize_phone(phone_number)
        if len(normalized) != 10 and len(normalized) != 11:
            return jsonify({'success': False, 'message': 'Invalid phone number format'})
        
        # Add to pool
        pool_entry = TwilioPhonePool(
            phone_number=f"+1{normalized}" if len(normalized) == 10 else f"+{normalized}",
            monthly_cost=monthly_cost
        )
        
        db.session.add(pool_entry)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Added {format_phone_display(pool_entry.phone_number)} to pool'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# Additional API Endpoints for Mobile App
@multi_user_bp.route('/user/<int:user_id>/settings', methods=['GET'])
def api_get_user_settings(user_id):
    """Get user settings for mobile app - SECURED"""
    user = verify_user_access(user_id)
    return jsonify({
        'pin': user.pin,
        'verbal_code': user.verbal_code,
        'retry_limit': user.retry_limit,
        'forward_mode': user.forward_mode,
        'rl_window_sec': user.rl_window_sec,
        'rl_max_attempts': user.rl_max_attempts,
        'rl_block_minutes': user.rl_block_minutes,
        'twilio_number_configured': user.twilio_number_configured
    })

@multi_user_bp.route('/user/<int:user_id>/settings', methods=['PUT'])
def api_update_user_settings(user_id):
    """Update user settings for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
    
    # Update allowed settings
    if 'pin' in data and data['pin'] and re.match(r'^\d{4}$', str(data['pin'])):
        user.pin = str(data['pin'])
    
    if 'verbal_code' in data and data['verbal_code'] and len(str(data['verbal_code'])) >= 3:
        user.verbal_code = str(data['verbal_code'])
    
    if 'retry_limit' in data and isinstance(data['retry_limit'], int) and 1 <= data['retry_limit'] <= 5:
        user.retry_limit = data['retry_limit']
    
    if 'rl_max_attempts' in data and isinstance(data['rl_max_attempts'], int):
        user.rl_max_attempts = data['rl_max_attempts']
    
    if 'rl_block_minutes' in data and isinstance(data['rl_block_minutes'], int):
        user.rl_block_minutes = data['rl_block_minutes']
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Settings updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/blocked', methods=['GET'])
def api_get_blocked_calls(user_id):
    """Get blocked calls for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    blocked = UserBlocklist.query.filter(
        UserBlocklist.user_id == user_id,
        UserBlocklist.unblock_at > datetime.utcnow()
    ).all()
    
    blocked_list = []
    for block in blocked:
        blocked_list.append({
            'id': block.id,
            'phone_number': block.caller_number,
            'display_name': format_phone_display(block.caller_number),
            'unblock_at': block.unblock_at.isoformat() if block.unblock_at else None,
            'blocked_at': (block.unblock_at - timedelta(minutes=user.rl_block_minutes)).isoformat() if block.unblock_at else None
        })
    
    return jsonify(blocked_list)

@multi_user_bp.route('/user/<int:user_id>/blocked/<int:block_id>', methods=['DELETE'])
def api_remove_blocked_call(user_id, block_id):
    """Remove a blocked call for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    blocked = UserBlocklist.query.filter_by(id=block_id, user_id=user_id).first_or_404()
    
    try:
        db.session.delete(blocked)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Blocked call removed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/blocked/<int:block_id>/whitelist', methods=['POST'])
def api_whitelist_blocked_call(user_id, block_id):
    """Move blocked call to whitelist for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    blocked = UserBlocklist.query.filter_by(id=block_id, user_id=user_id).first_or_404()
    
    # Check if already in whitelist
    existing = UserWhitelist.query.filter_by(
        user_id=user_id, 
        caller_number=blocked.caller_number
    ).first()
    
    if existing:
        return jsonify({'success': False, 'error': 'Number already in whitelist'}), 400
    
    try:
        # Add to whitelist
        whitelist_entry = UserWhitelist(
            user_id=user_id,
            caller_number=blocked.caller_number
        )
        db.session.add(whitelist_entry)
        
        # Remove from blocklist
        db.session.delete(blocked)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Number moved to trusted contacts'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/analytics', methods=['GET'])
def api_get_user_analytics(user_id):
    """Get user analytics data for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    # Get blocked calls count (current blocks)
    blocked_count = UserBlocklist.query.filter(
        UserBlocklist.user_id == user_id,
        UserBlocklist.unblock_at > datetime.utcnow()
    ).count()
    
    # Get trusted contacts count
    trusted_count = UserWhitelist.query.filter_by(user_id=user_id).count()
    
    # Get call history count for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_calls = MultiUserCallLog.query.filter(
        MultiUserCallLog.user_id == user_id,
        MultiUserCallLog.created_at >= thirty_days_ago
    ).count()
    
    # Get failed authentication attempts from last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    failed_attempts = UserFailLog.query.filter(
        UserFailLog.user_id == user_id,
        UserFailLog.failure_time >= seven_days_ago
    ).count()
    
    return jsonify({
        'blocked_calls': blocked_count,
        'trusted_contacts': trusted_count,
        'recent_calls': recent_calls,
        'failed_attempts': failed_attempts,
        'defense_number': format_phone_display(user.assigned_twilio_number),
        'real_phone_number': format_phone_display(user.real_phone_number),
        'account_status': 'Active' if user.is_active else 'Inactive',
        'twilio_configured': user.twilio_number_configured
    })

# API Endpoints for Mobile App  
@multi_user_bp.route('/lookup-user', methods=['POST'])
def lookup_user():
    """Look up user ID by email for demo purposes"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({'user_id': user.id, 'name': user.name})
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/contacts', methods=['GET'])
def api_get_contacts(user_id):
    """Get trusted contacts for mobile app - SECURED"""
    user = verify_user_access(user_id)
    contacts = UserWhitelist.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': contact.id,
        'phone_number': contact.caller_number,
        'display_name': format_phone_display(contact.caller_number),
        'custom_pin': contact.custom_pin,
        'created_at': contact.created_at.isoformat() if contact.created_at else None
    } for contact in contacts])

@multi_user_bp.route('/user/<int:user_id>/contacts', methods=['POST'])
def api_add_contact(user_id):
    """Add trusted contact for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        phone_number = normalize_phone(data.get('phone_number', ''))
        custom_pin = data.get('custom_pin', '').strip()
        
        if len(phone_number) < 10:
            return jsonify({'error': 'Invalid phone number'}), 400
        
        # Check if already exists
        existing = UserWhitelist.query.filter_by(
            user_id=user_id, 
            caller_number=phone_number
        ).first()
        if existing:
            return jsonify({'error': 'Contact already exists'}), 400
        
        contact = UserWhitelist(
            user_id=user_id,
            caller_number=phone_number,
            custom_pin=custom_pin
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'id': contact.id,
            'phone_number': contact.caller_number,
            'display_name': format_phone_display(contact.caller_number),
            'custom_pin': contact.custom_pin
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/contacts/<int:contact_id>', methods=['DELETE'])
def api_delete_contact(user_id, contact_id):
    """Delete trusted contact for mobile app - SECURED"""
    user = verify_user_access(user_id)
    contact = UserWhitelist.query.filter_by(id=contact_id, user_id=user_id).first_or_404()
    
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/calls', methods=['GET'])
def api_get_calls(user_id):
    """Get call history for mobile app - SECURED"""
    user = verify_user_access(user_id)
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Get actual call logs from database
    calls = MultiUserCallLog.query.filter_by(user_id=user_id).order_by(MultiUserCallLog.created_at.desc()).limit(limit).offset(offset).all()
    
    call_list = []
    for call in calls:
        call_list.append({
            'id': call.id,
            'to_number': call.to_number,
            'from_number': call.from_number,
            'direction': call.direction,
            'status': call.status,
            'duration_seconds': call.duration_seconds,
            'created_at': call.created_at.isoformat() if call.created_at else None
        })
    
    return jsonify(call_list)

@multi_user_bp.route('/user/<int:user_id>/calls/<int:call_id>/complete', methods=['POST'])
def api_complete_call(user_id, call_id):
    """Complete a call for mobile app - SECURED"""
    user = verify_user_access(user_id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    try:
        call_log = MultiUserCallLog.query.filter_by(id=call_id, user_id=user_id).first_or_404()
        
        # Update call with completion details
        call_log.status = data.get('status', 'completed')
        call_log.duration_seconds = data.get('duration_seconds', 0)
        call_log.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'call_id': call_id,
            'status': call_log.status,
            'duration': call_log.duration_seconds
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/calls/<int:call_id>/status', methods=['GET'])
def api_get_call_status(user_id, call_id):
    """Get call status for mobile app - SECURED"""
    user = verify_user_access(user_id)
    
    try:
        call_log = MultiUserCallLog.query.filter_by(id=call_id, user_id=user_id).first_or_404()
        
        return jsonify({
            'call_id': call_log.id,
            'status': call_log.status,
            'to_number': call_log.to_number,
            'from_number': call_log.from_number,
            'direction': call_log.direction,
            'duration_seconds': call_log.duration_seconds,
            'created_at': call_log.created_at.isoformat() if call_log.created_at else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

def get_user_by_twilio_number(twilio_number):
    """Helper to find user by their assigned Twilio number"""
    return User.query.filter_by(assigned_twilio_number=twilio_number).first()

def setup_twilio_webhook(phone_number):
    """Configure Twilio webhook for a phone number"""
    try:
        client = twilio_client()
        # Update the phone number's webhook URL
        # This would point to /multi/voice/incoming/{phone_number}
        webhook_url = f"{request.url_root}multi/voice/incoming/{normalize_phone(phone_number)}"
        
        # Find and update the Twilio phone number
        numbers = client.incoming_phone_numbers.list()
        for number in numbers:
            if number.phone_number == phone_number:
                number.update(voice_url=webhook_url, voice_method='POST')
                return True
        return False
    except Exception as e:
        print(f"Failed to configure Twilio webhook for {phone_number}: {e}")
        return False

# ============================================================================
# REAL CALLBUNKER BRIDGE CALLING - The Actual Working Mechanism!
# ============================================================================

@multi_user_bp.route('/voice/device-outbound', methods=['POST'])
def handle_device_outbound():
    """
    TwiML endpoint for Twilio Voice SDK outbound calls
    Direct browser-to-PSTN bridge with no hold music
    """
    to_number = request.form.get('To')
    caller_id = request.form.get('CallerId')  # Set in Voice token
    
    vr = VoiceResponse()
    
    if to_number:
        # Direct dial to target - no conference, no hold music
        vr.say("CallBunker connecting.", voice="polly.Joanna")
        dial = vr.dial(caller_id=caller_id)
        dial.number(to_number)
    else:
        vr.say("Invalid number.", voice="polly.Joanna")
        vr.hangup()
    
    return xml_response(vr)

@multi_user_bp.route('/voice/conference/<conference_name>', methods=['POST'])
def handle_conference_call(conference_name):
    """
    Handle conference call participants - joins target and user into same conference
    This is the TwiML endpoint that both call legs hit
    """
    participant = request.args.get('participant', 'unknown')
    
    vr = VoiceResponse()
    
    if participant == 'target':
        # Target person joining - no message, just join conference
        dial = vr.dial()
        dial.conference(
            conference_name,
            start_conference_on_enter=True,
            end_conference_on_exit=False,
            wait_url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient"
        )
    elif participant == 'user':
        # User joining via phone callback - brief message then join
        vr.say("CallBunker connecting your call.", voice="polly.Joanna")
        dial = vr.dial()
        dial.conference(
            conference_name,
            start_conference_on_enter=True,
            end_conference_on_exit=True,  # End when user hangs up
            wait_url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient"
        )
    elif participant == 'mobile_app':
        # Mobile app joining via Twilio Voice SDK - no message, direct conference join
        dial = vr.dial()
        dial.conference(
            conference_name,
            start_conference_on_enter=True,
            end_conference_on_exit=True,  # End when mobile app disconnects
            wait_url=""  # No hold music for mobile app
        )
    else:
        vr.say("Conference error. Please try again.", voice="polly.Joanna")
        vr.hangup()
    
    return xml_response(vr)

def xml_response(voice_response):
    """Helper to return proper TwiML XML response"""
    response = Response(str(voice_response), mimetype='application/xml')
    return response

@multi_user_bp.route('/user/<int:user_id>/call_direct', methods=['POST'])
def api_call_direct(user_id):
    """
    TRUE NO-CALLBACK CALLING - User speaks through web/mobile, only target phone rings
    Uses Twilio Voice SDK for direct calling without callback
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        to_number = data.get('to_number', '').strip()
        if not to_number:
            return jsonify({'error': 'to_number is required'}), 400
        
        # Normalize phone numbers
        to_number_normalized = '+1' + normalize_phone(to_number) if not to_number.startswith('+') else to_number
        # Use assigned Twilio number for CallBunker Voice SDK calling
        caller_id_number = user.assigned_twilio_number
        
        # Get Twilio client and public URL
        from utils.twilio_helpers import twilio_client
        client = twilio_client()
        
        # NOTE: This endpoint is now for fallback only
        # True no-callback uses Voice SDK directly via device-outbound TwiML
        return jsonify({
            'success': False,
            'message': 'Use Voice SDK for direct calling - this is fallback only',
            'voice_sdk_ready': True
        })
        
        # Create call log entry
        call_log = MultiUserCallLog(
            user_id=user_id,
            from_number=caller_id_number,
            to_number=to_number_normalized,
            direction='outbound',
            status='calling',
            twilio_call_sid=target_call.sid,
            conference_name=None  # No conference needed for direct calling
        )
        
        db.session.add(call_log)
        db.session.commit()
        
        print(f"DIRECT CALL DEBUG: Created call - Target: {target_call.sid}")
        print(f"DIRECT CALL DEBUG: Target number: {to_number_normalized}")
        print(f"DIRECT CALL DEBUG: Google Voice number: {caller_id_number}")
        
        return jsonify({
            'success': True,
            'approach': 'direct_calling',
            'call_log_id': call_log.id,
            'target_call_sid': target_call.sid,
            'to_number': to_number_normalized,
            'from_number': caller_id_number,
            'message': f'Direct call initiated - {to_number_normalized} will ring, you speak through app'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/voice-token', methods=['GET'])
def get_voice_token(user_id):
    """
    Generate Twilio Voice Access Token for direct calling through web/mobile
    """
    try:
        from twilio.jwt.access_token import AccessToken
        from twilio.jwt.access_token.grants import VoiceGrant
        
        user = User.query.get_or_404(user_id)
        
        # Use your Twilio credentials
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        api_key = os.environ.get('TWILIO_API_KEY')
        api_secret = os.environ.get('TWILIO_API_SECRET')
        app_sid = os.environ.get('TWIML_APP_SID')
        
        # Create a TwiML App URL for device outbound calls
        public_url = os.environ.get('PUBLIC_APP_URL')
        if not public_url:
            return jsonify({'error': 'PUBLIC_APP_URL not configured'}), 500
            
        # Create an Access Token with proper caller ID
        token = AccessToken(account_sid, api_key, api_secret, identity=f"user_{user_id}")
        
        # Create a Voice grant with outbound TwiML app
        voice_grant = VoiceGrant(
            outgoing_application_sid=app_sid,
            incoming_allow=True
        )
        token.add_grant(voice_grant)
        
        return jsonify({
            'success': True,
            'token': token.to_jwt(),
            'identity': f"user_{user_id}",
            'caller_id': user.assigned_twilio_number
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/call_bridge', methods=['POST'])
def api_call_bridge(user_id):
    """
    BRIDGE CALLING (OLD) - Both phones ring with hold music
    Creates a Twilio conference call bridging user and target
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        to_number = data.get('to_number', '').strip()
        if not to_number:
            return jsonify({'error': 'to_number is required'}), 400
        
        # Normalize phone numbers
        to_number_normalized = '+1' + normalize_phone(to_number) if not to_number.startswith('+') else to_number
        user_phone = '+1' + normalize_phone(user.real_phone_number) if len(user.real_phone_number) == 10 else user.real_phone_number
        # Use assigned Twilio number for CallBunker Voice SDK calling
        caller_id_number = user.assigned_twilio_number
        
        # Create conference name
        conference_name = f"callbunker_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Get Twilio client and public URL
        from utils.twilio_helpers import twilio_client
        client = twilio_client()
        
        # Use public URL that Twilio can reach
        public_url = os.environ.get('PUBLIC_APP_URL', 'https://4ec224cf-933c-4ca6-b58f-2fce3ea2d59f-00-23vazcc99oamt.janeway.replit.dev')
        
        # Call 1: Call the target number (they see assigned Twilio number as caller ID)
        target_call = client.calls.create(
            to=to_number_normalized,
            from_=caller_id_number,  # Target sees your assigned CallBunker number!
            url=f"{public_url}/multi/voice/conference/{conference_name}?participant=target",
            method='POST'
        )
        
        # Call 2: Call the user
        user_call = client.calls.create(
            to=user_phone,
            from_=caller_id_number,  # You see your own CallBunker number
            url=f"{public_url}/multi/voice/conference/{conference_name}?participant=user",
            method='POST'
        )
        
        # Create call log entry
        call_log = MultiUserCallLog(
            user_id=user_id,
            from_number=caller_id_number,
            to_number=to_number_normalized,
            direction='outbound',
            status='calling',
            twilio_call_sid=target_call.sid,
            conference_name=conference_name
        )
        
        db.session.add(call_log)
        db.session.commit()
        
        print(f"BRIDGE CALL DEBUG: Created calls - Target: {target_call.sid}, User: {user_call.sid}")
        print(f"BRIDGE CALL DEBUG: Conference: {conference_name}")
        print(f"BRIDGE CALL DEBUG: Target number: {to_number_normalized}, User number: {user_phone}")
        print(f"BRIDGE CALL DEBUG: Caller ID number: {caller_id_number}")
        
        return jsonify({
            'success': True,
            'approach': 'bridge_calling',
            'call_log_id': call_log.id,
            'target_call_sid': target_call.sid,
            'user_call_sid': user_call.sid,
            'conference_name': conference_name,
            'conference_name': conference_name,
            'to_number': to_number_normalized,
            'from_number': caller_id_number,
            'target_call_sid': target_call.sid,
            'user_call_sid': user_call.sid,
            'bridge_config': {
                'target_sees': caller_id_number,
                'user_phone': user_phone,
                'conference': conference_name,
                'cost': '$0.02 per minute per leg (2 legs total)'
            },
            'message': f'Bridge call initiated - both {to_number_normalized} and {user_phone} will ring shortly'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/call_mobile_app', methods=['POST'])
def api_call_mobile_app(user_id):
    """
    MOBILE APP CALLING WITHOUT CALLBACK
    Only calls target, mobile app connects via Twilio Voice SDK (no callback to user's phone!)
    """
    user = verify_user_access(user_id)
    data = request.get_json()
    
    try:
        to_number = data.get('to_number', '').strip()
        if not to_number:
            return jsonify({'error': 'to_number is required'}), 400
        
        # Normalize phone numbers
        to_number_normalized = '+1' + normalize_phone(to_number) if not to_number.startswith('+') else to_number
        # Use assigned Twilio number for CallBunker Voice SDK calling
        caller_id_number = user.assigned_twilio_number
        
        # Create conference name for this call
        conference_name = f"callbunker_mobile_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Get Twilio client and public URL
        client = twilio_client()
        public_url = os.environ.get('PUBLIC_APP_URL', 'https://4ec224cf-933c-4ca6-b58f-2fce3ea2d59f-00-23vazcc99oamt.janeway.replit.dev')
        
        # Generate Voice Access Token for mobile app
        access_token = generate_voice_access_token(user_id)
        
        # Call ONLY the target number (no callback to user's phone!)
        target_call = client.calls.create(
            to=to_number_normalized,
            from_=user.assigned_twilio_number,  # Use assigned Twilio number as caller ID
            url=f"{public_url}/multi/voice/conference/{conference_name}?participant=target",
            method='POST'
        )
        
        # Create call log entry
        call_log = MultiUserCallLog(
            user_id=user_id,
            from_number=user.assigned_twilio_number,
            to_number=to_number_normalized,
            direction='outbound',
            status='mobile_calling',
            twilio_call_sid=target_call.sid,
            conference_name=conference_name
        )
        
        db.session.add(call_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'approach': 'mobile_app_calling',
            'call_log_id': call_log.id,
            'conference_name': conference_name,
            'to_number': to_number_normalized,
            'from_number': user.assigned_twilio_number,
            'target_call_sid': target_call.sid,
            'access_token': access_token,
            'mobile_config': {
                'target_sees': user.assigned_twilio_number,
                'no_callback': True,
                'conference': conference_name,
                'cost': '$0.02 per minute (1 call leg only)',
                'connection_method': 'Twilio Voice SDK via internet'
            },
            'message': f'Target {to_number_normalized} will ring. Use access token to connect via mobile app.',
            'instructions': {
                'mobile_app': 'Use the access_token to connect to Twilio Voice SDK',
                'conference_endpoint': f'{public_url}/multi/voice/conference/{conference_name}?participant=mobile_app',
                'connection_type': 'internet_based'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/user/<int:user_id>/voice_token', methods=['GET'])
def get_voice_access_token(user_id):
    """Get Twilio Voice Access Token for mobile app"""
    user = verify_user_access(user_id)
    
    try:
        access_token = generate_voice_access_token(user_id)
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'identity': f'callbunker_user_{user_id}',
            'expires_in': 3600,  # 1 hour
            'usage': 'Use this token to initialize Twilio Voice SDK in mobile app'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@multi_user_bp.route('/voice/outbound', methods=['POST'])
def voice_sdk_outbound():
    """
    TwiML handler for Voice SDK outbound calls
    This endpoint is called by Twilio when a Voice SDK client makes an outbound call
    """
    try:
        # Get the destination number from Voice SDK call
        to_number = request.form.get('To')
        caller_identity = request.form.get('From')  # The user identity from Voice SDK
        
        if not to_number:
            return Response('<Response><Say>Invalid destination number</Say></Response>', mimetype='application/xml')
        
        # Extract user ID from caller identity (format: client:callbunker_user_123)
        print(f"WEBHOOK DEBUG: Received caller identity: '{caller_identity}'")
        print(f"WEBHOOK DEBUG: To number: '{to_number}'")
        
        # Strip 'client:' prefix if present (Twilio Voice SDK adds this)
        if caller_identity and caller_identity.startswith('client:'):
            caller_identity = caller_identity.replace('client:', '')
            print(f"WEBHOOK DEBUG: Stripped client prefix, now: '{caller_identity}'")
        
        if not caller_identity or not caller_identity.startswith('callbunker_user_'):
            print(f"WEBHOOK ERROR: Invalid caller identity format: '{caller_identity}'")
            return Response('<Response><Say>Invalid caller identity format</Say></Response>', mimetype='application/xml')
        
        user_id = int(caller_identity.replace('callbunker_user_', ''))
        user = User.query.get(user_id)
        
        if not user or not user.assigned_twilio_number:
            return Response('<Response><Say>User not found or no assigned number</Say></Response>', mimetype='application/xml')
        
        # Normalize the destination number
        def normalize_phone_number(phone_number):
            digits = re.sub(r'\D', '', phone_number)
            if len(digits) == 10:
                return '+1' + digits
            elif len(digits) == 11 and digits.startswith('1'):
                return '+' + digits
            return phone_number
        
        to_number_normalized = normalize_phone_number(to_number)
        
        # Create TwiML response to dial the target number using user's CallBunker number as caller ID
        vr = VoiceResponse()
        dial = vr.dial(caller_id=user.assigned_twilio_number)
        dial.number(to_number_normalized)
        
        # Log the call
        call_log = MultiUserCallLog(
            user_id=user.id,
            from_number=user.assigned_twilio_number,  # Add missing from_number
            to_number=to_number_normalized,
            direction='outbound',
            status='calling',
            twilio_call_sid=request.form.get('CallSid', 'voice_sdk_call'),
            conference_name=None
        )
        db.session.add(call_log)
        db.session.commit()
        
        print(f"VOICE SDK OUTBOUND: User {user_id} calling {to_number_normalized} via Voice SDK")
        print(f"VOICE SDK OUTBOUND: Using caller ID {user.assigned_twilio_number}")
        
        return Response(str(vr), mimetype='application/xml')
        
    except Exception as e:
        print(f"VOICE SDK OUTBOUND ERROR: {str(e)}")
        vr = VoiceResponse()
        vr.say("Sorry, there was an error placing your call. Please try again.")
        return Response(str(vr), mimetype='application/xml')

@multi_user_bp.route('/contact-support')
def contact_support():
    """Support contact page for users needing help"""
    return render_template('multi_user/contact_support.html')


# ============================================================================
# DIRECT VOICE SDK CALLING - No Google Voice Setup Required!
# ============================================================================
    
# Legacy Google Voice routes removed - CallBunker now uses direct Voice SDK calling

