#!/usr/bin/env python3
"""Diagnóstico: Verificar por qué el script no detecta columnas del modelo Clase"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib
import pkgutil
from src.db.base_class import Base

# Método 1: Importación directa
print("="*70)
print("MÉTODO 1: Importación directa")
print("="*70)
from src.models.academic.clase import Clase as ClaseDirecta

print(f"Modelo: {ClaseDirecta.__name__}")
print(f"Tabla: {ClaseDirecta.__tablename__}")
print(f"Columnas vía __table__.columns: {len(ClaseDirecta.__table__.columns)}")
for col in ClaseDirecta.__table__.columns:
    print(f"  - {col.name}")

# Método 2: Descubrimiento dinámico (como lo hace el script)
print("\n" + "="*70)
print("MÉTODO 2: Descubrimiento dinámico (script)")
print("="*70)

models_path = Path("src/models")
models = {}

for module_info in pkgutil.walk_packages([str(models_path)], prefix="src.models."):
    try:
        module = importlib.import_module(module_info.name)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Base) and 
                attr is not Base and
                hasattr(attr, '__tablename__')):
                table_name = attr.__tablename__
                if table_name == "Clase":
                    print(f"✅ Encontrado: {module_info.name}.{attr_name}")
                    print(f"   Tabla: {table_name}")
                    print(f"   Columnas: {len(attr.__table__.columns)}")
                    cols = [col.name for col in attr.__table__.columns]
                    print(f"   Lista: {sorted(cols)}")
                    models[table_name] = attr
    except Exception as e:
        print(f"⚠️  Error importando {module_info.name}: {e}")

if "Clase" not in models:
    print("❌ ERROR: No se pudo descubrir el modelo Clase dinámicamente")
else:
    print(f"\n✅ Modelo Clase descubierto correctamente con {len(models['Clase'].__table__.columns)} columnas")
