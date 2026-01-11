# WSO2 APIM Load Testing Tool

Herramienta de testing de carga asincrónica para APIs WSO2 APIM con soporte OAuth2, preguntas aleatorias y ejecución de lotes con gaps configurables.

## Características

- ✅ **Autenticación OAuth2**: Generación automática de tokens
- ✅ **Peticiones aleatorias**: Selecciona preguntas al azar de un pool configurado
- ✅ **Load test simple**: Una ráfaga de N peticiones
- ✅ **Load test con lotes**: Múltiples ráfagas con gaps y duración total
- ✅ **Visualización en tiempo real**: Barras de progreso con tqdm (enviadas vs completadas)
- ✅ **Estadísticas detalladas**: Latencias, RPS actual, tasas de éxito/fallo
- ✅ **Control de RPS**: Throttling configurable de peticiones por segundo

## Instalación

### 1. Configurar variables de entorno

Edita `config.yaml` con tus credenciales:

```yaml
oauth2:
  token_url: "https://apim-next.apis.coach:9450/oauth2/token"
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
  scope: ""

api:
  endpoint: "https://apim-next.apis.coach:8250/your-api/chat/completions"
  model: "gpt-4o-mini"
  max_tokens: 200        # ⚠️ 50 causa truncado, 200+ recomendado
  temperature: 0.2
  questions:
    - "Your first question"
    - "Your second question"
    # ... más preguntas

http:
  verify_ssl: false
```

### 2. Ejecutar setup

```bash
./run.sh   # Crea venv, instala deps
```

## Uso

### Modo 1: Single Request (Verificación rápida)

```bash
./run.sh
```

**Output:**
```
[DEBUG] Fetching OAuth2 token from https://...
[DEBUG] OAuth2 token obtained successfully
[DEBUG] ========== REQUEST ==========
[DEBUG] Endpoint: https://...
[DEBUG] Headers: {...}
[DEBUG] Payload: {...}
[DEBUG] Timeout: 60s
[DEBUG] =================================

HTTP 200 | Content-Type: application/json; charset=UTF-8
Isabel's training routine...

----- Full JSON -----
{...}
```

### Modo 2: Load Test Simple (Un lote)

Lanza N peticiones a velocidad RPS configurada.

```bash
# 10 peticiones (default)
./run.sh load

# 20 peticiones a 10 RPS
./run.sh load --count 20

# 50 peticiones a 5 RPS
./run.sh load --rps 5 --count 50

# 100 peticiones a 2 RPS
./run.sh load --rps 2 --count 100
```

**Output:**
```
[INFO] Target: https://...
[INFO] RPS: 5 | Count: 20 (buckle up)

[INFO] Iniciando load test
  RPS: 5
  Peticiones totales: 20
  Endpoint: https://...
  SSL Verify: False

Enviando:   0%|               | 0/20 [00:00<?, ? req/s]
[INFO] Creando y ejecutando peticiones...
[INFO] 20 peticiones lanzadas

[20/20] ✓19 ✗1 | 4.8 req/s: 100%|████████████| 20/20 [00:04<00:00, 5.2 req/s]

============================================================
LOAD TEST SUMMARY
============================================================
Total time:     4.25s
Target RPS:     5
Actual RPS:     4.71
Total requests: 20
Success:        19 (95.0%)
Failed:         1 (5.0%)

Error breakdown:
  HTTP 446: 1

Latency (ms):
  Average:    1245.67
  P50:        1150.00
  P95:        1890.00
  P99:        1950.00
============================================================
```

### Modo 3: Load Test con Lotes y Gaps

Lanza múltiples lotes de peticiones separados por gaps, durante un tiempo total.

```bash
# 15 peticiones cada 30s durante 5 minutos (300s)
./run.sh load --count 15 --gap 30 --time 300

# 10 peticiones cada 20s durante 2 minutos a 8 RPS
./run.sh load --rps 8 --count 10 --gap 20 --time 120

# 5 peticiones cada 45s durante 3 minutos a 2 RPS
./run.sh load --rps 2 --count 5 --gap 45 --time 180
```

**Output:**
```
[INFO] Target: https://...
[INFO] RPS: 10 | Count/batch: 3 | Gap: 10s | Duration: 25s

============================================================
BATCH #1 @ t=0.0s
============================================================

[INFO] Iniciando load test
  RPS: 10
  Peticiones totales: 3
  ...
[3/3] ✓2 ✗1 | 1.5 req/s: 100%|████████████| 3/3 [00:02<00:00, 1.5 req/s]

LOAD TEST SUMMARY
...
Total requests: 3
Success:        2 (66.7%)
...

[INFO] Esperando 10s antes del siguiente lote...

============================================================
BATCH #2 @ t=12.4s
============================================================
...
```

## Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `--rps` | int | 10 | Peticiones por segundo (throttling) |
| `--count` | int | 10 | Total de peticiones por lote |
| `--gap` | int | None | Segundos de espera entre lotes (opcional) |
| `--time` | int | None | Duración total en segundos (requerido con `--gap`) |

### Combinaciones válidas:

```bash
# ✅ Válido: modo simple
./run.sh load
./run.sh load --count 20
./run.sh load --rps 5 --count 50

# ✅ Válido: modo con lotes
./run.sh load --gap 30 --time 300          # usa defaults: rps=10, count=10
./run.sh load --count 15 --gap 30 --time 300
./run.sh load --rps 8 --count 20 --gap 45 --time 600

# ❌ Inválido: --gap sin --time (se fija --time=300 automáticamente)
./run.sh load --count 10 --gap 20          # WARN: --time seteado a 300
```

## Interpretación de Resultados

### Latencia
- **Average**: Tiempo promedio de respuesta (ms)
- **P50**: Percentil 50% (mediana)
- **P95**: Percentil 95% (95% de requests más rápidos)
- **P99**: Percentil 99% (99% de requests más rápidos)

### Errores
- **HTTP 446**: Content moderation bloqueó (Azure Content Safety)
- **HTTP 429**: Rate limit excedido
- **HTTP 5xx**: Error del servidor
- **TIMEOUT**: Request excedió 60 segundos
- **CONN_ERROR**: Problema de conexión

### Métricas
- **Actual RPS**: RPS real alcanzado (puede ser menor al target si hay latencia)
- **Success rate**: % de requests con HTTP 200-299
- **Fail rate**: % de requests con errores

## Ejemplos de Casos de Uso

### Caso 1: Prueba rápida de conectividad
```bash
./run.sh load --count 3
```
Verifica que el endpoint responde con 3 peticiones rápidas.

### Caso 2: Test de carga sostenida (5 minutos)
```bash
./run.sh load --rps 10 --count 30 --gap 60 --time 300
```
- Cada minuto: 30 peticiones a 10 RPS (3 segundos)
- Pausa de 60 segundos antes del siguiente lote
- Total: 5 minutos

### Caso 3: Prueba de pico de carga
```bash
./run.sh load --rps 20 --count 100
```
100 peticiones seguidas a 20 RPS (máximo stress en corto plazo).

### Caso 4: Test de degradación (rampdown)
```bash
./run.sh load --rps 50 --count 50
./run.sh load --rps 25 --count 50
./run.sh load --rps 10 --count 50
```
Ejecutar secuencialmente para ver cómo se degrada el rendimiento.

### Caso 5: Test nocturno de larga duración (hora)
```bash
./run.sh load --rps 5 --count 20 --gap 120 --time 3600
```
- 20 peticiones cada 2 minutos
- Durante 1 hora total
- Carga leve sostenida

## Troubleshooting

### "finish_reason: length"
El modelo cortó porque llegó al `max_tokens`. Aumenta en `config.yaml`:
```yaml
api:
  max_tokens: 200  # Era 50, ahora 200+
```

### HTTP 446 (Content Moderation)
Azure Content Safety bloqueó. Revisa `config.yaml` → `questions`, evita términos sensibles.

### TIMEOUT después de 60s
El backend no responde. Verifica:
1. Endpoint accesible: `curl -k -v https://endpoint`
2. OAuth2 funciona: `./run.sh` (single request)
3. Firewall/VPN bloqueando puerto

### Conexión rechazada
Puerto no accesible. Verifica red y configuración del endpoint en `config.yaml`.

## Archivos

```
.
├── app.py           # Single request tester (OAuth2 + API call)
├── load_test.py     # Async load test (simple + lotes)
├── config.yaml      # Configuración (credenciales, preguntas, endpoint)
├── run.sh           # Script de setup y lanzamiento
└── README.md        # Este archivo
```

## Dependencias

```
requests>=2.28.0      # OAuth2 + sync requests
aiohttp>=3.9.0       # Async HTTP client
pyyaml>=6.0          # Config parsing
tqdm>=4.65.0         # Progress bars
```

Instaladas automáticamente por `./run.sh`.

## Notas de Performance

- **RPS máximo recomendado**: 20-50 (depende del endpoint)
- **Max connections**: 500 por defecto (configurable en `load_test.py`)
- **Timeout**: 60 segundos para todas las requests
- **SSL verify**: `false` (para certificados auto-firmados)

## License

MIT / Internal Use Only
