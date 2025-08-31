# CallBunker GitHub Repository Setup Guide

## ⚠️ Important: .expo Folder and GitHub

### **The Issue**
The CallBunker mobile app contains a `.expo` folder and `node_modules` that should **NOT** be pushed to GitHub because:
- `.expo` contains local development cache and temporary files
- `node_modules` contains dependencies that should be installed fresh
- These folders are large and cause repository bloat
- They can contain machine-specific configurations

### **Solution: .gitignore Configuration**

Create a `.gitignore` file in your repository root:

```gitignore
# Expo
.expo/
.expo-shared/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# React Native
*.orig.*
web-build/

# macOS
.DS_Store

# Temporary files
*.tmp
*.temp

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
build/
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS generated files
Thumbs.db
ehthumbs.db
```

## **GitHub Repository Setup Steps**

### **Step 1: Create Repository**
```bash
# Create new GitHub repository (on GitHub.com)
# Clone it locally
git clone https://github.com/yourusername/callbunker-app.git
cd callbunker-app
```

### **Step 2: Add .gitignore FIRST**
```bash
# Create .gitignore file with content above
echo "# Expo
.expo/
.expo-shared/

# Node
node_modules/
npm-debug.log*

# React Native
*.orig.*
web-build/" > .gitignore

# Add more patterns from the full .gitignore above
```

### **Step 3: Copy App Files (Excluding .expo)**
```bash
# Create mobile app directory
mkdir -p mobile_app/

# Copy callbunker-build but exclude .expo and node_modules
rsync -av --exclude='.expo' --exclude='node_modules' \
  /path/to/mobile_app/callbunker-build/ \
  ./mobile_app/callbunker-build/

# Or manually copy files, skipping .expo folder
```

### **Step 4: Commit Clean Code**
```bash
git add .gitignore
git add mobile_app/
git commit -m "Initial CallBunker mobile app setup"
git push origin main
```

## **Developer Instructions**

### **For Your Developer Team:**

**When Cloning the Repository:**
```bash
git clone https://github.com/yourusername/callbunker-app.git
cd callbunker-app/mobile_app/callbunker-build

# Install dependencies (recreates node_modules)
npm install

# Start development
npx expo start
```

**Important Notes:**
1. **Never commit .expo folder** - It's in .gitignore for a reason
2. **Always run `npm install`** after cloning to recreate node_modules
3. **Let Expo recreate .expo folder** locally when running `expo start`

## **GitHub Actions Configuration**

Update the GitHub Actions workflow to handle this properly:

```yaml
name: Build CallBunker APK

on:
  push:
    branches: [ main, develop ]

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
      run: npm install  # This recreates node_modules
      
    - name: Clear Expo cache
      working-directory: ./mobile_app/callbunker-build
      run: npx expo install --fix  # Ensures clean dependencies
      
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
        name: callbunker-apk-${{ github.sha }}
        path: "*.apk"
```

## **Repository Structure**

Your final GitHub repository should look like:

```
callbunker-app/
├── .gitignore                    # Excludes .expo, node_modules
├── README.md                     # Project documentation
├── mobile_app/
│   └── callbunker-build/
│       ├── App.js
│       ├── package.json
│       ├── app.json
│       ├── src/
│       │   ├── screens/
│       │   └── services/
│       └── android/
├── docs/                         # Documentation files
│   ├── SEND_TO_DEVELOPER.md
│   ├── COMPLETE_MOBILE_APP_PACKAGE.md
│   └── GITHUB_APK_BUILD_SETUP.md
└── .github/
    └── workflows/
        └── build-apk.yml
```

## **What Gets Excluded from GitHub**

**Never Committed:**
- `.expo/` folder (development cache)
- `node_modules/` (dependencies)
- Build artifacts and logs
- Local environment files

**Always Committed:**
- Source code (`src/` folder)
- Configuration files (`package.json`, `app.json`)
- Documentation and guides
- GitHub Actions workflows

## **Benefits of Proper Setup**

1. **Clean Repository** - Only source code, no bloat
2. **Fast Cloning** - Repository downloads quickly
3. **Fresh Builds** - Each developer gets clean dependencies
4. **No Conflicts** - Eliminates machine-specific files
5. **Professional** - Industry-standard repository structure

## **Developer Team Action Items**

1. **Create .gitignore before committing anything**
2. **Copy source code excluding .expo and node_modules**
3. **Set up GitHub Actions for automated building**
4. **Document the workflow for team members**
5. **Test the complete clone → install → build process**

Your developer team will know exactly what to do with this guide, and the repository will be clean and professional.