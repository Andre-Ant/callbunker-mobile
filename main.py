from app import app
from flask import send_from_directory, render_template_string, request, jsonify
import os
from sms_testing import send_protected_sms, get_sms_status
# from sms_verify import send_callbunker_verification  # Disabled for now

# Enable CORS headers manually
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Add main home route
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

# Add mobile web testing route
@app.route('/mobile')
def mobile_demo():
    try:
        with open('mobile_app/web/index.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return render_template_string('''
        <h1>Mobile Demo Loading...</h1>
        <p>Setting up CallBunker mobile demo...</p>
        <script>window.location.reload();</script>
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
            <h1>CallBunker Real SMS Testing</h1>
            <p><strong>Privacy Protection:</strong> Messages sent through CallBunker number +1 631 641-7727</p>
            <div class="alert alert-success">
                <strong>✅ SMS Ready:</strong> Your phone number is verified! CallBunker SMS should work immediately.<br>
                <strong>Test below:</strong> Send a message to +1 508 638-8084 to see privacy protection in action!
            </div>
            
            <form id="smsForm">
                <div class="form-group">
                    <label for="phoneNumber">Recipient Phone Number:</label>
                    <input type="tel" id="phoneNumber" placeholder="+1 (555) 123-4567" required>
                    <small>Enter your own number to test receiving messages</small>
                </div>
                
                <div class="form-group">
                    <label for="message">Message:</label>
                    <textarea id="message" rows="4" placeholder="Type your test message here..." required></textarea>
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
                            <em>Status "queued" means your message is being processed for delivery.</em><br>
                            Check your phone for the message with CallBunker privacy protection!
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
