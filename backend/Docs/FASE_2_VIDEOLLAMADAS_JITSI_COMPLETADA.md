# 🎬 FASE 2.0 - Sistema de Videollamadas con Jitsi Meet - COMPLETADA ✅

**Fecha:** 9 de Noviembre, 2025  
**Estado:** Base de Datos 100% Operativa  
**Arquitectura:** Jitsi Meet (SFU - Selective Forwarding Unit)

---

## 📋 Resumen Ejecutivo

Se ha completado la configuración de la base de datos para el sistema de videollamadas usando **Jitsi Meet** como proveedor de videollamadas. La arquitectura soporta:

- ✅ **75-200+ usuarios** simultáneos por sala (vs 4-8 en WebRTC P2P)
- ✅ **JWT Authentication** integrado
- ✅ **Grabaciones** con almacenamiento y procesamiento
- ✅ **Estadísticas** y métricas en tiempo real
- ✅ **Control de participantes** con roles de moderador

---

## 🗄️ Estructura de Base de Datos

### Tablas Creadas (3)

#### 1. `videollamadas` - Tabla Principal
```sql
CREATE TABLE videollamadas (
    id UUID PRIMARY KEY,
    jitsi_room_name VARCHAR(255) UNIQUE NOT NULL,  -- ⭐ Campo clave para Jitsi
    tipo_llamada tipo_llamada NOT NULL,            -- VIDEO o VOZ
    iniciador_id UUID REFERENCES Usuario,
    sala_chat_id UUID REFERENCES salas_chat,
    fecha_inicio TIMESTAMPTZ NOT NULL,
    fecha_fin TIMESTAMPTZ,
    duracion_segundos INTEGER,
    estado estado_videollamada NOT NULL,           -- PROGRAMADA, ACTIVA, FINALIZADA, CANCELADA
    configuracion JSON NOT NULL DEFAULT '{}',
    grabacion_url VARCHAR(500),
    transcripcion TEXT,
    resumen_ia TEXT
);
```

**Índices:**
- `ix_videollamadas_jitsi_room_name` - Búsqueda rápida por sala
- `ix_videollamadas_iniciador_id` - Videollamadas por usuario
- `ix_videollamadas_estado` - Filtrado por estado
- `ix_videollamadas_fecha_inicio` - Ordenamiento temporal

#### 2. `videollamadas_participantes` - Participantes
```sql
CREATE TABLE videollamadas_participantes (
    id UUID PRIMARY KEY,
    videollamada_id UUID REFERENCES videollamadas ON DELETE CASCADE,
    usuario_id UUID REFERENCES Usuario,
    fecha_union TIMESTAMPTZ NOT NULL,
    fecha_salida TIMESTAMPTZ,
    duracion_segundos INTEGER,
    es_moderador BOOLEAN NOT NULL DEFAULT FALSE,
    calidad_conexion calidad_conexion,
    estadisticas JSON
);
```

**Características:**
- Restricción única: Un usuario no puede estar duplicado en la misma videollamada activa
- Trigger automático para calcular duración cuando un participante sale

#### 3. `videollamadas_grabaciones` - Grabaciones
```sql
CREATE TABLE videollamadas_grabaciones (
    id UUID PRIMARY KEY,
    videollamada_id UUID REFERENCES videollamadas ON DELETE CASCADE,
    titulo VARCHAR(255) NOT NULL,
    archivo_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    formato formato_grabacion NOT NULL,        -- mp4, webm, mkv, avi
    calidad calidad_grabacion NOT NULL,        -- SD, HD, FHD, 4K
    duracion_segundos INTEGER NOT NULL,
    tamano_bytes BIGINT NOT NULL,
    fecha_subida TIMESTAMPTZ NOT NULL,
    estado_procesamiento estado_procesamiento, -- pendiente, procesando, completado, error
    error_mensaje TEXT,
    metadatos JSON
);
```

---

### ENUMs Creados (6)

```sql
-- Tipo de llamada
CREATE TYPE tipo_llamada AS ENUM ('VIDEO', 'VOZ');

-- Estados de videollamada
CREATE TYPE estado_videollamada AS ENUM (
    'PROGRAMADA',  -- Agendada pero no iniciada
    'ACTIVA',      -- En curso
    'FINALIZADA',  -- Terminada normalmente
    'CANCELADA'    -- Cancelada antes o durante
);

-- Calidad de conexión
CREATE TYPE calidad_conexion AS ENUM (
    'excelente',  -- < 50ms latencia, < 1% pérdida
    'buena',      -- 50-100ms, 1-3%
    'regular',    -- 100-200ms, 3-5%
    'mala'        -- > 200ms, > 5%
);

-- Formatos de grabación
CREATE TYPE formato_grabacion AS ENUM ('mp4', 'webm', 'mkv', 'avi');

-- Calidades de video
CREATE TYPE calidad_grabacion AS ENUM ('SD', 'HD', 'FHD', '4K');

-- Estados de procesamiento
CREATE TYPE estado_procesamiento AS ENUM (
    'pendiente',
    'procesando',
    'completado',
    'error'
);
```

---

### Funciones SQL (3)

#### 1. `finalizar_videollamada(uuid)`
Finaliza una videollamada activa y actualiza todos los participantes que no salieron.

```sql
SELECT * FROM finalizar_videollamada('uuid-de-videollamada');
-- Retorna: {success: boolean, mensaje: text}
```

**Acciones:**
- Marca videollamada como FINALIZADA
- Calcula duración total
- Cierra participantes activos
- Actualiza timestamps

#### 2. `get_estadisticas_videollamada(uuid)`
Retorna estadísticas completas en formato JSON.

```sql
SELECT get_estadisticas_videollamada('uuid-de-videollamada');
```

**Retorna:**
```json
{
  "videollamada_id": "uuid",
  "jitsi_room_name": "sala-matematicas-2024",
  "duracion_minutos": 45.5,
  "total_participantes": 25,
  "participantes_actuales": 18,
  "duracion_promedio_participante": 38.2,
  "tiene_grabacion": true,
  "total_grabaciones": 1
}
```

#### 3. `actualizar_duracion_participante()` (Trigger)
Se ejecuta automáticamente cuando un participante sale.

```sql
-- Automático: Calcula duracion_segundos = fecha_salida - fecha_union
```

---

### Vistas (1)

#### `videollamadas_activas`
Vista optimizada de videollamadas en curso con conteo de participantes.

```sql
SELECT * FROM videollamadas_activas;
```

**Columnas:**
- id, jitsi_room_name, tipo_llamada
- fecha_inicio, estado
- iniciador_nombre, iniciador_apellido
- **participantes_conectados** - Actualmente en la llamada
- **total_participantes** - Histórico

---

## 📂 Archivos del Sistema

### Scripts SQL
- **`scripts/create_videollamadas_tables.sql`** (12,905 caracteres)
  - SQL completo con todas las definiciones
  - ENUMs, tablas, índices, funciones, triggers, vistas
  - Comentarios exhaustivos en español

- **`scripts/setup_videollamadas_db.py`** (5,621 caracteres)
  - Script Python para ejecutar el SQL
  - Manejo de conexión y errores
  - Verificación post-ejecución
  - Soporte para variables de entorno

### Modelos Python
- **`src/models/communication/videollamada.py`** (223 líneas)
  ```python
  class Videollamada(Base):
      __tablename__ = "videollamadas"
      jitsi_room_name: Mapped[str]
      tipo_llamada: Mapped[str]
      # ... 13 campos más
  
  class VideollamadaParticipante(Base):
      __tablename__ = "videollamadas_participantes"
      # ... control de participantes
  
  class VideollamadaGrabacion(Base):
      __tablename__ = "videollamadas_grabaciones"
      # ... gestión de grabaciones
  ```

### ENUMs Python
- **`src/enums/communication/videollamada_enums.py`** (265 líneas)
  ```python
  class TipoLlamada(str, Enum):
      VIDEO = "video"
      VOZ = "voz"
  
  class EstadoVideollamada(str, Enum):
      PROGRAMADA = "programada"
      ACTIVA = "activa"
      FINALIZADA = "finalizada"
      CANCELADA = "cancelada"
      
      def puede_transicionar_a(self, nuevo_estado) -> bool:
          # Validación de transiciones de estado
  ```

### Schemas Pydantic
- **`src/schemas/communication/videollamada_schemas.py`** (822 líneas)
  ```python
  class VideollamadaBase(BaseModel):
      jitsi_room_name: str = Field(min_length=3, max_length=255)
      tipo_llamada: TipoLlamada
      sala_chat_id: Optional[UUID]
      configuracion: Dict[str, Any] = Field(default_factory=dict)
  
  class VideollamadaCreate(VideollamadaBase):
      # jitsi_room_name es opcional (se genera automáticamente)
  
  class VideollamadaUpdate(BaseModel):
      transcripcion: Optional[str]
      resumen_ia: Optional[str]
      # ... campos opcionales para actualización
  ```

### CRUD Operations
- **`src/crud/communication/videollamada.py`** (581+ líneas)
  ```python
  class CRUDVideollamada(CRUDBase):
      def create_videollamada(
          self, db, *, 
          jitsi_room_name: str,
          tipo_llamada: TipoLlamada,
          iniciador_id: UUID,
          # ...
      ) -> Videollamada:
          # Crea videollamada y agrega iniciador como moderador
  
      def finalizar_videollamada(self, db, videollamada_id: UUID):
          # Wrapper para función SQL
  
      def get_estadisticas(self, db, videollamada_id: UUID) -> dict:
          # Obtiene estadísticas completas
  ```

### JWT Authentication
- **`src/utils/jitsi_jwt.py`**
  ```python
  def generate_jitsi_token(
      user_id: UUID,
      room_name: str,
      display_name: str,
      moderator: bool = False
  ) -> str:
      # Genera JWT para autenticación en Jitsi
  
  def validate_jitsi_token(token: str) -> dict:
      # Valida y decodifica token
  ```

---

## 🔧 Uso y Ejemplos

### 1. Crear una Videollamada

```python
from src.crud.communication.videollamada import CRUDVideollamada
from src.enums.communication.videollamada_enums import TipoLlamada

crud_videollamada = CRUDVideollamada()

videollamada = crud_videollamada.create_videollamada(
    db=db,
    jitsi_room_name="clase-matematicas-2024",  # Nombre único
    tipo_llamada=TipoLlamada.VIDEO,
    iniciador_id=docente.usuario_id,
    sala_chat_id=sala.id,
    configuracion={
        "max_participantes": 30,
        "permitir_grabacion": True,
        "calidad_video": "HD",
        "idioma": "es"
    }
)
```

### 2. Generar Token JWT para Frontend

```python
from src.utils.jitsi_jwt import generate_jitsi_token

token = generate_jitsi_token(
    user_id=usuario.usuario_id,
    room_name=videollamada.jitsi_room_name,
    display_name=f"{usuario.nombres} {usuario.apellidos}",
    moderator=(usuario.rol == "DOCENTE")
)

# Retornar al frontend junto con room_name
return {
    "jitsi_room_name": videollamada.jitsi_room_name,
    "jwt_token": token,
    "jitsi_domain": "meet.jit.si"  # o tu servidor Jitsi
}
```

### 3. Consultar Videollamadas Activas

```sql
-- SQL Directo
SELECT * FROM videollamadas_activas;

-- O con función de estadísticas
SELECT get_estadisticas_videollamada('uuid-videollamada');
```

```python
# Python con CRUD
videollamadas_activas = crud_videollamada.get_activas(db)

for v in videollamadas_activas:
    stats = crud_videollamada.get_estadisticas(db, v.id)
    print(f"Sala: {v.jitsi_room_name}")
    print(f"Participantes: {stats['participantes_conectados']}")
```

### 4. Finalizar Videollamada

```python
# Opción 1: Con CRUD
result = crud_videollamada.finalizar_videollamada(
    db=db, 
    videollamada_id=videollamada.id
)

# Opción 2: Con función SQL directa
db.execute(
    select(finalizar_videollamada(videollamada.id))
)
```

### 5. Agregar Grabación

```python
from src.enums.communication.videollamada_enums import (
    FormatoGrabacion,
    CalidadGrabacion
)

grabacion = crud_videollamada.create_grabacion(
    db=db,
    videollamada_id=videollamada.id,
    titulo="Clase de Cálculo - Derivadas",
    archivo_url="https://storage.acadify.com/grabaciones/video123.mp4",
    thumbnail_url="https://storage.acadify.com/thumbnails/thumb123.jpg",
    formato=FormatoGrabacion.MP4,
    calidad=CalidadGrabacion.FHD,
    duracion_segundos=2700,  # 45 minutos
    tamano_bytes=524288000   # ~500 MB
)
```

---

## 🎯 Configuración de Jitsi Meet

### Opción 1: Usar Jitsi.org (Gratis)

```javascript
// Frontend - React
import { JitsiMeeting } from '@jitsi/react-sdk';

function VideoCallRoom({ roomName, jwt }) {
  return (
    <JitsiMeeting
      domain="meet.jit.si"
      roomName={roomName}
      jwt={jwt}
      configOverwrite={{
        startWithAudioMuted: true,
        disableModeratorIndicator: false,
        startScreenSharing: false,
        enableEmailInStats: false
      }}
      interfaceConfigOverwrite={{
        DISABLE_JOIN_LEAVE_NOTIFICATIONS: true,
        SHOW_JITSI_WATERMARK: false,
        TOOLBAR_BUTTONS: [
          'microphone', 'camera', 'closedcaptions', 'desktop',
          'fullscreen', 'fodeviceselection', 'hangup', 'chat',
          'recording', 'sharedvideo', 'settings', 'raisehand',
          'videoquality', 'filmstrip', 'stats', 'shortcuts',
          'tileview', 'download', 'help', 'mute-everyone'
        ]
      }}
      onApiReady={(externalApi) => {
        // API de Jitsi disponible
        console.log('Jitsi API Ready');
      }}
    />
  );
}
```

### Opción 2: Servidor Propio

```yaml
# docker-compose.yml para Jitsi
version: '3.5'
services:
    web:
        image: jitsi/web:latest
        ports:
            - '8443:443'
        environment:
            - ENABLE_AUTH=1
            - ENABLE_GUESTS=0
            - AUTH_TYPE=jwt
            - JWT_APP_ID=acadify
            - JWT_APP_SECRET=tu_secret_key
```

---

## 📊 Métricas y Estadísticas

### Estadísticas Disponibles

```sql
-- Por videollamada
SELECT get_estadisticas_videollamada('uuid');

-- Videollamadas activas con participantes
SELECT * FROM videollamadas_activas;

-- Top usuarios por tiempo en videollamadas
SELECT 
    u.nombres,
    u.apellidos,
    SUM(vp.duracion_segundos) / 3600.0 AS horas_total,
    COUNT(DISTINCT vp.videollamada_id) AS total_videollamadas
FROM videollamadas_participantes vp
JOIN "Usuario" u ON vp.usuario_id = u.usuario_id
GROUP BY u.usuario_id, u.nombres, u.apellidos
ORDER BY horas_total DESC
LIMIT 10;

-- Calidad promedio de conexión
SELECT 
    calidad_conexion,
    COUNT(*) AS total_sesiones,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS porcentaje
FROM videollamadas_participantes
WHERE calidad_conexion IS NOT NULL
GROUP BY calidad_conexion
ORDER BY 
    CASE calidad_conexion
        WHEN 'excelente' THEN 1
        WHEN 'buena' THEN 2
        WHEN 'regular' THEN 3
        WHEN 'mala' THEN 4
    END;
```

---

## 🚀 Próximos Pasos

### FASE 2.1 - API Endpoints ⏳
- [ ] Crear endpoint `POST /api/videollamadas/` - Iniciar videollamada
- [ ] Crear endpoint `GET /api/videollamadas/{id}` - Obtener detalles
- [ ] Crear endpoint `POST /api/videollamadas/{id}/join` - Unirse a sala
- [ ] Crear endpoint `POST /api/videollamadas/{id}/leave` - Salir de sala
- [ ] Crear endpoint `POST /api/videollamadas/{id}/finalize` - Finalizar
- [ ] Crear endpoint `GET /api/videollamadas/{id}/stats` - Estadísticas
- [ ] Crear endpoint `GET /api/videollamadas/active` - Listar activas
- [ ] Probar con `scripts/test_crud_videollamadas.py`

### FASE 2.2 - Frontend Integration ⏳
- [ ] Instalar `@jitsi/react-sdk` o usar IFrame API
- [ ] Crear componente `<JitsiMeeting />`
- [ ] Crear componente `<VideoCallWindow />`
- [ ] Crear componente `<CallControls />`
- [ ] Integrar JWT authentication
- [ ] Conectar con backend API
- [ ] Implementar reconexión automática
- [ ] Agregar indicadores de calidad de conexión

### FASE 2.3 - Grabaciones 📹
- [ ] Configurar Jibri (Jitsi Broadcasting Infrastructure)
- [ ] Implementar almacenamiento S3/MinIO
- [ ] Crear endpoints de gestión de grabaciones
- [ ] Implementar procesamiento asíncrono
- [ ] Agregar generación de thumbnails
- [ ] Implementar transcripción con IA (Whisper)
- [ ] Implementar resumen con IA (GPT)

---

## ✅ Checklist de Verificación

- [x] ✅ Tablas creadas en PostgreSQL
- [x] ✅ ENUMs definidos correctamente
- [x] ✅ Índices optimizados
- [x] ✅ Funciones SQL operativas
- [x] ✅ Trigger automático configurado
- [x] ✅ Vista de videollamadas activas
- [x] ✅ Modelos Python con Jitsi
- [x] ✅ ENUMs Python con validaciones
- [x] ✅ Schemas Pydantic completos
- [x] ✅ CRUD operations implementados
- [x] ✅ JWT utilities disponibles
- [x] ✅ Scripts de setup documentados
- [ ] ⏳ API endpoints REST
- [ ] ⏳ Frontend components
- [ ] ⏳ Tests de integración
- [ ] ⏳ Documentación de API

---

## 📝 Notas Técnicas

### Decisión: Jitsi vs WebRTC Puro

**Elegido: Jitsi Meet ✅**

**Razones:**
1. **Escalabilidad**: 75-200+ usuarios vs 4-8 en P2P
2. **Educación**: Diseñado para escenarios educativos
3. **Funcionalidades**: Grabación, transcripción, chat integrados
4. **Infraestructura**: JWT ya implementado en el proyecto
5. **Costo**: Gratis con jitsi.org o self-hosted
6. **Mantenimiento**: Menos código custom, más estable
7. **Mobile**: Apps nativas disponibles
8. **Calidad**: SFU optimizado para múltiples participantes

### Arquitectura SFU (Selective Forwarding Unit)

```
┌─────────────┐
│  Docente    │───┐
└─────────────┘   │
                  ▼
┌─────────────┐  ┌──────────────┐  ┌─────────────┐
│ Estudiante1 │◄─┤  Jitsi SFU   │─►│ Estudiante2 │
└─────────────┘  └──────────────┘  └─────────────┘
                  ▲
┌─────────────┐   │
│ Estudiante3 │───┘
└─────────────┘

- Cada usuario envía 1 stream al servidor
- Servidor reenvía N streams a cada participante
- Bandwidth: O(N) en lugar de O(N²) en P2P
```

### Campos JSON Configuración

```json
{
  "max_participantes": 50,
  "permitir_grabacion": true,
  "calidad_video": "HD",
  "idioma": "es",
  "habilitar_chat": true,
  "habilitar_pizarra": true,
  "permitir_compartir_pantalla": true,
  "requerir_moderador_para_iniciar": false,
  "sala_espera_habilitada": true,
  "timeout_inactividad_minutos": 60,
  "notificar_entrada_salida": true,
  "tema_personalizado": {
    "color_primario": "#1a73e8",
    "logo_url": "https://acadify.com/logo.png"
  }
}
```

---

## 🔗 Referencias

- [Jitsi Meet Handbook](https://jitsi.github.io/handbook/)
- [Jitsi IFrame API](https://jitsi.github.io/handbook/docs/dev-guide/dev-guide-iframe)
- [JWT Authentication](https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker#authentication)
- [@jitsi/react-sdk](https://www.npmjs.com/package/@jitsi/react-sdk)
- [Jibri Recording](https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker#jibri)

---

**Documento actualizado:** 9 de Noviembre, 2025  
**Autor:** AI Assistant  
**Estado del Proyecto:** Backend DB Completo ✅ → API Endpoints Pendiente ⏳
