"""add_comentario_table_only

Revision ID: ae7c3a726b51
Revises: d886690834dd
Create Date: 2025-09-30 13:50:25.470008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ae7c3a726b51'
down_revision: Union[str, Sequence[str], None] = 'd886690834dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crear tabla Comentario para comentarios de cursos."""
    
    # Crear enum para tipos de comentario si no existe
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tipocomentario AS ENUM ('comentario', 'anuncio', 'pregunta', 'respuesta');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Crear tabla Comentario usando SQL directo para evitar problemas con enum
    op.execute("""
        CREATE TABLE IF NOT EXISTS "Comentario" (
            comentario_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            curso_id UUID NOT NULL REFERENCES "Curso"(curso_id) ON DELETE CASCADE,
            autor_id UUID NOT NULL REFERENCES "Usuario"(usuario_id) ON DELETE CASCADE,
            contenido TEXT NOT NULL,
            tipo tipocomentario NOT NULL DEFAULT 'comentario',
            archivos_adjuntos JSON,
            comentario_padre_id UUID REFERENCES "Comentario"(comentario_id) ON DELETE CASCADE,
            fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            fecha_actualizacion TIMESTAMP WITH TIME ZONE,
            fecha_eliminacion TIMESTAMP WITH TIME ZONE,
            esta_eliminado BOOLEAN NOT NULL DEFAULT FALSE,
            editado BOOLEAN NOT NULL DEFAULT FALSE,
            activo BOOLEAN NOT NULL DEFAULT TRUE
        );
    """)
    
    # Crear índices para optimizar consultas
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_comentario_curso_id ON "Comentario"(curso_id);
        CREATE INDEX IF NOT EXISTS idx_comentario_autor_id ON "Comentario"(autor_id);
        CREATE INDEX IF NOT EXISTS idx_comentario_fecha_creacion ON "Comentario"(fecha_creacion);
        CREATE INDEX IF NOT EXISTS idx_comentario_tipo ON "Comentario"(tipo);
        CREATE INDEX IF NOT EXISTS idx_comentario_activo ON "Comentario"(activo);
        CREATE INDEX IF NOT EXISTS idx_comentario_curso_fecha ON "Comentario"(curso_id, fecha_creacion);
        CREATE INDEX IF NOT EXISTS idx_comentario_autor_fecha ON "Comentario"(autor_id, fecha_creacion);
        CREATE INDEX IF NOT EXISTS idx_comentario_tipo_activo ON "Comentario"(tipo, activo);
        CREATE INDEX IF NOT EXISTS idx_comentario_padre ON "Comentario"(comentario_padre_id);
    """)
    
    print("✅ Tabla Comentario creada exitosamente")
    print("✅ Enum TipoComentario creado")
    print("✅ Índices optimizados agregados")


def downgrade() -> None:
    """Eliminar tabla Comentario y enum."""
    
    # Eliminar tabla
    op.drop_table('Comentario')
    
    # Eliminar enum
    op.execute("DROP TYPE IF EXISTS tipocomentario")
    
    print("❌ Tabla Comentario eliminada")
    print("❌ Enum TipoComentario eliminado")
