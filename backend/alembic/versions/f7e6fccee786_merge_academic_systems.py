"""merge_academic_systems

Revision ID: f7e6fccee786
Revises: 8912dfc388c0, add_inscripciones_table
Create Date: 2025-10-30 18:36:41.920062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7e6fccee786'
down_revision: Union[str, Sequence[str], None] = ('8912dfc388c0', 'add_inscripciones_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
