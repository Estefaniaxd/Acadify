"""Remove chk_login constraint to allow all users to have both username and email

Revision ID: remove_chk_login_constraint
Revises: 
Create Date: 2025-11-10 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_chk_login_constraint'
down_revision = None  # Update this with the latest revision
branch_labels = None
depends_on = None


def upgrade():
    # Drop the chk_login constraint
    op.drop_constraint('chk_login', 'Usuario', type_='check')


def downgrade():
    # Recreate the old constraint if needed
    op.create_check_constraint(
        'chk_login',
        'Usuario',
        "(rol = 'administrador' AND username IS NOT NULL AND correo_institucional IS NULL) "
        "OR (rol <> 'administrador' AND correo_institucional IS NOT NULL AND username IS NULL)"
    )
