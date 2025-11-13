#!/usr/bin/env python3
"""Script rápido para verificar columnas del modelo Clase"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect
from src.db.base_class import Base

# Importar el modelo
from src.models.academic.clase import Clase

# Usar el inspector de SQLAlchemy
mapper = inspect(Clase)
columns = [col.key for col in mapper.columns]

print(f"Columnas detectadas en modelo Clase: {len(columns)}")
for col in sorted(columns):
    print(f"  - {col}")
