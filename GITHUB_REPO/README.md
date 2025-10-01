# CallBunker Mobile App

**Intelligent Communication Security Platform** - Native mobile calling with privacy protection, call screening, and caller ID spoofing.

## Features

✅ **Protected Dialer** - Make calls with CallBunker number as caller ID  
✅ **Native Device Calling** - Uses React Native's built-in Linking API (no VoIP complexity)  
✅ **Multi-language Support** - 10+ languages with automatic detection  
✅ **Call History** - Track all protected calls with detailed logs  
✅ **Trusted Contacts** - Manage whitelist with custom PINs  
✅ **Anonymous Messaging** - Send SMS from your CallBunker number  
✅ **Automatic Signup** - Each user gets unique CallBunker number from pool  

## Architecture

### Calling Flow

```
User initiates call → CallBunker API → Twilio Number Assigned
                                    ↓
Native Device Dialer Opens → Target receives call with CallBunker caller ID
```

**Key Implementation:**
- No Twilio Voice SDK required
- No VoIP/WebRTC complexity  
- Uses standard React Native `Linking.openURL('tel:...')`
- Twilio number shown to recipient (not traditional bridge calls)

### Backend Integration

This app connects to your deployed CallBunker backend:

- **Base URL:** Set in `src/services/CallBunkerContext.js`
- **Multi-user API:** `/multi/` endpoints for user isolation
- **Phone Pool:** Automatic number assignment from Twilio pool

## Prerequisites

- **Node.js** 18+ and npm/yarn
- **React Native development environment:**
  - For Android: Android Studio, JDK 17+
  - For iOS: macOS with Xcode 14+
- **Backend:** Deployed CallBunker backend with phone pool configured

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/callbunker-mobile.git
cd callbunker-mobile
```

### 2. Install Dependencies

```bash
npm install
# or
yarn install
```

### 3. Configure Backend URL

Edit `src/services/CallBunkerContext.js`:

```javascript
// Line 14 - Update with your backend URL
const API_BASE_URL = 'https://your-backend.repl.co';
```

### 4. Run on Device/Emulator

#### Android

```bash
# Start Metro bundler
npm start

# In another terminal, run Android
npm run android
```

#### iOS (macOS only)

```bash
# Install CocoaPods dependencies
cd ios && pod install && cd ..

# Run on iOS
npm run ios
```

### 5. Web Preview (Development Only)

```bash
npm run web
```

**Note:** Calling features don't work on web (requires native device)

## Building APK for Android

### Method 1: Using Expo (Recommended)

```bash
# Install EAS CLI globally
npm install -g eas-cli

# Login to Expo (create account at expo.dev)
eas login

# Configure build
eas build:configure

# Build APK
eas build --platform android --profile preview

# Download APK when complete (link provided in console)
```

### Method 2: Using React Native CLI

```bash
# Generate release APK
cd android
./gradlew assembleRelease

# APK location:
# android/app/build/outputs/apk/release/app-release.apk
```

### Method 3: Using Android Studio

1. Open `android/` folder in Android Studio
2. Select **Build → Build Bundle(s) / APK(s) → Build APK(s)**
3. APK saved in `android/app/build/outputs/apk/`

## Building for iOS

### Using Expo

```bash
# Build IPA for TestFlight/App Store
eas build --platform ios --profile production

# Build for ad-hoc distribution
eas build --platform ios --profile preview
```

### Using Xcode

1. Open `ios/CallBunker.xcworkspace` in Xcode
2. Select target device/simulator
3. Product → Archive
4. Distribute for TestFlight or ad-hoc

## Project Structure

```
callbunker-mobile/
├── src/
│   ├── screens/          # All app screens
│   │   ├── SignupScreen.js
│   │   ├── HomeScreen.js
│   │   ├── DialerScreen.js
│   │   ├── CallHistoryScreen.js
│   │   ├── ContactsScreen.js
│   │   ├── MessagesScreen.js
│   │   └── SettingsScreen.js
│   ├── services/         # Core services
│   │   ├── CallBunkerContext.js    # State management
│   │   └── CallBunkerNative.js     # Calling logic
│   ├── i18n/            # Internationalization
│   │   ├── index.js
│   │   └── translations.js
│   └── components/      # Reusable components
│       └── LanguageSelectionModal.js
├── android/             # Android native code
├── ios/                 # iOS native code
├── App.js              # Root component
├── package.json
└── README.md
```

## Key Files Explained

### `CallBunkerNative.js` - Core Calling Logic

Handles native device calling with CallBunker protection:

```javascript
async makeCall(targetNumber) {
    // 1. Get call configuration from backend
    const callData = await fetch(`${baseUrl}/multi/user/${userId}/call_direct`, {
        method: 'POST',
        body: JSON.stringify({ to_number: targetNumber })
    });
    
    // 2. Open native dialer with target number
    await Linking.openURL(`tel:${callData.target_number}`);
    
    // 3. Return CallBunker number for user reference
    return { callbunkerNumber: callData.twilio_caller_id };
}
```

### `CallBunkerContext.js` - State Management

Manages user authentication, backend connection, and app state:

```javascript
const CallBunkerProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [defenseNumber, setDefenseNumber] = useState(null);
    
    // Auto-load user session from AsyncStorage
    useEffect(() => {
        loadUserSession();
    }, []);
    
    return (
        <CallBunkerContext.Provider value={{ user, defenseNumber, ... }}>
            {children}
        </CallBunkerContext.Provider>
    );
};
```

## Backend API Endpoints Used

### User Management
- `POST /multi/signup` - Create new user and assign phone number
- `GET /multi/user/{userId}/info` - Get user details

### Calling
- `POST /multi/user/{userId}/call_direct` - Get call configuration
- `POST /multi/user/{userId}/calls/{callId}/complete` - Log call completion
- `GET /multi/user/{userId}/calls` - Get call history

### Contacts
- `GET /multi/user/{userId}/contacts` - List trusted contacts
- `POST /multi/user/{userId}/contacts` - Add trusted contact
- `DELETE /multi/user/{userId}/contacts/{contactId}` - Remove contact

### Messages
- `POST /multi/user/{userId}/send_message` - Send anonymous SMS

## Troubleshooting

### "Cannot connect to backend"
- Verify backend URL in `CallBunkerContext.js`
- Ensure backend is deployed and running
- Check network connectivity

### "Phone number assignment failed"
- Backend phone pool must have available numbers
- Use admin dashboard to replenish pool
- Check Twilio account balance

### "APK build fails"
- Ensure JDK 17+ installed: `java -version`
- Clean build: `cd android && ./gradlew clean`
- Check Android Studio SDK configuration

### "Linking.openURL not working"
- Only works on physical devices or emulators (not web)
- Ensure phone permissions enabled
- Test with `tel:` URL format

## Development Tips

### Testing Calls Without Backend

The app includes mock data for UI development. To test calling flow:

1. Disable backend calls in `CallBunkerNative.js`
2. Use mock call history from `getMockCallHistory()`
3. Test UI/UX without Twilio costs

### Adding New Languages

Edit `src/i18n/translations.js`:

```javascript
export const translations = {
    en: { "Home": "Home", ... },
    es: { "Home": "Inicio", ... },
    // Add new language:
    pt: { "Home": "Casa", ... }
};
```

### Debugging

```bash
# View React Native logs
npm start
# Then press 'd' in terminal for dev menu

# Android logs
adb logcat | grep CallBunker

# iOS logs  
xcrun simctl spawn booted log stream --predicate 'processImagePath contains "CallBunker"'
```

## Deployment Checklist

Before deploying to production:

- [ ] Update `API_BASE_URL` to production backend
- [ ] Configure app icon and splash screen
- [ ] Test signup flow with real Twilio numbers
- [ ] Verify all languages display correctly
- [ ] Build release APK/IPA
- [ ] Test on physical devices (iOS & Android)
- [ ] Submit to App Store / Play Store

## Security Notes

- User sessions stored in AsyncStorage (encrypted on device)
- No sensitive credentials in app code
- Backend handles all Twilio authentication
- Phone pool assignment prevents number conflicts

## License

Proprietary - All rights reserved

## Support

For issues or questions:
- Backend setup: See `PROVISIONING_GUIDE.md` in backend repo
- Mobile app: Create GitHub issue
- Twilio config: Check Twilio Console settings

---

**Built with React Native + Expo**  
**Backend: Flask + Twilio + PostgreSQL**
