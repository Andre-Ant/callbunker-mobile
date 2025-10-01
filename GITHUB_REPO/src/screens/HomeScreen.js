/**
 * CallBunker Home Screen
 * Main dashboard with privacy status and quick actions
 * Updated: September 17, 2025 - Latest production version
 */

import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useCallBunker} from '../services/CallBunkerContext';
import i18n from '../i18n';

function HomeScreen({navigation}) {
  const {
    user,
    callHistory,
    isLoading,
    error,
    loadCallHistory,
    clearError,
  } = useCallBunker();
  
  const [currentLanguage, setCurrentLanguage] = useState(i18n.getCurrentLanguage());
  
  useEffect(() => {
    // Initialize i18n system and sync current language
    const initializeLanguage = async () => {
      await i18n.init();
      setCurrentLanguage(i18n.getCurrentLanguage());
    };
    
    initializeLanguage();
    
    // Listen for language changes
    const removeListener = i18n.addLanguageChangeListener((language) => {
      setCurrentLanguage(language);
    });
    
    return removeListener;
  }, []);

  useEffect(() => {
    loadCallHistory();
  }, []);

  useEffect(() => {
    if (error) {
      Alert.alert(i18n.t('Error'), error, [
        {text: i18n.t('OK'), onPress: clearError},
      ]);
    }
  }, [error]);

  const recentCalls = callHistory.slice(0, 3);
  const totalCalls = callHistory.length;
  const protectedCalls = callHistory.filter(call => call.direction === 'outbound').length;

  const handleQuickDial = () => {
    navigation.navigate('Dialer');
  };

  const handleViewHistory = () => {
    navigation.navigate('History');
  };

  const handleManageContacts = () => {
    navigation.navigate('Contacts');
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Privacy Status Card */}
      <View style={styles.statusCard}>
        <View style={styles.statusHeader}>
          <Icon name="security" size={32} color="#4CAF50" />
          <View style={styles.statusText}>
            <Text style={styles.statusTitle}>{i18n.t('Privacy Protected')}</Text>
            <Text style={styles.statusSubtitle}>
              {i18n.t('Your real number is hidden and secure')}
            </Text>
          </View>
        </View>
        
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{protectedCalls}</Text>
            <Text style={styles.statLabel}>{i18n.t('Protected Calls')}</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{totalCalls}</Text>
            <Text style={styles.statLabel}>{i18n.t('Total Calls')}</Text>
          </View>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{i18n.t('Quick Actions')}</Text>
        
        <View style={styles.actionGrid}>
          <TouchableOpacity style={styles.actionCard} onPress={handleQuickDial}>
            <Icon name="phone" size={28} color="#007AFF" />
            <Text style={styles.actionTitle}>{i18n.t('Make Protected Call')}</Text>
            <Text style={styles.actionSubtitle}>{i18n.t('Hide your real number')}</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.actionCard} onPress={handleManageContacts}>
            <Icon name="contacts" size={28} color="#FF9500" />
            <Text style={styles.actionTitle}>{i18n.t('Trusted Contacts')}</Text>
            <Text style={styles.actionSubtitle}>{i18n.t('Manage whitelist')}</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Recent Activity */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>{i18n.t('Recent Activity')}</Text>
          <TouchableOpacity onPress={handleViewHistory}>
            <Text style={styles.viewAllText}>{i18n.t('View All')}</Text>
          </TouchableOpacity>
        </View>

        {recentCalls.length > 0 ? (
          <View style={styles.activityContainer}>
            {recentCalls.map((call, index) => (
              <View key={call.id || index} style={styles.activityItem}>
                <View style={styles.activityIcon}>
                  <Icon 
                    name={call.direction === 'outbound' ? 'call-made' : 'call-received'} 
                    size={20} 
                    color={call.status === 'completed' ? '#4CAF50' : '#FF5722'}
                  />
                </View>
                <View style={styles.activityContent}>
                  <Text style={styles.activityPhone}>{call.phoneNumber}</Text>
                  <Text style={styles.activityTime}>
                    {formatTimeAgo(call.timestamp)}
                  </Text>
                </View>
                <View style={styles.activityStatus}>
                  <Text style={[
                    styles.activityStatusText,
                    {color: call.status === 'completed' ? '#4CAF50' : '#FF5722'}
                  ]}>
                    {call.status === 'completed' ? formatDuration(call.duration) : call.status}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        ) : (
          <View style={styles.emptyState}>
            <Icon name="phone-disabled" size={48} color="#999" />
            <Text style={styles.emptyStateText}>{i18n.t('No recent calls')}</Text>
            <Text style={styles.emptyStateSubtext}>
              {i18n.t('Make your first protected call to get started')}
            </Text>
          </View>
        )}
      </View>

      {/* Features Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{i18n.t('CallBunker Features')}</Text>
        
        <View style={styles.featuresList}>
          <View style={styles.featureItem}>
            <Icon name="visibility-off" size={24} color="#007AFF" />
            <View style={styles.featureText}>
              <Text style={styles.featureTitle}>{i18n.t('Number Privacy')}</Text>
              <Text style={styles.featureDescription}>
                {i18n.t('Your real number stays hidden from all contacts')}
              </Text>
            </View>
          </View>
          
          <View style={styles.featureItem}>
            <Icon name="security" size={24} color="#4CAF50" />
            <View style={styles.featureText}>
              <Text style={styles.featureTitle}>{i18n.t('Call Screening')}</Text>
              <Text style={styles.featureDescription}>
                {i18n.t('Incoming calls require PIN or verbal authentication')}
              </Text>
            </View>
          </View>
          
          <View style={styles.featureItem}>
            <Icon name="savings" size={24} color="#FF9500" />
            <View style={styles.featureText}>
              <Text style={styles.featureTitle}>{i18n.t('Cost Effective')}</Text>
              <Text style={styles.featureDescription}>
                {i18n.t('Native calling with zero per-minute charges')}
              </Text>
            </View>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

// Helper functions
function formatTimeAgo(timestamp) {
  const now = new Date();
  const callTime = new Date(timestamp);
  const diffMs = now - callTime;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return i18n.t('Just now');
  if (diffMins < 60) return i18n.t('{n}m ago', {n: diffMins});
  if (diffHours < 24) return i18n.t('{n}h ago', {n: diffHours});
  return i18n.t('{n}d ago', {n: diffDays});
}

function formatDuration(seconds) {
  if (!seconds) return i18n.t('0s');
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return mins > 0 ? i18n.t('{mins}m {secs}s', {mins, secs}) : i18n.t('{secs}s', {secs});
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  content: {
    padding: 16,
  },
  statusCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  statusText: {
    marginLeft: 12,
    flex: 1,
  },
  statusTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 4,
  },
  statusSubtitle: {
    fontSize: 14,
    color: '#8E8E93',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#8E8E93',
    textAlign: 'center',
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#E5E5EA',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1C1C1E',
    marginBottom: 12,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  viewAllText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
  actionGrid: {
    flexDirection: 'row',
    gap: 12,
  },
  actionCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1C1C1E',
    marginTop: 8,
    marginBottom: 4,
    textAlign: 'center',
  },
  actionSubtitle: {
    fontSize: 12,
    color: '#8E8E93',
    textAlign: 'center',
  },
  activityContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    overflow: 'hidden',
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  activityIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F2F2F7',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  activityContent: {
    flex: 1,
  },
  activityPhone: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
    marginBottom: 2,
  },
  activityTime: {
    fontSize: 14,
    color: '#8E8E93',
  },
  activityStatus: {
    alignItems: 'flex-end',
  },
  activityStatusText: {
    fontSize: 14,
    fontWeight: '500',
  },
  emptyState: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 40,
    alignItems: 'center',
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '500',
    color: '#8E8E93',
    marginTop: 12,
    marginBottom: 8,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#C7C7CC',
    textAlign: 'center',
  },
  featuresList: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    overflow: 'hidden',
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  featureText: {
    marginLeft: 16,
    flex: 1,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: 14,
    color: '#8E8E93',
    lineHeight: 20,
  },
});

export default HomeScreen;