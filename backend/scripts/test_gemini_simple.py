"""
Test simple del GeminiService sin dependencias de modelos SQLAlchemy.

Este script prueba el servicio de IA con datos mockeados.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.ai import GeminiService, AIConfig


async def test_simple():
    """Test simple de análisis de código con IA."""
    
    print("="*80)
    print("TEST SIMPLE: GeminiService - Análisis de Código Python")
    print("="*80)
    print()
    
    # 1. Inicializar servicio
    print("📋 Inicializando GeminiService...")
    service = GeminiService()
    
    try:
        await service.inicializar()
        print("✅ Servicio inicializado correctamente\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 2. Código a analizar
    codigo_estudiante = """
def calcular_promedio(numeros):
    suma = 0
    for n in numeros:
        suma = suma + n
    return suma / len(numeros)

# Probar función
notas = [4.5, 3.8, 4.2, 5.0]
print(calcular_promedio(notas))
"""
    
    print("📝 Código a analizar:")
    print("-"*80)
    print(codigo_estudiante)
    print("-"*80)
    print()
    
    # 3. Crear prompt para análisis
    prompt = f"""Eres un profesor de programación. Analiza el siguiente código Python y proporciona retroalimentación constructiva en formato JSON.

CÓDIGO:
```python
{codigo_estudiante}
```

INSTRUCCIONES:
Evalúa el código considerando:
1. Funcionalidad (¿hace lo que debe hacer?)
2. Buenas prácticas (PEP 8, nombres descriptivos)
3. Eficiencia (¿hay forma mejor?)
4. Manejo de errores (¿valida inputs?)

Responde ÚNICAMENTE con un JSON válido con esta estructura:
{{
  "analisis_general": "Resumen del código en 2-3 oraciones",
  "fortalezas": ["Punto positivo 1", "Punto positivo 2"],
  "areas_mejora": ["Área 1 a mejorar", "Área 2"],
  "sugerencias": [
    {{
      "problema": "Descripción del problema",
      "solucion": "Cómo mejorarlo",
      "codigo_mejorado": "Ejemplo de código mejorado"
    }}
  ],
  "calificacion": 4.2
}}

NO incluyas markdown ni texto fuera del JSON."""
    
    # 4. Llamar a la API
    print("🤖 Enviando a Gemini para análisis...")
    
    try:
        respuesta = service.model.generate_content(
            prompt,
            generation_config=service.ai_config.get_generation_config()
        )
        
        print("✅ Respuesta recibida\n")
        
        # 5. Parsear respuesta
        texto_respuesta = respuesta.text
        
        # Limpiar markdown si existe
        if "```json" in texto_respuesta:
            texto_respuesta = texto_respuesta.split("```json")[1].split("```")[0]
        elif "```" in texto_respuesta:
            texto_respuesta = texto_respuesta.split("```")[1].split("```")[0]
        
        # Parsear JSON
        resultado = json.loads(texto_respuesta.strip())
        
        # 6. Mostrar resultados
        print("="*80)
        print("RETROALIMENTACIÓN DE IA")
        print("="*80)
        print()
        
        print("📊 ANÁLISIS GENERAL:")
        print(resultado.get("analisis_general", "N/A"))
        print()
        
        print("✨ FORTALEZAS:")
        for i, fortaleza in enumerate(resultado.get("fortalezas", []), 1):
            print(f"  {i}. {fortaleza}")
        print()
        
        print("🔧 ÁREAS DE MEJORA:")
        for i, area in enumerate(resultado.get("areas_mejora", []), 1):
            print(f"  {i}. {area}")
        print()
        
        print("💡 SUGERENCIAS ESPECÍFICAS:")
        for i, sug in enumerate(resultado.get("sugerencias", []), 1):
            print(f"\n  {i}. {sug.get('problema', '')}")
            print(f"     Solución: {sug.get('solucion', '')}")
            if sug.get('codigo_mejorado'):
                print(f"     Código mejorado:")
                print(f"     {sug.get('codigo_mejorado', '')}")
        print()
        
        print(f"📈 CALIFICACIÓN SUGERIDA: {resultado.get('calificacion', 0)}/5.0")
        print()
        
        # 7. Estadísticas de uso
        stats = service.get_estadisticas()
        print("="*80)
        print("ESTADÍSTICAS DE USO")
        print("="*80)
        print(f"Total requests: {stats.get('_request_count', 0)}")
        print(f"Total tokens: {stats.get('_token_count', 0)}")
        print(f"Total errores: {stats.get('_error_count', 0)}")
        print()
        
        print("✅ Test completado exitosamente!")
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando JSON: {e}")
        print(f"Respuesta raw: {texto_respuesta[:500]}")
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_simple())
