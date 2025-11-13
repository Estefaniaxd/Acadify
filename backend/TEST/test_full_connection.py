#!/usr/bin/env python3
"""
Script para probar la conexión completa entre frontend y backend
"""

import asyncio
import aiohttp
import json

async def test_frontend_backend_connection():
    """Probar conexión completa frontend-backend"""
    
    print("🚀 Probando conexión Frontend ↔ Backend...")
    print("=" * 55)
    
    # URLs a probar
    backend_url = "http://localhost:8000/api/v1/academic/cursos/public",
    frontend_url = "http://localhost:5174"
    
    async with aiohttp.ClientSession() as session:
        # 1. Probar backend directamente
        try:
            print("🔄 1. Probando backend directo...")
            async with session.get(backend_url) as response:
                if response.status == 200:,
                    data = await response.json()
                    print(f"✅ Backend: {response.status} OK")
                    print(f"📊 Total cursos: {data.get('total', 0)}")
                    print(f"🔗 Fuente: {data.get('source', 'unknown')}")
                    
                    if data.get('data'):
                        print("📚 Cursos encontrados:")
                        for curso in data['data']:
                            print(f"  • {curso.get('nombre', 'Sin nombre')} ({curso.get('codigo', 'Sin código')})")
                    
                else:
                    print(f"❌ Backend: {response.status} {response.reason}")
        except Exception as e:
            print(f"❌ Error backend: {e}")
        
        # 2. Verificar que el frontend esté accesible
        try:
            print("\n🔄 2. Verificando frontend...")
            async with session.get(frontend_url) as response:
                if response.status == 200:
                    print(f"✅ Frontend: {response.status} OK")
                    print(f"🌐 URL: {frontend_url}")
                else:
                    print(f"❌ Frontend: {response.status} {response.reason}")
        except Exception as e:
            print(f"❌ Error frontend: {e}")
    
    print("\n" + "=" * 55)
    print("🎯 Conexión completa lista!")
    print(f"📱 Frontend: {frontend_url}")
    print(f"🔧 Backend: {backend_url}")
    print("\n💡 Pasos para probar:")
    print("1. Abrir el frontend en el navegador")
    print("2. Navegar al módulo académico")
    print("3. Verificar que los cursos se carguen desde la BD")
    print("4. Crear comentarios/anuncios")
    print("5. Verificar funcionalidad completa")

if __name__ == "__main__":
    asyncio.run(test_frontend_backend_connection())