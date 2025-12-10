"""Add google_resources to entregas_tareas

Revision ID: add_google_resources
Revises: 
Create Date: 2025-11-23 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_google_resources'
down_revision = None  # Update this with the actual latest revision
branch_labels = None
depends_on = None


def upgrade():
    # Add google_resources column to entregas_tareas table
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('entregas_tareas')]
    if 'google_resources' not in columns:
        op.add_column(
            'entregas_tareas',
            sa.Column('google_resources', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
        )


def downgrade():
    # Remove google_resources column
    op.drop_column('entregas_tareas', 'google_resources')
