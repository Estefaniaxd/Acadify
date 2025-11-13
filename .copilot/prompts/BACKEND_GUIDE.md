# 🐍 Backend Guide - FastAPI + SQLAlchemy

> **Arquitectura Clean + Repository Pattern + Service Layer**

---

## 📂 ESTRUCTURA DETALLADA

```
backend/src/
├── main.py                 # 🚀 Entry point FastAPI
├── api/
│   ├── routes.py          # Router registry (lista central)
│   ├── deps.py            # Dependencies (get_db, get_current_user)
│   └── routes/            # Routers por dominio
│       ├── auth_main.py
│       ├── academic/
│       ├── gamification/
│       └── communication/
├── services/              # 🎯 Business logic layer
├── crud/                  # 💾 Data access layer (Repository)
├── models/                # 🗄️ SQLAlchemy models
├── schemas/               # 📋 Pydantic schemas
├── core/                  # ⚙️ Config, security, cache
├── db/                    # Database session
├── enums/                 # Python enums
└── utils/                 # Helper functions
```

---

## 🗄️ MODELOS SQLALCHEMY (PRINCIPALES)

### **Auth Domain** (`models/auth/`)

#### `usuario.py`
```python
class Usuario(Base):
    __tablename__ = "Usuario"
    
    # Primary Key
    usuario_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Auth fields
    nombre_usuario: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    contrasena_hash: Mapped[str]
    
    # Profile
    nombre: Mapped[str]
    apellido: Mapped[str]
    telefono: Mapped[str | None]
    avatar_url: Mapped[str | None]
    
    # Rol (enum)
    rol: Mapped[RolEnum] = mapped_column(default=RolEnum.ESTUDIANTE)
    
    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    
    # 2FA
    two_factor_enabled: Mapped[bool] = mapped_column(default=False)
    two_factor_secret: Mapped[str | None]
    
    # Institucional
    institucion_id: Mapped[UUID | None] = mapped_column(ForeignKey("Institucion.institucion_id"))
    
    # Timestamps
    fecha_creacion: Mapped[datetime] = mapped_column(default=func.now())
    fecha_actualizacion: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    ultimo_acceso: Mapped[datetime | None]
    
    # Relationships
    institucion: Mapped["Institucion"] = relationship(back_populates="usuarios")
    cursos_docente: Mapped[list["CursoDocente"]] = relationship(back_populates="docente")
    inscripciones: Mapped[list["Inscripcion"]] = relationship(back_populates="estudiante")
```

**Ubicación**: `backend/src/models/auth/usuario.py`

---

### **Academic Domain** (`models/academic/`)

#### Jerarquía: **Institución → Programa → Curso → Clase**

#### `institucion.py`
```python
class Institucion(Base):
    __tablename__ = "Institucion"
    
    institucion_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(index=True)
    sigla: Mapped[str | None]
    codigo: Mapped[str] = mapped_column(unique=True, index=True)
    
    # Tipo y nivel
    tipo_institucion: Mapped[TipoInstitucionEnum]
    nivel_educativo: Mapped[NivelEducativoEnum]
    sector: Mapped[SectorEnum]
    
    # Contacto
    email: Mapped[str | None]
    telefono: Mapped[str | None]
    sitio_web: Mapped[str | None]
    
    # Ubicación
    pais: Mapped[str | None]
    ciudad: Mapped[str | None]
    direccion: Mapped[str | None]
    
    # Branding
    logo_url: Mapped[str | None]
    color_primario: Mapped[str | None]
    color_secundario: Mapped[str | None]
    
    # Config
    usa_programas: Mapped[bool] = mapped_column(default=False)
    
    # Estado
    estado: Mapped[EstadoInstitucionEnum] = mapped_column(default=EstadoInstitucionEnum.PENDIENTE)
    
    # Timestamps
    fecha_creacion: Mapped[datetime] = mapped_column(default=func.now())
    fecha_activacion: Mapped[datetime | None]
    
    # Relationships
    programas: Mapped[list["Programa"]] = relationship(back_populates="institucion")
    cursos: Mapped[list["Curso"]] = relationship(back_populates="institucion")
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="institucion")
```

#### `programa.py`
```python
class Programa(Base):
    __tablename__ = "Programa"
    
    programa_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    institucion_id: Mapped[UUID] = mapped_column(ForeignKey("Institucion.institucion_id"))
    coordinador_id: Mapped[UUID | None] = mapped_column(ForeignKey("Usuario.usuario_id"))
    
    nombre: Mapped[str]
    codigo: Mapped[str] = mapped_column(unique=True)
    descripcion: Mapped[str | None]
    
    # Tipo y nivel
    nivel: Mapped[NivelProgramaEnum]  # pregrado, posgrado, tecnico
    tipo: Mapped[TipoProgramaEnum]    # presencial, virtual, hibrido
    
    # Duración
    duracion_semestres: Mapped[int | None]
    creditos_totales: Mapped[int | None]
    
    # Estado
    estado: Mapped[EstadoProgramaEnum] = mapped_column(default=EstadoProgramaEnum.ACTIVO)
    
    # Relationships
    institucion: Mapped["Institucion"] = relationship(back_populates="programas")
    coordinador: Mapped["Usuario"] = relationship()
    cursos: Mapped[list["Curso"]] = relationship(back_populates="programa")
```

#### `curso.py`
```python
class Curso(Base):
    __tablename__ = "Curso"
    
    curso_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    institucion_id: Mapped[UUID] = mapped_column(ForeignKey("Institucion.institucion_id"))
    programa_id: Mapped[UUID | None] = mapped_column(ForeignKey("Programa.programa_id"))
    
    nombre: Mapped[str]
    codigo_curso: Mapped[str] = mapped_column(unique=True)
    descripcion: Mapped[str | None]
    
    # Académico
    creditos: Mapped[int | None]
    horas_academicas: Mapped[int | None]
    nivel_dificultad: Mapped[NivelDificultadEnum | None]
    categoria: Mapped[CategoriaCursoEnum | None]
    
    # Modalidad
    modalidad: Mapped[ModalidadEnum]  # presencial, virtual, hibrido
    
    # Estado
    estado: Mapped[EstadoCursoEnum] = mapped_column(default=EstadoCursoEnum.BORRADOR)
    
    # Timestamps
    fecha_creacion: Mapped[datetime] = mapped_column(default=func.now())
    fecha_publicacion: Mapped[datetime | None]
    
    # Relationships
    institucion: Mapped["Institucion"] = relationship(back_populates="cursos")
    programa: Mapped["Programa"] = relationship(back_populates="cursos")
    grupos_curso: Mapped[list["GrupoCurso"]] = relationship(back_populates="curso")
    inscripciones: Mapped[list["Inscripcion"]] = relationship(back_populates="curso")
```

#### `clase.py`
```python
class Clase(Base):
    __tablename__ = "Clase"
    
    clase_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    grupo_id: Mapped[UUID] = mapped_column(ForeignKey("Grupo.grupo_id"))
    docente_id: Mapped[UUID | None] = mapped_column(ForeignKey("Usuario.usuario_id"))
    
    titulo: Mapped[str]
    descripcion: Mapped[str | None]
    contenido: Mapped[str | None]  # HTML o Markdown
    
    # Tipo y estado
    tipo_clase: Mapped[TipoClaseEnum]  # teoria, practica, evaluacion
    estado: Mapped[EstadoClaseEnum] = mapped_column(default=EstadoClaseEnum.PROGRAMADA)
    
    # Fechas
    fecha_inicio: Mapped[datetime | None]
    fecha_fin: Mapped[datetime | None]
    duracion_minutos: Mapped[int | None]
    
    # Acceso
    codigo_acceso: Mapped[str] = mapped_column(unique=True)
    requiere_inscripcion: Mapped[bool] = mapped_column(default=True)
    
    # Relationships
    grupo: Mapped["Grupo"] = relationship(back_populates="clases")
    docente: Mapped["Usuario"] = relationship()
    materiales: Mapped[list["MaterialEducativo"]] = relationship(back_populates="clase")
```

---

### **Gamification Domain** (`models/gamification/`)

#### `usuario_puntos.py`
```python
class UsuarioPuntos(Base):
    __tablename__ = "UsuarioPuntos"
    
    puntos_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("Usuario.usuario_id"))
    
    # Puntos
    puntos_totales: Mapped[int] = mapped_column(default=0)
    puntos_disponibles: Mapped[int] = mapped_column(default=0)  # No gastados
    puntos_gastados: Mapped[int] = mapped_column(default=0)
    
    # Nivel (calculado desde puntos_totales)
    nivel_actual: Mapped[int] = mapped_column(default=1)
    experiencia_siguiente_nivel: Mapped[int] = mapped_column(default=100)
    
    # Timestamps
    fecha_actualizacion: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    # Relationships
    usuario: Mapped["Usuario"] = relationship()
```

#### `racha_usuario.py`
```python
class RachaUsuario(Base):
    __tablename__ = "RachaUsuario"
    
    racha_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("Usuario.usuario_id"))
    
    # Racha actual
    dias_consecutivos: Mapped[int] = mapped_column(default=0)
    fecha_inicio_racha: Mapped[datetime | None]
    ultima_actividad: Mapped[datetime | None]
    
    # Histórico
    racha_maxima: Mapped[int] = mapped_column(default=0)
    total_dias_activos: Mapped[int] = mapped_column(default=0)
    
    # Estado
    racha_activa: Mapped[bool] = mapped_column(default=False)
    
    # Relationships
    usuario: Mapped["Usuario"] = relationship()
```

#### `logro.py`
```python
class Logro(Base):
    __tablename__ = "Logro"
    
    logro_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    nombre: Mapped[str]
    descripcion: Mapped[str]
    icono_url: Mapped[str | None]
    
    # Tipo y categoría
    tipo_logro: Mapped[TipoLogroEnum]  # bronce, plata, oro, platino
    categoria: Mapped[CategoriaLogroEnum]  # curso, racha, social, especial
    
    # Criterios
    criterio: Mapped[str]  # JSON con condiciones
    puntos_recompensa: Mapped[int] = mapped_column(default=0)
    
    # Visibilidad
    es_secreto: Mapped[bool] = mapped_column(default=False)
    es_activo: Mapped[bool] = mapped_column(default=True)
    
    # Relationships
    usuario_logros: Mapped[list["UsuarioLogro"]] = relationship(back_populates="logro")
```

---

## 🎯 SERVICES (BUSINESS LOGIC)

### **AuthService** (`services/auth/auth_service.py`)

**Responsabilidades:**
- Login (JWT + 2FA)
- Registro
- Refresh tokens
- Cambio de contraseña
- 2FA setup/verify

```python
class AuthService:
    def __init__(self, db: Session, redis_client: Redis):
        self.db = db
        self.redis = redis_client
    
    def login(
        self, 
        identifier: str, 
        password: str, 
        ip_address: str
    ) -> LoginResponse:
        """Autentica usuario y retorna tokens JWT.
        
        Flujo:
        1. Buscar usuario por username o email
        2. Validar contraseña (bcrypt)
        3. Verificar cuenta activa
        4. Si 2FA activado → retornar session_token temporal
        5. Si no 2FA → generar access_token + refresh_token
        6. Guardar refresh_token en Redis (TTL 30 días)
        7. Registrar login en log
        """
        # Buscar usuario
        user = crud.usuario.get_by_identifier(self.db, identifier)
        if not user:
            raise HTTPException(401, "Credenciales inválidas")
        
        # Verificar password
        if not verify_password(password, user.contrasena_hash):
            raise HTTPException(401, "Credenciales inválidas")
        
        # Verificar estado
        if not user.is_active:
            raise HTTPException(403, "Cuenta desactivada")
        
        # Si 2FA activado
        if user.two_factor_enabled:
            session_token = create_2fa_session_token(user.usuario_id)
            self.redis.setex(f"2fa_session:{session_token}", 300, user.usuario_id)
            return LoginResponse(
                requires_2fa=True,
                session_token=session_token
            )
        
        # Generar tokens
        access_token = create_access_token(data={"sub": str(user.usuario_id)})
        refresh_token = create_refresh_token()
        
        # Guardar refresh token en Redis
        self.redis.setex(
            f"refresh_token:{refresh_token}", 
            60 * 60 * 24 * 30,  # 30 días
            str(user.usuario_id)
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserProfile.from_orm(user)
        )
```

**Ubicación**: `backend/src/services/auth/auth_service.py`

---

### **InstitucionService** (`services/academic/institucion_service.py`)

**Métodos clave:**
```python
def crear_institucion(
    db: Session, 
    data: InstitucionCreate, 
    admin: Usuario
) -> Institucion:
    """Crea institución (solo admins).
    
    1. Validar permisos (rol admin)
    2. Validar código único
    3. Generar slug
    4. Crear registro
    5. Enviar email de bienvenida
    """

def obtener_estadisticas_institucion(
    db: Session,
    institucion_id: UUID,
    coordinador: Usuario
) -> dict:
    """Retorna estadísticas agregadas.
    
    Response:
    {
        "total_programas": 10,
        "total_cursos": 150,
        "total_docentes": 45,
        "total_estudiantes": 1200,
        "cursos_activos": 120,
        "programas_activos": 8
    }
    """
```

---

### **GamificacionService** (`services/gamificacion/gamificacion_service.py`)

```python
def otorgar_puntos(
    db: Session,
    usuario_id: UUID,
    cantidad: int,
    motivo: str,
    referencia_id: UUID | None = None
) -> UsuarioPuntos:
    """Otorga puntos al usuario.
    
    1. Obtener/crear UsuarioPuntos
    2. Sumar puntos
    3. Recalcular nivel si es necesario
    4. Registrar transacción
    5. Verificar logros desbloqueados
    6. Enviar notificación
    """

def actualizar_racha(
    db: Session,
    usuario_id: UUID
) -> RachaUsuario:
    """Actualiza racha diaria del usuario.
    
    Lógica:
    - Si última_actividad < 24h → incrementar días_consecutivos
    - Si última_actividad > 48h → resetear racha a 1
    - Actualizar racha_maxima si supera récord
    - Otorgar bonus de puntos si racha >= 7 días
    """

def verificar_logros(
    db: Session,
    usuario_id: UUID,
    evento: EventoGamificacion
) -> list[Logro]:
    """Verifica si el usuario desbloqueó logros.
    
    Criterios evaluados según evento:
    - "completar_tarea": 1/10/50/100 tareas
    - "racha_dias": 3/7/30/100 días consecutivos
    - "puntos_acumulados": 100/500/1000/5000 puntos
    - "primer_comentario", "primer_like", etc.
    """
```

---

## 💾 CRUD (DATA ACCESS LAYER)

### **Base CRUD** (`crud/base.py`)

```python
from typing import Generic, TypeVar
from sqlalchemy.orm import Session
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: UUID) -> ModelType | None:
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: UUID) -> bool:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
```

### **CRUDUsuario** (`crud/auth/crud_usuario.py`)

```python
class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    def get_by_email(self, db: Session, email: str) -> Usuario | None:
        return db.query(Usuario).filter(Usuario.email == email).first()
    
    def get_by_username(self, db: Session, username: str) -> Usuario | None:
        return db.query(Usuario).filter(Usuario.nombre_usuario == username).first()
    
    def get_by_identifier(self, db: Session, identifier: str) -> Usuario | None:
        """Busca por username O email."""
        return db.query(Usuario).filter(
            (Usuario.nombre_usuario == identifier) | (Usuario.email == identifier)
        ).first()
    
    def authenticate(self, db: Session, identifier: str, password: str) -> Usuario | None:
        user = self.get_by_identifier(db, identifier)
        if not user or not verify_password(password, user.contrasena_hash):
            return None
        return user

# Instancia singleton
usuario = CRUDUsuario(Usuario)
```

---

## 🛣️ ROUTERS (API ENDPOINTS)

### **Auth Router** (`api/routes/auth_main.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from src.api.deps import get_db, get_current_user
from src.services.auth.auth_service import AuthService

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
    ip: str = Depends(get_client_ip)
):
    """Login con username/email + password.
    
    Returns:
        - Si 2FA activado: { requires_2fa: true, session_token: "..." }
        - Si no 2FA: { access_token: "...", refresh_token: "..." }
    """
    auth_service = AuthService(db, redis_client)
    return auth_service.login(
        credentials.identifier,
        credentials.password,
        ip
    )

@router.post("/register", status_code=201, response_model=UserProfile)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Registro de nuevo usuario.
    
    1. Validar email único
    2. Validar username único
    3. Hash password
    4. Crear usuario
    5. Enviar email de verificación
    """

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Renueva access_token con refresh_token válido."""

@router.post("/logout")
def logout(
    refresh_token: str,
    current_user: Usuario = Depends(get_current_user)
):
    """Cierra sesión eliminando refresh_token de Redis."""

@router.get("/me", response_model=UserProfile)
def get_profile(
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna perfil del usuario autenticado."""

# 2FA Endpoints
@router.post("/2fa/setup")
def setup_2fa(current_user: Usuario = Depends(get_current_user)):
    """Genera secret TOTP y QR code."""

@router.post("/2fa/verify")
def verify_2fa(
    session_token: str,
    codigo: str,
    db: Session = Depends(get_db)
):
    """Verifica código 2FA y retorna tokens JWT."""

@router.post("/2fa/disable")
def disable_2fa(
    password: str,
    current_user: Usuario = Depends(get_current_user)
):
    """Desactiva 2FA (requiere contraseña)."""
```

**Ubicación**: `backend/src/api/routes/auth_main.py`

---

### **Instituciones Router** (`api/routes/academic/institucion.py`)

```python
@router.get("/mis-instituciones", response_model=list[InstitucionListItem])
def listar_mis_instituciones(
    incluir_estadisticas: bool = True,
    current_user: Usuario = Depends(require_coordinador)
):
    """Lista instituciones del coordinador actual.
    
    Query params:
        incluir_estadisticas: Si true, incluye total_cursos, total_estudiantes
    """

@router.get("/{institucion_id}/estadisticas")
def obtener_estadisticas(
    institucion_id: UUID,
    current_user: Usuario = Depends(require_coordinador)
):
    """Estadísticas completas de una institución."""

@router.post("/", response_model=Institucion, status_code=201)
def crear_institucion(
    data: InstitucionCreate,
    current_user: Usuario = Depends(require_admin)
):
    """Crea institución (solo admins)."""

@router.put("/{institucion_id}", response_model=Institucion)
def actualizar_institucion(
    institucion_id: UUID,
    data: InstitucionUpdate,
    current_user: Usuario = Depends(require_admin_or_coordinador)
):
    """Actualiza institución."""

@router.post("/{institucion_id}/invitar-coordinador")
def invitar_coordinador(
    institucion_id: UUID,
    email: str,
    current_user: Usuario = Depends(require_admin)
):
    """Invita coordinador por email (envía código de invitación)."""
```

---

## ⚙️ CORE (CONFIGURACIÓN)

### **Config** (`core/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost/db"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASS: str
    EMAIL_FROM: str
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Features
    ENABLE_2FA: bool = True
    ENABLE_GAMIFICATION: bool = True
    
    model_config = ConfigDict(env_file=".env")

settings = Settings()
```

---

## 🧪 TESTING

### **Test Structure** (`tests/`)

```
tests/
├── conftest.py           # Fixtures (db, client, users)
├── test_auth.py          # Tests de autenticación
├── test_instituciones.py
├── test_cursos.py
└── test_gamificacion.py
```

### **Example Test** (`test_auth.py`)

```python
import pytest
from fastapi.testclient import TestClient

def test_login_success(client: TestClient, test_user):
    response = client.post("/auth/login", json={
        "identifier": test_user.email,
        "password": "TestPassword123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_user):
    response = client.post("/auth/login", json={
        "identifier": test_user.email,
        "password": "WrongPassword"
    })
    assert response.status_code == 401
    assert "Credenciales inválidas" in response.json()["detail"]
```

---

## 📊 DATABASE OPERATIONS

### **Alembic Migrations**

```bash
# Crear migración automática
alembic revision --autogenerate -m "Add campo_nuevo to Usuario"

# Aplicar migraciones
alembic upgrade head

# Rollback
alembic downgrade -1

# Ver historial
alembic history --verbose
```

### **Manual Migration Example**

```python
# alembic/versions/xxx_add_racha_usuario.py

def upgrade():
    op.create_table(
        'RachaUsuario',
        sa.Column('racha_id', UUID(), primary_key=True),
        sa.Column('usuario_id', UUID(), ForeignKey('Usuario.usuario_id')),
        sa.Column('dias_consecutivos', sa.Integer(), default=0),
        sa.Column('fecha_inicio_racha', sa.DateTime()),
        sa.Column('ultima_actividad', sa.DateTime()),
        sa.Column('racha_maxima', sa.Integer(), default=0),
        sa.Column('racha_activa', sa.Boolean(), default=False)
    )
    op.create_index('ix_racha_usuario_id', 'RachaUsuario', ['usuario_id'])

def downgrade():
    op.drop_table('RachaUsuario')
```

---

## 🚀 DEPLOYMENT

### **Docker**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment Variables (Production)**

```bash
DATABASE_URL=postgresql://prod_user:secure_pass@db.example.com:5432/acadify_prod
REDIS_HOST=redis.example.com
SECRET_KEY=super-secure-random-key-min-64-chars
SMTP_HOST=smtp.sendgrid.net
SMTP_USER=apikey
SMTP_PASS=SG.xxx
FRONTEND_URL=https://acadify.example.com
```

---

## 📝 BEST PRACTICES

1. ✅ **Siempre usar transacciones** para operaciones multi-tabla
2. ✅ **Cachear queries pesados** en Redis (instituciones, estadísticas)
3. ✅ **Validar permisos** en cada endpoint (decorators)
4. ✅ **Type hints completos** en todas las funciones
5. ✅ **Docstrings** en servicios y endpoints complejos
6. ✅ **Logging estructurado** con contexto (user_id, request_id)
7. ✅ **Idempotencia** en endpoints críticos (crear con UUID del cliente)
8. ✅ **Rate limiting** en endpoints sensibles
9. ✅ **Tests unitarios** para servicios críticos (auth, gamificación)
10. ✅ **Migraciones reversibles** (siempre definir downgrade)

---

**Next**: Ver [FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md) para arquitectura del cliente.
