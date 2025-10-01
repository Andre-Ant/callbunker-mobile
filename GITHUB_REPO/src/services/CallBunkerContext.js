import React, { createContext, useContext, useReducer, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import CallBunkerNative from './CallBunkerNative';

const CallBunkerContext = createContext();

const initialState = {
  // Authentication state
  isAuthenticated: false,
  user: null,
  
  // Configuration
  apiUrl: 'https://d8e17dc1-d8d1-4de1-8b8d-ef7f765bc52f-00-3stkuqyoiccx9.spock.replit.dev',
  userId: 13, // Test user ID
  
  // App state
  isLoading: false,
  error: null,
  
  // Call state
  activeCalls: [],
  callHistory: [],
  
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
      return { ...state, user: action.payload };
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
          contact.phoneNumber !== action.payload.phoneNumber
        )
      };
    case 'SET_TRUSTED_CONTACTS':
      return { ...state, trustedContacts: action.payload };
    case 'UPDATE_SETTINGS':
      return { 
        ...state, 
        settings: { ...state.settings, ...action.payload } 
      };
    default:
      return state;
  }
}

export function CallBunkerProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Initialize CallBunker Native service
  const callBunker = new CallBunkerNative(state.apiUrl, state.userId);

  useEffect(() => {
    // Load saved settings and auth state on app start
    loadSavedData();
  }, []);

  const loadSavedData = async () => {
    try {
      // Load settings
      const savedSettings = await AsyncStorage.getItem('callbunker_settings');
      if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        dispatch({type: 'UPDATE_SETTINGS', payload: settings});
      }

      // Load auth state
      const authState = await AsyncStorage.getItem('callbunker_auth');
      if (authState) {
        const { isAuthenticated, user } = JSON.parse(authState);
        dispatch({type: 'SET_AUTHENTICATED', payload: isAuthenticated});
        dispatch({type: 'SET_USER', payload: user});
      }

      // Load contacts and call history
      await loadContacts();
      await loadCallHistory();

    } catch (error) {
      console.error('Error loading saved data:', error);
    }
  };

  const makeCall = async (phoneNumber) => {
    try {
      dispatch({type: 'SET_LOADING', payload: true});
      dispatch({type: 'SET_ERROR', payload: null});
      
      console.log(`[CallBunkerProvider] Initiating call to ${phoneNumber}`);
      
      // Add to active calls immediately
      const tempCall = {
        id: Date.now(),
        phoneNumber,
        status: 'initiating',
        startTime: new Date(),
      };
      
      dispatch({type: 'ADD_CALL', payload: tempCall});
      
      // Use CallBunker Native service
      const result = await callBunker.makeCall(phoneNumber);
      
      // Update with real call data
      const callInfo = {
        id: result.callLogId,
        phoneNumber: result.targetNumber,
        callerIdShown: result.callerIdShown,
        status: 'connected',
        startTime: new Date(),
        config: result.config
      };
      
      dispatch({type: 'UPDATE_CALL', payload: callInfo});
      
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
      // Find the call in active calls
      const call = state.activeCalls.find(c => c.id === callId);
      if (!call) {
        console.warn(`[CallBunkerProvider] Call ${callId} not found in active calls`);
        return;
      }

      // Complete via CallBunker Native service
      await callBunker.completeCall(callId, duration, status);
      
      // Move to call history
      const completedCall = {
        ...call,
        status,
        duration,
        endTime: new Date(),
      };
      
      dispatch({type: 'COMPLETE_CALL', payload: completedCall});
      
      console.log(`[CallBunkerProvider] Call ${callId} completed`);
      
    } catch (error) {
      console.error('[CallBunkerProvider] Error completing call:', error);
      dispatch({type: 'SET_ERROR', payload: 'Failed to complete call'});
    }
  };

  const loadCallHistory = async () => {
    try {
      const history = await callBunker.getCallHistory();
      dispatch({type: 'SET_CALL_HISTORY', payload: history});
    } catch (error) {
      console.error('Error loading call history:', error);
      // Load mock data for development
      const mockHistory = [
        {
          id: 1,
          phoneNumber: '+15551234567',
          callerIdShown: 'CallBunker Protected',
          direction: 'outbound',
          status: 'completed',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          duration: 245,
        },
        {
          id: 2,
          phoneNumber: '+15559876543',
          callerIdShown: 'CallBunker Protected',
          direction: 'outbound',
          status: 'completed',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          duration: 89,
        },
      ];
      dispatch({type: 'SET_CALL_HISTORY', payload: mockHistory});
    }
  };

  const loadContacts = async () => {
    try {
      // Load contacts from AsyncStorage
      const savedContacts = await AsyncStorage.getItem('callbunker_contacts');
      if (savedContacts) {
        const contacts = JSON.parse(savedContacts);
        dispatch({type: 'SET_TRUSTED_CONTACTS', payload: contacts});
      }
    } catch (error) {
      console.error('Error loading contacts:', error);
    }
  };

  const addTrustedContact = async (contact) => {
    try {
      const newContacts = [...state.trustedContacts, contact];
      
      // Save to AsyncStorage
      await AsyncStorage.setItem('callbunker_contacts', JSON.stringify(newContacts));
      
      dispatch({type: 'ADD_TRUSTED_CONTACT', payload: contact});
      
    } catch (error) {
      console.error('Error adding contact:', error);
      dispatch({type: 'SET_ERROR', payload: 'Failed to add contact'});
    }
  };

  const removeTrustedContact = async (contact) => {
    try {
      const newContacts = state.trustedContacts.filter(c => 
        c.phoneNumber !== contact.phoneNumber
      );
      
      // Save to AsyncStorage
      await AsyncStorage.setItem('callbunker_contacts', JSON.stringify(newContacts));
      
      dispatch({type: 'REMOVE_TRUSTED_CONTACT', payload: contact});
      
    } catch (error) {
      console.error('Error removing contact:', error);
      dispatch({type: 'SET_ERROR', payload: 'Failed to remove contact'});
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

  const clearError = () => {
    dispatch({type: 'SET_ERROR', payload: null});
  };

  const signupUser = async (userData) => {
    try {
      dispatch({type: 'SET_LOADING', payload: true});
      dispatch({type: 'SET_ERROR', payload: null});
      
      // Safely handle phone number formatting with null checks
      const realPhoneNumber = userData.realPhoneNumber ? userData.realPhoneNumber.replace(/\D/g, '') : '';
      
      const response = await fetch(`${state.apiUrl}/multi/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          name: userData.name || '',
          email: userData.email || '',
          real_phone_number: realPhoneNumber,
          pin: userData.pin || '1122',
          verbal_code: userData.verbalCode || 'open sesame',
        }),
      });

      if (response.ok) {
        const responseText = await response.text();
        console.log('Signup response:', responseText);
        
        if (responseText.includes('Account created') || responseText.includes('Defense Number')) {
          // Extract defense number from response if possible
          const defenseNumberMatch = responseText.match(/(\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/);
          const defenseNumber = defenseNumberMatch ? defenseNumberMatch[0] : null;
          
          const user = {
            name: userData.name,
            email: userData.email,
            defenseNumber: defenseNumber
          };
          
          dispatch({type: 'SET_AUTHENTICATED', payload: true});
          dispatch({type: 'SET_USER', payload: user});
          
          // Save auth state
          await AsyncStorage.setItem('callbunker_auth', JSON.stringify({
            isAuthenticated: true,
            user: user
          }));
          
          return true;
        }
      }
      
      throw new Error('Signup failed - please check your information');
      
    } catch (error) {
      console.error('Signup error:', error);
      dispatch({type: 'SET_ERROR', payload: error.message});
      throw error;
    } finally {
      dispatch({type: 'SET_LOADING', payload: false});
    }
  };

  const contextValue = {
    ...state,
    callBunker,
    makeCall,
    completeCall,
    addTrustedContact,
    removeTrustedContact,
    updateSettings,
    loadCallHistory,
    loadContacts,
    clearError,
    signupUser,
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