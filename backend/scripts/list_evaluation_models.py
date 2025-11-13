import os
import re

evaluaciones_dir = "src/models/evaluaciones"
archivos = [f for f in os.listdir(evaluaciones_dir) 
            if f.endswith('.py') and f != '__init__.py' and 'backup' not in f.lower()]

print("="*100)
print("📁 ARCHIVOS DE MODELOS DE EVALUACIONES Y SUS CLASES")
print("="*100)
print()

archivos_clases = {}

for archivo in sorted(archivos):
    filepath = os.path.join(evaluaciones_dir, archivo)
    with open(filepath, 'r') as f:
        content = f.read()
    
    clases = re.findall(r'^class (\w+)\(Base\):', content, re.MULTILINE)
    archivos_clases[archivo] = clases
    
    print(f"📄 {archivo}")
    if clases:
        for clase in clases:
            print(f"   • {clase}")
    else:
        print(f"   ⚠️  Sin clases Base encontradas")
    print()

print("="*100)
print("📊 RESUMEN")
print("="*100)
print()

# Listar todas las clases únicas
todas_clases = []
for clases in archivos_clases.values():
    todas_clases.extend(clases)

print(f"Total archivos: {len(archivos)}")
print(f"Total clases:   {len(todas_clases)}")
print()

print("🔍 CLASES ENCONTRADAS:")
for i, clase in enumerate(sorted(set(todas_clases)), 1):
    print(f"   {i:2d}. {clase}")
