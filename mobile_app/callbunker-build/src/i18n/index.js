/**
 * CallBunker i18n System
 * Mobile implementation of Flask-Babel functionality
 */

import { translations, LANGUAGES } from './translations';
import AsyncStorage from '@react-native-async-storage/async-storage';

class I18n {
  constructor() {
    this.currentLanguage = 'en';
    this.translations = translations;
    this.listeners = [];
  }

  async init() {
    try {
      // Try to load saved language preference
      const savedLanguage = await AsyncStorage.getItem('user_language');
      if (savedLanguage && this.translations[savedLanguage]) {
        const previousLanguage = this.currentLanguage;
        this.currentLanguage = savedLanguage;
        
        // Notify listeners if language changed during init
        if (previousLanguage !== savedLanguage) {
          this.listeners.forEach(listener => listener(savedLanguage));
        }
      }
    } catch (error) {
      console.warn('Failed to load saved language:', error);
    }
  }

  getCurrentLanguage() {
    return this.currentLanguage;
  }

  async setLanguage(languageCode) {
    if (this.translations[languageCode]) {
      this.currentLanguage = languageCode;
      
      // Save to AsyncStorage
      try {
        await AsyncStorage.setItem('user_language', languageCode);
      } catch (error) {
        console.warn('Failed to save language preference:', error);
      }
      
      // Notify listeners
      this.listeners.forEach(listener => listener(languageCode));
      
      return true;
    }
    return false;
  }

  translate(key, params = {}) {
    const languageTranslations = this.translations[this.currentLanguage] || this.translations.en;
    let translation = languageTranslations[key] || key;
    
    // Handle parameter substitution
    Object.keys(params).forEach(param => {
      translation = translation.replace(`{${param}}`, params[param]);
    });
    
    return translation;
  }

  // Short alias for translate
  t(key, params = {}) {
    return this.translate(key, params);
  }

  addLanguageChangeListener(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  getAvailableLanguages() {
    return LANGUAGES;
  }

  getLanguageName(code) {
    const language = LANGUAGES.find(lang => lang.code === code);
    return language ? language.name : code;
  }

  getLanguageNativeName(code) {
    const language = LANGUAGES.find(lang => lang.code === code);
    return language ? language.nativeName : code;
  }
}

// Create singleton instance
const i18n = new I18n();

export default i18n;
export { LANGUAGES };