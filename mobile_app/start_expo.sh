#!/bin/bash
cd /home/runner/workspace/mobile_app
echo "Starting CallBunker Mobile App..."
echo "Metro Bundler running on: http://localhost:8082"
echo ""
echo "To test on your device:"
echo "1. Download 'Expo Go' app from your app store"
echo "2. Open the app and scan QR code (if available)"
echo "3. Or manually enter: exp://192.168.1.100:8082"
echo ""
echo "Web testing: http://localhost:8082"
echo ""
npx expo start --port 8082 --web