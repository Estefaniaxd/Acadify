# backend/app/main.py
"""
Aplicación principal de FastAPI para Acadify.
"""

import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import setup_logging, log_error
from app.api.api import api_router
from app.utils.exceptions import AcadifyException

# -------------------------------
# Configuración de logging
# -------------------------------
logger = setup_logging(logger_name="acadify")


# -------------------------------
# Crear instancia de FastAPI
# -------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url="/api/v1/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/api/v1/redoc" if settings.DEBUG else None,
)

# -------------------------------
# Middlewares
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para registrar todas las peticiones HTTP con tiempo de ejecución."""
    start_time = time.time()
    logger.info(f"INICIO | {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"FIN | {request.method} {request.url.path} | "
                f"Status: {response.status_code} | Tiempo: {process_time:.3f}s")
    return response

# -------------------------------
# Manejo global de excepciones
# -------------------------------
@app.exception_handler(AcadifyException)
async def acadify_exception_handler(request: Request, exc: AcadifyException):
    """Manejador para excepciones personalizadas de Acadify"""
    log_error(exc, f"Excepción personalizada en {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "code": exc.error_code,
            "detail": exc.detail
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Manejador para excepciones HTTP estándar"""
    log_error(exc, f"Excepción HTTP en {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "code": "HTTP_ERROR"
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador para errores de validación de datos"""
    log_error(exc, f"Error de validación en {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Error de validación de datos",
            "code": "VALIDATION_ERROR",
            "detail": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejador para errores no capturados"""
    log_error(exc, f"Error no manejado en {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Error interno del servidor",
            "code": "INTERNAL_ERROR"
        }
    )

# -------------------------------
# Eventos de inicio y cierre
# -------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info(f"Iniciando {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Modo debug: {settings.DEBUG}")
    logger.info("Aplicación iniciada correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Cerrando aplicación...")

# -------------------------------
# Endpoints públicos
# -------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de verificación del estado de la aplicación"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": time.time()
    }

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz de la aplicación"""
    return {
        "message": f"Bienvenido a {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/api/v1/docs" if settings.DEBUG else "Documentación no disponible en producción"
    }

# -------------------------------
# Incluir rutas de la API
# -------------------------------
# en app/api/v1/endpoints/user.py

app.include_router(api_router, prefix="/api/v1")
