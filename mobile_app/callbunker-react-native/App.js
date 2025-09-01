/**
 * CallBunker Mobile App - React Native Version
 * Intelligent Communication Security Platform
 */

import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {createStackNavigator} from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {StatusBar, StyleSheet} from 'react-native';

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

// Main Tab Navigator
function MainTabs() {
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
        options={{title: 'CallBunker'}}
      />
      <Tab.Screen 
        name="Dialer" 
        component={DialerScreen}
        options={{title: 'Protected Dialer'}}
      />
      <Tab.Screen 
        name="Messages" 
        component={MessagesScreen}
        options={{title: 'Anonymous SMS'}}
      />
      <Tab.Screen 
        name="History" 
        component={CallHistoryScreen}
        options={{title: 'Call History'}}
      />
      <Tab.Screen 
        name="Contacts" 
        component={ContactsScreen}
        options={{title: 'Trusted Contacts'}}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{title: 'Settings'}}
      />
    </Tab.Navigator>
  );
}

// App Navigator with Authentication
function AppNavigator() {
  const {state} = useCallBunker();
  
  return (
    <Stack.Navigator screenOptions={{headerShown: false}}>
      {state.user ? (
        <>
          <Stack.Screen name="Main" component={MainTabs} />
          <Stack.Screen 
            name="CallLogDetail" 
            component={CallLogDetailScreen}
            options={{
              headerShown: true,
              title: 'Call Details',
              headerStyle: styles.header,
              headerTintColor: '#007AFF',
            }}
          />
        </>
      ) : (
        <Stack.Screen name="Signup" component={SignupScreen} />
      )}
    </Stack.Navigator>
  );
}

// Main App Component
export default function App() {
  return (
    <CallBunkerProvider>
      <StatusBar barStyle="dark-content" backgroundColor="#f8f9fa" />
      <NavigationContainer>
        <AppNavigator />
      </NavigationContainer>
    </CallBunkerProvider>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingBottom: 5,
    paddingTop: 5,
    height: 60,
  },
  header: {
    backgroundColor: '#ffffff',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
});