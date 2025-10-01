# APK Build Guide

Complete guide to building and distributing your CallBunker Android APK.

## Method 1: Expo Application Services (Recommended) ⭐

**Best for:** Easy cloud builds, automatic code signing, no local Android Studio needed.

### Prerequisites
- Expo account (free at expo.dev)
- EAS CLI installed globally

### Steps

#### 1. Install EAS CLI

```bash
npm install -g eas-cli
```

#### 2. Login to Expo

```bash
eas login
# Enter your Expo credentials
```

#### 3. Configure Project

```bash
# Initialize EAS configuration
eas build:configure

# This creates eas.json with build profiles
```

Your `eas.json` should look like:

```json
{
  "build": {
    "preview": {
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "android": {
        "buildType": "app-bundle"
      }
    }
  }
}
```

#### 4. Build APK

```bash
# Build for testing/distribution (APK)
eas build --platform android --profile preview

# Or build for Google Play (AAB)
eas build --platform android --profile production
```

#### 5. Download APK

When build completes:
- Check terminal for download URL
- Or visit: https://expo.dev/accounts/YOUR_ACCOUNT/projects/callbunker/builds
- Download APK and share via email, Drive, etc.

**Build time:** ~10-15 minutes (cloud build)

---

## Method 2: React Native CLI (Local Build)

**Best for:** Full control, offline builds, debugging build issues.

### Prerequisites
- Android Studio installed
- JDK 17 or 21 installed
- Android SDK configured

### Steps

#### 1. Configure Build Settings

Edit `android/app/build.gradle`:

```gradle
android {
    defaultConfig {
        applicationId "com.callbunker.mobile"
        minSdkVersion 24
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }
    
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

#### 2. Generate Release APK

```bash
cd android

# Clean previous builds
./gradlew clean

# Build release APK
./gradlew assembleRelease

# APK location:
# android/app/build/outputs/apk/release/app-release.apk
```

#### 3. Sign APK (Optional but Recommended)

For Google Play submission, you need a signed APK:

**Generate Keystore:**

```bash
keytool -genkeypair -v -storetype PKCS12 \
  -keystore callbunker-release.keystore \
  -alias callbunker-key \
  -keyalg RSA -keysize 2048 -validity 10000
```

**Configure Gradle:**

Create `android/gradle.properties`:

```properties
CALLBUNKER_UPLOAD_STORE_FILE=callbunker-release.keystore
CALLBUNKER_UPLOAD_KEY_ALIAS=callbunker-key
CALLBUNKER_UPLOAD_STORE_PASSWORD=your_keystore_password
CALLBUNKER_UPLOAD_KEY_PASSWORD=your_key_password
```

Update `android/app/build.gradle`:

```gradle
signingConfigs {
    release {
        storeFile file(CALLBUNKER_UPLOAD_STORE_FILE)
        storePassword CALLBUNKER_UPLOAD_STORE_PASSWORD
        keyAlias CALLBUNKER_UPLOAD_KEY_ALIAS
        keyPassword CALLBUNKER_UPLOAD_KEY_PASSWORD
    }
}
buildTypes {
    release {
        signingConfig signingConfigs.release
        // ... other settings
    }
}
```

**Build Signed APK:**

```bash
./gradlew assembleRelease
```

#### 4. Test APK

```bash
# Install on connected device
adb install app/build/outputs/apk/release/app-release.apk

# Or drag & drop APK to emulator
```

**Build time:** ~5-10 minutes (local build)

---

## Method 3: Android Studio GUI

**Best for:** Visual build management, beginners, debugging.

### Steps

#### 1. Open Project

```bash
# Open Android Studio
# File → Open → Select: callbunker-mobile/android/
```

#### 2. Configure Build Variant

- View → Tool Windows → Build Variants
- Select "release" for app module

#### 3. Build APK

- Build → Build Bundle(s) / APK(s) → Build APK(s)
- Wait for build to complete (~5-10 min)
- Click "locate" in notification to find APK

#### 4. Find APK

```
android/app/build/outputs/apk/release/app-release.apk
```

---

## APK Distribution Options

### Option 1: Direct Download Link

```bash
# Upload APK to cloud storage
# Share download link with users

# Example services:
- Google Drive
- Dropbox  
- Firebase App Distribution
- GitHub Releases
```

### Option 2: Google Play Store

#### Prepare for Submission

1. **Create App Bundle** (required by Play Store)

```bash
# Using EAS
eas build --platform android --profile production

# Or using Gradle
cd android && ./gradlew bundleRelease
# AAB location: android/app/build/outputs/bundle/release/app-release.aab
```

2. **Create Play Console Account**
   - Visit: https://play.google.com/console
   - Pay one-time $25 registration fee

3. **Create App Listing**
   - App name: CallBunker
   - Category: Communication
   - Upload screenshots, description, icon

4. **Upload AAB**
   - Production → Create new release
   - Upload app-release.aab
   - Set version code/name
   - Submit for review

5. **Review Process**
   - Initial review: 1-3 days
   - Updates: Few hours to 1 day

### Option 3: Internal Testing

```bash
# Firebase App Distribution (free)
npm install -g firebase-tools
firebase login
firebase appdistribution:distribute app-release.apk \
  --app YOUR_FIREBASE_APP_ID \
  --groups testers
```

---

## Troubleshooting Build Issues

### ❌ "Execution failed for task ':app:mergeReleaseResources'"

**Fix:** Clean and rebuild

```bash
cd android
./gradlew clean
./gradlew assembleRelease --stacktrace
```

### ❌ "Duplicate class found"

**Fix:** Check for duplicate dependencies in `android/app/build.gradle`

```gradle
configurations.all {
    resolutionStrategy {
        force 'com.facebook.react:react-native:0.79.6'
    }
}
```

### ❌ "SDK location not found"

**Fix:** Create `android/local.properties`:

```properties
sdk.dir=/Users/YOUR_USERNAME/Library/Android/sdk
# Or on Windows:
# sdk.dir=C:\\Users\\YOUR_USERNAME\\AppData\\Local\\Android\\Sdk
```

### ❌ "Keystore file not found"

**Fix:** Ensure keystore path is correct in `gradle.properties`

```bash
# Use absolute path
CALLBUNKER_UPLOAD_STORE_FILE=/absolute/path/to/callbunker-release.keystore
```

### ❌ "Insufficient memory for Java"

**Fix:** Increase Gradle memory in `android/gradle.properties`:

```properties
org.gradle.jvmargs=-Xmx4096m -XX:MaxPermSize=512m
```

---

## Build Optimization

### Reduce APK Size

1. **Enable Proguard** (already configured)
2. **Remove unused resources:**

```gradle
android {
    buildTypes {
        release {
            shrinkResources true
            minifyEnabled true
        }
    }
}
```

3. **Use APK splits** for different architectures:

```gradle
android {
    splits {
        abi {
            enable true
            reset()
            include 'armeabi-v7a', 'arm64-v8a'
            universalApk false
        }
    }
}
```

Expected APK sizes:
- Universal: ~50-70 MB
- Per-architecture: ~25-35 MB each

### Speed Up Builds

```gradle
# Enable parallel builds
org.gradle.parallel=true
org.gradle.daemon=true
org.gradle.configureondemand=true
```

---

## Version Management

Before each build, update version:

**In `app.json`:**

```json
{
  "expo": {
    "version": "1.0.1",
    "android": {
      "versionCode": 2
    }
  }
}
```

**In `android/app/build.gradle`:**

```gradle
defaultConfig {
    versionCode 2
    versionName "1.0.1"
}
```

**Versioning Rules:**
- `versionCode`: Integer, increments each build (1, 2, 3...)
- `versionName`: String, semantic version (1.0.0, 1.0.1, 1.1.0...)

---

## Pre-Deployment Checklist

Before distributing APK:

- [ ] Backend URL set to production (not localhost)
- [ ] App tested on physical device
- [ ] Signup flow creates real users
- [ ] Calling works with Twilio numbers
- [ ] All features functional (contacts, messages, history)
- [ ] Proguard enabled for release build
- [ ] Version code/name updated
- [ ] App icon and splash screen finalized
- [ ] Keystore backed up securely (if signed)

---

## Distribution Best Practices

### For Beta Testing
- Use Firebase App Distribution
- Collect crash reports
- Get user feedback before Play Store submission

### For Production
- Submit to Google Play Store
- Enable staged rollout (5% → 25% → 50% → 100%)
- Monitor crash reports in Play Console
- Respond to user reviews

### Direct APK Distribution
- Only for trusted users (security concern)
- Inform users to enable "Install from unknown sources"
- Provide SHA256 fingerprint for verification

```bash
# Get APK fingerprint
keytool -printcert -jarfile app-release.apk
```

---

**You're ready to build!** Choose the method that best fits your needs:

- **Quick testing:** Method 1 (EAS)
- **Production builds:** Method 2 (Gradle with signing)  
- **Visual debugging:** Method 3 (Android Studio)

For any build issues, check the troubleshooting section or create a GitHub issue.
