/**
 * CallBunker Multi-User Signup Screen
 * Allows new users to register for their own CallBunker number
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
} from 'react-native';
import { useCallBunker } from '../services/CallBunkerContext';

export default function SignupScreen({ navigation }) {
  const { signupUser, isLoading } = useCallBunker();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    realPhoneNumber: '',
    pin: '',
    verbalCode: '',
  });
  
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [assignedDefenseNumber, setAssignedDefenseNumber] = useState('');

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const formatPhoneNumber = (text) => {
    if (!text) return text;
    
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
    const { name, email, realPhoneNumber, pin, verbalCode } = formData;
    
    if (!name || !name.trim()) {
      Alert.alert('Required Field', 'Please enter your full name');
      return false;
    }
    
    if (!email || !email.trim() || !email.includes('@')) {
      Alert.alert('Required Field', 'Please enter a valid email address');
      return false;
    }
    
    if (!realPhoneNumber || !realPhoneNumber.trim()) {
      Alert.alert('Required Field', 'Please enter your real phone number');
      return false;
    }

    const cleanedPhone = realPhoneNumber.replace(/\D/g, '');
    if (cleanedPhone.length < 10) {
      Alert.alert('Invalid Phone', 'Please enter a valid 10-digit phone number');
      return false;
    }
    
    if (!pin || !pin.trim()) {
      Alert.alert('Required Field', 'Please create a 4-digit security PIN');
      return false;
    }

    if (!/^\d{4}$/.test(pin)) {
      Alert.alert('Invalid PIN', 'PIN must be exactly 4 digits (numbers only)');
      return false;
    }

    if (!verbalCode || !verbalCode.trim()) {
      Alert.alert('Required Field', 'Please create a verbal security code');
      return false;
    }

    if (verbalCode.trim().length < 3) {
      Alert.alert('Invalid Verbal Code', 'Verbal code must be at least 3 characters long');
      return false;
    }
    
    return true;
  };

  const handleSignup = async () => {
    if (!validateForm()) return;
    
    try {
      const result = await signupUser(formData);
      
      if (result && result.success) {
        const defenseNumber = result.defenseNumber || 'Your assigned CallBunker number';
        setAssignedDefenseNumber(defenseNumber);
        setShowSuccessModal(true);
      }
      
    } catch (error) {
      console.error('Signup error:', error);
      Alert.alert('Signup Failed', error.message || 'Please try again');
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
            <Text style={styles.label}>Full Name *</Text>
            <TextInput
              style={styles.input}
              value={formData.name}
              onChangeText={(text) => handleInputChange('name', text)}
              placeholder="Enter your full name"
              placeholderTextColor="#8E8E93"
              autoCapitalize="words"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Email Address *</Text>
            <TextInput
              style={styles.input}
              value={formData.email}
              onChangeText={(text) => handleInputChange('email', text)}
              placeholder="your.email@example.com"
              placeholderTextColor="#8E8E93"
              keyboardType="email-address"
              autoCapitalize="none"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Real Phone Number *</Text>
            <TextInput
              style={styles.input}
              value={formData.realPhoneNumber}
              onChangeText={(text) => handlePhoneChange('realPhoneNumber', text)}
              placeholder="(555) 987-6543"
              placeholderTextColor="#8E8E93"
              keyboardType="phone-pad"
            />
            <Text style={styles.helpText}>
              This will be kept private - only you can see it
            </Text>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Security PIN (4 digits) *</Text>
            <TextInput
              style={styles.input}
              value={formData.pin}
              onChangeText={(text) => handleInputChange('pin', text.replace(/\D/g, ''))}
              placeholder="Create a 4-digit PIN"
              placeholderTextColor="#8E8E93"
              keyboardType="numeric"
              maxLength={4}
              secureTextEntry
            />
            <Text style={styles.helpText}>
              Used for call screening - callers must enter this to reach you
            </Text>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Verbal Code *</Text>
            <TextInput
              style={styles.input}
              value={formData.verbalCode}
              onChangeText={(text) => handleInputChange('verbalCode', text)}
              placeholder="Create a verbal code (e.g., 'blue sky')"
              placeholderTextColor="#8E8E93"
              autoCapitalize="none"
            />
            <Text style={styles.helpText}>
              Alternative authentication method - callers can say this phrase
            </Text>
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
              🛡️ Get your own unique CallBunker Defense Number
            </Text>
            <Text style={styles.infoText}>
              📱 Make calls with complete privacy protection
            </Text>
            <Text style={styles.infoText}>
              🔒 Your real number stays completely hidden
            </Text>
          </View>
        </View>
      </View>

      {/* Success Modal */}
      <Modal
        visible={showSuccessModal}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowSuccessModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.successModal}>
            <Text style={styles.successIcon}>🎉</Text>
            <Text style={styles.successTitle}>Account Created!</Text>
            <Text style={styles.successMessage}>
              Your CallBunker Defense Number:{'\n'}
              <Text style={styles.defenseNumber}>{assignedDefenseNumber}</Text>
              {'\n\n'}
              You can now make calls with complete privacy protection.
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
    backgroundColor: '#F8F9FA',
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
    color: '#1C1C1E',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#F2F2F7',
    color: '#1C1C1E',
  },
  helpText: {
    fontSize: 12,
    color: '#8E8E93',
    marginTop: 4,
    fontStyle: 'italic',
  },
  signupButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginTop: 20,
  },
  buttonDisabled: {
    backgroundColor: '#C7C7CC',
  },
  signupButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  infoBox: {
    backgroundColor: '#E3F2FD',
    borderRadius: 8,
    padding: 15,
    marginTop: 20,
  },
  infoText: {
    fontSize: 14,
    color: '#1976D2',
    marginBottom: 5,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  successModal: {
    backgroundColor: 'white',
    padding: 30,
    borderRadius: 12,
    width: '100%',
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
    fontSize: 24,
    fontWeight: 'bold',
    color: '#28A745',
    marginBottom: 16,
    textAlign: 'center',
  },
  successMessage: {
    fontSize: 16,
    color: '#666',
    marginBottom: 24,
    lineHeight: 24,
    textAlign: 'center',
  },
  defenseNumber: {
    fontSize: 20,
    color: '#007AFF',
    fontWeight: 'bold',
  },
  successButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 8,
  },
  successButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
