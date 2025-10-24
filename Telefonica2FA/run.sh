#!/bin/bash

# Script para levantar el servidor Flask de Number Verification
# Mata cualquier proceso en el puerto 8080 antes de iniciar

echo "🔍 Verificando puerto 8080..."

# Buscar y matar procesos en el puerto 8080
if lsof -ti:8080 > /dev/null 2>&1; then
    echo "⚠️  Puerto 8080 ocupado. Matando procesos..."
    lsof -ti:8080 | xargs kill -9
    sleep 2
    echo "✅ Puerto 8080 liberado"
else
    echo "✅ Puerto 8080 disponible"
fi

# Cambiar al directorio del proyecto
cd "$(dirname "$0")"

# Activar el entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Levantar el servidor
echo "🚀 Iniciando servidor Flask en puerto 8080..."
python back.py
