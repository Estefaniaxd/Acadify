"""merge_all_heads

Revision ID: af506a175a7f
Revises: 09071cc14b42, remove_chk_login_constraint, add_oauth_tokens, fix_reacciones_unique_emoji
Create Date: 2025-11-23 20:45:28.582453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af506a175a7f'
down_revision: Union[str, Sequence[str], None] = ('09071cc14b42', 'remove_chk_login_constraint', 'add_oauth_tokens', 'fix_reacciones_unique_emoji')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
