import re
from sqlalchemy import create_engine, inspect
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
bd_cols = inspector.get_columns("videollamada_grabaciones")

print("="*100)
print("📋 ANÁLISIS: VideollamadaGrabacion")
print("="*100)
print()

print(f"1️⃣ BD: {len(bd_cols)} columnas")
print("-"*100)
for col in sorted(bd_cols, key=lambda x: x["name"]):
    tipo = str(col["type"])
    nullable = "?" if col.get("nullable", True) else "!"
    print(f"{nullable} {col['name']:40s} {tipo}")
print()

with open("src/models/communication/videollamada.py", "r") as f:
    content = f.read()

clases = re.findall(r"class (\w+)\(Base\):", content)
print(f"2️⃣ CLASES EN ARCHIVO: {len(clases)}")
for clase in clases:
    print(f"   • {clase}")
print()

pattern = r"class VideollamadaGrabacion\(Base\):.*?(?=class \w+\(Base\):|$)"
match = re.search(pattern, content, re.DOTALL)

if match:
    grabacion_content = match.group(0)
    model_cols = set(re.findall(r"(\w+)\s*=\s*Column\(", grabacion_content))
    
    print(f"3️⃣ MODELO: {len(model_cols)} columnas")
    print("-"*100)
    for col in sorted(model_cols):
        print(f"   • {col}")
    print()
    
    bd_cols_names = set(col["name"] for col in bd_cols)
    faltan = bd_cols_names - model_cols
    sobran = model_cols - bd_cols_names
    
    print("="*100)
    print("📊 COMPARACIÓN")
    print("="*100)
    print()
    
    if len(faltan) == 0 and len(sobran) == 0:
        print("✅ PERFECTO! Sincronizado 100%")
        print(f"Total: {len(bd_cols)} campos coinciden")
    else:
        if faltan:
            print(f"❌ FALTAN: {len(faltan)} campos")
            print()
            for col in sorted(faltan):
                col_info = next((c for c in bd_cols if c["name"] == col), None)
                if col_info:
                    tipo = str(col_info["type"])
                    nullable = "NULL" if col_info.get("nullable", True) else "NOT NULL"
                    print(f"   • {col:40s} {tipo:30s} {nullable}")
            print()
        
        if sobran:
            print(f"⚠️  SOBRAN: {len(sobran)} campos (NO existen en BD)")
            print()
            for col in sorted(sobran):
                print(f"   • {col}")
            print()
else:
    print("❌ No se encontró VideollamadaGrabacion")
