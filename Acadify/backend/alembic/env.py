# alembic/env.py

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


# Importa tu Base de modelos y todos los modelos para que Alembic los detecte
from src.db.base_class import Base
import src.models  # Esto importa todos los modelos gracias a __init__.py

# Configuración Alembic
config = context.config

# Configuración del archivo de log
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata que Alembic usará para generar migraciones
target_metadata = Base.metadata

# Conexión a la base de datos desde .env
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("La variable DATABASE_URL no está definida en .env")

def run_migrations_offline():
    """Ejecuta migraciones en modo offline."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Ejecuta migraciones en modo online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=DATABASE_URL
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
