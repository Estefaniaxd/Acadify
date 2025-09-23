#!/usr/bin/env python3
"""
Script de prueba rápida para el backend de avatars.
"""

import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    # Cambiar al directorio del backend
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🚀 Iniciando servidor de desarrollo...")
    print("📍 URL: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🎨 Assets: http://localhost:8000/avatar/assets")
    print("🛑 Presiona Ctrl+C para detener")
    print()
    
    # Ejecutar con configuración mínima
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )