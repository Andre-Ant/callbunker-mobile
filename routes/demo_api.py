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
            "from_number": user.twilio_phone_number or "(631) 641-7728",
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
                    "from_number": user.twilio_phone_number or "(631) 641-7728",
                    "status": "completed",
                    "duration": 154,  # 2:34
                    "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat()
                },
                {
                    "id": f"demo_{user_id}_sample_2", 
                    "to_number": "(555) 987-6543",
                    "from_number": user.twilio_phone_number or "(631) 641-7728",
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
                "defense_number": user.twilio_phone_number or "(631) 641-7728",
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