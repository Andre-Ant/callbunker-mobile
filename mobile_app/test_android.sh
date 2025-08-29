#!/bin/bash

# CallBunker Android Testing Script
# Quick setup and testing for Android development

echo "🔧 CallBunker Android Testing Setup"
echo "=================================="

# Check if Android SDK is available
if [ -z "$ANDROID_HOME" ]; then
    echo "❌ ANDROID_HOME not set. Please install Android Studio and set ANDROID_HOME"
    echo "   Example: export ANDROID_HOME=\$HOME/Library/Android/sdk"
    exit 1
fi

# Check if Node.js dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Update API URL in context (replace with your Replit URL)
echo "🔗 Updating API configuration..."
REPLIT_URL="your-replit-url.replit.app"
if [ ! -z "$1" ]; then
    REPLIT_URL="$1"
fi

# Create a temporary config update
cat > temp_config.js << EOF
// Update the API URL in CallBunkerContext.js
const fs = require('fs');
const path = './src/services/CallBunkerContext.js';
let content = fs.readFileSync(path, 'utf8');
content = content.replace(
    "apiUrl: 'https://your-callbunker-api.com'",
    "apiUrl: 'https://$REPLIT_URL'"
);
fs.writeFileSync(path, content);
console.log('✅ API URL updated to: https://$REPLIT_URL');
EOF

node temp_config.js
rm temp_config.js

# Check for connected Android devices
echo "📱 Checking for Android devices..."
adb devices -l

# Start Metro bundler in background
echo "🚀 Starting Metro bundler..."
npm start &
METRO_PID=$!

# Wait a moment for Metro to start
sleep 5

echo ""
echo "🎯 Android Testing Options:"
echo "1. Physical Device: npm run android"
echo "2. Emulator: emulator @YourAVD && npm run android"
echo ""
echo "📋 Testing Checklist:"
echo "✓ Grant phone permissions when prompted"
echo "✓ Test protected dialer functionality"
echo "✓ Verify caller ID spoofing works"
echo "✓ Check call history tracking"
echo "✓ Test trusted contacts management"
echo ""
echo "🐛 Debugging:"
echo "- View logs: adb logcat | grep CallBunker"
echo "- Reset cache: npx react-native start --reset-cache"
echo "- Shake device for debug menu"
echo ""
echo "Metro bundler is running (PID: $METRO_PID)"
echo "Run 'npm run android' in another terminal to start the app"