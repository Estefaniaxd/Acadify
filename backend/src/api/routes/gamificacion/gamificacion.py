# main.py o routers/gamificacion.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importa tus funciones CRUD y esquemas
from src.crud.gamificacion import puntos as crud_puntos
from src.crud.gamificacion import insignias as crud_insignias
from src.crud.gamificacion import recompensas as crud_recompensas
from src.crud.gamificacion import temas as crud_temas
from src.schemas.gamificacion import (
    puntos as schemas_puntos,
    insignias as schemas_insignias,
    recompensas as schemas_recompensas,
    temas as schemas_temas,
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

router = APIRouter()
router.include_router(temas_router, prefix="/temas", tags=["Temas"])
router.include_router(puntos_router, prefix="/puntos", tags=["Puntos"])
router.include_router(insignias_router, prefix="/insignias", tags=["Insignias"])
router.include_router(recompensas_router, prefix="/recompensas", tags=["Recompensas"])