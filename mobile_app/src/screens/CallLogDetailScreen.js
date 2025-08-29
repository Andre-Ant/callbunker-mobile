/**
 * CallBunker Call Log Detail Screen
 * Detailed view of individual call records
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Linking,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useCallBunker} from '../services/CallBunkerContext';

function CallLogDetailScreen({route, navigation}) {
  const {call} = route.params;
  const {makeCall} = useCallBunker();

  const handleCallBack = async () => {
    try {
      Alert.alert(
        'Call Back',
        `Call ${formatPhoneNumber(call.phoneNumber)} using CallBunker protection?`,
        [
          {text: 'Cancel', style: 'cancel'},
          {
            text: 'Call',
            onPress: async () => {
              try {
                await makeCall(call.phoneNumber);
                navigation.goBack();
              } catch (error) {
                console.error('Callback failed:', error);
              }
            },
          },
        ]
      );
    } catch (error) {
      console.error('Callback preparation failed:', error);
    }
  };

  const handleAddToContacts = () => {
    Alert.alert(
      'Add to Contacts',
      'This will add the number to your trusted contacts list, allowing them to bypass call screening.',
      [
        {text: 'Cancel', style: 'cancel'},
        {text: 'Add', onPress: () => {
          // Navigate to contacts screen or show add contact modal
          navigation.navigate('Contacts');
        }},
      ]
    );
  };

  const handleBlockNumber = () => {
    Alert.alert(
      'Block Number',
      'This feature will be available in a future update.',
      [{text: 'OK'}]
    );
  };

  const renderDetailRow = (icon, label, value, onPress, valueColor) => (
    <TouchableOpacity
      style={styles.detailRow}
      onPress={onPress}
      disabled={!onPress}
      activeOpacity={onPress ? 0.7 : 1}
    >
      <View style={styles.detailIcon}>
        <Icon name={icon} size={20} color="#007AFF" />
      </View>
      
      <View style={styles.detailContent}>
        <Text style={styles.detailLabel}>{label}</Text>
        <Text style={[styles.detailValue, valueColor && {color: valueColor}]}>
          {value}
        </Text>
      </View>
      
      {onPress && (
        <Icon name="chevron-right" size={20} color="#C7C7CC" />
      )}
    </TouchableOpacity>
  );

  const getCallStatusInfo = () => {
    switch (call.status) {
      case 'completed':
        return {
          color: '#4CAF50',
          icon: 'check-circle',
          text: 'Completed Successfully'
        };
      case 'failed':
        return {
          color: '#FF5722',
          icon: 'error',
          text: 'Call Failed'
        };
      case 'cancelled':
        return {
          color: '#FF9500',
          icon: 'cancel',
          text: 'Call Cancelled'
        };
      case 'missed':
        return {
          color: '#FF9500',
          icon: 'phone-missed',
          text: 'Missed Call'
        };
      default:
        return {
          color: '#8E8E93',
          icon: 'info',
          text: call.status
        };
    }
  };

  const statusInfo = getCallStatusInfo();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Call Header */}
      <View style={styles.header}>
        <View style={[styles.statusIcon, {backgroundColor: statusInfo.color + '20'}]}>
          <Icon name={statusInfo.icon} size={32} color={statusInfo.color} />
        </View>
        
        <Text style={styles.phoneNumber}>
          {formatPhoneNumber(call.phoneNumber)}
        </Text>
        
        <Text style={[styles.statusText, {color: statusInfo.color}]}>
          {statusInfo.text}
        </Text>
        
        <Text style={styles.callTime}>
          {formatDateTime(call.timestamp)}
        </Text>
      </View>

      {/* Call Details */}
      <View style={styles.section}>
        {renderDetailRow(
          'schedule',
          'Date & Time',
          formatDateTime(call.timestamp)
        )}
        
        {renderDetailRow(
          call.direction === 'outbound' ? 'call-made' : 'call-received',
          'Direction',
          call.direction === 'outbound' ? 'Outgoing Call' : 'Incoming Call'
        )}
        
        {renderDetailRow(
          'timer',
          'Duration',
          formatDuration(call.duration)
        )}
        
        {call.callerIdShown && renderDetailRow(
          'security',
          'Caller ID Shown',
          formatPhoneNumber(call.callerIdShown),
          null,
          '#4CAF50'
        )}
      </View>

      {/* Privacy Information */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Icon name="security" size={20} color="#4CAF50" />
          <Text style={styles.sectionTitle}>Privacy Protection</Text>
        </View>
        
        <View style={styles.privacyInfo}>
          <View style={styles.privacyItem}>
            <Icon name="visibility-off" size={16} color="#4CAF50" />
            <Text style={styles.privacyText}>Your real number was hidden</Text>
          </View>
          
          <View style={styles.privacyItem}>
            <Icon name="verified-user" size={16} color="#4CAF50" />
            <Text style={styles.privacyText}>Google Voice caller ID used</Text>
          </View>
          
          <View style={styles.privacyItem}>
            <Icon name="savings" size={16} color="#4CAF50" />
            <Text style={styles.privacyText}>Native calling - carrier rates only</Text>
          </View>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.actionButton} onPress={handleCallBack}>
            <Icon name="phone" size={24} color="#4CAF50" />
            <Text style={styles.actionButtonText}>Call Back</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.actionButton} onPress={handleAddToContacts}>
            <Icon name="person-add" size={24} color="#007AFF" />
            <Text style={styles.actionButtonText}>Add Contact</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.actionButton} onPress={handleBlockNumber}>
            <Icon name="block" size={24} color="#FF5722" />
            <Text style={styles.actionButtonText}>Block</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Technical Details */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Technical Details</Text>
        
        {renderDetailRow(
          'info',
          'Call Log ID',
          call.id?.toString() || 'N/A'
        )}
        
        {renderDetailRow(
          'settings-phone',
          'Implementation',
          'Native Device Calling'
        )}
        
        {renderDetailRow(
          'code',
          'Status Code',
          call.status
        )}
      </View>
    </ScrollView>
  );
}

// Helper functions
function formatPhoneNumber(phoneNumber) {
  if (!phoneNumber) return 'Unknown';
  const cleaned = phoneNumber.replace(/\D/g, '');
  const match = cleaned.match(/^(\d{1})(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return `+${match[1]} (${match[2]}) ${match[3]}-${match[4]}`;
  }
  return phoneNumber;
}

function formatDateTime(timestamp) {
  const date = new Date(timestamp);
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  };
  return date.toLocaleDateString('en-US', options);
}

function formatDuration(seconds) {
  if (!seconds || seconds === 0) return 'No duration';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  content: {
    paddingBottom: 30,
  },
  header: {
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingVertical: 30,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  statusIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  phoneNumber: {
    fontSize: 24,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 8,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
  },
  callTime: {
    fontSize: 14,
    color: '#8E8E93',
  },
  section: {
    backgroundColor: '#FFFFFF',
    marginTop: 20,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#E5E5EA',
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#F8F9FA',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1C1C1E',
    marginLeft: 8,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  detailIcon: {
    width: 32,
    height: 32,
    borderRadius: 6,
    backgroundColor: '#E3F2FD',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  detailContent: {
    flex: 1,
  },
  detailLabel: {
    fontSize: 14,
    color: '#8E8E93',
    marginBottom: 2,
  },
  detailValue: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
  },
  privacyInfo: {
    padding: 16,
  },
  privacyItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  privacyText: {
    fontSize: 14,
    color: '#4CAF50',
    marginLeft: 8,
    fontWeight: '500',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 20,
    paddingHorizontal: 16,
  },
  actionButton: {
    alignItems: 'center',
    flex: 1,
    paddingVertical: 12,
  },
  actionButtonText: {
    fontSize: 12,
    color: '#8E8E93',
    marginTop: 4,
    fontWeight: '500',
  },
});

export default CallLogDetailScreen;