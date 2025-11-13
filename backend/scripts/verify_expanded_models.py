"""
Script para verificar que los modelos expandidos se aplicaron correctamente
"""
from sqlalchemy import create_engine, text
from src.core.config import settings

def verificar_modelos():
    """Verifica que las columnas y ENUMs se agregaron correctamente"""
    engine = create_engine(settings.database_url)
    
    print("=" * 80)
    print("VERIFICACIÓN DE MODELOS EXPANDIDOS")
    print("=" * 80)
    
    with engine.connect() as conn:
        # ========== VERIFICAR COLUMNAS ==========
        print("\n📊 CONTEO DE COLUMNAS:")
        print("-" * 80)
        
        # Curso
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'Curso'
        """))
        curso_cols = result.scalar()
        print(f"✓ Curso: {curso_cols} columnas (esperado ~70)")
        
        # Programa
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'Programa'
        """))
        programa_cols = result.scalar()
        print(f"✓ Programa: {programa_cols} columnas (esperado ~95)")
        
        # Grupo
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'Grupo'
        """))
        grupo_cols = result.scalar()
        print(f"✓ Grupo: {grupo_cols} columnas (esperado ~65)")
        
        # ========== VERIFICAR ENUMS ==========
        print("\n🎨 ENUMS CREADOS:")
        print("-" * 80)
        
        result = conn.execute(text("""
            SELECT typname 
            FROM pg_type 
            WHERE typname IN (
                'nivel_dificultad', 'tipo_curso', 'categoria_curso', 
                'estado_curso', 'idioma_curso', 'estado_programa', 
                'duracion_programa', 'estado_grupo', 'tipo_grupo', 
                'modalidad_asistencia', 'formato_evaluacion'
            )
            ORDER BY typname
        """))
        
        enums = [row[0] for row in result]
        print(f"Total ENUMs creados: {len(enums)}/11")
        for enum in enums:
            print(f"  ✓ {enum}")
        
        # ========== VERIFICAR CAMPOS ESPECÍFICOS ==========
        print("\n🔍 CAMPOS ESPECÍFICOS CURSO:")
        print("-" * 80)
        
        result = conn.execute(text("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns 
            WHERE table_name = 'Curso' 
            AND column_name IN (
                'horas_teoricas', 'nivel_dificultad', 'tipo_curso', 
                'categoria_curso', 'estado', 'idioma', 
                'cupos_disponibles', 'permite_lista_espera',
                'tiene_costo', 'costo_matricula', 'genera_certificado',
                'metadata_curso', 'fecha_creacion'
            )
            ORDER BY column_name
        """))
        
        for row in result:
            print(f"  ✓ {row[0]:<30} {row[1]:<20} ({row[2]})")
        
        # ========== VERIFICAR CAMPOS ESPECÍFICOS PROGRAMA ==========
        print("\n🔍 CAMPOS ESPECÍFICOS PROGRAMA:")
        print("-" * 80)
        
        result = conn.execute(text("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns 
            WHERE table_name = 'Programa' 
            AND column_name IN (
                'codigo_programa', 'sigla', 'version', 'estado', 
                'duracion', 'creditos_totales', 'modalidad_programa',
                'tiene_costo', 'esta_acreditado', 'registro_calificado',
                'plan_estudios', 'malla_curricular'
            )
            ORDER BY column_name
        """))
        
        for row in result:
            print(f"  ✓ {row[0]:<30} {row[1]:<20} ({row[2]})")
        
        # ========== VERIFICAR CAMPOS ESPECÍFICOS GRUPO ==========
        print("\n🔍 CAMPOS ESPECÍFICOS GRUPO:")
        print("-" * 80)
        
        result = conn.execute(text("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns 
            WHERE table_name = 'Grupo' 
            AND column_name IN (
                'codigo_grupo', 'seccion', 'nivel', 'estado', 
                'tipo_grupo', 'periodo_academico_id',
                'capacidad_minima', 'capacidad_maxima', 'cupos_disponibles',
                'horario_regular', 'modalidad_grupo', 'criterios_evaluacion',
                'permite_interaccion_estudiantes'
            )
            ORDER BY column_name
        """))
        
        for row in result:
            print(f"  ✓ {row[0]:<30} {row[1]:<20} ({row[2]})")
        
        # ========== VERIFICAR ÍNDICES ==========
        print("\n📑 ÍNDICES CREADOS:")
        print("-" * 80)
        
        result = conn.execute(text("""
            SELECT 
                tablename,
                indexname
            FROM pg_indexes 
            WHERE indexname IN (
                'ix_curso_estado', 'ix_curso_tipo_curso', 
                'ix_programa_estado', 'ix_programa_codigo',
                'ix_grupo_estado', 'ix_grupo_periodo',
                'ix_grupo_codigo'
            )
            ORDER BY tablename, indexname
        """))
        
        for row in result:
            print(f"  ✓ {row[0]:<20} → {row[1]}")
        
        print("\n" + "=" * 80)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("=" * 80)
        
        # Resumen
        total_campos = curso_cols + programa_cols + grupo_cols
        print(f"\n📊 RESUMEN:")
        print(f"  Total columnas agregadas: {total_campos}")
        print(f"  Total ENUMs creados: {len(enums)}/11")
        print(f"  Estado: {'✅ EXITOSO' if len(enums) == 11 else '⚠️ REVISAR'}")

if __name__ == "__main__":
    verificar_modelos()
