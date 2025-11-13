"""
📊 ANÁLISIS COMPREHENSIVO DE TODOS LOS MODELOS vs BASE DE DATOS

Este script hace un análisis detallado modelo por modelo para determinar:
1. Modelos perfectamente sincronizados ✅
2. Modelos con campos faltantes en BD ❌ 
3. Modelos con campos extras en BD ⚠️
4. Modelos con múltiples clases en el mismo archivo 📁
5. Recomendaciones de acción para cada caso

Objetivo: Entender la situación completa para NO romper funcionalidades.
"""

import re
import os
from pathlib import Path
from sqlalchemy import create_engine, inspect
from src.core.config import settings
from collections import defaultdict

def get_bd_tables():
    """Obtener todas las tablas de la BD"""
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_bd_columns(table_name):
    """Obtener columnas de una tabla de BD"""
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    return set(col['name'] for col in inspector.get_columns(table_name))

def find_model_file(table_name):
    """Buscar el archivo del modelo para una tabla"""
    # Conversiones comunes
    possible_names = [
        table_name,  # inscripciones
        table_name.rstrip('s'),  # inscripcione
        table_name.rstrip('es'),  # inscripcion
        table_name + '.py',
        table_name[:-1] + '.py' if table_name.endswith('s') else table_name + '.py',
    ]
    
    models_dir = Path('/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/src/models')
    
    # Buscar en todos los subdirectorios
    for root, dirs, files in os.walk(models_dir):
        for file in files:
            if not file.endswith('.py') or file == '__init__.py':
                continue
            
            file_path = Path(root) / file
            
            # Verificar si el archivo contiene la tabla
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if f'__tablename__ = "{table_name}"' in content or f"__tablename__ = '{table_name}'" in content:
                        return file_path, content
            except Exception:
                continue
    
    return None, None

def extract_columns_from_class(content, class_name):
    """Extraer columnas de una clase específica en el archivo"""
    # Encontrar la clase
    class_pattern = rf'class {class_name}\([^)]+\):'
    class_match = re.search(class_pattern, content)
    
    if not class_match:
        return set()
    
    class_start = class_match.start()
    
    # Encontrar el final de la clase (siguiente clase o fin de archivo)
    next_class = re.search(r'\nclass \w+\([^)]+\):', content[class_start + 1:])
    if next_class:
        class_end = class_start + next_class.start()
    else:
        class_end = len(content)
    
    class_content = content[class_start:class_end]
    
    # Extraer columnas
    columns = set(re.findall(r'(\w+)\s*=\s*Column\(', class_content))
    
    return columns

def count_classes_in_file(content):
    """Contar cuántas clases SQLAlchemy hay en el archivo"""
    pattern = r'class (\w+)\(Base\):'
    return re.findall(pattern, content)

def get_class_for_table(content, table_name):
    """Encontrar el nombre de la clase que corresponde a la tabla"""
    # Buscar __tablename__ = "table_name"
    pattern = rf'class (\w+)\([^)]+\):.*?__tablename__\s*=\s*["\']({table_name})["\']'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    return None

def analyze_all_models():
    """Análisis completo de todos los modelos"""
    print('=' * 100)
    print('📊 ANÁLISIS COMPREHENSIVO: TODOS LOS MODELOS vs BASE DE DATOS')
    print('=' * 100)
    print()
    
    bd_tables = get_bd_tables()
    
    print(f'Total tablas en BD: {len(bd_tables)}')
    print()
    
    # Categorías de análisis
    perfectos = []  # ✅ Sincronizados perfectamente
    faltan_en_bd = []  # ❌ Campos en modelo pero NO en BD
    sobran_en_bd = []  # ⚠️ Campos en BD pero NO en modelo
    multi_clase = []  # 📁 Archivos con múltiples clases
    sin_modelo = []  # 🚫 Tablas sin modelo
    
    for table in sorted(bd_tables):
        bd_cols = get_bd_columns(table)
        model_file, content = find_model_file(table)
        
        if not model_file:
            sin_modelo.append((table, len(bd_cols)))
            continue
        
        # Contar clases en el archivo
        classes = count_classes_in_file(content)
        
        if len(classes) > 1:
            # Archivo multi-clase
            class_name = get_class_for_table(content, table)
            if class_name:
                model_cols = extract_columns_from_class(content, class_name)
            else:
                # No se pudo determinar la clase, usar todas las columnas del archivo
                model_cols = set(re.findall(r'(\w+)\s*=\s*Column\(', content))
            
            multi_clase.append({
                'tabla': table,
                'archivo': model_file.name,
                'clases': classes,
                'clase_principal': class_name,
                'bd_cols': len(bd_cols),
                'model_cols': len(model_cols),
                'faltan': len(model_cols - bd_cols),
                'sobran': len(bd_cols - model_cols),
            })
        else:
            # Archivo con una sola clase
            model_cols = set(re.findall(r'(\w+)\s*=\s*Column\(', content))
        
        faltan = model_cols - bd_cols
        sobran = bd_cols - model_cols
        
        if len(faltan) == 0 and len(sobran) == 0:
            perfectos.append((table, len(bd_cols)))
        elif len(faltan) > 0 and len(sobran) == 0:
            faltan_en_bd.append({
                'tabla': table,
                'archivo': model_file.name,
                'bd_cols': len(bd_cols),
                'model_cols': len(model_cols),
                'faltan_bd': len(faltan),
                'faltan_lista': sorted(faltan)[:10],  # Primeros 10
            })
        elif len(faltan) == 0 and len(sobran) > 0:
            sobran_en_bd.append({
                'tabla': table,
                'archivo': model_file.name,
                'bd_cols': len(bd_cols),
                'model_cols': len(model_cols),
                'sobran_bd': len(sobran),
                'sobran_lista': sorted(sobran)[:10],
            })
        elif len(faltan) > 0 and len(sobran) > 0:
            # Ambos problemas
            faltan_en_bd.append({
                'tabla': table,
                'archivo': model_file.name,
                'bd_cols': len(bd_cols),
                'model_cols': len(model_cols),
                'faltan_bd': len(faltan),
                'sobran_bd': len(sobran),
                'faltan_lista': sorted(faltan)[:10],
                'sobran_lista': sorted(sobran)[:10],
            })
    
    # ============================================================================
    # REPORTE
    # ============================================================================
    
    print('=' * 100)
    print('✅ MODELOS PERFECTAMENTE SINCRONIZADOS')
    print('=' * 100)
    print(f'Total: {len(perfectos)} modelos')
    print()
    for tabla, cols in perfectos:
        print(f'  ✅ {tabla:40s} {cols:3d} columnas')
    
    print()
    print('=' * 100)
    print('📁 ARCHIVOS CON MÚLTIPLES CLASES (NORMAL)')
    print('=' * 100)
    print(f'Total: {len(multi_clase)} archivos')
    print()
    for m in multi_clase:
        print(f"  📁 {m['tabla']:40s} archivo: {m['archivo']}")
        print(f"     Clases: {', '.join(m['clases'])}")
        if m['clase_principal']:
            print(f"     Clase principal: {m['clase_principal']}")
        print(f"     BD: {m['bd_cols']} cols | Modelo: {m['model_cols']} cols | Faltan: {m['faltan']} | Sobran: {m['sobran']}")
        print()
    
    print('=' * 100)
    print('❌ MODELOS CON CAMPOS FALTANTES EN BD (Requieren Atención)')
    print('=' * 100)
    print(f'Total: {len(faltan_en_bd)} modelos')
    print()
    for m in faltan_en_bd:
        print(f"  ❌ {m['tabla']:40s} archivo: {m['archivo']}")
        print(f"     BD: {m['bd_cols']} cols | Modelo: {m['model_cols']} cols")
        if m['faltan_bd'] > 0:
            print(f"     ⚠️  Faltan en BD: {m['faltan_bd']} campos")
            if 'faltan_lista' in m:
                print(f"     Ejemplos: {', '.join(m['faltan_lista'][:5])}")
        if 'sobran_bd' in m and m['sobran_bd'] > 0:
            print(f"     ⚠️  Sobran en BD: {m['sobran_bd']} campos")
            if 'sobran_lista' in m:
                print(f"     Ejemplos: {', '.join(m['sobran_lista'][:5])}")
        print()
    
    print('=' * 100)
    print('⚠️  MODELOS CON CAMPOS EXTRAS EN BD (Verificar)')
    print('=' * 100)
    print(f'Total: {len(sobran_en_bd)} modelos')
    print()
    for m in sobran_en_bd:
        print(f"  ⚠️  {m['tabla']:40s} archivo: {m['archivo']}")
        print(f"     BD: {m['bd_cols']} cols | Modelo: {m['model_cols']} cols")
        print(f"     Sobran en BD: {m['sobran_bd']} campos")
        print(f"     Ejemplos: {', '.join(m['sobran_lista'][:5])}")
        print()
    
    print('=' * 100)
    print('🚫 TABLAS SIN MODELO')
    print('=' * 100)
    print(f'Total: {len(sin_modelo)} tablas')
    print()
    for tabla, cols in sin_modelo:
        print(f'  🚫 {tabla:40s} {cols:3d} columnas')
    
    print()
    print('=' * 100)
    print('📈 RESUMEN ESTADÍSTICO')
    print('=' * 100)
    print(f'Total tablas en BD: {len(bd_tables)}')
    print(f'  ✅ Sincronizados: {len(perfectos)} ({len(perfectos)/len(bd_tables)*100:.1f}%)')
    print(f'  📁 Multi-clase: {len(multi_clase)} ({len(multi_clase)/len(bd_tables)*100:.1f}%)')
    print(f'  ❌ Con problemas: {len(faltan_en_bd)} ({len(faltan_en_bd)/len(bd_tables)*100:.1f}%)')
    print(f'  ⚠️  Extras en BD: {len(sobran_en_bd)} ({len(sobran_en_bd)/len(bd_tables)*100:.1f}%)')
    print(f'  🚫 Sin modelo: {len(sin_modelo)} ({len(sin_modelo)/len(bd_tables)*100:.1f}%)')
    print()
    
    print('=' * 100)
    print('💡 RECOMENDACIONES')
    print('=' * 100)
    print()
    print('1. ✅ MODELOS PERFECTOS: No requieren acción')
    print()
    print('2. 📁 MULTI-CLASE: Verificar que la clase principal esté correcta')
    print('   - Estos archivos contienen múltiples modelos (EntregaTarea, Rubrica, etc.)')
    print('   - Es ARQUITECTURA NORMAL, no un error')
    print()
    print('3. ❌ FALTAN CAMPOS EN BD:')
    print('   - ConfiguracionAntiTrampa: Modelo SOBREDISEÑADO (80+ campos extra)')
    print('     RECOMENDACIÓN: Sincronizar modelo CON BD (eliminar campos del modelo)')
    print('   - Otros: Agregar campos faltantes a BD con migración')
    print()
    print('4. ⚠️  SOBRAN CAMPOS EN BD: Agregar al modelo si son necesarios')
    print()
    print('5. 🚫 SIN MODELO: Crear modelos si se van a usar')
    print()
    
    return {
        'perfectos': perfectos,
        'multi_clase': multi_clase,
        'faltan_en_bd': faltan_en_bd,
        'sobran_en_bd': sobran_en_bd,
        'sin_modelo': sin_modelo,
    }

if __name__ == '__main__':
    results = analyze_all_models()
