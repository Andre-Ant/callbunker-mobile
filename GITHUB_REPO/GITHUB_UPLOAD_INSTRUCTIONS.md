# GitHub Upload Instructions

Step-by-step guide to upload your CallBunker mobile app to GitHub.

## Method 1: Using GitHub Web Interface (Easiest)

### Step 1: Create New Repository

1. Go to https://github.com/new
2. Repository name: `callbunker-mobile`
3. Description: "CallBunker Mobile - Intelligent Communication Security Platform"
4. Visibility: Private (or Public if you want)
5. **Do NOT** initialize with README (we already have one)
6. Click "Create repository"

### Step 2: Prepare Files for Upload

On your local machine, open terminal in the `GITHUB_REPO` folder:

```bash
cd GITHUB_REPO
```

### Step 3: Initialize Git

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: CallBunker mobile app v1.0"
```

### Step 4: Connect to GitHub

Replace `YOUR_USERNAME` with your GitHub username:

```bash
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/callbunker-mobile.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 5: Verify Upload

1. Go to https://github.com/YOUR_USERNAME/callbunker-mobile
2. You should see all files uploaded
3. README.md displays automatically

---

## Method 2: Using GitHub Desktop (Visual)

### Step 1: Install GitHub Desktop

Download from: https://desktop.github.com

### Step 2: Create Repository

1. Open GitHub Desktop
2. File → New Repository
3. Name: `callbunker-mobile`
4. Local Path: Select parent folder of `GITHUB_REPO`
5. Click "Create Repository"

### Step 3: Add Files

1. Drag `GITHUB_REPO` contents into repository folder
2. GitHub Desktop shows all changes
3. Write commit message: "Initial commit: CallBunker mobile app v1.0"
4. Click "Commit to main"

### Step 4: Publish to GitHub

1. Click "Publish repository" button
2. Choose visibility (Private/Public)
3. Click "Publish Repository"
4. Done!

---

## Method 3: Using Git Command Line (Advanced)

### Complete Workflow

```bash
# Navigate to GITHUB_REPO folder
cd GITHUB_REPO

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: CallBunker mobile app v1.0"

# Create GitHub repository (using GitHub CLI)
gh repo create callbunker-mobile --private --source=. --remote=origin

# Push to GitHub
git push -u origin main
```

**Note:** Requires GitHub CLI (`gh`) installed: https://cli.github.com

---

## Post-Upload Configuration

### Add Repository Description

1. Go to your GitHub repository
2. Click ⚙️ (Settings)
3. Add description: "CallBunker Mobile - Privacy-focused calling app with caller ID spoofing"
4. Add topics: `react-native`, `expo`, `twilio`, `privacy`, `mobile-app`

### Set Up Branch Protection (Optional)

1. Settings → Branches
2. Add rule for `main` branch
3. Enable: "Require pull request reviews"

### Add License (Optional)

1. Create new file: LICENSE
2. Choose license template (MIT, Apache, etc.)
3. Commit

### Create .env.example File

Create template for environment variables:

```bash
# In GITHUB_REPO folder
cat > .env.example << 'EOF'
# Backend Configuration
API_BASE_URL=https://your-backend.repl.co

# Optional: For development
USE_MOCK_DATA=false
EOF

git add .env.example
git commit -m "Add environment variables template"
git push
```

---

## Repository Structure on GitHub

After upload, your repository will have this structure:

```
📦 callbunker-mobile
├── 📄 README.md                    ← Main docs (displays on homepage)
├── 📄 QUICK_START.md              ← Fast setup guide
├── 📄 APK_BUILD_GUIDE.md          ← Build instructions
├── 📄 BACKEND_INTEGRATION.md      ← API documentation
├── 📄 REPOSITORY_CONTENTS.md      ← File structure reference
├── 📄 GITHUB_UPLOAD_INSTRUCTIONS.md ← This file
├── 📁 src/                        ← Source code
├── 📁 android/                    ← Android native
├── 📁 assets/                     ← App assets
├── 📄 App.js                      ← Root component
├── 📄 package.json                ← Dependencies
├── 📄 app.json                    ← Expo config
└── 📄 .gitignore                  ← Git ignore rules
```

---

## Inviting Collaborators

### Add Your Developer

1. Go to repository → Settings → Collaborators
2. Click "Add people"
3. Enter developer's GitHub username
4. Select permission level:
   - **Write**: Can push changes
   - **Admin**: Full access
5. They'll receive email invitation

### Developer Clone Instructions

Send this to your developer:

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/callbunker-mobile.git

# Navigate to project
cd callbunker-mobile

# Install dependencies
npm install

# Configure backend URL (edit src/services/CallBunkerContext.js)

# Run on Android
npm run android
```

---

## Keeping Repository Updated

### When You Make Changes

```bash
# Check what changed
git status

# Add changed files
git add .

# Commit with message
git commit -m "Update: Added new feature X"

# Push to GitHub
git push
```

### Common Commit Messages

```bash
# Feature additions
git commit -m "feat: Add phone number validation"

# Bug fixes
git commit -m "fix: Resolve signup error handling"

# Documentation updates
git commit -m "docs: Update README with new setup steps"

# Performance improvements
git commit -m "perf: Optimize call history loading"

# Configuration changes
git commit -m "config: Update Expo SDK to v53"
```

---

## Creating Releases

### Tag a Version

```bash
# Create version tag
git tag -a v1.0.0 -m "Release v1.0.0 - Initial stable release"

# Push tag to GitHub
git push origin v1.0.0
```

### Create GitHub Release

1. Go to repository → Releases → "Create a new release"
2. Choose tag: v1.0.0
3. Release title: "CallBunker Mobile v1.0.0"
4. Description:
   ```
   ## Features
   - Native device calling with caller ID spoofing
   - Multi-user support with automatic number assignment
   - 10+ language support
   - Call history and trusted contacts
   - Anonymous messaging
   
   ## Installation
   Download APK below or see README for build instructions.
   ```
5. Attach APK file (if built)
6. Click "Publish release"

---

## Repository Best Practices

### README Badges (Optional)

Add badges to README.md for professional look:

```markdown
![React Native](https://img.shields.io/badge/React%20Native-0.79-blue)
![Expo](https://img.shields.io/badge/Expo-53-black)
![License](https://img.shields.io/badge/License-Proprietary-red)
```

### GitHub Actions (CI/CD)

Create `.github/workflows/build.yml` for automatic builds:

```yaml
name: Build APK
on:
  push:
    branches: [ main ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm install
      - run: eas build --platform android --non-interactive
```

### Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug Report
about: Report a bug in CallBunker mobile app
---

## Bug Description
A clear description of the bug.

## Steps to Reproduce
1. Go to...
2. Click on...
3. See error

## Expected Behavior
What should happen.

## Screenshots
If applicable, add screenshots.

## Environment
- Device: [e.g. Samsung Galaxy S21]
- Android Version: [e.g. 13]
- App Version: [e.g. 1.0.0]
```

---

## Protecting Sensitive Information

### Files Already Protected

The `.gitignore` file prevents committing:
- `*.keystore` (signing keys)
- `.env` (environment secrets)
- `node_modules/`
- Build artifacts

### Verify No Secrets Committed

```bash
# Search for potential API keys
git log -p | grep -i "api_key\|secret\|password"

# If found, remove from history:
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch PATH/TO/FILE" \
  --prune-empty --tag-name-filter cat -- --all
```

### GitHub Secrets (for Actions)

If using GitHub Actions:

1. Repository → Settings → Secrets → Actions
2. Add secrets:
   - `EXPO_TOKEN`
   - `BACKEND_URL`
3. Reference in workflows: `${{ secrets.EXPO_TOKEN }}`

---

## Clone and Run Instructions

### For New Developers

Share this with anyone who needs to work on the app:

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/callbunker-mobile.git
cd callbunker-mobile

# 2. Install dependencies
npm install

# 3. Configure backend
# Edit src/services/CallBunkerContext.js
# Set API_BASE_URL to your backend

# 4. Run on Android
npm run android

# 5. Build APK
eas build --platform android --profile preview
```

---

## Troubleshooting Upload Issues

### Authentication Failed

```bash
# Use personal access token instead of password
# Generate at: https://github.com/settings/tokens

# When prompted for password, use token instead
```

### Large Files Rejected

```bash
# Remove large files from commit
git reset HEAD path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore
```

### Wrong Remote URL

```bash
# Check current remote
git remote -v

# Update remote URL
git remote set-url origin https://github.com/YOUR_USERNAME/callbunker-mobile.git
```

---

## Quick Reference Commands

```bash
# Check status
git status

# Add all changes
git add .

# Commit changes
git commit -m "Your message"

# Push to GitHub
git push

# Pull latest changes
git pull

# Create new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# Merge branch
git merge feature/new-feature

# View commit history
git log --oneline
```

---

## Final Checklist

Before sharing repository:

- [ ] All files uploaded successfully
- [ ] README.md displays correctly
- [ ] No sensitive information committed
- [ ] .gitignore configured properly
- [ ] Backend URL set to placeholder (not localhost)
- [ ] License file added (if applicable)
- [ ] Repository description added
- [ ] Topics/tags added for discoverability
- [ ] Collaborators invited
- [ ] First release created (with APK attached)

---

**Your repository is now live!** 🚀

Share the link with your developer:
```
https://github.com/YOUR_USERNAME/callbunker-mobile
```

They can clone, install, and start developing immediately!
