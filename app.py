import base64
import json
import random
import sys
from pathlib import Path

import requests
import yaml


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found (surprise, surprise): {path}")
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def build_basic_auth(client_id: str, client_secret: str) -> str:
    raw = f"{client_id}:{client_secret}".encode("ascii")
    return base64.b64encode(raw).decode("ascii")


def fetch_token(cfg: dict) -> tuple[str, str]:
    oauth_cfg = cfg.get("oauth2", {})
    api_cfg = cfg.get("api", {})
    client_id = (oauth_cfg.get("client_id") or "").strip()
    client_secret = (oauth_cfg.get("client_secret") or "").strip()

    if client_id and client_secret:
        print(f"[DEBUG] Fetching OAuth2 token from {oauth_cfg['token_url']}")
        headers = {
            "Authorization": f"Basic {build_basic_auth(client_id, client_secret)}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}
        scope = (oauth_cfg.get("scope") or "").strip()
        if scope:
            data["scope"] = scope
        response = requests.post(
            oauth_cfg["token_url"], headers=headers, data=data, timeout=10, verify=False
        )
        response.raise_for_status()
        payload = response.json()
        token = payload.get("access_token")
        if not token:
            raise RuntimeError("No access_token in OAuth2 response (someone messed up)")
        print(f"[DEBUG] OAuth2 token obtained successfully")
        return token, "oauth"

    api_key = (api_cfg.get("api_key") or "").strip()
    if api_key:
        print(f"[DEBUG] Using direct API Key (ballsy move)")
        return api_key, "api_key"

    raise RuntimeError("Missing client_id/client_secret or api_key in config.yaml (oops)")


def call_api(cfg: dict, token: str, token_source: str) -> requests.Response:
    api_cfg = cfg["api"]
    http_cfg = cfg.get("http", {})
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # Use Bearer in Authorization with the token
    headers["Authorization"] = f"Bearer {token}"

    questions = api_cfg.get("questions")
    if questions and isinstance(questions, list):
        question_text = random.choice(questions)
    else:
        question_text = api_cfg.get("question", "").strip()

    payload = {
        "model": api_cfg.get("model", "").strip(),
        "messages": [
            {"role": "user", "content": question_text},
        ],
        "max_tokens": api_cfg.get("max_tokens", 1000),
        "temperature": api_cfg.get("temperature", 0.2),
    }

    timeout = api_cfg.get("timeout_seconds", 10)
    
    print(f"\n[DEBUG] ========== REQUEST ==========")
    print(f"[DEBUG] Endpoint: {api_cfg['endpoint']}")
    print(f"[DEBUG] Headers: {json.dumps(headers, indent=2)}")
    print(f"[DEBUG] Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print(f"[DEBUG] Timeout: {timeout}s")
    print(f"[DEBUG] =================================\n")
    
    response = requests.post(
        api_cfg["endpoint"],
        json=payload,
        headers=headers,
        timeout=timeout,
        verify=http_cfg.get("verify_ssl", True),
    )
    response.raise_for_status()
    return response


def main() -> None:
    config_path = Path("config.yaml")
    try:
        cfg = load_config(config_path)
        token, token_source = fetch_token(cfg)
        print(f"[DEBUG] Token type: {token_source}")
        print(f"[DEBUG] Token (first 50 chars): {token[:50]}...")
        response = call_api(cfg, token, token_source)
    except requests.exceptions.Timeout:
        print("Error: TIMEOUT - El servidor no respondió en el tiempo límite")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"Error: CONNECTION - No se pudo conectar al servidor: {e}")
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}")
        sys.exit(1)

    print("API Response:\n")
    print(f"HTTP {response.status_code} | Content-Type: {response.headers.get('content-type', '')}")
    try:
        parsed = response.json()
        content = None
        if isinstance(parsed, dict):
            choices = parsed.get("choices")
            if choices and isinstance(choices, list):
                first = choices[0] or {}
                msg = first.get("message") or {}
                content = msg.get("content")
        if content:
            print(content)
            print("\n----- Full JSON (for those who love verbose output) -----")
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    except ValueError:
        print(response.text)


if __name__ == "__main__":
    main()
