# Repository Contents

Complete file structure of the CallBunker mobile app repository.

## 📂 Repository Structure

```
callbunker-mobile/
│
├── 📱 Source Code
│   ├── src/
│   │   ├── screens/              # All app screens
│   │   │   ├── SignupScreen.js          # User registration
│   │   │   ├── HomeScreen.js            # Main dashboard
│   │   │   ├── DialerScreen.js          # Protected calling
│   │   │   ├── CallHistoryScreen.js     # Call logs
│   │   │   ├── CallLogDetailScreen.js   # Individual call details
│   │   │   ├── ContactsScreen.js        # Trusted contacts
│   │   │   ├── MessagesScreen.js        # Anonymous SMS
│   │   │   └── SettingsScreen.js        # App settings
│   │   │
│   │   ├── services/             # Core business logic
│   │   │   ├── CallBunkerContext.js     # State management
│   │   │   └── CallBunkerNative.js      # Calling engine
│   │   │
│   │   ├── i18n/                 # Internationalization
│   │   │   ├── index.js                 # i18n configuration
│   │   │   └── translations.js          # 10+ language translations
│   │   │
│   │   └── components/           # Reusable components
│   │       └── LanguageSelectionModal.js
│   │
│   ├── App.js                    # Root component
│   └── index.js                  # Entry point
│
├── 🤖 Android Native
│   ├── android/
│   │   ├── app/
│   │   │   ├── src/main/
│   │   │   │   ├── java/com/callbunker/mobile/
│   │   │   │   │   ├── MainActivity.kt
│   │   │   │   │   └── MainApplication.kt
│   │   │   │   ├── res/                 # App icons, splash screens
│   │   │   │   └── AndroidManifest.xml
│   │   │   └── build.gradle             # App-level config
│   │   ├── build.gradle          # Project-level config
│   │   ├── gradle.properties     # Gradle settings
│   │   ├── settings.gradle       # Module settings
│   │   └── gradlew              # Gradle wrapper (Linux/Mac)
│   │   └── gradlew.bat          # Gradle wrapper (Windows)
│
├── 🎨 Assets
│   ├── assets/
│   │   ├── icon.png             # App icon (1024x1024)
│   │   ├── adaptive-icon.png    # Android adaptive icon
│   │   ├── splash.png           # Splash screen
│   │   ├── splash-icon.png      # Splash logo
│   │   └── favicon.png          # Web favicon
│
├── ⚙️ Configuration
│   ├── app.json                 # Expo config
│   ├── eas.json                 # EAS Build config
│   ├── package.json             # Dependencies
│   ├── babel.config.js          # Babel configuration
│   ├── metro.config.js          # Metro bundler config
│   └── .gitignore              # Git ignore rules
│
└── 📚 Documentation
    ├── README.md                # Main documentation
    ├── QUICK_START.md           # 5-minute setup guide
    ├── APK_BUILD_GUIDE.md       # Complete build instructions
    ├── BACKEND_INTEGRATION.md   # API documentation
    └── REPOSITORY_CONTENTS.md   # This file
```

## 📄 File Descriptions

### Core Application Files

#### **App.js** (179 lines)
Root component with navigation structure, authentication flow, and tab navigation setup.

**Key features:**
- Bottom tab navigation (6 tabs)
- Stack navigation for detail screens
- Authentication check wrapper
- i18n integration
- Theme configuration

#### **index.js** (1 line)
Entry point that registers the root component.

```javascript
import { registerRootComponent } from 'expo';
import App from './App';
registerRootComponent(App);
```

### Screen Components

#### **SignupScreen.js** (~200 lines)
User registration with automatic CallBunker number assignment.

**Features:**
- Name and email input
- Backend API integration
- Success modal with assigned number
- Google Voice integration link
- Error handling

#### **HomeScreen.js** (~250 lines)
Main dashboard showing protection status.

**Features:**
- Defense number display
- Protection stats
- Quick actions
- Feature explanations

#### **DialerScreen.js** (~300 lines)
Protected calling interface.

**Features:**
- Phone number input with formatting
- Native device calling via Linking API
- Post-call information modal
- CallBunker number display
- Call history integration

#### **CallHistoryScreen.js** (~200 lines)
Call log viewer with filtering.

**Features:**
- List of all protected calls
- Date/time display
- Duration tracking
- Tap to view details

#### **CallLogDetailScreen.js** (~150 lines)
Individual call details screen.

**Features:**
- Full call information
- Caller ID shown
- Duration display
- Quick redial option

#### **ContactsScreen.js** (~300 lines)
Trusted contacts management.

**Features:**
- Add/remove contacts
- Custom PIN assignment
- Search/filter
- Bulk operations

#### **MessagesScreen.js** (~250 lines)
Anonymous SMS sending interface.

**Features:**
- Message composition
- Recipient selection
- Send from CallBunker number
- Message history

#### **SettingsScreen.js** (~200 lines)
App configuration and preferences.

**Features:**
- Language selection
- Account information
- Privacy settings
- About section

### Service Modules

#### **CallBunkerContext.js** (~300 lines)
Global state management with React Context API.

**Manages:**
- User authentication state
- Defense number storage
- API base URL configuration
- Session persistence (AsyncStorage)
- Auto-login on app launch

**Key functions:**
```javascript
- signup(name, email)
- logout()
- loadUserSession()
- updateDefenseNumber()
```

#### **CallBunkerNative.js** (~290 lines)
Core calling engine using React Native Linking API.

**Key methods:**
```javascript
- makeCall(targetNumber)          // Initiate protected call
- completeCall(callId, duration)  // Log call completion
- getCallHistory(limit, offset)   // Fetch call logs
- isNativeCallingSupported()      // Check device capability
- requestCallPermissions()        // Request phone permissions
```

**Architecture:**
- No Twilio Voice SDK
- No WebRTC/VoIP
- Uses native device dialer
- Twilio number for caller ID only

### Internationalization

#### **src/i18n/index.js** (~100 lines)
i18n system configuration.

**Features:**
- Language detection (browser/device)
- AsyncStorage persistence
- Change listeners
- Fallback to English

**Supported languages:**
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)

#### **src/i18n/translations.js** (~500 lines)
Translation strings for all languages.

**Coverage:**
- UI labels
- Button text
- Error messages
- Help text

### Android Native Code

#### **MainActivity.kt**
Main Android activity (Kotlin).

```kotlin
class MainActivity : ReactActivity() {
    override fun getMainComponentName() = "CallBunker"
}
```

#### **MainApplication.kt**
Application initialization (Kotlin).

```kotlin
class MainApplication : Application(), ReactApplication {
    // React Native setup
    // Package initialization
}
```

#### **AndroidManifest.xml**
App permissions and configuration.

**Permissions:**
- INTERNET
- CALL_PHONE
- READ_PHONE_STATE

### Configuration Files

#### **package.json**
Dependencies and scripts.

**Key dependencies:**
- `expo`: ~53.0.22
- `react`: 19.0.0
- `react-native`: 0.79.6
- `@react-navigation/*`: Navigation
- `@react-native-async-storage`: Storage
- `react-native-vector-icons`: Icons

**Scripts:**
```json
{
  "start": "expo start",
  "android": "expo run:android",
  "ios": "expo run:ios",
  "web": "expo start --web"
}
```

#### **app.json**
Expo configuration.

**Settings:**
- App name: "CallBunker"
- Version: 1.0.0
- Orientation: portrait
- Icons and splash
- Android/iOS specific config

#### **eas.json**
EAS Build configuration.

**Profiles:**
- `preview`: APK builds for testing
- `production`: AAB builds for Play Store

#### **babel.config.js**
Babel transpiler configuration.

```javascript
module.exports = {
  presets: ['babel-preset-expo'],
  plugins: ['react-native-reanimated/plugin']
};
```

#### **metro.config.js**
Metro bundler configuration.

```javascript
const { getDefaultConfig } = require('expo/metro-config');
module.exports = getDefaultConfig(__dirname);
```

#### **.gitignore**
Files excluded from version control.

**Ignores:**
- node_modules/
- build/
- *.keystore
- .env files
- Platform-specific build artifacts

### Documentation Files

#### **README.md** (~400 lines)
Main repository documentation.

**Sections:**
- Features overview
- Architecture explanation
- Prerequisites
- Installation steps
- Running instructions
- Building APK/IPA
- Project structure
- Troubleshooting

#### **QUICK_START.md** (~300 lines)
Fast setup guide for developers.

**Sections:**
- 5-minute setup
- Step-by-step instructions
- Common issues & fixes
- Verification checklist

#### **APK_BUILD_GUIDE.md** (~600 lines)
Complete build documentation.

**Sections:**
- 3 build methods (EAS, Gradle, Android Studio)
- Signing configuration
- Distribution options
- Troubleshooting
- Optimization tips

#### **BACKEND_INTEGRATION.md** (~500 lines)
API integration guide.

**Sections:**
- API endpoints documentation
- Request/response formats
- Error handling
- Testing procedures
- Security considerations

## 📊 Statistics

### Code Metrics

- **Total Files**: 60+
- **Source Code Lines**: ~3,500
- **Documentation Lines**: ~2,000
- **Screens**: 8
- **Languages Supported**: 10+
- **API Endpoints Used**: 15+

### Build Outputs

- **APK Size** (universal): ~50-70 MB
- **APK Size** (per-arch): ~25-35 MB
- **Android Min SDK**: 24 (Android 7.0)
- **Android Target SDK**: 34 (Android 14)

### Dependencies

- **Total Dependencies**: 15
- **Dev Dependencies**: 3
- **React Native Version**: 0.79.6
- **Expo SDK Version**: 53

## 🔄 Update Workflow

### Adding New Features

1. Create screen in `src/screens/`
2. Add to navigation in `App.js`
3. Update i18n translations
4. Test on device
5. Build new APK

### Updating Dependencies

```bash
# Check for updates
npm outdated

# Update packages
npm update

# Or update specific package
npm install react-native@latest
```

### Version Bumping

Update version in 3 places:

1. `app.json` → `expo.version`
2. `app.json` → `expo.android.versionCode`
3. `android/app/build.gradle` → `versionName` & `versionCode`

## 🚀 Deployment Files

### For Development
- Source code
- package.json
- Configuration files

### For App Store Submission
- APK/AAB file
- Screenshots (5+ different screen sizes)
- App icon (512x512 PNG)
- Feature graphic (1024x500)
- Privacy policy
- App description

### For Beta Testing
- APK file
- Installation instructions
- Tester feedback form
- Backend test environment URL

## 📝 File Modification Guide

### To Change App Name

1. `app.json` → `expo.name`
2. `android/app/src/main/res/values/strings.xml` → `app_name`
3. `package.json` → `name`

### To Change App Icon

1. Replace `assets/icon.png` (1024x1024)
2. Replace `assets/adaptive-icon.png` (1024x1024)
3. Run: `expo prebuild --clean`

### To Change Backend URL

1. `src/services/CallBunkerContext.js` → Line 14
2. Set `API_BASE_URL` to your backend

### To Add New Language

1. `src/i18n/translations.js` → Add language object
2. `src/i18n/index.js` → Add to `SUPPORTED_LANGUAGES`
3. Test all screens with new language

## 🔐 Security Files

### Sensitive Files (Never Commit)

- `*.keystore` (signing keys)
- `.env` (environment variables)
- `google-services.json` (Firebase)
- `local.properties` (local SDK paths)

### Included Security

- `.gitignore` prevents sensitive files
- AsyncStorage encrypts user data (OS-level)
- HTTPS enforced for API calls
- No hardcoded credentials

---

**This repository contains everything needed to build, run, and deploy the CallBunker mobile app!**

For questions about specific files, see the main README.md or individual guide documents.
