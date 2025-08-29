from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from datetime import datetime, timedelta
from app import db
from models import Tenant, Whitelist, FailLog, Blocklist
from models_multi_user import TwilioPhonePool
from models_multi_user import User, TwilioPhonePool, UserWhitelist
from utils.auth import require_admin_web, parse_annotated_number, norm_digits
from utils.sendgrid_helper import send_notification_email
from sqlalchemy import func, and_
import re

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@require_admin_web
def admin_home():
    """Admin dashboard"""
    tenants = Tenant.query.all()
    return render_template('index.html', tenants=tenants)

@admin_bp.route('/tenant/<screening_number>')
@require_admin_web
def tenant_detail(screening_number):
    """View tenant details"""
    tenant = Tenant.query.get_or_404(screening_number)
    whitelists = Whitelist.query.filter_by(screening_number=screening_number).all()
    recent_fails = FailLog.query.filter_by(screening_number=screening_number).order_by(FailLog.ts.desc()).limit(20).all()
    active_blocks = Blocklist.query.filter(
        Blocklist.screening_number == screening_number,
        Blocklist.unblock_at > datetime.utcnow()
    ).all()
    
    return render_template('tenant_detail.html', 
                         tenant=tenant, 
                         whitelists=whitelists, 
                         recent_fails=recent_fails,
                         active_blocks=active_blocks)

@admin_bp.route('/tenant/<screening_number>/edit', methods=['GET', 'POST'])
@require_admin_web
def edit_tenant(screening_number):
    """Edit tenant configuration"""
    tenant = Tenant.query.get_or_404(screening_number)
    
    if request.method == 'POST':
        tenant.owner_label = request.form.get('owner_label', '').strip()
        tenant.forward_to = request.form.get('forward_to', '').strip()
        tenant.current_pin = request.form.get('current_pin', '1122').strip()
        tenant.verbal_code = request.form.get('verbal_code', 'open sesame').strip()
        tenant.retry_limit = int(request.form.get('retry_limit', 3))
        tenant.forward_mode = request.form.get('forward_mode', 'bridge').strip()
        tenant.rl_window_sec = int(request.form.get('rl_window_sec', 3600))
        tenant.rl_max_attempts = int(request.form.get('rl_max_attempts', 5))
        tenant.rl_block_minutes = int(request.form.get('rl_block_minutes', 60))
        tenant.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Tenant updated successfully!', 'success')
        return redirect(url_for('admin.tenant_detail', screening_number=screening_number))
    
    return render_template('tenant_form.html', tenant=tenant, action='Edit')

@admin_bp.route('/onboarding')
@require_admin_web
def onboarding():
    """Enhanced onboarding flow for new users"""
    return render_template('onboarding.html')

@admin_bp.route('/google-voice-setup', methods=['GET', 'POST'])
@require_admin_web
def google_voice_setup():
    """Google Voice setup with automatic whitelisting"""
    if request.method == 'GET':
        return render_template('google_voice_setup.html')
    
    try:
        google_voice_number = norm_digits(request.form.get('google_voice_number', '').strip())
        forward_to = norm_digits(request.form.get('forward_to', '').strip())
        
        if not google_voice_number or not forward_to:
            flash('Both phone numbers are required', 'error')
            return render_template('google_voice_setup.html')
        
        # Create or update tenant for the Google Voice number
        # The screening_number is the Google Voice number since that's what callers dial
        tenant = Tenant.query.get(google_voice_number)
        if not tenant:
            tenant = Tenant(
                screening_number=google_voice_number,
                owner_label=f"Google Voice User ({google_voice_number})",
                forward_to=forward_to,
                current_pin="1122",
                verbal_code="open sesame",
                retry_limit=3,
                forward_mode="bridge",
                rl_window_sec=3600,
                rl_max_attempts=5,
                rl_block_minutes=60
            )
            db.session.add(tenant)
        else:
            # Update existing tenant
            tenant.forward_to = forward_to
        
        # Key insight: Auto-whitelist the Google Voice number itself
        # Since the user configured GV to show their GV number as caller ID,
        # ALL forwarded calls will appear to come from this Google Voice number
        existing_whitelist = Whitelist.query.filter_by(
            screening_number=google_voice_number,
            number=google_voice_number
        ).first()
        
        if not existing_whitelist:
            whitelist_entry = Whitelist(
                screening_number=google_voice_number,
                number=google_voice_number,
                pin=None,  # No PIN needed for auto-whitelisted calls
                verbal=False
            )
            db.session.add(whitelist_entry)
        
        db.session.commit()
        
        flash(f'Google Voice setup complete! Your number {google_voice_number} is now protected by CallBunker.', 'success')
        return redirect(url_for('admin.tenant_detail', screening_number=google_voice_number))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Setup failed: {str(e)}', 'error')
        return render_template('google_voice_setup.html')

@admin_bp.route('/onboarding/tenant', methods=['POST'])
@require_admin_web
def onboarding_tenant():
    """Create or update tenant for onboarding flow"""
    try:
        screening_number = request.form.get('screening_number', '').strip()
        
        # Check if tenant already exists
        existing_tenant = Tenant.query.get(screening_number)
        if existing_tenant:
            # Update existing tenant instead of creating new one
            existing_tenant.owner_label = request.form.get('owner_label', '').strip()
            existing_tenant.forward_to = request.form.get('forward_to', '').strip()
            existing_tenant.current_pin = request.form.get('current_pin', '1122').strip()
            existing_tenant.verbal_code = request.form.get('verbal_code', 'open sesame').strip()
            existing_tenant.retry_limit = int(request.form.get('retry_limit', 3))
            existing_tenant.forward_mode = request.form.get('forward_mode', 'bridge').strip()
            existing_tenant.rl_window_sec = int(request.form.get('rl_window_sec', 3600))
            existing_tenant.rl_max_attempts = int(request.form.get('rl_max_attempts', 5))
            existing_tenant.rl_block_minutes = int(request.form.get('rl_block_minutes', 60))
            existing_tenant.updated_at = datetime.utcnow()
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Account updated successfully!', 'existing': True})
        
        # Create new tenant
        tenant = Tenant(
            screening_number=screening_number,
            owner_label=request.form.get('owner_label', '').strip(),
            forward_to=request.form.get('forward_to', '').strip(),
            current_pin=request.form.get('current_pin', '1122').strip(),
            verbal_code=request.form.get('verbal_code', 'open sesame').strip(),
            retry_limit=int(request.form.get('retry_limit', 3)),
            forward_mode=request.form.get('forward_mode', 'bridge').strip(),
            rl_window_sec=int(request.form.get('rl_window_sec', 3600)),
            rl_max_attempts=int(request.form.get('rl_max_attempts', 5)),
            rl_block_minutes=int(request.form.get('rl_block_minutes', 60))
        )
        
        db.session.add(tenant)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Account created successfully!', 'existing': False})
        
    except Exception as e:
        # Always return JSON, even for errors
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to create account: {str(e)}'}), 400

@admin_bp.route('/tenant/new', methods=['GET', 'POST'])
@require_admin_web
def new_tenant():
    """Create new tenant"""
    if request.method == 'POST':
        screening_number = request.form.get('screening_number', '').strip()
        
        # Check if tenant already exists
        if Tenant.query.get(screening_number):
            flash('A tenant with this screening number already exists!', 'error')
            return render_template('tenant_form.html', action='New')
        
        tenant = Tenant(
            screening_number=screening_number,
            owner_label=request.form.get('owner_label', '').strip(),
            forward_to=request.form.get('forward_to', '').strip(),
            current_pin=request.form.get('current_pin', '1122').strip(),
            verbal_code=request.form.get('verbal_code', 'open sesame').strip(),
            retry_limit=int(request.form.get('retry_limit', 3)),
            forward_mode=request.form.get('forward_mode', 'bridge').strip(),
            rl_window_sec=int(request.form.get('rl_window_sec', 3600)),
            rl_max_attempts=int(request.form.get('rl_max_attempts', 5)),
            rl_block_minutes=int(request.form.get('rl_block_minutes', 60))
        )
        
        db.session.add(tenant)
        db.session.commit()
        flash('Tenant created successfully!', 'success')
        return redirect(url_for('admin.tenant_detail', screening_number=screening_number))
    
    return render_template('tenant_form.html', action='New')

@admin_bp.route('/tenant/<screening_number>/whitelist')
@require_admin_web
def whitelist_manage(screening_number):
    """Manage whitelist for tenant"""
    tenant = Tenant.query.get_or_404(screening_number)
    whitelists = Whitelist.query.filter_by(screening_number=screening_number).all()
    return render_template('whitelist.html', tenant=tenant, whitelists=whitelists)

@admin_bp.route('/tenant/<screening_number>/whitelist/add', methods=['POST'])
@require_admin_web
def whitelist_add(screening_number):
    """Add entry to whitelist"""
    tenant = Tenant.query.get_or_404(screening_number)
    
    number_input = request.form.get('number', '').strip()
    number_raw, custom_pin = parse_annotated_number(number_input)
    
    if not number_raw:
        flash('Invalid number format!', 'error')
        return redirect(url_for('admin.whitelist_manage', screening_number=screening_number))
    
    # Normalize the number using the same logic as the voice system
    number = norm_digits(number_raw)
    
    # Check if entry already exists
    existing = Whitelist.query.filter_by(screening_number=screening_number, number=number).first()
    if existing:
        flash('This number is already in the whitelist!', 'error')
        return redirect(url_for('admin.whitelist_manage', screening_number=screening_number))
    
    whitelist_entry = Whitelist(
        screening_number=screening_number,
        number=number,
        pin=custom_pin,
        verbal=bool(request.form.get('verbal'))
    )
    
    db.session.add(whitelist_entry)
    db.session.commit()
    flash('Number added to whitelist!', 'success')
    return redirect(url_for('admin.whitelist_manage', screening_number=screening_number))

@admin_bp.route('/whitelist/<int:whitelist_id>/delete', methods=['POST'])
@require_admin_web
def whitelist_delete(whitelist_id):
    """Remove entry from whitelist"""
    whitelist_entry = Whitelist.query.get_or_404(whitelist_id)
    screening_number = whitelist_entry.screening_number
    
    db.session.delete(whitelist_entry)
    db.session.commit()
    flash('Number removed from whitelist!', 'success')
    return redirect(url_for('admin.whitelist_manage', screening_number=screening_number))

@admin_bp.route('/tenant/<screening_number>/unblock', methods=['POST'])
@require_admin_web
def unblock_number(screening_number):
    """Manually unblock a number"""
    caller_digits = request.form.get('caller_digits')
    
    if not screening_number or not caller_digits:
        flash('Missing required parameters!', 'error')
        return redirect(url_for('admin.admin_home'))
    
    # Remove from blocklist
    blocked_entries = Blocklist.query.filter_by(
        screening_number=screening_number,
        caller_digits=caller_digits
    ).all()
    
    for entry in blocked_entries:
        db.session.delete(entry)
    
    db.session.commit()
    flash(f'Number {caller_digits} has been unblocked!', 'success')
    return redirect(url_for('admin.tenant_detail', screening_number=screening_number))

@admin_bp.route('/tenant/<screening_number>/clear_logs', methods=['POST'])
@require_admin_web
def clear_logs(screening_number):
    """Clear failure logs for a tenant"""
    tenant = Tenant.query.get_or_404(screening_number)
    
    FailLog.query.filter_by(screening_number=screening_number).delete()
    db.session.commit()
    
    flash('Failure logs cleared!', 'success')
    return redirect(url_for('admin.tenant_detail', screening_number=screening_number))

@admin_bp.route('/tenant/<screening_number>/test_autowhitelist', methods=['POST'])
@require_admin_web
def test_autowhitelist(screening_number):
    """Test the auto-whitelist functionality"""
    tenant = Tenant.query.get_or_404(screening_number)
    test_number_raw = request.form.get('test_number', '+15551234567').strip()
    
    # Normalize the test number using the same logic as the voice system
    test_number_normalized = norm_digits(test_number_raw)
    
    # Get all whitelisted numbers for debugging
    all_whitelist = Whitelist.query.filter_by(screening_number=screening_number).all()
    whitelist_numbers = [wl.number for wl in all_whitelist]
    
    # Check current whitelist status with normalized number
    # First try the normalized format (without +)
    existing = Whitelist.query.filter_by(
        screening_number=screening_number,
        number=test_number_normalized
    ).first()
    
    # If not found, try the original format (with +) for legacy data
    if not existing:
        existing = Whitelist.query.filter_by(
            screening_number=screening_number,
            number=f"+{test_number_normalized}"
        ).first()
    
    if existing:
        return jsonify({
            'success': True,
            'message': f'Number {test_number_raw} is already whitelisted and would bypass authentication.',
            'whitelisted': True,
            'debug_info': f'Input: {test_number_raw} → Normalized: {test_number_normalized} → Found in whitelist!'
        })
    else:
        return jsonify({
            'success': True,
            'message': f'Number {test_number_raw} is NOT whitelisted. First call would require PIN ({tenant.current_pin}), then auto-whitelist for future calls.',
            'whitelisted': False,
            'pin': tenant.current_pin,
            'debug_info': f'Input: {test_number_raw} → Normalized: {test_number_normalized} → Not found. Whitelist has: {whitelist_numbers}'
        })

@admin_bp.route('/tenant/<screening_number>/delete', methods=['POST'])
@require_admin_web
def delete_tenant(screening_number):
    """Delete a tenant and all associated data"""
    try:
        tenant = Tenant.query.get_or_404(screening_number)
        tenant_name = tenant.owner_label or screening_number
        
        # Delete associated data (handled by cascade)
        db.session.delete(tenant)
        db.session.commit()
        
        flash(f"Successfully deleted user {tenant_name} and all associated data.", "success")
        
        # Send notification email if configured
        try:
            send_notification_email(
                subject="CallBunker - User Deleted",
                body=f"User {tenant_name} ({screening_number}) has been deleted from CallBunker.\n\nDeleted at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )
        except Exception as email_error:
            # Don't fail the deletion if email fails
            print(f"Email notification failed: {email_error}")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {e}", "error")
    
    return redirect(url_for('admin.admin_home'))


# ============================================================================
# ADVANCED ADMIN MONITORING ROUTES
# ============================================================================

@admin_bp.route("/monitor")
@require_admin_web
def twilio_monitor():
    """Advanced admin monitoring interface for Twilio numbers and tenant cohorts"""
    
    # Twilio Numbers Data - Using TwilioPhonePool from multi-user system
    try:
        twilio_numbers = TwilioPhonePool.query.all()
        
        # Add tenant relationship and call stats
        for number in twilio_numbers:
            number.tenant = Tenant.query.filter_by(screening_number=number.phone_number).first()
            number.calls_today = 0  # Could be enhanced with actual call logs
            number.last_activity = number.tenant.updated_at if number.tenant else None
    except:
        # Fallback if TwilioPhonePool does not exist yet
        twilio_numbers = []
    
    # Twilio Statistics
    twilio_stats = {
        "total_numbers": len(twilio_numbers),
        "active_numbers": len([n for n in twilio_numbers if getattr(n, "tenant", None)]),
        "available_numbers": len([n for n in twilio_numbers if not getattr(n, "tenant", None)]),
        "total_cost": sum(getattr(n, "monthly_cost", 1.00) or 1.00 for n in twilio_numbers)
    }
    
    # Get all tenants with relationships
    all_tenants = Tenant.query.outerjoin(Whitelist).all()
    
    # Tenant Statistics and Cohorts
    now = datetime.utcnow()
    today = now.date()
    
    verified_tenants = [t for t in all_tenants if t.test_verified_at]
    unverified_tenants = [t for t in all_tenants if not t.test_verified_at]
    
    # Active today (updated today)
    active_today_tenants = [t for t in all_tenants if t.updated_at and t.updated_at.date() == today]
    
    # Google Voice users (tenants with forward_to configured)
    google_voice_tenants = [t for t in all_tenants if t.forward_to and t.forward_to != t.screening_number]
    
    tenant_stats = {
        "total_tenants": len(all_tenants),
        "verified_tenants": len(verified_tenants),
        "unverified_tenants": len(unverified_tenants),
        "active_today": len(active_today_tenants),
        "google_voice_users": len(google_voice_tenants)
    }
    
    return render_template("admin/twilio_monitor.html",
                         twilio_numbers=twilio_numbers,
                         twilio_stats=twilio_stats,
                         tenant_stats=tenant_stats,
                         all_tenants=all_tenants,
                         verified_tenants=verified_tenants,
                         unverified_tenants=unverified_tenants,
                         active_today_tenants=active_today_tenants,
                         google_voice_tenants=google_voice_tenants,
                         now=now,
                         timedelta=timedelta)

@admin_bp.route("/test-webhook/<phone_number>", methods=["POST"])
@require_admin_web
def test_webhook(phone_number):
    """Test webhook endpoint for a specific Twilio number"""
    try:
        data = request.get_json() or {}
        test_from = data.get("from_number", "+15551234567")
        
        # Find tenant for this number
        tenant = Tenant.query.filter_by(screening_number=phone_number).first()
        if not tenant:
            return jsonify({"success": False, "message": f"No tenant found for {phone_number}"})
        
        # Log test activity
        tenant.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": f"Webhook test completed for {phone_number}",
            "tenant": tenant.owner_label or "Unnamed",
            "forward_to": tenant.forward_to
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Test failed: {str(e)}"})

@admin_bp.route("/test-tenant/<screening_number>", methods=["POST"])
@require_admin_web
def test_tenant_config(screening_number):
    """Test tenant configuration"""
    try:
        tenant = Tenant.query.get_or_404(screening_number)
        
        # Update last activity
        tenant.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Test completed for tenant {tenant.owner_label or screening_number}",
            "config": {
                "pin": tenant.current_pin,
                "verbal": tenant.verbal_code,
                "mode": tenant.forward_mode,
                "retries": tenant.retry_limit
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Test failed: {str(e)}"})


@admin_bp.route('/tenant/list')
@require_admin_web
def tenant_list():
    """Simple tenant list view"""
    tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
    return render_template('tenant_list.html', tenants=tenants)

@admin_bp.route('/verify-twilio-numbers')
def verify_twilio_numbers():
    """Guide for verifying Twilio numbers for outbound calls"""
    twilio_numbers = TwilioPhonePool.query.all()
    return render_template('admin/verify_twilio_numbers.html', 
                         twilio_numbers=twilio_numbers,
                         format_phone=format_phone)

@admin_bp.route('/verification-walkthrough')
def verification_walkthrough():
    """Step-by-step walkthrough for Google Voice verification"""
    return render_template('admin/verification_walkthrough.html')

@admin_bp.route('/verification-troubleshooting')
def verification_troubleshooting():
    """Troubleshooting guide for verification call issues"""
    return render_template('admin/verification_troubleshooting.html')

@admin_bp.route('/sms-verification-guide')
def sms_verification_guide():
    """SMS verification guide - the easy way"""
    return render_template('admin/sms_verification_guide.html')
