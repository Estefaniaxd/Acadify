"""
Script de verificación completa del sistema de evaluaciones.
Verifica qué sistema está activo y funcionando.
"""
from sqlalchemy import create_engine, inspect, text
from src.core.config import settings
import os

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

print("="*100)
print("🔍 VERIFICACIÓN COMPLETA: Sistema de Evaluaciones")
print("="*100)
print()

# ==================== PARTE 1: VERIFICAR TABLAS EN BD ====================
print("📊 PARTE 1: TABLAS EN BASE DE DATOS")
print("-"*100)
print()

tablas_esperadas = [
    'examenes',       # Sistema examen.py
    'evaluaciones',   # Sistema evaluacion_expandida.py
    'preguntas_evaluacion',
    'intentos_evaluacion',
    'respuestas_estudiante',
    'banco_preguntas',
    'configuracion_evaluaciones',
    'estadisticas_examen'
]

tablas_existentes = inspector.get_table_names()

for tabla in tablas_esperadas:
    if tabla in tablas_existentes:
        cols = inspector.get_columns(tabla)
        print(f"✅ {tabla:40s} EXISTE ({len(cols):2d} columnas)")
    else:
        print(f"❌ {tabla:40s} NO EXISTE")

print()

# ==================== PARTE 2: VERIFICAR DATOS EN TABLAS ====================
print("="*100)
print("📈 PARTE 2: DATOS EN TABLAS (¿Hay registros?)")
print("-"*100)
print()

with engine.connect() as conn:
    for tabla in tablas_esperadas:
        if tabla in tablas_existentes:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                count = result.scalar()
                if count > 0:
                    print(f"✅ {tabla:40s} {count:5d} registros 📦")
                else:
                    print(f"⚪ {tabla:40s} {count:5d} registros (vacía)")
            except Exception as e:
                print(f"❌ {tabla:40s} ERROR: {str(e)[:50]}")

print()

# ==================== PARTE 3: VERIFICAR IMPORTS EN CÓDIGO ====================
print("="*100)
print("🔍 PARTE 3: ¿QUÉ MODELOS USAN LAS APIs?")
print("-"*100)
print()

# Buscar imports en archivos de rutas
import re

def buscar_imports(directorio, patron):
    """Busca imports en archivos Python"""
    resultados = []
    for root, dirs, files in os.walk(directorio):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        matches = re.findall(patron, content)
                        if matches:
                            resultados.append((filepath, matches))
                except:
                    pass
    return resultados

print("🔎 Buscando imports de 'Examen' (examen.py):")
examen_imports = buscar_imports('src/api/routes', r'from.*models.*import.*Examen|import.*Examen')
if examen_imports:
    for filepath, matches in examen_imports[:5]:
        print(f"   • {filepath}")
else:
    print("   ❌ No encontrado")
print()

print("🔎 Buscando imports de 'Evaluacion' (evaluacion_expandida.py):")
evaluacion_imports = buscar_imports('src/api/routes', r'from.*models.*import.*Evaluacion|import.*Evaluacion')
if evaluacion_imports:
    for filepath, matches in evaluacion_imports[:5]:
        print(f"   • {filepath}")
else:
    print("   ❌ No encontrado")
print()

# ==================== PARTE 4: VERIFICAR CRUD ====================
print("="*100)
print("🔍 PARTE 4: ¿QUÉ MODELOS USAN LOS CRUD?")
print("-"*100)
print()

crud_files = [
    'src/crud/evaluaciones/crud_examen.py',
    'src/crud/evaluaciones/crud_pregunta.py',
    'src/crud/evaluaciones/crud_intento.py',
    'src/crud/evaluaciones/crud_respuesta.py'
]

for crud_file in crud_files:
    if os.path.exists(crud_file):
        print(f"📄 {os.path.basename(crud_file)}:")
        with open(crud_file, 'r') as f:
            content = f.read()
            # Buscar imports de modelos
            imports_examen = re.findall(r'from.*models.*examen.*import', content, re.IGNORECASE)
            imports_evaluacion = re.findall(r'from.*models.*evaluacion.*import', content, re.IGNORECASE)
            
            if imports_examen:
                print(f"   ✅ Usa sistema 'examen.py'")
                print(f"      {imports_examen[0][:70]}...")
            elif imports_evaluacion:
                print(f"   ✅ Usa sistema 'evaluacion_expandida.py'")
                print(f"      {imports_evaluacion[0][:70]}...")
            else:
                print(f"   ⚪ No detectado")
        print()

# ==================== PARTE 5: CONCLUSIÓN ====================
print("="*100)
print("📋 CONCLUSIÓN")
print("="*100)
print()

if 'examenes' not in tablas_existentes and 'evaluaciones' in tablas_existentes:
    print("🎯 SISTEMA ACTIVO: evaluacion_expandida.py")
    print()
    print("Evidencia:")
    print("   ✅ Tabla 'evaluaciones' SÍ existe en BD")
    print("   ❌ Tabla 'examenes' NO existe en BD")
    print()
    if examen_imports:
        print("   ⚠️  PROBLEMA: Las APIs importan 'Examen' pero la tabla no existe")
        print("   📝 ACCIÓN: Actualizar APIs para usar 'Evaluacion' o crear alias")
    else:
        print("   ✅ Las APIs no usan 'Examen' directamente")
    print()
    print("💡 DECISIÓN: Sincronizar 'Evaluacion' de evaluacion_expandida.py con BD")
    
elif 'examenes' in tablas_existentes and 'evaluaciones' not in tablas_existentes:
    print("🎯 SISTEMA ACTIVO: examen.py")
    print()
    print("Evidencia:")
    print("   ✅ Tabla 'examenes' SÍ existe en BD")
    print("   ❌ Tabla 'evaluaciones' NO existe en BD")
    print()
    print("💡 DECISIÓN: Sincronizar 'Examen' de examen.py con BD")
    
elif 'examenes' in tablas_existentes and 'evaluaciones' in tablas_existentes:
    print("⚠️  AMBOS SISTEMAS COEXISTEN")
    print()
    print("   ✅ Tabla 'examenes' existe")
    print("   ✅ Tabla 'evaluaciones' existe")
    print()
    print("💡 DECISIÓN: Verificar cuál tiene más datos y cuál usan las APIs")
    
else:
    print("❌ NINGÚN SISTEMA EXISTE EN BD")
    print()
    print("   Ni 'examenes' ni 'evaluaciones' existen en la base de datos")
