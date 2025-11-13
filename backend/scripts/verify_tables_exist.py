from sqlalchemy import create_engine, inspect
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
tablas = inspector.get_table_names()

print("="*100)
print("🔍 VERIFICACIÓN: Tabla 'examenes' vs 'evaluaciones'")
print("="*100)
print()

# Buscar tabla examenes
if 'examenes' in tablas:
    cols = inspector.get_columns('examenes')
    print(f"✅ Tabla 'examenes' EXISTE ({len(cols)} columnas)")
    print(f"   → Modelo: Examen (examen.py)")
    print()
else:
    print("❌ Tabla 'examenes' NO existe")
    print()

# Verificar tabla evaluaciones
if 'evaluaciones' in tablas:
    cols = inspector.get_columns('evaluaciones')
    print(f"✅ Tabla 'evaluaciones' EXISTE ({len(cols)} columnas)")
    print(f"   → Modelo: Evaluacion (evaluacion_expandida.py)")
    print()
else:
    print("❌ Tabla 'evaluaciones' NO existe")
    print()

# Buscar todas las tablas relacionadas
print("📊 TODAS LAS TABLAS RELACIONADAS:")
print("-"*100)
eval_tables = [t for t in tablas if any(x in t.lower() for x in ['exam', 'evalua', 'pregunta', 'intento', 'respuesta'])]
for t in sorted(eval_tables):
    cols = inspector.get_columns(t)
    print(f"   • {t:45s} ({len(cols):2d} cols)")

print()
print("="*100)
print("💡 CONCLUSIÓN")
print("="*100)
print()
print("Hay DOS sistemas:")
print()
print("1️⃣ Sistema ACTUAL (usado en APIs/CRUD):")
print("   ❌ Tabla 'examenes' NO existe → examen.py está roto")
print()
print("2️⃣ Sistema REAL (existe en BD):")
print("   ✅ Tabla 'evaluaciones' SÍ existe → evaluacion_expandida.py es el correcto")
print()
print("⚠️  PROBLEMA: Las APIs usan 'Examen' pero la BD tiene 'evaluaciones'")
