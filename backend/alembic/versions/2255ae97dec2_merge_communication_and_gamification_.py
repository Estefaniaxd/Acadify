"""merge_communication_and_gamification_heads

Revision ID: 2255ae97dec2
Revises: 71e793236241, d886690834dd
Create Date: 2025-10-31 16:20:17.645274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2255ae97dec2'
down_revision: Union[str, Sequence[str], None] = ('71e793236241', 'd886690834dd')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
