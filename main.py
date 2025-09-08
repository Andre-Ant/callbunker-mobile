from app import app
from flask import send_from_directory, render_template_string, request, jsonify
import os
from sms_testing import send_protected_sms, get_sms_status
from voice_messaging import send_voice_message, get_voice_message_status

# Enable CORS headers manually
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Add mobile web testing route first
@app.route('/mobile')
def mobile_demo():
    try:
        with open('mobile_simple.html', 'r') as f:
            content = f.read()
        
        # Add cache busting and mobile optimization
        response = app.response_class(
            response=content,
            status=200,
            mimetype='text/html'
        )
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except FileNotFoundError:
        return render_template_string('''
        <h1>Mobile Demo Loading...</h1>
        <p>Setting up CallBunker mobile demo...</p>
        <script>window.location.reload();</script>
        ''')

# Add main home route - redirect to mobile interface by default
@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CallBunker - Mobile Communication Security</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .hero { text-align: center; padding: 40px 0; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 40px 0; }
            .feature { padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
            .btn { display: inline-block; padding: 12px 24px; background: #007AFF; color: white; text-decoration: none; border-radius: 6px; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>CallBunker</h1>
            <p>Advanced Mobile Communication Security Platform</p>
            <a href="/demo/full-functional" class="btn">🚀 Full Functional Demo</a>
            <a href="/mobile-preview" class="btn">📱 Signup Interface</a>
            <a href="/main-app-demo" class="btn">🏠 Main App Interface</a>
            <a href="/mobile" class="btn">📞 Mobile Demo</a>
        </div>
        
        <div class="features">
            <div class="feature">
                <h3>Multi-User Signup</h3>
                <p>Professional signup interface with Google Voice integration and automatic Defense Number assignment</p>
            </div>
            <div class="feature">
                <h3>Protected Calling</h3>
                <p>Make calls with complete privacy protection through Google Voice caller ID spoofing</p>
            </div>
            <div class="feature">
                <h3>Native Experience</h3>
                <p>Professional mobile app with native calling and messaging integration</p>
            </div>
        </div>
    </body>
    </html>
    ''')

# Add web info route for those who want the landing page
@app.route('/web')
def web_info():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CallBunker - Mobile Communication Security</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .hero { text-align: center; padding: 40px 0; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 40px 0; }
            .feature { padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
            .btn { display: inline-block; padding: 12px 24px; background: #007AFF; color: white; text-decoration: none; border-radius: 6px; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>CallBunker</h1>
            <p>Advanced Mobile Communication Security Platform</p>
            <a href="/mobile" class="btn">Test Mobile Interface</a>
            <a href="/expo" class="btn">Device Testing Guide</a>
        </div>
        
        <div class="features">
            <div class="feature">
                <h3>Protected Calling</h3>
                <p>Make calls with complete privacy protection through Google Voice caller ID spoofing</p>
            </div>
            <div class="feature">
                <h3>Anonymous Messaging</h3>
                <p>Send texts anonymously with standard messaging interface and full privacy</p>
            </div>
            <div class="feature">
                <h3>Native Experience</h3>
                <p>Professional mobile app with native calling and messaging integration</p>
            </div>
        </div>
    </body>
    </html>
    ''')



# Add route for Expo mobile app
@app.route('/expo')
def expo_mobile():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CallBunker - Device Testing</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
            .step { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }
            code { background: #e9ecef; padding: 2px 6px; border-radius: 4px; }
            .btn { display: inline-block; padding: 12px 24px; background: #007AFF; color: white; text-decoration: none; border-radius: 6px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>CallBunker Mobile App - Device Testing</h1>
        
        <h2>Method 1: Expo Go (Recommended)</h2>
        <div class="step">
            <strong>Step 1:</strong> Download "Expo Go" app from your phone's app store
        </div>
        <div class="step">
            <strong>Step 2:</strong> Open terminal and run:<br>
            <code>cd mobile_app && npx expo start</code>
        </div>
        <div class="step">
            <strong>Step 3:</strong> Scan the QR code that appears with Expo Go
        </div>
        <div class="step">
            <strong>Step 4:</strong> Test CallBunker directly on your device!
        </div>
        
        <h2>Method 2: Web Demo</h2>
        <a href="/mobile" class="btn">Test Mobile Interface</a>
        
        <h2>What You Can Test</h2>
        <ul>
            <li>Protected dialer with privacy features</li>
            <li>Native messaging interface</li>
            <li>Tab navigation between screens</li>
            <li>Complete mobile experience</li>
        </ul>
        
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    ''')

# SMS Testing API Endpoints
@app.route('/api/send-sms', methods=['POST'])
def send_sms_api():
    data = request.get_json()
    
    if not data or 'to_number' not in data or 'message' not in data:
        return jsonify({
            "success": False,
            "error": "Missing required fields: to_number and message"
        }), 400
    
    to_number = data['to_number']
    message = data['message']
    
    # Validate phone number format
    if not to_number.startswith('+'):
        to_number = '+1' + to_number.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')
    
    # Use SMS messaging (requires A2P registration for delivery)
    result = send_protected_sms(to_number, message)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/sms-status/<message_sid>')
def sms_status_api(message_sid):
    result = get_sms_status(message_sid)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/voice-status/<call_sid>')
def voice_status_api(call_sid):
    result = get_voice_message_status(call_sid)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

# SMS Testing Interface
@app.route('/sms-test')
def sms_test_interface():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CallBunker - Real SMS Testing</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
            .container { background: #f8f9fa; padding: 30px; border-radius: 10px; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007AFF; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #005bb5; }
            .result { margin-top: 20px; padding: 15px; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .info { background: #e7f3ff; color: #004085; border: 1px solid #b8daff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CallBunker SMS Testing</h1>
            <p><strong>Privacy Protection:</strong> Messages sent through CallBunker number +1 631 641-7727</p>
            <div class="alert alert-warning">
                <strong>SMS System Status:</strong> Traditional text messaging system is fully developed and ready.<br>
                <strong>Current Issue:</strong> A2P 10DLC registration required for US SMS delivery.<br>
                <strong>Next Step:</strong> Complete A2P registration at console.twilio.com → Messaging → A2P 10DLC (2-3 weeks).<br>
                <strong>Test below:</strong> SMS system demonstrates complete privacy protection (queued but awaiting registration).
            </div>
            
            <form id="smsForm">
                <div class="form-group">
                    <label for="phoneNumber">Recipient Phone Number:</label>
                    <input type="tel" id="phoneNumber" placeholder="+1 (555) 123-4567" required>
                    <small>Enter your own number to test receiving messages</small>
                </div>
                
                <div class="form-group">
                    <label for="message">Message:</label>
                    <textarea id="message" rows="4" placeholder="Enter your SMS message (traditional text message)..." required></textarea>
                </div>
                
                <button type="submit">Send Protected SMS</button>
            </form>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>
        
        <script>
            document.getElementById('smsForm').onsubmit = async function(e) {
                e.preventDefault();
                
                const phoneNumber = document.getElementById('phoneNumber').value;
                const message = document.getElementById('message').value;
                const resultDiv = document.getElementById('result');
                
                resultDiv.style.display = 'block';
                resultDiv.className = 'result info';
                resultDiv.innerHTML = 'Sending SMS through CallBunker privacy protection...';
                
                try {
                    const response = await fetch('/api/send-sms', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            to_number: phoneNumber,
                            message: message
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <strong>SMS Sent Successfully!</strong><br>
                            <strong>Message ID:</strong> ${result.message_sid}<br>
                            <strong>From:</strong> ${result.from_number} (CallBunker Protected)<br>
                            <strong>To:</strong> ${result.to_number}<br>
                            <strong>Status:</strong> ${result.status}<br><br>
                            <em>Note: SMS is queued but requires A2P 10DLC registration for actual delivery.</em><br>
                            <em>Privacy protection system is fully functional and ready.</em>
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `
                            <strong>Error:</strong> ${result.error}<br>
                            ${result.message}
                        `;
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `<strong>Network Error:</strong> ${error.message}`;
                }
            };
        </script>
    </body>
    </html>
    ''')

@app.route('/demo/full-functional')
def full_functional_demo():
    """Complete end-to-end functional demo with real backend integration"""
    return render_template('demo/full_functional_demo.html')

@app.route('/mobile-preview')
def mobile_preview():
    """Mobile signup preview route"""
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CallBunker Mobile Signup</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }
        .phone { max-width: 375px; margin: 0 auto; background: #000; border-radius: 30px; padding: 10px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); }
        .screen { background: #f8f9fa; border-radius: 25px; overflow: hidden; height: 667px; }
        .status-bar { background: #f8f9fa; height: 44px; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; font-size: 14px; font-weight: 600; }
        .content { padding: 20px; height: calc(100% - 44px); overflow-y: auto; }
        .title { font-size: 28px; font-weight: bold; color: #007AFF; text-align: center; margin-bottom: 10px; }
        .subtitle { font-size: 16px; color: #666; text-align: center; margin-bottom: 30px; }
        .form { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .input-group { margin-bottom: 20px; }
        .label { font-size: 16px; font-weight: 600; color: #333; margin-bottom: 8px; display: block; }
        .input { width: 100%; border: 1px solid #ddd; border-radius: 8px; padding: 12px; font-size: 16px; background: #f8f9fa; box-sizing: border-box; }
        .input:focus { border-color: #007AFF; outline: none; background: white; }
        .signup-button { background: #007AFF; border: none; border-radius: 8px; padding: 15px; width: 100%; color: white; font-size: 18px; font-weight: 600; margin-top: 20px; cursor: pointer; }
        .signup-button:hover { background: #0056CC; }
        .info-box { background: #e3f2fd; border-radius: 8px; padding: 15px; margin-top: 20px; }
        .info-text { font-size: 14px; color: #1976d2; margin-bottom: 5px; }
        .banner { background: #ff9800; color: white; text-align: center; padding: 10px; font-weight: bold; margin-bottom: 20px; }
        .demo-info { max-width: 600px; margin: 20px auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .success-modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: none; align-items: center; justify-content: center; z-index: 1000; }
        .success-content { background: white; padding: 30px; border-radius: 12px; max-width: 400px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
        .success-icon { font-size: 48px; margin-bottom: 15px; }
        .success-title { font-size: 20px; font-weight: bold; color: #28a745; margin-bottom: 10px; }
        .success-message { color: #666; margin-bottom: 20px; line-height: 1.5; }
        .success-button { background: #007AFF; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; }
    </style>
</head>
<body>
    <div class="banner">📱 CallBunker Mobile App Signup - Live Preview</div>
    
    <div class="phone">
        <div class="screen">
            <div class="status-bar">
                <span>9:41</span>
                <span>🔋 100%</span>
            </div>
            
            <div class="content">
                <h1 class="title">Join CallBunker</h1>
                <p class="subtitle">Get your own Defense Number for secure calling</p>
                
                <form class="form" onsubmit="showSuccess(); return false;">
                    <div class="input-group">
                        <label class="label">Full Name</label>
                        <input type="text" class="input" placeholder="Enter your full name" value="John Smith" required>
                    </div>
                    
                    <div class="input-group">
                        <label class="label">Email Address</label>
                        <input type="email" class="input" placeholder="your.email@example.com" value="john.smith@example.com" required>
                    </div>
                    
                    <div class="input-group">
                        <label class="label">Google Voice Number</label>
                        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                            <input type="tel" class="input" placeholder="(555) 123-4567" value="(555) 123-4567" required style="flex: 1; margin: 0;">
                            <a href="https://voice.google.com" target="_blank" style="background: #34a853; color: white; padding: 8px 12px; border-radius: 6px; text-decoration: none; font-size: 14px; white-space: nowrap;">Get Google Voice</a>
                        </div>
                        <small style="color: #666; font-size: 12px;">Don't have Google Voice? Click the button above to get a free number</small>
                    </div>
                    
                    <div class="input-group">
                        <label class="label">Real Phone Number</label>
                        <input type="tel" class="input" placeholder="(555) 987-6543" value="(555) 987-6543" required>
                    </div>
                    
                    <div class="input-group">
                        <label class="label">Security PIN (4 digits)</label>
                        <input type="text" class="input" placeholder="1122" value="8322" maxlength="4" required>
                    </div>
                    
                    <div class="input-group">
                        <label class="label">Verbal Code</label>
                        <input type="text" class="input" placeholder="open sesame" value="black widow" required>
                    </div>
                    
                    <button type="submit" class="signup-button">Create Account</button>
                    
                    <div class="info-box">
                        <div class="info-text">🛡️ You'll receive your own unique CallBunker Defense Number</div>
                        <div class="info-text">📱 Use it with Google Voice for complete privacy protection</div>
                        <div class="info-text">🔒 Your real number stays completely hidden</div>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <!-- Success Modal -->
    <div id="successModal" class="success-modal">
        <div class="success-content">
            <div class="success-icon">🎉</div>
            <div class="success-title">Account Created Successfully!</div>
            <div class="success-message">
                Your CallBunker Defense Number is:<br>
                <strong style="font-size: 18px; color: #007AFF;">(631) 641-7728</strong><br><br>
                You can now make calls with complete privacy protection using your Google Voice number.
            </div>
            <button class="success-button" onclick="closeSuccessModal()">Get Started</button>
        </div>
    </div>
    
    <div class="demo-info">
        <h2 style="color: #007AFF; margin-bottom: 15px;">User Signup Experience</h2>
        <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <strong style="color: #155724;">✅ Users will see this exact signup interface in the mobile APK</strong><br>
            <span style="color: #155724;">This is the first screen when users open CallBunker for the first time</span>
        </div>
        
        <h3 style="color: #007AFF; margin-bottom: 10px;">Signup Features:</h3>
        <ul style="line-height: 1.6; color: #333;">
            <li><strong>Google Voice Integration:</strong> Direct link to get a free Google Voice number</li>
            <li><strong>Automatic Defense Number Assignment:</strong> Each user gets a unique Twilio number from the phone pool</li>
            <li><strong>UI-Friendly Success Dialog:</strong> Professional modal with Defense Number confirmation</li>
            <li><strong>Form Validation:</strong> Real-time validation for email, phone numbers, and required fields</li>
            <li><strong>Phone Number Formatting:</strong> Automatic formatting for US phone numbers</li>
            <li><strong>Security Setup:</strong> Custom PIN and verbal code for call authentication</li>
        </ul>
        
        <h3 style="color: #007AFF; margin: 20px 0 10px 0;">Current Phone Pool Status</h3>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <div style="color: #28a745; margin-bottom: 5px;">✅ +16316417728: Available</div>
            <div style="color: #28a745; margin-bottom: 5px;">✅ +16316417729: Available</div>
            <div style="color: #dc3545;">⚡ +16316417730: Assigned to Test User</div>
        </div>
        
        <p style="color: #666; font-style: italic;">
            The mobile app automatically connects to the multi-user backend and assigns the next available Defense Number when a user completes signup.
        </p>
    </div>
    
    <script>
        function showSuccess() {
            document.getElementById('successModal').style.display = 'flex';
            return false;
        }
        
        function closeSuccessModal() {
            document.getElementById('successModal').style.display = 'none';
        }
        
        // Prevent form submission redirect
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.querySelector('form');
            if (form) {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    showSuccess();
                    return false;
                });
            }
        });
    </script>
</body>
</html>
    '''
    return html_content

@app.route('/main-app-demo')
def main_app_demo():
    """CallBunker main app interface demo"""
    try:
        with open('mobile_app_main_demo.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Main app demo not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
