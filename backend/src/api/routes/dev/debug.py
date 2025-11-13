import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
import redis.asyncio as redis
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, get_db, get_redis_client
from src.models.users.usuario import Usuario
from src.utils.security import security_manager


logger = logging.getLogger("auth-debug")

router = APIRouter(prefix="/debug", tags=["Depuración"])
security = HTTPBearer()


class TokenInfoResponse(BaseModel):
    token_valid: bool
    token_details: dict[str, Any] | None = None
    error_message: str | None = None
    user_id: str | None = None
    roles: list | None = None


@router.get("/token-info", response_model=TokenInfoResponse)
async def get_token_info(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        HTTPBearer(auto_error=False)
    ),
):
    """Analiza y devuelve información sobre el token JWT proporcionado.
    Útil para depurar problemas de autenticación.
    """
    response = TokenInfoResponse(token_valid=False)

    # Log de todas las cabeceras para depuración
    headers_dict = dict(request.headers.items())
    auth_header = headers_dict.get("authorization", "No hay header de autorización")
    logger.debug(f"Headers recibidos: {json.dumps(headers_dict, indent=2)}")
    logger.debug(f"Header de autorización: {auth_header}")

    if not credentials:
        response.error_message = "No se proporcionó token. Asegúrate de incluir el header 'Authorization: Bearer <token>'"
        return response

    token = credentials.credentials
    logger.debug(
        f"Token recibido (primeros 15 caracteres): {token[:15] if token else 'None'}..."
    )

    try:
        # Verificar formato básico
        if not token:
            response.error_message = "Token vacío"
            return response

        token_parts = token.split(".")
        if len(token_parts) != 3:
            response.error_message = f"Formato de token inválido: Se esperan 3 partes, se encontraron {len(token_parts)}"
            return response

        # Intentar decodificar el token
        payload = security_manager.decode_token(token)

        # Si llegamos aquí, el token es válido
        response.token_valid = True
        response.token_details = payload
        response.user_id = payload.get("sub")
        response.roles = payload.get("roles", [])

        return response
    except Exception as e:
        response.error_message = f"Error al decodificar token: {e!s}"
        logger.exception(f"Error de token: {e!s}")
        return response


@router.get("/auth-test")
async def auth_test(request: Request, user: Usuario = Depends(get_current_user)):
    """Endpoint de prueba que requiere autenticación.
    Devuelve información básica del usuario autenticado.
    """
    # Log de todas las cabeceras para depuración
    headers_dict = dict(request.headers.items())

    return {
        "message": "Autenticación exitosa",
        "user_id": str(user.usuario_id),
        "rol": user.rol.value,
        "headers_received": headers_dict,
    }


@router.get("/health-check")
async def health_check(
    db: Session = Depends(get_db), redis_client: redis.Redis = Depends(get_redis_client)
):
    """Verifica la salud de las conexiones a la base de datos y Redis."""
    health_status = {
        "status": "healthy",
        "components": {"database": "unknown", "redis": "unknown"},
        "details": {},
    }

    # Verificar base de datos
    try:
        # Ejecutar una consulta simple
        db.execute("SELECT 1").fetchall()
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = "unhealthy"
        health_status["details"]["database_error"] = str(e)
        health_status["status"] = "degraded"

    # Verificar Redis
    try:
        await redis_client.ping()
        health_status["components"]["redis"] = "healthy"
    except Exception as e:
        health_status["components"]["redis"] = "unhealthy"
        health_status["details"]["redis_error"] = str(e)
        health_status["status"] = "degraded"

    # Si algún componente está degradado, el status general es degraded
    if any(status == "unhealthy" for status in health_status["components"].values()):
        health_status["status"] = "degraded"

    return health_status
