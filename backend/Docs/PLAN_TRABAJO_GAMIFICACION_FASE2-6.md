# 📋 PLAN DE TRABAJO - GAMIFICACIÓN FASE 2-6

**Proyecto:** Sistema de Gamificación Acadify  
**Inicio:** 3 de noviembre de 2025  
**Duración:** 6 semanas  
**Estado:** 📌 EN PLANIFICACIÓN

---

## 🎯 OBJETIVO GENERAL

Completar la implementación del sistema de gamificación desde la capa de servicios hasta el frontend funcional, incluyendo:
- API REST completa (31 endpoints)
- Schemas de validación
- Testing comprehensivo
- Población de datos inicial
- Documentación de API
- Optimizaciones de performance

---

## 📅 CRONOGRAMA SEMANAL

### ✅ FASE 0: BASE DE DATOS Y SERVICIOS (COMPLETADA)

**Duración:** 2 días (31 oct - 1 nov 2025)  
**Estado:** ✅ 100% Completado

**Entregables completados:**
- [x] Migración 004_gamification_sql.py aplicada
- [x] 8 tablas creadas (145 columnas)
- [x] 5 enums PostgreSQL
- [x] 41 índices para optimización
- [x] 7 recompensas milestone insertadas
- [x] 4 servicios implementados (~2,350 líneas)
- [x] Documentación técnica completa

---

### 📝 FASE 1: SCHEMAS Y VALIDACIÓN (Semana 1)

**Duración:** 5 días (4-8 noviembre 2025)  
**Responsable:** Desarrollador Backend  
**Prioridad:** 🔴 ALTA

#### Día 1 (Lunes 4 nov): Schemas de Puntos

**Tareas:**
- [ ] Crear `src/schemas/gamification/puntos_schemas.py`
- [ ] Implementar 8 schemas:
  - `PuntosBaseResponse`
  - `NivelInfo`
  - `HistorialPuntoItem`
  - `InsigniaBasica`
  - `PuntosCompletoResponse`
  - `RankingUsuarioItem`
  - `RankingResponse`
  - `PosicionRankingResponse`

**Código esperado:**
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class NivelInfo(BaseModel):
    """Información detallada del nivel actual."""
    nivel_actual: str = Field(..., example="Oro II")
    puntos_minimos_nivel: int = Field(..., ge=0)
    puntos_siguiente_nivel: Optional[int] = Field(None, ge=0)
    progreso_porcentaje: float = Field(..., ge=0, le=100)
    puntos_para_siguiente: int = Field(..., ge=0)

class InsigniaBasica(BaseModel):
    """Información básica de insignia."""
    insignia_id: str
    nombre: str
    descripcion: str
    imagen_url: Optional[str]
    tipo: str

class HistorialPuntoItem(BaseModel):
    """Item individual del historial de puntos."""
    cambio: int
    motivo: str
    fecha: datetime
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class PuntosCompletoResponse(BaseModel):
    """Respuesta completa con toda la información de puntos."""
    puntos_acumulados: int = Field(..., ge=0)
    nivel: str
    nivel_info: NivelInfo
    historial_reciente: List[HistorialPuntoItem] = []
    insignias: List[InsigniaBasica] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "puntos_acumulados": 1250,
                "nivel": "Plata III",
                "nivel_info": {...},
                "historial_reciente": [...],
                "insignias": [...]
            }
        }
```

**Tiempo estimado:** 4 horas  
**Líneas de código:** ~200

#### Día 2 (Martes 5 nov): Schemas de Etiquetas

**Tareas:**
- [ ] Crear `src/schemas/gamification/etiquetas_schemas.py`
- [ ] Implementar 12 schemas:
  - `EtiquetaBase`
  - `EtiquetaCatalogo`
  - `CompraEtiquetaRequest`
  - `CompraEtiquetaResponse`
  - `UsuarioEtiquetaDetalle`
  - `EquiparEtiquetasRequest`
  - `EquiparEtiquetasResponse`
  - `EvolucionDisponibleResponse`
  - `EvolucionResponse`
  - `EstadisticasEtiquetasResponse`

**Validaciones especiales:**
- Máximo 5 etiquetas en `EquiparEtiquetasRequest`
- UUID válidos
- Enums correctos (CategoriaEtiqueta, RarezaEtiqueta)

**Tiempo estimado:** 5 horas  
**Líneas de código:** ~300

#### Día 3 (Miércoles 6 nov): Schemas de Tienda

**Tareas:**
- [ ] Crear `src/schemas/gamification/tienda_schemas.py`
- [ ] Implementar 15 schemas:
  - `TiendaItemBase`
  - `TiendaItemCatalogo`
  - `CompraRequest`
  - `CompraResponse`
  - `InventarioItem`
  - `InventarioResponse`
  - `EquiparItemRequest`
  - `EquiparItemResponse`
  - `UsarItemRequest`
  - `UsarItemResponse`
  - `TransaccionHistorial`
  - `EstadisticasTiendaResponse`

**Validaciones especiales:**
- Cantidad > 0 en compras
- Precio >= 0
- Stock validation

**Tiempo estimado:** 6 horas  
**Líneas de código:** ~400

#### Día 4 (Jueves 7 nov): Schemas de Rachas

**Tareas:**
- [ ] Crear `src/schemas/gamification/rachas_schemas.py`
- [ ] Implementar 14 schemas:
  - `RachaBase`
  - `RachaCompleta`
  - `ActividadRequest`
  - `VerificacionRachaResponse`
  - `CongeladorRequest`
  - `CongeladorResponse`
  - `RecuperacionResponse`
  - `EventoRachaHistorial`
  - `MilestoneInfo`
  - `EstadisticasRachaResponse`

**Validaciones especiales:**
- Días de congelación: 1-30
- TipoActividadRacha enum
- Fechas válidas

**Tiempo estimado:** 5 horas  
**Líneas de código:** ~350

#### Día 5 (Viernes 8 nov): Schemas Comunes y Refactoring

**Tareas:**
- [ ] Crear `src/schemas/gamification/__init__.py`
- [ ] Crear `src/schemas/gamification/common.py` (schemas compartidos)
- [ ] Revisar y refactorizar todos los schemas
- [ ] Agregar tests unitarios para validators
- [ ] Documentar cada schema con ejemplos

**Schemas comunes:**
```python
class PaginationParams(BaseModel):
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)

class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[dict] = None
```

**Tiempo estimado:** 4 horas  
**Líneas de código:** ~150

**📊 Totales Fase 1:**
- **Tiempo total:** 24 horas (3 días efectivos)
- **Archivos creados:** 5
- **Líneas de código:** ~1,400
- **Schemas totales:** 49

---

### 🌐 FASE 2: API ENDPOINTS (Semana 2)

**Duración:** 5 días (11-15 noviembre 2025)  
**Responsable:** Desarrollador Backend  
**Prioridad:** 🔴 ALTA

#### Día 1 (Lunes 11 nov): Endpoints de Puntos

**Tareas:**
- [ ] Crear `src/api/routes/gamification/puntos.py`
- [ ] Implementar 6 endpoints:
  ```python
  GET  /api/gamification/puntos/mis-puntos
  GET  /api/gamification/puntos/ranking
  GET  /api/gamification/puntos/mi-posicion
  GET  /api/gamification/puntos/historial
  GET  /api/gamification/puntos/niveles
  POST /api/gamification/puntos/otorgar  # Admin only
  ```
- [ ] Agregar dependencias de autenticación
- [ ] Manejo de errores con HTTPException
- [ ] Logging de operaciones

**Estructura base:**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db, get_usuario_actual
from src.services.gamification.puntos_service import PuntosService
from src.schemas.gamification.puntos_schemas import *
from src.models.auth.usuario import Usuario

router = APIRouter(prefix="/puntos", tags=["Puntos"])

@router.get("/mis-puntos", response_model=PuntosCompletoResponse)
async def obtener_mis_puntos(
    usuario_actual: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene información completa de puntos del usuario actual.
    
    Incluye:
    - Puntos acumulados
    - Nivel actual y progreso
    - Historial reciente (últimos 10 movimientos)
    - Insignias obtenidas
    """
    service = PuntosService(db)
    return await service.obtener_puntos_usuario(usuario_actual.usuario_id)
```

**Tiempo estimado:** 6 horas  
**Líneas de código:** ~250

#### Día 2 (Martes 12 nov): Endpoints de Etiquetas

**Tareas:**
- [ ] Crear `src/api/routes/gamification/etiquetas.py`
- [ ] Implementar 8 endpoints:
  ```python
  GET    /api/gamification/etiquetas/catalogo
  GET    /api/gamification/etiquetas/{etiqueta_id}
  GET    /api/gamification/etiquetas/mis-etiquetas
  POST   /api/gamification/etiquetas/{etiqueta_id}/comprar
  PUT    /api/gamification/etiquetas/equipar
  DELETE /api/gamification/etiquetas/desequipar-todas
  POST   /api/gamification/etiquetas/{etiqueta_id}/evolucionar
  GET    /api/gamification/etiquetas/estadisticas
  ```
- [ ] Validación de ownership (usuario solo accede a sus etiquetas)
- [ ] Rate limiting consideration

**Tiempo estimado:** 7 horas  
**Líneas de código:** ~350

#### Día 3 (Miércoles 13 nov): Endpoints de Tienda (Parte 1)

**Tareas:**
- [ ] Crear `src/api/routes/gamification/tienda.py`
- [ ] Implementar primeros 5 endpoints:
  ```python
  GET  /api/gamification/tienda/catalogo
  GET  /api/gamification/tienda/{item_id}
  GET  /api/gamification/tienda/destacados
  GET  /api/gamification/tienda/nuevos
  GET  /api/gamification/tienda/limitados
  ```

**Funcionalidades especiales:**
- Filtros avanzados (categoría, rareza, precio)
- Paginación eficiente
- Marcadores de "nuevo", "destacado", "limitado"

**Tiempo estimado:** 6 horas  
**Líneas de código:** ~300

#### Día 4 (Jueves 14 nov): Endpoints de Tienda (Parte 2)

**Tareas:**
- [ ] Continuar con 5 endpoints adicionales:
  ```python
  POST /api/gamification/tienda/comprar
  GET  /api/gamification/tienda/inventario
  PUT  /api/gamification/tienda/equipar/{inventario_id}
  PUT  /api/gamification/tienda/desequipar/{inventario_id}
  POST /api/gamification/tienda/usar/{inventario_id}
  ```
- [ ] Agregar endpoints de transacciones:
  ```python
  GET  /api/gamification/tienda/transacciones
  GET  /api/gamification/tienda/estadisticas
  ```

**Tiempo estimado:** 7 horas  
**Líneas de código:** ~350

#### Día 5 (Viernes 15 nov): Endpoints de Rachas

**Tareas:**
- [ ] Crear `src/api/routes/gamification/rachas.py`
- [ ] Implementar 7 endpoints:
  ```python
  GET  /api/gamification/rachas/mi-racha
  POST /api/gamification/rachas/verificar
  POST /api/gamification/rachas/activar-congelador
  POST /api/gamification/rachas/recuperar
  GET  /api/gamification/rachas/historial
  GET  /api/gamification/rachas/milestones
  GET  /api/gamification/rachas/estadisticas
  ```
- [ ] Integración con sistema de notificaciones
- [ ] Webhooks para eventos importantes

**Tiempo estimado:** 6 horas  
**Líneas de código:** ~300

**Tareas adicionales Fase 2:**
- [ ] Crear `src/api/routes/gamification/__init__.py`
- [ ] Registrar todos los routers en `src/api/routes.py`
- [ ] Configurar CORS para endpoints
- [ ] Documentación Swagger automática
- [ ] Testing manual con Postman/Thunder Client

**📊 Totales Fase 2:**
- **Tiempo total:** 32 horas (4 días efectivos)
- **Archivos creados:** 5
- **Líneas de código:** ~1,550
- **Endpoints totales:** 31

---

### 🧪 FASE 3: TESTING (Semana 3)

**Duración:** 5 días (18-22 noviembre 2025)  
**Responsable:** QA + Backend Developer  
**Prioridad:** 🟡 MEDIA-ALTA

#### Estructura de Testing

**Framework:** pytest + pytest-asyncio + httpx

**Archivos a crear:**
```
TEST/gamification/
├── __init__.py
├── conftest.py                          # Fixtures compartidos
├── test_puntos_service.py               # 15 tests
├── test_etiquetas_service.py            # 20 tests
├── test_tienda_service.py               # 25 tests
├── test_rachas_service.py               # 18 tests
├── test_puntos_endpoints.py             # 12 tests
├── test_etiquetas_endpoints.py          # 16 tests
├── test_tienda_endpoints.py             # 20 tests
└── test_rachas_endpoints.py             # 14 tests
```

#### Día 1-2 (Lunes-Martes 18-19 nov): Tests de Servicios

**Tests de PuntosService:**
- [ ] test_calcular_puntos_tarea_basico
- [ ] test_calcular_puntos_con_bonus
- [ ] test_calcular_puntos_con_penalizacion_tardia
- [ ] test_otorgar_puntos_exitoso
- [ ] test_otorgar_puntos_crea_usuario_puntos
- [ ] test_verificar_insignias_automatico
- [ ] test_calcular_nivel_correcto
- [ ] test_obtener_ranking_paginado
- [ ] test_obtener_posicion_usuario

**Tests de EtiquetasService:**
- [ ] test_get_catalogo_con_filtros
- [ ] test_comprar_etiqueta_exitoso
- [ ] test_comprar_etiqueta_sin_puntos
- [ ] test_comprar_etiqueta_duplicada
- [ ] test_equipar_etiquetas_maximo_5
- [ ] test_equipar_etiquetas_desequipa_anterior
- [ ] test_evolucionar_etiqueta_cumple_requisitos
- [ ] test_evolucionar_etiqueta_sin_requisitos
- [ ] test_otorgar_etiqueta_por_logro

**Tiempo estimado:** 12 horas

#### Día 3-4 (Miércoles-Jueves 20-21 nov): Tests de Endpoints

**Tests de API:**
- [ ] test_get_mis_puntos_autenticado
- [ ] test_get_mis_puntos_no_autenticado_401
- [ ] test_comprar_etiqueta_endpoint
- [ ] test_equipar_etiquetas_validacion
- [ ] test_comprar_item_tienda
- [ ] test_comprar_item_sin_stock_400
- [ ] test_verificar_racha_incrementa
- [ ] test_verificar_racha_usa_proteccion

**Fixtures comunes (conftest.py):**
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from httpx import AsyncClient

@pytest.fixture
async def db_session():
    """Sesión de base de datos de prueba."""
    engine = create_async_engine(
        "postgresql+asyncpg://test_user:test_pass@localhost/acadify_test"
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def usuario_test(db_session):
    """Usuario de prueba con puntos."""
    usuario = Usuario(
        correo="test@acadify.com",
        nombre="Test",
        apellido="User"
    )
    db_session.add(usuario)
    await db_session.commit()
    
    puntos = UsuarioPuntos(
        usuario_id=usuario.usuario_id,
        puntos_acumulados=1000
    )
    db_session.add(puntos)
    await db_session.commit()
    
    return usuario

@pytest.fixture
async def client(db_session):
    """Cliente HTTP de prueba."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

**Tiempo estimado:** 14 horas

#### Día 5 (Viernes 22 nov): Tests de Integración y Coverage

**Tareas:**
- [ ] Tests de integración end-to-end
- [ ] Test de flujo completo: usuario gana puntos → compra etiqueta → equipa
- [ ] Test de flujo completo: usuario mantiene racha → recibe milestone
- [ ] Análisis de cobertura con pytest-cov
- [ ] Identificar código no cubierto
- [ ] Agregar tests faltantes para >80% coverage

**Comando coverage:**
```bash
pytest --cov=src/services/gamification --cov=src/api/routes/gamification --cov-report=html
```

**Tiempo estimado:** 8 horas

**📊 Totales Fase 3:**
- **Tiempo total:** 34 horas (4.25 días efectivos)
- **Archivos creados:** 9
- **Tests totales:** ~140
- **Cobertura objetivo:** >80%

---

### 📦 FASE 4: POBLACIÓN DE DATOS (Semana 4)

**Duración:** 5 días (25-29 noviembre 2025)  
**Responsable:** Backend Developer  
**Prioridad:** 🟡 MEDIA

#### Día 1 (Lunes 25 nov): Etiquetas (100+ items)

**Archivo:** `scripts/populate_etiquetas.py`

**Estructura:**
```python
# 22 categorías × ~5 etiquetas cada una = 110 etiquetas

ETIQUETAS_DATA = {
    "matematicas": [
        {
            "nombre": "Sumador Principiante",
            "rareza": "comun",
            "precio": 50,
            "descripcion": "Completaste tu primera suma"
        },
        {
            "nombre": "Maestro de Álgebra",
            "rareza": "raro",
            "precio": 200,
            "descripcion": "Resolviste 20 problemas de álgebra"
        },
        # ... 3 más
    ],
    "programacion": [
        {
            "nombre": "Hello World",
            "rareza": "comun",
            "precio": 50
        },
        {
            "nombre": "Python Ninja",
            "rareza": "epico",
            "precio": 800,
            "etiqueta_evolucion": "Python Sensei"
        },
        # ... 3 más
    ],
    # ... resto de categorías
}
```

**Distribución por rareza:**
- 60 Comunes (50-100 pts)
- 30 Raras (150-300 pts)
- 15 Épicas (500-1000 pts)
- 5 Legendarias (1500-2500 pts)

**Cadenas de evolución:** 10 cadenas (2-4 niveles cada una)

**Tiempo estimado:** 8 horas

#### Día 2 (Martes 26 nov): Items de Tienda - Avatar (80 items)

**Archivo:** `scripts/populate_tienda_avatar.py`

**Vinculación con avatar_asset:**
```python
# Obtener todos los avatar_assets existentes
assets_cabeza = await db.execute(
    select(AvatarAsset).where(AvatarAsset.category == "hair")
)

# Crear items de tienda vinculados
for asset in assets_cabeza:
    item = TiendaItem(
        nombre=f"Cabello: {asset.name}",
        categoria=CategoriaItem.AVATAR_CABEZA,
        avatar_asset_id=asset.id,
        precio_puntos=calcular_precio(asset.rarity),
        rareza=mapear_rareza(asset.rarity)
    )
    db.add(item)
```

**Categorías avatar:**
- 20 Cabezas (peinados, sombreros)
- 15 Torsos (camisas, chaquetas)
- 15 Piernas (pantalones, faldas)
- 10 Zapatos
- 10 Accesorios
- 10 Conjuntos completos

**Tiempo estimado:** 6 horas

#### Día 3 (Miércoles 27 nov): Items de Tienda - Cosméticos (60 items)

**Archivo:** `scripts/populate_tienda_cosmeticos.py`

**Categorías cosméticas:**
- 10 Fotos de perfil (marcos)
- 10 Fotos de portada (fondos)
- 10 Marcos de perfil animados
- 10 Efectos de perfil
- 10 Temas de chat
- 5 Packs de stickers
- 5 Packs de emojis personalizados

**Ejemplos:**
```python
COSMETICOS = [
    {
        "nombre": "Marco Dorado",
        "categoria": "foto_perfil",
        "rareza": "raro",
        "precio": 300,
        "imagen_url": "/assets/marcos/dorado.png"
    },
    {
        "nombre": "Efecto Fuego",
        "categoria": "efecto_perfil",
        "rareza": "epico",
        "precio": 800,
        "animacion_url": "/assets/efectos/fuego.gif"
    }
]
```

**Tiempo estimado:** 5 horas

#### Día 4 (Jueves 28 nov): Items Funcionales (60 items)

**Archivo:** `scripts/populate_tienda_funcionales.py`

**Items funcionales:**

1. **Multiplicadores de Puntos (15 items)**
```python
{
    "nombre": "Boost 2x - 24h",
    "categoria": "multiplicador_puntos",
    "tipo": "consumible",
    "precio": 500,
    "efecto_json": {
        "tipo": "multiplicador",
        "factor": 2.0,
        "duracion_horas": 24
    }
}
```

2. **Protecciones de Racha (15 items)**
```python
{
    "nombre": "Escudo Racha 3 Días",
    "categoria": "proteccion_racha",
    "precio": 300,
    "efecto_json": {
        "tipo": "congelador",
        "dias": 3
    }
}
```

3. **Desbloqueos de Contenido (15 items)**
4. **Boosts de Experiencia (15 items)**

**Tiempo estimado:** 6 horas

#### Día 5 (Viernes 29 nov): Recompensas y Milestones Adicionales

**Tareas:**
- [ ] Crear milestones adicionales para rachas semanales/mensuales
- [ ] Vincular insignias existentes con etiquetas
- [ ] Crear recompensas especiales de eventos
- [ ] Script de validación de integridad de datos
- [ ] Backup de datos poblados

**Archivo:** `scripts/populate_recompensas_adicionales.py`

**Recompensas semanales:**
```python
RECOMPENSAS_SEMANALES = [
    {"semanas": 1, "puntos": 200, "dias_congelacion": 1},
    {"semanas": 4, "puntos": 1000, "dias_congelacion": 3},
    {"semanas": 12, "puntos": 3000, "dias_congelacion": 5},
    {"semanas": 26, "puntos": 10000, "dias_congelacion": 10}
]
```

**Tiempo estimado:** 5 horas

**📊 Totales Fase 4:**
- **Tiempo total:** 30 horas (3.75 días efectivos)
- **Scripts creados:** 5
- **Etiquetas:** 110
- **Items tienda:** 200
- **Recompensas:** 20+

---

### 📖 FASE 5: DOCUMENTACIÓN API (Semana 5)

**Duración:** 3 días (2-6 diciembre 2025)  
**Responsable:** Tech Writer + Backend Developer  
**Prioridad:** 🟢 MEDIA

#### Día 1 (Lunes 2 dic): Swagger/OpenAPI

**Tareas:**
- [ ] Configurar generación automática de docs
- [ ] Agregar descriptions a todos los endpoints
- [ ] Ejemplos de request/response en schemas
- [ ] Tags y agrupación lógica
- [ ] Servidor de pruebas en docs

**Configuración FastAPI:**
```python
app = FastAPI(
    title="Acadify Gamification API",
    description="API completa del sistema de gamificación",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_tags=[
        {"name": "Puntos", "description": "Gestión de puntos y niveles"},
        {"name": "Etiquetas", "description": "Sistema de badges"},
        {"name": "Tienda", "description": "Tienda virtual e inventario"},
        {"name": "Rachas", "description": "Sistema de rachas diarias"}
    ]
)
```

**Tiempo estimado:** 6 horas

#### Día 2 (Martes 3 dic): Postman Collection

**Tareas:**
- [ ] Crear colección Postman completa
- [ ] 31 requests configurados
- [ ] Variables de entorno (dev, staging, prod)
- [ ] Tests automatizados en requests
- [ ] Scripts pre-request para auth tokens
- [ ] Exportar a JSON

**Estructura:**
```
Acadify Gamification.postman_collection.json
├── Puntos (6 requests)
├── Etiquetas (8 requests)
├── Tienda (10 requests)
└── Rachas (7 requests)
```

**Tiempo estimado:** 5 horas

#### Día 3 (Miércoles 4 dic): Guías de Integración

**Archivos a crear:**

1. **`Docs/API_GAMIFICATION_GUIDE.md`**
   - Introducción al sistema
   - Autenticación y headers
   - Rate limiting
   - Códigos de error comunes
   - Ejemplos por lenguaje (Python, JavaScript, cURL)

2. **`Docs/FRONTEND_INTEGRATION.md`**
   - Hooks React recomendados
   - Context providers
   - Estado global (Redux/Zustand)
   - Manejo de WebSockets para notificaciones
   - Componentes de ejemplo

3. **`Docs/BUSINESS_LOGIC.md`**
   - Reglas de negocio completas
   - Fórmulas de cálculo
   - Casos de uso principales
   - Diagramas de flujo

**Tiempo estimado:** 9 horas

**📊 Totales Fase 5:**
- **Tiempo total:** 20 horas (2.5 días efectivos)
- **Archivos creados:** 4
- **Documentación:** Completa y publicable

---

### ⚡ FASE 6: OPTIMIZACIÓN (Semana 6)

**Duración:** 5 días (9-13 diciembre 2025)  
**Responsable:** Backend Developer + DevOps  
**Prioridad:** 🟢 MEDIA

#### Día 1-2 (Lunes-Martes 9-10 dic): Caché con Redis

**Tareas:**
- [ ] Configurar Redis en proyecto
- [ ] Implementar caché para rankings
- [ ] Caché de catálogos (etiquetas, tienda)
- [ ] Invalidación automática
- [ ] Monitoring de hit/miss rate

**Implementación:**
```python
from redis.asyncio import Redis
import json

class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def get_ranking_cached(self, key: str = "ranking:global"):
        """Obtiene ranking de caché (TTL: 5 minutos)."""
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set_ranking_cached(self, ranking: list, ttl: int = 300):
        """Guarda ranking en caché."""
        await self.redis.setex(
            "ranking:global",
            ttl,
            json.dumps(ranking)
        )
```

**Endpoints a cachear:**
- GET /api/gamification/puntos/ranking (5 min TTL)
- GET /api/gamification/etiquetas/catalogo (15 min TTL)
- GET /api/gamification/tienda/catalogo (10 min TTL)
- GET /api/gamification/rachas/milestones (1 hora TTL)

**Tiempo estimado:** 12 horas

#### Día 3 (Miércoles 11 dic): Optimización de Queries

**Tareas:**
- [ ] Analizar queries lentos con pg_stat_statements
- [ ] Agregar índices adicionales si necesario
- [ ] Optimizar joins (selectinload vs joinedload)
- [ ] Limitar N+1 queries
- [ ] Usar EXPLAIN ANALYZE

**Queries a optimizar:**
```sql
-- Ranking con paginación
SELECT u.nombre, up.puntos_acumulados 
FROM usuario_puntos up 
JOIN Usuario u ON u.usuario_id = up.usuario_id 
ORDER BY up.puntos_acumulados DESC 
LIMIT 50 OFFSET 0;

-- Catálogo de tienda con filtros
SELECT * FROM tienda_item 
WHERE categoria = 'avatar_cabeza' 
  AND rareza = 'epico' 
  AND es_activo = true 
ORDER BY rareza DESC, precio_puntos DESC;
```

**Índices adicionales a considerar:**
```sql
CREATE INDEX IF NOT EXISTS idx_tienda_categoria_rareza 
ON tienda_item(categoria, rareza) WHERE es_activo = true;

CREATE INDEX IF NOT EXISTS idx_usuario_puntos_ranking 
ON usuario_puntos(puntos_acumulados DESC);
```

**Tiempo estimado:** 6 horas

#### Día 4 (Jueves 12 dic): Rate Limiting y Seguridad

**Tareas:**
- [ ] Implementar rate limiting con slowapi
- [ ] Límites por endpoint y usuario
- [ ] Protección contra spam de compras
- [ ] Logging de intentos sospechosos
- [ ] Alertas automáticas

**Configuración:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Aplicar a endpoints sensibles
@router.post("/comprar")
@limiter.limit("10/minute")  # Máximo 10 compras por minuto
async def comprar_item(...):
    ...

@router.post("/etiquetas/{id}/comprar")
@limiter.limit("20/minute")
async def comprar_etiqueta(...):
    ...
```

**Tiempo estimado:** 5 horas

#### Día 5 (Viernes 13 dic): Monitoring y Métricas

**Tareas:**
- [ ] Configurar Prometheus metrics
- [ ] Dashboard Grafana
- [ ] Alertas de performance
- [ ] Logging estructurado (JSON)
- [ ] APM (Application Performance Monitoring)

**Métricas a trackear:**
- Tiempo de respuesta por endpoint (p50, p95, p99)
- Queries a base de datos (conteo, duración)
- Tasa de error (4xx, 5xx)
- Uso de caché (hit rate)
- Transacciones por minuto

**Tiempo estimado:** 7 horas

**📊 Totales Fase 6:**
- **Tiempo total:** 30 horas (3.75 días efectivos)
- **Mejoras:** Caché, optimización, seguridad, monitoring
- **Performance:** 2-3x más rápido

---

## 📊 RESUMEN GENERAL

### Tiempo Total Estimado

| Fase | Días Efectivos | Horas | % del Total |
|------|---------------|-------|-------------|
| 1. Schemas | 3 días | 24h | 14.5% |
| 2. API Endpoints | 4 días | 32h | 19.3% |
| 3. Testing | 4.25 días | 34h | 20.5% |
| 4. Población Datos | 3.75 días | 30h | 18.1% |
| 5. Documentación | 2.5 días | 20h | 12.0% |
| 6. Optimización | 3.75 días | 30h | 18.1% |
| **TOTAL** | **21.25 días** | **170 horas** | **100%** |

**Con buffer 20%:** ~25 días → **5 semanas laborables**

### Entregables Finales

**Código:**
- 49 Schemas de validación
- 31 Endpoints REST
- 140+ Tests (>80% coverage)
- 5 Scripts de población
- 4 Servicios optimizados

**Datos:**
- 110 Etiquetas categorizadas
- 200 Items de tienda
- 20+ Recompensas de racha
- Vinculación con 50+ avatar assets

**Documentación:**
- Guía de API completa
- Postman Collection
- Guía de integración frontend
- Swagger/OpenAPI automático

**Infraestructura:**
- Caché Redis configurado
- Rate limiting activo
- Monitoring con Grafana
- Optimizaciones de queries

---

## 🚀 INICIO INMEDIATO

### Siguiente Tarea (HOY)

**Fase 1 - Día 1: Schemas de Puntos**

```bash
# 1. Crear estructura
mkdir -p src/schemas/gamification
touch src/schemas/gamification/__init__.py
touch src/schemas/gamification/puntos_schemas.py

# 2. Comenzar implementación
code src/schemas/gamification/puntos_schemas.py
```

**Template inicial:**
```python
"""
Schemas de validación para el módulo de Puntos.

Este módulo define los modelos Pydantic para:
- Respuestas de información de puntos
- Niveles y progreso
- Rankings y posiciones
- Historial de puntos

Author: GitHub Copilot & Team
Date: 4 de noviembre de 2025
Version: 1.0.0
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# Implementar aquí los 8 schemas...
```

---

## 📞 CONTACTO Y SOPORTE

**Project Manager:** [TBD]  
**Tech Lead:** [TBD]  
**QA Lead:** [TBD]  

**Repositorio:** `Acadify/backend`  
**Branch principal:** `develop`  
**Convención commits:** `feat(gamification): descripción`

---

**Documento creado:** 2 de noviembre de 2025  
**Última actualización:** 2 de noviembre de 2025  
**Estado:** ✅ APROBADO PARA EJECUCIÓN

