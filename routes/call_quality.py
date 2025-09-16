"""
CallBunker Call Quality Monitoring Routes
Real-time call quality metrics and user feedback system
"""
import json
import logging
import hmac
import hashlib
import base64
import os
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, session
from sqlalchemy import func, desc, and_
from app import db
from models_multi_user import User, MultiUserCallLog, CallQualityMetrics, QualityAlert

call_quality_bp = Blueprint('call_quality', __name__)

@call_quality_bp.route('/dashboard')
def quality_dashboard():
    """Call quality monitoring dashboard"""
    return render_template('call_quality_dashboard.html')

def validate_twilio_signature(request_body, signature):
    """Validate Twilio webhook signature for security"""
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not auth_token:
        return False
    
    # Get the full URL (including protocol and domain)
    url = request.url
    
    # Compute the expected signature
    computed_sig = base64.b64encode(
        hmac.new(
            auth_token.encode('utf-8'),
            (url + request_body).encode('utf-8'),
            hashlib.sha1
        ).digest()
    ).decode('ascii')
    
    return hmac.compare_digest(computed_sig, signature)

def require_user_auth(user_id):
    """Require authentication for user-specific endpoints"""
    # For demo/development, we'll do basic session check
    # In production, implement proper JWT/OAuth authentication
    if 'user_id' not in session:
        return False, jsonify({'error': 'Authentication required'}), 401
    
    # Verify user owns the resource
    if session['user_id'] != user_id:
        return False, jsonify({'error': 'Unauthorized access'}), 403
    
    return True, None, None

@call_quality_bp.route('/twilio/insights', methods=['POST'])
def twilio_insights_webhook():
    """Webhook to receive Twilio Voice Insights data"""
    try:
        # Validate Twilio signature for security
        signature = request.headers.get('X-Twilio-Signature', '')
        if not validate_twilio_signature(request.get_data(as_text=True), signature):
            logging.warning("Invalid Twilio signature in insights webhook")
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get Voice Insights data from Twilio
        insights_data = request.get_json()
        
        call_sid = insights_data.get('CallSid')
        if not call_sid:
            return jsonify({'error': 'Missing CallSid'}), 400
        
        # Find the call log for this Twilio call
        call_log = MultiUserCallLog.query.filter_by(twilio_call_sid=call_sid).first()
        if not call_log:
            logging.warning(f"No call log found for Call SID: {call_sid}")
            return jsonify({'message': 'Call log not found'}), 200
        
        # Extract quality metrics from Voice Insights
        quality_metrics = CallQualityMetrics.query.filter_by(call_log_id=call_log.id).first()
        if not quality_metrics:
            quality_metrics = CallQualityMetrics()
            quality_metrics.call_log_id = call_log.id
            quality_metrics.user_id = call_log.user_id
            db.session.add(quality_metrics)
        
        # Map Twilio Voice Insights metrics
        if 'jitter' in insights_data:
            quality_metrics.jitter_ms = insights_data['jitter']
        if 'rtt' in insights_data:  # Round-trip time
            quality_metrics.latency_ms = insights_data['rtt']
        if 'packet_loss' in insights_data:
            quality_metrics.packet_loss_percent = insights_data['packet_loss']
        if 'mos' in insights_data:
            quality_metrics.mos_score = insights_data['mos']
        
        # Additional Twilio metrics
        edge_location = insights_data.get('edge_location')
        if edge_location:
            quality_metrics.quality_issues = json.dumps({
                'edge_location': edge_location,
                'source': 'twilio_insights'
            })
        
        # Auto-assess quality
        quality_category = assess_quality_category(quality_metrics)
        quality_metrics.quality_category = quality_category
        
        db.session.commit()
        
        # Check for quality alerts
        check_and_create_alerts(call_log.user_id, quality_metrics)
        
        logging.info(f"Voice Insights processed for call {call_sid}: {quality_category} quality")
        
        return jsonify({'success': True, 'quality_category': quality_category})
        
    except Exception as e:
        logging.error(f"Error processing Voice Insights webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@call_quality_bp.route('/api/users/<int:user_id>/calls/<int:call_log_id>/quality', methods=['POST'])
def submit_quality_metrics(user_id, call_log_id):
    """Submit real-time call quality metrics during or after a call"""
    # Require authentication
    auth_valid, error_response, status_code = require_user_auth(user_id)
    if not auth_valid:
        return error_response, status_code
    
    user = User.query.get_or_404(user_id)
    call_log = MultiUserCallLog.query.filter_by(user_id=user_id, id=call_log_id).first()
    
    if not call_log:
        return jsonify({'error': 'Call not found'}), 404
    
    data = request.get_json()
    
    # Find existing metrics or create new
    quality_metrics = CallQualityMetrics.query.filter_by(
        call_log_id=call_log_id,
        user_id=user_id
    ).first()
    
    if not quality_metrics:
        quality_metrics = CallQualityMetrics()
        quality_metrics.call_log_id = call_log_id
        quality_metrics.user_id = user_id
        db.session.add(quality_metrics)
    
    # Update metrics from request data
    if 'jitter_ms' in data:
        quality_metrics.jitter_ms = data['jitter_ms']
    if 'latency_ms' in data:
        quality_metrics.latency_ms = data['latency_ms']
    if 'packet_loss_percent' in data:
        quality_metrics.packet_loss_percent = data['packet_loss_percent']
    if 'mos_score' in data:
        quality_metrics.mos_score = data['mos_score']
    if 'audio_input_level' in data:
        quality_metrics.audio_input_level = data['audio_input_level']
    if 'audio_output_level' in data:
        quality_metrics.audio_output_level = data['audio_output_level']
    if 'echo_score' in data:
        quality_metrics.echo_score = data['echo_score']
    if 'network_type' in data:
        quality_metrics.network_type = data['network_type']
    if 'device_platform' in data:
        quality_metrics.device_platform = data['device_platform']
    if 'app_version' in data:
        quality_metrics.app_version = data['app_version']
    
    # Automatic quality assessment
    quality_category = assess_quality_category(quality_metrics)
    quality_metrics.quality_category = quality_category
    
    # Detect quality issues
    issues = detect_quality_issues(quality_metrics)
    if issues:
        quality_metrics.quality_issues = json.dumps(issues)
    
    quality_metrics.measurement_time = datetime.utcnow()
    db.session.commit()
    
    # Check if we need to create quality alerts
    check_and_create_alerts(user_id, quality_metrics)
    
    return jsonify({
        'success': True,
        'quality_id': quality_metrics.id,
        'quality_category': quality_category,
        'issues_detected': issues,
        'recommendations': get_quality_recommendations(quality_metrics)
    })

@call_quality_bp.route('/api/users/<int:user_id>/calls/<int:call_log_id>/feedback', methods=['POST'])
def submit_user_feedback(user_id, call_log_id):
    """Submit user feedback for call quality"""
    # Require authentication
    auth_valid, error_response, status_code = require_user_auth(user_id)
    if not auth_valid:
        return error_response, status_code
    
    user = User.query.get_or_404(user_id)
    
    data = request.get_json()
    user_rating = data.get('rating')  # 1-5 scale
    user_feedback = data.get('feedback', '')
    
    if not user_rating or not (1 <= user_rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Find or create quality metrics record
    quality_metrics = CallQualityMetrics.query.filter_by(
        call_log_id=call_log_id,
        user_id=user_id
    ).first()
    
    if not quality_metrics:
        quality_metrics = CallQualityMetrics()
        quality_metrics.call_log_id = call_log_id
        quality_metrics.user_id = user_id
        db.session.add(quality_metrics)
    
    quality_metrics.user_rating = user_rating
    quality_metrics.user_feedback = user_feedback
    quality_metrics.feedback_submitted_at = datetime.utcnow()
    
    # Update quality category based on user rating if no automatic assessment
    if not quality_metrics.quality_category:
        if user_rating >= 4:
            quality_metrics.quality_category = 'excellent' if user_rating == 5 else 'good'
        elif user_rating == 3:
            quality_metrics.quality_category = 'fair'
        else:
            quality_metrics.quality_category = 'poor'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Thank you for your feedback!',
        'quality_id': quality_metrics.id
    })

@call_quality_bp.route('/api/users/<int:user_id>/quality/summary', methods=['GET'])
def get_quality_summary(user_id):
    """Get call quality summary for a user"""
    # Require authentication
    auth_valid, error_response, status_code = require_user_auth(user_id)
    if not auth_valid:
        return error_response, status_code
    
    user = User.query.get_or_404(user_id)
    
    # Query parameters
    days = request.args.get('days', 7, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Get recent quality metrics
    quality_metrics = db.session.query(CallQualityMetrics)\
        .join(MultiUserCallLog)\
        .filter(CallQualityMetrics.user_id == user_id)\
        .filter(CallQualityMetrics.created_at >= since_date)\
        .order_by(desc(CallQualityMetrics.created_at))\
        .limit(limit).all()
    
    # Calculate averages
    total_calls = len(quality_metrics)
    if total_calls == 0:
        return jsonify({
            'total_calls': 0,
            'average_mos': None,
            'average_latency': None,
            'average_jitter': None,
            'quality_distribution': {},
            'recent_metrics': []
        })
    
    # Calculate statistics
    mos_scores = [m.mos_score for m in quality_metrics if m.mos_score is not None]
    latencies = [m.latency_ms for m in quality_metrics if m.latency_ms is not None]
    jitters = [m.jitter_ms for m in quality_metrics if m.jitter_ms is not None]
    
    avg_mos = sum(mos_scores) / len(mos_scores) if mos_scores else None
    avg_latency = sum(latencies) / len(latencies) if latencies else None
    avg_jitter = sum(jitters) / len(jitters) if jitters else None
    
    # Quality distribution
    quality_counts = {}
    for metric in quality_metrics:
        category = metric.quality_category or 'unknown'
        quality_counts[category] = quality_counts.get(category, 0) + 1
    
    return jsonify({
        'total_calls': total_calls,
        'average_mos': round(avg_mos, 2) if avg_mos else None,
        'average_latency': round(avg_latency, 1) if avg_latency else None,
        'average_jitter': round(avg_jitter, 1) if avg_jitter else None,
        'quality_distribution': quality_counts,
        'recent_metrics': [{
            'call_log_id': m.call_log_id,
            'mos_score': m.mos_score,
            'latency_ms': m.latency_ms,
            'jitter_ms': m.jitter_ms,
            'packet_loss_percent': m.packet_loss_percent,
            'quality_category': m.quality_category,
            'user_rating': m.user_rating,
            'network_type': m.network_type,
            'device_platform': m.device_platform,
            'created_at': m.created_at.isoformat()
        } for m in quality_metrics]
    })

@call_quality_bp.route('/api/users/<int:user_id>/quality/alerts', methods=['GET'])
def get_quality_alerts(user_id):
    """Get active quality alerts for a user"""
    user = User.query.get_or_404(user_id)
    
    active_alerts = QualityAlert.query.filter_by(
        user_id=user_id,
        is_active=True
    ).order_by(desc(QualityAlert.created_at)).all()
    
    return jsonify([{
        'alert_id': alert.id,
        'alert_type': alert.alert_type,
        'severity': alert.severity,
        'message': alert.message,
        'calls_affected': alert.calls_affected,
        'time_period_hours': alert.time_period_hours,
        'created_at': alert.created_at.isoformat()
    } for alert in active_alerts])

@call_quality_bp.route('/api/users/<int:user_id>/quality/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(user_id, alert_id):
    """Acknowledge a quality alert"""
    alert = QualityAlert.query.filter_by(
        id=alert_id,
        user_id=user_id
    ).first_or_404()
    
    alert.acknowledged_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Alert acknowledged'})

# Helper functions

def assess_quality_category(metrics):
    """Automatically assess call quality category based on metrics"""
    if not metrics.mos_score and not metrics.latency_ms and not metrics.jitter_ms:
        return None
    
    # MOS Score is the primary indicator
    if metrics.mos_score:
        if metrics.mos_score >= 4.0:
            return 'excellent'
        elif metrics.mos_score >= 3.5:
            return 'good'
        elif metrics.mos_score >= 2.5:
            return 'fair'
        else:
            return 'poor'
    
    # Fallback to latency/jitter assessment
    poor_indicators = 0
    if metrics.latency_ms and metrics.latency_ms > 300:  # >300ms latency
        poor_indicators += 1
    if metrics.jitter_ms and metrics.jitter_ms > 100:  # >100ms jitter
        poor_indicators += 1
    if metrics.packet_loss_percent and metrics.packet_loss_percent > 5:  # >5% packet loss
        poor_indicators += 1
    
    if poor_indicators >= 2:
        return 'poor'
    elif poor_indicators == 1:
        return 'fair'
    else:
        return 'good'

def detect_quality_issues(metrics):
    """Detect specific quality issues based on metrics"""
    issues = []
    
    if metrics.latency_ms and metrics.latency_ms > 200:
        issues.append({
            'type': 'high_latency',
            'severity': 'high' if metrics.latency_ms > 300 else 'medium',
            'value': metrics.latency_ms,
            'message': f'High latency detected: {metrics.latency_ms}ms'
        })
    
    if metrics.jitter_ms and metrics.jitter_ms > 50:
        issues.append({
            'type': 'high_jitter',
            'severity': 'high' if metrics.jitter_ms > 100 else 'medium',
            'value': metrics.jitter_ms,
            'message': f'High jitter detected: {metrics.jitter_ms}ms'
        })
    
    if metrics.packet_loss_percent and metrics.packet_loss_percent > 1:
        issues.append({
            'type': 'packet_loss',
            'severity': 'high' if metrics.packet_loss_percent > 5 else 'medium',
            'value': metrics.packet_loss_percent,
            'message': f'Packet loss detected: {metrics.packet_loss_percent}%'
        })
    
    if metrics.echo_score and metrics.echo_score > 0.3:
        issues.append({
            'type': 'echo',
            'severity': 'medium',
            'value': metrics.echo_score,
            'message': 'Echo detected during call'
        })
    
    if metrics.audio_input_level and metrics.audio_input_level < 0.1:
        issues.append({
            'type': 'low_microphone',
            'severity': 'medium',
            'value': metrics.audio_input_level,
            'message': 'Low microphone input level'
        })
    
    return issues

def get_quality_recommendations(metrics):
    """Get recommendations based on quality metrics"""
    recommendations = []
    
    if metrics.network_type == 'cellular':
        recommendations.append("Consider switching to Wi-Fi for better call quality")
    
    if metrics.latency_ms and metrics.latency_ms > 200:
        recommendations.append("High latency detected - check your internet connection")
    
    if metrics.jitter_ms and metrics.jitter_ms > 50:
        recommendations.append("Network instability detected - try moving closer to your router")
    
    if metrics.echo_score and metrics.echo_score > 0.3:
        recommendations.append("Use headphones or earbuds to reduce echo")
    
    if metrics.audio_input_level and metrics.audio_input_level < 0.1:
        recommendations.append("Check microphone settings or speak louder")
    
    return recommendations

def check_and_create_alerts(user_id, quality_metrics):
    """Check if quality metrics warrant creating alerts"""
    # Check for poor quality pattern (multiple poor calls in short time)
    recent_poor_calls = db.session.query(CallQualityMetrics)\
        .filter(CallQualityMetrics.user_id == user_id)\
        .filter(CallQualityMetrics.created_at >= datetime.utcnow() - timedelta(hours=1))\
        .filter(CallQualityMetrics.quality_category == 'poor')\
        .count()
    
    if recent_poor_calls >= 3:
        # Check if we already have an active alert for this
        existing_alert = QualityAlert.query.filter_by(
            user_id=user_id,
            alert_type='poor_quality',
            is_active=True
        ).first()
        
        if not existing_alert:
            alert = QualityAlert()
            alert.user_id = user_id
            alert.alert_type = 'poor_quality'
            alert.severity = 'high'
            alert.message = f'Multiple poor quality calls detected in the last hour ({recent_poor_calls} calls)'
            alert.calls_affected = recent_poor_calls
            alert.time_period_hours = 1
            alert.trigger_condition = json.dumps({
                'condition': 'poor_quality_calls',
                'threshold': 3,
                'period_hours': 1,
                'actual_count': recent_poor_calls
            })
            db.session.add(alert)
            db.session.commit()
            
            logging.warning(f"Quality alert created for user {user_id}: {alert.message}")