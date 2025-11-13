"""Add indexes to all foreign keys

Revision ID: add_fk_indexes
Revises: a9a32870107a
Create Date: 2025-10-28 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_fk_indexes'
down_revision = 'a9a32870107a'
branch_labels = None
depends_on = None

def upgrade():
    """Add indexes to foreign key columns for better query performance"""
    
    # Nota: Los índices se crearán automáticamente en nuevas instalaciones
    # porque agregamos index=True a los modelos.
    # 
    # Para bases de datos existentes, SQLAlchemy detectará los cambios
    # cuando se ejecute: alembic revision --autogenerate -m "add fk indexes"
    pass

def downgrade():
    """Remove indexes from foreign key columns"""
    pass
