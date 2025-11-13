"""add_dominio_field_to_institucion

Revision ID: 2471209688e1
Revises: add_fk_indexes
Create Date: 2025-10-29 10:33:56.865412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2471209688e1'
down_revision: Union[str, Sequence[str], None] = 'add_fk_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar columna dominio a instituciones
    op.add_column(
        'Institucion',
        sa.Column('dominio', sa.String(length=255), nullable=True, comment='Dominio de correo institucional (ej: arp.edu.co)')
    )
    
    # Crear índice para búsquedas rápidas por dominio
    op.create_index(
        'idx_institucion_dominio',
        'Institucion',
        ['dominio']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar índice
    op.drop_index('idx_institucion_dominio', table_name='Institucion')
    
    # Eliminar columna
    op.drop_column('Institucion', 'dominio')
