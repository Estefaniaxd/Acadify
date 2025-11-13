import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.begin() as conn:
    conn.execute(text('ALTER TABLE eventos_audio RENAME COLUMN metadata TO datos_adicionales'))
print('✅ Columna renombrada exitosamente')
