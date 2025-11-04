#!/usr/bin/env python3
"""
Script mejorado de verificación que evita problemas con metadatos cacheados
"""

import asyncio
import asyncpg
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from collections import defaultdict

# Lista de modelos a verificar manualmente (table_name -> filepath)
MODELS_TO_CHECK = {
    # Academic
    'Clase': 'src/models/academic/clase.py',
    'MaterialEducativo': 'src/models/academic/material_educativo.py',
    'Curso': 'src/models/academic/curso.py',
    'Grupo': 'src/models/academic/grupo.py',
    'Programa': 'src/models/academic/programa.py',
    'Institucion': 'src/models/instituciones/institucion.py',
    # Assessment
    'evaluaciones': 'src/models/assessment/evaluacion.py',
    'preguntas_evaluacion': 'src/models/assessment/pregunta_evaluacion.py',
    'respuestas_estudiante': 'src/models/assessment/respuesta_estudiante.py',
    'configuraciones_antitrampa': 'src/models/assessment/configuracion_antitrampa.py',
    # Communication
    'tareas': 'src/models/academic/tarea.py',
    'mensajes': 'src/models/communication/mensaje_chat.py',
    'notificaciones': 'src/models/communication/notificacion.py',
}

async def check_model_sync(conn, table_name, model_module_path):
    """Verifica sincronización de un modelo específico"""
    
    # Obtener columnas de la BD
    db_cols = await conn.fetch("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' 
        AND table_name = $1
        ORDER BY ordinal_position
    """, table_name)
    
    db_col_names = {row['column_name'] for row in db_cols}
    
    # Leer columnas directamente del código fuente sin importar el módulo
    try:
        source_file = model_module_path
        
        with open(source_file, 'r') as f:
            content = f.read()
        
        # Buscar definiciones de columnas
        import re
        # Patrón: nombre_columna = Column(
        pattern = r'^\s+(\w+)\s*=\s*Column\('
        model_col_names = set()
        
        in_class = False
        for line in content.split('\n'):
            if f'class {table_name}(Base)' in line:
                in_class = True
            elif in_class and re.match(r'^class \w+', line):
                break  # Salir al encontrar otra clase
            elif in_class:
                match = re.match(pattern, line)
                if match:
                    model_col_names.add(match.group(1))
        
        # Comparar
        missing_in_db = model_col_names - db_col_names
        extra_in_db = db_col_names - model_col_names
        
        return {
            'table': table_name,
            'db_cols': len(db_col_names),
            'model_cols': len(model_col_names),
            'missing_in_db': missing_in_db,
            'extra_in_db': extra_in_db,
            'synced': len(missing_in_db) == 0 and len(extra_in_db) == 0
        }
        
    except Exception as e:
        return {
            'table': table_name,
            'error': str(e)
        }

async def main():
    db_url = settings.get_database_url(async_driver=False)
    conn = await asyncpg.connect(db_url)
    
    print("="*70)
    print("VERIFICACIÓN MEJORADA: Modelos vs Base de Datos")
    print("="*70)
    print()
    
    results = []
    
    for table_name, module_path in MODELS_TO_CHECK.items():
        result = await check_model_sync(conn, table_name, module_path)
        results.append(result)
        
        print(f"📋 {table_name}")
        print(f"   {'─'*66}")
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   BD: {result['db_cols']} columnas | Modelo: {result['model_cols']} columnas")
            
            if result['synced']:
                print(f"   ✅ Perfectamente sincronizado")
            else:
                if result['missing_in_db']:
                    print(f"   ❌ Faltan en BD ({len(result['missing_in_db'])}): {', '.join(sorted(result['missing_in_db']))}")
                if result['extra_in_db']:
                    print(f"   ⚠️  Extra en BD ({len(result['extra_in_db'])}): {', '.join(sorted(result['extra_in_db']))}")
        print()
    
    # Resumen
    print("="*70)
    print("📊 RESUMEN")
    print("="*70)
    synced = sum(1 for r in results if r.get('synced', False))
    with_issues = len(results) - synced
    print(f"   ✅ Sincronizados: {synced}")
    print(f"   ⚠️  Con diferencias: {with_issues}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
