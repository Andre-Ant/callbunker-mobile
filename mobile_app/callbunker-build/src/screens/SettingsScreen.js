/**
 * CallBunker Settings Screen
 * App configuration and preferences
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  Linking,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useCallBunker} from '../services/CallBunkerContext';
import LanguageSelectionModal, {LANGUAGES} from '../components/LanguageSelectionModal';

function SettingsScreen() {
  const {settings, updateSettings, callBunker} = useCallBunker();
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  
  const handleSettingChange = (key, value) => {
    updateSettings({[key]: value});
  };

  const handleTestNativeCalling = async () => {
    try {
      const isSupported = await callBunker.isNativeCallingSupported();
      const hasPermissions = await callBunker.requestCallPermissions();
      
      Alert.alert(
        'Native Calling Test',
        `Device Support: ${isSupported ? 'Yes' : 'No'}\nPermissions: ${hasPermissions ? 'Granted' : 'Denied'}`,
        [{text: 'OK'}]
      );
    } catch (error) {
      Alert.alert('Test Failed', error.message);
    }
  };

  const handlePrivacyPolicy = () => {
    Linking.openURL('https://callbunker.com/privacy');
  };

  const handleSupport = () => {
    Linking.openURL('https://callbunker.com/support');
  };

  const handleAbout = () => {
    Alert.alert(
      'CallBunker Mobile',
      'Version 1.0.0\n\nIntelligent Communication Security Platform\n\nProtect your privacy with advanced call screening and number protection.',
      [{text: 'OK'}]
    );
  };

  const handleLanguageSelect = () => {
    setShowLanguageModal(true);
  };

  const changeLanguage = async (languageCode) => {
    try {
      // Update local settings
      handleSettingChange('language', languageCode);
      
      // Show success message
      const selectedLanguage = LANGUAGES.find(lang => lang.code === languageCode);
      Alert.alert(
        'Language Preference Saved',
        `Language preference changed to ${selectedLanguage?.name || languageCode.toUpperCase()} and saved to your settings.`,
        [{text: 'OK'}]
      );
      
      // Note: In a real implementation, you would also update the backend user preferences
      // and potentially trigger an app restart or reload to apply the language change
    } catch (error) {
      Alert.alert('Error', 'Failed to change language. Please try again.');
    }
  };

  const getCurrentLanguageName = () => {
    const selectedLanguage = LANGUAGES.find(lang => lang.code === (settings.language || 'en'));
    return selectedLanguage ? selectedLanguage.name : 'English';
  };

  const renderSettingItem = (icon, title, subtitle, onPress, rightComponent) => (
    <TouchableOpacity
      style={styles.settingItem}
      onPress={onPress}
      disabled={!onPress}
      activeOpacity={onPress ? 0.7 : 1}
    >
      <View style={styles.settingIcon}>
        <Icon name={icon} size={24} color="#007AFF" />
      </View>
      
      <View style={styles.settingContent}>
        <Text style={styles.settingTitle}>{title}</Text>
        {subtitle && (
          <Text style={styles.settingSubtitle}>{subtitle}</Text>
        )}
      </View>
      
      {rightComponent || (onPress && (
        <Icon name="chevron-right" size={20} color="#C7C7CC" />
      ))}
    </TouchableOpacity>
  );

  const renderSwitchItem = (icon, title, subtitle, value, onValueChange) => (
    renderSettingItem(
      icon,
      title,
      subtitle,
      null,
      <Switch
        value={value}
        onValueChange={onValueChange}
        trackColor={{false: '#E5E5EA', true: '#007AFF'}}
        thumbColor="#FFFFFF"
      />
    )
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Privacy Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Privacy & Security</Text>
        
        {renderSwitchItem(
          'auto-awesome',
          'Auto-whitelist Verified Callers',
          'Automatically trust callers who pass authentication',
          settings.autoWhitelist,
          (value) => handleSettingChange('autoWhitelist', value)
        )}
        
        {renderSwitchItem(
          'record-voice-over',
          'Call Recording (Coming Soon)',
          'Record protected calls for security',
          false, // settings.callRecording,
          null // (value) => handleSettingChange('callRecording', value)
        )}
      </View>

      {/* Notifications */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notifications</Text>
        
        {renderSwitchItem(
          'notifications',
          'Push Notifications',
          'Get notified about calls and security events',
          settings.notifications,
          (value) => handleSettingChange('notifications', value)
        )}
      </View>

      {/* Appearance */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Appearance</Text>
        
        {renderSettingItem(
          'language',
          'Language',
          `Current: ${getCurrentLanguageName()}`,
          handleLanguageSelect
        )}
        
        {renderSwitchItem(
          'dark-mode',
          'Dark Mode (Coming Soon)',
          'Use dark theme throughout the app',
          false, // settings.darkMode,
          null // (value) => handleSettingChange('darkMode', value)
        )}
      </View>

      {/* System */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System</Text>
        
        {renderSettingItem(
          'phone',
          'Test Native Calling',
          'Check device compatibility and permissions',
          handleTestNativeCalling
        )}
        
        {renderSettingItem(
          'storage',
          'Clear Call History (Coming Soon)',
          'Remove all stored call records',
          null // handleClearHistory
        )}
      </View>

      {/* Support */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Support</Text>
        
        {renderSettingItem(
          'help',
          'Help & Support',
          'Get help with CallBunker features',
          handleSupport
        )}
        
        {renderSettingItem(
          'privacy-tip',
          'Privacy Policy',
          'Learn how we protect your data',
          handlePrivacyPolicy
        )}
        
        {renderSettingItem(
          'info',
          'About CallBunker',
          'Version and app information',
          handleAbout
        )}
      </View>

      {/* Features Overview */}
      <View style={styles.featuresSection}>
        <Text style={styles.sectionTitle}>CallBunker Features</Text>
        
        <View style={styles.featuresList}>
          <View style={styles.featureItem}>
            <Icon name="security" size={20} color="#4CAF50" />
            <Text style={styles.featureText}>Zero per-minute calling costs</Text>
          </View>
          
          <View style={styles.featureItem}>
            <Icon name="visibility-off" size={20} color="#007AFF" />
            <Text style={styles.featureText}>Complete number privacy protection</Text>
          </View>
          
          <View style={styles.featureItem}>
            <Icon name="verified-user" size={20} color="#FF9500" />
            <Text style={styles.featureText}>Advanced call screening with PIN/verbal auth</Text>
          </View>
          
          <View style={styles.featureItem}>
            <Icon name="speed" size={20} color="#9C27B0" />
            <Text style={styles.featureText}>Native device calling integration</Text>
          </View>
        </View>
      </View>

      {/* Language Selection Modal */}
      <LanguageSelectionModal
        visible={showLanguageModal}
        onClose={() => setShowLanguageModal(false)}
        selectedLanguage={settings.language || 'en'}
        onLanguageSelect={changeLanguage}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  content: {
    paddingBottom: 30,
  },
  section: {
    marginTop: 20,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#E5E5EA',
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#8E8E93',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#F8F9FA',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  settingIcon: {
    width: 32,
    height: 32,
    borderRadius: 6,
    backgroundColor: '#E3F2FD',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
    marginBottom: 2,
  },
  settingSubtitle: {
    fontSize: 14,
    color: '#8E8E93',
    lineHeight: 18,
  },
  featuresSection: {
    marginTop: 20,
    marginHorizontal: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  featuresList: {
    padding: 16,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  featureText: {
    fontSize: 14,
    color: '#1C1C1E',
    marginLeft: 12,
    flex: 1,
  },
});

export default SettingsScreen;