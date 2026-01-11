#!/bin/bash

# Sustained Load Test
# 15 peticiones cada 60 segundos durante 5 minutos (300s)
# Esto genera: ~5 lotes de 15 req = 75 peticiones totales

echo "=========================================="
echo "SUSTAINED LOAD TEST (5 min)"
echo "=========================================="
echo "Count:    15 peticiones/lote"
echo "Gap:      60 segundos entre lotes"
echo "Duration: 300 segundos (5 minutos)"
echo "Total:    ~75 peticiones"
echo "=========================================="
echo ""

./run.sh load --count 15 --gap 60 --time 300

echo ""
echo "=========================================="
echo "Test completado"
echo "=========================================="
