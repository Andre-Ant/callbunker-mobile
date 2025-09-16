#!/usr/bin/env python3
"""
Database Migration: Create Call Quality Monitoring Tables
Run this script to create the new tables for call quality monitoring
"""
import os
import sys
from app import app, db

def create_quality_tables():
    """Create the new quality monitoring tables"""
    print("Creating call quality monitoring tables...")
    
    with app.app_context():
        try:
            # Import the new models to ensure they're registered
            from models_multi_user import CallQualityMetrics, QualityAlert
            
            # Create all tables (this will only create new ones)
            db.create_all()
            
            print("✅ Call quality monitoring tables created successfully!")
            print("   - call_quality_metrics")
            print("   - quality_alerts")
            print("")
            print("The following features are now available:")
            print("   🔍 Real-time call quality monitoring")
            print("   📊 Quality metrics tracking (MOS, latency, jitter)")
            print("   🚨 Automated quality alerts")
            print("   📈 Quality analytics dashboard")
            print("")
            print("Dashboard URL: /quality/dashboard")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = create_quality_tables()
    sys.exit(0 if success else 1)