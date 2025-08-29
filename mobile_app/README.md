# CallBunker Mobile App

Intelligent Communication Security Platform - Native Mobile Application

## Overview

CallBunker Mobile provides advanced call screening and privacy protection through native device calling with caller ID spoofing. This React Native application integrates with the CallBunker backend to deliver cost-effective, secure communication.

## Features

- **Protected Dialer**: Make calls with your Google Voice number as caller ID
- **Call History**: Track all protected calls with detailed information
- **Trusted Contacts**: Manage whitelist for call screening bypass
- **Native Calling**: Zero per-minute costs using device's built-in calling
- **Privacy Protection**: Your real number stays completely hidden

## Architecture

### Core Technologies
- **React Native 0.72.6**: Cross-platform mobile framework
- **React Navigation 6**: Navigation and routing
- **Native Modules**: iOS CallKit and Android TelecomManager integration
- **Context API**: Global state management

### Native Integration
- **iOS**: CallKit framework for native calling with caller ID spoofing
- **Android**: TelecomManager and PhoneAccount system for call management
- **Permissions**: Automatic permission handling for call features

## Installation

### Prerequisites
- Node.js 16+
- React Native CLI
- Xcode (for iOS development)
- Android Studio (for Android development)

### Setup
```bash
# Install dependencies
npm install

# iOS setup
cd ios && pod install && cd ..

# Android setup - ensure Android SDK is configured
```

### Configuration
1. Update API URL in `src/services/CallBunkerContext.js`
2. Configure native modules for your project
3. Set up permissions in platform manifest files

## Development

### Start Metro bundler
```bash
npm start
```

### Run on iOS
```bash
npm run ios
```

### Run on Android
```bash
npm run android
```

### Build for Production

#### iOS
```bash
npm run build:ios
```

#### Android
```bash
npm run build:android
```

## Project Structure

```
mobile_app/
├── src/
│   ├── screens/              # Main app screens
│   │   ├── HomeScreen.js     # Dashboard and overview
│   │   ├── DialerScreen.js   # Protected dialer interface
│   │   ├── CallHistoryScreen.js  # Call history management
│   │   ├── ContactsScreen.js # Trusted contacts management
│   │   ├── SettingsScreen.js # App configuration
│   │   └── CallLogDetailScreen.js # Individual call details
│   └── services/             # Core services
│       ├── CallBunkerContext.js   # Global state management
│       └── CallBunkerNative.js    # Native calling integration
├── ios/                      # iOS native code
├── android/                  # Android native code
└── App.js                    # Main app component
```

## Native Modules

### iOS Integration
The app uses CallKit for iOS native calling:
- `CallManager.swift`: Main iOS native module
- `CallManager.m`: React Native bridge
- Handles caller ID spoofing and call management

### Android Integration
Uses TelecomManager for Android calling:
- `CallManagerModule.java`: Main Android native module
- `CallConnectionService.java`: Connection service for call handling
- Manages phone accounts and caller ID configuration

## API Integration

### CallBunker Backend
- **Base URL**: Configure in `CallBunkerContext.js`
- **Endpoints**: 
  - `/api/users/{id}/call_direct` - Initiate native call
  - `/api/users/{id}/calls/{id}/status` - Get call status
  - `/api/users/{id}/calls/{id}/complete` - Complete call logging

### Authentication
- Uses user ID for API calls
- No complex auth required for MVP
- Future: JWT token authentication

## Privacy & Security

### Number Protection
- Real phone number never exposed
- Google Voice number shown as caller ID
- Complete privacy protection for outgoing calls

### Data Storage
- Local storage for app settings
- Call history cached locally
- No sensitive data stored on device

### Permissions
- **iOS**: Microphone access for calls
- **Android**: CALL_PHONE permission for native calling
- Automatic permission request handling

## Cost Benefits

### Traditional VoIP Approach
- Setup: $5,000-10,000
- Monthly: $20-50 per 1000 calls
- Annual: $5,240-10,600

### CallBunker Native Approach
- Setup: $2,000-5,000
- Monthly: $0 (carrier rates only)
- Annual: $2,000-5,000

**Savings: ~$3,000-5,000 per year**

## Testing

### Device Testing
```javascript
// Test native calling support
const isSupported = await callBunker.isNativeCallingSupported();
console.log('Native calling supported:', isSupported);

// Test permissions
const hasPermissions = await callBunker.requestCallPermissions();
console.log('Permissions granted:', hasPermissions);
```

### Call Flow Testing
1. Open dialer screen
2. Enter test phone number
3. Verify call configuration
4. Test native calling initiation
5. Verify caller ID spoofing

## Troubleshooting

### Common Issues

**Caller ID not showing:**
- Check carrier support for caller ID modification
- Verify native module integration
- Test with different target numbers

**Native calling not working:**
- Verify permissions are granted
- Check device telephony capabilities
- Ensure native modules are properly linked

**API connection failed:**
- Verify backend API URL configuration
- Check network connectivity
- Validate API endpoints

## Deployment

### App Store (iOS)
1. Configure signing and provisioning
2. Build release version
3. Upload to App Store Connect
4. Submit for review

### Google Play (Android)
1. Generate signed APK
2. Upload to Google Play Console
3. Configure store listing
4. Publish to production

## Support

For development questions:
1. Check the troubleshooting section
2. Review native module documentation
3. Test with CallBunker web demo
4. Contact development team

## License

Copyright © 2025 CallBunker. All rights reserved.