import os
import logging
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, get_locale
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure supported languages
app.config['LANGUAGES'] = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',
    'ru': 'Русский',
    'ja': '日本語',
    'ko': '한국어',
    'zh': '中文'
}

def get_locale():
    """Select the best language based on user preference, session, or browser"""
    # 1. Check session for manually selected language (takes priority)
    if 'language' in session:
        return session['language']
    
    # 2. Check if user is logged in and has a preferred language
    if 'user_id' in session:
        try:
            from models_multi_user import User
            user = User.query.get(session['user_id'])
            if user and user.preferred_language:
                return user.preferred_language
        except:
            pass
    
    # 3. Use browser's preferred language if supported
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'en'

# Configure Flask-Babel for internationalization with the locale selector
babel = Babel(app, locale_selector=get_locale)

# Enable template auto-reload for development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

@app.context_processor
def inject_conf_vars():
    """Make Flask-Babel functions available in templates"""
    from flask_babel import gettext, ngettext
    return dict(
        _=gettext,
        ngettext=ngettext,
        get_locale=get_locale
    )

# Production session configuration
# Fix for deployed environments where sessions don't work
is_production = os.environ.get("REPLIT_DEPLOYMENT") is not None

# Check if SESSION_SECRET is properly set
if not os.environ.get("SESSION_SECRET"):
    print("WARNING: SESSION_SECRET not set! Sessions will not persist.")
    if not is_production:
        app.secret_key = "dev-secret-change-me"
        print("Using development fallback secret key")

app.config.update(
    SESSION_COOKIE_SECURE=False,            # Allow HTTP in development 
    SESSION_COOKIE_HTTPONLY=True,           # No JS access to cookies
    SESSION_COOKIE_SAMESITE='Lax',          # CSRF protection
    PERMANENT_SESSION_LIFETIME=7200,        # 2 hours
)

# Configure the database
database_url = os.environ.get("DATABASE_URL", "sqlite:///callbunker.db")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    import models_multi_user
    db.create_all()
    
    # Auto-seed phone pool from Twilio if empty (for production deployment)
    def ensure_phone_pool_seeded():
        """Automatically populate phone pool from Twilio API if database is empty"""
        try:
            from models_multi_user import TwilioPhonePool
            
            # Check if phone pool is empty
            if TwilioPhonePool.query.count() == 0:
                print("Phone pool is empty, seeding from Twilio API...")
                
                from utils.twilio_helpers import twilio_client
                client = twilio_client()
                
                # Get all incoming phone numbers from Twilio
                numbers = client.incoming_phone_numbers.list()
                
                added_count = 0
                for number in numbers:
                    # Add each number to pool
                    pool_entry = TwilioPhonePool()
                    pool_entry.phone_number = number.phone_number
                    pool_entry.monthly_cost = 1.00
                    pool_entry.is_assigned = False
                    db.session.add(pool_entry)
                    added_count += 1
                
                db.session.commit()
                print(f"Auto-seeded {added_count} phone numbers from Twilio API")
                return added_count
            else:
                existing_count = TwilioPhonePool.query.count()
                print(f"Phone pool already has {existing_count} numbers, skipping seed")
                return 0
                
        except Exception as e:
            print(f"Phone pool seeding failed: {e}")
            # Don't crash app startup on seeding failure
            return 0
    
    # Seed phone pool if empty
    ensure_phone_pool_seeded()

# Register blueprints
from routes.voice import voice_bp
from routes.admin import admin_bp
from routes.main import main_bp
from routes.multi_user import multi_user_bp
from routes.multi_user_voice import multi_user_voice_bp
from routes.demo import demo_bp
from routes.tutorial import tutorial_bp
from routes.dialer import dialer_bp
from routes.demo_api import demo_api_bp
from routes.call_quality import call_quality_bp

app.register_blueprint(voice_bp, url_prefix='/voice')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(main_bp)
app.register_blueprint(multi_user_bp, url_prefix='/multi')
app.register_blueprint(multi_user_voice_bp, url_prefix='/multi/voice')
app.register_blueprint(demo_bp)
app.register_blueprint(tutorial_bp, url_prefix='/tutorial')
app.register_blueprint(dialer_bp)
app.register_blueprint(demo_api_bp)
app.register_blueprint(call_quality_bp, url_prefix='/quality')

# Simple test route to verify deployment is working
@app.route('/working')
def working_test():
    return """
    <html>
    <head><title>CallBunker - Deployment Test</title></head>
    <body style="font-family: Arial; padding: 30px; background: #f0f0f0;">
        <div style="background: white; padding: 30px; border-radius: 10px;">
            <h1 style="color: green;">✅ Deployment is Working!</h1>
            <p><strong>This confirms the app is deployed correctly.</strong></p>
            <hr>
            <h3>Available Routes:</h3>
            <ul>
                <li><a href="/multi/login">Multi Login</a></li>
                <li><a href="/multi/test">Multi Test</a></li>
                <li><a href="/multi/debug-auth">Debug Auth</a></li>
                <li><a href="/multi/">Multi Home</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
