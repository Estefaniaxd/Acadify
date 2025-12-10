#!/bin/bash
# DIAGNÓSTICO VISUAL DE ARCHIVOS
# Este script reinicia el backend y prepara los logs para diagnóstico

set -e

echo "======================================================================"
echo "🔍 DIAGNÓSTICO CRÍTICO: ¿Por qué solo 1 archivo se registra?"
echo "======================================================================"
echo ""
echo "📋 Pasos que realizaremos:"
echo "   1. Matar proceso backend viejo"
echo "   2. Iniciar backend con logs detallados"
echo "   3. Instrucciones para que pruebes"
echo ""
echo "======================================================================"
echo ""

# Paso 1: Matar proceso viejo
echo "🔴 [1/3] Matando proceso backend viejo en puerto 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2
echo "✅ Puerto 8000 liberado"
echo ""

# Paso 2: Iniciar backend
echo "🟢 [2/3] Iniciando backend con logging detallado..."
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "                    LOGS DEL BACKEND"
echo "════════════════════════════════════════════════════════════════"
echo ""

cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend

# Ejecutar backend y capturar TODOS los logs
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000 2>&1 | tee /tmp/backend_logs_$(date +%s).log &

BACKEND_PID=$!

# Dar tiempo para que inicie
sleep 3

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo ""
    echo "❌ Backend falló al iniciar"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✅ Backend corriendo en PID: $BACKEND_PID"
echo ""
echo "======================================================================"
echo "📝 [3/3] PRÓXIMOS PASOS - PRUEBA ESTOS PASOS EXACTOS:"
echo "======================================================================"
echo ""
echo "1️⃣  ABRE EL NAVEGADOR:"
echo "   → http://localhost:5173"
echo ""
echo "2️⃣  ABRE DEVELOPER TOOLS (F12):"
echo "   → Pestaña: Console"
echo ""
echo "3️⃣  EN LA PÁGINA:"
echo "   → Selecciona una tarea"
echo "   → Click en 'Subir archivo'"
echo ""
echo "4️⃣  SUBE ESTOS ARCHIVOS (exactamente 6):"
echo ""
echo "   📄 archivo_1.txt"
echo "   📄 archivo_2.pdf"
echo "   📄 archivo_3.docx"
echo "   📄 archivo_4.xlsx"
echo "   📄 archivo_5.jpg"
echo "   📄 archivo_6.pptx"
echo ""
echo "   💡 Si no los tienes, puedes crear vacíos:"
echo "      touch archivo_{1..6}.txt"
echo ""
echo "5️⃣  VERIFICA EN CONSOLE:"
echo "   → Deberías ver algo como:"
echo "   → [1] archivo_1.txt (0.00 MB)"
echo "   → [2] archivo_2.pdf (0.00 MB)"
echo "   → ... etc"
echo ""
echo "6️⃣  CLICK EN 'ENTREGAR TAREA'"
echo ""
echo "7️⃣  OBSERVA LA RESPUESTA:"
echo "   → ¿Muestra 6 archivos o solo 1?"
echo "   → ¿Los nombres tienen UUID o nombres reales?"
echo ""
echo "======================================================================"
echo "📊 MIENTRAS REALIZAS ESTOS PASOS, LOS LOGS ABAJO TE MOSTRARÁN:"
echo "======================================================================"
echo ""
echo "✅ Archivos RECIBIDOS en POST /entregas"
echo "✅ Archivos GUARDADOS en disco"
echo "✅ JSON CREADO para archivos_adicionales"
echo "✅ Lo que se RETORNA en GET /entregas"
echo ""
echo "======================================================================"
echo ""
echo "⏳ Esperando que completes los pasos arriba..."
echo ""
echo "   (Este proceso seguirá corriendo en background)"
echo "   (Los logs aparecerán abajo en tiempo real)"
echo ""
echo "======================================================================"
echo ""

# Mantener el script corriendo
wait $BACKEND_PID
