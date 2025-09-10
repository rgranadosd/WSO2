#!/usr/bin/env python3
import requests
import urllib3
from requests.auth import HTTPBasicAuth
import streamlit as st
import json
import yaml

# ------------------------------
# Localisation import
# ------------------------------
from localization import t, set_lang, get_lang

# ------------------------------
# Script para llamar a OpenAI vía WSO2
# ------------------------------

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def validate_provider_config(provider_config, required_fields, lang):
    missing = [field for field in required_fields if field not in provider_config]
    if missing:
        st.error(t('missing_fields', lang, fields=", ".join(missing)))
        st.stop()



# ------------------------------
# Language selector (with fallback)
# ------------------------------
if hasattr(st, 'sidebar'):
    lang = st.sidebar.selectbox("🌐 Language / Idioma", ["en", "es"], format_func=lambda l: {"en": "English", "es": "Español"}[l])
else:
    lang = 'en'
set_lang(lang)

required_fields = ["TOKEN_URL", "CONSUMER_KEY", "CONSUMER_SECRET", "WSO2_GATEWAY_URL"]
for prov in config["providers"]:
    validate_provider_config(config["providers"][prov], required_fields, get_lang())

# Inicialización de contadores para todos los proveedores definidos en el YAML
provider_keys = list(config["providers"].keys())
for prov in provider_keys:
    if f"{prov}_success" not in st.session_state:
        st.session_state[f"{prov}_success"] = 0
    if f"{prov}_error" not in st.session_state:
        st.session_state[f"{prov}_error"] = 0


# Banner superior con logo WSO2 y colores corporativos
display_banner = f"""
<div style='background-color:#fff;padding:18px 0 10px 0;display:flex;align-items:center;justify-content:center;border-bottom:2px solid #FF5000;'>
    <img src='https://wso2.cachefly.net/wso2/sites/all/2023/images/webp/wso2-logo.webp' alt='WSO2 Logo' style='height:44px;margin-right:24px;'>
    <span style='color:#232323;font-size:2.2rem;font-weight:bold;letter-spacing:1px;'>{t('title')}</span>
</div>
"""
st.markdown(display_banner, unsafe_allow_html=True)

st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #fff !important;
    }
    textarea, .stTextInput > div > input, .stTextArea > div > textarea {
        background-color: #fff !important;
        color: #232323 !important;
        font-size: 1.1rem !important;
        font-family: inherit !important;
        border: 1.5px solid #bbb !important;
        border-radius: 7px !important;
        box-shadow: none !important;
        padding: 8px 10px !important;
    }
    label, .stTextInput label, .stTextArea label {
        color: #232323 !important;
        font-weight: bold !important;
    }
    /* --- Eliminado CSS de .stSelectbox y dropdown para usar el estilo por defecto de Streamlit --- */
    /* Aquí terminan los estilos personalizados */
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    /* Solo personaliza el selectbox para fondo blanco y texto negro en negrita */
    .stSelectbox > div[data-baseweb="select"] {
        background-color: #fff !important;
        color: #232323 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }
    .stSelectbox > div[data-baseweb="select"] div {
        color: #232323 !important;
        font-weight: bold !important;
    }
    .stSelectbox label {
        color: #232323 !important;
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<hr style='margin:0 0 20px 0;border:1px solid #eee;'>", unsafe_allow_html=True)


# Contadores dinámicos con look WSO2 para todos los proveedores definidos en el YAML
cols = st.columns(len(provider_keys))
for idx, prov in enumerate(provider_keys):
    cols[idx].markdown(f"""
    <div style='color:#FF5000;font-size:1.1rem;font-weight:bold;'>{t('success_count', provider=prov, count=st.session_state.get(f'{prov}_success', 0))}</div>
    <div style='color:#d32f2f;font-size:1.1rem;font-weight:bold;'>{t('error_count', provider=prov, count=st.session_state.get(f'{prov}_error', 0))}</div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin:20px 0 20px 0;border:1px solid #eee;'>", unsafe_allow_html=True)


# Sección de interacción
titulo_interaccion = f"<h3 style='color:#232323;margin-bottom:10px;'>{t('select_and_ask')}</h3>"
st.markdown(titulo_interaccion, unsafe_allow_html=True)

# Select dinámico de proveedores y etiquetas
provider = st.selectbox(t('select_provider'), provider_keys, index=0)
provider_config = config["providers"][provider]

# Acceso a los valores de configuración
TOKEN_URL = provider_config["TOKEN_URL"]
CONSUMER_KEY = provider_config["CONSUMER_KEY"]
CONSUMER_SECRET = provider_config["CONSUMER_SECRET"]
WSO2_GATEWAY_URL = provider_config["WSO2_GATEWAY_URL"]



question_label = t('ask_question', provider=provider)
answer_label = t('response_from', provider=provider)

model = provider_config.get("MODEL", "")


default_question = t('default_question')
user_question = st.text_area(question_label, value=default_question, height=100)

st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

if st.button(t('send'), type="primary"):
    # Paso 1: Obtener el access token automáticamente
    try:
        token_data = {
            "grant_type": "client_credentials"
        }
        print(f"[LOG] Requesting token from: {TOKEN_URL} with client_id: {CONSUMER_KEY}")
        token_response = requests.post(
            TOKEN_URL,
            data=token_data,
            auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET),
            verify=False
        )
        print(f"[LOG] Token response status: {token_response.status_code}")
        print(f"[LOG] Token response body: {token_response.text}")
        if token_response.status_code == 200:
            access_token = token_response.json().get("access_token")
            if not access_token:
                print("[ERROR] No access token in response!")
                st.error(t('no_access_token'))
                st.error(f"Server response: {token_response.text}")
                st.stop()
        else:
            print(f"[ERROR] Token request failed: {token_response.text}")
            st.error(t('token_error', status=token_response.status_code))
            st.error(f"Server response: {token_response.text}")
            st.stop()
        # Paso 2: Hacer la llamada a la API con el token obtenido
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": user_question
                }
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        payload_str = json.dumps(payload, ensure_ascii=False)
        print(f"[LOG] JSON payload sent to model API:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")
        print(f"[LOG] Sending request to: {WSO2_GATEWAY_URL}")
        print(f"[LOG] Request headers: {headers}")
        print(f"[LOG] Request payload: {payload_str}")
        api_response = requests.post(
            WSO2_GATEWAY_URL, 
            headers=headers, 
            data=payload_str,
            verify=False
        )
        print(f"[LOG] API response status: {api_response.status_code}")
        print(f"[LOG] API response body: {api_response.text}")
        if api_response.status_code == 200:
            st.session_state[f"{provider}_success"] += 1
            try:
                result = api_response.json()
                print(f"[LOG] API response JSON: {result}")
                content = None
                if "choices" in result and result["choices"]:
                    content = result["choices"][0]["message"]["content"]
                st.session_state[f"last_response_{provider}"] = content or str(result)
            except Exception as ex:
                print(f"[ERROR] Exception parsing API response JSON: {ex}")
                st.session_state[f"last_response_{provider}"] = api_response.text
            st.rerun()
        else:
            st.session_state[f"{provider}_error"] += 1
            try:
                error_json = api_response.json()
                print(f"[ERROR] API error JSON: {error_json}")
                if isinstance(error_json, dict) and str(error_json.get("code")) == "900514":
                    # Mostrar el motivo real del bloqueo
                    reason = None
                    if (
                        "message" in error_json
                        and isinstance(error_json["message"], dict)
                        and "assessments" in error_json["message"]
                    ):
                        assessments = error_json["message"]["assessments"]
                        if isinstance(assessments, dict) and "invalidUrls" in assessments:
                            invalid_urls = ", ".join(assessments["invalidUrls"])
                            reason = t('blocked_url', urls=invalid_urls)
                        elif isinstance(assessments, str):
                            reason = assessments
                    # Si no hay assessments, intenta mostrar actionReason o el mensaje original
                    if not reason:
                        if (
                            "message" in error_json
                            and isinstance(error_json["message"], dict)
                            and "actionReason" in error_json["message"]
                        ):
                            reason = error_json["message"]["actionReason"]
                        elif "message" in error_json and "description" in error_json:
                            reason = str(error_json["message"] +  " : " + error_json["description"])
                        elif "message" in error_json:
                            reason = str(error_json["message"])
                        else:
                            reason = str(error_json)
                    st.session_state[f"last_response_{provider}"] = reason
                else:
                    st.session_state[f"last_response_{provider}"] = api_response.text
            except Exception as ex:
                print(f"[ERROR] Exception parsing API error JSON: {ex}")
                st.session_state[f"last_response_{provider}"] = t('unknown_error')
            st.rerun()
    except Exception as e:
        print(f"[ERROR] Exception in main request flow: {e}")
        st.session_state[f"{provider}_error"] += 1
        st.session_state[f"last_response_{provider}"] = t('api_request_error', error=str(e))
        st.rerun()

# Mostrar la última respuesta si existe (después del botón)
if f"last_response_{provider}" in st.session_state:
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.text_area(answer_label, value=st.session_state[f"last_response_{provider}"], height=200)

