/**
 * CallBunker Mobile App
 * Intelligent Communication Security Platform
 */

import React, {useState, useEffect} from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {createStackNavigator} from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {StatusBar, StyleSheet} from 'react-native';
import i18n from './src/i18n';

// Screens
import HomeScreen from './src/screens/HomeScreen';
import DialerScreen from './src/screens/DialerScreen';
import CallHistoryScreen from './src/screens/CallHistoryScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import ContactsScreen from './src/screens/ContactsScreen';
import MessagesScreen from './src/screens/MessagesScreen';
import CallLogDetailScreen from './src/screens/CallLogDetailScreen';
import SignupScreen from './src/screens/SignupScreen';

// Services
import {CallBunkerProvider, useCallBunker} from './src/services/CallBunkerContext';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Main Tab Navigator with i18n support
function MainTabs() {
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
  
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        tabBarIcon: ({focused, color, size}) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = 'security';
          } else if (route.name === 'Dialer') {
            iconName = 'phone';
          } else if (route.name === 'Messages') {
            iconName = 'message';
          } else if (route.name === 'History') {
            iconName = 'history';
          } else if (route.name === 'Contacts') {
            iconName = 'contacts';
          } else if (route.name === 'Settings') {
            iconName = 'settings';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: styles.tabBar,
        headerStyle: styles.header,
        headerTintColor: '#007AFF',
        headerTitleStyle: styles.headerTitle,
      })}>
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{title: i18n.t('Home')}}
      />
      <Tab.Screen 
        name="Dialer" 
        component={DialerScreen}
        options={{title: i18n.t('Protected Dialer')}}
      />
      <Tab.Screen 
        name="Messages" 
        component={MessagesScreen}
        options={{title: i18n.t('Messages')}}
      />
      <Tab.Screen 
        name="History" 
        component={CallHistoryScreen}
        options={{title: i18n.t('History')}}
      />
      <Tab.Screen 
        name="Contacts" 
        component={ContactsScreen}
        options={{title: i18n.t('Contacts')}}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{title: i18n.t('Settings')}}
      />
    </Tab.Navigator>
  );
}

// Authentication Check Component
function AuthCheck() {
  const { isAuthenticated, userId } = useCallBunker();
  
  if (!isAuthenticated || !userId) {
    return (
      <Stack.Navigator screenOptions={{headerShown: false}}>
        <Stack.Screen name="Signup" component={SignupScreen} />
      </Stack.Navigator>
    );
  }
  
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}>
      <Stack.Screen name="MainTabs" component={MainTabs} />
      <Stack.Screen 
        name="CallLogDetail" 
        component={CallLogDetailScreen}
        options={{
          headerShown: true,
          title: i18n.t('Call Details'),
          headerStyle: styles.header,
          headerTintColor: '#007AFF',
          headerTitleStyle: styles.headerTitle,
        }}
      />
    </Stack.Navigator>
  );
}

// Root App
function App() {
  return (
    <CallBunkerProvider>
      <StatusBar barStyle="dark-content" backgroundColor="#F8F9FA" />
      <NavigationContainer>
        <AuthCheck />
      </NavigationContainer>
    </CallBunkerProvider>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E5E5EA',
    paddingBottom: 5,
    paddingTop: 5,
    height: 60,
  },
  header: {
    backgroundColor: '#F8F9FA',
    shadowColor: 'transparent',
    elevation: 0,
  },
  headerTitle: {
    fontWeight: '600',
    fontSize: 18,
  },
});

export default App;