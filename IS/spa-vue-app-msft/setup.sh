#!/bin/bash

# Vue SPA Authentication Sample - Setup Script
# ===========================================

echo "Vue SPA Authentication Sample Setup"
echo "======================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    exit 1
fi

    echo "Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "Building project..."
npm run build
if [ $? -ne 0 ]; then
    echo "Error: Build failed"
    exit 1
fi

# Check configuration
echo "Checking configuration..."
if [ -f "src/config.json" ]; then
    CLIENT_ID=$(node -e "try { console.log(require('./src/config.json').clientID) } catch(e) { console.log('') }")
    if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "your-client-id" ]; then
        echo "Warning: Please update src/config.json with your actual clientID"
        echo "   Current clientID: $CLIENT_ID"
        echo ""
        echo "To configure the application:"
        echo "   1. Open src/config.json"
        echo "   2. Replace 'your-client-id' with your actual Asgardeo client ID"
        echo "   3. Update other configuration values as needed"
        echo ""
    else
        echo "Configuration looks good!"
    fi
else
            echo "Error: src/config.json not found"
    exit 1
fi

echo ""
echo "Setup completed successfully!"
echo ""
echo "To start the application:"
echo "   ./start.sh     # Full start with build"
echo "   ./build.sh     # Production environment script with options"
echo ""
echo "For more information, visit:"
echo "   https://github.com/asgardeo/asgardeo-vue-sdk"
echo ""
