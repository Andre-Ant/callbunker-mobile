/**
 * CallBunker Messages Screen
 * SMS functionality coming soon
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

function MessagesScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Icon name="message" size={64} color="#C7C7CC" />
        <Text style={styles.title}>SMS Coming Soon</Text>
        <Text style={styles.subtitle}>
          Secure messaging with privacy protection will be available shortly.
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  title: {
    fontSize: 24,
    fontWeight: '600',
    color: '#1C1C1E',
    marginTop: 16,
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
    lineHeight: 22,
  },
});

export default MessagesScreen;