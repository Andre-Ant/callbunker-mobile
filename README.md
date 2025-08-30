# CallBunker - Communication Security Platform

## 🛡️ Advanced Mobile Call Screening & Privacy Protection

CallBunker is a comprehensive communication security platform that provides intelligent call screening, authentication, and privacy protection through both web and native mobile applications.

### 🔥 Key Features
- **Call Screening**: PIN and verbal authentication to block unwanted calls
- **Native Mobile Calling**: Device-based calling with caller ID spoofing protection
- **Privacy Protection**: Google Voice integration for number privacy
- **Real-Time Analytics**: Track blocked calls and trusted contacts
- **DTMF Touch Tones**: Authentic phone dialer experience
- **Contact Management**: Unified trusted contacts with whitelist integration

## 📱 Mobile App - Ready for APK Build

### Latest Updates (August 30, 2025)
- ✅ **Real Analytics Data**: Statistics reflect actual blocked calls count
- ✅ **Seamless Whitelist**: Blocked numbers integrate directly into trusted contacts  
- ✅ **Enhanced Privacy**: Focus on unique PIN/voice authentication features
- ✅ **DTMF Audio**: Professional phone dialer with industry-standard touch tones
- ✅ **JavaScript Fixes**: All console errors resolved for smooth operation

### Quick APK Build
```bash
cd mobile_app/callbunker-build
npx eas login
npx eas build --platform android --profile preview
```

**Build Results:**
- 📦 APK Size: ~50MB with complete CallBunker features
- 📱 Compatibility: Android 6.0+ (API 23+)
- ⏱️ Build Time: 5-10 minutes via Expo cloud build

## 🚀 Getting Started

### For Developers
1. **Clone Repository**: `git clone [your-repo-url]`
2. **Install Dependencies**: `cd mobile_app/callbunker-build && npm install`
3. **Build APK**: Follow instructions in `UPDATED_APK_BUILD_GUIDE.md`

### For End Users
1. **Download APK**: Get latest build from releases or EAS dashboard
2. **Install App**: Enable "Unknown Sources" and install APK
3. **Setup CallBunker**: Configure your defense number and authentication

## 🏗️ Architecture

### Frontend
- **Web Interface**: Responsive Bootstrap design optimized for mobile
- **Mobile App**: React Native with Expo SDK 53
- **UI Framework**: Bootstrap with Replit dark theme
- **Audio**: Web Audio API for DTMF touch tones

### Backend
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL with SQLite fallback
- **Voice Services**: Twilio integration for call handling
- **Authentication**: PIN and verbal code verification

### Key Components
- **Call Screening Engine**: Multi-step verification with configurable retry logic
- **Contact Management**: Smart whitelist with automatic trust building
- **Analytics System**: Real-time data tracking and reporting
- **Privacy Layer**: Google Voice integration for number protection

## 🔧 Technical Specifications

### Mobile App
- **Platform**: React Native (iOS/Android)
- **Build System**: Expo Application Services (EAS)
- **Package**: com.callbunker.mobile
- **Permissions**: Phone, Internet, Call Management
- **Architecture**: Universal (ARM64, x86)

### Web Application
- **Framework**: Flask + SQLAlchemy
- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **Database**: PostgreSQL/SQLite
- **Deployment**: Gunicorn WSGI server

## 📋 Documentation

### Build Guides
- [`UPDATED_APK_BUILD_GUIDE.md`](UPDATED_APK_BUILD_GUIDE.md) - Complete APK build instructions
- [`DEVELOPER_HANDOFF_UPDATED.md`](DEVELOPER_HANDOFF_UPDATED.md) - Project overview and setup
- [`GITHUB_APK_BUILD_SETUP.md`](GITHUB_APK_BUILD_SETUP.md) - Repository deployment guide

### Technical Documentation
- [`replit.md`](replit.md) - System architecture and design decisions
- [`mobile_app/README.md`](mobile_app/README.md) - Mobile app specifications
- [`EXPO_BUILD_GUIDE.md`](EXPO_BUILD_GUIDE.md) - Original build setup guide

## 🛠️ Development

### Prerequisites
- Node.js 18+
- Python 3.11+
- Expo CLI (`npm install -g @expo/cli`)
- EAS CLI (`npm install -g eas-cli`)

### Local Development
```bash
# Backend
python main.py

# Mobile App
cd mobile_app/callbunker-build
npx expo start
```

### Environment Variables
```
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
DATABASE_URL=your_database_url
PUBLIC_APP_URL=your_app_url
```

## 🎯 Current Status

- ✅ **Web Interface**: Fully functional with all recent updates
- ✅ **Mobile App**: Ready for APK build with Expo SDK 53
- ✅ **Call Screening**: PIN/verbal authentication system complete
- ✅ **Analytics**: Real-time data display with actual usage statistics
- ✅ **Contact Management**: Unified whitelist and trusted contacts
- ✅ **Audio Features**: DTMF touch tones with authentic frequencies

## 📞 Features Overview

### Call Protection
- Intelligent call screening with customizable authentication
- PIN verification (currently: 8322)
- Verbal code authentication (currently: "Black widow")
- Automatic whitelist building for trusted callers

### Privacy Features
- Google Voice integration for outgoing call protection
- Caller ID spoofing prevention
- Defense number concept for business security
- Anonymous calling capabilities

### User Experience
- Mobile-optimized responsive design
- Authentic phone dialer with DTMF sounds
- Real-time analytics and usage tracking
- Intuitive contact management with batch operations

Your complete CallBunker communication security platform is ready for deployment and APK generation!