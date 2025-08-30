# Your Next Steps: Download CallBunker APK

## Immediate Actions Required

### 1. Login to EAS from Your Computer
Open your terminal/command prompt and navigate to the project:
```bash
cd mobile_app/callbunker-build
npx eas login
```
Enter your Expo account email and password when prompted.

### 2. Build Your CallBunker APK
Run this single command:
```bash
npx eas build --platform android --profile preview
```

### 3. What Happens Next
- EAS will provide a build URL (like: https://expo.dev/accounts/yourname/projects/callbunker/builds/...)
- Build process takes 5-10 minutes
- You'll receive an email notification when complete
- The APK will be available for download

### 4. Download and Install
- Visit the build URL or go to https://expo.dev/accounts
- Click "Download" for your completed build
- Transfer APK to your Android device
- Enable "Install from Unknown Sources" if needed
- Install and launch CallBunker!

## Your APK Will Include:
- Native Android calling through device
- Google Voice caller ID spoofing
- Complete CallBunker privacy protection
- Professional mobile interface
- Contact management system
- SMS integration (ready for A2P registration)

## Build Commands Summary:
```bash
# Navigate to project
cd mobile_app/callbunker-build

# Login (one time only)
npx eas login

# Build APK (main command)
npx eas build --platform android --profile preview

# Check build status anytime
npx eas build:list
```

Your CallBunker APK will be ready in minutes after running the build command!