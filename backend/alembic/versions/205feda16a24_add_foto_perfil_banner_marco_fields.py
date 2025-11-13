"""add_foto_perfil_banner_marco_fields

Revision ID: 205feda16a24
Revises: 3973d5a2f9d3
Create Date: 2025-11-03 12:39:01.775779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '205feda16a24'
down_revision: Union[str, Sequence[str], None] = '3973d5a2f9d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar campos para foto de perfil custom
    op.add_column('Usuario', sa.Column('foto_perfil_custom_url', sa.Text(), nullable=True))
    op.add_column('Usuario', sa.Column('usa_foto_custom', sa.Boolean(), nullable=False, server_default='false'))
    
    # Agregar campos para banner/portada
    op.add_column('Usuario', sa.Column('banner_url', sa.Text(), nullable=True))
    op.add_column('Usuario', sa.Column('banner_activo_id', sa.Uuid(), nullable=True))
    
    # Agregar campo para marco de perfil (de la tienda)
    op.add_column('Usuario', sa.Column('marco_perfil_id', sa.Uuid(), nullable=True))
    
    # Foreign keys - solo si la tabla tienda_item existe
    connection = op.get_bind()
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='tienda_item')"
    ))
    tienda_exists = result.scalar()
    
    if tienda_exists:
        op.create_foreign_key(
            'fk_usuario_banner_tienda',
            'Usuario', 'tienda_item',
            ['banner_activo_id'], ['item_id'],
            ondelete='SET NULL'
        )
        
        op.create_foreign_key(
            'fk_usuario_marco_tienda',
            'Usuario', 'tienda_item',
            ['marco_perfil_id'], ['item_id'],
            ondelete='SET NULL'
        )
    
    # Índices para mejor performance
    op.create_index('idx_usuario_foto_custom', 'Usuario', ['usa_foto_custom'])
    op.create_index('idx_usuario_banner_activo', 'Usuario', ['banner_activo_id'])
    op.create_index('idx_usuario_marco_perfil', 'Usuario', ['marco_perfil_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar índices
    op.drop_index('idx_usuario_marco_perfil', table_name='Usuario')
    op.drop_index('idx_usuario_banner_activo', table_name='Usuario')
    op.drop_index('idx_usuario_foto_custom', table_name='Usuario')
    
    # Eliminar foreign keys si existen
    connection = op.get_bind()
    try:
        op.drop_constraint('fk_usuario_marco_tienda', 'Usuario', type_='foreignkey')
    except:
        pass
    try:
        op.drop_constraint('fk_usuario_banner_tienda', 'Usuario', type_='foreignkey')
    except:
        pass
    
    # Eliminar columnas
    op.drop_column('Usuario', 'marco_perfil_id')
    op.drop_column('Usuario', 'banner_activo_id')
    op.drop_column('Usuario', 'banner_url')
    op.drop_column('Usuario', 'usa_foto_custom')
    op.drop_column('Usuario', 'foto_perfil_custom_url')
