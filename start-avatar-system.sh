#!/bin/bash

# 🚀 Script de Inicio Rápido para Acadify Avatar System
# Este script facilita el inicio de ambos servicios para pruebas

echo "🎨 Acadify Avatar System - Inicio Rápido"
echo "========================================"

# Función para verificar si un puerto está en uso
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Verificar si el backend ya está ejecutándose
if check_port 8000; then
    echo "✅ Backend ya está ejecutándose en puerto 8000"
else
    echo "🚀 Iniciando Backend..."
    cd /home/esteban/Acadify/backend
    
    # Verificar si el entorno virtual existe
    if [ -d "venv" ]; then
        echo "📦 Activando entorno virtual..."
        source venv/bin/activate
    else
        echo "⚠️  Entorno virtual no encontrado. Creando..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
    
    echo "🔥 Iniciando FastAPI en puerto 8000..."
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    # Esperar a que el backend inicie
    echo "⏳ Esperando que el backend inicie..."
    sleep 5
fi

# Verificar si el frontend ya está ejecutándose
if check_port 5173; then
    echo "✅ Frontend ya está ejecutándose en puerto 5173"
else
    echo "🚀 Iniciando Frontend..."
    cd /home/esteban/Acadify/frontend
    
    # Verificar dependencias
    if [ ! -d "node_modules" ]; then
        echo "📦 Instalando dependencias de npm..."
        npm install
    fi
    
    echo "🎨 Iniciando React Dev Server en puerto 5173..."
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
fi

echo ""
echo "🎉 ¡Servicios iniciados exitosamente!"
echo "================================"
echo "🌐 Backend:  http://localhost:8000"
echo "🎨 Frontend: http://localhost:5173"
echo "🖼️  Avatar Editor: http://localhost:5173/avatar"
echo ""
echo "📚 Para ver el estado de los assets:"
echo "curl http://localhost:8000/api/v1/avatar/assets?gender=male"
echo ""
echo "🛑 Para detener los servicios:"
echo "pkill -f uvicorn"
echo "pkill -f vite"
echo ""
echo "💡 Consejo: Abre http://localhost:5173/avatar en tu navegador"
echo "y utiliza el menú lateral para acceder al Editor de Avatar."
echo ""
echo "🎨 ¡Disfruta creando avatars!"