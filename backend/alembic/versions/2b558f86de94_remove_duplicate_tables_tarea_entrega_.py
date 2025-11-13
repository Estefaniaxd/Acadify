"""remove_duplicate_tables_tarea_entrega_mensaje

Revision ID: 2b558f86de94
Revises: 744e107d1138
Create Date: 2025-10-29 21:26:14.268729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b558f86de94'
down_revision: Union[str, Sequence[str], None] = '744e107d1138'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Eliminar tablas duplicadas (viejas) que están vacías.
    
    Tablas a eliminar:
    - EntregarTarea (vieja) → Ya existe entregas_tareas (nueva) ✅
    - Tarea (vieja) → Ya existe tareas (nueva) ✅
    - Mensaje (vieja) → Ya existe mensajes (nueva) ✅
    
    Todas estas tablas están vacías (0 registros), confirmado el 2025-10-29.
    ORDEN IMPORTANTE: EntregarTarea primero (tiene FK a Tarea), luego Tarea.
    """
    # PASO 1: Eliminar tabla vieja EntregarTarea (CamelCase) PRIMERO
    # La tabla nueva es "entregas_tareas" (snake_case) con esquema completo
    # Debe eliminarse primero porque tiene FK a Tarea
    op.drop_table('EntregarTarea')
    
    # PASO 2: Eliminar tabla vieja Tarea (CamelCase)
    # La tabla nueva es "tareas" (snake_case) con esquema completo
    op.drop_table('Tarea')
    
    # PASO 3: Eliminar tabla vieja Mensaje (CamelCase)
    # La tabla nueva es "mensajes" (snake_case) con esquema completo
    op.drop_table('Mensaje')
    
    print("✅ Tablas duplicadas eliminadas exitosamente:")
    print("   - EntregarTarea (vieja) → Usar entregas_tareas (nueva)")
    print("   - Tarea (vieja) → Usar tareas (nueva)")
    print("   - Mensaje (vieja) → Usar mensajes (nueva)")


def downgrade() -> None:
    """
    Revertir eliminación de tablas (recrear tablas viejas).
    NOTA: Esta operación NO recuperará datos si existieran.
    """
    # Recrear tabla Tarea (vieja - simple)
    op.create_table(
        'Tarea',
        sa.Column('tarea_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('docente_id', sa.UUID(), nullable=True),
        sa.Column('clase_id', sa.UUID(), nullable=False),
        sa.Column('titulo', sa.String(50), nullable=False),
        sa.Column('descripcion', sa.TEXT(), nullable=True),
        sa.Column('fecha_asignacion', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_limite', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('archivo_adjunto', sa.TEXT(), nullable=True),
        sa.Column('permite_entregas_tardias', sa.BOOLEAN(), nullable=False),
        sa.PrimaryKeyConstraint('tarea_id'),
        sa.ForeignKeyConstraint(['docente_id'], ['Docente.docente_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['clase_id'], ['Clase.clase_id'], ondelete='CASCADE')
    )
    
    # Recrear tabla EntregarTarea (vieja - simple)
    op.create_table(
        'EntregarTarea',
        sa.Column('entrega_tarea_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tarea_id', sa.UUID(), nullable=False),
        sa.Column('estudiante_id', sa.UUID(), nullable=False),
        sa.Column('fecha_entrega', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('archivo_entrega', sa.TEXT(), nullable=True),
        sa.Column('comentarios', sa.TEXT(), nullable=True),
        sa.Column('calificacion', sa.FLOAT(), nullable=True),
        sa.PrimaryKeyConstraint('entrega_tarea_id'),
        sa.ForeignKeyConstraint(['tarea_id'], ['Tarea.tarea_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['estudiante_id'], ['Estudiante.estudiante_id'], ondelete='CASCADE')
    )
    
    # Recrear tabla Mensaje (vieja - simple)
    op.create_table(
        'Mensaje',
        sa.Column('mensaje_id', sa.UUID(), nullable=False),
        sa.Column('chat_grupo_id', sa.UUID(), nullable=False),
        sa.Column('emisor_id', sa.UUID(), nullable=True),
        sa.Column('fecha_hora', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('tipo', sa.Enum('texto', 'imagen', 'archivo', 'link', name='tipo_mensaje'), nullable=False),
        sa.Column('contenido', sa.TEXT(), nullable=False),
        sa.PrimaryKeyConstraint('mensaje_id'),
        sa.ForeignKeyConstraint(['chat_grupo_id'], ['ChatGrupo.chat_grupo_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['emisor_id'], ['Usuario.usuario_id'], ondelete='SET NULL')
    )
    
    print("⚠️  Tablas duplicadas recreadas (VACÍAS):")
    print("   - Tarea (vieja) recreada")
    print("   - EntregarTarea (vieja) recreada")
    print("   - Mensaje (vieja) recreada")
