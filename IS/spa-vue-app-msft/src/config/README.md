# Configuration Guide

This directory contains the configuration files for the Vue.js authentication application.

## Files Structure

- `index.ts` - Main configuration file that combines JSON config with environment variables
- `../config.json` - Base configuration file

## Configuration Sources (in order of precedence)

1. **Environment Variables** (highest priority)
2. **config.json** file
3. **Default values** (lowest priority)

## Environment Variables

The following environment variables can be used to override the configuration:

- `VUE_APP_CLIENT_ID` - OAuth client ID
- `VUE_APP_BASE_URL` - WSO2 Identity Server base URL
- `VUE_APP_SIGN_IN_REDIRECT_URL` - Sign-in redirect URL
- `VUE_APP_SIGN_OUT_REDIRECT_URL` - Sign-out redirect URL

## Usage

```typescript
import config from '@/config';

// Access configuration
console.log(config.clientID);
console.log(config.baseUrl);
```

## Configuration Validation

The configuration is automatically validated on import. The following checks are performed:

- Required fields are present
- Client ID is not using default placeholder values
- URLs are properly formatted

## Environment

The application uses a **single production environment** with all features enabled:

- **Environment**: Production (always)
- **OIDC Session Management**: Enabled
- **Debug Mode**: Enabled
- **Hot Reload**: Enabled
- **Error Boundary**: Enabled
- **Type Checking**: Enabled

## Best Practices

1. **Never hardcode sensitive values** in the source code
2. **Use environment variables** for configuration overrides
3. **Keep config.json** for production convenience
4. **Validate configuration** before using it
5. **Use TypeScript interfaces** for type safety

## Example .env file

```env
# Production Environment (all features enabled)
VUE_APP_CLIENT_ID=your-client-id
VUE_APP_BASE_URL=https://localhost:9443
VUE_APP_SIGN_IN_REDIRECT_URL=https://localhost:3000/auth/callback
VUE_APP_SIGN_OUT_REDIRECT_URL=https://localhost:3000
```
