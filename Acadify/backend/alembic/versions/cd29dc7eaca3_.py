"""empty message

Revision ID: cd29dc7eaca3
Revises: a7b8c9d0e1f2, f9360cf90f66
Create Date: 2025-09-26 17:52:59.152557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd29dc7eaca3'
down_revision: Union[str, Sequence[str], None] = ('a7b8c9d0e1f2', 'f9360cf90f66')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
