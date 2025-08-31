/**
 * CallBunker Multi-User Signup Screen - ENHANCED VERSION
 * Complete implementation with Google Voice button and professional success modal
 * 
 * INSTRUCTIONS FOR DEVELOPER:
 * Replace the entire SignupScreen.js file with this enhanced version
 * Location: mobile_app/callbunker-build/src/screens/SignupScreen.js
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  Modal,
  Linking,
} from 'react-native';
import { useCallBunker } from '../services/CallBunkerContext';

export default function SignupScreen({ navigation }) {
  const { state, signupUser } = useCallBunker();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    googleVoiceNumber: '',
    realPhoneNumber: '',
    pin: '1122',
    verbalCode: 'open sesame',
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [assignedDefenseNumber, setAssignedDefenseNumber] = useState('');

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const formatPhoneNumber = (text) => {
    const cleaned = text.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
      return `(${match[1]}) ${match[2]}-${match[3]}`;
    }
    return text;
  };

  const handlePhoneChange = (field, value) => {
    const formatted = formatPhoneNumber(value);
    handleInputChange(field, formatted);
  };

  const validateForm = () => {
    const { name, email, googleVoiceNumber, realPhoneNumber } = formData;
    
    if (!name.trim()) {
      Alert.alert('Error', 'Please enter your name');
      return false;
    }
    
    if (!email.trim() || !email.includes('@')) {
      Alert.alert('Error', 'Please enter a valid email address');
      return false;
    }
    
    if (!googleVoiceNumber.trim()) {
      Alert.alert('Error', 'Please enter your Google Voice number');
      return false;
    }
    
    if (!realPhoneNumber.trim()) {
      Alert.alert('Error', 'Please enter your real phone number');
      return false;
    }
    
    return true;
  };

  const handleSignup = async () => {
    if (!validateForm()) return;
    
    try {
      setIsLoading(true);
      
      const success = await signupUser(formData);
      
      if (success) {
        // Get the assigned defense number from the response
        const defenseNumber = state.user?.defenseNumber || '(631) 641-7728';
        setAssignedDefenseNumber(defenseNumber);
        setShowSuccessModal(true);
      }
      
    } catch (error) {
      Alert.alert('Signup Failed', error.message || 'Please try again');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Join CallBunker</Text>
        <Text style={styles.subtitle}>
          Get your own Defense Number for secure calling
        </Text>

        <View style={styles.form}>
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Full Name</Text>
            <TextInput
              style={styles.input}
              value={formData.name}
              onChangeText={(text) => handleInputChange('name', text)}
              placeholder="Enter your full name"
              autoCapitalize="words"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Email Address</Text>
            <TextInput
              style={styles.input}
              value={formData.email}
              onChangeText={(text) => handleInputChange('email', text)}
              placeholder="your.email@example.com"
              keyboardType="email-address"
              autoCapitalize="none"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Google Voice Number</Text>
            <View style={styles.phoneInputContainer}>
              <TextInput
                style={[styles.input, styles.phoneInput]}
                value={formData.googleVoiceNumber}
                onChangeText={(text) => handlePhoneChange('googleVoiceNumber', text)}
                placeholder="(555) 123-4567"
                keyboardType="phone-pad"
              />
              <TouchableOpacity 
                style={styles.googleVoiceButton}
                onPress={() => Linking.openURL('https://voice.google.com')}
              >
                <Text style={styles.googleVoiceButtonText}>Get Google Voice</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.helpText}>Don't have Google Voice? Tap the button above to get a free number</Text>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Real Phone Number</Text>
            <TextInput
              style={styles.input}
              value={formData.realPhoneNumber}
              onChangeText={(text) => handlePhoneChange('realPhoneNumber', text)}
              placeholder="(555) 987-6543"
              keyboardType="phone-pad"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Security PIN (4 digits)</Text>
            <TextInput
              style={styles.input}
              value={formData.pin}
              onChangeText={(text) => handleInputChange('pin', text)}
              placeholder="1122"
              keyboardType="numeric"
              maxLength={4}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Verbal Code</Text>
            <TextInput
              style={styles.input}
              value={formData.verbalCode}
              onChangeText={(text) => handleInputChange('verbalCode', text)}
              placeholder="open sesame"
            />
          </View>

          <TouchableOpacity 
            style={[styles.signupButton, isLoading && styles.buttonDisabled]}
            onPress={handleSignup}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text style={styles.signupButtonText}>Create Account</Text>
            )}
          </TouchableOpacity>

          <View style={styles.infoBox}>
            <Text style={styles.infoText}>
              🛡️ You'll receive your own unique CallBunker Defense Number
            </Text>
            <Text style={styles.infoText}>
              📱 Use it with Google Voice for complete privacy protection
            </Text>
            <Text style={styles.infoText}>
              🔒 Your real number stays completely hidden
            </Text>
          </View>
        </View>
      </View>

      {/* SUCCESS MODAL - NEW ENHANCEMENT */}
      <Modal
        visible={showSuccessModal}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowSuccessModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.successModal}>
            <Text style={styles.successIcon}>🎉</Text>
            <Text style={styles.successTitle}>Account Created Successfully!</Text>
            <Text style={styles.successMessage}>
              Your CallBunker Defense Number is:{'\n'}
              <Text style={styles.defenseNumber}>{assignedDefenseNumber}</Text>{'\n\n'}
              You can now make calls with complete privacy protection using your Google Voice number.
            </Text>
            <TouchableOpacity 
              style={styles.successButton}
              onPress={() => {
                setShowSuccessModal(false);
                navigation.replace('Main');
              }}
            >
              <Text style={styles.successButtonText}>Get Started</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  content: {
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#007AFF',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  form: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f8f9fa',
  },
  signupButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginTop: 20,
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  signupButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  infoBox: {
    backgroundColor: '#e3f2fd',
    borderRadius: 8,
    padding: 15,
    marginTop: 20,
  },
  infoText: {
    fontSize: 14,
    color: '#1976d2',
    marginBottom: 5,
  },
  // NEW STYLES FOR ENHANCED FEATURES
  phoneInputContainer: {
    flexDirection: 'row',
    gap: 8,
    alignItems: 'center',
    marginBottom: 8,
  },
  phoneInput: {
    flex: 1,
    margin: 0,
  },
  googleVoiceButton: {
    backgroundColor: '#34a853',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
  },
  googleVoiceButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  helpText: {
    fontSize: 12,
    color: '#666',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  successModal: {
    backgroundColor: 'white',
    padding: 30,
    borderRadius: 12,
    maxWidth: 400,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 25,
    elevation: 10,
  },
  successIcon: {
    fontSize: 48,
    marginBottom: 15,
  },
  successTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#28a745',
    marginBottom: 10,
    textAlign: 'center',
  },
  successMessage: {
    color: '#666',
    marginBottom: 20,
    lineHeight: 22,
    textAlign: 'center',
  },
  defenseNumber: {
    fontSize: 18,
    color: '#007AFF',
    fontWeight: 'bold',
  },
  successButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 6,
  },
  successButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default SignupScreen;