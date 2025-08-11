#!/bin/bash

# Vue SPA Authentication Sample - Start Script
# ===========================================

echo "Starting Vue SPA Authentication Sample..."
echo "=========================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    echo "Please install npm or use a Node.js installer that includes npm"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

# Check if config.json exists and has valid clientID
if [ -f "src/config.json" ]; then
    CLIENT_ID=$(node -e "try { console.log(require('./src/config.json').clientID) } catch(e) { console.log('') }")
    if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "your-client-id" ]; then
        echo "Warning: Please update src/config.json with your actual clientID"
        echo "   Current clientID: $CLIENT_ID"
        echo ""
    fi
else
            echo "Error: src/config.json not found"
    exit 1
fi

# Build the project
echo "Building project..."
npm run build
if [ $? -ne 0 ]; then
    echo "Error: Build failed"
    exit 1
fi

# Check if port 3000 is available
echo "Checking if port 3000 is available..."
PORT_3000_PID=$(lsof -ti:3000 2>/dev/null)

if [ ! -z "$PORT_3000_PID" ]; then
    echo "Port 3000 is in use by PID: $PORT_3000_PID"
    echo "Killing process on port 3000..."
    kill -9 $PORT_3000_PID 2>/dev/null
    sleep 2
    echo "Process killed. Port 3000 is now available."
else
    echo "Port 3000 is available."
fi

# Start the development server
echo "Starting development server..."
echo "   URL: http://localhost:3000"
echo "   Press Ctrl+C to stop"
echo ""

npm start
