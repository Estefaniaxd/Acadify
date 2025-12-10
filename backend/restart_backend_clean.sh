#!/bin/bash

echo "🔄 REINICIANDO BACKEND..."

# 1. Matar todos los procesos uvicorn
echo "1️⃣ Matando procesos uvicorn..."
pkill -9 -f "uvicorn" || true
sleep 2

# 2. Verificar que estén muertos
echo "2️⃣ Verificando que estén muertos..."
if pgrep -f "uvicorn" > /dev/null; then
    echo "❌ Aún hay procesos uvicorn"
    exit 1
else
    echo "✅ Todos los procesos terminados"
fi

# 3. Cambiar a directorio backend
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend

# 4. Activar venv
source venv/bin/activate
echo "✅ venv activado"

# 5. Iniciar uvicorn
echo "3️⃣ Iniciando uvicorn..."
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

