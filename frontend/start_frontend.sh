#!/bin/bash

# Script para iniciar el frontend de Acadify
echo "🚀 Iniciando frontend de Acadify..."
echo ""

cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/frontend

# Verificar si ya está corriendo
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️ El puerto 3000 ya está en uso"
    echo "Deteniendo proceso existente..."
    kill $(lsof -t -i:3000) 2>/dev/null
    sleep 2
fi

echo "Iniciando servidor de desarrollo..."
npm run dev
