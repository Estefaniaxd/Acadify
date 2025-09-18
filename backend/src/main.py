from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa los routers
from src.api.routes import auth_main, usuario
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

# Importar rutas

from src.api import routes

for router, prefix, tags in routes.routers:
    app.include_router(router, prefix=prefix, tags=tags)

# Servicio Redis
redis_service = RedisService()


# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    await redis_service.connect()
    print("🚀 Acadify API iniciada exitosamente")
    print("📚 Documentación disponible en: http://127.0.0.1:8000/docs")
    print("🔐 Endpoints de autenticación reorganizados y optimizados")


@app.on_event("shutdown")
async def shutdown_event():
    await redis_service.disconnect()
    print("👋 Acadify API desconectada")


# Incluir routers organizados
app.include_router(auth_main.router)  # Nuevo router organizado por funcionalidad
app.include_router(usuario.router)


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
