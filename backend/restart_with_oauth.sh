#!/bin/bash

# Script para reiniciar el servidor backend con OAuth
echo "🔄 Reiniciando servidor backend..."
echo ""

# Encontrar y matar el proceso de uvicorn
PID=$(ps aux | grep -E "uvicorn src.main:app" | grep -v grep | awk '{print $2}' | head -1)

if [ -n "$PID" ]; then
    echo "Deteniendo servidor existente (PID: $PID)..."
    kill $PID
    sleep 2
    echo "✓ Servidor detenido"
else
    echo "No se encontró servidor corriendo"
fi

echo ""
echo "Iniciando servidor con OAuth habilitado..."
echo ""

# Activar entorno virtual e iniciar servidor
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
