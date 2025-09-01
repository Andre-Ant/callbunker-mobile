# CallBunker React Native Project Setup

## Current Project Analysis
The CallBunker mobile app is currently built with Expo. Your developer needs pure React Native project files. Here's how to convert and set up the project properly.

## React Native Project Structure Required

### **Core React Native Files Needed:**

1. **index.js** - Entry point for React Native
2. **metro.config.js** - Metro bundler configuration
3. **babel.config.js** - Babel transpiler configuration
4. **react-native.config.js** - React Native CLI configuration
5. **android/** folder - Android-specific configuration
6. **ios/** folder - iOS-specific configuration (if needed)

### **Package.json Updates**
The package.json needs React Native dependencies instead of Expo.

## Conversion Steps

### **Step 1: Create React Native Entry Point**
Create `index.js` in the root:

```javascript
import {AppRegistry} from 'react-native';
import App from './App';
import {name as appName} from './app.json';

AppRegistry.registerComponent(appName, () => App);
```

### **Step 2: Update Package.json**
Replace Expo dependencies with React Native:

```json
{
  "name": "callbunker",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "start": "react-native start",
    "android": "react-native run-android",
    "ios": "react-native run-ios",
    "build": "cd android && ./gradlew assembleRelease"
  },
  "dependencies": {
    "react": "18.2.0",
    "react-native": "0.72.6",
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/stack": "^6.3.20",
    "@react-navigation/bottom-tabs": "^6.5.11",
    "react-native-screens": "^3.25.0",
    "react-native-safe-area-context": "^4.7.4",
    "react-native-gesture-handler": "^2.13.4",
    "react-native-vector-icons": "^10.0.2"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@babel/preset-env": "^7.20.0",
    "@babel/runtime": "^7.20.0",
    "metro-react-native-babel-preset": "0.76.8"
  }
}
```

### **Step 3: Create Metro Configuration**
Create `metro.config.js`:

```javascript
const {getDefaultConfig} = require('metro-config');

module.exports = (async () => {
  const {
    resolver: {sourceExts, assetExts},
  } = await getDefaultConfig();
  
  return {
    transformer: {
      babelTransformerPath: require.resolve('metro-react-native-babel-preset'),
    },
    resolver: {
      assetExts: assetExts.filter(ext => ext !== 'svg'),
      sourceExts: [...sourceExts, 'svg'],
    },
  };
})();
```

### **Step 4: Create Babel Configuration**
Create `babel.config.js`:

```javascript
module.exports = {
  presets: ['module:metro-react-native-babel-preset'],
  plugins: [
    'react-native-reanimated/plugin',
  ],
};
```

### **Step 5: Update Android Configuration**
Ensure `android/app/src/main/java/.../MainApplication.java` exists:

```java
package com.callbunker;

import android.app.Application;
import com.facebook.react.ReactApplication;
import com.facebook.react.ReactNativeHost;
import com.facebook.react.ReactPackage;
import com.facebook.react.shell.MainReactPackage;
import java.util.Arrays;
import java.util.List;

public class MainApplication extends Application implements ReactApplication {

  private final ReactNativeHost mReactNativeHost = new ReactNativeHost(this) {
    @Override
    public boolean getUseDeveloperSupport() {
      return BuildConfig.DEBUG;
    }

    @Override
    protected List<ReactPackage> getPackages() {
      return Arrays.<ReactPackage>asList(
          new MainReactPackage()
      );
    }

    @Override
    protected String getJSMainModuleName() {
      return "index";
    }
  };

  @Override
  public ReactNativeHost getReactNativeHost() {
    return mReactNativeHost;
  }

  @Override
  public void onCreate() {
    super.onCreate();
  }
}
```

### **Step 6: Update App.js**
Remove Expo-specific imports and use pure React Native:

```javascript
import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {createStackNavigator} from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {StatusBar} from 'react-native';

// Import screens (same as current)
import HomeScreen from './src/screens/HomeScreen';
import DialerScreen from './src/screens/DialerScreen';
// ... other imports

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar barStyle="dark-content" />
      {/* Navigation structure */}
    </NavigationContainer>
  );
}
```

## Directory Structure for React Native

```
callbunker-react-native/
├── index.js                     # Entry point
├── App.js                       # Main app component
├── package.json                 # React Native dependencies
├── metro.config.js              # Metro bundler config
├── babel.config.js              # Babel config
├── react-native.config.js       # RN CLI config
├── android/                     # Android project
│   ├── app/
│   │   ├── build.gradle
│   │   └── src/main/
│   │       ├── AndroidManifest.xml
│   │       └── java/com/callbunker/
├── ios/                         # iOS project (optional)
└── src/
    ├── screens/                 # All screen components
    └── services/                # Services and context
```

## Developer Instructions

### **For Pure React Native Setup:**

1. **Initialize new React Native project:**
```bash
npx react-native init CallBunker
cd CallBunker
```

2. **Copy source code:**
```bash
# Copy src/ folder from CallBunker app
cp -r /path/to/callbunker-build/src/ ./src/

# Copy assets
cp -r /path/to/callbunker-build/assets/ ./assets/
```

3. **Install dependencies:**
```bash
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context
npm install react-native-gesture-handler react-native-vector-icons
```

4. **Link native dependencies:**
```bash
cd ios && pod install  # For iOS
# Android linking is automatic in newer RN versions
```

5. **Run the app:**
```bash
npx react-native run-android  # For Android
npx react-native run-ios      # For iOS
```

## Alternative: Expo Eject

If your developer prefers to keep the existing Expo setup but get React Native files:

```bash
cd mobile_app/callbunker-build/
npx expo eject
```

This converts the Expo project to React Native while preserving all existing code.

## What Your Developer Gets

**Pure React Native Project:**
- Standard React Native CLI project structure
- All CallBunker screens and functionality
- Native Android/iOS configurations
- No Expo dependencies
- Direct access to native modules
- Standard build processes

The conversion maintains all existing functionality while providing the React Native project structure your developer requested.