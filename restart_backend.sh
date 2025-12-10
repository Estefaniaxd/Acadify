#!/bin/bash

# ==========================================
# RESTART BACKEND Y CAPTURA LOGS
# ==========================================

echo "🔴 Deteniendo backend actual..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2
echo "✅ Puerto liberado"

echo ""
echo "🟢 Iniciando backend con logging detallado..."
echo "=================================================="
echo "El backend está corriendo. Ahora:"
echo ""
echo "1. Abre http://localhost:5173 en navegador"
echo "2. Entra a una tarea"
echo "3. Upload 6 archivos"
echo "4. Click 'Entregar Tarea'"
echo "5. Observa los LOGS abajo"
echo ""
echo "Los logs te dirán EXACTAMENTE dónde falla"
echo "=================================================="
echo ""

cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
