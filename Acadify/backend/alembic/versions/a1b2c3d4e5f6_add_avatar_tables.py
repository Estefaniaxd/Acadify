"""Add avatar tables for user avatars and assets

Revision ID: a1b2c3d4e5f6
Revises: fc4e3b4225a5
Create Date: 2025-09-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'fc4e3b4225a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to add avatar tables."""
    
    # Crear tabla avatar_asset
    op.create_table('avatar_asset',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
    sa.Column('meta_info', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.String(length=1), server_default=sa.text("'Y'"), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('filename'),
        comment='Assets disponibles para construcción de avatars'
    )
    
    # Crear índices para avatar_asset
    op.create_index(op.f('ix_avatar_asset_id'), 'avatar_asset', ['id'], unique=False)
    op.create_index(op.f('ix_avatar_asset_category'), 'avatar_asset', ['category'], unique=False)
    
    # Crear tabla user_avatar
    op.create_table('user_avatar',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('layers', sa.JSON(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('layers_hash', sa.String(length=64), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_public', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['Usuario.usuario_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Avatars creados y guardados por usuarios'
    )
    
    # Crear índices para user_avatar
    op.create_index(op.f('ix_user_avatar_id'), 'user_avatar', ['id'], unique=False)
    op.create_index(op.f('ix_user_avatar_user_id'), 'user_avatar', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_avatar_layers_hash'), 'user_avatar', ['layers_hash'], unique=False)
    
    # Agregar constraint para un solo avatar activo por usuario
    # Restricción única estándar (no condicional, por compatibilidad)
    op.create_unique_constraint(
        'uk_user_avatar_active_per_user',
        'user_avatar',
        ['user_id']
    )


def downgrade() -> None:
    """Downgrade schema to remove avatar tables."""
    
    # Eliminar constraint único
    op.drop_constraint('uk_user_avatar_active_per_user', 'user_avatar', type_='unique')
    
    # Eliminar índices de user_avatar
    op.drop_index(op.f('ix_user_avatar_layers_hash'), table_name='user_avatar')
    op.drop_index(op.f('ix_user_avatar_user_id'), table_name='user_avatar')
    op.drop_index(op.f('ix_user_avatar_id'), table_name='user_avatar')
    
    # Eliminar tabla user_avatar
    op.drop_table('user_avatar')
    
    # Eliminar índices de avatar_asset
    op.drop_index(op.f('ix_avatar_asset_category'), table_name='avatar_asset')
    op.drop_index(op.f('ix_avatar_asset_id'), table_name='avatar_asset')
    
    # Eliminar tabla avatar_asset
    op.drop_table('avatar_asset')