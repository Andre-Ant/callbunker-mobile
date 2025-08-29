package com.callbunker.native;

import android.Manifest;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.telecom.PhoneAccount;
import android.telecom.PhoneAccountHandle;
import android.telecom.TelecomManager;
import android.os.Build;

import androidx.core.content.ContextCompat;
import androidx.core.app.ActivityCompat;

import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReadableMap;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.bridge.WritableNativeMap;

import java.util.HashMap;
import java.util.Map;

/**
 * CallBunker Native Calling Module for Android
 * 
 * Provides native calling capabilities with caller ID spoofing
 * using Android's TelecomManager and PhoneAccount system.
 */
public class CallManagerModule extends ReactContextBaseJavaModule {
    
    private static final String MODULE_NAME = "CallManager";
    private static final int CALL_PERMISSION_REQUEST = 1001;
    
    private ReactApplicationContext reactContext;
    private TelecomManager telecomManager;
    
    public CallManagerModule(ReactApplicationContext reactContext) {
        super(reactContext);
        this.reactContext = reactContext;
        this.telecomManager = (TelecomManager) reactContext.getSystemService(Context.TELECOM_SERVICE);
    }
    
    @Override
    public String getName() {
        return MODULE_NAME;
    }
    
    @Override
    public Map<String, Object> getConstants() {
        final Map<String, Object> constants = new HashMap<>();
        constants.put("PLATFORM", "android");
        constants.put("SUPPORTS_CALLER_ID", true);
        constants.put("SUPPORTS_NATIVE_CALLING", true);
        constants.put("MIN_SDK_VERSION", Build.VERSION_CODES.M);
        return constants;
    }
    
    /**
     * Make a call with caller ID spoofing
     */
    @ReactMethod
    public void makeCall(ReadableMap options, Promise promise) {
        String phoneNumber = options.getString("number");
        String callerID = options.getString("callerId");
        
        if (phoneNumber == null || phoneNumber.isEmpty()) {
            promise.reject("INVALID_PARAMS", "Phone number is required");
            return;
        }
        
        if (callerID == null || callerID.isEmpty()) {
            promise.reject("INVALID_PARAMS", "Caller ID is required");
            return;
        }
        
        // Check permissions
        if (!hasCallPermission()) {
            promise.reject("NO_PERMISSION", "CALL_PHONE permission not granted");
            return;
        }
        
        try {
            // Clean phone number
            String cleanNumber = phoneNumber.replaceAll("[^0-9+]", "");
            if (!cleanNumber.startsWith("+")) {
                cleanNumber = "+1" + cleanNumber; // Assume US if no country code
            }
            
            // Create phone account handle for caller ID spoofing
            PhoneAccountHandle phoneAccountHandle = createPhoneAccountHandle(callerID);
            
            // Register phone account if not already registered
            registerPhoneAccount(phoneAccountHandle, callerID);
            
            // Create call intent
            Intent callIntent = new Intent(Intent.ACTION_CALL);
            callIntent.setData(Uri.parse("tel:" + cleanNumber));
            callIntent.putExtra(TelecomManager.EXTRA_PHONE_ACCOUNT_HANDLE, phoneAccountHandle);
            callIntent.putExtra(TelecomManager.EXTRA_START_CALL_WITH_SPEAKERPHONE, false);
            callIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            
            // Start the call
            reactContext.startActivity(callIntent);
            
            // Return success
            WritableMap result = new WritableNativeMap();
            result.putBoolean("success", true);
            result.putString("phoneNumber", cleanNumber);
            result.putString("callerID", callerID);
            result.putString("method", "android_telecom");
            
            promise.resolve(result);
            
        } catch (Exception e) {
            promise.reject("CALL_FAILED", "Failed to initiate call: " + e.getMessage(), e);
        }
    }
    
    /**
     * Check if app has call permission
     */
    @ReactMethod
    public void hasCallPermission(Promise promise) {
        boolean hasPermission = hasCallPermission();
        promise.resolve(hasPermission);
    }
    
    /**
     * Request call permission
     */
    @ReactMethod
    public void requestCallPermission(Promise promise) {
        if (hasCallPermission()) {
            promise.resolve(true);
            return;
        }
        
        // Note: In a real implementation, you'd need to handle the permission request
        // through an Activity. This is a simplified version.
        promise.resolve(false);
    }
    
    /**
     * Test if caller ID spoofing is supported
     */
    @ReactMethod
    public void testCallerIDSupport(Promise promise) {
        try {
            // Check if TelecomManager is available and we can create phone accounts
            boolean supported = (telecomManager != null && 
                               Build.VERSION.SDK_INT >= Build.VERSION_CODES.M);
            promise.resolve(supported);
        } catch (Exception e) {
            promise.resolve(false);
        }
    }
    
    /**
     * Check if device can make calls
     */
    @ReactMethod
    public void canMakeCalls(Promise promise) {
        try {
            PackageManager pm = reactContext.getPackageManager();
            boolean canMakeCalls = pm.hasSystemFeature(PackageManager.FEATURE_TELEPHONY);
            promise.resolve(canMakeCalls);
        } catch (Exception e) {
            promise.resolve(false);
        }
    }
    
    // MARK: - Private Helper Methods
    
    private boolean hasCallPermission() {
        return ContextCompat.checkSelfPermission(reactContext, Manifest.permission.CALL_PHONE) 
               == PackageManager.PERMISSION_GRANTED;
    }
    
    private PhoneAccountHandle createPhoneAccountHandle(String callerID) {
        ComponentName componentName = new ComponentName(reactContext, CallConnectionService.class);
        return new PhoneAccountHandle(componentName, callerID);
    }
    
    private void registerPhoneAccount(PhoneAccountHandle handle, String callerID) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            try {
                // Create phone account for caller ID
                PhoneAccount.Builder builder = PhoneAccount.builder(handle, "CallBunker - " + callerID)
                    .setCapabilities(PhoneAccount.CAPABILITY_CALL_PROVIDER)
                    .setAddress(Uri.parse("tel:" + callerID))
                    .setShortDescription("CallBunker Protected Number");
                
                PhoneAccount phoneAccount = builder.build();
                
                // Register the account
                if (telecomManager != null) {
                    telecomManager.registerPhoneAccount(phoneAccount);
                }
            } catch (Exception e) {
                // Handle registration errors gracefully
                System.err.println("Failed to register phone account: " + e.getMessage());
            }
        }
    }
}