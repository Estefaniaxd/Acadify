#!/usr/bin/env python3
"""
Script para probar los endpoints de cursos con datos reales de la BD
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

async def test_curso_endpoints():
    """Probar endpoints de cursos"""
    try:
        from src.api.routes.academic.curso import listar_cursos_publico, obtener_curso
        
        print("🔄 Probando endpoint público de cursos...")
        resultado = await listar_cursos_publico()
        
        print(f"✅ Status: {resultado['success']}")
        print(f"📊 Total cursos: {resultado['total']}")
        print(f"🔗 Fuente: {resultado['source']}")
        print(f"💬 Mensaje: {resultado['message']}")
        
        if resultado['data']:
            print("\n📚 Cursos encontrados:")
            for curso in resultado['data']:
                print(f"  • {curso['nombre']} (ID: {curso['id']})")
                
            # Probar endpoint específico con el primer curso
            primer_curso_id = resultado['data'][0]['id']
            print(f"\n🔄 Probando curso específico ID: {primer_curso_id}")
            
            curso_detallado = await obtener_curso(primer_curso_id)
            print(f"✅ Curso obtenido: {curso_detallado['data']['nombre']}")
            print(f"📝 Descripción: {curso_detallado['data']['descripcion']}")
            print(f"🎓 Modalidad: {curso_detallado['data']['modalidad']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    
    print("🚀 Iniciando pruebas de endpoints de cursos...")
    print("=" * 50)
    
    success = asyncio.run(test_curso_endpoints())
    
    print("=" * 50)
    if success:
        print("✅ Todas las pruebas completadas exitosamente!")
    else:
        print("❌ Algunas pruebas fallaron.")