# 🔧 Acadify Backend - Guía Técnica Detallada

## 🏗️ Arquitectura de Microservicios

### 📦 Estructura de Servicios

```
src/services/
├── auth/                    # Servicio de Autenticación
│   ├── auth_service.py     # Lógica principal de auth
│   ├── redis_service.py    # Gestión de Redis
│   ├── token_service.py    # Manejo de JWT
│   └── twofa_service.py    # Autenticación 2FA
├── email/                  # Servicio de Email
│   ├── email_service.py    # Envío de emails
│   └── templates/          # Plantillas HTML
├── usuario/                # Servicio de Usuarios
│   └── usuario_service.py  # Gestión de usuarios
└── security.py            # Utilidades de seguridad
```

### 🔄 Flujo de Datos

```mermaid
graph TB
    A[Cliente] --> B[FastAPI Router]
    B --> C[Dependency Injection]
    C --> D[Service Layer]
    D --> E[CRUD Layer]
    E --> F[SQLAlchemy ORM]
    F --> G[PostgreSQL]
    
    D --> H[Redis Cache]
    D --> I[Email Service]
    D --> J[Security Utils]
```

---

## 🔴 Redis - Implementación Detallada

### 🎯 ¿Por qué Redis en Acadify?

Redis es fundamental en nuestro sistema por las siguientes razones:

- **⚡ Velocidad**: Operaciones en microsegundos (datos en RAM)
- **🔄 Persistencia**: Snapshots y logs de transacciones (RDB + AOF)
- **📈 Escalabilidad**: Clustering y replicación master-slave
- **🛠️ Versatilidad**: Strings, Hashes, Lists, Sets, Sorted Sets
- **💾 Eficiencia**: Reduce carga en PostgreSQL

### 🎯 Configuración del Cliente Redis

```python
# src/services/auth/redis_service.py
import redis.asyncio as redis
from src.core.config import settings

class RedisService:
    def __init__(self):
        self.redis_client: redis.Redis = None
        self.connected = False
    
    async def connect(self):
        """Establecer conexión con Redis"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                max_connections=10
            )
            
            # Test de conexión
            await self.redis_client.ping()
            self.connected = True
            print(f"✅ Redis conectado: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
        except Exception as e:
            print(f"❌ Error conectando Redis: {e}")
            self.connected = False
    
    async def disconnect(self):
        """Cerrar conexión Redis"""
        if self.redis_client:
            await self.redis_client.aclose()
            self.connected = False
```

### 🔑 Casos de Uso de Redis

#### 1. 🎫 Gestión de Tokens JWT

```python
async def store_token(self, user_id: int, token: str, expiry: int):
    """Almacenar token JWT con expiración"""
    key = f"jwt_token:{user_id}:{token[-10:]}"
    await self.redis_client.setex(key, expiry, token)

async def invalidate_token(self, user_id: int, token: str):
    """Invalidar token (logout/blacklist)"""
    key = f"jwt_token:{user_id}:{token[-10:]}"
    await self.redis_client.delete(key)

async def is_token_valid(self, user_id: int, token: str) -> bool:
    """Verificar si token es válido"""
    key = f"jwt_token:{user_id}:{token[-10:]}"
    return await self.redis_client.exists(key)
```

#### 2. 🔐 Códigos OTP para 2FA

```python
async def store_otp(self, email: str, otp_code: str):
    """Almacenar código OTP por 5 minutos"""
    key = f"otp:{email}"
    await self.redis_client.setex(key, 300, otp_code)  # 5 min TTL

async def verify_otp(self, email: str, provided_otp: str) -> bool:
    """Verificar código OTP"""
    key = f"otp:{email}"
    stored_otp = await self.redis_client.get(key)
    
    if stored_otp and stored_otp == provided_otp:
        await self.redis_client.delete(key)  # Usar solo una vez
        return True
    return False
```

#### 3. 📊 Cache de Sesiones de Usuario

```python
async def store_user_session(self, user_id: int, session_data: dict):
    """Cache de datos de sesión"""
    key = f"user_session:{user_id}"
    await self.redis_client.hset(key, mapping=session_data)
    await self.redis_client.expire(key, 3600)  # 1 hora

async def get_user_session(self, user_id: int) -> dict:
    """Obtener datos de sesión"""
    key = f"user_session:{user_id}"
    return await self.redis_client.hgetall(key)
```

#### 4. ⏱️ Rate Limiting

```python
async def check_rate_limit(self, ip: str, limit: int = 5, window: int = 60) -> bool:
    """Verificar límite de requests por IP"""
    key = f"rate_limit:{ip}"
    current = await self.redis_client.get(key)
    
    if current is None:
        await self.redis_client.setex(key, window, 1)
        return True
    elif int(current) < limit:
        await self.redis_client.incr(key)
        return True
    else:
        return False  # Rate limit exceeded
```

---

## 🔒 Seguridad - Sistema Multicapa

### 🛡️ Autenticación JWT + Redis

```python
# src/services/auth/token_service.py
from jose import jwt, JWTError
from datetime import datetime, timedelta
from src.core.config import settings

class TokenService:
    def __init__(self, redis_service: RedisService):
        self.redis = redis_service
        
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        """Crear token de acceso JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        # Almacenar en Redis
        user_id = data.get("sub")
        expiry_seconds = int(expires_delta.total_seconds())
        asyncio.create_task(
            self.redis.store_token(user_id, encoded_jwt, expiry_seconds)
        )
        
        return encoded_jwt
    
    def create_refresh_token(self, data: dict):
        """Crear token de refresh (7 días)"""
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode = data.copy()
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(
            to_encode, 
            settings.REFRESH_SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
```

### 🔐 Hashing de Contraseñas

```python
# src/utils/security.py
import bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashear contraseña con bcrypt"""
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validar fortaleza de contraseña"""
    if len(password) < 8:
        return False, "Contraseña debe tener al menos 8 caracteres"
    
    if not any(c.isupper() for c in password):
        return False, "Contraseña debe contener al menos una mayúscula"
    
    if not any(c.islower() for c in password):
        return False, "Contraseña debe contener al menos una minúscula"
    
    if not any(c.isdigit() for c in password):
        return False, "Contraseña debe contener al menos un número"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Contraseña debe contener al menos un carácter especial"
    
    return True, "Contraseña válida"
```

### 🚨 Middleware de Seguridad

```python
# src/api/middleware/security.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # CORS Headers
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        
        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_service: RedisService):
        super().__init__(app)
        self.redis = redis_service
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        
        # Verificar rate limit
        if not await self.redis.check_rate_limit(client_ip, limit=100, window=60):
            raise HTTPException(
                status_code=429,
                detail="Demasiadas solicitudes. Intenta de nuevo en 1 minuto."
            )
        
        return await call_next(request)
```

---

## 📊 Base de Datos - Optimizaciones

### 🎯 Configuración de SQLAlchemy

```python
# src/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from src.core.config import settings

# Engine con pool de conexiones optimizado
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # Conexiones permanentes
    max_overflow=30,        # Conexiones adicionales
    pool_pre_ping=True,     # Verificar conexiones
    pool_recycle=3600,      # Reciclar cada hora
    echo=settings.DEBUG     # Logs SQL en desarrollo
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

### 🔍 Índices de Base de Datos

```python
# src/models/users/usuario.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Índices compuestos para consultas optimizadas
    __table_args__ = (
        Index('idx_usuario_email_active', 'email', 'is_active'),
        Index('idx_usuario_username_active', 'username', 'is_active'),
        Index('idx_usuario_created_active', 'created_at', 'is_active'),
    )
```

---

## 🚀 API Endpoints - Documentación

### 🔐 Endpoints de Autenticación

```python
# src/api/routes/auth_main.py
from fastapi import APIRouter, Depends, HTTPException
from src.schemas.auth import LoginRequest, LoginResponse, RegisterRequest

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
    redis: RedisService = Depends(get_redis)
):
    """
    Iniciar sesión con email/username y contraseña
    
    - **identifier**: Email o username del usuario
    - **password**: Contraseña del usuario
    - **otp_code**: Código 2FA (opcional)
    
    Retorna:
    - **access_token**: Token JWT para autenticación
    - **refresh_token**: Token para renovar sesión
    - **token_type**: Tipo de token (Bearer)
    - **user**: Datos básicos del usuario
    - **requires_2fa**: Si necesita verificación 2FA
    """

@router.post("/register", response_model=dict)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Registrar nuevo usuario
    
    - **email**: Email único del usuario
    - **username**: Username único del usuario  
    - **password**: Contraseña (mín. 8 caracteres)
    - **full_name**: Nombre completo del usuario
    """

@router.post("/logout")
async def logout(
    token: str = Depends(get_current_token),
    current_user: Usuario = Depends(get_current_user),
    redis: RedisService = Depends(get_redis)
):
    """
    Cerrar sesión e invalidar token
    """

@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    redis: RedisService = Depends(get_redis)
):
    """
    Renovar access token usando refresh token
    """
```

### 📝 Validación de Datos con Pydantic

```python
# src/schemas/auth/auth_schemas.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class LoginRequest(BaseModel):
    identifier: str  # Email o username
    password: str
    otp_code: Optional[str] = None
    
    @validator('identifier')
    def identifier_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('El identificador no puede estar vacío')
        return v.strip()
    
    @validator('password')
    def password_must_not_be_empty(cls, v):
        if not v or len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('El username solo puede contener letras y números')
        if len(v) < 3:
            raise ValueError('El username debe tener al menos 3 caracteres')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserBasic
    requires_2fa: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

---

## ⚙️ Configuración del Entorno

### 🔧 Variables de Entorno (.env)

```bash
# Base de datos PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/acadify_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=acadify_db
DB_USER=acadify_user
DB_PASSWORD=your_secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password

# JWT Tokens
SECRET_KEY=your_super_secret_jwt_key_here_make_it_long_and_random
REFRESH_SECRET_KEY=your_refresh_token_secret_key_different_from_access
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=acadify@example.com

# Aplicación
APP_NAME=Acadify
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://acadify.com

# Seguridad
RATE_LIMIT_PER_MINUTE=60
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=15
```

### 🎛️ Configuración Centralizada

```python
# src/core/config.py
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Acadify Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "acadify_db"
    DB_USER: str
    DB_PASSWORD: str
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # JWT
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email
    SMTP_SERVER: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Security
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def redis_url(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## 🧪 Testing y Calidad de Código

### 🎯 Tests Unitarios

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.services.auth.redis_service import RedisService

client = TestClient(app)

@pytest.fixture
def mock_redis():
    return RedisService()

def test_login_successful():
    """Test login exitoso"""
    response = client.post("/auth/login", json={
        "identifier": "test@example.com",
        "password": "TestPassword123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login con credenciales incorrectas"""
    response = client.post("/auth/login", json={
        "identifier": "test@example.com",
        "password": "wrong_password"
    })
    assert response.status_code == 401
    assert "Credenciales incorrectas" in response.json()["detail"]

def test_register_new_user():
    """Test registro de nuevo usuario"""
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser123",
        "password": "SecurePass123!",
        "full_name": "New User"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "Usuario registrado exitosamente"
```

### 📊 Cobertura de Código

```bash
# Ejecutar tests con cobertura
pip install pytest pytest-cov
pytest --cov=src --cov-report=html --cov-report=term

# Ver reporte en HTML
open htmlcov/index.html
```

---

## 🚀 Deployment y DevOps

### 🐳 Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://acadify:password@postgres:5432/acadify_db
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: acadify_db
      POSTGRES_USER: acadify
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

volumes:
  postgres_data:
  redis_data:
```

### ☁️ Deployment en Producción

```bash
# 1. Preparar servidor
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose nginx certbot python3-certbot-nginx

# 2. Clonar repositorio
git clone https://github.com/tu-usuario/acadify.git
cd acadify/backend

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con valores de producción

# 4. Construir y ejecutar
docker-compose up -d --build

# 5. Configurar Nginx (reverse proxy)
sudo nano /etc/nginx/sites-available/acadify
```

```nginx
# /etc/nginx/sites-available/acadify
server {
    listen 80;
    server_name api.acadify.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activar sitio y SSL
sudo ln -s /etc/nginx/sites-available/acadify /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d api.acadify.com
```

---

## 📝 Comandos de Desarrollo

### 🔄 Gestión de Base de Datos

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1

# Verificar estado
alembic current
alembic history

# Poblar datos iniciales
python scripts/seed_database.py
```

### 🏃‍♂️ Comandos de Ejecución

```bash
# Desarrollo local
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Producción
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Con logging
uvicorn src.main:app --log-config logging.conf

# Tests
pytest -v
pytest tests/test_auth.py -v

# Linting
flake8 src/
black src/
isort src/

# Análisis de seguridad
bandit -r src/
safety check
```

### 📊 Monitoreo y Logs

```python
# src/core/logging.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configurar logging estructurado"""
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    
    return logger

# Uso en endpoints
logger = setup_logging()

@router.post("/login")
async def login(request: LoginRequest):
    logger.info("Login attempt", extra={
        "identifier": request.identifier,
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent")
    })
```

---

## 🤝 Contribución y Estándares

### 📋 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
```

### 🎯 Estándares de Código

```python
# Ejemplo de función bien documentada
async def authenticate_user(
    db: Session, 
    identifier: str, 
    password: str,
    redis: RedisService
) -> tuple[Usuario | None, bool]:
    """
    Autenticar usuario por email/username y contraseña.
    
    Args:
        db: Sesión de base de datos SQLAlchemy
        identifier: Email o username del usuario
        password: Contraseña en texto plano
        redis: Servicio Redis para rate limiting
        
    Returns:
        tuple: (Usuario autenticado o None, requiere_2fa)
        
    Raises:
        HTTPException: Si las credenciales son incorrectas
        
    Example:
        >>> user, needs_2fa = await authenticate_user(db, "user@example.com", "password", redis)
        >>> if user:
        ...     print(f"Usuario {user.email} autenticado")
    """
    
    # Rate limiting por IP
    client_ip = "192.168.1.1"  # Obtener IP real
    if not await redis.check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos de login"
        )
    
    # Buscar usuario por email o username
    user = db.query(Usuario).filter(
        or_(
            Usuario.email == identifier.lower(),
            Usuario.username == identifier.lower()
        )
    ).first()
    
    if not user or not verify_password(password, user.hashed_password):
        logger.warning(f"Login fallido para: {identifier}")
        return None, False
    
    # Verificar si tiene 2FA habilitado
    requires_2fa = user.two_factor_enabled
    
    logger.info(f"Usuario autenticado: {user.email}")
    return user, requires_2fa
```

---

Este README proporciona una guía técnica completa del backend de Acadify, incluyendo implementación de Redis, seguridad, API endpoints, configuración y deployment. El sistema está diseñado para ser escalable, seguro y mantenible. 🚀