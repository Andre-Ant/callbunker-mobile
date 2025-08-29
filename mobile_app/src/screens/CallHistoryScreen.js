/**
 * CallBunker Call History Screen
 * View all protected calls with detailed information
 */

import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useCallBunker} from '../services/CallBunkerContext';

function CallHistoryScreen({navigation}) {
  const {
    callHistory,
    isLoading,
    error,
    loadCallHistory,
    clearError,
  } = useCallBunker();
  
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadCallHistory();
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
      await loadCallHistory();
    } finally {
      setRefreshing(false);
    }
  };

  const handleCallPress = (call) => {
    navigation.navigate('CallLogDetail', {call});
  };

  const renderCallItem = ({item: call}) => (
    <TouchableOpacity
      style={styles.callItem}
      onPress={() => handleCallPress(call)}
      activeOpacity={0.7}
    >
      <View style={styles.callIcon}>
        <Icon
          name={call.direction === 'outbound' ? 'call-made' : 'call-received'}
          size={24}
          color={getCallStatusColor(call.status)}
        />
      </View>
      
      <View style={styles.callContent}>
        <View style={styles.callHeader}>
          <Text style={styles.phoneNumber}>{formatPhoneNumber(call.phoneNumber)}</Text>
          <Text style={styles.callTime}>{formatTime(call.timestamp)}</Text>
        </View>
        
        <View style={styles.callDetails}>
          <View style={styles.callerIdInfo}>
            <Icon name="security" size={14} color="#4CAF50" />
            <Text style={styles.callerIdText}>
              ID: {formatPhoneNumber(call.callerIdShown)}
            </Text>
          </View>
          
          <Text style={[styles.callStatus, {color: getCallStatusColor(call.status)}]}>
            {getCallStatusText(call.status, call.duration)}
          </Text>
        </View>
      </View>
      
      <Icon name="chevron-right" size={20} color="#C7C7CC" />
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Icon name="phone-disabled" size={64} color="#C7C7CC" />
      <Text style={styles.emptyStateTitle}>No Call History</Text>
      <Text style={styles.emptyStateText}>
        Your protected calls will appear here
      </Text>
      <TouchableOpacity
        style={styles.emptyStateButton}
        onPress={() => navigation.navigate('Dialer')}
      >
        <Text style={styles.emptyStateButtonText}>Make Your First Call</Text>
      </TouchableOpacity>
    </View>
  );

  const renderSectionHeader = (date) => (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionHeaderText}>{date}</Text>
    </View>
  );

  // Group calls by date
  const groupedCalls = groupCallsByDate(callHistory);

  return (
    <View style={styles.container}>
      {callHistory.length === 0 && !isLoading ? (
        renderEmptyState()
      ) : (
        <FlatList
          data={groupedCalls}
          renderItem={({item}) => {
            if (item.type === 'header') {
              return renderSectionHeader(item.date);
            }
            return renderCallItem({item: item.call});
          }}
          keyExtractor={(item, index) => 
            item.type === 'header' ? `header-${item.date}` : `call-${item.call.id || index}`
          }
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              colors={['#007AFF']}
              tintColor="#007AFF"
            />
          }
          contentContainerStyle={callHistory.length === 0 ? styles.emptyContainer : null}
          showsVerticalScrollIndicator={false}
        />
      )}
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

function formatTime(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) {
    return date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
  } else if (diffDays === 1) {
    return 'Yesterday';
  } else {
    return date.toLocaleDateString([], {month: 'short', day: 'numeric'});
  }
}

function formatDate(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) {
    return 'Today';
  } else if (diffDays === 1) {
    return 'Yesterday';
  } else {
    return date.toLocaleDateString([], {
      weekday: 'long',
      month: 'long', 
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  }
}

function getCallStatusColor(status) {
  switch (status) {
    case 'completed':
      return '#4CAF50';
    case 'failed':
    case 'cancelled':
      return '#FF5722';
    case 'missed':
      return '#FF9500';
    default:
      return '#8E8E93';
  }
}

function getCallStatusText(status, duration) {
  switch (status) {
    case 'completed':
      return formatDuration(duration);
    case 'failed':
      return 'Failed';
    case 'cancelled':
      return 'Cancelled';
    case 'missed':
      return 'Missed';
    default:
      return status;
  }
}

function formatDuration(seconds) {
  if (!seconds || seconds === 0) return '0s';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (mins > 0) {
    return `${mins}m ${secs}s`;
  }
  return `${secs}s`;
}

function groupCallsByDate(calls) {
  const grouped = [];
  let currentDate = null;
  
  calls.forEach(call => {
    const callDate = formatDate(call.timestamp);
    
    if (callDate !== currentDate) {
      grouped.push({
        type: 'header',
        date: callDate
      });
      currentDate = callDate;
    }
    
    grouped.push({
      type: 'call',
      call
    });
  });
  
  return grouped;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
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
  sectionHeader: {
    backgroundColor: '#F8F9FA',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  sectionHeaderText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#8E8E93',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  callItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  callIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F2F2F7',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  callContent: {
    flex: 1,
  },
  callHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  phoneNumber: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
  },
  callTime: {
    fontSize: 14,
    color: '#8E8E93',
  },
  callDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  callerIdInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  callerIdText: {
    fontSize: 12,
    color: '#4CAF50',
    marginLeft: 4,
    fontWeight: '500',
  },
  callStatus: {
    fontSize: 14,
    fontWeight: '500',
  },
});

export default CallHistoryScreen;