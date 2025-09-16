from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.gamification import gamificacion as gamificacion_router

from src.services.auth.redis_service import RedisService
from src.core.config import settings

# Inicializa la app FastAPI
app = FastAPI(
    title="Acadify API",
    description="API para autenticación y gestión de usuarios en Acadify",
    version="1.0.0",
)

# Configuración CORS (ajusta origins con tu frontend real)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # Ej: "http://localhost:3000"
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


@app.on_event("shutdown")
async def shutdown_event():
    await redis_service.disconnect()


# Ruta raíz (opcional)
@app.get("/")
def root():
    return {"message": "Hello Acadify 🚀"}
