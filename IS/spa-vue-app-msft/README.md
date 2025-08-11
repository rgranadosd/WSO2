# Vue.js 3.5.18 SPA Authentication Sample

A Vue.js 3.5.18 Single Page Application (SPA) that demonstrates authentication using the Asgardeo Auth SPA SDK.

## Quick Start

### Prerequisites
- Node.js (v14 or higher)
- npm (comes with Node.js)

### Installation & Setup

#### For All Platforms:
1. **Clone or navigate to the project directory**
   ```bash
   cd vue-app-microsoft
   ```

2. **Run the setup script**
   ```bash
   ./setup.sh
   ```

3. **Configure the application**
   - Open `src/config.json`
   - Replace the `clientID` with your actual Asgardeo client ID
   - Update other configuration values as needed

4. **Start the application**
   ```bash
   ./start.sh
   ```

## How to Run the Application

### Step 1: Initial Setup
Run the setup script to prepare the environment:
```bash
./setup.sh
```

This script will:
- Check if Node.js and npm are installed
- Install all dependencies
- Build the project
- Verify configuration
- Provide guidance if configuration needs to be updated

### Step 2: Configure the Application
Before running, ensure your configuration is correct:
1. Open `src/config.json`
2. Replace `"clientID": "your-client-id"` with your actual Asgardeo client ID
3. Update other configuration values if needed

### Step 3: Start the Application

#### Option A: Quick Start (Recommended)
```bash
./start.sh
```
This starts the production server immediately on http://localhost:3000

#### Option B: Interactive Script
```bash
./build.sh
```
This provides interactive options:
1. **Start Production Server** - Hot reload, debugging, all features enabled
2. **Build for Production** - Create optimized files in `dist/` folder
3. **Build + Start Production Server** - Build and serve production files

### Available Scripts

- **`./setup.sh`** - Initial setup and environment preparation
- **`./start.sh`** - Quick start production server
- **`./build.sh`** - Interactive production environment script

## Manual Commands

If you prefer to run commands manually instead of using the scripts:

```bash
# Install dependencies
npm install

# Start production server
npm start

# Build for production
npm run build
```

**Note**: Using the provided scripts (`./setup.sh`, `./start.sh`, `./build.sh`) is recommended as they include additional checks and guidance.

## Production Environment

The application uses a **single production environment** with all features enabled:

- **OIDC Session Management**: Enabled for better session handling
- **Debug Mode**: Enhanced logging and error reporting
- **Hot Reload**: Automatic reload on file changes
- **Error Boundary**: Graceful error handling
- **Type Checking**: Full TypeScript support
- **Production Environment**: All features enabled by default

## Project Structure

```
vue-app-microsoft/
├── src/
│   ├── components/          # Vue components
│   ├── layouts/             # Layout components
│   ├── pages/               # Page components
│   ├── composables/         # Vue composables
│   ├── router/              # Vue Router configuration
│   ├── assets/              # Static assets
│   ├── config.json          # Asgardeo configuration
│   ├── main.ts              # Application entry point
│   └── App.vue              # Root component
├── dist/                    # Built files (generated)
├── *.sh                     # Execution scripts
└── package.json             # Dependencies and scripts
```

## Configuration

The application is configured through `src/config.json` with a production environment:

```json
{
  "clientID": "your-client-id",
  "baseUrl": "https://localhost:9443",
  "signInRedirectURL": "https://localhost:3000/auth/callback",
  "signOutRedirectURL": "https://localhost:3000",
  "scope": ["openid", "profile", "email", "address", "phone"],
  "enableOIDCSessionManagement": true,
  "checkSessionInterval": 3,
  "environment": "production",
  "enableDebugMode": true,
  "enableHotReload": true,
  "enableErrorBoundary": true,
  "enableTypeChecking": true
}
```

### Required Configuration
- **clientID**: Your Asgardeo application client ID
- **baseUrl**: Your Asgardeo server URL
- **signInRedirectURL**: Where to redirect after successful login
- **signOutRedirectURL**: Where to redirect after logout

### Features (All Enabled)
- **enableOIDCSessionManagement**: OIDC session management for better session handling
- **enableDebugMode**: Enhanced logging and debugging capabilities
- **enableHotReload**: Automatic reload on file changes during production
- **enableErrorBoundary**: Graceful error handling and recovery
- **enableTypeChecking**: Full TypeScript type checking support

## Accessing the Application

Once started, the application will be available at:
- **URL**: http://localhost:3000
- **Port**: 3000 (configurable in package.json)

## Troubleshooting

### Common Issues

1. **"Node.js is not installed"**
   - Install Node.js from https://nodejs.org/

2. **"npm is not installed"**
   - npm comes with Node.js, reinstall Node.js

3. **"Build failed"**
   - Check if all dependencies are installed: `npm install`
   - Check for TypeScript errors in the console

4. **"Configuration error"**
   - Update `src/config.json` with valid Asgardeo credentials
   - Ensure your Asgardeo server is running

5. **"Port 3000 is already in use"**
   - Stop other applications using port 3000
   - Or change the port in package.json

### Debug Mode

For detailed debugging, run:
```bash
npm start
```

## Example Usage

### Complete Workflow Example

```bash
# 1. Navigate to project directory
cd vue-app-microsoft

# 2. Run setup (first time only)
./setup.sh

# 3. Configure your client ID in src/config.json
# Replace "your-client-id" with your actual Asgardeo client ID

# 4. Start the application
./start.sh

# 5. Open browser and go to http://localhost:3000
```

### Production Workflow

```bash
# For production use
./start.sh                    # Quick start
# or
./build.sh                    # Interactive options

# To rebuild after changes
npm run build                 # Manual build
# or
./build.sh                    # Choose option 2
```

## Documentation

- [Asgardeo Auth SPA SDK](https://github.com/asgardeo/asgardeo-auth-spa)
- [Vue.js 3.5.18 Documentation](https://vuejs.org/)
- [Vue Router](https://router.vuejs.org/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

---

**Note**: This is a Vue.js 3.5.18 version of the original React SPA authentication sample, demonstrating the same functionality using Vue.js and the Asgardeo Auth SPA SDK.
