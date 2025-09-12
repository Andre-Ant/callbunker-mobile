"""
CallBunker Business Models - Each user gets their own Twilio number
"""
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app import db

class User(db.Model):
    """Individual users who sign up for CallBunker service"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    real_phone_number = db.Column(db.String(20), nullable=False)  # Where calls should be forwarded
    assigned_twilio_number = db.Column(db.String(20), nullable=False, unique=True, index=True)  # Their CallBunker number
    
    # Authentication settings
    pin = db.Column(db.String(4), default="1122", nullable=False)
    verbal_code = db.Column(db.String(50), default="open sesame", nullable=False)
    password_hash = db.Column(db.String(256))  # For web login
    
    # Call screening settings
    retry_limit = db.Column(db.Integer, default=3, nullable=False)
    forward_mode = db.Column(db.String(20), default="bridge", nullable=False)
    
    # Rate limiting settings
    rl_window_sec = db.Column(db.Integer, default=3600, nullable=False)
    rl_max_attempts = db.Column(db.Integer, default=5, nullable=False)
    rl_block_minutes = db.Column(db.Integer, default=60, nullable=False)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    twilio_number_configured = db.Column(db.Boolean, default=False, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    whitelists = relationship("UserWhitelist", back_populates="user", cascade="all, delete-orphan")
    fail_logs = relationship("UserFailLog", back_populates="user", cascade="all, delete-orphan")
    blocklists = relationship("UserBlocklist", back_populates="user", cascade="all, delete-orphan")

class TwilioPhonePool(db.Model):
    """Pool of available Twilio phone numbers for assignment"""
    __tablename__ = 'twilio_phone_pool'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    is_assigned = db.Column(db.Boolean, default=False, nullable=False)
    assigned_to_user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=True)
    monthly_cost = db.Column(db.Numeric(5,2), default=1.00, nullable=False)  # $1/month per Twilio number
    
    # Webhook configuration
    webhook_configured = db.Column(db.Boolean, default=False, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    assigned_user = relationship("User", foreign_keys=[assigned_to_user_id])

class MultiUserCallLog(db.Model):
    """Call logs for multi-user system"""
    __tablename__ = 'multi_user_call_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False, index=True)
    from_number = db.Column(db.String(20), nullable=False)
    to_number = db.Column(db.String(20), nullable=False)
    direction = db.Column(db.String(10), nullable=False)  # 'inbound' or 'outbound'
    status = db.Column(db.String(20), nullable=False)
    twilio_call_sid = db.Column(db.String(50), nullable=True)
    conference_name = db.Column(db.String(100), nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])

class UserWhitelist(db.Model):
    """Per-user whitelisted numbers"""
    __tablename__ = 'user_whitelist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False, index=True)
    caller_number = db.Column(db.String(20), nullable=False, index=True)
    custom_pin = db.Column(db.String(4), nullable=True)
    allows_verbal = db.Column(db.Boolean, default=False, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="whitelists")

class UserFailLog(db.Model):
    """Per-user authentication failure tracking"""
    __tablename__ = 'user_fail_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False, index=True)
    caller_number = db.Column(db.String(20), nullable=False, index=True)
    failure_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="fail_logs")

class UserBlocklist(db.Model):
    """Per-user temporarily blocked numbers"""
    __tablename__ = 'user_blocklist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False, index=True)
    caller_number = db.Column(db.String(20), nullable=False, index=True)
    unblock_at = db.Column(db.DateTime, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="blocklists")