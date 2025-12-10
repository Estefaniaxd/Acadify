
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Configurar pool de conexiones para load testing
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_timeout=60,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Export get_db for FastAPI dependency injection
from collections.abc import Generator
def get_db() -> Generator:
    """Dependency to get database session."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
