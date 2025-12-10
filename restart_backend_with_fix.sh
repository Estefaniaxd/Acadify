#!/bin/bash
# restart_backend_with_fix.sh
# Reinicia el backend con el fix aplicado

set -e

ACADIFY_PATH="/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify"
BACKEND_PATH="$ACADIFY_PATH/backend"
VENV_PATH="$BACKEND_PATH/venv"
PYTHON="$VENV_PATH/bin/python"
UVICORN="$VENV_PATH/bin/uvicorn"

echo "🔧 Reiniciando Backend con Fix..."
echo ""

# 1. Detener backend anterior
echo "⏹️  Deteniendo backend anterior..."
pkill -9 -f "uvicorn.*main:app" || true
sleep 1

# 2. Verificar que no está corriendo
if ps aux | grep -v grep | grep -q "uvicorn.*main:app"; then
    echo "❌ Backend aún está corriendo. Intenta de nuevo:"
    echo "   pkill -9 -f 'uvicorn.*main:app'"
    exit 1
fi

echo "✅ Backend detenido"
echo ""

# 3. Iniciar backend
echo "🚀 Iniciando backend..."
cd "$BACKEND_PATH"

# Activar venv e iniciar uvicorn
$PYTHON -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000 2>&1 &

BACKEND_PID=$!
echo "📌 Backend PID: $BACKEND_PID"

# 4. Esperar a que esté listo
echo ""
echo "⏳ Esperando que backend esté listo..."
sleep 3

# 5. Verificar que está corriendo
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend iniciado correctamente"
    echo ""
    echo "🔗 API disponible en: http://127.0.0.1:8000"
    echo "📚 Docs en: http://127.0.0.1:8000/docs"
    echo ""
    echo "📋 Próximos pasos:"
    echo "   1. Recarga el frontend (F5)"
    echo "   2. Intenta entregar una tarea"
    echo "   3. Verifica en DevTools que GET entrega no falla"
else
    echo "❌ Error: Backend no inició"
    sleep 2
    ps aux | grep uvicorn | grep -v grep || true
    exit 1
fi
