# CallBunker Native Mobile Integration

This package provides complete native calling integration for CallBunker, enabling cost-effective mobile calling with caller ID spoofing while maintaining privacy protection.

## Overview

CallBunker's native calling approach eliminates per-minute charges by using the device's built-in calling capabilities with caller ID spoofing. Your target sees your Google Voice number while your real number stays completely hidden.

## Benefits

- **Zero per-minute costs** - Only carrier charges apply
- **Native call quality** - Uses carrier network, not internet
- **Privacy protection** - Google Voice number shown as caller ID
- **Familiar interface** - Standard phone app experience
- **Offline capability** - Works without internet after initial API call

## Package Structure

```
mobile_integration/
├── react_native/
│   └── CallBunkerNative.js         # Main React Native integration
├── ios/
│   ├── CallManager.swift           # iOS native module
│   └── CallManager.m              # React Native bridge
├── android/
│   ├── CallManagerModule.java     # Android native module
│   └── CallConnectionService.java # Android connection service
└── README.md                      # This file
```

## Quick Start

### 1. Install React Native Module

Copy the files to your React Native project:

```bash
# Copy React Native integration
cp react_native/CallBunkerNative.js src/services/

# Copy iOS files
cp ios/* ios/YourProject/

# Copy Android files
cp android/* android/app/src/main/java/com/yourproject/
```

### 2. iOS Setup

Add to your `ios/YourProject/Info.plist`:

```xml
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access to make calls</string>
```

### 3. Android Setup

Add to your `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.CALL_PHONE" />
<uses-permission android:name="android.permission.MANAGE_OWN_CALLS" />

<service
    android:name=".CallConnectionService"
    android:permission="android.permission.BIND_TELECOM_CONNECTION_SERVICE">
    <intent-filter>
        <action android:name="android.telecom.ConnectionService" />
    </intent-filter>
</service>
```

### 4. Initialize CallBunker

```javascript
import CallBunkerNative from './services/CallBunkerNative';

const callBunker = new CallBunkerNative('https://your-api.com', userId);
```

### 5. Make Your First Call

```javascript
async function makeCall(phoneNumber) {
    try {
        // Check if native calling is supported
        const isSupported = await callBunker.isNativeCallingSupported();
        if (!isSupported) {
            throw new Error('Native calling not supported');
        }

        // Make the call
        const callInfo = await callBunker.makeCall(phoneNumber);
        console.log('Call initiated:', callInfo);
        
        // The native dialer opens automatically
        // Target sees your Google Voice number as caller ID
        
        return callInfo;
    } catch (error) {
        console.error('Call failed:', error);
    }
}
```

## API Reference

### CallBunkerNative Class

#### Constructor
```javascript
new CallBunkerNative(baseUrl, userId)
```

#### Methods

##### `makeCall(targetNumber)`
Initiates a native call with caller ID spoofing.

**Parameters:**
- `targetNumber` (string): Phone number to call

**Returns:** Promise resolving to call information:
```javascript
{
    callLogId: 123,
    targetNumber: "+15551234567",
    callerIdShown: "+16179421250",
    config: { /* native call config */ }
}
```

##### `completeCall(callLogId, durationSeconds, status)`
Logs call completion for tracking.

**Parameters:**
- `callLogId` (number): Call log ID from makeCall
- `durationSeconds` (number): Call duration in seconds
- `status` (string): Call status ('completed', 'failed', 'cancelled')

##### `getCallStatus(callLogId)`
Gets current call status.

##### `getCallHistory(limit, offset)`
Retrieves call history.

##### `isNativeCallingSupported()`
Checks if native calling is supported on device.

##### `requestCallPermissions()`
Requests necessary call permissions.

## Platform-Specific Notes

### iOS Implementation

Uses CallKit framework for native calling integration:

- **CallKit integration** - Provides system-level call management
- **Caller ID spoofing** - Shows custom caller ID in native interface
- **Background capability** - Calls work even when app is backgrounded
- **VoIP entitlements** - May require VoIP background mode

### Android Implementation

Uses TelecomManager and PhoneAccount system:

- **Phone account registration** - Creates custom phone accounts for caller ID
- **Connection service** - Manages call connections
- **Permission handling** - Requires CALL_PHONE permission
- **API level requirements** - Requires Android 6.0+ (API 23) for full features

## Testing

### Test Native Calling Support

```javascript
// Check if device supports native calling
const isSupported = await callBunker.isNativeCallingSupported();
console.log('Native calling supported:', isSupported);

// Check permissions
const hasPermissions = await callBunker.requestCallPermissions();
console.log('Permissions granted:', hasPermissions);
```

### Test Call Flow

```javascript
// Make a test call
const callInfo = await callBunker.makeCall('+15551234567');

// Simulate call completion after 30 seconds
setTimeout(async () => {
    await callBunker.completeCall(callInfo.callLogId, 30, 'completed');
}, 30000);
```

## Troubleshooting

### Common Issues

**Caller ID not showing:**
- Check carrier support for caller ID modification
- Verify phone account registration on Android
- Test with different target numbers

**Permission errors:**
- Ensure CALL_PHONE permission is granted
- Check CallKit entitlements on iOS
- Verify TelecomManager access on Android

**Calls not initiating:**
- Check device telephony capabilities
- Verify API connectivity
- Test with simpler phone numbers

### Debug Logging

Enable debug logging in CallBunkerNative:

```javascript
// Add to constructor for detailed logging
console.log('[CallBunker] Debug mode enabled');
```

## Cost Analysis

### Traditional Bridge Approach
- Setup: $5,000-10,000
- Monthly: $20-50 (1000 calls)
- Annual: $5,240-10,600

### Native Calling Approach
- Setup: $2,000-5,000
- Monthly: $0 (carrier only)
- Annual: $2,000-5,000

**Savings: ~$3,000-5,000 per year**

## Security Considerations

- **Caller ID spoofing** may be detected by some carriers
- **Permission handling** requires careful user consent
- **Call logging** ensures audit trail for privacy compliance
- **API security** protects calling configuration

## Support

For implementation questions or issues:

1. Check the troubleshooting section
2. Review platform-specific documentation
3. Test with the web demo at `/dialer/1`
4. Verify API endpoint responses

## License

This integration is part of the CallBunker privacy protection system.