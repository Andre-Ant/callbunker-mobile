//
//  CallManager.m
//  React Native Bridge for CallManager
//

#import <React/RCTBridgeModule.h>

@interface RCT_EXTERN_MODULE(CallManager, NSObject)

// Make a call with caller ID spoofing
RCT_EXTERN_METHOD(makeCall:(NSDictionary *)options
                  resolver:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject)

// Check if device can make calls
RCT_EXTERN_METHOD(canMakeCalls:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject)

// Test caller ID support
RCT_EXTERN_METHOD(testCallerIDSupport:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject)

// End an active call
RCT_EXTERN_METHOD(endCall:(NSString *)callId
                  resolver:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject)

// Get active call info
RCT_EXTERN_METHOD(getActiveCall:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject)

@end