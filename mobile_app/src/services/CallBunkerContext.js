/**
 * CallBunker Context Provider
 * Manages global state and configuration
 */

import React, {createContext, useContext, useReducer, useEffect} from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import CallBunkerNative from './CallBunkerNative';

const CallBunkerContext = createContext();

const initialState = {
  user: null,
  apiUrl: 'https://your-callbunker-api.com', // Replace with your API URL
  userId: 1, // Replace with dynamic user ID
  callHistory: [],
  contacts: [],
  settings: {
    autoWhitelist: true,
    callRecording: false,
    notifications: true,
    darkMode: false,
  },
  isLoading: false,
  error: null,
};

function callBunkerReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return {...state, isLoading: action.payload};
    
    case 'SET_ERROR':
      return {...state, error: action.payload, isLoading: false};
    
    case 'SET_USER':
      return {...state, user: action.payload};
    
    case 'SET_CALL_HISTORY':
      return {...state, callHistory: action.payload};
    
    case 'ADD_CALL_TO_HISTORY':
      return {
        ...state,
        callHistory: [action.payload, ...state.callHistory],
      };
    
    case 'UPDATE_CALL_IN_HISTORY':
      return {
        ...state,
        callHistory: state.callHistory.map(call =>
          call.id === action.payload.id ? {...call, ...action.payload} : call
        ),
      };
    
    case 'SET_CONTACTS':
      return {...state, contacts: action.payload};
    
    case 'ADD_CONTACT':
      return {
        ...state,
        contacts: [action.payload, ...state.contacts],
      };
    
    case 'REMOVE_CONTACT':
      return {
        ...state,
        contacts: state.contacts.filter(contact => contact.id !== action.payload),
      };
    
    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: {...state.settings, ...action.payload},
      };
    
    default:
      return state;
  }
}

export function CallBunkerProvider({children}) {
  const [state, dispatch] = useReducer(callBunkerReducer, initialState);
  
  // Initialize CallBunker service
  const callBunker = new CallBunkerNative(state.apiUrl, state.userId);

  useEffect(() => {
    loadStoredData();
  }, []);

  const loadStoredData = async () => {
    try {
      dispatch({type: 'SET_LOADING', payload: true});
      
      // Load stored settings
      const storedSettings = await AsyncStorage.getItem('callbunker_settings');
      if (storedSettings) {
        dispatch({type: 'UPDATE_SETTINGS', payload: JSON.parse(storedSettings)});
      }
      
      // Load call history
      await loadCallHistory();
      
      // Load contacts
      await loadContacts();
      
    } catch (error) {
      console.error('Error loading stored data:', error);
      dispatch({type: 'SET_ERROR', payload: 'Failed to load app data'});
    } finally {
      dispatch({type: 'SET_LOADING', payload: false});
    }
  };

  const loadCallHistory = async () => {
    try {
      const history = await callBunker.getCallHistory(50, 0);
      dispatch({type: 'SET_CALL_HISTORY', payload: history});
    } catch (error) {
      console.error('Error loading call history:', error);
    }
  };

  const loadContacts = async () => {
    try {
      // Load trusted contacts from API
      const response = await fetch(`${state.apiUrl}/api/users/${state.userId}/contacts`);
      if (response.ok) {
        const contacts = await response.json();
        dispatch({type: 'SET_CONTACTS', payload: contacts});
      }
    } catch (error) {
      console.error('Error loading contacts:', error);
    }
  };

  const makeCall = async (phoneNumber) => {
    try {
      dispatch({type: 'SET_LOADING', payload: true});
      dispatch({type: 'SET_ERROR', payload: null});
      
      // Check if native calling is supported
      const isSupported = await callBunker.isNativeCallingSupported();
      if (!isSupported) {
        throw new Error('Native calling not supported on this device');
      }

      // Make the call
      const callInfo = await callBunker.makeCall(phoneNumber);
      
      // Add to call history
      const callRecord = {
        id: callInfo.callLogId,
        phoneNumber: callInfo.targetNumber,
        callerIdShown: callInfo.callerIdShown,
        direction: 'outbound',
        status: 'initiated',
        timestamp: new Date().toISOString(),
        duration: 0,
      };
      
      dispatch({type: 'ADD_CALL_TO_HISTORY', payload: callRecord});
      
      return callInfo;
      
    } catch (error) {
      console.error('Failed to make call:', error);
      dispatch({type: 'SET_ERROR', payload: error.message});
      throw error;
    } finally {
      dispatch({type: 'SET_LOADING', payload: false});
    }
  };

  const completeCall = async (callLogId, duration, status = 'completed') => {
    try {
      await callBunker.completeCall(callLogId, duration, status);
      
      // Update call in history
      dispatch({
        type: 'UPDATE_CALL_IN_HISTORY',
        payload: {
          id: callLogId,
          status,
          duration,
          endTime: new Date().toISOString(),
        },
      });
      
    } catch (error) {
      console.error('Failed to complete call:', error);
    }
  };

  const addTrustedContact = async (contact) => {
    try {
      dispatch({type: 'SET_LOADING', payload: true});
      
      const response = await fetch(`${state.apiUrl}/api/users/${state.userId}/contacts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(contact),
      });
      
      if (response.ok) {
        const newContact = await response.json();
        dispatch({type: 'ADD_CONTACT', payload: newContact});
        return newContact;
      } else {
        throw new Error('Failed to add contact');
      }
      
    } catch (error) {
      console.error('Error adding contact:', error);
      dispatch({type: 'SET_ERROR', payload: 'Failed to add contact'});
      throw error;
    } finally {
      dispatch({type: 'SET_LOADING', payload: false});
    }
  };

  const removeTrustedContact = async (contactId) => {
    try {
      const response = await fetch(`${state.apiUrl}/api/users/${state.userId}/contacts/${contactId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        dispatch({type: 'REMOVE_CONTACT', payload: contactId});
      } else {
        throw new Error('Failed to remove contact');
      }
      
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