from datetime import datetime, timedelta
from typing import Optional
from app import db
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

class Tenant(db.Model):
    __tablename__ = 'tenant'
    
    screening_number = db.Column(db.String(20), primary_key=True)  # User's real number (E.164)
    owner_label = db.Column(db.String(100), nullable=True)
    forward_to = db.Column(db.String(20), nullable=False)  # Same as screening_number for forwarding model
    current_pin = db.Column(db.String(4), default="1122", nullable=False)
    verbal_code = db.Column(db.String(50), default="open sesame", nullable=False)
    retry_limit = db.Column(db.Integer, default=3, nullable=False)
    forward_mode = db.Column(db.String(20), default="bridge", nullable=False)  # "bridge" | "voicemail"
    rl_window_sec = db.Column(db.Integer, default=3600, nullable=False)
    rl_max_attempts = db.Column(db.Integer, default=5, nullable=False)
    rl_block_minutes = db.Column(db.Integer, default=60, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Test-call verification markers
    test_verified_at = db.Column(db.DateTime, nullable=True, index=True)
    last_test_call_sid = db.Column(db.String(50), nullable=True, index=True)
    last_test_result = db.Column(db.String(20), nullable=True)  # "confirmed"|"failed"|"no_input"
    
    # Relationships
    whitelists = relationship("Whitelist", back_populates="tenant", cascade="all, delete-orphan")
    fail_logs = relationship("FailLog", back_populates="tenant", cascade="all, delete-orphan")
    blocklists = relationship("Blocklist", back_populates="tenant", cascade="all, delete-orphan")

class Whitelist(db.Model):
    __tablename__ = 'whitelist'
    
    id = db.Column(db.Integer, primary_key=True)
    screening_number = db.Column(db.String(20), ForeignKey('tenant.screening_number'), nullable=False, index=True)
    number = db.Column(db.String(20), nullable=False, index=True)  # caller digits/e164-ish
    pin = db.Column(db.String(4), nullable=True)
    verbal = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="whitelists")

class FailLog(db.Model):
    __tablename__ = 'faillog'
    
    id = db.Column(db.Integer, primary_key=True)
    screening_number = db.Column(db.String(20), ForeignKey('tenant.screening_number'), nullable=False, index=True)
    caller_digits = db.Column(db.String(20), nullable=False, index=True)
    ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="fail_logs")

class Blocklist(db.Model):
    __tablename__ = 'blocklist'
    
    id = db.Column(db.Integer, primary_key=True)
    screening_number = db.Column(db.String(20), ForeignKey('tenant.screening_number'), nullable=False, index=True)
    caller_digits = db.Column(db.String(20), nullable=False, index=True)
    unblock_at = db.Column(db.DateTime, nullable=False, index=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="blocklists")
