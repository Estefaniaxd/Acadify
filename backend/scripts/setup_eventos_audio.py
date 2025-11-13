#!/usr/bin/env python3
"""
Script para crear la tabla eventos_audio directamente en PostgreSQL.
Ejecuta el SQL sin usar Alembic para evitar complicaciones.

Uso:
    python setup_eventos_audio.py
"""

import sys
import os
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from src.core.config import settings


def crear_tabla_eventos_audio():
    """
    Crea la tabla eventos_audio directamente en PostgreSQL.
    """
    print("🚀 Iniciando creación de tabla eventos_audio...")
    
    # Crear engine de SQLAlchemy
    try:
        engine = create_engine(settings.DATABASE_URL)
        print(f"✅ Conectado a la base de datos: {settings.DATABASE_URL.split('@')[-1]}")
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return False
    
    # SQL para crear la tabla
    sql_create_table = """
    -- Crear tabla eventos_audio para almacenar eventos de audio del sistema de proctoring
    CREATE TABLE IF NOT EXISTS eventos_audio (
        evento_audio_id SERIAL PRIMARY KEY,
        intento_id VARCHAR NOT NULL,
        nivel_audio FLOAT NOT NULL CHECK (nivel_audio >= 0 AND nivel_audio <= 100),
        frecuencias_detectadas JSONB DEFAULT '[]'::jsonb,
        duracion_ms INTEGER NOT NULL CHECK (duracion_ms > 0),
        es_sospechoso BOOLEAN DEFAULT false,
        descripcion TEXT,
        datos_adicionales JSONB DEFAULT '{}'::jsonb,
        fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        
        -- Foreign Key hacia intentos_evaluacion
        CONSTRAINT fk_eventos_audio_intento 
            FOREIGN KEY (intento_id) 
            REFERENCES intentos_evaluacion(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    );
    """
    
    sql_create_indexes = """
    -- Crear índices para optimizar las consultas
    CREATE INDEX IF NOT EXISTS idx_eventos_audio_intento_id 
        ON eventos_audio(intento_id);

    CREATE INDEX IF NOT EXISTS idx_eventos_audio_fecha_creacion 
        ON eventos_audio(fecha_creacion DESC);

    CREATE INDEX IF NOT EXISTS idx_eventos_audio_sospechoso 
        ON eventos_audio(es_sospechoso) 
        WHERE es_sospechoso = true;

    CREATE INDEX IF NOT EXISTS idx_eventos_audio_nivel_alto 
        ON eventos_audio(nivel_audio) 
        WHERE nivel_audio > 70;
    """
    
    sql_create_comments = """
    -- Comentarios descriptivos
    COMMENT ON TABLE eventos_audio IS 'Registra eventos de audio capturados durante el sistema de proctoring';
    COMMENT ON COLUMN eventos_audio.evento_audio_id IS 'ID único del evento de audio';
    COMMENT ON COLUMN eventos_audio.intento_id IS 'Referencia al intento de examen';
    COMMENT ON COLUMN eventos_audio.nivel_audio IS 'Nivel de audio detectado (0-100)';
    COMMENT ON COLUMN eventos_audio.frecuencias_detectadas IS 'Array JSON con frecuencias dominantes detectadas';
    COMMENT ON COLUMN eventos_audio.duracion_ms IS 'Duración del evento en milisegundos';
    COMMENT ON COLUMN eventos_audio.es_sospechoso IS 'Indica si el evento es considerado sospechoso';
    COMMENT ON COLUMN eventos_audio.datos_adicionales IS 'Datos adicionales en formato JSON';
    """
    
    try:
        with engine.begin() as conn:
            # Crear tabla
            print("\n📋 Creando tabla eventos_audio...")
            conn.execute(text(sql_create_table))
            print("✅ Tabla eventos_audio creada exitosamente")
            
            # Crear índices
            print("\n🔍 Creando índices...")
            conn.execute(text(sql_create_indexes))
            print("✅ Índices creados exitosamente")
            
            # Agregar comentarios
            print("\n📝 Agregando comentarios...")
            conn.execute(text(sql_create_comments))
            print("✅ Comentarios agregados exitosamente")
            
            # Verificar que la tabla existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'eventos_audio'
                );
            """))
            exists = result.scalar()
            
            if exists:
                print("\n✨ ¡Tabla eventos_audio verificada correctamente!")
                
                # Mostrar estructura de la tabla
                print("\n📊 Estructura de la tabla:")
                result = conn.execute(text("""
                    SELECT 
                        column_name,
                        data_type,
                        character_maximum_length,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_name = 'eventos_audio'
                    ORDER BY ordinal_position;
                """))
                
                print(f"\n{'COLUMNA':<30} {'TIPO':<20} {'NULLABLE':<10} {'DEFAULT':<30}")
                print("-" * 90)
                for row in result:
                    col_name = row[0]
                    data_type = row[1]
                    if row[2]:
                        data_type += f"({row[2]})"
                    nullable = row[3]
                    default = row[4] or ''
                    print(f"{col_name:<30} {data_type:<20} {nullable:<10} {default:<30}")
                
                # Contar registros
                result = conn.execute(text("SELECT COUNT(*) FROM eventos_audio"))
                count = result.scalar()
                print(f"\n📈 Total de registros en eventos_audio: {count}")
                
                return True
            else:
                print("❌ Error: La tabla no se pudo crear")
                return False
                
    except Exception as e:
        print(f"\n❌ Error al ejecutar SQL: {e}")
        return False
    finally:
        engine.dispose()


def verificar_tabla_intentos():
    """
    Verifica que la tabla intentos_evaluacion exista antes de crear eventos_audio.
    """
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.begin() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'intentos_evaluacion'
                );
            """))
            exists = result.scalar()
            
            if not exists:
                print("⚠️  ADVERTENCIA: La tabla 'intentos_evaluacion' no existe.")
                print("   Asegúrate de que las migraciones base estén ejecutadas.")
                return False
            
            return True
    except Exception as e:
        print(f"❌ Error al verificar tabla intentos_examenes: {e}")
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("   SETUP: Tabla eventos_audio para Sistema de Proctoring")
    print("=" * 60)
    
    # Verificar tabla base
    print("\n🔍 Verificando tabla base 'intentos_evaluacion'...")
    if not verificar_tabla_intentos():
        print("\n❌ No se puede continuar sin la tabla base.")
        sys.exit(1)
    
    print("✅ Tabla base verificada correctamente")
    
    # Crear tabla eventos_audio
    if crear_tabla_eventos_audio():
        print("\n" + "=" * 60)
        print("   ✨ ¡SETUP COMPLETADO EXITOSAMENTE! ✨")
        print("=" * 60)
        print("\n📌 Próximos pasos:")
        print("   1. Verificar que los endpoints de proctoring funcionen")
        print("   2. Instalar MediaPipe: npm install @mediapipe/face_detection @mediapipe/camera_utils")
        print("   3. Probar el sistema completo en el navegador")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("   ❌ ERROR EN EL SETUP")
        print("=" * 60)
        sys.exit(1)
