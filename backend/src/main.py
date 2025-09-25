from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import sys
import os
from pathlib import Path

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

# Configurar archivos estáticos para avatars
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"📁 Archivos estáticos montados en /static desde {static_dir}")
else:
    logger.warning(f"⚠️ Directorio de archivos estáticos no encontrado: {static_dir}")

# Configuración CORS más permisiva para desarrollo
cors_origins = settings.BACKEND_CORS_ORIGINS
if not cors_origins:
    # Si no hay orígenes configurados, usar los más comunes para desarrollo
    cors_origins = [
        "http://localhost:3000",      # Create React App default
        "http://localhost:5173",      # Vite default 
        "http://localhost:5174",      # Vite alternative
        "http://127.0.0.1:5173",      # Localhost variante
        "http://localhost:8080",      # Vue/otros
    ]
else:
    # Convertir URLs de Pydantic a strings sin barras finales
    cors_origins = [str(url).rstrip('/') for url in cors_origins]

logger.info(f"🌐 CORS Origins configurados: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Servicio Redis
redis_service = RedisService()

# Ruta completa para avatars con composición de imágenes
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.api.routes.avatar_service_complete import router as avatar_complete_router
app.include_router(avatar_complete_router, prefix="/avatar", tags=["avatars-complete"])

# Incluir todos los routers desde el archivo de configuración EXCEPTO el avatar router que puede causar conflictos
for router, prefix, tags in routers:
    # Saltar el router de avatar porque ya incluimos avatar_service_complete
    if prefix != "/avatar":
        app.include_router(router, prefix=prefix, tags=tags)

# Handler específico para peticiones OPTIONS (CORS preflight)
@app.options("/{path:path}")
async def options_handler(path: str):
    """Maneja las peticiones OPTIONS para CORS preflight"""
    return {"message": "OK"}

# Ruta raíz con información del sistema
@app.get("/")
def root():
    return {
        "message": "Acadify API 🚀",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "cors_origins": cors_origins,  # Mostrar orígenes CORS configurados
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
