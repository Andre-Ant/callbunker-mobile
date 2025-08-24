from datetime import datetime, timedelta
from typing import Optional
from app import db
from models import Tenant, FailLog, Blocklist

def is_blocked(tenant: Tenant, caller_digits: str) -> Optional[int]:
    """
    Check if caller is currently blocked for this tenant.
    Returns remaining block time in seconds, or None if not blocked.
    """
    blocked_entry = Blocklist.query.filter_by(
        screening_number=tenant.screening_number,
        caller_digits=caller_digits
    ).first()
    
    if not blocked_entry:
        return None
    
    remaining_seconds = int((blocked_entry.unblock_at - datetime.utcnow()).total_seconds())
    
    if remaining_seconds <= 0:
        # Block has expired, remove it
        db.session.delete(blocked_entry)
        db.session.commit()
        return None
    
    return remaining_seconds

def note_failure_and_maybe_block(tenant: Tenant, caller_digits: str):
    """
    Record a failure and potentially block the caller if they've exceeded limits.
    """
    cutoff = datetime.utcnow() - timedelta(seconds=tenant.rl_window_sec)
    
    # Count recent failures
    recent_count = FailLog.query.filter(
        FailLog.screening_number == tenant.screening_number,
        FailLog.caller_digits == caller_digits,
        FailLog.ts >= cutoff
    ).count()
    
    # Add this failure
    fail_log = FailLog(
        screening_number=tenant.screening_number,
        caller_digits=caller_digits
    )
    db.session.add(fail_log)
    recent_count += 1
    
    # Check if we should block
    if recent_count >= tenant.rl_max_attempts:
        unblock_at = datetime.utcnow() + timedelta(minutes=tenant.rl_block_minutes)
        
        # Check if already blocked
        existing_block = Blocklist.query.filter_by(
            screening_number=tenant.screening_number,
            caller_digits=caller_digits
        ).first()
        
        if existing_block:
            # Update existing block
            existing_block.unblock_at = unblock_at
        else:
            # Create new block
            new_block = Blocklist(
                screening_number=tenant.screening_number,
                caller_digits=caller_digits,
                unblock_at=unblock_at
            )
            db.session.add(new_block)
    
    db.session.commit()

def clear_failures(tenant: Tenant, caller_digits: str):
    """
    Clear all failure records for a caller (successful verification).
    """
    FailLog.query.filter_by(
        screening_number=tenant.screening_number,
        caller_digits=caller_digits
    ).delete()
    db.session.commit()
