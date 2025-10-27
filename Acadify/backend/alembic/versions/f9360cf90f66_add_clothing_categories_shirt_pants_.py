"""add_clothing_categories_shirt_pants_shoes_jacket

Revision ID: f9360cf90f66
Revises: a5664b066656
Create Date: 2025-09-23 01:22:17.447947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9360cf90f66'
down_revision: Union[str, Sequence[str], None] = 'a5664b066656'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Actualizar assets existentes de 'clothes' a categorías específicas
    # Esto se puede hacer manualmente después o con un script
    
    # Para ahora, solo documentamos que las nuevas categorías serán:
    # shirt, pants, shoes, jacket
    # El model AvatarAsset ya acepta cualquier string en category
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # Volver assets de categorías específicas a 'clothes'
    op.execute("""
        UPDATE avatar_asset 
        SET category = 'clothes' 
        WHERE category IN ('shirt', 'pants', 'shoes', 'jacket')
    """)
    pass
