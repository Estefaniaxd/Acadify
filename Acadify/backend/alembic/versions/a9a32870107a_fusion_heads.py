"""Fusion heads

Revision ID: a9a32870107a
Revises: 291ba6082c35, 9f8e5d4c3b2a, ae7c3a726b51
Create Date: 2025-09-30 19:12:25.498646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9a32870107a'
down_revision: Union[str, Sequence[str], None] = ('291ba6082c35', '9f8e5d4c3b2a', 'ae7c3a726b51')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
