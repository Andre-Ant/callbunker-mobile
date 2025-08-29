package com.callbunker.native;

import android.net.Uri;
import android.telecom.Connection;
import android.telecom.ConnectionRequest;
import android.telecom.ConnectionService;
import android.telecom.PhoneAccountHandle;
import android.telecom.TelecomManager;

/**
 * CallBunker Connection Service for Android
 * 
 * Required for managing phone accounts and caller ID spoofing
 * on Android devices using the Telecom framework.
 */
public class CallConnectionService extends ConnectionService {
    
    @Override
    public Connection onCreateOutgoingConnection(PhoneAccountHandle connectionManagerPhoneAccount, 
                                               ConnectionRequest request) {
        
        // Extract phone number from request
        Uri handle = request.getAddress();
        if (handle == null) {
            return Connection.createFailedConnection(
                new android.telecom.DisconnectCause(android.telecom.DisconnectCause.ERROR, "No phone number provided")
            );
        }
        
        // Create connection
        CallBunkerConnection connection = new CallBunkerConnection();
        connection.setAddress(handle, TelecomManager.PRESENTATION_ALLOWED);
        connection.setInitializing();
        
        // Set caller display info from phone account
        PhoneAccountHandle accountHandle = request.getAccountHandle();
        if (accountHandle != null) {
            connection.setCallerDisplayName(accountHandle.getId(), TelecomManager.PRESENTATION_ALLOWED);
        }
        
        return connection;
    }
    
    /**
     * Custom Connection class for CallBunker calls
     */
    private static class CallBunkerConnection extends Connection {
        
        public CallBunkerConnection() {
            super();
            setAudioModeIsVoip(false); // Use cellular network, not VoIP
        }
        
        @Override
        public void onAnswer() {
            setActive();
        }
        
        @Override
        public void onReject() {
            setDisconnected(new android.telecom.DisconnectCause(android.telecom.DisconnectCause.REJECTED));
            destroy();
        }
        
        @Override
        public void onDisconnect() {
            setDisconnected(new android.telecom.DisconnectCause(android.telecom.DisconnectCause.LOCAL));
            destroy();
        }
        
        @Override
        public void onAbort() {
            setDisconnected(new android.telecom.DisconnectCause(android.telecom.DisconnectCause.CANCELED));
            destroy();
        }
        
        @Override
        public void onHold() {
            setOnHold();
        }
        
        @Override
        public void onUnhold() {
            setActive();
        }
    }
}