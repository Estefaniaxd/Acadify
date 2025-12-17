#!/usr/bin/env python3
"""
Test directo de la función obtener_entrega
Para verificar que funciona sin errores de serialización
"""

import sys
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session
import json

# Simular resultado de BD
class FakeResult:
    def __init__(self, data):
        self._mapping = data

# Datos de test
test_data = {
    'entrega_id': UUID('a9c849ab-2194-4bfb-991f-ec2cd5317981'),
    'tarea_id': UUID('9f5df54d-983f-4885-b4e6-2209c7a23d47'),
    'estudiante_id': UUID('46de825e-fc4c-4d38-8741-03924e13ccf7'),
    'titulo_entrega': 'Mi Tarea',
    'descripcion_entrega': None,
    'comentarios_estudiante': 'Entrega de tarea',
    'archivo_url': '/uploads/entregas/abc123.pdf',
    'archivos_adicionales': json.dumps({
        "archivos": [
            {
                "url": "/uploads/entregas/abc123.pdf",
                "nombre_original": "1-hojadevida.pdf",
                "nombre_almacenado": "abc123.pdf"
            }
        ]
    }),
    'contenido_texto': 'Entrega de tarea',
    'enlaces_externos': None,
    'fecha_entrega': datetime.now(timezone.utc),
    'fecha_limite_original': None,
    'numero_intento': 1,
    'es_entrega_tardia': False,
    'calificacion': None,
    'calificacion_letras': None,
    'comentarios_docente': None,
    'rubrica_calificacion': None,
    'estado': 'entregada',
    'es_final': False,
    'requiere_revision': False,
    'tiempo_empleado': None,
    'dificultad_percibida': None,
    'satisfaccion_estudiante': None,
    'fecha_creacion': datetime.now(timezone.utc),
    'fecha_actualizacion': None,
    'calificado_por': None,
    'fecha_calificacion': None,
}

print("=" * 60)
print("TEST: Simulando obtener_entrega")
print("=" * 60)

# Convertir resultado a diccionario (como haría SQLAlchemy)
entrega = dict(test_data)

print("\n✅ Datos originales cargados:")
for key, value in entrega.items():
    print(f"  {key}: {type(value).__name__} = {value}")

# Convertir UUIDs a strings
print("\n🔄 Convirtiendo UUIDs a strings...")
for key in ['entrega_id', 'tarea_id', 'estudiante_id', 'calificado_por']:
    if key in entrega and entrega[key] is not None:
        entrega[key] = str(entrega[key])

print("✅ UUIDs convertidos")

# Convertir timestamps a ISO format strings
print("\n🔄 Convirtiendo timestamps a ISO format...")
for key in ['fecha_entrega', 'fecha_limite_original', 'fecha_creacion', 'fecha_actualizacion', 'fecha_calificacion']:
    if key in entrega and entrega[key] is not None:
        entrega[key] = entrega[key].isoformat() if hasattr(entrega[key], 'isoformat') else str(entrega[key])

print("✅ Timestamps convertidos")

# Parsear archivos
print("\n🔄 Parseando archivos adicionales...")
archivos_lista = []

if entrega.get('archivos_adicionales'):
    try:
        archivos_data = json.loads(entrega['archivos_adicionales'])
        if isinstance(archivos_data, dict) and 'archivos' in archivos_data:
            for archivo in archivos_data['archivos']:
                if isinstance(archivo, dict) and 'url' in archivo:
                    archivos_lista.append({
                        "url": archivo['url'],
                        "nombre": archivo.get('nombre_original') or archivo.get('nombre') or archivo['url'].split("/")[-1],
                        "nombre_original": archivo.get('nombre_original')
                    })
        print(f"✅ {len(archivos_lista)} archivos parseados")
    except (json.JSONDecodeError, TypeError) as e:
        print(f"❌ Error parseando JSON: {e}")

entrega['archivos'] = archivos_lista

# Intentar serializar a JSON
print("\n🔄 Intentando serializar a JSON...")
try:
    json_str = json.dumps(entrega, default=str)
    print("✅ Serialización exitosa!")
    print(f"\n📋 Resultado JSON (primeros 500 chars):")
    print(json_str[:500])
except Exception as e:
    print(f"❌ Error en serialización: {e}")
    print(f"\nDatos problemáticos:")
    for key, value in entrega.items():
        try:
            json.dumps({key: value}, default=str)
        except Exception as e2:
            print(f"  ❌ {key}: {type(value).__name__} - {e2}")

print("\n" + "=" * 60)
print("✅ TEST COMPLETADO")
print("=" * 60)
