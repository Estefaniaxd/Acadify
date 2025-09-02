# alembic/env.py (fragmento clave)
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
from backend.app.models.models import Base  # <- importa tu Base

config = context.config
fileConfig(config.config_file_name)

# usa la URL de entorno si existe
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata
