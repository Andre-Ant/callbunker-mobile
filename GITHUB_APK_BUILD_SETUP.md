# CallBunker Mobile App - GitHub Repository Setup

## GitHub Integration Benefits

Using GitHub for your CallBunker repo provides several advantages:

### **✅ Automated APK Building**
- GitHub Actions can automatically build APKs when code changes
- No need for local Android Studio setup
- Continuous integration and deployment

### **✅ Team Collaboration**
- Multiple developers can work on the same codebase
- Version control and code history
- Pull request reviews for code quality

### **✅ Free CI/CD Pipeline**
- GitHub Actions provides free build minutes
- Automatic testing and deployment
- Release management with APK distribution

## **Setup Instructions for GitHub**

### **1. Repository Structure**
Your GitHub repo should contain:
```
your-callbunker-repo/
├── mobile_app/callbunker-build/    # Complete mobile app
├── backend/                        # Flask backend (optional)
├── docs/                          # Documentation
└── .github/workflows/             # GitHub Actions (we'll create this)
```

### **2. GitHub Actions Workflow**
Create `.github/workflows/build-apk.yml`:

```yaml
name: Build CallBunker APK

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Setup Expo CLI
      run: npm install -g @expo/cli eas-cli
      
    - name: Install dependencies
      working-directory: ./mobile_app/callbunker-build
      run: npm install
      
    - name: Login to Expo
      run: eas login --non-interactive
      env:
        EXPO_TOKEN: ${{ secrets.EXPO_TOKEN }}
        
    - name: Build APK
      working-directory: ./mobile_app/callbunker-build
      run: eas build --platform android --profile preview --non-interactive
      
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: callbunker-apk
        path: ./mobile_app/callbunker-build/*.apk
```

### **3. Required GitHub Secrets**
In your GitHub repo settings, add these secrets:

- `EXPO_TOKEN` - Your Expo authentication token
- `ANDROID_KEYSTORE` - Android signing keystore (optional)
- `KEYSTORE_PASSWORD` - Keystore password (optional)

### **4. Alternative: Direct APK Build**
For simpler setup without Expo dependency:

```yaml
name: Build Direct APK

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Setup React Native
      run: |
        npm install -g react-native-cli
        
    - name: Install dependencies
      working-directory: ./mobile_app/callbunker-build
      run: npm install
      
    - name: Build APK
      working-directory: ./mobile_app/callbunker-build
      run: |
        cd android
        ./gradlew assembleRelease
        
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: callbunker-apk
        path: ./mobile_app/callbunker-build/android/app/build/outputs/apk/release/*.apk
```

## **Developer Instructions with GitHub**

### **Option 1: Using GitHub Actions (Recommended)**

**Step 1: Push Code to GitHub**
```bash
git clone your-github-repo
cd your-github-repo
# Copy mobile_app/callbunker-build/ to repo
git add .
git commit -m "Add CallBunker mobile app"
git push origin main
```

**Step 2: Automatic APK Build**
- GitHub Actions automatically builds APK on push
- Download APK from Actions tab in GitHub
- No local setup required

**Step 3: Apply Signup Enhancement**
```bash
# Update SignupScreen.js with enhanced version
git add src/screens/SignupScreen.js
git commit -m "Enhanced signup with Google Voice integration"
git push origin main
# GitHub Actions builds new APK automatically
```

### **Option 2: Local Development + GitHub**

**Step 1: Clone and Setup**
```bash
git clone your-github-repo
cd your-github-repo/mobile_app/callbunker-build
npm install
```

**Step 2: Local Development**
```bash
# Test on device
npx expo start --tunnel

# Or use GitHub Codespaces
# Provides cloud development environment
```

**Step 3: Build APK**
```bash
# Local build
eas build --platform android

# Or push to GitHub and let Actions build
git push origin main
```

## **GitHub Codespaces Option**

GitHub Codespaces provides a cloud development environment:

### **Benefits:**
- No local setup required
- Pre-configured development environment
- Access from any browser
- Integrated with GitHub repo

### **Setup:**
1. Open your GitHub repo
2. Click "Code" → "Codespaces" → "Create codespace"
3. Environment loads with Node.js and tools pre-installed
4. Run `cd mobile_app/callbunker-build && npm install`
5. Test app with `npx expo start --tunnel`

## **Distribution Options**

### **1. GitHub Releases**
- Automatic APK uploads to GitHub Releases
- Users download directly from GitHub
- Version tracking and release notes

### **2. GitHub Pages**
- Host download page for APK
- Instructions and screenshots
- Professional distribution portal

### **3. Direct Links**
- Share APK download links
- Email distribution to beta testers
- Simple installation process

## **Updated Developer Package**

Your developer now needs:

**Files to Send:**
1. **COMPLETE_MOBILE_APP_PACKAGE.md** - App documentation
2. **GITHUB_APK_BUILD_SETUP.md** - This GitHub setup guide
3. **Complete mobile app folder** - `mobile_app/callbunker-build/`
4. **COMPLETE_SIGNUPSCREEN_CODE.js** - Enhanced signup

**GitHub Setup:**
1. Create GitHub repository
2. Add mobile app code
3. Set up GitHub Actions for APK building
4. Configure secrets and environment

**Benefits of GitHub Approach:**
- Automated APK building
- No local Android Studio required
- Team collaboration
- Professional CI/CD pipeline
- Free hosting and distribution

This approach is actually better than local Expo Go testing because it provides production APK builds automatically through GitHub's infrastructure.