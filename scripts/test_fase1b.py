#!/usr/bin/env python3
"""
Quick validation script para Phase 1B - Gamification

Verifica:
1. Imports correctos
2. Método existe en CRUD
3. Endpoint está disponible
4. Sin errores de sintaxis

Uso:
    cd backend
    python test_fase1b.py
"""

import sys
from pathlib import Path

# Agregar backend al path
backend_path = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

print("=" * 70)
print("🧪 FASE 1B - VALIDATION TEST")
print("=" * 70)

# Test 1: Imports en CRUD
print("\n✓ Test 1: Imports en CRUD...")
try:
    from src.crud.academic.tarea import crud_entrega_tarea, CRUDTarea
    print("  ✅ CRUD imports OK")
except Exception as e:
    print(f"  ❌ Error en CRUD imports: {e}")
    sys.exit(1)

# Test 2: Método existe
print("\n✓ Test 2: Método calificar_entrega_con_puntos existe...")
if hasattr(crud_entrega_tarea, "calificar_entrega_con_puntos"):
    print("  ✅ Método encontrado en CRUD")
else:
    print("  ❌ Método NO encontrado en CRUD")
    sys.exit(1)

# Test 3: Imports en Route
print("\n✓ Test 3: Imports en Route...")
try:
    from src.api.routes.academic.tareas import router
    print("  ✅ Route imports OK")
except Exception as e:
    print(f"  ❌ Error en Route imports: {e}")
    sys.exit(1)

# Test 4: Endpoint registrado
print("\n✓ Test 4: Endpoint /entregas/{entrega_id}/calificar registrado...")
endpoints = [r.path for r in router.routes]
calificar_path = "/entregas/{entrega_id}/calificar"
if any(calificar_path in path for path in endpoints):
    print(f"  ✅ Endpoint encontrado: {calificar_path}")
else:
    print(f"  ❌ Endpoint NO encontrado: {calificar_path}")
    print(f"  Endpoints disponibles: {endpoints[:5]}...")
    sys.exit(1)

# Test 5: Verificar signature del método
print("\n✓ Test 5: Signature del método calificar_entrega_con_puntos...")
import inspect
sig = inspect.signature(crud_entrega_tarea.calificar_entrega_con_puntos)
params = list(sig.parameters.keys())
required_params = ["db", "entrega_id", "calificacion_data", "calificado_por"]
if all(p in params for p in required_params):
    print(f"  ✅ Parámetros OK: {params}")
else:
    print(f"  ❌ Parámetros inválidos: {params}")
    print(f"     Esperados: {required_params}")
    sys.exit(1)

# Test 6: Verificar docstring
print("\n✓ Test 6: Docstring del método...")
if crud_entrega_tarea.calificar_entrega_con_puntos.__doc__:
    doc_preview = crud_entrega_tarea.calificar_entrega_con_puntos.__doc__[:100]
    print(f"  ✅ Docstring present: {doc_preview}...")
else:
    print("  ⚠️  Sin docstring (pero no es error crítico)")

print("\n" + "=" * 70)
print("✅ ALL VALIDATION TESTS PASSED")
print("=" * 70)
print("\n📝 Próximos pasos:")
print("  1. pytest tests/api/test_tareas.py -v")
print("  2. Probar endpoints manualmente")
print("  3. Verificar BD después de calificar")
print("=" * 70)
