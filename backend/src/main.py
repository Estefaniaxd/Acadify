from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa los routers existentes
from src.api.routes import auth, usuario

# Importa routers del módulo academic
from src.api.routes.academic import (
    institucion,
    programa,
    curso,
    curso_docente,
    grupo,
    grupo_curso,
    estudiante_grupo,
    material_educativo,
    material_clase,
    material_curso,
)

from src.services.auth.redis_service import RedisService
from src.core.config import settings

# Inicializa la app FastAPI
app = FastAPI(
    title="Acadify API",
    description="API para autenticación y gestión de usuarios en Acadify",
    version="1.0.0"
)

# Configuración CORS (ajusta origins con tu frontend real)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # Ej: "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servicio Redis
redis_service = RedisService()

# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    await redis_service.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await redis_service.disconnect()

# Incluir routers existentes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(usuario.router, prefix="/usuarios", tags=["Usuarios"])

# Incluir routers del módulo academic
app.include_router(institucion.router, prefix="/instituciones", tags=["Instituciones"])
app.include_router(programa.router, prefix="/programas", tags=["Programas"])
app.include_router(curso.router, prefix="/cursos", tags=["Cursos"])
app.include_router(curso_docente.router, prefix="/curso-docentes", tags=["Curso-Docentes"])
app.include_router(grupo.router, prefix="/grupos", tags=["Grupos"])
app.include_router(grupo_curso.router, prefix="/grupo-cursos", tags=["Grupo-Cursos"])
app.include_router(estudiante_grupo.router, prefix="/estudiante-grupos", tags=["Estudiante-Grupos"])
app.include_router(material_educativo.router, prefix="/material-educativo", tags=["Material Educativo"])
app.include_router(material_clase.router, prefix="/material-clases", tags=["Material-Clases"])
app.include_router(material_curso.router, prefix="/material-cursos", tags=["Material-Cursos"])

# Ruta raíz (opcional)
@app.get("/")
def root():
    return {"message": "Hello Acadify 🚀"}
