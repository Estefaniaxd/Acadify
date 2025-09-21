"""add invitation_tokens table

Revision ID: add_invitation_tokens
Revises: 142455def377
Create Date: 2025-09-18

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_invitation_tokens'
down_revision: Union[str, Sequence[str], None] = '142455def377'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'invitation_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('codigo', sa.String(length=6), nullable=False, unique=True, index=True),
        sa.Column('email_destino', sa.String(length=100), nullable=False),
        sa.Column('institucion_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('Institucion.institucion_id', ondelete='CASCADE'), nullable=False),
        sa.Column('estado', sa.Enum('pendiente', 'usado', 'expirado', name='estado_invitacion'), nullable=False, server_default='pendiente'),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_expiracion', sa.DateTime(timezone=True), nullable=False),
        sa.Column('coordinador_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('Usuario.usuario_id', ondelete='SET NULL'), nullable=True),
        sa.Column('usado_en', sa.DateTime(timezone=True), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('invitation_tokens')
