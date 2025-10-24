from flask import Flask, redirect, request, session, url_for, jsonify
from urllib.parse import quote_plus
import base64
import json
import logging
import socket
import base64
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s')

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

# Google OAuth2 Credentials
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')

# Telefonica Number Verification API
NUMBER_VERIFICATION_CLIENT_ID = os.getenv('NUMBER_VERIFICATION_CLIENT_ID')
NUMBER_VERIFICATION_CLIENT_SECRET = os.getenv('NUMBER_VERIFICATION_CLIENT_SECRET')
NUMBER_VERIFICATION_REDIRECT_URI = os.getenv('NUMBER_VERIFICATION_REDIRECT_URI')

# Telefonica API Endpoints
NUMBER_VERIFICATION_AUTHORIZE_URL = os.getenv('NUMBER_VERIFICATION_AUTHORIZE_URL')
NUMBER_VERIFICATION_TOKEN_URL = os.getenv('NUMBER_VERIFICATION_TOKEN_URL')
NUMBER_VERIFICATION_VERIFY_URL = os.getenv('NUMBER_VERIFICATION_VERIFY_URL')
NUMBER_VERIFICATION_BASE_URL = os.getenv('NUMBER_VERIFICATION_BASE_URL')
NUMBER_VERIFICATION_VERIFY_PATH = os.getenv('NUMBER_VERIFICATION_VERIFY_PATH', '/number-verification/v0/verify')
NUMBER_VERIFICATION_SCOPE = os.getenv('NUMBER_VERIFICATION_SCOPE')

# Phone Number
DEFAULT_PHONE_NUMBER = os.getenv('DEFAULT_PHONE_NUMBER', '+34600111222')

# Server Configuration
SERVER_PORT = int(os.getenv('SERVER_PORT', '6000'))

# Home simple con enlaces de prueba (ahora manejado por home_with_callback)

@app.route('/healthz')
def healthz():
    return 'ok', 200

@app.route('/test-js')
def test_js():
    return '''
<!DOCTYPE html>
<html>
<head><title>Test JavaScript</title></head>
<body>
    <h1>Test de JavaScript</h1>
    <button onclick="testRedirect()">Probar Redirección</button>
    <div id="result"></div>
    
    <script>
        function testRedirect() {
            const clientId = 'a83566d0-dc97-406a-99a8-a63e9b3f1417';
            const scope = 'dpv:FraudPreventionAndDetection#number-verification-verify-read';
            const redirectUri = 'http://localhost:6000';
            const phoneNumber = '+34660360318';
            
            const params = new URLSearchParams({
                response_type: 'code',
                client_id: clientId,
                scope: scope,
                redirect_uri: redirectUri,
                state: phoneNumber
            });
            
            const authUrl = 'https://sandbox.opengateway.telefonica.com/apigateway/authorize?' + params.toString();
            
            document.getElementById('result').innerHTML = '<p><strong>URL generada:</strong><br>' + authUrl + '</p><p><button onclick="window.location.href=\'' + authUrl + '\'">Redirigir a Telefónica</button></p>';
            
            console.log('URL generada:', authUrl);
        }
    </script>
</body>
</html>
    '''

def render_page(title: str, body_html: str) -> str:
    return f"""
<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>
body{{font-family:system-ui,Arial;margin:24px;max-width:900px}}
pre{{background:#f5f5f5;padding:12px;overflow:auto}}
.ok{{color:#0a0}} .err{{color:#a00}}
</style></head>
<body>
<h2>{title}</h2>
{body_html}
</body></html>
"""

# 1. Inicio login Google
@app.route('/auth/google')
def google_auth():
    encoded_redirect = quote_plus(GOOGLE_REDIRECT_URI or '')
    # Agregar scopes para obtener número de teléfono (contacts.readonly para acceder a /connections)
    scope = quote_plus('email profile https://www.googleapis.com/auth/contacts.readonly')
    google_auth_url = (
        'https://accounts.google.com/o/oauth2/v2/auth?'
        f'client_id={GOOGLE_CLIENT_ID}&'
        'response_type=code&'
        f'redirect_uri={encoded_redirect}&'
        f'scope={scope}&'
        'access_type=offline&'
        'prompt=consent'
    )
    logging.info('Redirigiendo a Google OAuth: %s', google_auth_url)
    return redirect(google_auth_url)

# 2. Callback Google OAuth2
@app.route('/oauth2callback')
def google_oauth_callback():
    # Log completo de lo recibido desde Google
    logging.info('Google callback - query params: %s', dict(request.args))
    logging.info('Google callback - path: %s', request.path)
    code = request.args.get('code')
    if not code:
        logging.error('Callback Google sin parámetro code')
        return render_page('Error Google', '<p class="err">Falta parámetro code en el callback.</p>'), 400

    logging.info('Intercambiando code por token en Google...')
    token_res = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
    )
    logging.info('Google token status: %s', token_res.status_code)
    logging.info('Google token raw body: %s', token_res.text)
    try:
        token_json = token_res.json()
    except Exception:
        logging.exception('Error parseando JSON de Google')
        return render_page('Error Google', f'<p class="err">Error parseando respuesta de token.</p><pre>status={token_res.status_code}\n{token_res.text}</pre>'), 400

    if token_res.status_code != 200:
        logging.error('Fallo de token Google %s: %s', token_res.status_code, token_json)
        return render_page('Error Google', f'<p class="err">Error de token ({token_res.status_code}).</p><pre>{token_json}</pre>'), 400

    access_token = token_json.get('access_token')
    id_token = token_json.get('id_token')
    if not access_token:
        logging.error('Google no devolvió access_token: %s', token_json)
        return render_page('Error Google', f'<p class="err">Google no devolvió access_token.</p><pre>{token_json}</pre>'), 400

    # Decodificar id_token si viene (JWT)
    if id_token:
        try:
            parts = id_token.split('.')
            if len(parts) == 3:
                payload_b64 = parts[1] + '==='  # padding
                payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8'))
                logging.error('🔴 Google id_token (payload decodificado): %s', payload)
            else:
                logging.warning('id_token recibido pero no parece JWT estándar')
        except Exception:
            logging.exception('Error decodificando id_token de Google')

    logging.error('🔴 Google access_token (longitud=%s): %s', len(access_token), access_token)

    session['google_token'] = access_token
    logging.info('Login Google OK, guardado token en sesión')
    
    # Obtener número de teléfono de Google People API
    phone_number = None
    try:
        # Intentar primero con /me
        people_api_url = 'https://people.googleapis.com/v1/people/me?personFields=phoneNumbers'
        people_response = requests.get(
            people_api_url,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        logging.info('🔵 People API /me Response Status: %s', people_response.status_code)
        logging.info('🔵 People API /me Response Body: %s', people_response.text)
        
        if people_response.status_code == 200:
            people_data = people_response.json()
            phone_numbers = people_data.get('phoneNumbers', [])
            if phone_numbers:
                phone_number = phone_numbers[0].get('value')
                logging.info('📱 Número obtenido de /me: %s', phone_number)
                session['google_phone'] = phone_number
        
        # Si /me no tiene número, intentar con /connections (contactos del usuario)
        if not phone_number:
            logging.info('🔵 Intentando con /connections...')
            connections_url = 'https://people.googleapis.com/v1/people/me/connections?personFields=phoneNumbers,names&pageSize=100'
            connections_response = requests.get(
                connections_url,
                headers={'Authorization': f'Bearer {access_token}'}
            )
            logging.info('🔵 Connections Response Status: %s', connections_response.status_code)
            logging.info('🔵 Connections Response Body: %s', connections_response.text[:500])
            
            if connections_response.status_code == 200:
                connections_data = connections_response.json()
                connections = connections_data.get('connections', [])
                logging.info('🔵 Total conexiones encontradas: %s', len(connections))
                
                # Buscar el contacto del propio usuario o el primer contacto con teléfono
                for conn in connections:
                    conn_phones = conn.get('phoneNumbers', [])
                    if conn_phones:
                        phone_number = conn_phones[0].get('value')
                        conn_name = conn.get('names', [{}])[0].get('displayName', 'Unknown')
                        logging.info('📱 Número encontrado en conexión "%s": %s', conn_name, phone_number)
                        session['google_phone'] = phone_number
                        break
        
        if not phone_number:
            logging.warning('⚠️ No se pudo obtener número de teléfono de Google')
            
    except Exception:
        logging.exception('Error obteniendo número de teléfono de Google')
    
    # Mostrar los datos del JWT en una caja bonita
    jwt_data_html = f'''
    <div style="background: #f8f9fa; border: 2px solid #28a745; border-radius: 10px; padding: 20px; margin: 20px 0; font-family: monospace;">
        <h3 style="color: #28a745; margin-top: 0;">✅ Google Authentication Successful!</h3>
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h4>👤 User Data:</h4>
            <p><strong>Name:</strong> {payload.get('name', 'N/A')}</p>
            <p><strong>Email:</strong> {payload.get('email', 'N/A')}</p>
            <p><strong>ID:</strong> {payload.get('sub', 'N/A')}</p>
            <p><strong>Verified:</strong> {'✅ Yes' if payload.get('email_verified') else '❌ No'}</p>
            <p><strong>Phone Number:</strong> {phone_number if phone_number else '❌ Not available'}</p>
        </div>
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h4>🔑 JWT Token (ID Token):</h4>
            <textarea readonly style="width: 100%; height: 100px; font-family: monospace; font-size: 11px; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">{id_token}</textarea>
        </div>
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h4>🔐 Access Token:</h4>
            <textarea readonly style="width: 100%; height: 80px; font-family: monospace; font-size: 11px; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">{access_token}</textarea>
        </div>
        <div style="margin-top: 20px; text-align: center;">
            <a href="/" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px;">Back to Home</a>
            {'<a href="/auth/number-verification-auto" style="display: inline-block; padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 5px;">Verify Phone Number Automatically</a>' if phone_number else '<a href="/frontend/number-verification" style="display: inline-block; padding: 10px 20px; background: #ff7300; color: white; text-decoration: none; border-radius: 5px; margin: 5px;">Verify Number (Manual)</a>'}
        </div>
    </div>
    '''
    return render_page('✅ Google Authentication', jwt_data_html)

# 2.1. Ruta para verificación automática con número de Google
@app.route('/auth/number-verification-auto')
def number_verification_auto():
    phone_number = session.get('google_phone')
    if not phone_number:
        return render_page('❌ Error', '<p class="err">No phone number available from Google. Please use manual verification.</p><p><a href="/frontend/number-verification">Manual Verification</a></p>'), 400
    
    # Redirigir a Telefónica con el número obtenido de Google
    logging.info('🔄 Iniciando verificación automática con número: %s', phone_number)
    
    encoded_redirect_telco = quote_plus(NUMBER_VERIFICATION_REDIRECT_URI or '')
    authorize_url = (
        f'{NUMBER_VERIFICATION_AUTHORIZE_URL}?'
        'response_type=code&'
        f'client_id={NUMBER_VERIFICATION_CLIENT_ID}&'
        f'redirect_uri={encoded_redirect_telco}&'
        f'scope={quote_plus(NUMBER_VERIFICATION_SCOPE or "")}&'
        f'state={quote_plus(phone_number)}'
    )
    
    logging.info('Redirigiendo a Telefónica para verificar: %s', phone_number)
    return redirect(authorize_url)

# 3.1. Frontend: Página HTML para Number Verification (CORRECTO)
@app.route('/frontend/number-verification')
def frontend_number_verification():
    return f'''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Number Verification - Frontend</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .container {{ max-width: 600px; }}
        .form-group {{ margin: 20px 0; }}
        label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
        input[type="text"] {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
        button {{ background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
        button:hover {{ background: #0056b3; }}
        .info {{ background: #e7f3ff; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        .error {{ background: #ffe7e7; padding: 15px; border-radius: 4px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔵 Number Verification - Frontend (Correcto)</h1>
        
        <div class="info">
            <strong>¿Por qué desde el frontend?</strong><br>
            La API de Number Verification debe ejecutarse desde el dispositivo del usuario para verificar que el número pertenece a ese dispositivo específico.
        </div>
        
        <form id="numberVerificationForm">
            <div class="form-group">
                <label for="phoneNumber">Número de teléfono:</label>
                <input type="text" id="phoneNumber" name="phoneNumber" value="+34660360318" required>
            </div>
            
            <button type="submit">Verificar Número</button>
        </form>
        
        <div id="result" style="margin-top: 20px;"></div>
    </div>

    <script>
        var CLIENT_ID = "{NUMBER_VERIFICATION_CLIENT_ID}";
        var SCOPE = "{NUMBER_VERIFICATION_SCOPE}";
        var REDIRECT_URI = "{NUMBER_VERIFICATION_REDIRECT_URI}";
        
        document.getElementById('numberVerificationForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            
            var phoneNumber = document.getElementById('phoneNumber').value;
            var resultDiv = document.getElementById('result');
            
            // Construir URL de autorización
            var params = new URLSearchParams({{
                response_type: 'code',
                client_id: CLIENT_ID,
                scope: SCOPE,
                redirect_uri: REDIRECT_URI,
                state: phoneNumber
            }});
            
            var authUrl = 'https://sandbox.opengateway.telefonica.com/apigateway/authorize?' + params.toString();
            
            console.log('Redirigiendo a:', authUrl);
            resultDiv.innerHTML = '<div class="info">Redirigiendo...</div>';
            
            window.location.href = authUrl;
        }});
    </script>
</body>
</html>
    '''

# 3.2. Testing: Llamada directa a Telefónica /authorize
@app.route('/test/telefonica-authorize')
def test_telefonica_authorize():
    encoded_redirect_telco = quote_plus(NUMBER_VERIFICATION_REDIRECT_URI or '')
    number_verif_auth_url = (
        f'{NUMBER_VERIFICATION_AUTHORIZE_URL}?'
        'response_type=code&'
        f'client_id={NUMBER_VERIFICATION_CLIENT_ID}&'
        f'redirect_uri={encoded_redirect_telco}&'
        f'scope={quote_plus(NUMBER_VERIFICATION_SCOPE or "")}&'
        f'state={quote_plus(DEFAULT_PHONE_NUMBER)}'
    )
    
    logging.info('🔵 LLAMADA DIRECTA A TELEFÓNICA /AUTHORIZE:')
    logging.info('   URL: %s', number_verif_auth_url)
    logging.info('   Headers: accept=application/json')
    
    try:
        response = requests.get(
            number_verif_auth_url,
            headers={'accept': 'application/json'},
            allow_redirects=False  # No seguir redirects para ver la respuesta directa
        )
        
        logging.info('🔵 RESPUESTA DE TELEFÓNICA /AUTHORIZE:')
        logging.info('   Status Code: %s', response.status_code)
        logging.info('   Headers: %s', dict(response.headers))
        logging.info('   Body: %s', response.text)
        
        return render_page(
            'Test Telefónica /authorize', 
            f'<h3>Llamada directa a Telefónica /authorize</h3>'
            f'<p><strong>URL:</strong> {number_verif_auth_url}</p>'
            f'<p><strong>Status Code:</strong> {response.status_code}</p>'
            f'<p><strong>Headers:</strong></p><pre>{dict(response.headers)}</pre>'
            f'<p><strong>Body:</strong></p><pre>{response.text}</pre>'
        )
        
    except Exception as e:
        logging.exception('Error en llamada directa a Telefónica')
        return render_page('Error Test Telefónica', f'<p class="err">Error: {str(e)}</p>'), 500

# 3. Inicio verificación de número (2FA) - ELIMINADO (solo frontend)

# 4. Callback Number Verification
@app.route('/')
def home_with_callback():
    # Si hay parámetros de callback de Telefónica, procesarlos
    if request.args.get('code') or request.args.get('error'):
        return number_verification_callback()
    
    # Si no, mostrar la página principal
    return '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo Autenticación - Google & Telefónica</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            width: 100%;
        }
        h1 {
            color: #1a202c;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 50px;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        .options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 48px 40px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            text-decoration: none;
            color: inherit;
            display: block;
            border: 1px solid #e2e8f0;
        }
        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.1), 0 4px 8px rgba(0,0,0,0.06);
            border-color: #cbd5e0;
        }
        .card-icon {
            font-size: 2.5em;
            font-weight: 600;
            text-align: center;
            margin-bottom: 24px;
        }
        .card-title {
            font-size: 1.5em;
            font-weight: 600;
            text-align: center;
            margin-bottom: 16px;
            color: #1a202c;
        }
        .card-description {
            text-align: center;
            color: #718096;
            font-size: 0.95em;
            line-height: 1.6;
        }
        .google-card {
            border-top: 4px solid #4285f4;
        }
        .google-card .card-icon {
            color: #4285f4;
        }
        .telefonica-card {
            border-top: 4px solid #019DF4;
        }
        .telefonica-card .card-icon {
            color: #019DF4;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PoC - 2FA Telefónica</h1>
        
        <div class="options">
            <a href="/auth/google" class="card google-card">
                <div class="card-icon" style="color: #4285f4;">Google</div>
                <div class="card-title">Google OAuth</div>
                <div class="card-description">
                    Authentication with Google<br>
                    Returns JWT with your data
                </div>
            </a>
            
            <a href="/frontend/number-verification" class="card telefonica-card">
                <div class="card-icon" style="color: #019DF4;">Telefónica</div>
                <div class="card-title">Number Verification</div>
                <div class="card-description">
                    Mobile number verification<br>
                    Requires Movistar SIM card
                </div>
            </a>
        </div>
    </div>
</body>
</html>
    '''

def number_verification_callback():
    code = request.args.get('code')
    error = request.args.get('error')
    error_description = request.args.get('error_description')
    state = request.args.get('state')
    
    # Log completo de lo que recibimos de Telefónica
    logging.info('🔵 CALLBACK DE TELEFÓNICA RECIBIDO:')
    logging.info('   URL completa: %s', request.url)
    logging.info('   Query params: %s', dict(request.args))
    logging.info('   Code: %s', code)
    logging.info('   Error: %s', error)
    logging.info('   Error Description: %s', error_description)
    logging.info('   State: %s', state)
    
    if error:
        logging.error('Error en callback Number Verification: %s - %s', error, error_description)
        return render_page('Error Number Verification', f'<p class="err">Error de Telefónica: {error}</p><p>Descripción: {error_description}</p><p>Este error indica que el flujo de autorización frontend no está funcionando correctamente.</p>'), 400
    
    if not code:
        logging.error('Callback Number Verification sin parámetro code')
        return render_page('Error Number Verification', '<p class="err">Falta parámetro code en el callback.</p>'), 400

    logging.info('Intercambiando code por token en Number Verification (Basic Auth) contra %s ...', NUMBER_VERIFICATION_TOKEN_URL)
    basic_credentials = f"{NUMBER_VERIFICATION_CLIENT_ID}:{NUMBER_VERIFICATION_CLIENT_SECRET}".encode('utf-8')
    basic_b64 = base64.b64encode(basic_credentials).decode('utf-8')
    logging.info('Basic Auth: %s', basic_b64)
    
    # Log detallado de la llamada para obtener access_token
    logging.info('🔵 LLAMADA A TELEFÓNICA PARA ACCESS_TOKEN:')
    logging.info('   URL: %s', NUMBER_VERIFICATION_TOKEN_URL)
    logging.info('   Headers: Content-Type=application/x-www-form-urlencoded, Authorization=Basic %s', basic_b64)
    logging.info('   Data: grant_type=authorization_code, code=%s', code)
    
    token_res = requests.post(
        NUMBER_VERIFICATION_TOKEN_URL,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {basic_b64}',
        },
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': NUMBER_VERIFICATION_REDIRECT_URI,
        }
    )
    logging.info('Respuesta token status: %s', token_res.status_code)
    logging.info('🔵 RESPUESTA DE TELEFÓNICA PARA ACCESS_TOKEN:')
    logging.info('   Status Code: %s', token_res.status_code)
    logging.info('   Headers: %s', dict(token_res.headers))
    logging.info('   Body: %s', token_res.text)
    try:
        token_json = token_res.json()
    except Exception:
        logging.exception('Error parseando JSON de token Number Verification. status=%s body=%s', token_res.status_code, token_res.text)
        return render_page('Error Number Verification', f'<p class="err">Error parseando respuesta de token.</p><pre>status={token_res.status_code}\n{token_res.text}</pre>'), 400

    if token_res.status_code != 200:
        logging.error('Fallo token Number Verification %s: %s', token_res.status_code, token_json)
        return render_page('Error Number Verification', f'<p class="err">Error de token ({token_res.status_code}).</p><pre>{token_json}</pre>'), 400

    access_token = token_json.get('access_token')
    if not access_token:
        logging.error('Number Verification no devolvió access_token: %s', token_json)
        return render_page('Error Number Verification', f'<p class="err">No se recibió access_token.</p><pre>{token_json}</pre>'), 400
    
    logging.error('🔴 TOKEN OAUTH2 OBTENIDO: %s', access_token)
    logging.error('🔴 RESPUESTA COMPLETA: %s', token_json)

    # Asegurar que el número tenga el formato correcto (+34...)
    phone_number = state.strip() if state else DEFAULT_PHONE_NUMBER
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    # Usar el endpoint correcto que funciona
    verify_url = 'https://sandbox.opengateway.telefonica.com/apigateway/number-verification/v1/verify'
    logging.info('🔵 LLAMADA A VERIFY:')
    logging.info('   URL: %s', verify_url)
    logging.info('   Número original (state): %s', state)
    logging.info('   Número corregido: %s', phone_number)
    logging.info('   Access Token (primeros 50): %s...', access_token[:50])
    
    verification_res = requests.post(
        verify_url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        json={"phoneNumber": phone_number}
    )
    
    logging.info('🔵 RESPUESTA DE VERIFY:')
    logging.info('   Status: %s', verification_res.status_code)
    logging.info('   Headers: %s', dict(verification_res.headers))
    logging.info('   Body length: %s', len(verification_res.text))
    logging.info('   Body: %s', verification_res.text)
    
    try:
        verification_json = verification_res.json()
    except Exception:
        logging.exception('Error parseando JSON de verify')
        return render_page('Respuesta de Telefónica', f'''
            <p class="ok">✅ Autenticación exitosa con Telefónica</p>
            <p class="ok">✅ Access Token obtenido</p>
            <p class="err">⚠️ La API de verificación devolvió una respuesta no-JSON</p>
            <pre>Status: {verification_res.status_code}\nHeaders: {dict(verification_res.headers)}\nBody: {verification_res.text or "(vacío)"}</pre>
            <p>Esto puede significar que la API está funcionando pero devolvió un formato inesperado.</p>
        '''), 400

    if verification_res.status_code != 200:
        logging.error('Error verify status=%s body=%s', verification_res.status_code, verification_res.text)
        return render_page('Error Number Verification', f'<p class="err">Error en verify ({verification_res.status_code}).</p><pre>{verification_json}</pre>'), 400
    # Según guía OG, el campo es devicePhoneNumberVerified (booleano)
    result = verification_json.get('devicePhoneNumberVerified')
    
    # Crear página bonita con el resultado
    result_html = f'''
    <div style="background: #f8f9fa; border: 2px solid {'#28a745' if result else '#ffc107'}; border-radius: 10px; padding: 20px; margin: 20px 0;">
        <h3 style="color: {'#28a745' if result else '#ffc107'}; margin-top: 0;">
            {'✅ Verification Successful' if result else '⚠️ Verification Failed'}
        </h3>
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h4>📱 Verification Information:</h4>
            <p><strong>Verified number:</strong> {phone_number}</p>
            <p><strong>Result:</strong> {'✅ Number matches device SIM' if result else '❌ Number does NOT match device SIM'}</p>
            <p><strong>Device Phone Number Verified:</strong> {result}</p>
        </div>
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h4>🔍 Complete JSON Response:</h4>
            <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">{json.dumps(verification_json, indent=2, ensure_ascii=False)}</pre>
        </div>
        <div style="background: white; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h4>🔐 Access Token Used:</h4>
            <textarea readonly style="width: 100%; height: 80px; font-size: 10px; border: 1px solid #ddd; padding: 5px;">{access_token}</textarea>
        </div>
        <div style="text-align: center; margin-top: 20px;">
            <a href="/" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Back to Home</a>
        </div>
    </div>
    '''
    
    if result is True:
        return render_page('✅ Number Verification - Success', result_html), 200
    else:
        return render_page('⚠️ Number Verification - Failed', result_html), 200

if __name__ == '__main__':
    # Detectar IP local para mostrar la URL de acceso en el log
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"

    logging.info("Base URL local: http://%s:%s", local_ip, SERVER_PORT)
    logging.info("Abre esa URL desde el navegador del dispositivo externo")

    app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)
