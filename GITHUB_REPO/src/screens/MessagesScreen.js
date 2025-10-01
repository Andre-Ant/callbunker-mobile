/**
 * CallBunker Anonymous Messages Screen
 * Send SMS from your CallBunker number
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useCallBunker } from '../services/CallBunkerContext';

function MessagesScreen() {
  const { sendMessage, defenseNumber, isLoading, error, clearError } = useCallBunker();
  
  const [toNumber, setToNumber] = useState('');
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (error) {
      Alert.alert('Error', error, [
        { text: 'OK', onPress: clearError }
      ]);
    }
  }, [error]);

  const formatPhoneNumber = (text) => {
    const cleaned = text.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
      return `(${match[1]}) ${match[2]}-${match[3]}`;
    }
    return text;
  };

  const handlePhoneChange = (text) => {
    const formatted = formatPhoneNumber(text);
    setToNumber(formatted);
  };

  const validateInputs = () => {
    if (!toNumber || !toNumber.trim()) {
      Alert.alert('Error', 'Please enter a recipient phone number');
      return false;
    }

    const cleaned = toNumber.replace(/\D/g, '');
    if (cleaned.length < 10) {
      Alert.alert('Error', 'Please enter a valid 10-digit phone number');
      return false;
    }

    if (!message || !message.trim()) {
      Alert.alert('Error', 'Please enter a message');
      return false;
    }

    if (message.length > 1600) {
      Alert.alert('Error', 'Message is too long. Please keep it under 1600 characters.');
      return false;
    }

    return true;
  };

  const handleSendMessage = async () => {
    if (!validateInputs()) return;

    try {
      setSending(true);
      
      // Clean phone number (remove formatting)
      const cleanedNumber = toNumber.replace(/\D/g, '');
      const formattedNumber = cleanedNumber.length === 10 ? `+1${cleanedNumber}` : `+${cleanedNumber}`;
      
      await sendMessage(formattedNumber, message);
      
      Alert.alert(
        'Message Sent!',
        `Your message was sent from your CallBunker number.\n\nRecipient will see: ${defenseNumber || 'Your CallBunker Number'}`,
        [
          {
            text: 'OK',
            onPress: () => {
              // Clear form
              setToNumber('');
              setMessage('');
            }
          }
        ]
      );
      
    } catch (error) {
      Alert.alert(
        'Send Failed',
        error.message || 'Failed to send message. Please try again.'
      );
    } finally {
      setSending(false);
    }
  };

  const remainingChars = 1600 - message.length;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Icon name="message" size={32} color="#007AFF" />
          <Text style={styles.headerTitle}>Anonymous Messaging</Text>
          <Text style={styles.headerSubtitle}>
            Send SMS from your CallBunker number
          </Text>
        </View>

        {/* From Info */}
        <View style={styles.fromCard}>
          <Icon name="shield" size={20} color="#4CAF50" />
          <View style={styles.fromInfo}>
            <Text style={styles.fromLabel}>Sending from:</Text>
            <Text style={styles.fromNumber}>{defenseNumber || 'Your CallBunker Number'}</Text>
          </View>
        </View>

        {/* Message Form */}
        <View style={styles.form}>
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>
              <Icon name="phone" size={16} color="#333" /> To (Phone Number)
            </Text>
            <TextInput
              style={styles.phoneInput}
              value={toNumber}
              onChangeText={handlePhoneChange}
              placeholder="(555) 123-4567"
              placeholderTextColor="#8E8E93"
              keyboardType="phone-pad"
              maxLength={14}
            />
          </View>

          <View style={styles.inputGroup}>
            <View style={styles.messageLabelRow}>
              <Text style={styles.inputLabel}>
                <Icon name="textsms" size={16} color="#333" /> Message
              </Text>
              <Text style={[
                styles.charCount,
                remainingChars < 100 && styles.charCountWarning,
                remainingChars <= 0 && styles.charCountError
              ]}>
                {remainingChars} characters left
              </Text>
            </View>
            <TextInput
              style={styles.messageInput}
              value={message}
              onChangeText={setMessage}
              placeholder="Type your message here..."
              placeholderTextColor="#8E8E93"
              multiline
              numberOfLines={8}
              maxLength={1600}
              textAlignVertical="top"
            />
          </View>

          <TouchableOpacity
            style={[
              styles.sendButton,
              (sending || isLoading) && styles.sendButtonDisabled
            ]}
            onPress={handleSendMessage}
            disabled={sending || isLoading}
          >
            {sending || isLoading ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <>
                <Icon name="send" size={20} color="#FFFFFF" />
                <Text style={styles.sendButtonText}>Send Message</Text>
              </>
            )}
          </TouchableOpacity>
        </View>

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Icon name="info-outline" size={20} color="#007AFF" />
          <View style={styles.infoContent}>
            <Text style={styles.infoTitle}>Privacy Protection</Text>
            <Text style={styles.infoText}>
              • Recipient sees your CallBunker number{'\n'}
              • Your real number stays hidden{'\n'}
              • SMS sent through secure Twilio gateway{'\n'}
              • Standard carrier rates may apply
            </Text>
          </View>
        </View>

        {/* Tips Card */}
        <View style={styles.tipsCard}>
          <Icon name="lightbulb-outline" size={20} color="#FFA000" />
          <View style={styles.tipsContent}>
            <Text style={styles.tipsTitle}>Tips</Text>
            <Text style={styles.tipsText}>
              • Maximum message length: 1600 characters{'\n'}
              • Messages longer than 160 chars sent as multiple SMS{'\n'}
              • Recipients can reply to your CallBunker number
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
    backgroundColor: '#F8F9FA',
  },
  content: {
    padding: 16,
  },
  header: {
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#1C1C1E',
    marginTop: 12,
    marginBottom: 6,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#8E8E93',
    textAlign: 'center',
  },
  fromCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F5E8',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  fromInfo: {
    marginLeft: 12,
    flex: 1,
  },
  fromLabel: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '500',
    marginBottom: 4,
  },
  fromNumber: {
    fontSize: 16,
    color: '#2E7D32',
    fontWeight: '600',
  },
  form: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
    marginBottom: 8,
  },
  messageLabelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  charCount: {
    fontSize: 12,
    color: '#8E8E93',
  },
  charCountWarning: {
    color: '#FFA000',
    fontWeight: '500',
  },
  charCountError: {
    color: '#FF3B30',
    fontWeight: '600',
  },
  phoneInput: {
    backgroundColor: '#F2F2F7',
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#1C1C1E',
  },
  messageInput: {
    backgroundColor: '#F2F2F7',
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#1C1C1E',
    minHeight: 120,
  },
  sendButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  sendButtonDisabled: {
    backgroundColor: '#C7C7CC',
  },
  sendButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#E3F2FD',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  infoContent: {
    marginLeft: 12,
    flex: 1,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0D47A1',
    marginBottom: 6,
  },
  infoText: {
    fontSize: 14,
    color: '#1565C0',
    lineHeight: 20,
  },
  tipsCard: {
    flexDirection: 'row',
    backgroundColor: '#FFF8E1',
    padding: 16,
    borderRadius: 12,
  },
  tipsContent: {
    marginLeft: 12,
    flex: 1,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#F57C00',
    marginBottom: 6,
  },
  tipsText: {
    fontSize: 14,
    color: '#E65100',
    lineHeight: 20,
  },
});

export default MessagesScreen;
