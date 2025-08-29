# CallBunker Android Testing Guide

## Prerequisites

### 1. Install Android Development Tools
```bash
# Install Android Studio
# Download from: https://developer.android.com/studio

# Install Java Development Kit (JDK 11 or higher)
# On macOS with Homebrew:
brew install openjdk@11

# On Ubuntu/Debian:
sudo apt install openjdk-11-jdk

# On Windows: Download from Oracle or use OpenJDK
```

### 2. Configure Environment Variables
Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export ANDROID_HOME=$HOME/Library/Android/sdk  # macOS
# export ANDROID_HOME=$HOME/Android/Sdk        # Linux
# export ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk  # Windows

export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools/bin

export JAVA_HOME=/Library/Java/JavaVirtualMachines/openjdk-11.jdk/Contents/Home  # macOS
# export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  # Linux
```

### 3. Install Android SDK Components
Open Android Studio and install:
- Android SDK Platform 33
- Android SDK Build-Tools 33.0.0
- Android Emulator
- Intel x86 Emulator Accelerator (HAXM installer)

## Setup CallBunker Mobile for Android

### 1. Navigate to Project Directory
```bash
cd mobile_app
```

### 2. Install Node.js Dependencies
```bash
npm install
```

### 3. Update API Configuration
Edit `src/services/CallBunkerContext.js`:
```javascript
const initialState = {
  apiUrl: 'https://your-replit-url.replit.app', // Replace with your Replit URL
  userId: 1, // Your user ID
  // ... rest of config
};
```

## Testing Options

### Option 1: Android Emulator (Recommended for Development)

#### Create Android Virtual Device (AVD)
```bash
# Open Android Studio
# Go to Tools > AVD Manager
# Click "Create Virtual Device"
# Choose a device (e.g., Pixel 4)
# Select API Level 33 (Android 13)
# Click "Finish"
```

#### Start Emulator
```bash
# Start emulator from command line
emulator @Pixel_4_API_33

# Or start from Android Studio AVD Manager
```

#### Run CallBunker App
```bash
# Start Metro bundler
npm start

# In another terminal, build and run Android app
npm run android
```

### Option 2: Physical Android Device

#### Enable Developer Options
1. Go to Settings > About phone
2. Tap "Build number" 7 times
3. Go back to Settings > Developer options
4. Enable "USB debugging"

#### Connect Device
```bash
# Connect via USB cable
# Accept USB debugging prompt on device

# Verify device is connected
adb devices
```

#### Run App on Device
```bash
npm run android
```

## Testing Native Calling Features

### 1. Grant Permissions
When the app launches, it will request:
- Phone permissions (CALL_PHONE)
- Manage own calls (MANAGE_OWN_CALLS)

Grant these permissions for full functionality.

### 2. Test Call Flow
1. Open CallBunker app
2. Go to "Protected Dialer" tab
3. Enter a test phone number
4. Tap the green call button
5. Confirm the protected call dialog

### 3. Expected Behavior
- App will show call configuration
- Native Android dialer should open
- Your Google Voice number will be shown as caller ID
- Real number stays hidden

### 4. Verify Features
- **Home Screen**: Privacy status and call statistics
- **Dialer**: Native calling with caller ID spoofing
- **History**: Call logs with privacy information
- **Contacts**: Trusted contacts management
- **Settings**: App configuration and testing tools

## Troubleshooting

### Common Issues

#### Metro bundler won't start
```bash
# Clear Metro cache
npx react-native start --reset-cache
```

#### Build errors
```bash
# Clean and rebuild
cd android
./gradlew clean
cd ..
npm run android
```

#### Native module not found
```bash
# Ensure native modules are linked
cd android
./gradlew clean
cd ..
npm install
npm run android
```

#### Permissions denied
- Manually grant permissions in Android Settings > Apps > CallBunker > Permissions
- Enable Phone and Microphone permissions

#### Emulator performance issues
- Increase emulator RAM allocation in AVD settings
- Enable hardware acceleration (HAXM/Hyper-V)
- Use a newer API level (33+)

### Debug Native Calling
```bash
# Enable React Native debugging
# Open app, shake device/press Ctrl+M
# Select "Debug JS Remotely"
# Check Chrome DevTools console
```

### Check Device Logs
```bash
# View Android system logs
adb logcat | grep CallBunker

# Filter for call-related logs
adb logcat | grep -E "(CallManager|TelecomManager|CallConnection)"
```

## Production Testing

### Test Call Scenarios
1. **Outgoing calls**: Verify caller ID spoofing works
2. **Permission handling**: Test first-time permission requests
3. **Network connectivity**: Test with/without internet
4. **Call completion**: Verify call logging works
5. **Contact management**: Test trusted contacts features

### Carrier Compatibility
Test with different carriers to verify:
- Caller ID spoofing support
- Native calling functionality
- Permission requirements

### Performance Testing
- Test on different Android versions (API 21+)
- Test on various device specifications
- Monitor battery usage during calls
- Check memory usage and performance

## Deployment Preparation

### Generate Signed APK
```bash
# Generate release keystore (one-time setup)
keytool -genkey -v -keystore callbunker-release-key.keystore -alias callbunker -keyalg RSA -keysize 2048 -validity 10000

# Build release APK
cd android
./gradlew assembleRelease

# APK will be generated at:
# android/app/build/outputs/apk/release/app-release.apk
```

### Test Release Build
```bash
# Install release APK on device
adb install android/app/build/outputs/apk/release/app-release.apk
```

## Next Steps

After successful Android testing:
1. Test on multiple Android devices and versions
2. Verify carrier compatibility
3. Test call quality and reliability
4. Prepare for Google Play Store submission
5. Set up crash reporting and analytics

## Support

For Android-specific issues:
1. Check React Native Android documentation
2. Review Android Telecom API documentation
3. Test native modules separately
4. Use Android Studio debugger for native code

The CallBunker Android app provides complete privacy protection with native calling integration, eliminating per-minute charges while maintaining caller ID spoofing capabilities.