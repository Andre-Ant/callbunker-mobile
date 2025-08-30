from app import app
from flask import send_from_directory, render_template_string
import os

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
