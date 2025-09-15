# Copilot Instructions for Acadify

## Arquitectura General
- El proyecto es monorepo con dos carpetas principales:
  - `acadify-frontend/`: React + TypeScript + Vite. UI y lógica de cliente.
  - `backend/`: FastAPI (Python), arquitectura modular, autenticación avanzada, integración con PostgreSQL y Redis.

## Backend (FastAPI)
- Entrypoint: `src/main.py`.
- Rutas principales: `src/api/routes/` (ej: `auth.py`, `usuario.py`).
- Dependencias y servicios: `src/services/`, organizados por dominio (ej: `auth/`, `usuario_service.py`).
- Modelos y esquemas: `src/models/`, `src/schemas/`.
- Configuración: `src/core/config.py` (usa Pydantic Settings, variables de entorno, propiedades para URLs de DB y Redis).
- Base de datos: SQLAlchemy, modelos en subcarpetas de `src/models/`, sesión en `src/db/session.py` y `src/db/base_session.py`.
- Redis: Cliente asíncrono, inicializado vía `RedisService` (`src/services/auth/redis_service.py`).
- Migraciones: Alembic (`alembic/`, `alembic.ini`).

## Frontend (React)
- Entrypoint: `src/main.tsx`.
- Páginas: `src/pages/`.
- Componentes: `src/components/`.
- Configuración Vite: `vite.config.ts`.

## Workflows y Comandos Clave
- Backend:
  - Ejecutar API: `uvicorn src.main:app --reload` (desde `backend/`).
  - Migraciones: `alembic upgrade head`.
  - Instalar dependencias: `pip install -r requirements.txt`.
- Frontend:
  - Ejecutar dev: `npm run dev` (desde `acadify-frontend/`).
  - Instalar dependencias: `npm install`.

## Convenciones y Patrones
- Importaciones absolutas desde `src.` en backend.
- Servicios y lógica de dominio en subcarpetas de `src/services/`.
- Uso de dependencias FastAPI para inyección de sesión DB, usuario actual, etc.
- Configuración centralizada en `src/core/config.py`.
- Los archivos vacíos en `db/` (`base_session.py`, `base_class.py`) deben exponer los objetos requeridos por los modelos y dependencias.
- Redis y email se usan para autenticación avanzada y notificaciones.

## Integraciones y Externos
- PostgreSQL (configurable en `.env` o variables de entorno).
- Redis (configurable en `.env` o variables de entorno).
- Email SMTP (configurable en `.env`).

## Ejemplo de patrón de dependencia
```python
from src.api.deps import get_db, get_current_user

@router.get("/me")
def get_profile(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    ...
```

## Notas
- Si agregas nuevos servicios, sigue la estructura de subcarpetas en `src/services/`.
- Si cambias la configuración, actualiza `src/core/config.py` y documenta en el README correspondiente.
- Para nuevas rutas, usa routers y dependencias como en los ejemplos existentes.
