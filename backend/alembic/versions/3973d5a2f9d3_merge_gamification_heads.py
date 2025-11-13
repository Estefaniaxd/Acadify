"""merge_gamification_heads

Revision ID: 3973d5a2f9d3
Revises: 004_gamification_sql, d64825b96463
Create Date: 2025-11-03 12:38:20.856079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3973d5a2f9d3'
down_revision: Union[str, Sequence[str], None] = ('004_gamification_sql', 'd64825b96463')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
