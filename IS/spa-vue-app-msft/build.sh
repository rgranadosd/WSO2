#!/bin/bash

# Vue SPA Authentication Sample - Production Environment Script
# ===========================================================

echo "Vue SPA Authentication - Production Environment"
echo "==============================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "   Please install Node.js from https://nodejs.org/"
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

# Check configuration
echo "Checking configuration..."
if [ -f "src/config.json" ]; then
    CLIENT_ID=$(node -e "try { console.log(require('./src/config.json').clientID) } catch(e) { console.log('') }")
    if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "your-client-id" ]; then
        echo "Warning: Please update src/config.json with your actual clientID"
        echo "   Current clientID: $CLIENT_ID"
    else
        echo "Configuration looks good"
    fi
fi

# Function to start production server
start_prod() {
    echo ""
    echo "Starting Production Server..."
    echo "   URL: http://localhost:3000"
    echo "   Hot reload: Enabled"
    echo "   Debug mode: Enabled"
    echo "   Environment: Production (all features enabled)"
    echo "   Press Ctrl+C to stop"
    echo ""
    npm start
}

# Function to build for production
build_prod() {
    echo ""
    echo "Building for Production..."
    
    # Clean previous build
    echo "Cleaning previous build..."
    rm -rf dist

    # Build the project
    echo "Building project..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "Error: Build failed"
        exit 1
    fi

    # Check if build was successful
    if [ -d "dist" ] && [ -f "dist/main.js" ]; then
        echo "Build completed successfully!"
        echo "Build files created in: dist/"
        echo "Build size:"
        ls -lh dist/
        
        echo ""
        echo "To serve the built files:"
        echo "   npm install -g serve"
        echo "   serve -s dist -l 3000"
        echo ""
    else
        echo "Error: Build files not found"
        exit 1
    fi
}

# Main script logic
echo ""
echo "Choose an option:"
echo "1) Start Production Server (all features enabled)"
echo "2) Build for Production"
echo "3) Build + Start Production Server"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        start_prod
        ;;
    2)
        build_prod
        ;;
    3)
        build_prod
        echo "Starting Production Server..."
        echo "   URL: http://localhost:3000"
        echo "   Environment: Production (built from production config)"
        echo "   Press Ctrl+C to stop"
        echo ""
        npx serve -s dist -l 3000
        ;;
    *)
        echo "Error: Invalid choice. Please run the script again and select 1, 2, or 3."
        exit 1
        ;;
esac
