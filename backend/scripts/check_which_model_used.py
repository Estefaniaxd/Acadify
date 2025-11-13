import re
from sqlalchemy import create_engine, inspect
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

print("="*100)
print("🔍 VERIFICACIÓN: ¿Qué modelo se usa para 'evaluaciones'?")
print("="*100)
print()

# Leer examen.py
with open("src/models/evaluaciones/examen.py", "r") as f:
    examen_content = f.read()

# Buscar __tablename__ en clase Examen
match_examen = re.search(r'class Examen\(Base\):.*?__tablename__\s*=\s*["\'](\w+)["\']', examen_content, re.DOTALL)
if match_examen:
    tablename_examen = match_examen.group(1)
    print(f"📄 examen.py → clase Examen")
    print(f"   __tablename__ = '{tablename_examen}'")
    print()

# Leer evaluacion_expandida.py
with open("src/models/evaluaciones/evaluacion_expandida.py", "r") as f:
    evaluacion_content = f.read()

# Buscar __tablename__ en clase Evaluacion
match_evaluacion = re.search(r'class Evaluacion\(Base\):.*?__tablename__\s*=\s*["\'](\w+)["\']', evaluacion_content, re.DOTALL)
if match_evaluacion:
    tablename_evaluacion = match_evaluacion.group(1)
    print(f"📄 evaluacion_expandida.py → clase Evaluacion")
    print(f"   __tablename__ = '{tablename_evaluacion}'")
    print()

print("="*100)
print("📊 CONCLUSIÓN")
print("="*100)
print()

if match_examen and match_evaluacion:
    if tablename_examen == tablename_evaluacion:
        print(f"⚠️  CONFLICTO: Ambas clases apuntan a la misma tabla '{tablename_examen}'")
        print()
        print("Las APIs usan:")
        print("   ✅ src.models.evaluaciones.Examen (en CRUD)")
        print("   ❌ src.models.evaluaciones.Evaluacion (NO usado en CRUD)")
        print()
        print("💡 DECISIÓN:")
        print(f"   • Usar 'Examen' de examen.py como modelo principal")
        print(f"   • Verificar sincronización de 'Examen' con BD")
        print(f"   • evaluacion_expandida.py puede ser sistema futuro/alternativo")
    else:
        print(f"✅ No hay conflicto: Apuntan a tablas diferentes")
        print(f"   • Examen → {tablename_examen}")
        print(f"   • Evaluacion → {tablename_evaluacion}")
