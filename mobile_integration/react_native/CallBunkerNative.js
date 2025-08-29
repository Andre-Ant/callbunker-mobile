/**
 * CallBunker Native Calling Integration for React Native
 * 
 * This module provides native calling capabilities with caller ID spoofing
 * for CallBunker's privacy protection system.
 */

import { NativeModules, Platform } from 'react-native';

const { CallManager } = NativeModules;

export class CallBunkerNative {
    constructor(baseUrl, userId) {
        this.baseUrl = baseUrl;
        this.userId = userId;
        this.activeCalls = new Map();
    }

    /**
     * Make a call using native device calling with caller ID spoofing
     * @param {string} targetNumber - Phone number to call
     * @returns {Promise<Object>} Call configuration and log ID
     */
    async makeCall(targetNumber) {
        try {
            console.log(`[CallBunker] Initiating native call to ${targetNumber}`);
            
            // Get call configuration from CallBunker API
            const response = await fetch(`${this.baseUrl}/api/users/${this.userId}/call_direct`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    to_number: targetNumber
                })
            });

            const callData = await response.json();

            if (!callData.success) {
                throw new Error(callData.error || 'Failed to get call configuration');
            }

            console.log('[CallBunker] Call configuration received:', callData);

            // Store call info for tracking
            this.activeCalls.set(callData.call_log_id, {
                ...callData,
                startTime: Date.now(),
                status: 'initiating'
            });

            // Use native calling with caller ID spoofing
            await CallManager.makeCall({
                number: callData.native_call_config.target_number,
                callerId: callData.native_call_config.spoofed_caller_id
            });

            console.log('[CallBunker] Native call initiated successfully');
            
            return {
                callLogId: callData.call_log_id,
                targetNumber: callData.to_number,
                callerIdShown: callData.from_number,
                config: callData.native_call_config
            };

        } catch (error) {
            console.error('[CallBunker] Call failed:', error);
            throw new Error(`Call failed: ${error.message}`);
        }
    }

    /**
     * Complete a call and log the duration
     * @param {number} callLogId - Call log ID from makeCall
     * @param {number} durationSeconds - Call duration in seconds
     * @param {string} status - Call status (completed, failed, cancelled)
     */
    async completeCall(callLogId, durationSeconds = 0, status = 'completed') {
        try {
            console.log(`[CallBunker] Completing call ${callLogId}, duration: ${durationSeconds}s`);

            const response = await fetch(`${this.baseUrl}/api/users/${this.userId}/calls/${callLogId}/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    status: status,
                    duration_seconds: durationSeconds
                })
            });

            const result = await response.json();
            
            // Remove from active calls
            this.activeCalls.delete(callLogId);
            
            console.log('[CallBunker] Call completion logged:', result);
            return result;

        } catch (error) {
            console.error('[CallBunker] Failed to complete call:', error);
            throw error;
        }
    }

    /**
     * Get call status
     * @param {number} callLogId - Call log ID
     * @returns {Promise<Object>} Call status information
     */
    async getCallStatus(callLogId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/users/${this.userId}/calls/${callLogId}/status`);
            const status = await response.json();
            
            return status;
        } catch (error) {
            console.error('[CallBunker] Failed to get call status:', error);
            throw error;
        }
    }

    /**
     * Get call history
     * @param {number} limit - Number of calls to retrieve
     * @param {number} offset - Offset for pagination
     * @returns {Promise<Array>} Array of call records
     */
    async getCallHistory(limit = 50, offset = 0) {
        try {
            const response = await fetch(`${this.baseUrl}/api/users/${this.userId}/calls?limit=${limit}&offset=${offset}`);
            const history = await response.json();
            
            return history;
        } catch (error) {
            console.error('[CallBunker] Failed to get call history:', error);
            throw error;
        }
    }

    /**
     * Check if native calling is supported on this device
     * @returns {Promise<boolean>} True if native calling is supported
     */
    async isNativeCallingSupported() {
        try {
            if (!CallManager) {
                return false;
            }

            if (Platform.OS === 'ios') {
                return await CallManager.canMakeCalls();
            } else if (Platform.OS === 'android') {
                return await CallManager.hasCallPermission();
            }

            return false;
        } catch (error) {
            console.error('[CallBunker] Error checking native calling support:', error);
            return false;
        }
    }

    /**
     * Request call permissions
     * @returns {Promise<boolean>} True if permissions granted
     */
    async requestCallPermissions() {
        try {
            if (Platform.OS === 'android') {
                return await CallManager.requestCallPermission();
            }
            // iOS permissions are handled automatically by CallKit
            return true;
        } catch (error) {
            console.error('[CallBunker] Error requesting call permissions:', error);
            return false;
        }
    }

    /**
     * Auto-complete calls that are still active (cleanup utility)
     */
    async cleanupActiveCalls() {
        const now = Date.now();
        const maxCallDuration = 10 * 60 * 1000; // 10 minutes

        for (const [callLogId, callInfo] of this.activeCalls) {
            const elapsed = now - callInfo.startTime;
            
            if (elapsed > maxCallDuration) {
                console.log(`[CallBunker] Auto-completing stale call ${callLogId}`);
                try {
                    await this.completeCall(callLogId, Math.floor(elapsed / 1000), 'auto_completed');
                } catch (error) {
                    console.error(`[CallBunker] Failed to auto-complete call ${callLogId}:`, error);
                }
            }
        }
    }
}

// Usage example:
/*
import { CallBunkerNative } from './CallBunkerNative';

// Initialize
const callBunker = new CallBunkerNative('https://your-callbunker-api.com', 1);

// Make a call
async function makeProtectedCall(phoneNumber) {
    try {
        // Check if native calling is supported
        const isSupported = await callBunker.isNativeCallingSupported();
        if (!isSupported) {
            throw new Error('Native calling not supported on this device');
        }

        // Make the call
        const callInfo = await callBunker.makeCall(phoneNumber);
        console.log('Call initiated:', callInfo);

        // The native dialer will open automatically
        // When the call ends, complete it
        // You'd typically track this through app state changes or call events
        
        return callInfo;
    } catch (error) {
        console.error('Failed to make call:', error);
        alert(`Call failed: ${error.message}`);
    }
}

// Complete a call when it ends
async function onCallEnded(callLogId, durationSeconds) {
    try {
        await callBunker.completeCall(callLogId, durationSeconds, 'completed');
        console.log('Call completion logged');
    } catch (error) {
        console.error('Failed to log call completion:', error);
    }
}
*/

export default CallBunkerNative;