#!/usr/bin/env python3
"""
Diagnóstico rápido del problema de entrega de tareas.
Ejecutar desde backend: python ../diagnostic_entrega_issue.py
"""

import sys
import os

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 80)
print("🔍 DIAGNÓSTICO DE ENTREGA DE TAREAS")
print("=" * 80)

# 1. Verificar Pydantic schemas
print("\n1️⃣ Verificando schemas Pydantic...")
try:
    from src.schemas.academic.tarea_schemas import EntregaTareaResponse, EntregaTareaBase
    print(f"   ✅ EntregaTareaBase fields: {EntregaTareaBase.model_fields.keys()}")
    print(f"   ✅ EntregaTareaResponse fields: {EntregaTareaResponse.model_fields.keys()}")
    
    # Verificar que no hay duplicados en model_config
    base_config = getattr(EntregaTareaBase, 'model_config', None)
    resp_config = getattr(EntregaTareaResponse, 'model_config', None)
    print(f"   ✅ EntregaTareaBase.model_config: {base_config}")
    print(f"   ✅ EntregaTareaResponse.model_config: {resp_config}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# 2. Verificar si hay fields con max_length que causen slice error
print("\n2️⃣ Buscando campos con max_length potencialmente problemáticos...")
try:
    from pydantic import Field
    from typing import get_type_hints
    
    for field_name, field_info in EntregaTareaResponse.model_fields.items():
        if hasattr(field_info, 'metadata'):
            for meta in field_info.metadata or []:
                if hasattr(meta, 'max_length'):
                    field_type = field_info.annotation
                    print(f"   ⚠️  {field_name}: type={field_type}, max_length={meta.max_length}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Verificar entrega de prueba
print("\n3️⃣ Creando objeto EntregaTareaResponse de prueba...")
try:
    from datetime import datetime
    from enum import Enum
    from src.enums.academic import EstadoEntrega
    
    test_data = {
        "entrega_id": "550e8400-e29b-41d4-a716-446655440000",
        "tarea_id": "550e8400-e29b-41d4-a716-446655440001",
        "estudiante_id": "550e8400-e29b-41d4-a716-446655440002",
        "numero_intento": 1,
        "es_entrega_tardia": False,
        "estado": EstadoEntrega.ENTREGADA,
        "es_final": False,
        "requiere_revision": False,
        "fecha_creacion": datetime.now(),
        # Campos opcionales
        "archivos_adicionales": [{"url": "/uploads/file1.pdf", "nombre": "file1.pdf"}],
        "contenido_texto": "Test entrega",
    }
    
    # Intentar crear el modelo
    entrega_obj = EntregaTareaResponse(**test_data)
    print(f"   ✅ Objeto creado exitosamente")
    print(f"   ✅ Estado: {entrega_obj.estado}")
    print(f"   ✅ Archivos: {entrega_obj.archivos_adicionales}")
except Exception as e:
    print(f"   ❌ Error al crear objeto: {e}")
    import traceback
    traceback.print_exc()

# 4. Verificar conversión JSON
print("\n4️⃣ Probando conversión a JSON...")
try:
    import json
    
    # Crear un dict similar a lo que retorna la BD
    entrega_dict = {
        "entrega_id": "550e8400-e29b-41d4-a716-446655440000",
        "tarea_id": "550e8400-e29b-41d4-a716-446655440001",
        "estudiante_id": "550e8400-e29b-41d4-a716-446655440002",
        "numero_intento": 1,
        "es_entrega_tardia": False,
        "estado": "entregada",
        "es_final": False,
        "requiere_revision": False,
        "fecha_creacion": datetime.now().isoformat(),
        "archivos_adicionales": json.dumps({"archivos": [{"url": "/uploads/file1.pdf"}]}),
    }
    
    # Convertir a JSON
    json_str = json.dumps(entrega_dict, default=str)
    print(f"   ✅ JSON conversion OK")
    print(f"   ✅ JSON length: {len(json_str)}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ Diagnóstico completado")
print("=" * 80)
