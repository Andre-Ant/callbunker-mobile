/**
 * LanguageSelectionModal Component
 * Cross-platform language picker using Modal + FlatList
 * Fixes Alert limitation of only supporting 3 buttons
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  FlatList,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import i18n, { LANGUAGES } from '../i18n';

function LanguageSelectionModal({ 
  visible, 
  onClose, 
  selectedLanguage = 'en', 
  onLanguageSelect 
}) {
  
  const handleLanguageSelect = async (languageCode) => {
    try {
      // Update i18n system
      await i18n.setLanguage(languageCode);
      
      // Call parent callback
      if (onLanguageSelect) {
        await onLanguageSelect(languageCode);
      }
      onClose();
    } catch (error) {
      console.error('Failed to change language:', error);
    }
  };

  const renderLanguageItem = ({ item }) => {
    const isSelected = item.code === selectedLanguage;
    
    return (
      <TouchableOpacity
        style={[styles.languageItem, isSelected && styles.selectedLanguageItem]}
        onPress={() => handleLanguageSelect(item.code)}
        activeOpacity={0.7}
        accessibilityRole="button"
        accessibilityLabel={`Select ${item.name}`}
        accessibilityState={{ selected: isSelected }}
      >
        <View style={styles.languageInfo}>
          <Text style={[styles.languageName, isSelected && styles.selectedLanguageName]}>
            {item.name}
          </Text>
          <Text style={[styles.nativeLanguageName, isSelected && styles.selectedNativeLanguageName]}>
            {item.nativeName}
          </Text>
        </View>
        
        {isSelected && (
          <Icon name="check" size={24} color="#007AFF" />
        )}
      </TouchableOpacity>
    );
  };

  const getCurrentLanguageName = () => {
    const language = LANGUAGES.find(lang => lang.code === selectedLanguage);
    return language ? language.name : 'English';
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <SafeAreaView style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.closeButton}
            onPress={onClose}
            activeOpacity={0.7}
            accessibilityRole="button"
            accessibilityLabel="Close language selection"
          >
            <Icon name="close" size={24} color="#007AFF" />
          </TouchableOpacity>
          
          <Text style={styles.title}>{i18n.t('Language')}</Text>
          
          <View style={styles.placeholder} />
        </View>

        {/* Current Selection Info */}
        <View style={styles.currentSelectionContainer}>
          <Text style={styles.currentSelectionLabel}>{i18n.t('Current')} {i18n.t('Language')}</Text>
          <Text style={styles.currentSelectionValue}>{getCurrentLanguageName()}</Text>
        </View>

        {/* Language List */}
        <FlatList
          data={LANGUAGES}
          renderItem={renderLanguageItem}
          keyExtractor={(item) => item.code}
          style={styles.languageList}
          contentContainerStyle={styles.languageListContent}
          showsVerticalScrollIndicator={true}
          accessibilityRole="list"
          accessibilityLabel="Available languages"
        />

        {/* Footer Info */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            {i18n.t('Language')} preference will be saved to your settings.
          </Text>
        </View>
      </SafeAreaView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  closeButton: {
    padding: 8,
    marginLeft: -8,
  },
  title: {
    fontSize: 17,
    fontWeight: '600',
    color: '#1C1C1E',
  },
  placeholder: {
    width: 40, // Same width as close button for centering
  },
  currentSelectionContainer: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  currentSelectionLabel: {
    fontSize: 13,
    color: '#8E8E93',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  currentSelectionValue: {
    fontSize: 16,
    fontWeight: '500',
    color: '#007AFF',
  },
  languageList: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  languageListContent: {
    paddingBottom: 20,
  },
  languageItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
    backgroundColor: '#FFFFFF',
  },
  selectedLanguageItem: {
    backgroundColor: '#F0F8FF',
  },
  languageInfo: {
    flex: 1,
  },
  languageName: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1C1C1E',
    marginBottom: 2,
  },
  selectedLanguageName: {
    color: '#007AFF',
  },
  nativeLanguageName: {
    fontSize: 14,
    color: '#8E8E93',
  },
  selectedNativeLanguageName: {
    color: '#007AFF',
    opacity: 0.8,
  },
  footer: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E5EA',
  },
  footerText: {
    fontSize: 13,
    color: '#8E8E93',
    textAlign: 'center',
    lineHeight: 18,
  },
});

export { LANGUAGES };
export default LanguageSelectionModal;