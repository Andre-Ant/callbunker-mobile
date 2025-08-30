/**
 * CallBunker Mobile App
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

// Services
import {CallBunkerProvider} from './src/services/CallBunkerContext';

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
        options={{title: 'Messages'}}
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

// Root Stack Navigator
function App() {
  return (
    <CallBunkerProvider>
      <StatusBar barStyle="dark-content" backgroundColor="#F8F9FA" />
      <NavigationContainer>
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
              title: 'Call Details',
              headerStyle: styles.header,
              headerTintColor: '#007AFF',
              headerTitleStyle: styles.headerTitle,
            }}
          />
        </Stack.Navigator>
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