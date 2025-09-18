#!/bin/bash

echo "==================================="
echo "🔍 Buscando Token Endpoint de WSO2"
echo "==================================="
echo ""

# Lista de posibles endpoints
ENDPOINTS=(
    "https://localhost:8243/oauth2/token"
    "https://localhost:8243/t/carbon.super/oauth2/token"
    "https://localhost:9443/oauth2/token"
    "https://localhost:8243/token"
    "https://localhost:9443/token"
)

echo "Probando endpoints comunes..."
echo ""

for endpoint in "${ENDPOINTS[@]}"; do
    echo "→ Probando: $endpoint"
    
    # Hacer la petición y capturar el código HTTP
    response=$(curl -k -s -w "\nHTTP_CODE:%{http_code}" -X POST "$endpoint" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "grant_type=client_credentials" 2>/dev/null)
    
    http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_CODE/d' | head -c 100)
    
    if [ "$http_code" == "404" ]; then
        echo "  ❌ 404 - No existe"
    elif [ "$http_code" == "401" ] || [ "$http_code" == "400" ]; then
        echo "  ✅ ENCONTRADO! (devuelve $http_code - necesita credenciales)"
        echo "  📝 Usa este endpoint en tu .env:"
        echo "     WSO2_TOKEN_ENDPOINT=$endpoint"
        echo ""
    elif [ "$http_code" == "200" ]; then
        echo "  ✅ ENCONTRADO! (devuelve 200)"
        echo "  📝 Usa este endpoint en tu .env:"
        echo "     WSO2_TOKEN_ENDPOINT=$endpoint"
        echo ""
    else
        echo "  ⚠️  Código HTTP: $http_code"
        echo "     Respuesta: $body"
    fi
    echo ""
done

echo "==================================="
echo "📌 Siguiente paso:"
echo "1. Actualiza WSO2_TOKEN_ENDPOINT en tu archivo .env"
echo "2. Ejecuta tu script de Python nuevamente"
echo "==================================="