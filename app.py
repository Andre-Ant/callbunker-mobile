import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Production session configuration
# Fix for deployed environments where sessions don't work
is_production = os.environ.get("REPLIT_DEPLOYMENT") is not None
app.config.update(
    SESSION_COOKIE_SECURE=is_production,     # HTTPS only in production
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
                    pool_entry = TwilioPhonePool(
                        phone_number=number.phone_number,
                        monthly_cost=1.00,
                        is_assigned=False
                    )
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

app.register_blueprint(voice_bp, url_prefix='/voice')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(main_bp)
app.register_blueprint(multi_user_bp, url_prefix='/multi')
app.register_blueprint(multi_user_voice_bp, url_prefix='/multi/voice')
app.register_blueprint(demo_bp)
app.register_blueprint(tutorial_bp, url_prefix='/tutorial')
app.register_blueprint(dialer_bp)
app.register_blueprint(demo_api_bp)

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
