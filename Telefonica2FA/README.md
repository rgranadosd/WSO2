# PoC - 2FA Telefónica

Proof of Concept demonstrating two-factor authentication (2FA) integration with Google OAuth and Telefónica's Number Verification API.

## Overview

This Flask application provides a complete implementation of:
- **Google OAuth 2.0** authentication with user profile retrieval
- **Telefónica Number Verification API** for mobile number verification via carrier network
- Seamless integration between both authentication methods

## Features

- Google OAuth login with JWT token display
- Telefónica Number Verification using OpenGateway API
- Automatic phone number retrieval from Google Contacts (when available)
- Manual phone number input fallback
- Professional, modern UI design
- Comprehensive logging for debugging
- Automatic server restart script

## Prerequisites

- Python 3.8+
- Google Cloud Platform account with OAuth credentials
- Telefónica OpenGateway developer account
- Movistar SIM card (for Number Verification testing)

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/rgranadosd/WSO2.git
cd WSO2/Telefonica2FA
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install flask requests python-dotenv
```

4. **Configure environment variables:**

Create a `.env` file in the project root with the following variables:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8080/oauth2callback

# Telefónica Number Verification Configuration
NUMBER_VERIFICATION_CLIENT_ID=your_telefonica_client_id
NUMBER_VERIFICATION_CLIENT_SECRET=your_telefonica_client_secret
NUMBER_VERIFICATION_AUTHORIZE_URL=https://sandbox.opengateway.telefonica.com/apigateway/authorize
NUMBER_VERIFICATION_TOKEN_URL=https://sandbox.opengateway.telefonica.com/apigateway/token
NUMBER_VERIFICATION_VERIFY_URL=https://sandbox.opengateway.telefonica.com/apigateway/number-verification/v1/verify
NUMBER_VERIFICATION_REDIRECT_URI=http://localhost:8080
NUMBER_VERIFICATION_SCOPE=dpv:FraudPreventionAndDetection#number-verification-verify-read
DEFAULT_PHONE_NUMBER=+34660360318
```

## Google Cloud Console Setup

### 1. Enable Required APIs

- Go to [Google Cloud Console](https://console.cloud.google.com)
- Enable **Google People API**
- Enable **OAuth 2.0**

### 2. Configure OAuth Consent Screen

- Navigate to: APIs & Services → OAuth consent screen
- Set User Type to "External" (for testing)
- Add test users under "Test users" section
- Add your email address as a test user

### 3. Create OAuth Credentials

- Go to: APIs & Services → Credentials
- Create OAuth 2.0 Client ID
- Application type: Web application
- Authorized redirect URIs: `http://localhost:8080/oauth2callback`

### 4. Configure Scopes

The application requests the following scopes:
- `email` - User email address
- `profile` - User profile information
- `https://www.googleapis.com/auth/contacts.readonly` - Read contacts for phone number retrieval

## Telefónica OpenGateway Setup

### 1. Register Application

- Visit [Telefónica OpenGateway Developer Portal](https://developers.opengateway.telefonica.com)
- Create a new application
- Subscribe to **Number Verification API**

### 2. Configure Redirect URI

- Set redirect URI to: `http://localhost:8080`
- Must match exactly with `NUMBER_VERIFICATION_REDIRECT_URI` in `.env`

### 3. Note API Credentials

- Copy `client_id` and `client_secret` to your `.env` file

## Running the Application

### Option 1: Using the startup script (Recommended)

```bash
./run.sh
```

This script will:
- Check if port 8080 is available
- Kill any existing processes on port 8080
- Activate the virtual environment
- Start the Flask server

### Option 2: Manual start

```bash
source venv/bin/activate
python back.py
```

The server will start on:
- `http://localhost:8080` (for local testing with tethering)
- `http://<your-local-ip>:8080` (for external device testing)

## Usage

### Google OAuth Flow

1. Navigate to `http://localhost:8080/`
2. Click on **"Google OAuth"** card
3. Authenticate with your Google account
4. View returned JWT token and user data
5. If phone number is available in Google Contacts, you'll see a button for automatic verification

### Telefónica Number Verification Flow

#### Automatic (if phone number retrieved from Google):
1. Complete Google OAuth first
2. Click **"Verify Phone Number Automatically"**
3. Authorize with Telefónica (must use Movistar mobile data or tethering)
4. View verification result

#### Manual:
1. From home page, click **"Number Verification"** card
2. Enter your phone number in international format (e.g., `+34660360318`)
3. Click **"Verify Number"**
4. Authorize with Telefónica (must use Movistar mobile data or tethering)
5. View verification result

## Important Notes

### Network Requirements

- **Telefónica Number Verification** requires:
  - Active Movistar SIM card
  - Device connected via Movistar mobile data OR
  - Laptop using tethering from Movistar mobile device

### Localhost vs IP Address

- Use `localhost:8080` when testing with tethering from Movistar mobile
- The redirect URI must be exactly `http://localhost:8080` (not IP address)
- IP addresses change depending on network, causing OAuth callback failures

### Phone Number Format

Phone numbers must be in E.164 format:
- Include country code: `+34`
- No spaces or special characters
- Example: `+34660360318`

### Google Phone Number Retrieval

The application attempts to retrieve phone numbers from Google via:
1. Google People API `/me` endpoint (user's own profile)
2. Google Contacts API `/connections` endpoint (user's contacts)

**Note:** Phone numbers may not be available if:
- User hasn't added their number to Google Contacts
- Google Workspace policies restrict access (corporate accounts)
- Privacy settings prevent API access

In these cases, the manual input flow will be used.

## Project Structure

```
.
├── back.py              # Main Flask application
├── run.sh              # Server startup script
├── .env                # Environment variables (not in git)
├── requirements.txt    # Python dependencies
├── venv/              # Virtual environment (not in git)
├── README.md          # This file
├── LICENSE            # Apache 2.0 license
└── .gitignore         # Git ignore rules
```

## API Endpoints

### Application Routes

- `GET /` - Home page with authentication options
- `GET /auth/google` - Initiate Google OAuth flow
- `GET /oauth2callback` - Google OAuth callback handler
- `GET /frontend/number-verification` - Number verification input form
- `GET /auth/number-verification-auto` - Automatic verification with Google phone number

### External API Calls

**Google APIs:**
- `POST https://oauth2.googleapis.com/token` - Exchange authorization code for access token
- `GET https://people.googleapis.com/v1/people/me` - Get user profile
- `GET https://people.googleapis.com/v1/people/me/connections` - Get user contacts

**Telefónica APIs:**
- `GET https://sandbox.opengateway.telefonica.com/apigateway/authorize` - Initiate number verification
- `POST https://sandbox.opengateway.telefonica.com/apigateway/token` - Get access token
- `POST https://sandbox.opengateway.telefonica.com/apigateway/number-verification/v1/verify` - Verify phone number

## Troubleshooting

### Port 8080 already in use

```bash
lsof -ti:8080 | xargs kill -9
```

Or use the provided script which handles this automatically:
```bash
./run.sh
```

### OAuth redirect URI mismatch

Ensure the redirect URI in `.env` exactly matches the one configured in:
- Google Cloud Console
- Telefónica Developer Portal

### Number Verification fails

- Verify you're using Movistar mobile data or tethering
- Check the phone number format includes `+` prefix
- Ensure NUMBER_VERIFICATION_REDIRECT_URI is `http://localhost:8080`

### Google People API 403 error

- Enable Google People API in Google Cloud Console
- Add your email as a test user in OAuth consent screen
- Wait 1-2 minutes for changes to propagate

## Development

### Debug Mode

The application runs with Flask debug mode enabled by default:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Logging

Comprehensive logging is enabled for all API calls:
- Request URLs and headers
- Response status codes and bodies
- Token information (first 50 characters for security)

Check the console output for detailed logs.

## Security Considerations

- Never commit `.env` file to version control
- Access tokens are logged (first 50 chars only) for debugging
- Use HTTPS in production
- Implement proper session management for production
- Consider using production WSGI server (e.g., Gunicorn)

## Production Deployment

For production use, consider:
- Using a production WSGI server (Gunicorn, uWSGI)
- Enabling HTTPS with proper SSL certificates
- Implementing rate limiting
- Adding CSRF protection
- Using secure session cookies
- Storing secrets in secure vault (not .env files)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

For issues related to:
- **Google OAuth**: [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- **Telefónica APIs**: [OpenGateway Documentation](https://developers.opengateway.telefonica.com/)

## Acknowledgments

- Google OAuth 2.0 implementation
- Telefónica OpenGateway Number Verification API
- Flask web framework

