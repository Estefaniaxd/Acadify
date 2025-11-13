#!/usr/bin/env python3#!/usr/bin/env python3

import reimport re

from sqlalchemy import create_engine, inspectfrom sqlalchemy import create_engine, inspect

from src.core.config import settingsfrom src.core.config import settings



# Conectar a BD# Conectar a BD

engine = create_engine(settings.DATABASE_URL)engine = create_engine(settings.DATABASE_URL)

inspector = inspect(engine)inspector = inspect(engine)



# Obtener columnas de BD# Obtener columnas de BD

bd_cols = {col["name"] for col in inspector.get_columns("tareas")}bd_cols = {col["name"] for col in inspector.get_columns("tareas")}



# Leer modelo y extraer columnas# Leer modelo y extraer columnas

with open("src/models/academic/tarea.py", "r") as f:with open("src/models/academic/tarea.py", "r") as f:

    content = f.read()    content = f.read()

        

# Encontrar columnas definidas en el modelo# Encontrar columnas definidas en el modelo

pattern = r"(\w+)\s*=\s*Column\("pattern = r"(\w+)\s*=\s*Column\("

model_cols = set(re.findall(pattern, content))model_cols = set(re.findall(pattern, content))



print(f"📋 Campos en BD: {len(bd_cols)}")print(f"📋 Campos en BD: {len(bd_cols)}")

print(f"📋 Campos en Modelo: {len(model_cols)}")print(f"�� Campos en Modelo: {len(model_cols)}")

print(f"\n⚠️  Campos que FALTAN en el modelo:")print(f"

⚠️  Campos que FALTAN en el modelo:")

faltan = bd_cols - model_cols

for col in sorted(faltan):faltan = bd_cols - model_cols

    print(f"   - {col}")for col in sorted(faltan):

    print(f"   - {col}")

print(f"\n✅ Campos que SOBRAN en el modelo (no están en BD):")

sobran = model_cols - bd_colsprint(f"

for col in sorted(sobran):✅ Campos que SOBRAN en el modelo (no están en BD):")

    print(f"   - {col}")sobran = model_cols - bd_cols

for col in sorted(sobran):

print(f"\n📊 Resumen:")    print(f"   - {col}")

print(f"   Total coincidencias: {len(bd_cols & model_cols)}")
print(f"   Faltan en modelo: {len(faltan)}")
print(f"   Sobran en modelo: {len(sobran)}")
