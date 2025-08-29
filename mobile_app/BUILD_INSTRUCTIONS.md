# CallBunker Mobile - Build Instructions

## Quick Start for Real Device Testing

### Option 1: Expo Go (Fastest - No Build Required)
1. Install "Expo Go" app on your phone from App Store/Play Store
2. Run: `cd mobile_app && npx expo start`
3. Scan QR code with Expo Go to test instantly

### Option 2: Development Build (Full Features)
1. Install Expo CLI: `npm install -g @expo/cli`
2. Install EAS CLI: `npm install -g eas-cli`
3. Login to Expo: `npx expo login`
4. Initialize EAS: `eas init`
5. Build for Android: `eas build --platform android --profile preview`
6. Download APK when build completes

### Option 3: Local APK Build
1. Run: `cd mobile_app && npx expo export --platform android`
2. Use Android Studio or gradle to build APK
3. Install APK directly on device

## Current App Features
- Protected dialer with Google Voice integration
- Native messaging interface
- Call screening simulation
- Privacy protection demonstration
- Mobile-optimized UI

## Testing on Device
- Real calling functionality requires native modules
- Messaging works with proper Google Voice integration
- Current version shows full UI/UX experience