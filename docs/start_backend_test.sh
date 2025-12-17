#!/bin/bash
# Script para levantar backend y probar reacciones

echo "🚀 Iniciando Backend Acadify..."
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend

echo "📝 Verificando que el archivo reaccion_service.py está actualizado..."
grep -q "uuid4" src/services/academic/reaccion_service.py && echo "✅ UUID4 encontrado" || echo "❌ UUID4 no encontrado"

echo ""
echo "🔄 Levantando uvicorn en puerto 8000..."
echo "Presiona Ctrl+C para detener"
echo ""

uvicorn src.main:app --reload --port 8000
