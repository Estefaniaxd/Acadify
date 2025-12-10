"""
Revision para permitir múltiples reacciones por usuario y comentario (una por emoji).
Agrega índice único (comentario_id, usuario_id, emoji) en la tabla Reacciones.
Elimina índice único antiguo si existe.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_reacciones_unique_emoji'
down_revision = None  # Cambia esto por la última migración real
branch_labels = None
depends_on = None

def upgrade():
    # Eliminar constraint único antiguo si existe
    with op.batch_alter_table('Reacciones') as batch_op:
        # try:
        #     batch_op.drop_constraint('uq_reacciones_comentario_usuario', type_='unique')
        # except Exception:
        #     pass  # Si no existe, ignorar
        # Crear nuevo índice único
        batch_op.create_unique_constraint('uq_reacciones_comentario_usuario_emoji', ['comentario_id', 'usuario_id', 'emoji'])

def downgrade():
    with op.batch_alter_table('Reacciones') as batch_op:
        batch_op.drop_constraint('uq_reacciones_comentario_usuario_emoji', type_='unique')
        # Restaurar el índice antiguo si era necesario
        batch_op.create_unique_constraint('uq_reacciones_comentario_usuario', ['comentario_id', 'usuario_id'])
