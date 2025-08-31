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
        Alert.alert(
          'Success!', 
          'Your CallBunker account has been created. You will receive your unique Defense Number shortly.',
          [
            {
              text: 'Continue',
              onPress: () => navigation.replace('Main')
            }
          ]
        );
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
            <TextInput
              style={styles.input}
              value={formData.googleVoiceNumber}
              onChangeText={(text) => handlePhoneChange('googleVoiceNumber', text)}
              placeholder="(555) 123-4567"
              keyboardType="phone-pad"
            />
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
});