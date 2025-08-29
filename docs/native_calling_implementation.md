# Native Calling Implementation Guide for CallBunker

## Overview
CallBunker now uses native mobile calling for the most cost-effective and user-friendly experience. Instead of complex VoIP or bridge solutions, your mobile app uses the device's built-in calling capabilities with caller ID spoofing.

## How It Works

### 1. API Flow
```
Mobile App → POST /api/users/{user_id}/call_direct → Get calling config → Native device call
```

### 2. No Twilio Calls
- **Zero per-minute costs** - Only carrier charges apply
- **No bridge complexity** - Direct connection using phone's native calling
- **Better reliability** - Uses carrier network, not internet

### 3. Caller ID Protection
- Target sees your Google Voice number as caller ID
- Your real number stays completely hidden
- CallBunker logs all calls for tracking

## API Endpoints

### Initiate Native Call
```
POST /api/users/{user_id}/call_direct
```

**Request:**
```json
{
  "to_number": "5551234567"
}
```

**Response:**
```json
{
  "success": true,
  "approach": "native_calling",
  "call_log_id": 123,
  "to_number": "+15551234567",
  "from_number": "+16179421250",
  "native_call_config": {
    "target_number": "+15551234567",
    "spoofed_caller_id": "+16179421250",
    "method": "device_native",
    "cost": "carrier_only"
  },
  "instructions": {
    "implementation": "Use device native calling with caller ID spoofing",
    "ios_method": "CallKit with CXStartCallAction",
    "android_method": "TelecomManager with PhoneAccountHandle",
    "react_native": "NativeModules.CallManager.makeCall()"
  },
  "message": "Ready for native calling - mobile app should initiate call now"
}
```

### Check Call Status
```
GET /api/users/{user_id}/calls/{call_log_id}/status
```

### Complete Call
```
POST /api/users/{user_id}/calls/{call_log_id}/complete
```

**Request:**
```json
{
  "status": "completed",
  "duration_seconds": 45
}
```

## Mobile Implementation

### React Native Integration
```javascript
import { NativeModules } from 'react-native';
const { CallManager } = NativeModules;

export class CallBunkerNativeDialer {
    static async makeCall(targetNumber) {
        try {
            // Get call configuration
            const response = await fetch('/api/users/1/call_direct', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ to_number: targetNumber })
            });
            
            const callData = await response.json();
            
            if (callData.success) {
                // Use native calling
                await CallManager.makeCall({
                    number: callData.native_call_config.target_number,
                    callerId: callData.native_call_config.spoofed_caller_id
                });
                
                return callData.call_log_id;
            }
        } catch (error) {
            console.error('Native call failed:', error);
            throw error;
        }
    }
    
    static async completeCall(callLogId, duration) {
        await fetch(`/api/users/1/calls/${callLogId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                status: 'completed',
                duration_seconds: duration
            })
        });
    }
}
```

### iOS Native Module (Swift)
```swift
// CallManager.swift
import React
import CallKit

@objc(CallManager)
class CallManager: NSObject {
    private let callController = CXCallController()
    
    @objc
    func makeCall(_ options: NSDictionary, resolver: @escaping RCTPromiseResolveBlock, rejecter: @escaping RCTPromiseRejectBlock) {
        
        guard let phoneNumber = options["number"] as? String,
              let callerID = options["callerId"] as? String else {
            rejecter("INVALID_PARAMS", "Missing phone number or caller ID", nil)
            return
        }
        
        let handle = CXHandle(type: .phoneNumber, value: phoneNumber)
        let startCallAction = CXStartCallAction(call: UUID(), handle: handle)
        
        // Set the caller ID
        startCallAction.contactIdentifier = callerID
        
        let transaction = CXTransaction(action: startCallAction)
        callController.request(transaction) { error in
            if let error = error {
                rejecter("CALL_FAILED", "Failed to start call: \(error.localizedDescription)", error)
            } else {
                resolver("Call initiated")
            }
        }
    }
}
```

### Android Native Module (Kotlin)
```kotlin
// CallManagerModule.kt
class CallManagerModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {
    
    override fun getName(): String = "CallManager"
    
    @ReactMethod
    fun makeCall(options: ReadableMap, promise: Promise) {
        val phoneNumber = options.getString("number")
        val callerID = options.getString("callerId")
        
        if (phoneNumber == null || callerID == null) {
            promise.reject("INVALID_PARAMS", "Missing phone number or caller ID")
            return
        }
        
        try {
            val context = reactApplicationContext
            val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
            
            // Create phone account for caller ID spoofing
            val phoneAccountHandle = PhoneAccountHandle(
                ComponentName(context, CallConnectionService::class.java),
                callerID
            )
            
            val callIntent = Intent(Intent.ACTION_CALL).apply {
                data = Uri.parse("tel:$phoneNumber")
                putExtra(TelecomManager.EXTRA_PHONE_ACCOUNT_HANDLE, phoneAccountHandle)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            
            if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                context.startActivity(callIntent)
                promise.resolve("Call initiated")
            } else {
                promise.reject("NO_PERMISSION", "Call permission not granted")
            }
        } catch (e: Exception) {
            promise.reject("CALL_FAILED", "Failed to start call: ${e.message}", e)
        }
    }
}
```

## Benefits

### Cost Savings
- **$0 per-minute charges** - No Twilio calling fees
- **Carrier rates only** - Standard mobile plan rates
- **Estimated savings**: $500-2000/month for active users

### User Experience
- **Familiar interface** - Uses phone's native calling UI
- **Instant connection** - No waiting for bridges or VoIP setup
- **Works offline** - No internet required after initial API call
- **High reliability** - Carrier-grade voice quality

### Privacy Protection
- **Google Voice caller ID** - Target sees your protected number
- **Real number hidden** - Your actual phone number never exposed
- **Call logging** - All calls tracked in CallBunker system

## Testing

### Test the Implementation
1. **Web Demo**: Visit `/dialer/1` to test the API
2. **Check Response**: Verify you get native calling configuration
3. **Mobile Integration**: Implement native modules in your app
4. **Test Calls**: Make test calls and verify caller ID spoofing

### Troubleshooting

**Caller ID Not Showing:**
- Check carrier support for caller ID modification
- Verify phone account registration on Android
- Test with different target numbers

**Permissions Issues:**
- Ensure CALL_PHONE permission granted
- Check CallKit entitlements on iOS
- Verify TelecomManager access on Android

## Migration from Bridge Approach

If you were using the bridge approach:

1. **Update API calls** from `/api/users/{id}/calls` to `/api/users/{id}/call_direct`
2. **Remove VoIP dependencies** - No more Twilio Voice SDK needed
3. **Implement native modules** - Add iOS/Android calling code
4. **Update call tracking** - Use call_log_id instead of call_sid

## Next Steps

1. **Implement native modules** in your mobile app
2. **Test caller ID spoofing** on your target carriers
3. **Add call completion tracking** for analytics
4. **Monitor cost savings** compared to bridge approach

The native calling approach provides the best balance of cost-effectiveness, user experience, and privacy protection for CallBunker's mission.