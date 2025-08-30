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
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useCallBunker} from '../services/CallBunkerContext';

function ContactsScreen() {
  const {
    contacts,
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

    try {
      await addTrustedContact({
        name: newContactName.trim(),
        phone_number: newContactPhone.trim(),
        auto_whitelisted: false,
      });
      
      setNewContactName('');
      setNewContactPhone('');
      setShowAddModal(false);
      
      Alert.alert('Success', `${newContactName} added to trusted contacts`);
    } catch (error) {
      console.error('Failed to add contact:', error);
    }
  };

  const handleRemoveContact = (contact) => {
    Alert.alert(
      'Remove Contact',
      `Remove ${contact.name} from trusted contacts?`,
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Remove',
          style: 'destructive',
          onPress: () => removeTrustedContact(contact.id),
        },
      ]
    );
  };

  const handleCallContact = (contact) => {
    Alert.alert(
      'Protected Call',
      `Call ${contact.name} (${contact.phone_number})?\n\nThis will be a privacy-protected call.`,
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Call',
          onPress: () => {
            // Navigate to dialer with number pre-filled
            console.log('Calling:', contact.phone_number);
          },
        },
      ]
    );
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
        <Text style={styles.contactPhone}>{contact.phone_number}</Text>
        <View style={styles.contactStatus}>
          <Icon 
            name={contact.auto_whitelisted ? 'verified' : 'verified-user'} 
            size={14} 
            color={contact.auto_whitelisted ? '#4CAF50' : '#007AFF'} 
          />
          <Text style={styles.contactStatusText}>
            {contact.auto_whitelisted ? 'Auto-whitelisted' : 'Manual whitelist'}
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
          <TouchableOpacity onPress={() => setShowAddModal(false)}>
            <Text style={styles.modalCancelButton}>Cancel</Text>
          </TouchableOpacity>
          <Text style={styles.modalTitle}>Add Contact</Text>
          <TouchableOpacity onPress={handleAddContact}>
            <Text style={styles.modalSaveButton}>Save</Text>
          </TouchableOpacity>
        </View>
        
        <View style={styles.modalContent}>
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>Name</Text>
            <TextInput
              style={styles.textInput}
              value={newContactName}
              onChangeText={setNewContactName}
              placeholder="Enter contact name"
              placeholderTextColor="#8E8E93"
            />
          </View>
          
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>Phone Number</Text>
            <TextInput
              style={styles.textInput}
              value={newContactPhone}
              onChangeText={setNewContactPhone}
              placeholder="Enter phone number"
              placeholderTextColor="#8E8E93"
              keyboardType="phone-pad"
            />
          </View>
          
          <View style={styles.helpText}>
            <Icon name="info" size={16} color="#8E8E93" />
            <Text style={styles.helpTextContent}>
              Trusted contacts can bypass call screening and reach you directly
            </Text>
          </View>
        </View>
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
      {contacts.length > 0 ? (
        <FlatList
          data={contacts}
          renderItem={renderContact}
          keyExtractor={item => item.id?.toString() || item.phone_number}
          style={styles.contactsList}
          contentContainerStyle={styles.contactsListContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
          }
        />
      ) : (
        <View style={styles.emptyState}>
          <Icon name="contacts" size={64} color="#C7C7CC" />
          <Text style={styles.emptyStateTitle}>No Trusted Contacts</Text>
          <Text style={styles.emptyStateSubtitle}>
            Add contacts who can bypass call screening
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
      });

      setNewContactName('');
      setNewContactPhone('');
      setShowAddModal(false);
      
      Alert.alert('Success', 'Contact added to trusted list');
    } catch (error) {
      console.error('Failed to add contact:', error);
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
          onPress: () => removeTrustedContact(contact.id),
        },
      ]
    );
  };

  const renderContactItem = ({item: contact}) => (
    <View style={styles.contactItem}>
      <View style={styles.contactAvatar}>
        <Text style={styles.contactInitial}>
          {contact.name.charAt(0).toUpperCase()}
        </Text>
      </View>
      
      <View style={styles.contactContent}>
        <Text style={styles.contactName}>{contact.name}</Text>
        <Text style={styles.contactPhone}>{formatPhoneNumber(contact.phone_number)}</Text>
        {contact.auto_whitelisted && (
          <View style={styles.autoWhitelistBadge}>
            <Icon name="auto-awesome" size={12} color="#4CAF50" />
            <Text style={styles.autoWhitelistText}>Auto-added</Text>
          </View>
        )}
      </View>
      
      <TouchableOpacity
        style={styles.removeButton}
        onPress={() => handleRemoveContact(contact)}
      >
        <Icon name="remove-circle-outline" size={24} color="#FF5722" />
      </TouchableOpacity>
    </View>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Icon name="group-add" size={64} color="#C7C7CC" />
      <Text style={styles.emptyStateTitle}>No Trusted Contacts</Text>
      <Text style={styles.emptyStateText}>
        Add contacts who can bypass call screening{'\n'}
        They won't need to enter a PIN to reach you
      </Text>
      <TouchableOpacity
        style={styles.emptyStateButton}
        onPress={() => setShowAddModal(true)}
      >
        <Text style={styles.emptyStateButtonText}>Add First Contact</Text>
      </TouchableOpacity>
    </View>
  );

  const renderHeader = () => (
    <View style={styles.header}>
      <View style={styles.headerContent}>
        <Text style={styles.headerTitle}>Trusted Contacts</Text>
        <Text style={styles.headerSubtitle}>
          These contacts bypass call screening
        </Text>
      </View>
      
      <TouchableOpacity
        style={styles.addButton}
        onPress={() => setShowAddModal(true)}
      >
        <Icon name="add" size={24} color="#007AFF" />
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      {renderHeader()}
      
      {contacts.length === 0 && !isLoading ? (
        renderEmptyState()
      ) : (
        <FlatList
          data={contacts}
          renderItem={renderContactItem}
          keyExtractor={(item) => item.id.toString()}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              colors={['#007AFF']}
              tintColor="#007AFF"
            />
          }
          contentContainerStyle={contacts.length === 0 ? styles.emptyContainer : styles.listContainer}
          showsVerticalScrollIndicator={false}
        />
      )}

      {/* Add Contact Modal */}
      <Modal
        visible={showAddModal}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity
              style={styles.modalButton}
              onPress={() => {
                setShowAddModal(false);
                setNewContactName('');
                setNewContactPhone('');
              }}
            >
              <Text style={styles.modalButtonText}>Cancel</Text>
            </TouchableOpacity>
            
            <Text style={styles.modalTitle}>Add Trusted Contact</Text>
            
            <TouchableOpacity
              style={styles.modalButton}
              onPress={handleAddContact}
            >
              <Text style={[styles.modalButtonText, styles.modalSaveButton]}>Save</Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.modalContent}>
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Name</Text>
              <TextInput
                style={styles.textInput}
                value={newContactName}
                onChangeText={setNewContactName}
                placeholder="Enter contact name"
                autoFocus
              />
            </View>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Phone Number</Text>
              <TextInput
                style={styles.textInput}
                value={newContactPhone}
                onChangeText={setNewContactPhone}
                placeholder="+1 (555) 123-4567"
                keyboardType="phone-pad"
              />
            </View>
            
            <View style={styles.infoBox}>
              <Icon name="info-outline" size={20} color="#007AFF" />
              <Text style={styles.infoText}>
                This contact will bypass call screening and connect directly to you without entering a PIN.
              </Text>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

// Helper functions
function formatPhoneNumber(phoneNumber) {
  if (!phoneNumber) return '';
  const cleaned = phoneNumber.replace(/\D/g, '');
  const match = cleaned.match(/^(\d{1})(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return `+${match[1]} (${match[2]}) ${match[3]}-${match[4]}`;
  }
  return phoneNumber;
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
    paddingHorizontal: 16,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  headerContent: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#8E8E93',
  },
  addButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#E3F2FD',
    justifyContent: 'center',
    alignItems: 'center',
  },
  listContainer: {
    paddingVertical: 8,
  },
  emptyContainer: {
    flex: 1,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyStateTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#8E8E93',
    marginTop: 20,
    marginBottom: 8,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#C7C7CC',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 30,
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
    fontWeight: '600',
  },
  contactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  contactAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  contactInitial: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  contactContent: {
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
    marginBottom: 4,
  },
  autoWhitelistBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F5E8',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  autoWhitelistText: {
    fontSize: 11,
    color: '#4CAF50',
    fontWeight: '500',
    marginLeft: 4,
  },
  removeButton: {
    padding: 8,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
  },
  modalButton: {
    minWidth: 60,
  },
  modalButtonText: {
    fontSize: 16,
    color: '#007AFF',
  },
  modalSaveButton: {
    fontWeight: '600',
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
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1C1C1E',
  },
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#E3F2FD',
    padding: 16,
    borderRadius: 8,
    marginTop: 20,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#007AFF',
    marginLeft: 12,
    lineHeight: 20,
  },
});

export default ContactsScreen;