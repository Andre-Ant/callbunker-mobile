"""
CallBunker Phone Number Provisioning System
Hybrid model: Pool-based with automatic threshold replenishment
"""
import os
from twilio.rest import Client
from models_multi_user import TwilioPhonePool
from app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Configuration
POOL_THRESHOLD_LOW = 10  # Alert when pool drops below this
POOL_THRESHOLD_CRITICAL = 5  # Emergency replenishment
REPLENISHMENT_BATCH_SIZE = 20  # How many to buy when replenishing

class PhoneProvisioning:
    """Manages phone number pool and automatic provisioning"""
    
    def __init__(self):
        self.twilio_client = Client(
            os.environ.get('TWILIO_ACCOUNT_SID'),
            os.environ.get('TWILIO_AUTH_TOKEN')
        )
        self.public_url = os.environ.get('PUBLIC_APP_URL')
    
    def get_pool_status(self):
        """Get current pool statistics"""
        total = TwilioPhonePool.query.count()
        available = TwilioPhonePool.query.filter_by(is_assigned=False).count()
        assigned = TwilioPhonePool.query.filter_by(is_assigned=True).count()
        
        status = 'healthy'
        if available <= POOL_THRESHOLD_CRITICAL:
            status = 'critical'
        elif available <= POOL_THRESHOLD_LOW:
            status = 'low'
        
        return {
            'total': total,
            'available': available,
            'assigned': assigned,
            'status': status,
            'threshold_low': POOL_THRESHOLD_LOW,
            'threshold_critical': POOL_THRESHOLD_CRITICAL
        }
    
    def purchase_phone_number(self, area_code=None, country_code='US'):
        """
        Purchase a single phone number from Twilio
        
        Args:
            area_code: Preferred area code (e.g., '631')
            country_code: Country code (default 'US')
        
        Returns:
            TwilioPhonePool object or None if failed
        """
        try:
            logger.info(f"Purchasing phone number (area_code={area_code}, country={country_code})")
            
            # Search for available number
            search_params = {
                'country_code': country_code,
            }
            
            if area_code:
                search_params['area_code'] = area_code
            
            search_params['limit'] = 1
            available_numbers = self.twilio_client.available_phone_numbers(country_code).local.list(**search_params)
            
            if not available_numbers:
                logger.error(f"No available numbers found for area code {area_code}")
                return None
            
            phone_number = available_numbers[0].phone_number
            
            # Purchase the number
            purchased = self.twilio_client.incoming_phone_numbers.create(
                phone_number=phone_number,
                voice_url=f"{self.public_url}/voice/incoming",
                voice_method='POST',
                status_callback=f"{self.public_url}/voice/status",
                status_callback_method='POST'
            )
            
            logger.info(f"Purchased number: {purchased.phone_number}")
            
            # Add to pool
            pool_entry = TwilioPhonePool()
            pool_entry.phone_number = purchased.phone_number
            pool_entry.is_assigned = False
            pool_entry.monthly_cost = 1.00
            pool_entry.webhook_configured = True
            pool_entry.created_at = datetime.utcnow()
            
            db.session.add(pool_entry)
            db.session.commit()
            
            logger.info(f"Added {purchased.phone_number} to pool")
            return pool_entry
            
        except Exception as e:
            logger.error(f"Failed to purchase phone number: {e}")
            db.session.rollback()
            return None
    
    def purchase_batch(self, count=REPLENISHMENT_BATCH_SIZE, area_code=None):
        """
        Purchase multiple phone numbers in batch
        
        Args:
            count: Number of phones to purchase
            area_code: Preferred area code
        
        Returns:
            List of purchased phone numbers
        """
        purchased = []
        failed = 0
        
        logger.info(f"Starting batch purchase of {count} numbers")
        
        for i in range(count):
            number = self.purchase_phone_number(area_code=area_code)
            if number:
                purchased.append(number)
            else:
                failed += 1
                logger.warning(f"Failed to purchase number {i+1}/{count}")
        
        logger.info(f"Batch purchase complete: {len(purchased)} purchased, {failed} failed")
        return purchased
    
    def check_and_replenish(self):
        """
        Check pool status and replenish if below threshold
        Uses database advisory lock to prevent concurrent replenishment
        
        Returns:
            Dict with replenishment results
        """
        # Use PostgreSQL advisory lock to prevent concurrent replenishment
        # Lock ID: 12345 (arbitrary but consistent)
        lock_acquired = False
        
        try:
            # Try to acquire advisory lock (non-blocking)
            result = db.session.execute(db.text("SELECT pg_try_advisory_lock(12345) AS acquired"))
            lock_acquired = result.fetchone()[0]
            
            if not lock_acquired:
                logger.info("Replenishment already in progress (lock held by another process)")
                return {
                    'replenished': False,
                    'reason': 'concurrent_replenishment_in_progress',
                    'status': self.get_pool_status()
                }
            
            # Check status within lock
            status = self.get_pool_status()
            
            if status['available'] > POOL_THRESHOLD_LOW:
                logger.info(f"Pool healthy: {status['available']} available")
                return {
                    'replenished': False,
                    'reason': 'pool_healthy',
                    'status': status
                }
            
            # Calculate how many to purchase
            target_count = POOL_THRESHOLD_LOW + REPLENISHMENT_BATCH_SIZE
            needed = target_count - status['available']
            
            logger.warning(f"Pool below threshold ({status['available']} < {POOL_THRESHOLD_LOW}). Replenishing {needed} numbers...")
            
            purchased = self.purchase_batch(count=needed)
            
            new_status = self.get_pool_status()
            
            return {
                'replenished': True,
                'purchased_count': len(purchased),
                'previous_status': status,
                'new_status': new_status,
                'purchased_numbers': [p.phone_number for p in purchased]
            }
            
        finally:
            # Always release lock if acquired
            if lock_acquired:
                db.session.execute(db.text("SELECT pg_advisory_unlock(12345)"))
                logger.debug("Released replenishment advisory lock")
    
    def configure_webhook(self, phone_number):
        """
        Configure webhook for a specific phone number
        
        Args:
            phone_number: Phone number to configure (E.164 format)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the Twilio number
            numbers = self.twilio_client.incoming_phone_numbers.list(phone_number=phone_number)
            
            if not numbers:
                logger.error(f"Number {phone_number} not found in Twilio account")
                return False
            
            twilio_number = numbers[0]
            
            # Update webhook configuration
            twilio_number.update(
                voice_url=f"{self.public_url}/voice/incoming",
                voice_method='POST',
                status_callback=f"{self.public_url}/voice/status",
                status_callback_method='POST'
            )
            
            # Update pool entry
            pool_entry = TwilioPhonePool.query.filter_by(phone_number=phone_number).first()
            if pool_entry:
                pool_entry.webhook_configured = True
                db.session.commit()
            
            logger.info(f"Configured webhook for {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure webhook for {phone_number}: {e}")
            return False
    
    def configure_all_webhooks(self):
        """Configure webhooks for all pool numbers"""
        pool_numbers = TwilioPhonePool.query.filter_by(webhook_configured=False).all()
        
        configured = 0
        for number in pool_numbers:
            if self.configure_webhook(number.phone_number):
                configured += 1
        
        return {
            'total': len(pool_numbers),
            'configured': configured,
            'failed': len(pool_numbers) - configured
        }

# Global instance
phone_provisioning = PhoneProvisioning()
