# CallBunker Android Testing Without Android Studio

## Alternative Testing Methods

### Option 1: Expo Development Build (Recommended)

#### Setup
```bash
# Install Expo CLI
npm install -g @expo/cli

# Create expo configuration
cd mobile_app
npx create-expo-app --template
```

#### Convert to Expo
```bash
# Install Expo dependencies
npm install expo
npx install-expo-modules@latest

# Create app.json
cat > app.json << 'EOF'
{
  "expo": {
    "name": "CallBunker",
    "slug": "callbunker-mobile",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "platforms": ["ios", "android"],
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#FFFFFF"
      },
      "permissions": [
        "android.permission.CALL_PHONE",
        "android.permission.MANAGE_OWN_CALLS",
        "android.permission.READ_PHONE_STATE"
      ]
    },
    "plugins": [
      [
        "expo-dev-client"
      ]
    ]
  }
}
EOF

# Start development server
npx expo start
```

### Option 2: React Native CLI with Physical Device

#### Prerequisites
```bash
# Install React Native CLI
npm install -g react-native-cli

# Install Java (required for Android builds)
# On macOS with Homebrew:
brew install openjdk@11

# On Ubuntu/Debian:
sudo apt install openjdk-11-jdk

# On Windows: Download OpenJDK 11
```

#### Setup Android SDK (Command Line)
```bash
# Download Android command line tools
mkdir -p $HOME/android-sdk
cd $HOME/android-sdk
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip

# Setup environment
export ANDROID_HOME=$HOME/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/bin:$ANDROID_HOME/platform-tools

# Install required packages
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"
```

#### Build and Test
```bash
cd mobile_app

# Connect Android device via USB
# Enable USB debugging in Developer Options

# Check device connection
adb devices

# Build and install
npx react-native run-android
```

### Option 3: Cloud-Based Testing

#### Using BrowserStack App Live
1. Visit https://app-live.browserstack.com/
2. Upload APK file (build with Option 2)
3. Test on real Android devices in browser

#### Using Firebase Test Lab
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Upload APK for testing
firebase test android run \
  --app path/to/your.apk \
  --device model=Pixel2,version=28
```

### Option 4: Web-Based Development

#### React Native Web
```bash
cd mobile_app

# Install React Native Web
npm install react-native-web

# Create web configuration
cat > webpack.config.js << 'EOF'
const createExpoWebpackConfigAsync = require('@expo/webpack-config');

module.exports = async function (env, argv) {
  const config = await createExpoWebpackConfigAsync(env, argv);
  return config;
};
EOF

# Start web development server
npm run web
```

### Option 5: Replit Mobile Development

Since you're on Replit, let's create a web-based mobile testing environment:

```bash
# Create mobile web version
cd mobile_app

# Install react-device-detect for mobile simulation
npm install react-device-detect

# Create mobile web entry point
cat > web.js << 'EOF'
import {AppRegistry} from 'react-native';
import App from './App';

AppRegistry.registerComponent('CallBunkerMobile', () => App);
AppRegistry.runApplication('CallBunkerMobile', {
  rootTag: document.getElementById('root'),
});
EOF
```

## Testing Strategies

### 1. Native Calling Simulation
Since native calling requires actual Android hardware, create a simulation mode:

```javascript
// In CallBunkerNative.js, add simulation mode
async makeCall(targetNumber) {
  if (Platform.OS === 'web' || this.simulationMode) {
    // Simulate call flow for testing
    console.log(`[SIMULATION] Calling ${targetNumber}`);
    
    // Show what would happen
    Alert.alert(
      'Call Simulation',
      `Would call: ${targetNumber}\nCaller ID: ${this.googleVoiceNumber}\nStatus: Success`
    );
    
    return {
      callLogId: Date.now(),
      targetNumber,
      callerIdShown: this.googleVoiceNumber,
      status: 'simulated'
    };
  }
  
  // Normal native calling code...
}
```

### 2. UI/UX Testing
Test all app screens and functionality:
- Navigation between screens
- Form inputs and validation
- API integration (mock responses)
- State management
- Error handling

### 3. API Integration Testing
```bash
# Test backend API endpoints
curl -X POST https://your-replit-url.replit.app/api/users/1/call_direct \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+15551234567"}'
```

## Quick Start Commands

### For Web Testing:
```bash
cd mobile_app
npm install
npm install react-native-web
npm start
# Open http://localhost:19006 in mobile browser
```

### For Physical Device (no Android Studio):
```bash
cd mobile_app
npm install

# Connect Android device with USB debugging enabled
adb devices

# Install and run
npx react-native run-android
```

### For Expo (Easiest):
```bash
cd mobile_app
npm install -g @expo/cli
npx create-expo-app --template
# Scan QR code with Expo Go app on your phone
```

## Recommended Approach for Your Situation

Given that Android Studio isn't available:

1. **Start with Expo** - Easiest to test on real devices
2. **Use web browser** for UI/UX development
3. **Set up simulation mode** for native calling features
4. **Use physical device** when ready for real testing

The CallBunker app will work great with these alternative approaches, and you can still test all the core functionality including the protected dialer interface and privacy features.

Which option would you like to try first?