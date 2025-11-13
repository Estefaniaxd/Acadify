"""add_missing_curso_fields

Revision ID: 744e107d1138
Revises: 2471209688e1
Create Date: 2025-10-29 13:23:35.198590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '744e107d1138'
down_revision: Union[str, Sequence[str], None] = '2471209688e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agregar campos faltantes a la tabla Curso."""
    
    # Campos de información básica
    op.add_column('Curso', sa.Column('objetivos', sa.TEXT(), nullable=True))
    op.add_column('Curso', sa.Column('codigo_curso', sa.String(20), nullable=True, comment='Código identificador del curso (ej: MAT101)'))
    op.add_column('Curso', sa.Column('codigo_acceso', sa.String(10), nullable=True, unique=True, comment='Código para que estudiantes se unan'))
    op.add_column('Curso', sa.Column('creditos', sa.INTEGER(), nullable=True, server_default='0'))
    op.add_column('Curso', sa.Column('horas_academicas', sa.INTEGER(), nullable=True, server_default='0'))
    
    # Campos de configuración
    op.add_column('Curso', sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('Curso', sa.Column('permite_inscripcion', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('Curso', sa.Column('maximo_estudiantes', sa.INTEGER(), nullable=True))
    op.add_column('Curso', sa.Column('minimo_estudiantes', sa.INTEGER(), nullable=True, server_default='1'))
    
    # Campos de configuración de material
    op.add_column('Curso', sa.Column('permite_material_estudiantes', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('Curso', sa.Column('requiere_aprobacion_material', sa.Boolean(), nullable=False, server_default='true'))
    
    # Crear índice para codigo_acceso
    op.create_index('idx_curso_codigo_acceso', 'Curso', ['codigo_acceso'], unique=True)
    
    print("✅ Campos agregados exitosamente a la tabla Curso")


def downgrade() -> None:
    """Eliminar campos agregados de la tabla Curso."""
    
    # Eliminar índice
    op.drop_index('idx_curso_codigo_acceso', table_name='Curso')
    
    # Eliminar columnas
    op.drop_column('Curso', 'requiere_aprobacion_material')
    op.drop_column('Curso', 'permite_material_estudiantes')
    op.drop_column('Curso', 'minimo_estudiantes')
    op.drop_column('Curso', 'maximo_estudiantes')
    op.drop_column('Curso', 'permite_inscripcion')
    op.drop_column('Curso', 'activo')
    op.drop_column('Curso', 'horas_academicas')
    op.drop_column('Curso', 'creditos')
    op.drop_column('Curso', 'codigo_acceso')
    op.drop_column('Curso', 'codigo_curso')
    op.drop_column('Curso', 'objetivos')
    
    print("⬇️ Campos eliminados de la tabla Curso")
