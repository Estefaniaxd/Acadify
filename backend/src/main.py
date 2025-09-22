from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("api_debug.log")
    ]
)

# Reducir logs de bibliotecas externas para una consola más limpia
logging.getLogger("passlib").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)  # Solo errores críticos
logging.getLogger("sqlalchemy.pool").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.orm").setLevel(logging.ERROR)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

# Crear logger específico para la aplicación
logger = logging.getLogger("acadify-api")

# Importa los routers
from src.api.routes import routers
from src.services.auth.redis_service import RedisService
from src.core.config import settings

# Inicializa la app FastAPI
app = FastAPI(
    title="Acadify API",
    description="API para autenticación y gestión de usuarios en Acadify",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuración CORS (ajusta origins con tu frontend real)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],  # Usa la lista de orígenes permitidos o permite todos por defecto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servicio Redis
redis_service = RedisService()

# Incluir todos los routers desde el archivo de configuración
for router, prefix, tags in routers:
    app.include_router(router, prefix=prefix, tags=tags)

# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    try:
        redis_service.connect()
        logger.info("🚀 Acadify API iniciada exitosamente")
        logger.info("📚 Documentación disponible en: http://127.0.0.1:8000/docs")
        logger.info("🔐 Endpoints de autenticación reorganizados y optimizados")
        
        # Información del sistema
        import platform
        import sys
        logger.debug(f"Python: {sys.version}")
        logger.debug(f"Platform: {platform.platform()}")
        logger.debug(f"Redis host: {settings.REDIS_HOST}")
        logger.debug(f"Redis port: {settings.REDIS_PORT}")
        logger.debug(f"CORS origins: {settings.BACKEND_CORS_ORIGINS}")
        logger.debug(f"JWT Algorithm: {settings.ALGORITHM}")
        logger.debug(f"Access token expire minutes: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
        
    except Exception as e:
        logger.error(f"Error en startup: {e}")
        raise e


@app.on_event("shutdown")
async def shutdown_event():
    redis_service.disconnect()
    print("👋 Acadify API desconectada")


# Ruta raíz con información del sistema
@app.get("/")
def root():
    return {
        "message": "Acadify API 🚀",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "auth": {
            "endpoints_reorganized": True,
            "new_structure": {
                "core": "/auth (login, register, logout, profile)",
                "passwords": "/auth/forgot-password, /auth/reset-password, /auth/change-password", 
                "2fa": "/auth/2fa/* (setup, verify, disable, status)",
                "admin_users": "/auth/users/* (CRUD operations)",
                "account_mgmt": "/auth/users/{id}/* (activate, deactivate, unlock)",
                "health": "/auth/health"
            }
        }
    }
