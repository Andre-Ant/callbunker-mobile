# CallBunker Mobile App - Production Configuration Guide

## ⚠️ REQUIRED STEPS BEFORE BUILDING APK

### Step 1: Configure Backend URL

Open `src/services/CallBunkerContext.js` and update the API_BASE_URL (line 10):

```javascript
// Change this line:
const API_BASE_URL = 'http://localhost:5000';

// To your deployed backend URL:
const API_BASE_URL = 'https://your-callbunker-backend.repl.co';
```

### Step 2: Verify Backend Endpoints

Ensure your backend has these multi-user endpoints working:
- `POST /multi/signup` - User registration
- `POST /multi/login` - User authentication  
- `POST /multi/user/{id}/call_direct` - Initiate protected calls
- `GET /multi/user/{id}/calls` - Fetch call history
- `GET /multi/user/{id}/contacts` - Fetch trusted contacts
- `POST /multi/user/{id}/contacts` - Add trusted contact
- `DELETE /multi/user/{id}/contacts/{contact_id}` - Remove contact
- `POST /multi/user/{id}/send_message` - Send anonymous message

### Step 3: Build APK

Follow the instructions in `APK_BUILD_GUIDE.md` to build your APK using:
- **Expo EAS** (recommended for simplicity)
- **Android Studio** (for full control)
- **Gradle CLI** (for CI/CD pipelines)

## What's Fixed in This Version

### ✅ Multi-User Support
- No hardcoded user IDs - each user gets their own isolated experience
- Automatic Defense Number assignment per user
- Proper authentication flow with AsyncStorage persistence

### ✅ Auth Timing Bug Fixed
- `loadSavedData()` now properly loads contacts and call history on app startup
- Fixed race condition where userId wasn't available immediately after dispatch

### ✅ Defensive Null Checks
- All API methods validate userId before making requests
- Graceful error handling for unauthenticated requests

### ✅ ContactsScreen Navigation
- Cleaned up duplicate code (857 → 494 lines)
- "Call" button now navigates to Dialer with phone number pre-filled
- Proper contact management with add/remove functionality

### ✅ MessagesScreen Complete
- Fully functional anonymous messaging
- Sends from user's Defense Number
- Proper validation and error handling

### ✅ SignupScreen Security
- Removed hardcoded PIN ("1122") and verbal code ("open sesame")
- All fields now required with validation
- Secure PIN input with masking

### ✅ Clear Configuration
- Prominent API URL configuration with detailed comments
- Easy one-line change for production deployment

## Testing Checklist

Before distributing your APK:

1. ✅ Backend URL configured correctly
2. ✅ User can sign up and receive Defense Number
3. ✅ User can log in and stay logged in (persistence works)
4. ✅ Protected calls work and display Twilio caller ID
5. ✅ Call history loads on app startup
6. ✅ Trusted contacts load on app startup
7. ✅ Can add/remove trusted contacts
8. ✅ Anonymous messaging works with Defense Number
9. ✅ Navigation between all screens works smoothly

## Support

For issues or questions:
1. Check `GET_STARTED.md` for setup instructions
2. Review `APK_BUILD_GUIDE.md` for build troubleshooting
3. Verify backend endpoints are responding correctly
4. Check React Native logs: `npx react-native log-android` or `log-ios`

## File Structure

```
GITHUB_REPO/
├── src/
│   ├── services/
│   │   ├── CallBunkerContext.js    ← **CONFIGURE API URL HERE**
│   │   └── CallBunkerNative.js
│   └── screens/
│       ├── DialerScreen.js
│       ├── ContactsScreen.js
│       ├── MessagesScreen.js
│       ├── SignupScreen.js
│       └── ... (4 more screens)
├── App.js
├── package.json
├── GET_STARTED.md
├── APK_BUILD_GUIDE.md
└── CONFIGURATION_GUIDE.md          ← **YOU ARE HERE**
```

---

**Ready to build? Update the API URL and follow APK_BUILD_GUIDE.md!**
