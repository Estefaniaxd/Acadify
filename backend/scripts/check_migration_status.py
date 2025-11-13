#!/usr/bin/env python3
"""
Script para verificar el estado de la base de datos antes de la migración

Uso:
    python scripts/check_migration_status.py
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect, text
from src.core.config import settings


def check_database_status():
    """Verifica el estado actual de la base de datos"""
    
    print("=" * 80)
    print("🔍 VERIFICACIÓN DE BASE DE DATOS - SISTEMA DE EVALUACIONES")
    print("=" * 80)
    print()
    
    # Crear conexión
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    inspector = inspect(engine)
    
    print("📊 Estado de las tablas:")
    print("-" * 80)
    
    # Tablas esperadas (versión antigua)
    tablas_antiguas = {
        'examenes': 'Tabla de evaluaciones (versión antigua)',
        'preguntas_examen': 'Tabla de preguntas (versión antigua)',
        'intentos_examen': 'Tabla de intentos (versión antigua)',
        'respuestas_estudiante': 'Tabla de respuestas',
        'banco_preguntas': 'Banco de preguntas',
        'configuracion_evaluaciones': 'Configuración (versión antigua)',
        'estadisticas_examen': 'Estadísticas',
        'eventos_anti_trampa': 'Eventos anti-trampa (versión antigua)',
    }
    
    # Tablas nuevas esperadas
    tablas_nuevas = {
        'evaluaciones': 'Tabla de evaluaciones (expandida)',
        'preguntas_evaluacion': 'Tabla de preguntas (expandida)',
        'intentos_evaluacion': 'Tabla de intentos (expandida)',
        'configuraciones_antitrampa': 'Configuración anti-trampa completa',
        'plantillas_configuracion': 'Plantillas de configuración',
    }
    
    tablas_existentes = inspector.get_table_names()
    
    # Verificar tablas antiguas
    print("\n📦 TABLAS ANTIGUAS:")
    for tabla, descripcion in tablas_antiguas.items():
        if tabla in tablas_existentes:
            print(f"  ✅ {tabla}: {descripcion}")
            # Contar registros
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                count = result.scalar()
                print(f"     └─ Registros: {count}")
        else:
            print(f"  ❌ {tabla}: No existe")
    
    # Verificar tablas nuevas
    print("\n🆕 TABLAS NUEVAS (POST-MIGRACIÓN):")
    for tabla, descripcion in tablas_nuevas.items():
        if tabla in tablas_existentes:
            print(f"  ✅ {tabla}: {descripcion} - YA MIGRADA")
        else:
            print(f"  ⏳ {tabla}: {descripcion} - PENDIENTE")
    
    # Verificar versión de Alembic
    print("\n📝 VERSIÓN DE ALEMBIC:")
    print("-" * 80)
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            print(f"  Versión actual: {version}")
            
            if version == 'expand_evaluation_system_complete':
                print("  ✅ La migración ya fue aplicada")
            elif version == '291ba6082c35':
                print("  ⏳ Migración base aplicada, listo para expandir")
            else:
                print(f"  ⚠️  Versión desconocida: {version}")
    except Exception as e:
        print(f"  ❌ Error al verificar versión: {e}")
    
    # Verificar columnas específicas en examenes/evaluaciones
    print("\n🔍 VERIFICACIÓN DE CAMPOS CLAVE:")
    print("-" * 80)
    
    if 'examenes' in tablas_existentes:
        columnas = [col['name'] for col in inspector.get_columns('examenes')]
        campos_nuevos = [
            'tipo_evaluacion',
            'visibilidad',
            'usar_ia_calificacion',
            'requerir_camara',
            'otorga_puntos',
            'es_adaptativa',
        ]
        
        print("  Tabla 'examenes':")
        for campo in campos_nuevos:
            if campo in columnas:
                print(f"    ✅ {campo}: Existe (ya migrada)")
            else:
                print(f"    ⏳ {campo}: No existe (pendiente)")
    
    if 'evaluaciones' in tablas_existentes:
        print("  ✅ Tabla 'evaluaciones' ya migrada")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    print("-" * 80)
    
    if 'evaluaciones' in tablas_existentes:
        print("  ✅ La migración ya fue aplicada. El sistema está actualizado.")
    elif 'examenes' in tablas_existentes:
        columnas_examenes = [col['name'] for col in inspector.get_columns('examenes')]
        if 'tipo_evaluacion' in columnas_examenes:
            print("  ⚠️  Migración parcial detectada. Verifica manualmente.")
        else:
            print("  ✅ Listo para ejecutar la migración:")
            print("     alembic upgrade head")
    else:
        print("  ❌ No hay tablas de evaluación. Ejecuta migraciones desde cero:")
        print("     alembic upgrade head")
    
    print("\n" + "=" * 80)
    print("✅ Verificación completada")
    print("=" * 80)
    
    engine.dispose()


if __name__ == "__main__":
    try:
        check_database_status()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
