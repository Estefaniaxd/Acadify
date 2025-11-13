"""Configuración de pytest para tests de tareas.

Hereda fixtures del conftest principal de e2e.
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path para importar fixtures del e2e
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Importar fixtures del conftest principal (e2e)
from e2e.conftest import *  # noqa: F401, F403
