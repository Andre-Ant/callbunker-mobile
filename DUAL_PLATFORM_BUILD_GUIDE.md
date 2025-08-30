# CallBunker - Android & iOS Build Guide

## Yes! Same Project Works for Both Platforms ✅

Your CallBunker project is built with React Native/Expo, which means **one codebase = both Android and iOS apps**.

## Build Commands for Both Platforms

### Android APK
```bash
npx eas build --platform android --profile preview
```

### iOS App (IPA)
```bash
npx eas build --platform ios --profile preview
```

### Both at Once
```bash
npx eas build --platform all --profile preview
```

## Platform-Specific Requirements

### Android (Easier)
- **Output:** APK file you can install directly
- **Requirements:** Just your Expo account
- **Install:** Enable "Unknown Sources" and install APK
- **Time:** 5-10 minutes

### iOS (More Complex)
- **Output:** IPA file for App Store or TestFlight
- **Requirements:** 
  - Apple Developer Account ($99/year)
  - Device UUIDs for testing
- **Install:** TestFlight or App Store distribution
- **Time:** 10-15 minutes

## Updated Configuration

I've configured your project for both platforms:

**iOS Permissions Added:**
- Contact access for secure calling
- Microphone access for phone calls  
- Phone access description

**Build Profiles:**
- Android: Direct APK installation
- iOS: TestFlight/App Store ready

## Developer Instructions

**For Android + iOS:**
```bash
cd callbunker-build
npx eas login
npx eas build --platform all --profile preview
```

**For Android Only:**
```bash
npx eas build --platform android --profile preview
```

**For iOS Only:**
```bash
npx eas build --platform ios --profile preview
```

## What Your Developer Needs

### For Android:
- Your Expo account credentials
- 30 minutes of time

### For iOS (Additional):
- Apple Developer Account access
- iOS device UUIDs for testing
- App Store Connect access (for distribution)

## App Features (Same on Both Platforms)

- Native device calling
- Caller ID spoofing through Google Voice
- Contact management
- Privacy protection
- Professional CallBunker interface
- SMS integration (ready for A2P registration)

## Cost Breakdown

**Free:**
- Expo account
- Android APK generation
- Testing on Android devices

**Paid:**
- Apple Developer Account: $99/year (required for iOS)
- App Store distribution (included in developer account)

## Recommendation

**Start with Android first:**
1. Build and test Android APK (free, immediate)
2. Verify all features work correctly
3. Then build iOS version with Apple Developer Account

Your single CallBunker project will create professional apps for both platforms with identical features and functionality!