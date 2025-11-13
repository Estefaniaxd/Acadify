import re
from sqlalchemy import create_engine, inspect
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
bd_cols = inspector.get_columns("inscripciones")

print("="*100)
print("📋 ANÁLISIS DETALLADO: Inscripciones")
print("="*100)
print()

print(f"1️⃣ COLUMNAS EN BASE DE DATOS ({len(bd_cols)}):")
print("-"*100)

# Agrupar por categorías
print("\n🔑 IDENTIFICACIÓN Y RELACIONES:")
for col in bd_cols:
    if 'id' in col['name'] or col['name'] in ['tipo_inscripcion']:
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n📊 ESTADO Y CONTROL:")
for col in bd_cols:
    if 'estado' in col['name'] or 'activ' in col['name']:
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n📅 FECHAS Y TIEMPOS:")
for col in bd_cols:
    if 'fecha' in col['name'] or 'timestamp' in col['name'].lower() or col['name'] in ['created_at', 'updated_at']:
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n💰 INFORMACIÓN FINANCIERA:")
for col in bd_cols:
    if any(x in col['name'] for x in ['costo', 'descuento', 'pago', 'precio', 'valor', 'financ']):
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n📝 DOCUMENTACIÓN Y NOTAS:")
for col in bd_cols:
    if any(x in col['name'] for x in ['nota', 'observ', 'comentario', 'descripcion', 'motivo', 'justificacion']):
        tipo = str(col['type'])
        nullable = '?' if col.get('nullable', True) else '!'
        print(f"{nullable} {col['name']:40s} {tipo}")

print("\n🎯 OTROS CAMPOS:")
otros = []
categorias = ['id', 'estado', 'activ', 'fecha', 'timestamp', 'created', 'updated', 
              'costo', 'descuento', 'pago', 'precio', 'valor', 'financ',
              'nota', 'observ', 'comentario', 'descripcion', 'motivo', 'justificacion']
for col in bd_cols:
    if not any(x in col['name'] for x in categorias) and col['name'] not in ['tipo_inscripcion']:
        otros.append(col)

for col in otros:
    tipo = str(col['type'])
    nullable = '?' if col.get('nullable', True) else '!'
    print(f"{nullable} {col['name']:40s} {tipo}")

print()
print("="*100)
print(f"📊 TOTAL: {len(bd_cols)} columnas en Base de Datos")
print("="*100)
