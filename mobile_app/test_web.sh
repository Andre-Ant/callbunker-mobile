#!/bin/bash

# CallBunker Web Testing Script
# Quick setup for browser-based mobile testing

echo "🌐 CallBunker Web Testing Setup"
echo "==============================="

# Check if Node.js dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Install web dependencies
echo "🔧 Installing React Native Web..."
npm install react-native-web react-dom

# Create web entry point
echo "📄 Creating web entry point..."
cat > public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <meta name="theme-color" content="#000000" />
    <title>CallBunker Mobile</title>
    <style>
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: #F8F9FA;
        }
        #root {
            height: 100vh;
            max-width: 400px;
            margin: 0 auto;
            border: 1px solid #ddd;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div id="root"></div>
</body>
</html>
EOF

# Create web webpack config
echo "⚙️ Creating web configuration..."
cat > webpack.config.js << 'EOF'
const path = require('path');
const webpack = require('webpack');

module.exports = {
  mode: 'development',
  entry: './index.web.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
  },
  resolve: {
    alias: {
      'react-native$': 'react-native-web',
      'react-native-vector-icons/MaterialIcons': 'react-native-vector-icons/dist/MaterialIcons',
    },
    extensions: ['.web.js', '.js', '.json'],
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-react', '@babel/preset-env'],
            plugins: ['@babel/plugin-proposal-class-properties']
          }
        }
      }
    ]
  },
  plugins: [
    new webpack.DefinePlugin({
      __DEV__: JSON.stringify(true),
    })
  ],
  devServer: {
    static: './public',
    port: 3000,
    hot: true,
  }
};
EOF

# Create web entry point
cat > index.web.js << 'EOF'
import {AppRegistry} from 'react-native';
import App from './App';

AppRegistry.registerComponent('CallBunkerMobile', () => App);
AppRegistry.runApplication('CallBunkerMobile', {
  rootTag: document.getElementById('root'),
});
EOF

# Update package.json scripts
echo "📝 Updating package.json scripts..."
npm pkg set scripts.web="webpack serve --mode development"
npm pkg set scripts.build:web="webpack --mode production"

# Install additional web dependencies
npm install --save-dev webpack webpack-cli webpack-dev-server babel-loader @babel/core @babel/preset-env @babel/preset-react @babel/plugin-proposal-class-properties

echo ""
echo "✅ Web testing setup complete!"
echo ""
echo "🚀 Starting development server..."
echo "📱 Open http://localhost:3000 in your browser"
echo "💡 Use browser dev tools to simulate mobile device"
echo ""
echo "🧪 Test Features:"
echo "- Protected dialer interface"
echo "- Call history simulation"
echo "- Trusted contacts management"
echo "- Settings and preferences"
echo ""

# Start the web server
npm run web