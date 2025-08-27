from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from datetime import datetime
from app import db
from models import Tenant, Whitelist, FailLog, Blocklist
from utils.auth import require_admin_web, parse_annotated_number, norm_digits
from utils.sendgrid_helper import send_notification_email
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
    number, custom_pin = parse_annotated_number(number_input)
    
    if not number:
        flash('Invalid number format!', 'error')
        return redirect(url_for('admin.whitelist_manage', screening_number=screening_number))
    
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
    existing = Whitelist.query.filter_by(
        screening_number=screening_number,
        number=test_number_normalized
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
