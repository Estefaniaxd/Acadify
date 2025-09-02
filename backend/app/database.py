# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
import os

# Leer variables de entorno
user = os.getenv("DATABASE_USER", "postgres")
password = os.getenv("DATABASE_PASSWORD", "243019")
host = os.getenv("DATABASE_HOST", "localhost")
port = os.getenv("DATABASE_PORT", 5432)
db_name = os.getenv("DATABASE_NAME", "acadify_new")

# Construir URL de conexión, escapando caracteres especiales
DATABASE_URL = f"postgresql://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{db_name}"

# Crear engine con UTF-8 forzado
engine = create_engine(
    DATABASE_URL,
    connect_args={"client_encoding": "utf8"},
    pool_pre_ping=True,
    echo=True  # Para ver los logs de SQL
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base
Base = declarative_base()
