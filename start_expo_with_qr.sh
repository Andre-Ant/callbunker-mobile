#!/bin/bash
echo "Starting CallBunker Expo Server..."
echo "=================================="
cd /home/runner/workspace/mobile_app

echo "To see QR code for device testing:"
echo "1. Run this command in a new terminal:"
echo "   cd mobile_app && npx expo start"
echo ""
echo "2. The QR code will appear in the terminal output"
echo "3. Scan with Expo Go app on your device"
echo ""
echo "Alternative: Testing in web browser..."
npx expo start --web --port 8082