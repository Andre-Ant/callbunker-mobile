# CallBunker Multi-User APK Build Guide - FINAL VERSION

## 🎯 OVERVIEW

This guide covers building the **final multi-user APK** for CallBunker. The mobile app now includes complete signup flow, multi-user backend integration, and automatic Defense Number assignment.

## ✅ PREREQUISITES COMPLETED

### Backend Configuration
- ✅ Multi-user routes active (`/multi/signup`, `/multi/user/{id}/`)
- ✅ Phone pool system with 3 Twilio numbers
- ✅ User registration and assignment system operational
- ✅ Database schema updated for multi-user support

### Mobile App Updates
- ✅ All API endpoints updated to multi-user routes
- ✅ Signup screen implemented with complete registration form
- ✅ Authentication flow with persistent sessions
- ✅ User isolation and data management

## 📱 APK BUILD PROCESS

### Step 1: Navigate to Mobile App Directory
```bash
cd mobile_app/callbunker-build
```

### Step 2: Install Dependencies
```bash
npm install
# Install any missing React Native dependencies
npm install @react-native-async-storage/async-storage
npm install react-native-vector-icons
```

### Step 3: Configure Expo/EAS Build

#### Option A: EAS Build (Recommended)
```bash
# Install EAS CLI if not already installed
npm install -g @expo/cli

# Login to Expo account
expo login

# Configure build
eas build:configure

# Build APK
eas build --platform android --profile preview
```

#### Option B: Expo Build (Legacy)
```bash
# Install Expo CLI if not already installed
npm install -g expo-cli

# Login to Expo account
expo login

# Build APK
expo build:android --type=apk
```

### Step 4: Update App Configuration
Before building, ensure the backend URL is correctly set:

**File: `mobile_app/callbunker-build/src/services/CallBunkerContext.js`**
```javascript
apiUrl: 'https://your-replit-url.replit.app', // Update with your actual Replit URL
```

## 🔧 BUILD CONFIGURATION

### EAS Build Configuration (eas.json)
```json
{
  "cli": {
    "version": ">= 3.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "android": {
        "buildType": "aab"
      }
    }
  },
  "submit": {
    "production": {}
  }
}
```

### App Configuration (app.json)
```json
{
  "expo": {
    "name": "CallBunker",
    "slug": "callbunker",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#007AFF"
    },
    "android": {
      "package": "com.callbunker.app",
      "versionCode": 1,
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#007AFF"
      },
      "permissions": [
        "CALL_PHONE",
        "READ_PHONE_STATE",
        "READ_CONTACTS",
        "RECORD_AUDIO"
      ]
    },
    "plugins": [
      [
        "expo-build-properties",
        {
          "android": {
            "compileSdkVersion": 33,
            "targetSdkVersion": 33,
            "buildToolsVersion": "33.0.0"
          }
        }
      ]
    ]
  }
}
```

## 🏗️ MULTI-USER FEATURES

### User Registration Flow
1. **Download APK** → Install CallBunker
2. **First Launch** → Signup screen appears
3. **Complete Form**:
   - Full Name
   - Email Address
   - Google Voice Number
   - Real Phone Number
   - Security PIN (4 digits)
   - Verbal Code

### Automatic Assignment
- Each user receives unique Defense Number from phone pool
- Backend assigns from available Twilio numbers:
  - `+16316417728`
  - `+16316417729`
  - `+16316417730`

### User Isolation
- Separate call history per user
- Individual trusted contacts lists
- Personal settings and preferences
- Unique authentication codes

## 📋 TESTING CHECKLIST

### Before Distribution
- [ ] Backend URL updated in mobile app
- [ ] Signup flow tested with real data
- [ ] Phone number assignment working
- [ ] Call functionality operational
- [ ] Contact management working
- [ ] Settings persistence verified

### APK Validation
- [ ] APK installs successfully
- [ ] Signup creates new user account
- [ ] User receives Defense Number
- [ ] All features accessible post-signup
- [ ] Data persists between app sessions

## 🚀 DISTRIBUTION OPTIONS

### Option 1: Direct APK Distribution
- Download APK from Expo/EAS build
- Share APK file directly with users
- Users enable "Install from Unknown Sources"

### Option 2: Google Play Store
- Use AAB (Android App Bundle) format
- Complete Google Play Console setup
- Follow store publishing guidelines

### Option 3: Internal Testing
- Use Expo Go for development testing
- TestFlight equivalent for internal distribution
- Beta testing with limited user group

## 🔍 TROUBLESHOOTING

### Common Build Issues

#### Missing Dependencies
```bash
npm install --legacy-peer-deps
expo install --fix
```

#### Build Failures
```bash
# Clear cache
expo r -c
rm -rf node_modules
npm install
```

#### Android SDK Issues
- Ensure Android SDK properly configured
- Update build tools to latest version
- Check Java version compatibility

### Runtime Issues

#### API Connection Failed
- Verify backend URL in `CallBunkerContext.js`
- Check Replit deployment status
- Ensure CORS properly configured

#### Signup Failures
- Verify multi-user routes active
- Check phone pool availability
- Validate form data formatting

## 📊 MONITORING

### User Registration
Monitor backend logs for:
- New user signups
- Phone number assignments
- Registration failures

### APK Performance
Track metrics:
- Installation success rate
- User retention after signup
- Feature usage patterns

## 🎉 SUCCESS METRICS

### Multi-User System Ready When:
- [ ] APK builds without errors
- [ ] Signup flow creates users successfully
- [ ] Each user gets unique Defense Number
- [ ] All CallBunker features functional
- [ ] User data properly isolated
- [ ] Phone pool assignments working

---

**FINAL STATUS**: CallBunker mobile app is ready for multi-user APK distribution with complete signup flow and automatic Defense Number assignment system.