import re
from sqlalchemy import create_engine, inspect
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
bd_cols = inspector.get_columns("inscripciones")

print("="*100)
print("📋 COMPARACIÓN: Inscripcion (Modelo vs BD)")
print("="*100)
print()

# Leer modelo
with open("src/models/academic/inscripcion.py", "r") as f:
    content = f.read()

model_cols = set(re.findall(r'(\w+)\s*=\s*Column\(', content))

bd_cols_names = set(col['name'] for col in bd_cols)
faltan = bd_cols_names - model_cols
sobran = model_cols - bd_cols_names

print(f"1️⃣ BD:     {len(bd_cols)} columnas")
print(f"2️⃣ Modelo: {len(model_cols)} columnas")
print()

if len(faltan) == 0 and len(sobran) == 0:
    print("✅ ¡PERFECTO! Inscripcion 100% sincronizado")
    print(f"Total: {len(bd_cols)} campos coinciden exactamente")
else:
    if faltan:
        print("="*100)
        print(f"❌ FALTAN EN MODELO: {len(faltan)} campos")
        print("="*100)
        print()
        for col in sorted(faltan):
            col_info = next((c for c in bd_cols if c['name'] == col), None)
            if col_info:
                tipo = str(col_info['type'])
                nullable = 'NULL' if col_info.get('nullable', True) else 'NOT NULL'
                print(f"   • {col:40s} {tipo:30s} {nullable}")
        print()
    
    if sobran:
        print("="*100)
        print(f"⚠️  SOBRAN EN MODELO: {len(sobran)} campos")
        print("="*100)
        print()
        print("   (Estos campos NO existen en BD, deben eliminarse)")
        print()
        for col in sorted(sobran):
            print(f"   • {col}")
        print()

print()
print("="*100)
print("📊 RESUMEN")
print("="*100)
if len(faltan) == 0 and len(sobran) == 0:
    print("✅ Modelo perfectamente sincronizado con BD")
else:
    print(f"⚠️  Requiere ajustes: {len(faltan)} faltan, {len(sobran)} sobran")
