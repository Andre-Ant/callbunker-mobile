# Quick Start Guide

Get CallBunker mobile app running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:

```bash
# Check Node.js version (need 18+)
node --version

# Check npm
npm --version

# For Android development
java -version  # Need JDK 17+
```

## Step-by-Step Setup

### 1. Clone & Install (2 minutes)

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/callbunker-mobile.git
cd callbunker-mobile

# Install dependencies
npm install

# This installs:
# - React Native
# - Navigation libraries  
# - Expo SDK
# - All required packages
```

### 2. Configure Backend (1 minute)

Open `src/services/CallBunkerContext.js` and update line 14:

```javascript
// REPLACE THIS:
const API_BASE_URL = 'http://localhost:5000';

// WITH YOUR DEPLOYED BACKEND:
const API_BASE_URL = 'https://your-callbunker-backend.repl.co';
```

**Important:** Use your actual Replit deployment URL or production backend URL.

### 3. Run on Android (2 minutes)

```bash
# Terminal 1 - Start Metro bundler
npm start

# Terminal 2 - Run on Android device/emulator
npm run android

# App will automatically install and launch!
```

### 4. Test the App

1. **Signup Screen** appears first
   - Enter name and email
   - Tap "Create Account"
   - You'll be assigned a CallBunker number automatically

2. **Home Screen** shows your protection status
   - See your Defense Number
   - View protection features

3. **Protected Dialer**
   - Tap Dialer tab
   - Enter any phone number
   - Tap "Protected Call"
   - Native dialer opens with target number
   - Recipient sees your CallBunker number as caller ID

4. **Call History**
   - View all protected calls
   - See caller ID shown for each call

## Running on iOS

```bash
# Install CocoaPods dependencies (one-time)
cd ios
pod install
cd ..

# Run on iOS simulator
npm run ios

# Or open in Xcode
open ios/CallBunker.xcworkspace
```

## Common Issues & Fixes

### ❌ "Cannot connect to Metro"

```bash
# Clear cache and restart
npm start -- --reset-cache
```

### ❌ "Backend connection failed"

- Check `API_BASE_URL` is correct
- Verify backend is deployed and running
- Test backend URL in browser

### ❌ "Build failed"

```bash
# Clean Android build
cd android
./gradlew clean
cd ..
npm run android
```

### ❌ "Dependencies not installing"

```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

Once app is running:

### Test Full Flow
1. Complete signup to get CallBunker number
2. Make a protected call
3. Check call history
4. Add trusted contacts
5. Send anonymous message

### Build APK for Distribution

See `APK_BUILD_GUIDE.md` for detailed instructions on:
- Building release APK
- Code signing
- Google Play submission

### Customize Your App

Edit these files:
- `app.json` - App name, version, icons
- `assets/` - Replace icon.png and splash.png
- `src/i18n/translations.js` - Add/modify languages

## Development Mode Features

The app includes helpful development features:

```javascript
// In CallBunkerNative.js
getMockCallHistory()  // Returns sample call data for UI testing

// In CallBunkerContext.js  
// Set to true for offline development
const USE_MOCK_DATA = false;
```

## Verification Checklist

Before deploying to production:

- [ ] Backend URL configured correctly
- [ ] App builds without errors
- [ ] Signup flow works (creates user + assigns number)
- [ ] Protected calling works (native dialer opens)
- [ ] Call history displays correctly
- [ ] Trusted contacts can be added/removed
- [ ] Messages can be sent
- [ ] Settings language selection works
- [ ] Icons and splash screen customized

## Performance Tips

### Speed Up Development

```bash
# Use development build (faster)
npm run android -- --variant=debug

# Enable fast refresh (automatic in dev mode)
# Shake device → Enable Fast Refresh
```

### Reduce APK Size

```bash
# Enable Proguard in android/app/build.gradle
minifyEnabled true
shrinkResources true
```

## Getting Help

- **App crashes:** Check logs with `npm start` (press 'd' for dev menu)
- **Backend issues:** See backend repo's `PROVISIONING_GUIDE.md`
- **Build problems:** Check `android/build.gradle` configuration
- **Calling not working:** Ensure on physical device (not web preview)

---

**You're ready to go!** The app should now be running on your device. Test the signup flow and make your first protected call.

For production deployment, proceed to `APK_BUILD_GUIDE.md`.
