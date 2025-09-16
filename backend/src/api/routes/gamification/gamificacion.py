# main.py o routers/gamification.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importa tus funciones CRUD y esquemas
from backend.src.schemas.gamification import (
    recompensa as schemas_recompensas,
    tema as schemas_temas,
)
from backend.src.crud.gamification import historial_puntos as crud_puntos
from src.crud.gamification import insignias as crud_insignias
from src.crud.gamification import recompensas as crud_recompensas
from backend.src.crud.gamification import tema as crud_temas
from src.schemas.gamification import (
    puntos as schemas_puntos,
    insignias as schemas_insignias,
)

# Asume que ya tienes una dependencia para la sesión de DB
from src.db.session import get_db

# Asume que ya tienes un módulo de autenticación con una dependencia
# para obtener el usuario actual a partir del token JWT
from src.api.dependencies import get_current_user
from src.models.users.usuario import Usuario


from .temas import router as temas_router
from .puntos import router as puntos_router
from .insignias import router as insignias_router
from .recompensas import router as recompensas_router
