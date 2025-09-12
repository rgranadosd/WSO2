ls# WSO2 API Manager - LLM Gateway

This application is a Streamlit interface to interact with LLM models (such as OpenAI and Mistral) through a WSO2 API Gateway, handling OAuth2 authentication and allowing you to dynamically select the AI provider.

## Requirements
- Python 3.8+
- The libraries listed in `requirements.txt` (Streamlit, requests, PyYAML, etc.)

## Installation
1. Clone the repository or download the files.
2. Create a virtual environment and install the dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure the `config.yaml` file (see below).

## Usage
Start the application with:
```bash
streamlit run tesing.py
```

A web interface will open where you can:
- Select the provider (OpenAI, Mistral, etc.)
- Enter your question
- View the model's response
- See counters for successful and failed calls per provider

## Configuration: `config.yaml`
The `config.yaml` file defines the available providers and their connection parameters. Example:

```yaml
providers:
  OPENAI:
    TOKEN_URL: "https://apim.dev.apis.coach:9443/oauth2/token"
    CONSUMER_KEY: "..."
    CONSUMER_SECRET: "..."
    WSO2_GATEWAY_URL: "https://localhost:8243/openaiapi/2.3.0/chat/completions"
    MODEL: "gpt-4o"
  MISTRAL:
    TOKEN_URL: "https://apim.dev.apis.coach:9443/oauth2/token"
    CONSUMER_KEY: "..."
    CONSUMER_SECRET: "..."
    WSO2_GATEWAY_URL: "https://apim.dev.apis.coach:8243/mistralaiapi_rafa/0.0.2/v1/chat/completions"
    MODEL: "mistral-tiny"
```

### Required fields per provider
- `TOKEN_URL`: OAuth2 endpoint to obtain the token.
- `CONSUMER_KEY` and `CONSUMER_SECRET`: OAuth2 credentials.
- `WSO2_GATEWAY_URL`: API Gateway endpoint for the model.
- `MODEL`: Model name to use (according to the provider).

### Adding a new provider
1. Add a new entry under `providers:` in `config.yaml` following the format above.
2. No code changes are needed: the app automatically detects the defined providers.

## Security
- Do not share your keys or secrets.
- The `config.yaml` file may contain sensitive information.

## Notes
- If you get SSL errors, you can disable verification in the code (already included for development environments).
- API error messages are shown as-is to facilitate troubleshooting.

---

**WSO2 API Manager - LLM Gateway** 