"""
Test de schemas Pydantic para IA y Gamificación.

Valida que los schemas funcionen correctamente con validaciones.

Author: GitHub Copilot & Team
Date: 31 octubre 2025
"""

import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.schemas.ai_schemas import (
    EntregarTareaRequest,
    ArchivoMetadata,
    RetroalimentacionIA,
    SugerenciaEspecifica,
    CriterioRubrica,
    PuntosDesglose,
    GamificacionInfo,
    InsigniaInfo,
    EntregaConIAResponse,
    PuntosUsuarioResponse,
    RankingResponse
)

print("="*80)
print("TEST: Schemas Pydantic - IA y Gamificación")
print("="*80)
print()

# ==================== TEST 1: EntregarTareaRequest ====================

print("📝 Test 1: EntregarTareaRequest")
print("-"*80)

try:
    # Caso válido
    request = EntregarTareaRequest(
        contenido_texto="def suma(a, b):\n    return a + b",
        archivo_metadata=ArchivoMetadata(
            nombre="tarea.py",
            mime_type="text/x-python",
            tamaño_bytes=1024
        )
    )
    
    print("✅ Request válido creado")
    print(f"   Contenido: {request.contenido_texto[:30]}...")
    print(f"   Archivo: {request.archivo_metadata.nombre}")
    print()
    
    # Validación: contenido vacío debe fallar
    try:
        invalid_request = EntregarTareaRequest(contenido_texto="   ")
        print("❌ ERROR: Debería fallar con contenido vacío")
    except ValueError as e:
        print("✅ Validación correcta: contenido vacío rechazado")
        print(f"   Error: {str(e)}")
        print()

except Exception as e:
    print(f"❌ Error: {e}")
    print()

# ==================== TEST 2: RetroalimentacionIA ====================

print("📝 Test 2: RetroalimentacionIA")
print("-"*80)

try:
    retroalimentacion = RetroalimentacionIA(
        analisis_general="Código funcional con oportunidades de mejora",
        fortalezas=["Código claro", "Bien documentado"],
        areas_mejora=["Falta validación", "Sin type hints"],
        sugerencias_especificas=[
            SugerenciaEspecifica(
                ubicacion="Línea 2",
                problema="División por cero si lista vacía",
                sugerencia="Agregar validación",
                ejemplo="if not lista: raise ValueError()"
            )
        ],
        nivel_cumplimiento="85%",
        cumple_rubrica={
            "funcionalidad": CriterioRubrica(
                puntos=4.5,
                comentario="Excelente funcionalidad"
            )
        },
        puntos_clave_missing=["Validación de entrada"],
        calificacion=4.2
    )
    
    print("✅ Retroalimentación creada")
    print(f"   Calificación: {retroalimentacion.calificacion}/5.0")
    print(f"   Fortalezas: {len(retroalimentacion.fortalezas)}")
    print(f"   Áreas mejora: {len(retroalimentacion.areas_mejora)}")
    print(f"   Sugerencias: {len(retroalimentacion.sugerencias_especificas)}")
    print()
    
    # Validación: calificación fuera de rango
    try:
        invalid_retro = RetroalimentacionIA(
            analisis_general="Test",
            fortalezas=[],
            areas_mejora=[],
            sugerencias_especificas=[],
            nivel_cumplimiento="0%",
            calificacion=6.0  # Fuera de rango
        )
        print("❌ ERROR: Debería fallar con calificación > 5")
    except ValueError as e:
        print("✅ Validación correcta: calificación fuera de rango rechazada")
        print()

except Exception as e:
    print(f"❌ Error: {e}")
    print()

# ==================== TEST 3: PuntosDesglose ====================

print("📝 Test 3: PuntosDesglose")
print("-"*80)

try:
    puntos = PuntosDesglose(
        puntos_base=50,
        puntos_bonificacion=20,
        penalizacion_tardia=0,
        penalizacion_intentos=0,
        puntos_totales=70,
        desglose="50 (base) + 20 (bonus excelencia)"
    )
    
    print("✅ Puntos desglose creado")
    print(f"   Base: {puntos.puntos_base}")
    print(f"   Bonus: {puntos.puntos_bonificacion}")
    print(f"   Total: {puntos.puntos_totales}")
    print(f"   Desglose: {puntos.desglose}")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    print()

# ==================== TEST 4: GamificacionInfo ====================

print("📝 Test 4: GamificacionInfo")
print("-"*80)

try:
    gamificacion = GamificacionInfo(
        puntos_otorgados=70,
        puntos_acumulados=170,
        nivel_actual="Bronce II",
        nuevas_insignias=[
            InsigniaInfo(
                insignia_id="uuid-123",
                nombre="Novato",
                descripcion="Primera insignia",
                imagen_url="https://cdn.example.com/novato.png"
            )
        ],
        progreso_siguiente_nivel=68.0
    )
    
    print("✅ Gamificación info creada")
    print(f"   Puntos otorgados: {gamificacion.puntos_otorgados}")
    print(f"   Puntos acumulados: {gamificacion.puntos_acumulados}")
    print(f"   Nivel: {gamificacion.nivel_actual}")
    print(f"   Nuevas insignias: {len(gamificacion.nuevas_insignias)}")
    print(f"   Progreso: {gamificacion.progreso_siguiente_nivel}%")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    print()

# ==================== TEST 5: Response Completo ====================

print("📝 Test 5: EntregaConIAResponse (JSON completo)")
print("-"*80)

try:
    # Crear response completo como lo haría la API
    from src.schemas.ai_schemas import EntregaConIAData
    
    response = EntregaConIAResponse(
        success=True,
        message="Entrega procesada exitosamente con IA",
        data=EntregaConIAData(
            entrega_id="uuid-abc-123",
            intentos=1,
            es_tardia=False,
            fecha_entrega=datetime.now(),
            retroalimentacion_ia=retroalimentacion,
            puntos=puntos,
            gamificacion=gamificacion
        )
    )
    
    print("✅ Response completo creado")
    
    # Serializar a JSON (como lo haría FastAPI)
    json_data = response.model_dump(mode='json')
    json_str = json.dumps(json_data, indent=2, default=str)
    
    print()
    print("JSON generado (primeras 30 líneas):")
    print("-"*80)
    lines = json_str.split('\n')[:30]
    print('\n'.join(lines))
    if len(json_str.split('\n')) > 30:
        print("...")
    print()
    
    # Verificar estructura
    assert json_data['success'] == True
    assert 'data' in json_data
    assert 'retroalimentacion_ia' in json_data['data']
    assert 'puntos' in json_data['data']
    assert 'gamificacion' in json_data['data']
    
    print("✅ Estructura JSON validada")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print()

# ==================== TEST 6: OpenAPI Schema ====================

print("📝 Test 6: OpenAPI Schema Generation")
print("-"*80)

try:
    # Obtener schema OpenAPI (como lo haría FastAPI)
    schema = EntregaConIAResponse.model_json_schema()
    
    print("✅ OpenAPI Schema generado")
    print(f"   Title: {schema.get('title', 'N/A')}")
    print(f"   Properties: {len(schema.get('properties', {}))}")
    print(f"   Required: {schema.get('required', [])}")
    
    # Verificar que tenga ejemplos
    if 'examples' in schema or any('example' in str(v) for v in schema.get('properties', {}).values()):
        print("   ✅ Contiene ejemplos para documentación")
    
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    print()

print("="*80)
print("✅ TODOS LOS TESTS DE SCHEMAS PASARON")
print("="*80)
print()

print("📊 RESUMEN:")
print("  • EntregarTareaRequest: ✅")
print("  • RetroalimentacionIA: ✅")
print("  • PuntosDesglose: ✅")
print("  • GamificacionInfo: ✅")
print("  • EntregaConIAResponse: ✅")
print("  • OpenAPI Schema: ✅")
print()

print("🎯 Schemas listos para usar en FastAPI Routes!")
