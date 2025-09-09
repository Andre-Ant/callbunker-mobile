"""
Demo API endpoints for the full functional demo
Provides call simulation and history for web-based testing
"""

from flask import Blueprint, request, jsonify
from models_multi_user import db, User, UserWhitelist
from datetime import datetime, timedelta
import json

demo_api_bp = Blueprint('demo_api', __name__, url_prefix='/demo/api')

# In-memory call history for demo purposes
demo_call_history = {}

@demo_api_bp.route('/signup', methods=['POST'])
def demo_signup():
    """Create new user account for demo"""
    try:
        data = request.get_json()
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data.get('email')).first()
        if existing_user:
            return jsonify({'success': False, 'error': 'User with this email already exists'})
        
        # Get available phone number
        from models_multi_user import TwilioPhonePool
        available_number = TwilioPhonePool.query.filter_by(is_assigned=False).first()
        if not available_number:
            return jsonify({'success': False, 'error': 'No CallBunker numbers available. Please contact support.'})
        
        # Normalize phone numbers
        import re
        def normalize_phone(phone):
            return re.sub(r'[^\d]', '', phone)
        
        # Create new user
        user = User()
        user.name = data.get('name')
        user.email = data.get('email').lower().strip()
        user.google_voice_number = normalize_phone(data.get('google_voice_number', ''))
        user.real_phone_number = normalize_phone(data.get('real_phone_number', ''))
        user.assigned_twilio_number = available_number.phone_number
        user.pin = data.get('pin', '1234')
        user.verbal_code = data.get('verbal_code', 'open sesame')
        user.retry_limit = 3
        user.forward_mode = 'bridge'
        user.rl_window_sec = 3600
        user.rl_max_attempts = 5
        user.rl_block_minutes = 60
        user.is_active = True
        user.google_voice_verified = False
        user.twilio_number_configured = False
        user.created_at = datetime.now()
        user.updated_at = datetime.now()
        
        # Save user first to get the ID
        db.session.add(user)
        db.session.flush()  # This gives user an ID without committing
        
        # Now assign the phone number
        available_number.is_assigned = True
        available_number.assigned_to_user_id = user.id
        
        # Commit everything
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'assigned_twilio_number': user.assigned_twilio_number,
                'google_voice_number': user.google_voice_number,
                'pin': user.pin,
                'verbal_code': user.verbal_code
            }
        })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@demo_api_bp.route('/make-call', methods=['POST'])
def demo_make_call():
    """Make a simulated call for demo"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        target_number = data.get('target_number')
        
        user = User.query.get_or_404(user_id)
        
        # Generate call log entry
        call_id = f"demo_{user_id}_{int(datetime.now().timestamp())}"
        
        # Store in demo history
        if user_id not in demo_call_history:
            demo_call_history[user_id] = []
        
        call_entry = {
            'id': call_id,
            'target_number': target_number,
            'caller_id_shown': user.google_voice_number,
            'status': 'completed',
            'direction': 'outbound',
            'duration': 45,
            'timestamp': datetime.now().isoformat()
        }
        
        demo_call_history[user_id].insert(0, call_entry)  # Add to front
        
        return jsonify({
            'success': True,
            'call_id': call_id,
            'target_number': target_number,
            'caller_id_shown': user.google_voice_number,
            'message': 'Call initiated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@demo_api_bp.route('/call-history/<int:user_id>', methods=['GET'])
def demo_call_history_route(user_id):
    """Get call history for demo user"""
    try:
        user = User.query.get_or_404(user_id)
        calls = demo_call_history.get(user_id, [])
        
        return jsonify({
            'success': True,
            'calls': calls
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@demo_api_bp.route('/contacts/<int:user_id>', methods=['GET'])
def demo_get_contacts(user_id):
    """Get trusted contacts for demo user"""
    try:
        contacts = UserWhitelist.query.filter_by(user_id=user_id).all()
        
        contacts_list = []
        for contact in contacts:
            contacts_list.append({
                'id': contact.id,
                'name': f"Contact {contact.caller_number[-4:]}",  # Generate name since model doesn't store it
                'phone_number': contact.caller_number,
                'auto_whitelisted': not contact.allows_verbal
            })
        
        return jsonify({
            'success': True,
            'contacts': contacts_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@demo_api_bp.route('/add-contact', methods=['POST'])
def demo_add_contact():
    """Add trusted contact for demo"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        name = data.get('name')
        phone_number = data.get('phone_number')
        
        # Normalize phone number
        import re
        normalized_phone = re.sub(r'[^\d]', '', phone_number)
        
        # Create new contact (UserWhitelist only has caller_number, not name)
        contact = UserWhitelist()
        contact.user_id = user_id
        contact.caller_number = normalized_phone
        contact.allows_verbal = False
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'contact': {
                'id': contact.id,
                'name': name,  # Store name separately since model doesn't have it
                'phone_number': contact.caller_number
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@demo_api_bp.route('/remove-contact', methods=['POST'])
def demo_remove_contact():
    """Remove trusted contact for demo"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        contact_id = data.get('contact_id')
        
        contact = UserWhitelist.query.filter_by(id=contact_id, user_id=user_id).first()
        if contact:
            db.session.delete(contact)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Contact not found'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@demo_api_bp.route('/user/<int:user_id>/call_direct', methods=['POST'])
def demo_call_direct(user_id):
    """Simulate call initiation for demo"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        to_number = data.get('to_number', '')
        
        # Generate a unique call log ID
        call_log_id = f"demo_{user_id}_{int(datetime.now().timestamp())}"
        
        # Simulate call configuration
        call_config = {
            "success": True,
            "call_log_id": call_log_id,
            "to_number": to_number,
            "from_number": user.assigned_twilio_number or "(631) 641-7728",
            "native_call_config": {
                "target_number": to_number,
                "spoofed_caller_id": user.google_voice_number or "(555) 123-4567"
            },
            "status": "initiated",
            "timestamp": datetime.now().isoformat()
        }
        
        # Store call in demo history
        if user_id not in demo_call_history:
            demo_call_history[user_id] = []
        
        demo_call_history[user_id].append({
            "id": call_log_id,
            "to_number": to_number,
            "from_number": call_config["from_number"],
            "status": "initiated",
            "duration": 0,
            "timestamp": call_config["timestamp"]
        })
        
        return jsonify(call_config)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@demo_api_bp.route('/user/<int:user_id>/calls/<call_log_id>/complete', methods=['POST'])
def demo_complete_call(user_id, call_log_id):
    """Log call completion for demo"""
    try:
        data = request.get_json()
        status = data.get('status', 'completed')
        duration = data.get('duration_seconds', 0)
        
        # Update call in demo history
        if user_id in demo_call_history:
            for call in demo_call_history[user_id]:
                if call['id'] == call_log_id:
                    call['status'] = status
                    call['duration'] = duration
                    call['completed_at'] = datetime.now().isoformat()
                    break
        
        return jsonify({
            "success": True,
            "message": "Call completion logged successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@demo_api_bp.route('/user/<int:user_id>/calls', methods=['GET'])
def demo_get_call_history(user_id):
    """Get call history for demo"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get demo call history
        user_calls = demo_call_history.get(user_id, [])
        
        # Add some sample calls if none exist
        if not user_calls:
            sample_calls = [
                {
                    "id": f"demo_{user_id}_sample_1",
                    "to_number": "(555) 123-4567",
                    "from_number": user.assigned_twilio_number or "(631) 641-7728",
                    "status": "completed",
                    "duration": 154,  # 2:34
                    "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat()
                },
                {
                    "id": f"demo_{user_id}_sample_2", 
                    "to_number": "(555) 987-6543",
                    "from_number": user.assigned_twilio_number or "(631) 641-7728",
                    "status": "completed",
                    "duration": 105,  # 1:45
                    "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()
                }
            ]
            demo_call_history[user_id] = sample_calls
            user_calls = sample_calls
        
        # Format for display
        formatted_calls = []
        for call in user_calls:
            duration_str = "0:00"
            if call.get('duration', 0) > 0:
                minutes = call['duration'] // 60
                seconds = call['duration'] % 60
                duration_str = f"{minutes}:{seconds:02d}"
            
            # Calculate time ago
            try:
                call_time = datetime.fromisoformat(call['timestamp'])
                time_diff = datetime.now() - call_time
                if time_diff.days > 0:
                    time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
                elif time_diff.seconds > 60:
                    minutes = time_diff.seconds // 60
                    time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                else:
                    time_ago = "Just now"
            except:
                time_ago = "Unknown"
            
            formatted_calls.append({
                "id": call['id'],
                "phone": call['to_number'],
                "time": time_ago,
                "duration": duration_str,
                "status": call['status']
            })
        
        return jsonify(formatted_calls)
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@demo_api_bp.route('/user/<int:user_id>/status', methods=['GET'])
def demo_user_status(user_id):
    """Get user status and stats for demo"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Count trusted contacts
        contacts_count = UserWhitelist.query.filter_by(user_id=user_id).count()
        
        # Count calls
        calls_count = len(demo_call_history.get(user_id, []))
        
        return jsonify({
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "defense_number": user.assigned_twilio_number or "(631) 641-7728",
                "google_voice": user.google_voice_number
            },
            "stats": {
                "trusted_contacts": contacts_count,
                "total_calls": calls_count,
                "blocked_calls": 6  # Mock data for demo
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500