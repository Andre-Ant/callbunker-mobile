/**
 * CallBunker Settings Screen
 * App configuration and preferences
 */

import React, {useState, useEffect} from 'react';
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
import LanguageSelectionModal from '../components/LanguageSelectionModal';
import i18n, { LANGUAGES } from '../i18n';

function SettingsScreen() {
  const {settings, updateSettings, callBunker} = useCallBunker();
  const [showLanguageModal, setShowLanguageModal] = useState(false);
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
  
  const handleSettingChange = (key, value) => {
    updateSettings({[key]: value});
  };

  const handleTestNativeCalling = async () => {
    try {
      const isSupported = await callBunker.isNativeCallingSupported();
      const hasPermissions = await callBunker.requestCallPermissions();
      
      Alert.alert(
        i18n.t('Test Native Calling'),
        `${i18n.t('Device Support')}: ${isSupported ? i18n.t('Yes') : i18n.t('No')}\n${i18n.t('Permissions')}: ${hasPermissions ? i18n.t('Granted') : i18n.t('Denied')}`,
        [{text: i18n.t('OK')}]
      );
    } catch (error) {
      Alert.alert(i18n.t('Test Failed'), error.message);
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
      i18n.t('CallBunker Mobile'),
      `${i18n.t('Version')} 1.0.0\n\n${i18n.t('Intelligent Communication Security Platform')}\n\n${i18n.t('Protect your privacy with advanced call screening and number protection')}.`,
      [{text: i18n.t('OK')}]
    );
  };

  const handleLanguageSelect = () => {
    setShowLanguageModal(true);
  };

  const changeLanguage = async (languageCode) => {
    try {
      // Update i18n system
      await i18n.setLanguage(languageCode);
      
      // Update local settings
      handleSettingChange('language', languageCode);
      
      // Show success message
      const selectedLanguage = LANGUAGES.find(lang => lang.code === languageCode);
      Alert.alert(
        i18n.t('Language Preference Saved'),
        i18n.t('Language preference changed to {language} and saved to your settings.', {
          language: selectedLanguage?.name || languageCode.toUpperCase()
        }),
        [{text: i18n.t('OK')}]
      );
      
      // TODO: Update backend user preferences via API call
    } catch (error) {
      Alert.alert(i18n.t('Error'), i18n.t('Failed to change language. Please try again.'));
    }
  };

  const getCurrentLanguageName = () => {
    const selectedLanguage = LANGUAGES.find(lang => lang.code === currentLanguage);
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
        <Text style={styles.sectionTitle}>{i18n.t('Privacy & Security')}</Text>
        
        {renderSwitchItem(
          'auto-awesome',
          i18n.t('Auto-whitelist Verified Callers'),
          i18n.t('Automatically trust callers who pass authentication'),
          settings.autoWhitelist,
          (value) => handleSettingChange('autoWhitelist', value)
        )}
        
        {renderSwitchItem(
          'record-voice-over',
          i18n.t('Call Recording (Coming Soon)'),
          i18n.t('Record protected calls for security'),
          false, // settings.callRecording,
          null // (value) => handleSettingChange('callRecording', value)
        )}
      </View>

      {/* Notifications */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{i18n.t('Notifications')}</Text>
        
        {renderSwitchItem(
          'notifications',
          i18n.t('Push Notifications'),
          i18n.t('Get notified about calls and security events'),
          settings.notifications,
          (value) => handleSettingChange('notifications', value)
        )}
      </View>

      {/* Appearance */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{i18n.t('Appearance')}</Text>
        
        {renderSettingItem(
          'language',
          i18n.t('Language'),
          `${i18n.t('Current')}: ${getCurrentLanguageName()}`,
          handleLanguageSelect
        )}
        
        {renderSwitchItem(
          'dark-mode',
          i18n.t('Dark Mode (Coming Soon)'),
          i18n.t('Use dark theme throughout the app'),
          false, // settings.darkMode,
          null // (value) => handleSettingChange('darkMode', value)
        )}
      </View>

      {/* System */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{i18n.t('System')}</Text>
        
        {renderSettingItem(
          'phone',
          i18n.t('Test Native Calling'),
          i18n.t('Check device compatibility and permissions'),
          handleTestNativeCalling
        )}
        
        {renderSettingItem(
          'storage',
          i18n.t('Clear Call History (Coming Soon)'),
          i18n.t('Remove all stored call records'),
          null // handleClearHistory
        )}
      </View>

      {/* Support */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{i18n.t('Support')}</Text>
        
        {renderSettingItem(
          'help',
          i18n.t('Help & Support'),
          i18n.t('Get help with CallBunker features'),
          handleSupport
        )}
        
        {renderSettingItem(
          'privacy-tip',
          i18n.t('Privacy Policy'),
          i18n.t('Learn how we protect your data'),
          handlePrivacyPolicy
        )}
        
        {renderSettingItem(
          'info',
          i18n.t('About CallBunker'),
          i18n.t('Version and app information'),
          handleAbout
        )}
      </View>

      {/* Features Overview */}
      <View style={styles.featuresSection}>
        <Text style={styles.sectionTitle}>{i18n.t('CallBunker Features')}</Text>
        
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
        selectedLanguage={currentLanguage}
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