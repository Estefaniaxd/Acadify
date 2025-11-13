# 📁 Estructura del Proyecto Acadify Backend

## 📋 Índice
1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura de Carpetas Detallada](#estructura-de-carpetas-detallada)
4. [Patrones de Diseño](#patrones-de-diseño)
5. [Convenciones de Nomenclatura](#convenciones-de-nomenclatura)
6. [Flujo de Datos](#flujo-de-datos)

---

## 🎯 Visión General

**Acadify Backend** es una plataforma educativa completa construida con **FastAPI** que implementa una arquitectura en capas limpia y escalable. El sistema sigue los principios de **Clean Architecture** y **Domain-Driven Design (DDD)**.

### Tecnologías Principales
- **Framework:** FastAPI 0.104+
- **Base de Datos:** PostgreSQL
- **ORM:** SQLAlchemy 2.0+
- **Migraciones:** Alembic
- **Validación:** Pydantic V2
- **Autenticación:** JWT (JSON Web Tokens)
- **Testing:** Pytest
- **Documentación:** Swagger/OpenAPI automática

### Características Principales
- ✅ Sistema de autenticación y autorización basado en roles
- ✅ Gestión académica completa (cursos, tareas, calificaciones)
- ✅ Sistema de gamificación (puntos, insignias, rachas, tienda)
- ✅ Comunicación en tiempo real (mensajes, notificaciones)
- ✅ Sistema de evaluaciones con IA integrada
- ✅ Panel de administración para gestión de contenido
- ✅ Avatar personalizable con sistema de items

---

## 🏗️ Arquitectura del Sistema

### Tipo de Arquitectura: **Layered Architecture (Clean Architecture)**

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                    (API Endpoints/Routes)                    │
│                         FastAPI                              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                        │
│                   (Business Logic/Services)                  │
│              Orquestación de Casos de Uso                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                            │
│              (Models, Schemas, Enums, Utils)                 │
│                  Reglas de Negocio                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                       │
│            (Database, CRUD, External Services)               │
│                    PostgreSQL + SQLAlchemy                   │
└─────────────────────────────────────────────────────────────┘
```

### Principios Aplicados

1. **Separation of Concerns (SoC)**: Cada capa tiene una responsabilidad única
2. **Dependency Inversion**: Las capas superiores no dependen de las inferiores
3. **Single Responsibility**: Cada módulo tiene una única razón para cambiar
4. **DRY (Don't Repeat Yourself)**: Código reutilizable y modular
5. **SOLID Principles**: Aplicados en toda la arquitectura

---

## 📂 Estructura de Carpetas Detallada

```
backend/
│
├── 📁 src/                          # Código fuente principal
│   ├── 📄 main.py                   # Punto de entrada de la aplicación
│   ├── 📄 __init__.py
│   │
│   ├── 📁 api/                      # CAPA DE PRESENTACIÓN
│   │   ├── 📁 v1/                   # Versión 1 de la API
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📁 endpoints/        # Endpoints organizados por dominio
│   │   │   │   ├── 📁 admin/        # Endpoints administrativos
│   │   │   │   │   ├── tienda_admin.py      # Admin: Gestión tienda
│   │   │   │   │   ├── badges_admin.py      # Admin: Gestión badges
│   │   │   │   │   └── users_admin.py       # Admin: Gestión usuarios
│   │   │   │   │
│   │   │   │   ├── 📁 gamification/ # Endpoints gamificación
│   │   │   │   │   ├── tienda.py            # Tienda de items
│   │   │   │   │   ├── puntos.py            # Sistema de puntos
│   │   │   │   │   ├── insignias.py         # Badges/insignias
│   │   │   │   │   └── racha.py             # Sistema de rachas
│   │   │   │   │
│   │   │   │   └── 📄 ...
│   │   │   │
│   │   │   └── 📄 api.py            # Router principal v1
│   │   │
│   │   └── 📁 routes/               # Routes legacy (en migración)
│   │       ├── 📁 auth/             # Autenticación
│   │       ├── 📁 users/            # Usuarios
│   │       ├── 📁 academic/         # Sistema académico
│   │       │   ├── cursos.py        # Gestión cursos
│   │       │   ├── inscripciones.py # Inscripciones
│   │       │   ├── curso_comentarios.py
│   │       │   ├── curso_tareas.py
│   │       │   └── curso_archivos.py
│   │       │
│   │       ├── 📁 evaluaciones/     # Evaluaciones/exámenes
│   │       ├── 📁 communication/    # Mensajes/notificaciones
│   │       └── 📁 dev/              # Herramientas desarrollo
│   │
│   ├── 📁 services/                 # CAPA DE APLICACIÓN (Lógica de Negocio)
│   │   ├── 📁 auth/                 # Servicios autenticación
│   │   │   ├── auth_service.py
│   │   │   └── token_service.py
│   │   │
│   │   ├── 📁 users/                # Servicios usuarios
│   │   │   └── user_service.py
│   │   │
│   │   ├── 📁 academic/             # Servicios académicos
│   │   │   ├── curso_service.py
│   │   │   ├── tarea_service.py
│   │   │   └── calificacion_service.py
│   │   │
│   │   ├── 📁 gamification/         # Servicios gamificación
│   │   │   ├── puntos_service.py    # Gestión puntos
│   │   │   ├── tienda_service.py    # Lógica tienda
│   │   │   ├── insignias_service.py # Lógica badges
│   │   │   ├── racha_service.py     # Lógica rachas
│   │   │   └── avatar_service.py    # Lógica avatar
│   │   │
│   │   ├── 📁 evaluaciones/         # Servicios evaluaciones
│   │   ├── 📁 communication/        # Servicios comunicación
│   │   └── 📁 ai/                   # Servicios IA
│   │       ├── ai_service.py
│   │       └── 📁 helpers/
│   │
│   ├── 📁 models/                   # CAPA DE DOMINIO (Modelos ORM)
│   │   ├── 📄 __init__.py
│   │   │
│   │   ├── 📁 users/                # Modelos usuarios
│   │   │   ├── usuario.py
│   │   │   └── perfil.py
│   │   │
│   │   ├── 📁 auth/                 # Modelos autenticación
│   │   │   └── refresh_token.py
│   │   │
│   │   ├── 📁 academic/             # Modelos académicos
│   │   │   ├── curso.py
│   │   │   ├── tarea.py
│   │   │   ├── entrega.py
│   │   │   └── calificacion.py
│   │   │
│   │   ├── 📁 gamification/         # Modelos gamificación
│   │   │   ├── puntos_usuario.py
│   │   │   ├── tienda_item.py
│   │   │   ├── inventario_item.py
│   │   │   ├── transaccion_tienda.py
│   │   │   ├── insignia.py
│   │   │   ├── insignia_usuario.py
│   │   │   ├── racha_usuario.py
│   │   │   └── hito_racha.py
│   │   │
│   │   ├── 📁 avatar/               # Modelos avatar
│   │   ├── 📁 evaluaciones/         # Modelos evaluaciones
│   │   ├── 📁 communication/        # Modelos comunicación
│   │   └── 📁 assessment/           # Modelos assessment
│   │
│   ├── 📁 schemas/                  # CAPA DE DOMINIO (Schemas Pydantic)
│   │   ├── 📄 __init__.py
│   │   │
│   │   ├── 📁 auth/                 # Schemas autenticación
│   │   │   ├── login.py
│   │   │   └── token.py
│   │   │
│   │   ├── 📁 users/                # Schemas usuarios
│   │   │   ├── usuario.py
│   │   │   └── perfil.py
│   │   │
│   │   ├── 📁 academic/             # Schemas académicos
│   │   │   ├── curso.py
│   │   │   ├── tarea.py
│   │   │   └── calificacion.py
│   │   │
│   │   ├── 📁 gamification/         # Schemas gamificación
│   │   │   ├── puntos.py
│   │   │   ├── tienda.py
│   │   │   ├── insignia.py
│   │   │   └── racha.py
│   │   │
│   │   └── 📁 ...
│   │
│   ├── 📁 enums/                    # CAPA DE DOMINIO (Enumeraciones)
│   │   ├── 📄 __init__.py
│   │   │
│   │   ├── 📁 users/                # Enums usuarios
│   │   │   └── rol.py               # RolEnum
│   │   │
│   │   ├── 📁 academic/             # Enums académicos
│   │   │   ├── estado_curso.py
│   │   │   └── tipo_tarea.py
│   │   │
│   │   ├── 📁 gamification/         # Enums gamificación
│   │   │   ├── rareza.py            # RarezaEnum
│   │   │   ├── categoria_item.py    # CategoriaItemEnum
│   │   │   └── tipo_transaccion.py  # TipoTransaccionEnum
│   │   │
│   │   └── 📁 ...
│   │
│   ├── 📁 crud/                     # CAPA DE INFRAESTRUCTURA (CRUD Operations)
│   │   ├── 📄 base.py               # CRUD base genérico
│   │   ├── 📄 user.py
│   │   ├── 📄 curso.py
│   │   └── 📄 ...
│   │
│   ├── 📁 db/                       # CAPA DE INFRAESTRUCTURA (Database)
│   │   ├── 📄 base.py               # Base declarativa SQLAlchemy
│   │   ├── 📄 session.py            # Sesión de base de datos
│   │   └── 📄 init_db.py            # Inicialización DB
│   │
│   ├── 📁 core/                     # Configuración Core
│   │   ├── 📄 config.py             # Settings (Pydantic Settings)
│   │   ├── 📄 security.py           # JWT, hashing, tokens
│   │   ├── 📄 deps.py               # Dependencies FastAPI
│   │   └── 📄 exceptions.py         # Excepciones personalizadas
│   │
│   ├── 📁 utils/                    # Utilidades transversales
│   │   ├── 📄 email.py              # Envío emails
│   │   ├── 📄 validators.py         # Validadores custom
│   │   ├── 📄 helpers.py            # Funciones helper
│   │   └── 📄 ...
│   │
│   └── 📁 templates/                # Templates HTML (emails, etc.)
│       └── 📄 email_verification.html
│
├── 📁 tests/                        # Tests automatizados
│   ├── 📄 conftest.py               # Fixtures pytest
│   │
│   ├── 📁 unit/                     # Tests unitarios
│   │   └── 📁 services/
│   │
│   ├── 📁 integration/              # Tests integración
│   │   └── 📄 test_calificar_entrega_flow.py
│   │
│   └── 📁 gamification/             # Tests gamificación
│       ├── 📄 test_tienda_service.py
│       ├── 📄 test_insignias_service.py
│       └── 📄 test_racha_service.py
│
├── 📁 alembic/                      # Migraciones base de datos
│   ├── 📄 env.py
│   ├── 📄 script.py.mako
│   └── 📁 versions/                 # Archivos de migración
│       └── 📄 xxxx_initial_migration.py
│
├── 📁 docs/                         # Documentación del proyecto
│   ├── 📁 architecture/             # Docs arquitectura
│   │   └── 📄 01-PROJECT_STRUCTURE.md  # Este archivo
│   │
│   ├── 📁 api/                      # Docs API endpoints
│   ├── 📁 database/                 # Docs base de datos
│   ├── 📁 services/                 # Docs servicios
│   └── 📁 deployment/               # Docs despliegue
│
├── 📁 scripts/                      # Scripts utilidades
│   ├── 📄 seed_database.py
│   ├── 📄 generate_test_data.py
│   └── 📄 backup_db.sh
│
├── 📄 .env                          # Variables de entorno (NO en git)
├── 📄 .env.example                  # Ejemplo variables entorno
├── 📄 .gitignore                    # Archivos ignorados git
├── 📄 alembic.ini                   # Configuración Alembic
├── 📄 pyproject.toml                # Configuración proyecto Python
├── 📄 requirements.txt              # Dependencias Python
├── 📄 pytest.ini                    # Configuración pytest
└── 📄 README.md                     # README principal
```

---

## 🎨 Patrones de Diseño

### 1. **Repository Pattern** (CRUD Layer)

**Ubicación:** `src/crud/`

**Propósito:** Abstrae el acceso a datos, proporcionando una interfaz limpia para operaciones CRUD.

**Ejemplo:**
```python
# src/crud/base.py
class CRUDBase:
    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: CreateSchemaType):
        # ...
```

**Beneficios:**
- ✅ Separa lógica de negocio del acceso a datos
- ✅ Facilita testing con mocks
- ✅ Centraliza queries complejas

---

### 2. **Service Layer Pattern**

**Ubicación:** `src/services/`

**Propósito:** Encapsula la lógica de negocio compleja, orquestando múltiples operaciones.

**Ejemplo:**
```python
# src/services/gamification/tienda_service.py
class TiendaService:
    def comprar_item(self, db: Session, usuario_id: UUID, item_id: UUID):
        # 1. Validar puntos suficientes
        # 2. Validar stock disponible
        # 3. Crear transacción
        # 4. Actualizar inventario
        # 5. Descontar puntos
        # 6. Registrar log
        pass
```

**Beneficios:**
- ✅ Lógica de negocio reutilizable
- ✅ Transacciones atómicas
- ✅ Testing independiente de endpoints

---

### 3. **Dependency Injection Pattern**

**Ubicación:** `src/core/deps.py`

**Propósito:** Inyecta dependencias (DB session, usuario actual, etc.) en endpoints.

**Ejemplo:**
```python
# src/core/deps.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Usuario:
    # Validar token y retornar usuario
    pass
```

**Uso en endpoints:**
```python
@router.get("/me")
async def read_users_me(
    current_user: Usuario = Depends(get_current_user)
):
    return current_user
```

**Beneficios:**
- ✅ Código limpio y testeable
- ✅ Reutilización de dependencias
- ✅ Validación automática

---

### 4. **Factory Pattern** (Schemas)

**Ubicación:** `src/schemas/`

**Propósito:** Crear y validar objetos de transferencia de datos (DTOs).

**Ejemplo:**
```python
# src/schemas/gamification/tienda.py
class ItemCreate(BaseModel):
    nombre: str
    categoria: CategoriaItemEnum
    rareza: RarezaEnum
    usar_precio_automatico: bool = True
    precio_puntos: Optional[int] = None

class ItemResponse(ItemCreate):
    id: UUID
    total_vendidos: int
    activo: bool
    created_at: datetime
```

**Beneficios:**
- ✅ Validación automática con Pydantic
- ✅ Documentación OpenAPI automática
- ✅ Type safety

---

### 5. **Strategy Pattern** (Pricing System)

**Ubicación:** `src/services/gamification/tienda_service.py`

**Propósito:** Permitir diferentes estrategias de cálculo (precio automático vs manual).

**Ejemplo:**
```python
def calcular_precio(item: TiendaItem) -> int:
    if item.usar_precio_automatico:
        return PRECIOS_POR_RAREZA[item.rareza]
    else:
        return item.precio_puntos
```

**Beneficios:**
- ✅ Flexibilidad en lógica de negocio
- ✅ Fácil extensión con nuevas estrategias
- ✅ Código limpio y mantenible

---

## 📝 Convenciones de Nomenclatura

### Archivos
- **Modelos:** `snake_case.py` → `tienda_item.py`
- **Schemas:** `snake_case.py` → `tienda.py`
- **Services:** `*_service.py` → `tienda_service.py`
- **Endpoints:** `snake_case.py` → `tienda_admin.py`
- **Tests:** `test_*.py` → `test_tienda_service.py`

### Clases
- **Modelos:** `PascalCase` → `TiendaItem`
- **Schemas:** `PascalCase` → `ItemCreate`, `ItemResponse`
- **Services:** `PascalCase` → `TiendaService`
- **Enums:** `PascalCase` → `RarezaEnum`, `CategoriaItemEnum`

### Variables y Funciones
- **Variables:** `snake_case` → `usuario_actual`, `items_disponibles`
- **Funciones:** `snake_case` → `comprar_item()`, `obtener_catalogo()`
- **Constantes:** `UPPER_SNAKE_CASE` → `MAX_ITEMS_EQUIPADOS = 5`

### Endpoints (URLs)
- **Kebab-case:** `/api/v1/tienda/mis-items`
- **Plurales para colecciones:** `/api/v1/items`
- **Singular para recurso:** `/api/v1/items/{item_id}`

### Base de Datos
- **Tablas:** `snake_case` (plural) → `tienda_items`, `usuarios`
- **Columnas:** `snake_case` → `usuario_id`, `created_at`
- **Foreign Keys:** `{tabla}_id` → `usuario_id`, `item_id`

---

## 🔄 Flujo de Datos

### Flujo Típico de una Petición

```
┌─────────────┐
│   Cliente   │
│  (Frontend) │
└──────┬──────┘
       │ HTTP Request
       ↓
┌─────────────────────────────────────────┐
│         1. API Endpoint (Route)         │
│  src/api/v1/endpoints/gamification/     │
│                                         │
│  @router.post("/tienda/comprar")       │
│  async def comprar_item(...)           │
└──────┬──────────────────────────────────┘
       │ Dependency Injection
       ↓
┌─────────────────────────────────────────┐
│      2. Dependencies (Validación)       │
│         src/core/deps.py                │
│                                         │
│  - get_db() → Session                  │
│  - get_current_user() → Usuario        │
└──────┬──────────────────────────────────┘
       │ Call Service
       ↓
┌─────────────────────────────────────────┐
│      3. Service Layer (Lógica)         │
│   src/services/gamification/            │
│                                         │
│  tienda_service.comprar_item()         │
│  - Validaciones de negocio             │
│  - Orquestación de operaciones         │
└──────┬──────────────────────────────────┘
       │ CRUD Operations
       ↓
┌─────────────────────────────────────────┐
│    4. CRUD Layer (Data Access)         │
│           src/crud/                     │
│                                         │
│  - crud_item.get(item_id)              │
│  - crud_inventario.create(...)         │
│  - crud_puntos.update(...)             │
└──────┬──────────────────────────────────┘
       │ SQLAlchemy Queries
       ↓
┌─────────────────────────────────────────┐
│         5. Models (ORM)                 │
│          src/models/                    │
│                                         │
│  - TiendaItem                          │
│  - InventarioItem                      │
│  - PuntosUsuario                       │
└──────┬──────────────────────────────────┘
       │ SQL Queries
       ↓
┌─────────────────────────────────────────┐
│         6. Database                     │
│        PostgreSQL                       │
│                                         │
│  - Tables: tienda_items,               │
│    inventario_items, puntos_usuarios   │
└──────┬──────────────────────────────────┘
       │ Results
       ↓
┌─────────────────────────────────────────┐
│    7. Schema (Response Validation)      │
│         src/schemas/                    │
│                                         │
│  ItemResponse (Pydantic)               │
│  - Validación automática               │
│  - Serialización JSON                  │
└──────┬──────────────────────────────────┘
       │ JSON Response
       ↓
┌─────────────┐
│   Cliente   │
│  (Frontend) │
└─────────────┘
```

### Ejemplo Concreto: Comprar Item

**1. Cliente envía request:**
```http
POST /api/v1/tienda/comprar
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "item_id": "a1b2c3d4-e5f6-...",
  "cantidad": 1
}
```

**2. Endpoint recibe y valida:**
```python
@router.post("/comprar", response_model=ItemResponse)
async def comprar_item(
    compra: CompraItemRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return tienda_service.comprar_item(db, current_user.id, compra)
```

**3. Service ejecuta lógica:**
```python
def comprar_item(self, db: Session, usuario_id: UUID, compra: CompraItemRequest):
    # Validar puntos
    puntos = crud_puntos.get_by_usuario(db, usuario_id)
    if puntos.puntos_disponibles < item.precio_puntos:
        raise HTTPException(400, "Puntos insuficientes")
    
    # Validar stock
    if item.stock_limitado and item.stock_actual < compra.cantidad:
        raise HTTPException(400, "Stock insuficiente")
    
    # Crear transacción
    transaccion = crud_transaccion.create(db, ...)
    
    # Actualizar inventario
    inventario = crud_inventario.add_or_update(db, ...)
    
    # Descontar puntos
    puntos_service.gastar_puntos(db, usuario_id, item.precio_puntos)
    
    return inventario
```

**4. CRUD accede a DB:**
```python
def create(self, db: Session, obj_in: TransaccionCreate):
    db_obj = TransaccionTienda(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
```

**5. Respuesta al cliente:**
```json
{
  "id": "a1b2c3d4-e5f6-...",
  "nombre": "Cabello Galaxia",
  "categoria": "CABELLO",
  "rareza": "EPICO",
  "precio_puntos": 1000,
  "cantidad": 1,
  "equipado": false,
  "created_at": "2025-11-10T10:30:00Z"
}
```

---

## 🔐 Seguridad en Capas

### 1. **Endpoint Layer**
```python
@router.post("/admin/items")
async def create_item(
    current_user: Usuario = Depends(require_admin)  # ← Validación rol
):
    pass
```

### 2. **Service Layer**
```python
def create_item(self, db: Session, usuario: Usuario, item_data):
    if usuario.rol not in [RolEnum.ADMIN, RolEnum.COORDINADOR]:
        raise HTTPException(403, "No autorizado")
    # ...
```

### 3. **Database Layer**
```python
# Modelo con soft delete
class TiendaItem(Base):
    activo = Column(Boolean, default=True)
    eliminado_en = Column(DateTime, nullable=True)
```

---

## 📊 Métricas y KPIs

### Complejidad del Código
- **Líneas por archivo:** < 1000 (objetivo)
- **Funciones por archivo:** < 50
- **Líneas por función:** < 50
- **Parámetros por función:** < 7

### Cobertura de Tests
- **Objetivo:** > 80%
- **Crítico:** Services y CRUD > 90%
- **Aceptable:** Endpoints > 70%

### Performance
- **Tiempo respuesta API:** < 200ms (p95)
- **Queries por request:** < 10
- **Conexiones DB pool:** 20-100

---

## 🚀 Ventajas de Esta Arquitectura

### ✅ **Mantenibilidad**
- Código organizado por dominios
- Separación clara de responsabilidades
- Fácil localizar y modificar funcionalidad

### ✅ **Escalabilidad**
- Servicios independientes
- Fácil agregar nuevos módulos
- Preparado para microservicios

### ✅ **Testabilidad**
- Cada capa testeable independientemente
- Mocks fáciles de crear
- Tests aislados y rápidos

### ✅ **Reutilización**
- Services compartidos entre endpoints
- CRUD genérico reutilizable
- Utils transversales

### ✅ **Documentación Automática**
- Swagger UI generado automáticamente
- Schemas Pydantic → OpenAPI
- Tipos Python → Documentación

---

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)

---

## 🔄 Próximos Pasos

1. ✅ Estructura base documentada
2. ⏳ Documentar cada módulo individual
3. ⏳ Diagramas de arquitectura visuales
4. ⏳ Guías de desarrollo por dominio
5. ⏳ Documentación de APIs (OpenAPI extendida)

---

**Última actualización:** 10 de Noviembre de 2025  
**Versión:** 1.0  
**Autor:** Equipo Acadify Backend
