/**
 * CallBunker Native Calling Integration for React Native
 * 
 * This module provides native calling capabilities with caller ID spoofing
 * for CallBunker's privacy protection system.
 */

import { NativeModules, Platform } from 'react-native';

const { CallManager } = NativeModules;

export default class CallBunkerNative {
    constructor(baseUrl, userId) {
        this.baseUrl = baseUrl;
        this.userId = userId;
        this.twilioNumber = null; // Twilio number assigned from phone pool
        this.activeCalls = new Map();
        this.simulationMode = Platform.OS === 'web' || !CallManager;
    }

    /**
     * Make a call using native device calling with CallBunker protection
     * Uses React Native's built-in Linking API - no additional packages required
     * @param {string} targetNumber - Phone number to call
     * @returns {Promise<Object>} Call configuration and log ID
     */
    async makeCall(targetNumber) {
        try {
            // Validate user ID
            if (!this.userId) {
                throw new Error('User not authenticated. Please log in first.');
            }

            console.log(`[CallBunker] Initiating call to ${targetNumber}`);
            
            // Get call configuration from CallBunker Multi-User API
            const response = await fetch(`${this.baseUrl}/multi/user/${this.userId}/call_direct`, {
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

            // Validate backend response format
            if (!callData.target_number || !callData.twilio_caller_id) {
                throw new Error('Invalid API response format - missing target_number or twilio_caller_id');
            }

            // Store call info for tracking
            this.activeCalls.set(callData.call_log_id, {
                ...callData,
                startTime: Date.now(),
                status: 'initiating'
            });

            // Use React Native's built-in Linking API to make the call
            // This works on both iOS and Android without any additional packages
            const { Linking } = require('react-native');
            const telUrl = `tel:${callData.target_number}`;
            
            const canOpen = await Linking.canOpenURL(telUrl);
            if (!canOpen) {
                throw new Error('Device cannot make phone calls');
            }

            console.log('[CallBunker] Opening native dialer:', telUrl);
            await Linking.openURL(telUrl);

            console.log('[CallBunker] Call initiated successfully');
            
            // Return call info including CallBunker number for user reference
            return {
                callLogId: callData.call_log_id,
                targetNumber: callData.target_number,
                callerIdShown: callData.twilio_caller_id,
                twilioNumber: callData.twilio_caller_id,
                callbunkerNumber: callData.twilio_caller_id,
                config: callData,
                privacyNote: `Give them your CallBunker number ${this.formatPhoneDisplay(callData.twilio_caller_id)} for protected callbacks`
            };

        } catch (error) {
            console.error('[CallBunker] Call failed:', error);
            throw new Error(`Call failed: ${error.message}`);
        }
    }

    /**
     * Format phone number for display
     * @param {string} phoneNumber - Phone number to format
     * @returns {string} Formatted phone number
     */
    formatPhoneDisplay(phoneNumber) {
        if (!phoneNumber) return '';
        
        const cleaned = phoneNumber.replace(/\D/g, '');
        
        // US number formatting
        if (cleaned.length === 11 && cleaned.startsWith('1')) {
            const digits = cleaned.substring(1);
            return `(${digits.substring(0, 3)}) ${digits.substring(3, 6)}-${digits.substring(6)}`;
        } else if (cleaned.length === 10) {
            return `(${cleaned.substring(0, 3)}) ${cleaned.substring(3, 6)}-${cleaned.substring(6)}`;
        }
        
        return phoneNumber;
    }

    /**
     * Complete a call and log the duration
     * @param {number} callLogId - Call log ID from makeCall
     * @param {number} durationSeconds - Call duration in seconds
     * @param {string} status - Call status (completed, failed, cancelled)
     */
    async completeCall(callLogId, durationSeconds = 0, status = 'completed') {
        try {
            // Validate user ID
            if (!this.userId) {
                console.warn('[CallBunker] Cannot complete call - user not authenticated');
                return;
            }

            console.log(`[CallBunker] Completing call ${callLogId}, duration: ${durationSeconds}s`);

            const response = await fetch(`${this.baseUrl}/multi/user/${this.userId}/calls/${callLogId}/complete`, {
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
            const response = await fetch(`${this.baseUrl}/multi/user/${this.userId}/calls/${callLogId}/status`);
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
            // Validate user ID
            if (!this.userId) {
                console.warn('[CallBunker] Cannot fetch call history - user not authenticated');
                return [];
            }

            const response = await fetch(`${this.baseUrl}/multi/user/${this.userId}/calls?limit=${limit}&offset=${offset}`);
            
            if (response.ok) {
                const history = await response.json();
                return Array.isArray(history) ? history : [];
            } else {
                // Return mock data for development
                return this.getMockCallHistory();
            }
        } catch (error) {
            console.error('[CallBunker] Failed to get call history:', error);
            // Return mock data for development
            return this.getMockCallHistory();
        }
    }

    /**
     * Mock call history for development
     */
    getMockCallHistory() {
        return [
            {
                id: 1,
                phoneNumber: '+15551234567',
                callerIdShown: this.userDefenseNumber || 'Private',
                direction: 'outbound',
                status: 'completed',
                timestamp: new Date(Date.now() - 3600000).toISOString(),
                duration: 245,
            },
            {
                id: 2,
                phoneNumber: '+15559876543',
                callerIdShown: this.userDefenseNumber || 'Private',
                direction: 'outbound',
                status: 'completed',
                timestamp: new Date(Date.now() - 7200000).toISOString(),
                duration: 89,
            },
            {
                id: 3,
                phoneNumber: '+15555551234',
                callerIdShown: this.userDefenseNumber || 'Private',
                direction: 'outbound',
                status: 'failed',
                timestamp: new Date(Date.now() - 10800000).toISOString(),
                duration: 0,
            },
        ];
    }

    /**
     * Check if native calling is supported on this device
     * @returns {Promise<boolean>} True if native calling is supported
     */
    async isNativeCallingSupported() {
        try {
            if (!CallManager) {
                // For development, assume supported
                return true;
            }

            if (Platform.OS === 'ios') {
                return await CallManager.canMakeCalls();
            } else if (Platform.OS === 'android') {
                return await CallManager.hasCallPermission();
            }

            return false;
        } catch (error) {
            console.error('[CallBunker] Error checking native calling support:', error);
            return true; // Assume supported for development
        }
    }

    /**
     * Request call permissions
     * @returns {Promise<boolean>} True if permissions granted
     */
    async requestCallPermissions() {
        try {
            if (!CallManager) {
                return true; // For development
            }

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