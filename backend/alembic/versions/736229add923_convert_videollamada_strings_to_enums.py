"""convert_videollamada_strings_to_enums

Convierte columnas de tipo String a Enum en las tablas de videollamadas
para mejorar type-safety y validación.

Revision ID: 736229add923
Revises: a3987820719a
Create Date: 2025-11-01 20:30:29.203315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '736229add923'
down_revision: Union[str, Sequence[str], None] = 'a3987820719a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Convierte columnas String a Enum en videollamadas.
    
    Cambios:
    - videollamadas.tipo_llamada: VARCHAR -> TipoLlamada Enum
    - videollamadas.estado: VARCHAR -> EstadoVideollamada Enum
    - videollamada_participantes.calidad_conexion: VARCHAR -> CalidadConexion Enum
    - videollamada_grabaciones.formato: VARCHAR -> FormatoGrabacion Enum
    - videollamada_grabaciones.calidad: VARCHAR -> CalidadGrabacion Enum
    - videollamada_grabaciones.estado_procesamiento: VARCHAR -> EstadoProcesamiento Enum
    """
    
    # 1. Eliminar CheckConstraints existentes que bloquean la conversión
    op.execute("ALTER TABLE videollamadas DROP CONSTRAINT IF EXISTS ck_videollamada_tipo CASCADE")
    op.execute("ALTER TABLE videollamadas DROP CONSTRAINT IF EXISTS ck_videollamada_estado CASCADE")
    op.execute("ALTER TABLE videollamada_participantes DROP CONSTRAINT IF EXISTS ck_participante_calidad CASCADE")
    op.execute("ALTER TABLE videollamada_grabaciones DROP CONSTRAINT IF EXISTS ck_grabacion_formato CASCADE")
    op.execute("ALTER TABLE videollamada_grabaciones DROP CONSTRAINT IF EXISTS ck_grabacion_calidad CASCADE")
    op.execute("ALTER TABLE videollamada_grabaciones DROP CONSTRAINT IF EXISTS ck_grabacion_estado CASCADE")
    
    # 2. Crear tipos ENUM en PostgreSQL
    op.execute("CREATE TYPE tipollamada AS ENUM ('VIDEO', 'VOZ')")
    op.execute("CREATE TYPE estadovideollamada AS ENUM ('PROGRAMADA', 'ACTIVA', 'FINALIZADA', 'CANCELADA')")
    op.execute("CREATE TYPE calidadconexion AS ENUM ('EXCELENTE', 'BUENA', 'REGULAR', 'MALA')")
    op.execute("CREATE TYPE formatograbacion AS ENUM ('MP4', 'WEBM', 'MKV', 'AVI')")
    op.execute("CREATE TYPE calidadgrabacion AS ENUM ('SD', 'HD', 'FHD', 'UHD_4K')")
    op.execute("CREATE TYPE estadoprocesamiento AS ENUM ('PENDIENTE', 'PROCESANDO', 'COMPLETADO', 'ERROR')")
    
    # 3. Convertir videollamadas.tipo_llamada (video -> VIDEO, voz -> VOZ)
    op.execute("""
        ALTER TABLE videollamadas 
        ALTER COLUMN tipo_llamada TYPE tipollamada 
        USING UPPER(tipo_llamada)::tipollamada
    """)
    
    # 4. Convertir videollamadas.estado (activa -> ACTIVA, finalizada -> FINALIZADA, cancelada -> CANCELADA)
    op.execute("""
        ALTER TABLE videollamadas 
        ALTER COLUMN estado TYPE estadovideollamada 
        USING UPPER(estado)::estadovideollamada
    """)
    
    # Actualizar el default de estado
    op.execute("ALTER TABLE videollamadas ALTER COLUMN estado SET DEFAULT 'ACTIVA'::estadovideollamada")
    
    # 5. Convertir videollamada_participantes.calidad_conexion (si tiene datos)
    op.execute("""
        ALTER TABLE videollamada_participantes 
        ALTER COLUMN calidad_conexion TYPE calidadconexion 
        USING CASE 
            WHEN calidad_conexion IS NULL THEN NULL
            ELSE UPPER(calidad_conexion)::calidadconexion
        END
    """)
    
    # 6. Convertir videollamada_grabaciones.formato (si tiene datos)
    op.execute("""
        ALTER TABLE videollamada_grabaciones 
        ALTER COLUMN formato TYPE formatograbacion 
        USING CASE 
            WHEN formato IS NULL THEN NULL
            ELSE UPPER(formato)::formatograbacion
        END
    """)
    
    # 7. Convertir videollamada_grabaciones.calidad (si tiene datos)
    # Casos especiales: 4K -> UHD_4K
    op.execute("""
        ALTER TABLE videollamada_grabaciones 
        ALTER COLUMN calidad TYPE calidadgrabacion 
        USING CASE 
            WHEN calidad IS NULL THEN NULL
            WHEN UPPER(calidad) = '4K' THEN 'UHD_4K'::calidadgrabacion
            ELSE UPPER(calidad)::calidadgrabacion
        END
    """)
    
    # 8. Convertir videollamada_grabaciones.estado_procesamiento
    # Primero eliminar el default
    op.execute("ALTER TABLE videollamada_grabaciones ALTER COLUMN estado_procesamiento DROP DEFAULT")
    
    # Convertir el tipo
    op.execute("""
        ALTER TABLE videollamada_grabaciones 
        ALTER COLUMN estado_procesamiento TYPE estadoprocesamiento 
        USING UPPER(estado_procesamiento)::estadoprocesamiento
    """)
    
    # Actualizar el default de estado_procesamiento
    op.execute("ALTER TABLE videollamada_grabaciones ALTER COLUMN estado_procesamiento SET DEFAULT 'PENDIENTE'::estadoprocesamiento")


def downgrade() -> None:
    """
    Revierte los cambios, convirtiendo Enum de vuelta a VARCHAR.
    """
    
    # 1. Convertir de vuelta a VARCHAR
    op.execute("""
        ALTER TABLE videollamadas 
        ALTER COLUMN tipo_llamada TYPE VARCHAR(20) 
        USING LOWER(tipo_llamada::text)
    """)
    
    op.execute("""
        ALTER TABLE videollamadas 
        ALTER COLUMN estado TYPE VARCHAR(20) 
        USING LOWER(estado::text)
    """)
    
    op.execute("ALTER TABLE videollamadas ALTER COLUMN estado SET DEFAULT 'activa'")
    
    op.execute("""
        ALTER TABLE videollamada_participantes 
        ALTER COLUMN calidad_conexion TYPE VARCHAR(20) 
        USING LOWER(calidad_conexion::text)
    """)
    
    op.execute("""
        ALTER TABLE videollamada_grabaciones 
        ALTER COLUMN formato TYPE VARCHAR(20) 
        USING LOWER(formato::text)
    """)
    
    # Caso especial para 4K
    op.execute("""
        ALTER TABLE videollamada_grabaciones 
        ALTER COLUMN calidad TYPE VARCHAR(20) 
        USING CASE 
            WHEN calidad::text = 'UHD_4K' THEN '4K'
            ELSE LOWER(calidad::text)
        END
    """)
    
    op.execute("""
        ALTER TABLE videollamada_grabaciones 
        ALTER COLUMN estado_procesamiento TYPE VARCHAR(20) 
        USING LOWER(estado_procesamiento::text)
    """)
    
    op.execute("ALTER TABLE videollamada_grabaciones ALTER COLUMN estado_procesamiento SET DEFAULT 'pendiente'")
    
    # 2. Eliminar tipos ENUM
    op.execute("DROP TYPE IF EXISTS tipollamada CASCADE")
    op.execute("DROP TYPE IF EXISTS estadovideollamada CASCADE")
    op.execute("DROP TYPE IF EXISTS calidadconexion CASCADE")
    op.execute("DROP TYPE IF EXISTS formatograbacion CASCADE")
    op.execute("DROP TYPE IF EXISTS calidadgrabacion CASCADE")
    op.execute("DROP TYPE IF EXISTS estadoprocesamiento CASCADE")
