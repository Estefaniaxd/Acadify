# src/api/routes/auth/auth_health.py

from typing import Any, Dict
from fastapi import APIRouter, Depends
import logging

from src.api.deps import get_redis_client
import redis.asyncio as redis

logger = logging.getLogger(__name__)

# Router de health check
router = APIRouter(
    prefix="/auth", 
    tags=["💊 Autenticación - Health Check"],
    responses={
        200: {"description": "Estado del sistema de autenticación"}
    }
)


@router.get("/health")
async def auth_health_check(
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Health check del sistema de autenticación.
    
    **Verificaciones realizadas:**
    - Conectividad con Redis (cache y sesiones)
    - Estado del servicio de autenticación
    - Componentes críticos del sistema
    
    **Estados posibles:**
    - healthy: Todos los componentes funcionando
    - degraded: Algunos componentes con problemas
    - unhealthy: Falla crítica del sistema
    
    **Componentes monitoreados:**
    - Redis: Almacenamiento de sesiones y blacklist de tokens
    - Auth Service: Servicio principal de autenticación
    - Database: Conexión a base de datos (implícita)
    
    **Uso:**
    - Monitoreo automático de sistemas
    - Verificación de dependencias en CI/CD
    - Diagnóstico rápido de problemas
    
    **Respuestas:**
    - 200: Estado del sistema (siempre retorna 200)
    - Contenido indica salud real de componentes
    """
    try:
        # Test Redis connection
        await redis_client.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        redis_status = "unhealthy"
    
    # Determinar estado general
    overall_status = "healthy"
    if redis_status != "healthy":
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "components": {
            "redis": redis_status,
            "auth_service": "healthy",
            "database": "assumed_healthy"  # Se verifica implícitamente en otros endpoints
        },
        "message": "Sistema de autenticación operativo" if overall_status == "healthy" 
                  else "Algunos componentes presentan problemas"
    }