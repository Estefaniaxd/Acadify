from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings


# Configurar pool de conexiones para load testing
# pool_size: conexiones permanentes
# max_overflow: conexiones temporales adicionales
# pool_timeout: tiempo de espera para obtener conexión
# pool_recycle: reciclar conexiones cada X segundos (evitar conexiones muertas)
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_size=20,  # Aumentado de 5 a 20
    max_overflow=40,  # Aumentado de 10 a 40
    pool_timeout=60,  # Aumentado de 30 a 60 segundos
    pool_recycle=3600,  # Reciclar cada hora
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
