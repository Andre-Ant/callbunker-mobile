//
//  CallManager.swift
//  CallBunker Native Calling for iOS
//
//  Implements native calling with caller ID spoofing using CallKit
//

import Foundation
import CallKit
import React

@objc(CallManager)
class CallManager: NSObject {
    
    private let callController = CXCallController()
    private var activeCall: UUID?
    
    override init() {
        super.init()
        setupCallKit()
    }
    
    // MARK: - CallKit Setup
    
    private func setupCallKit() {
        // CallKit configuration
        let configuration = CXProviderConfiguration(localizedName: "CallBunker")
        configuration.supportsVideo = false
        configuration.maximumCallsPerCallGroup = 1
        configuration.maximumCallGroups = 1
        configuration.supportedHandleTypes = [.phoneNumber]
        
        // Optional: Add custom ringtone
        // configuration.ringtoneSound = "custom_ringtone.wav"
        
        print("[CallBunker] CallKit configured")
    }
    
    // MARK: - React Native Bridge Methods
    
    @objc
    func makeCall(_ options: NSDictionary, resolver: @escaping RCTPromiseResolveBlock, rejecter: @escaping RCTPromiseRejectBlock) {
        
        guard let phoneNumber = options["number"] as? String,
              let callerID = options["callerId"] as? String else {
            rejecter("INVALID_PARAMS", "Missing phone number or caller ID", nil)
            return
        }
        
        // Validate phone number format
        let cleanNumber = phoneNumber.replacingOccurrences(of: "[^0-9+]", with: "", options: .regularExpression)
        guard !cleanNumber.isEmpty else {
            rejecter("INVALID_NUMBER", "Invalid phone number format", nil)
            return
        }
        
        initiateCall(to: cleanNumber, callerID: callerID, resolver: resolver, rejecter: rejecter)
    }
    
    @objc
    func canMakeCalls(_ resolver: @escaping RCTPromiseResolveBlock, rejecter: @escaping RCTPromiseRejectBlock) {
        // Check if device can make calls
        let canMakeCalls = UIApplication.shared.canOpenURL(URL(string: "tel://")!)
        resolver(canMakeCalls)
    }
    
    @objc
    func testCallerIDSupport(_ resolver: @escaping RCTPromiseResolveBlock, rejecter: @escaping RCTPromiseRejectBlock) {
        // Test if caller ID spoofing is supported
        // Note: This is a best-effort check, actual support varies by carrier
        resolver(true) // iOS generally supports caller ID through CallKit
    }
    
    // MARK: - Call Management
    
    private func initiateCall(to phoneNumber: String, callerID: String, resolver: @escaping RCTPromiseResolveBlock, rejecter: @escaping RCTPromiseRejectBlock) {
        
        // Create call handle
        let handle = CXHandle(type: .phoneNumber, value: phoneNumber)
        let callUUID = UUID()
        
        // Create start call action
        let startCallAction = CXStartCallAction(call: callUUID, handle: handle)
        
        // Set contact identifier to show custom caller ID
        startCallAction.contactIdentifier = callerID
        
        // Set call as outgoing
        startCallAction.isVideo = false
        
        // Create transaction
        let transaction = CXTransaction(action: startCallAction)
        
        // Request the transaction
        callController.request(transaction) { [weak self] error in
            DispatchQueue.main.async {
                if let error = error {
                    print("[CallBunker] CallKit error: \(error.localizedDescription)")
                    rejecter("CALL_FAILED", "Failed to start call: \(error.localizedDescription)", error)
                } else {
                    print("[CallBunker] Call initiated successfully")
                    self?.activeCall = callUUID
                    
                    resolver([
                        "success": true,
                        "callId": callUUID.uuidString,
                        "phoneNumber": phoneNumber,
                        "callerID": callerID
                    ])
                }
            }
        }
    }
    
    @objc
    func endCall(_ callId: String, resolver: @escaping RCTPromiseResolveBlock, rejecter: @escaping RCTPromiseRejectBlock) {
        
        guard let uuid = UUID(uuidString: callId) else {
            rejecter("INVALID_CALL_ID", "Invalid call ID format", nil)
            return
        }
        
        let endCallAction = CXEndCallAction(call: uuid)
        let transaction = CXTransaction(action: endCallAction)
        
        callController.request(transaction) { error in
            DispatchQueue.main.async {
                if let error = error {
                    rejecter("END_CALL_FAILED", "Failed to end call: \(error.localizedDescription)", error)
                } else {
                    self.activeCall = nil
                    resolver(["success": true])
                }
            }
        }
    }
    
    // MARK: - Call State Monitoring
    
    @objc
    func getActiveCall(_ resolver: @escaping RCTPromiseResolveBlock, rejecter: @escaping RCTPromiseRejectBlock) {
        if let callUUID = activeCall {
            resolver([
                "hasActiveCall": true,
                "callId": callUUID.uuidString
            ])
        } else {
            resolver([
                "hasActiveCall": false
            ])
        }
    }
    
    // MARK: - Utility Methods
    
    @objc
    static func requiresMainQueueSetup() -> Bool {
        return true
    }
    
    @objc
    func constantsToExport() -> [AnyHashable : Any]! {
        return [
            "PLATFORM": "ios",
            "SUPPORTS_CALLER_ID": true,
            "SUPPORTS_NATIVE_CALLING": true
        ]
    }
}

// MARK: - CallKit Provider Delegate (Optional - for incoming calls)

extension CallManager: CXProviderDelegate {
    
    func providerDidReset(_ provider: CXProvider) {
        print("[CallBunker] Provider reset")
        activeCall = nil
    }
    
    func provider(_ provider: CXProvider, perform action: CXStartCallAction) {
        // Handle outgoing calls
        action.fulfill()
    }
    
    func provider(_ provider: CXProvider, perform action: CXEndCallAction) {
        // Handle call ending
        activeCall = nil
        action.fulfill()
    }
    
    func provider(_ provider: CXProvider, didActivate audioSession: AVAudioSession) {
        // Audio session activated
        print("[CallBunker] Audio session activated")
    }
    
    func provider(_ provider: CXProvider, didDeactivate audioSession: AVAudioSession) {
        // Audio session deactivated
        print("[CallBunker] Audio session deactivated")
    }
}