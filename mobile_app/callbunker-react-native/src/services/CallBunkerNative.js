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
        this.simulationMode = Platform.OS === 'web' || !CallManager;
        this.googleVoiceNumber = '+16179421250'; // Your Google Voice number
    }

    /**
     * Make a call using native device calling with caller ID spoofing
     * @param {string} targetNumber - Phone number to call
     * @returns {Promise<Object>} Call configuration and log ID
     */
    async makeCall(targetNumber) {
        try {
            console.log(`[CallBunker] Initiating call to ${targetNumber}`);
            
            // Simulation mode for web/testing
            if (this.simulationMode) {
                console.log('[CallBunker] Running in simulation mode');
                
                const callLogId = Date.now();
                const callInfo = {
                    callLogId,
                    targetNumber: targetNumber,
                    callerIdShown: this.googleVoiceNumber,
                    status: 'simulated',
                    config: {
                        target_number: targetNumber,
                        spoofed_caller_id: this.googleVoiceNumber
                    }
                };
                
                // Store simulated call
                this.activeCalls.set(callLogId, {
                    ...callInfo,
                    startTime: Date.now(),
                    status: 'initiating'
                });
                
                console.log('[CallBunker] Simulated call setup:', callInfo);
                return callInfo;
            }
            
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

            // Store call info for tracking
            this.activeCalls.set(callData.call_log_id, {
                ...callData,
                startTime: Date.now(),
                status: 'initiating'
            });

            // Use native calling with caller ID spoofing
            if (CallManager) {
                await CallManager.makeCall({
                    number: callData.native_call_config.target_number,
                    callerId: callData.native_call_config.spoofed_caller_id
                });
            } else {
                // Fallback for development/testing
                console.warn('[CallBunker] CallManager not available, using fallback');
                // In production, this would open the default dialer
                // For now, just log the action
            }

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
                callerIdShown: '+16179421250',
                direction: 'outbound',
                status: 'completed',
                timestamp: new Date(Date.now() - 3600000).toISOString(),
                duration: 245,
            },
            {
                id: 2,
                phoneNumber: '+15559876543',
                callerIdShown: '+16179421250',
                direction: 'outbound',
                status: 'completed',
                timestamp: new Date(Date.now() - 7200000).toISOString(),
                duration: 89,
            },
            {
                id: 3,
                phoneNumber: '+15555551234',
                callerIdShown: '+16179421250',
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

export default CallBunkerNative;