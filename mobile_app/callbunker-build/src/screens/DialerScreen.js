/**
 * CallBunker Protected Dialer Screen
 * Native calling with caller ID spoofing
 */

import React, {useState, useRef, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Vibration,
  Alert,
  ActivityIndicator,
  StatusBar,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useCallBunker} from '../services/CallBunkerContext';

function DialerScreen() {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isDialing, setIsDialing] = useState(false);
  const {makeCall, isLoading, error, clearError} = useCallBunker();

  useEffect(() => {
    if (error) {
      Alert.alert('Call Failed', error, [
        {text: 'OK', onPress: clearError},
      ]);
    }
  }, [error]);

  const handleNumberPress = (digit) => {
    if (phoneNumber.length < 15) {
      setPhoneNumber(prev => prev + digit);
      Vibration.vibrate(50);
    }
  };

  const handleBackspace = () => {
    setPhoneNumber(prev => prev.slice(0, -1));
    Vibration.vibrate(50);
  };

  const handleCall = async () => {
    if (!phoneNumber || phoneNumber.length < 3) {
      Alert.alert('Invalid Number', 'Please enter a valid phone number');
      return;
    }

    try {
      setIsDialing(true);
      
      // Show confirmation with privacy info
      Alert.alert(
        'Protected Call',
        `Call ${phoneNumber}?\n\nYour Google Voice number will be shown as caller ID. Your real number stays hidden.`,
        [
          {
            text: 'Cancel',
            style: 'cancel',
            onPress: () => setIsDialing(false),
          },
          {
            text: 'Call',
            onPress: async () => {
              try {
                const callInfo = await makeCall(phoneNumber);
                
                // Show success feedback
                Alert.alert(
                  'Call Initiated',
                  `Calling ${callInfo.targetNumber}\nCaller ID shown: ${callInfo.callerIdShown}`,
                  [
                    {
                      text: 'OK',
                      onPress: () => {
                        setPhoneNumber('');
                        setIsDialing(false);
                      },
                    },
                  ]
                );
              } catch (error) {
                setIsDialing(false);
                console.error('Call failed:', error);
              }
            },
          },
        ]
      );
    } catch (error) {
      setIsDialing(false);
      console.error('Call preparation failed:', error);
    }
  };

  const formatPhoneNumber = (number) => {
    // Simple US phone number formatting
    const cleaned = number.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{0,3})(\d{0,3})(\d{0,4})$/);
    if (match) {
      return [match[1], match[2], match[3]].filter(Boolean).join('-');
    }
    return number;
  };

  const dialpadButtons = [
    [{number: '1', letters: ''}, {number: '2', letters: 'ABC'}, {number: '3', letters: 'DEF'}],
    [{number: '4', letters: 'GHI'}, {number: '5', letters: 'JKL'}, {number: '6', letters: 'MNO'}],
    [{number: '7', letters: 'PQRS'}, {number: '8', letters: 'TUV'}, {number: '9', letters: 'WXYZ'}],
    [{number: '*', letters: ''}, {number: '0', letters: '+'}, {number: '#', letters: ''}],
  ];

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F8F9FA" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Protected Dialer</Text>
        <Text style={styles.headerSubtitle}>Your number stays hidden</Text>
      </View>

      {/* Phone Number Display */}
      <View style={styles.numberDisplay}>
        <Text style={styles.phoneNumber}>
          {phoneNumber ? formatPhoneNumber(phoneNumber) : 'Enter number'}
        </Text>
        <View style={styles.privacyIndicator}>
          <Icon name="security" size={16} color="#4CAF50" />
          <Text style={styles.privacyText}>Privacy Protected</Text>
        </View>
      </View>

      {/* Dialpad */}
      <View style={styles.dialpad}>
        {dialpadButtons.map((row, rowIndex) => (
          <View key={rowIndex} style={styles.dialpadRow}>
            {row.map((button, buttonIndex) => (
              <TouchableOpacity
                key={buttonIndex}
                style={styles.dialpadButton}
                onPress={() => handleNumberPress(button.number)}
                activeOpacity={0.7}
              >
                <Text style={styles.dialpadNumber}>{button.number}</Text>
                {button.letters ? (
                  <Text style={styles.dialpadLetters}>{button.letters}</Text>
                ) : null}
              </TouchableOpacity>
            ))}
          </View>
        ))}
      </View>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity
          style={[styles.actionButton, styles.backspaceButton]}
          onPress={handleBackspace}
          disabled={!phoneNumber}
        >
          <Icon 
            name="backspace" 
            size={24} 
            color={phoneNumber ? '#FF3B30' : '#C7C7CC'} 
          />
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.callButton,
            (!phoneNumber || isLoading || isDialing) && styles.callButtonDisabled
          ]}
          onPress={handleCall}
          disabled={!phoneNumber || isLoading || isDialing}
        >
          {isLoading || isDialing ? (
            <ActivityIndicator size="small" color="#FFFFFF" />
          ) : (
            <Icon name="phone" size={28} color="#FFFFFF" />
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, styles.contactsButton]}
          onPress={() => {/* Navigate to contacts */}}
        >
          <Icon name="contacts" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>

      {/* Features Info */}
      <View style={styles.featuresInfo}>
        <View style={styles.featureItem}>
          <Icon name="visibility-off" size={18} color="#007AFF" />
          <Text style={styles.featureText}>Real number hidden</Text>
        </View>
        <View style={styles.featureItem}>
          <Icon name="savings" size={18} color="#4CAF50" />
          <Text style={styles.featureText}>Carrier rates only</Text>
        </View>
        <View style={styles.featureItem}>
          <Icon name="security" size={18} color="#FF9500" />
          <Text style={styles.featureText}>Google Voice caller ID</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    alignItems: 'center',
    paddingTop: 20,
    paddingBottom: 30,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#8E8E93',
  },
  numberDisplay: {
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 30,
    minHeight: 80,
    justifyContent: 'center',
  },
  phoneNumber: {
    fontSize: 32,
    fontWeight: '300',
    color: '#1C1C1E',
    marginBottom: 8,
    minHeight: 40,
    textAlign: 'center',
  },
  privacyIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F5E8',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  privacyText: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '500',
    marginLeft: 4,
  },
  dialpad: {
    flex: 1,
    paddingHorizontal: 40,
    justifyContent: 'center',
  },
  dialpadRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  dialpadButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  dialpadNumber: {
    fontSize: 28,
    fontWeight: '300',
    color: '#1C1C1E',
  },
  dialpadLetters: {
    fontSize: 10,
    color: '#8E8E93',
    fontWeight: '500',
    letterSpacing: 1,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 40,
    paddingBottom: 30,
  },
  actionButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  backspaceButton: {
    backgroundColor: '#F2F2F7',
  },
  contactsButton: {
    backgroundColor: '#E3F2FD',
  },
  callButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#4CAF50',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#4CAF50',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  callButtonDisabled: {
    backgroundColor: '#C7C7CC',
    shadowColor: '#000',
    shadowOpacity: 0.1,
  },
  featuresInfo: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  featureItem: {
    alignItems: 'center',
    flex: 1,
  },
  featureText: {
    fontSize: 11,
    color: '#8E8E93',
    marginTop: 4,
    textAlign: 'center',
  },
});

export default DialerScreen;