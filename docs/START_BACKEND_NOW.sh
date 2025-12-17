#!/bin/bash

# ============================================================
# COMANDO LISTO PARA EJECUTAR - DIAGNÓSTICO 6 ARCHIVOS
# ============================================================
# 
# Uso: Copia TODO este archivo y ejecuta en terminal
# Resultado: Backend reiniciado + logs visibles en tiempo real
#
# ============================================================

echo "🔴 ==================== PASO 1: DETENIENDO BACKEND ===================="
echo ""

# Mata proceso anterior
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Espera
sleep 2

echo "✅ Backend anterior detenido"
echo ""
echo "🟢 ==================== PASO 2: INICIANDO BACKEND NUEVO ===================="
echo ""
echo "📋 INSTRUCCIONES:"
echo ""
echo "1. El backend está corriendo aquí abajo"
echo "2. Abre otra terminal o tab"
echo "3. Navega a: http://localhost:5173"
echo "4. Entra a CUALQUIER tarea"
echo "5. Upload 6 archivos (ej: doc1.pdf, doc2.pdf, ..., doc6.pdf)"
echo "6. Click en 'ENTREGAR TAREA'"
echo "7. OBSERVA LOS LOGS QUE APARECEN ABAJO"
echo "8. Copia LOS LOGS desde '📥 POST' hasta 'COMPLETADO'"
echo "9. Comparte esos logs"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - NO cierres esta terminal"
echo "   - Los logs aparecerán cuando hagas upload + entregar"
echo "   - Busca líneas que digan:"
echo "     • 'Archivos recibidos: X' (¿cuántos?)"
echo "     • '[1] archivo1.pdf' (¿aparecen todos?)"
echo "     • 'Guardado en disco' (¿cuántas veces?)"
echo "     • 'PROCESAMIENTO COMPLETADO' (¿cuántos?)"
echo ""
echo "=============================================================="
echo ""

# Inicia backend
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Si se cierra, mostrar mensaje
echo ""
echo "❌ Backend se detuvo"
echo "Para reiniciar: ejecuta este script de nuevo"
