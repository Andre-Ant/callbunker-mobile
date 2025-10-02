import React, { createContext, useContext, useReducer, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import CallBunkerNative from './CallBunkerNative';

const CallBunkerContext = createContext();

//=============================================================================
// ⚠️  CONFIGURATION REQUIRED - UPDATE BEFORE BUILDING APK
//=============================================================================
// Set this to your deployed CallBunker backend URL:
const API_BASE_URL = 'http://localhost:5000';

// PRODUCTION EXAMPLE:
// const API_BASE_URL = 'https://your-callbunker-backend.repl.co';
//
// For Replit deployments, use your Replit app URL
// For custom domains, use: https://api.yourdomain.com
//=============================================================================

const initialState = {
  // Authentication state
  isAuthenticated: false,
  user: null,
  userId: null,
  defenseNumber: null,
  
  // App state
  isLoading: false,
  error: null,
  
  // Call state
  activeCalls: [],
  callHistory: [],
  voiceReady: false, // Tracks if Twilio system is ready for outgoing calls
  
  // Contacts
  trustedContacts: [],
  
  // Settings
  settings: {
    enableNotifications: true,
    soundEnabled: true,
    vibrationEnabled: true,
    theme: 'light',
  },
};

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_AUTHENTICATED':
      return { ...state, isAuthenticated: action.payload };
    case 'SET_USER':
      return { 
        ...state, 
        user: action.payload,
        userId: action.payload?.id || null,
        defenseNumber: action.payload?.defenseNumber || null
      };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'ADD_CALL':
      return { 
        ...state, 
        activeCalls: [...state.activeCalls, action.payload] 
      };
    case 'UPDATE_CALL':
      return {
        ...state,
        activeCalls: state.activeCalls.map(call =>
          call.id === action.payload.id ? { ...call, ...action.payload } : call
        )
      };
    case 'COMPLETE_CALL':
      return {
        ...state,
        activeCalls: state.activeCalls.filter(call => call.id !== action.payload.id),
        callHistory: [action.payload, ...state.callHistory]
      };
    case 'SET_CALL_HISTORY':
      return { ...state, callHistory: action.payload };
    case 'ADD_TRUSTED_CONTACT':
      return {
        ...state,
        trustedContacts: [...state.trustedContacts, action.payload]
      };
    case 'REMOVE_TRUSTED_CONTACT':
      return {
        ...state,
        trustedContacts: state.trustedContacts.filter(contact => 
          contact.id !== action.payload
        )
      };
    case 'SET_TRUSTED_CONTACTS':
      return { ...state, trustedContacts: action.payload };
    case 'UPDATE_SETTINGS':
      return { 
        ...state, 
        settings: { ...state.settings, ...action.payload } 
      };
    case 'SET_VOICE_READY':
      return { ...state, voiceReady: action.payload };
    case 'LOGOUT':
      return initialState;
    default:
      return state;
  }
}

export function CallBunkerProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  useEffect(() => {
    // Load saved settings and auth state on app start
    loadSavedData();
  }, []);

  // Create CallBunker Native instance with current userId
  const getCallBunkerInstance = () => {
    return new CallBunkerNative(API_BASE_URL, state.userId);
  };

  const loadSavedData = async () => {
    try {
      // Load auth state first
      const authState = await AsyncStorage.getItem('callbunker_auth');
      let authenticatedUserId = null;
      
      if (authState) {
        const userData = JSON.parse(authState);
        if (userData && userData.id) {
          authenticatedUserId = userData.id;
          dispatch({type: 'SET_AUTHENTICATED', payload: true});
          dispatch({type: 'SET_USER', payload: userData});
        }
      }

      // Load settings
      const savedSettings = await AsyncStorage.getItem('callbunker_settings');
      if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        dispatch({type: 'UPDATE_SETTINGS', payload: settings});
      }

      // Load contacts and call history if authenticated
      // Use the authenticatedUserId from storage, not state (timing issue fix)
      if (authenticatedUserId) {
        // Create temporary CallBunker instance with authenticated user ID
        const tempCallBunker = new CallBunkerNative(API_BASE_URL, authenticatedUserId);
        
        try {
          const contacts = await fetch(`${API_BASE_URL}/multi/user/${authenticatedUserId}/contacts`);
          if (contacts.ok) {
            const data = await contacts.json();
            dispatch({type: 'SET_TRUSTED_CONTACTS', payload: data.contacts || []});
          }
        } catch (error) {
          console.error('Error loading contacts on startup:', error);
        }

        try {
          const history = await tempCallBunker.getCallHistory();
          dispatch({type: 'SET_CALL_HISTORY', payload: history});
        } catch (error) {
          console.error('Error loading call history on startup:', error);
        }
      }

    } catch (error) {
      console.error('Error loading saved data:', error);
    }
  };

  const signupUser = async (userData) => {
    try {
      dispatch({type: 'SET_LOADING', payload: true});
      dispatch({type: 'SET_ERROR', payload: null});
      
      // Validate required fields
      if (!userData.name || !userData.email || !userData.pin || !userData.verbalCode) {
        throw new Error('All fields are required');
      }

      // Validate PIN (must be 4 digits)
      if (!/^\d{4}$/.test(userData.pin)) {
        throw new Error('PIN must be 4 digits');
      }

      // Validate verbal code (not empty)
      if (userData.verbalCode.trim().length < 3) {
        throw new Error('Verbal code must be at least 3 characters');
      }
      
      const realPhoneNumber = userData.realPhoneNumber ? userData.realPhoneNumber.replace(/\D/g, '') : '';
      
      const response = await fetch(`${API_BASE_URL}/multi/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          name: userData.name,
          email: userData.email,
          real_phone_number: realPhoneNumber,
          pin: userData.pin,
          verbal_code: userData.verbalCode,
        }),
      });

      const responseText = await response.text();
      console.log('Signup response:', responseText);

      if (response.ok && (responseText.includes('Account created') || responseText.includes('Defense Number'))) {
        // Extract defense number and user ID from response
        const defenseNumberMatch = responseText.match(/(\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/);
        const defenseNumber = defenseNumberMatch ? defenseNumberMatch[0] : null;
        
        // Extract user ID if available in response
        const userIdMatch = responseText.match(/user_id[:\s]+(\d+)/i);
        const userId = userIdMatch ? parseInt(userIdMatch[1]) : Date.now(); // Fallback to timestamp
        
        const user = {
          id: userId,
          name: userData.name,
          email: userData.email,
          defenseNumber: defenseNumber
        };
        
        // Save auth state
        await AsyncStorage.setItem('callbunker_auth', JSON.stringify(user));
        
        dispatch({type: 'SET_AUTHENTICATED', payload: true});
        dispatch({type: 'SET_USER', payload: user});
        
        return { success: true, defenseNumber };
      }
      
      throw new Error(responseText || 'Signup failed - please check your information');
      
    } catch (error) {
      console.error('Signup error:', error);
      dispatch({type: 'SET_ERROR', payload: error.message});
      throw error;
    } finally {
      dispatch({type: 'SET_LOADING', payload: false});
    }
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem('callbunker_auth');
      await AsyncStorage.removeItem('callbunker_contacts');
      dispatch({type: 'LOGOUT'});
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const makeCall = async (phoneNumber) => {
    try {
      if (!state.userId) {
        throw new Error('User not authenticated');
      }

      dispatch({type: 'SET_LOADING', payload: true});
      dispatch({type: 'SET_ERROR', payload: null});
      
      console.log(`[CallBunkerProvider] Initiating call to ${phoneNumber}`);
      
      const callBunker = getCallBunkerInstance();
      const result = await callBunker.makeCall(phoneNumber);
      
      // Add to call history
      const callInfo = {
        id: result.callLogId,
        phoneNumber: result.targetNumber,
        callerIdShown: result.callerIdShown || state.defenseNumber,
        status: 'completed',
        timestamp: new Date().toISOString(),
        direction: 'outbound'
      };
      
      dispatch({type: 'ADD_CALL', payload: callInfo});
      
      console.log('[CallBunkerProvider] Call initiated successfully:', result);
      return result;
      
    } catch (error) {
      console.error('[CallBunkerProvider] Call failed:', error);
      dispatch({type: 'SET_ERROR', payload: error.message});
      throw error;
    } finally {
      dispatch({type: 'SET_LOADING', payload: false});
    }
  };

  const completeCall = async (callId, duration = 0, status = 'completed') => {
    try {
      if (!state.userId) return;

      const callBunker = getCallBunkerInstance();
      await callBunker.completeCall(callId, duration, status);
      
      console.log(`[CallBunkerProvider] Call ${callId} completed`);
      
    } catch (error) {
      console.error('[CallBunkerProvider] Error completing call:', error);
    }
  };

  const loadCallHistory = async () => {
    try {
      if (!state.userId) return;

      const callBunker = getCallBunkerInstance();
      const history = await callBunker.getCallHistory();
      dispatch({type: 'SET_CALL_HISTORY', payload: history});
    } catch (error) {
      console.error('Error loading call history:', error);
      dispatch({type: 'SET_CALL_HISTORY', payload: []});
    }
  };

  const loadContacts = async () => {
    try {
      if (!state.userId) return;

      const response = await fetch(`${API_BASE_URL}/multi/user/${state.userId}/contacts`);
      if (response.ok) {
        const data = await response.json();
        dispatch({type: 'SET_TRUSTED_CONTACTS', payload: data.contacts || []});
      }
    } catch (error) {
      console.error('Error loading contacts:', error);
      dispatch({type: 'SET_TRUSTED_CONTACTS', payload: []});
    }
  };

  const addTrustedContact = async (contact) => {
    try {
      if (!state.userId) {
        throw new Error('User not authenticated');
      }

      const response = await fetch(`${API_BASE_URL}/multi/user/${state.userId}/contacts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone_number: contact.phone_number,
          name: contact.name,
          custom_pin: contact.custom_pin || null
        }),
      });

      if (response.ok) {
        const data = await response.json();
        await loadContacts(); // Reload contacts to get updated list
        return data;
      } else {
        throw new Error('Failed to add contact');
      }
      
    } catch (error) {
      console.error('Error adding contact:', error);
      dispatch({type: 'SET_ERROR', payload: 'Failed to add contact'});
      throw error;
    }
  };

  const removeTrustedContact = async (contactId) => {
    try {
      if (!state.userId) {
        throw new Error('User not authenticated');
      }

      const response = await fetch(`${API_BASE_URL}/multi/user/${state.userId}/contacts/${contactId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        dispatch({type: 'REMOVE_TRUSTED_CONTACT', payload: contactId});
      } else {
        throw new Error('Failed to remove contact');
      }
      
    } catch (error) {
      console.error('Error removing contact:', error);
      dispatch({type: 'SET_ERROR', payload: 'Failed to remove contact'});
      throw error;
    }
  };

  const sendMessage = async (toNumber, message) => {
    try {
      if (!state.userId) {
        throw new Error('User not authenticated');
      }

      dispatch({type: 'SET_LOADING', payload: true});
      
      const response = await fetch(`${API_BASE_URL}/multi/user/${state.userId}/send_message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to_number: toNumber,
          message: message
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        const error = await response.text();
        throw new Error(error || 'Failed to send message');
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      dispatch({type: 'SET_ERROR', payload: error.message});
      throw error;
    } finally {
      dispatch({type: 'SET_LOADING', payload: false});
    }
  };

  const updateSettings = async (newSettings) => {
    try {
      const updatedSettings = {...state.settings, ...newSettings};
      
      // Save to AsyncStorage
      await AsyncStorage.setItem('callbunker_settings', JSON.stringify(updatedSettings));
      
      dispatch({type: 'UPDATE_SETTINGS', payload: newSettings});
      
    } catch (error) {
      console.error('Error updating settings:', error);
      dispatch({type: 'SET_ERROR', payload: 'Failed to update settings'});
    }
  };

  const checkVoiceReady = async () => {
    try {
      if (!state.userId) {
        console.warn('[CallBunker] Cannot check voice ready - user not authenticated');
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/multi/user/${state.userId}/settings`);
      
      if (response.ok) {
        const settings = await response.json();
        const isReady = settings.twilio_number_configured === true;
        dispatch({type: 'SET_VOICE_READY', payload: isReady});
        return isReady;
      }
      
      return false;
    } catch (error) {
      console.error('Error checking voice ready status:', error);
      return false;
    }
  };

  const clearError = () => {
    dispatch({type: 'SET_ERROR', payload: null});
  };

  const contextValue = {
    ...state,
    apiUrl: API_BASE_URL,
    signupUser,
    logout,
    makeCall,
    completeCall,
    addTrustedContact,
    removeTrustedContact,
    sendMessage,
    updateSettings,
    loadCallHistory,
    loadContacts,
    checkVoiceReady,
    clearError,
  };

  return (
    <CallBunkerContext.Provider value={contextValue}>
      {children}
    </CallBunkerContext.Provider>
  );
}

export function useCallBunker() {
  const context = useContext(CallBunkerContext);
  if (context === undefined) {
    throw new Error('useCallBunker must be used within a CallBunkerProvider');
  }
  return context;
}
