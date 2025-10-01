/**
 * CallBunker Trusted Contacts Screen
 * Manage whitelist for call screening bypass
 */

import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  TextInput,
  Modal,
  RefreshControl,
  ScrollView,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useCallBunker} from '../services/CallBunkerContext';

function ContactsScreen({ navigation }) {
  const {
    trustedContacts,
    isLoading,
    error,
    addTrustedContact,
    removeTrustedContact,
    loadContacts,
    clearError,
  } = useCallBunker();

  const [showAddModal, setShowAddModal] = useState(false);
  const [newContactName, setNewContactName] = useState('');
  const [newContactPhone, setNewContactPhone] = useState('');
  const [newContactPin, setNewContactPin] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadContacts();
  }, []);

  useEffect(() => {
    if (error) {
      Alert.alert('Error', error, [
        {text: 'OK', onPress: clearError},
      ]);
    }
  }, [error]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await loadContacts();
    } finally {
      setRefreshing(false);
    }
  };

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
    setNewContactPhone(formatted);
  };

  const handleAddContact = async () => {
    if (!newContactName.trim() || !newContactPhone.trim()) {
      Alert.alert('Missing Information', 'Please enter both name and phone number');
      return;
    }

    // Validate phone number
    const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
    if (!phoneRegex.test(newContactPhone)) {
      Alert.alert('Invalid Phone Number', 'Please enter a valid phone number');
      return;
    }

    // Validate PIN if provided
    if (newContactPin && !/^\d{4}$/.test(newContactPin)) {
      Alert.alert('Invalid PIN', 'PIN must be exactly 4 digits');
      return;
    }

    try {
      const cleanedPhone = newContactPhone.replace(/\D/g, '');
      const formattedPhone = cleanedPhone.length === 10 ? `+1${cleanedPhone}` : `+${cleanedPhone}`;

      await addTrustedContact({
        name: newContactName.trim(),
        phone_number: formattedPhone,
        custom_pin: newContactPin || null,
      });
      
      setNewContactName('');
      setNewContactPhone('');
      setNewContactPin('');
      setShowAddModal(false);
      
      Alert.alert('Success', `${newContactName} added to trusted contacts`);
    } catch (error) {
      console.error('Failed to add contact:', error);
      Alert.alert('Error', error.message || 'Failed to add contact');
    }
  };

  const handleRemoveContact = (contact) => {
    Alert.alert(
      'Remove Contact',
      `Remove ${contact.name} from trusted contacts?\n\nThis contact will need to authenticate on future calls.`,
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Remove',
          style: 'destructive',
          onPress: async () => {
            try {
              await removeTrustedContact(contact.id);
              Alert.alert('Removed', `${contact.name} removed from trusted contacts`);
            } catch (error) {
              Alert.alert('Error', 'Failed to remove contact');
            }
          },
        },
      ]
    );
  };

  const handleCallContact = (contact) => {
    Alert.alert(
      'Protected Call',
      `Call ${contact.name}?\n\nThis will be a privacy-protected call using your CallBunker number.`,
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Call Now',
          onPress: () => {
            // Navigate to Dialer with phone number pre-filled
            navigation.navigate('Dialer', { 
              prefillNumber: contact.phone_number 
            });
          },
        },
      ]
    );
  };

  const formatPhoneDisplay = (phoneNumber) => {
    if (!phoneNumber) return '';
    const cleaned = phoneNumber.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{1})(\d{3})(\d{3})(\d{4})$/);
    if (match) {
      return `+${match[1]} (${match[2]}) ${match[3]}-${match[4]}`;
    }
    return phoneNumber;
  };

  const renderContact = ({item: contact}) => (
    <View style={styles.contactItem}>
      <View style={styles.contactAvatar}>
        <Text style={styles.contactInitial}>
          {contact.name.charAt(0).toUpperCase()}
        </Text>
      </View>
      
      <View style={styles.contactInfo}>
        <Text style={styles.contactName}>{contact.name}</Text>
        <Text style={styles.contactPhone}>{formatPhoneDisplay(contact.phone_number)}</Text>
        <View style={styles.contactStatus}>
          <Icon 
            name={contact.auto_whitelisted ? 'auto-awesome' : 'verified-user'} 
            size={14} 
            color={contact.auto_whitelisted ? '#4CAF50' : '#007AFF'} 
          />
          <Text style={styles.contactStatusText}>
            {contact.auto_whitelisted ? 'Auto-added after auth' : 'Manually added'}
          </Text>
        </View>
      </View>
      
      <View style={styles.contactActions}>
        <TouchableOpacity
          style={styles.contactActionButton}
          onPress={() => handleCallContact(contact)}
        >
          <Icon name="phone" size={20} color="#007AFF" />
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.contactActionButton, styles.removeButton]}
          onPress={() => handleRemoveContact(contact)}
        >
          <Icon name="delete" size={20} color="#FF3B30" />
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderAddContactModal = () => (
    <Modal
      visible={showAddModal}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setShowAddModal(false)}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity onPress={() => {
            setShowAddModal(false);
            setNewContactName('');
            setNewContactPhone('');
            setNewContactPin('');
          }}>
            <Text style={styles.modalCancelButton}>Cancel</Text>
          </TouchableOpacity>
          <Text style={styles.modalTitle}>Add Trusted Contact</Text>
          <TouchableOpacity onPress={handleAddContact}>
            <Text style={styles.modalSaveButton}>Save</Text>
          </TouchableOpacity>
        </View>
        
        <ScrollView style={styles.modalContent}>
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>Name *</Text>
            <TextInput
              style={styles.textInput}
              value={newContactName}
              onChangeText={setNewContactName}
              placeholder="Enter contact name"
              placeholderTextColor="#8E8E93"
              autoFocus
            />
          </View>
          
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>Phone Number *</Text>
            <TextInput
              style={styles.textInput}
              value={newContactPhone}
              onChangeText={handlePhoneChange}
              placeholder="(555) 123-4567"
              placeholderTextColor="#8E8E93"
              keyboardType="phone-pad"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>Custom PIN (Optional)</Text>
            <TextInput
              style={styles.textInput}
              value={newContactPin}
              onChangeText={(text) => setNewContactPin(text.replace(/\D/g, ''))}
              placeholder="4-digit PIN (optional)"
              placeholderTextColor="#8E8E93"
              keyboardType="numeric"
              maxLength={4}
              secureTextEntry
            />
            <Text style={styles.helpText}>
              Leave empty to use your default PIN
            </Text>
          </View>
          
          <View style={styles.helpBox}>
            <Icon name="info" size={20} color="#007AFF" />
            <Text style={styles.helpTextContent}>
              Trusted contacts can bypass call screening and reach you directly without authentication
            </Text>
          </View>
        </ScrollView>
      </View>
    </Modal>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Trusted Contacts</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => setShowAddModal(true)}
        >
          <Icon name="add" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>

      {/* Info Card */}
      <View style={styles.infoCard}>
        <Icon name="security" size={20} color="#4CAF50" />
        <Text style={styles.infoText}>
          Trusted contacts can bypass call screening and reach you directly
        </Text>
      </View>

      {/* Contacts List */}
      {trustedContacts && trustedContacts.length > 0 ? (
        <FlatList
          data={trustedContacts}
          renderItem={renderContact}
          keyExtractor={item => item.id?.toString() || item.phone_number}
          style={styles.contactsList}
          contentContainerStyle={styles.contactsListContent}
          refreshControl={
            <RefreshControl 
              refreshing={refreshing} 
              onRefresh={handleRefresh}
              colors={['#007AFF']}
              tintColor="#007AFF"
            />
          }
        />
      ) : (
        <View style={styles.emptyState}>
          <Icon name="contacts" size={64} color="#C7C7CC" />
          <Text style={styles.emptyStateTitle}>No Trusted Contacts</Text>
          <Text style={styles.emptyStateSubtitle}>
            Add contacts who can bypass call screening and reach you directly
          </Text>
          <TouchableOpacity
            style={styles.emptyStateButton}
            onPress={() => setShowAddModal(true)}
          >
            <Text style={styles.emptyStateButtonText}>Add First Contact</Text>
          </TouchableOpacity>
        </View>
      )}

      {renderAddContactModal()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1C1C1E',
  },
  addButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#E3F2FD',
    justifyContent: 'center',
    alignItems: 'center',
  },
  infoCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F5E8',
    margin: 16,
    padding: 16,
    borderRadius: 12,
  },
  infoText: {
    fontSize: 14,
    color: '#4CAF50',
    marginLeft: 8,
    flex: 1,
    lineHeight: 20,
  },
  contactsList: {
    flex: 1,
  },
  contactsListContent: {
    paddingHorizontal: 16,
  },
  contactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 16,
    marginBottom: 8,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 1},
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  contactAvatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  contactInitial: {
    fontSize: 20,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  contactInfo: {
    flex: 1,
  },
  contactName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
    marginBottom: 4,
  },
  contactPhone: {
    fontSize: 14,
    color: '#8E8E93',
    marginBottom: 6,
  },
  contactStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  contactStatusText: {
    fontSize: 12,
    color: '#8E8E93',
    marginLeft: 4,
  },
  contactActions: {
    flexDirection: 'row',
    gap: 8,
  },
  contactActionButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F2F2F7',
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeButton: {
    backgroundColor: '#FFEBEE',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#8E8E93',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyStateSubtitle: {
    fontSize: 16,
    color: '#C7C7CC',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 22,
  },
  emptyStateButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  emptyStateButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '500',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
  },
  modalCancelButton: {
    fontSize: 16,
    color: '#8E8E93',
  },
  modalSaveButton: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
  modalContent: {
    padding: 16,
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
  textInput: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#1C1C1E',
  },
  helpText: {
    fontSize: 12,
    color: '#8E8E93',
    marginTop: 4,
    fontStyle: 'italic',
  },
  helpBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#E3F2FD',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  helpTextContent: {
    fontSize: 14,
    color: '#1565C0',
    marginLeft: 8,
    flex: 1,
    lineHeight: 20,
  },
});

export default ContactsScreen;
