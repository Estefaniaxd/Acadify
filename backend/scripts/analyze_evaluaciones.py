import re
from sqlalchemy import create_engine, inspect
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
bd_cols = inspector.get_columns("evaluaciones")

print("="*100)
print("📋 ANÁLISIS DETALLADO: Evaluaciones")
print("="*100)
print()

print(f"1️⃣ COLUMNAS EN BASE DE DATOS ({len(bd_cols)}):")
print("-"*100)

# Agrupar por categorías
print("\n🔑 IDENTIFICACIÓN:")
for col in bd_cols:
    if 'id' in col['name']:
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n⚙️ CONFIGURACIÓN GENERAL:")
for col in bd_cols:
    if any(x in col['name'] for x in ['tipo', 'modo', 'estado', 'titulo', 'descripcion', 'instrucciones', 'peso']):
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n⏱️ TIEMPO Y FECHAS:")
for col in bd_cols:
    if any(x in col['name'] for x in ['fecha', 'hora', 'duracion', 'tiempo', 'timestamp', 'created', 'updated']):
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n📊 PUNTUACIÓN Y CALIFICACIÓN:")
for col in bd_cols:
    if any(x in col['name'] for x in ['punto', 'puntuacion', 'calificacion', 'nota', 'puntaje']):
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n🎯 CONFIGURACIÓN DE PREGUNTAS:")
for col in bd_cols:
    if 'pregunta' in col['name']:
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n🔒 ANTITRAMPA Y SEGURIDAD:")
for col in bd_cols:
    if any(x in col['name'] for x in ['antitrampa', 'bloqueo', 'permitir', 'requiere', 'prevenir', 'detectar']):
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n✅ INTENTOS Y LÍMITES:")
for col in bd_cols:
    if any(x in col['name'] for x in ['intento', 'maximo', 'minimo', 'limite']):
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n🎨 UI Y EXPERIENCIA:")
for col in bd_cols:
    if any(x in col['name'] for x in ['mostrar', 'visible', 'ocultar', 'navegacion']):
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n📤 RESULTADOS Y RETROALIMENTACIÓN:")
for col in bd_cols:
    if any(x in col['name'] for x in ['resultado', 'feedback', 'retroalimentacion', 'respuesta']):
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n📁 OTROS:")
otros_keys = ['id', 'tipo', 'modo', 'estado', 'titulo', 'descripcion', 'instrucciones', 'peso',
              'fecha', 'hora', 'duracion', 'tiempo', 'timestamp', 'created', 'updated',
              'punto', 'puntuacion', 'calificacion', 'nota', 'puntaje', 'pregunta',
              'antitrampa', 'bloqueo', 'permitir', 'requiere', 'prevenir', 'detectar',
              'intento', 'maximo', 'minimo', 'limite', 'mostrar', 'visible', 'ocultar', 'navegacion',
              'resultado', 'feedback', 'retroalimentacion', 'respuesta']

otros = [col for col in bd_cols if not any(k in col['name'] for k in otros_keys)]
for col in otros:
    tipo = str(col['type'])
    nullable = '?' if col.get('nullable', True) else '!'
    print(f"{nullable} {col['name']:40s} {tipo}")

print()
print("="*100)
print(f"📊 TOTAL: {len(bd_cols)} columnas en Base de Datos")
print("="*100)
