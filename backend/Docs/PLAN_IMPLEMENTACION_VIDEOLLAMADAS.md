# 🚀 PLAN DE IMPLEMENTACIÓN - SISTEMA DE VIDEOLLAMADAS + VOZ + IA

**Proyecto**: Acadify - Sistema de Comunicación Avanzado  
**Fecha Inicio**: 1 de Noviembre de 2025  
**Duración Estimada**: 12-15 días laborales  
**Arquitecto**: Sistema de Videollamadas con IA  
**Versión**: 1.0

---

## 📋 TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Objetivos y Alcance](#objetivos-y-alcance)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Stack Tecnológico](#stack-tecnológico)
5. [Fases de Implementación](#fases-de-implementación)
6. [Principios de Desarrollo](#principios-de-desarrollo)
7. [Plan Detallado por Tarea](#plan-detallado-por-tarea)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Plan](#deployment-plan)
10. [Risks & Mitigation](#risks--mitigation)

---

## 🎯 RESUMEN EJECUTIVO

### **Objetivo Principal**
Implementar un sistema completo de videollamadas y llamadas de voz integrado con inteligencia artificial (Rutilio) que permita:
- 📹 Videollamadas HD multi-participante
- 🎙️ Llamadas de voz (audio-only)
- 🤖 Asistente IA en llamadas (@Rutilio)
- 📝 Transcripción automática en tiempo real
- 💾 Grabación y almacenamiento
- 📊 Analytics y reportes
- 🔔 Notificaciones inteligentes

### **Métricas de Éxito**
| Métrica | Target | Medición |
|---------|--------|----------|
| **Code Coverage** | > 85% | pytest-cov |
| **Test Pass Rate** | 100% | CI/CD Pipeline |
| **API Response Time** | < 200ms | Prometheus |
| **WebSocket Latency** | < 100ms | Custom metrics |
| **Jitsi Connection Success** | > 99% | Analytics |
| **IA Response Time** | < 3s | Monitoring |
| **User Satisfaction** | > 4.5/5 | Surveys |

### **Entregables**
✅ 36 tareas completadas  
✅ 100% test coverage en componentes críticos  
✅ Documentación completa (técnica + usuario)  
✅ Demo funcional  
✅ Deployment ready  

---

## 🎯 OBJETIVOS Y ALCANCE

### **Objetivos de Negocio**
1. ✅ Mejorar colaboración entre estudiantes/profesores
2. ✅ Reducir dependencia de herramientas externas (Zoom, Meet)
3. ✅ Integrar IA para mejorar experiencia educativa
4. ✅ Proporcionar analytics de participación
5. ✅ Accesibilidad con transcripciones automáticas

### **Objetivos Técnicos**
1. ✅ Sistema escalable (100+ usuarios simultáneos)
2. ✅ Alta disponibilidad (99.9% uptime)
3. ✅ Baja latencia (< 100ms WebSocket)
4. ✅ Arquitectura modular y mantenible
5. ✅ Clean Code + SOLID principles
6. ✅ Tests automatizados completos
7. ✅ Documentación exhaustiva

### **Alcance (IN SCOPE)**
✅ Videollamadas 1-a-1 y grupales  
✅ Llamadas de solo voz (audio-only)  
✅ Integración Jitsi Meet  
✅ WebSocket real-time  
✅ Rutilio IA en llamadas (@menciones)  
✅ Transcripción automática  
✅ Grabación de llamadas  
✅ Resumen automático post-llamada  
✅ Compartir pantalla  
✅ Chat durante llamada  
✅ Permisos y roles (admin/moderador)  
✅ Notificaciones  
✅ Analytics básicos  
✅ API REST + WebSocket  
✅ Frontend React  

### **Fuera de Alcance (OUT OF SCOPE)**
❌ Streaming a YouTube/Facebook (v2)  
❌ Virtual backgrounds con IA (v2)  
❌ Traducción simultánea multi-idioma (v2)  
❌ Transcripción en vivo en video (v2)  
❌ Integración con calendarios externos (v2)  
❌ Apps móviles nativas (v2)  
❌ WebRTC SFU custom (usamos Jitsi)  

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### **Diagrama de Arquitectura General**

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ JitsiMeetModal│  │ Transcripción│  │   Rutilio    │          │
│  │  Component   │  │   Component   │  │  Assistant   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                   │                 │
│         └──────────────────┴───────────────────┘                 │
│                            │                                     │
│                            ▼                                     │
│                   ┌────────────────┐                             │
│                   │  WebSocket     │                             │
│                   │  Connection    │                             │
│                   └────────────────┘                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ WSS + HTTPS
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │              API Layer (REST + WebSocket)              │     │
│  │  /videollamadas/iniciar  /videollamadas/unirse  ...    │     │
│  └──────────────┬─────────────────────────┬───────────────┘     │
│                 │                         │                      │
│                 ▼                         ▼                      │
│  ┌──────────────────────┐   ┌────────────────────────┐          │
│  │  Service Layer       │   │  WebSocket Manager     │          │
│  │  - VideollamadaSvc   │   │  - Broadcast events    │          │
│  │  - GrabacionSvc      │   │  - Presence tracking   │          │
│  │  - AnalyticsSvc      │   │  - Room management     │          │
│  └──────────┬───────────┘   └────────────┬───────────┘          │
│             │                            │                      │
│             ▼                            ▼                      │
│  ┌──────────────────────────────────────────────────┐          │
│  │              CRUD Layer (Repository)             │          │
│  │  - VideollamadaCRUD  - ParticipanteCRUD          │          │
│  └──────────────────┬───────────────────────────────┘          │
│                     │                                           │
│                     ▼                                           │
│  ┌──────────────────────────────────────────────────┐          │
│  │           Database Layer (SQLAlchemy)            │          │
│  │  Models: Videollamada, Participante, Grabacion   │          │
│  └──────────────────┬───────────────────────────────┘          │
└────────────────────┬┴───────────────────────────────────────────┘
                     │
                     ▼
       ┌──────────────────────────┐
       │   PostgreSQL Database    │
       │   - videollamadas        │
       │   - grabaciones          │
       │   - transcripciones      │
       └──────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    SERVICIOS EXTERNOS                            │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Jitsi Meet  │  │  OpenAI      │  │  Storage     │          │
│  │  - WebRTC    │  │  - Whisper   │  │  (S3/MinIO)  │          │
│  │  - Recording │  │  - GPT-4     │  │  - Videos    │          │
│  │  - Streaming │  │  - TTS       │  │  - Audios    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### **Flujo de Datos - Iniciar Videollamada**

```
Usuario A                Frontend              Backend              Jitsi           IA (Rutilio)
   │                        │                     │                   │                   │
   │  Click "Videollamada"  │                     │                   │                   │
   ├───────────────────────>│                     │                   │                   │
   │                        │                     │                   │                   │
   │                        │  POST /videollamadas/iniciar            │                   │
   │                        ├────────────────────>│                   │                   │
   │                        │                     │                   │                   │
   │                        │                     │  1. Validar permisos                  │
   │                        │                     │  2. Crear registro en BD              │
   │                        │                     │  3. Generar JWT token                 │
   │                        │                     │  4. Generar room_name                 │
   │                        │                     │                   │                   │
   │                        │  Response: {        │                   │                   │
   │                        │    jwt_token,       │                   │                   │
   │                        │    room_name,       │                   │                   │
   │                        │    jitsi_url        │                   │                   │
   │                        │  }                  │                   │                   │
   │                        │<────────────────────┤                   │                   │
   │                        │                     │                   │                   │
   │                        │  5. WS: broadcast "videollamada_iniciada"                   │
   │                        │     a participantes de sala              │                   │
   │                        │<────────────────────┤                   │                   │
   │                        │                     │                   │                   │
   │                        │  6. Abrir modal     │                   │                   │
   │  Modal Jitsi abierto   │  7. Init Jitsi API  │                   │                   │
   │<───────────────────────┤                     │                   │                   │
   │                        │                     │                   │                   │
   │                        │  8. Jitsi External API: join room       │                   │
   │                        ├─────────────────────┴──────────────────>│                   │
   │                        │                     │     (with JWT)    │                   │
   │                        │                     │                   │                   │
   │  Usuario en llamada    │<───────────────────────────────────────┤                   │
   │                        │                     │                   │                   │
   │                        │  9. WS: "user_joined_call"              │                   │
   │                        │<────────────────────┤                   │                   │
   │                        │                     │                   │                   │
   │  Dice "@Rutilio ayuda" │                     │                   │                   │
   │                        │  10. Detectar mención                   │                   │
   │                        ├────────────────────>│                   │                   │
   │                        │                     │  11. Transcribir audio (Whisper)      │
   │                        │                     ├───────────────────┴──────────────────>│
   │                        │                     │                   │  12. Generar respuesta (GPT-4)
   │                        │                     │                   │                   │
   │                        │                     │  13. TTS (Text-to-Speech)             │
   │                        │                     │<──────────────────────────────────────┤
   │                        │                     │                   │                   │
   │  Rutilio responde      │  14. Reproducir audio en Jitsi          │                   │
   │  con voz               │<────────────────────┤                   │                   │
   │<───────────────────────┤                     │                   │                   │
```

### **Modelo de Base de Datos**

```sql
-- ============================================
-- TABLA: videollamadas
-- ============================================
CREATE TABLE videollamadas (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jitsi_room_name VARCHAR(255) UNIQUE NOT NULL,
    
    -- Relaciones
    sala_chat_id UUID REFERENCES SalaChat(id) ON DELETE CASCADE,
    iniciada_por_id UUID REFERENCES Usuario(id),
    
    -- Configuración
    titulo VARCHAR(255),
    descripcion TEXT,
    tipo_llamada VARCHAR(20) NOT NULL CHECK (tipo_llamada IN ('video', 'audio', 'screen')),
    
    -- Estado
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (
        estado IN ('pendiente', 'activa', 'finalizada', 'cancelada', 'error')
    ),
    esta_activa BOOLEAN DEFAULT TRUE,
    
    -- Participantes
    participantes_ids TEXT[] DEFAULT '{}',
    max_participantes INTEGER DEFAULT 50,
    participantes_actuales INTEGER DEFAULT 0,
    
    -- Permisos y Moderación
    requiere_moderador BOOLEAN DEFAULT FALSE,
    moderadores_ids TEXT[] DEFAULT '{}',
    todos_pueden_compartir_pantalla BOOLEAN DEFAULT TRUE,
    todos_pueden_grabar BOOLEAN DEFAULT FALSE,
    
    -- Seguridad
    requiere_password BOOLEAN DEFAULT FALSE,
    password_encriptada VARCHAR(255),
    
    -- Grabación
    permite_grabar BOOLEAN DEFAULT FALSE,
    esta_grabando BOOLEAN DEFAULT FALSE,
    grabacion_iniciada_por_id UUID REFERENCES Usuario(id),
    url_grabacion TEXT,
    duracion_grabacion_segundos INTEGER,
    
    -- Transcripción y IA
    transcripcion_habilitada BOOLEAN DEFAULT TRUE,
    rutilio_habilitado BOOLEAN DEFAULT TRUE,
    rutilio_unido BOOLEAN DEFAULT FALSE,
    
    -- Métricas y Analytics
    fecha_inicio TIMESTAMPTZ,
    fecha_fin TIMESTAMPTZ,
    duracion_segundos INTEGER,
    pico_participantes INTEGER DEFAULT 0,
    total_mensajes_chat INTEGER DEFAULT 0,
    total_interacciones_ia INTEGER DEFAULT 0,
    
    -- Calidad de Conexión (promedio)
    calidad_audio_promedio DECIMAL(3,2),  -- 0.00 a 5.00
    calidad_video_promedio DECIMAL(3,2),  -- 0.00 a 5.00
    latencia_promedio_ms INTEGER,
    
    -- Metadatos flexibles (JSONB para extensibilidad)
    configuracion JSONB DEFAULT '{}'::jsonb,
    estadisticas JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Auditoría
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_eliminacion TIMESTAMPTZ,  -- Soft delete
    
    -- Índices
    CONSTRAINT videollamadas_duracion_check CHECK (duracion_segundos >= 0)
);

-- Índices para performance
CREATE INDEX idx_videollamadas_sala ON videollamadas(sala_chat_id);
CREATE INDEX idx_videollamadas_iniciada_por ON videollamadas(iniciada_por_id);
CREATE INDEX idx_videollamadas_estado ON videollamadas(estado);
CREATE INDEX idx_videollamadas_activas ON videollamadas(esta_activa) WHERE esta_activa = TRUE;
CREATE INDEX idx_videollamadas_fecha_inicio ON videollamadas(fecha_inicio);
CREATE INDEX idx_videollamadas_jitsi_room ON videollamadas(jitsi_room_name);

-- ============================================
-- TABLA: grabaciones_videollamadas
-- ============================================
CREATE TABLE grabaciones_videollamadas (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    videollamada_id UUID REFERENCES videollamadas(id) ON DELETE CASCADE,
    
    -- Archivo
    nombre_archivo VARCHAR(500) NOT NULL,
    url_archivo TEXT NOT NULL,
    url_thumbnail TEXT,
    
    -- Metadatos
    duracion_segundos INTEGER NOT NULL,
    tamano_bytes BIGINT NOT NULL,
    formato VARCHAR(10) DEFAULT 'mp4',
    resolucion VARCHAR(20),  -- '1920x1080', '1280x720', etc.
    fps INTEGER,
    codec_video VARCHAR(50),
    codec_audio VARCHAR(50),
    
    -- Procesamiento
    estado_procesamiento VARCHAR(20) DEFAULT 'procesando' CHECK (
        estado_procesamiento IN ('procesando', 'completado', 'error')
    ),
    progreso_procesamiento INTEGER DEFAULT 0,  -- 0-100
    
    -- Acceso y Permisos
    es_publica BOOLEAN DEFAULT FALSE,
    requiere_autenticacion BOOLEAN DEFAULT TRUE,
    usuarios_con_acceso TEXT[] DEFAULT '{}',
    
    -- Transcripción asociada
    transcripcion_id UUID,
    tiene_transcripcion BOOLEAN DEFAULT FALSE,
    
    -- Analytics
    total_reproducciones INTEGER DEFAULT 0,
    total_descargas INTEGER DEFAULT 0,
    
    -- Metadatos
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Auditoría
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_eliminacion TIMESTAMPTZ,
    fecha_expiracion TIMESTAMPTZ,  -- Auto-delete después de X días
    
    -- Índices
    CONSTRAINT grabaciones_duracion_check CHECK (duracion_segundos > 0),
    CONSTRAINT grabaciones_tamano_check CHECK (tamano_bytes > 0)
);

CREATE INDEX idx_grabaciones_videollamada ON grabaciones_videollamadas(videollamada_id);
CREATE INDEX idx_grabaciones_estado ON grabaciones_videollamadas(estado_procesamiento);

-- ============================================
-- TABLA: transcripciones_videollamadas
-- ============================================
CREATE TABLE transcripciones_videollamadas (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    videollamada_id UUID REFERENCES videollamadas(id) ON DELETE CASCADE,
    grabacion_id UUID REFERENCES grabaciones_videollamadas(id),
    
    -- Contenido
    transcripcion_completa TEXT NOT NULL,
    transcripcion_vtt TEXT,  -- Formato WebVTT para subtítulos
    transcripcion_srt TEXT,  -- Formato SRT
    idioma_detectado VARCHAR(10) DEFAULT 'es',
    
    -- Segmentos (timestamped)
    segmentos JSONB NOT NULL DEFAULT '[]'::jsonb,
    /* Formato de segmentos:
    [
        {
            "inicio": 0.5,
            "fin": 5.2,
            "texto": "Hola a todos",
            "speaker": "usuario_123",
            "confianza": 0.95
        },
        ...
    ]
    */
    
    -- Análisis con IA
    resumen_ia TEXT,
    temas_principales TEXT[],
    palabras_clave TEXT[],
    action_items JSONB DEFAULT '[]'::jsonb,
    decisiones_tomadas JSONB DEFAULT '[]'::jsonb,
    participantes_mas_activos JSONB DEFAULT '[]'::jsonb,
    
    -- Metadatos
    confianza_promedio DECIMAL(3,2),  -- 0.00 a 1.00
    total_palabras INTEGER,
    duracion_hablada_segundos INTEGER,
    
    -- Estado
    estado_procesamiento VARCHAR(20) DEFAULT 'procesando' CHECK (
        estado_procesamiento IN ('procesando', 'completado', 'error')
    ),
    
    -- Búsqueda (Full-Text Search)
    search_vector TSVECTOR,
    
    -- Auditoría
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    
    -- Índices
    CONSTRAINT transcripciones_confianza_check CHECK (confianza_promedio >= 0 AND confianza_promedio <= 1)
);

CREATE INDEX idx_transcripciones_videollamada ON transcripciones_videollamadas(videollamada_id);
CREATE INDEX idx_transcripciones_grabacion ON transcripciones_videollamadas(grabacion_id);
CREATE INDEX idx_transcripciones_search ON transcripciones_videollamadas USING GIN(search_vector);

-- Trigger para actualizar search_vector automáticamente
CREATE TRIGGER transcripciones_search_update
BEFORE INSERT OR UPDATE ON transcripciones_videollamadas
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search_vector, 'pg_catalog.spanish', transcripcion_completa);

-- ============================================
-- TABLA: interacciones_ia_videollamadas
-- ============================================
CREATE TABLE interacciones_ia_videollamadas (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    videollamada_id UUID REFERENCES videollamadas(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES Usuario(id),
    
    -- Interacción
    tipo_interaccion VARCHAR(50) NOT NULL CHECK (
        tipo_interaccion IN ('mencion', 'pregunta', 'comando', 'respuesta')
    ),
    
    -- Contenido
    texto_usuario TEXT NOT NULL,
    texto_ia TEXT NOT NULL,
    audio_usuario_url TEXT,
    audio_ia_url TEXT,
    
    -- Context
    timestamp_llamada INTERVAL,  -- Minuto:Segundo en la llamada
    contexto_previo JSONB,
    
    -- Métricas
    tiempo_respuesta_ms INTEGER,
    confianza_transcripcion DECIMAL(3,2),
    utilidad_respuesta INTEGER,  -- 1-5 (rating del usuario)
    
    -- Auditoría
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_interacciones_ia_videollamada ON interacciones_ia_videollamadas(videollamada_id);
CREATE INDEX idx_interacciones_ia_usuario ON interacciones_ia_videollamadas(usuario_id);

-- ============================================
-- TABLA: notificaciones_videollamadas
-- ============================================
CREATE TABLE notificaciones_videollamadas (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    videollamada_id UUID REFERENCES videollamadas(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES Usuario(id) ON DELETE CASCADE,
    
    -- Contenido
    tipo_notificacion VARCHAR(50) NOT NULL CHECK (
        tipo_notificacion IN (
            'invitacion',
            'llamada_iniciada',
            'usuario_unido',
            'llamada_finalizada',
            'grabacion_disponible',
            'transcripcion_lista',
            'resumen_disponible',
            'llamada_perdida'
        )
    ),
    titulo VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    
    -- Acción
    url_accion TEXT,
    accion_realizada BOOLEAN DEFAULT FALSE,
    
    -- Estado
    es_leida BOOLEAN DEFAULT FALSE,
    fecha_lectura TIMESTAMPTZ,
    
    -- Auditoría
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_expiracion TIMESTAMPTZ
);

CREATE INDEX idx_notif_videollamadas_usuario ON notificaciones_videollamadas(usuario_id);
CREATE INDEX idx_notif_videollamadas_leidas ON notificaciones_videollamadas(es_leida);
```

---

## 🛠️ STACK TECNOLÓGICO

### **Backend**
```yaml
Framework: FastAPI 0.104+
Language: Python 3.12+
Database: PostgreSQL 15+
ORM: SQLAlchemy 2.0+
Migrations: Alembic
WebSocket: FastAPI WebSocket + Python asyncio
Real-time: Custom WebSocket Manager
Authentication: JWT (python-jose)
Validation: Pydantic v2
Testing: pytest + pytest-asyncio + pytest-cov
API Docs: OpenAPI/Swagger (built-in FastAPI)
```

### **Frontend**
```yaml
Framework: React 18+ con TypeScript
State Management: React Context + Custom Hooks
WebSocket Client: native WebSocket API
HTTP Client: Fetch API / Axios
UI Components: Tailwind CSS + Heroicons
Jitsi Integration: Jitsi Meet External API
Audio Processing: Web Audio API
Testing: Vitest + React Testing Library + Playwright
Build Tool: Vite
```

### **Servicios Externos**
```yaml
Video Conferencing: Jitsi Meet (open source)
  - Self-hosted o meet.jit.si
  - WebRTC para P2P
  - Jibri para grabación
  - JWT Authentication

AI Services: OpenAI API
  - Whisper API: Speech-to-Text (transcripción)
  - GPT-4 Turbo: Generación de respuestas
  - TTS API: Text-to-Speech (voz de Rutilio)
  
Storage: MinIO / AWS S3
  - Grabaciones de video
  - Audios de transcripción
  - Thumbnails
  
Monitoring:
  - Logs: Python logging + file rotation
  - Metrics: Prometheus + Grafana (opcional v2)
  - Errors: Sentry (opcional v2)
```

### **Infraestructura**
```yaml
Deployment: Docker + Docker Compose
Reverse Proxy: Nginx
SSL/TLS: Let's Encrypt
Cache: Redis (para WebSocket state)
Queue: Celery + Redis (procesamiento async)
```

---

## 📊 PRINCIPIOS DE DESARROLLO

### **1. CLEAN CODE**

#### **Naming Conventions**
```python
# ✅ BUENO: Nombres descriptivos y claros
def iniciar_videollamada_en_sala(
    sala_id: UUID,
    usuario_id: UUID,
    tipo_llamada: TipoLlamada
) -> Videollamada:
    """
    Inicia una nueva videollamada en una sala de chat.
    
    Args:
        sala_id: ID de la sala donde se iniciará la llamada
        usuario_id: ID del usuario que inicia la llamada
        tipo_llamada: Tipo de llamada (video, audio, screen)
        
    Returns:
        Objeto Videollamada creado
        
    Raises:
        PermissionDenied: Si el usuario no tiene permisos
        SalaNotFound: Si la sala no existe
    """
    pass

# ❌ MALO: Nombres crípticos
def init_vc(s_id: str, u_id: str, t: str) -> dict:
    pass
```

#### **Funciones Pequeñas y Enfocadas**
```python
# ✅ BUENO: Una función, una responsabilidad
def validar_permisos_iniciar_llamada(usuario: Usuario, sala: SalaChat) -> bool:
    """Valida si el usuario puede iniciar llamadas en la sala."""
    participante = obtener_participante(usuario.id, sala.id)
    return participante.puede_iniciar_llamadas

def generar_nombre_sala_jitsi(sala_id: UUID) -> str:
    """Genera un nombre único para la sala de Jitsi."""
    timestamp = int(datetime.now().timestamp())
    random_suffix = secrets.token_hex(4)
    return f"acadify_{sala_id}_{timestamp}_{random_suffix}"

def crear_jwt_token_jitsi(
    room_name: str,
    user_id: UUID,
    user_name: str,
    is_moderator: bool
) -> str:
    """Genera un JWT token para autenticación en Jitsi."""
    # Implementación...
    pass

# ❌ MALO: Función que hace muchas cosas
def start_call(user, sala):
    # Valida permisos
    # Crea sala
    # Genera token
    # Envía notificaciones
    # Actualiza estadísticas
    # 200 líneas de código...
    pass
```

#### **Comentarios Significativos**
```python
# ✅ BUENO: Comentarios que explican el "por qué"
def calcular_duracion_llamada(videollamada: Videollamada) -> int:
    """
    Calcula la duración de la videollamada en segundos.
    
    Nota: Si la llamada aún está activa (fecha_fin es None),
    calcula la duración desde el inicio hasta ahora.
    Esto es útil para mostrar duración en tiempo real.
    """
    if videollamada.fecha_fin is None:
        # Llamada activa - calcular desde inicio hasta ahora
        return int((datetime.utcnow() - videollamada.fecha_inicio).total_seconds())
    
    # Llamada finalizada - usar duración guardada
    return videollamada.duracion_segundos

# ❌ MALO: Comentarios obvios
def sumar(a, b):
    # Suma a y b
    return a + b
```

### **2. SOLID PRINCIPLES**

#### **S - Single Responsibility Principle**
```python
# ✅ BUENO: Cada clase tiene una única responsabilidad

class VideollamadaRepository:
    """Responsable SOLO de acceso a datos de videollamadas."""
    
    def get(self, videollamada_id: UUID) -> Optional[Videollamada]:
        pass
    
    def create(self, videollamada_data: VideollamadaCreate) -> Videollamada:
        pass
    
    def update(self, videollamada_id: UUID, data: VideollamadaUpdate) -> Videollamada:
        pass

class VideollamadaService:
    """Responsable SOLO de lógica de negocio de videollamadas."""
    
    def __init__(self, repo: VideollamadaRepository):
        self.repo = repo
    
    def iniciar_llamada(self, sala_id: UUID, usuario_id: UUID) -> Videollamada:
        # Validaciones
        # Lógica de negocio
        # Llamadas al repositorio
        pass

class NotificacionService:
    """Responsable SOLO de enviar notificaciones."""
    
    def notificar_llamada_iniciada(self, videollamada: Videollamada):
        pass

# ❌ MALO: Clase que hace todo
class VideollamadaManager:
    """Hace CRUD, lógica de negocio, notificaciones, analytics, etc."""
    pass
```

#### **O - Open/Closed Principle**
```python
# ✅ BUENO: Abierto para extensión, cerrado para modificación

from abc import ABC, abstractmethod

class TranscripcionStrategy(ABC):
    """Interface para estrategias de transcripción."""
    
    @abstractmethod
    async def transcribir(self, audio_url: str) -> str:
        pass

class WhisperTranscripcion(TranscripcionStrategy):
    """Implementación usando OpenAI Whisper."""
    
    async def transcribir(self, audio_url: str) -> str:
        # Implementación con Whisper API
        pass

class GoogleSpeechTranscripcion(TranscripcionStrategy):
    """Implementación usando Google Speech-to-Text."""
    
    async def transcribir(self, audio_url: str) -> str:
        # Implementación con Google API
        pass

class TranscripcionService:
    """Servicio que usa estrategia de transcripción."""
    
    def __init__(self, strategy: TranscripcionStrategy):
        self.strategy = strategy
    
    async def transcribir_audio(self, audio_url: str) -> str:
        return await self.strategy.transcribir(audio_url)

# Uso - fácil cambiar la estrategia sin modificar el servicio
servicio = TranscripcionService(WhisperTranscripcion())
# O cambiar a:
# servicio = TranscripcionService(GoogleSpeechTranscripcion())
```

#### **L - Liskov Substitution Principle**
```python
# ✅ BUENO: Subclases pueden sustituir a clase base

class Notificador(ABC):
    """Clase base para notificadores."""
    
    @abstractmethod
    async def enviar(self, usuario_id: UUID, mensaje: str) -> bool:
        pass

class EmailNotificador(Notificador):
    """Envía notificaciones por email."""
    
    async def enviar(self, usuario_id: UUID, mensaje: str) -> bool:
        # Enviar email
        return True

class WebSocketNotificador(Notificador):
    """Envía notificaciones vía WebSocket."""
    
    async def enviar(self, usuario_id: UUID, mensaje: str) -> bool:
        # Enviar por WebSocket
        return True

class PushNotificador(Notificador):
    """Envía notificaciones push."""
    
    async def enviar(self, usuario_id: UUID, mensaje: str) -> bool:
        # Enviar push notification
        return True

# Uso - cualquier notificador funciona igual
async def notificar_usuarios(usuarios: List[UUID], mensaje: str, notificador: Notificador):
    for usuario_id in usuarios:
        await notificador.enviar(usuario_id, mensaje)
```

#### **I - Interface Segregation Principle**
```python
# ✅ BUENO: Interfaces específicas y pequeñas

class LlamadaReader(Protocol):
    """Interface solo para leer videollamadas."""
    def get(self, id: UUID) -> Optional[Videollamada]: ...
    def get_activas(self) -> List[Videollamada]: ...

class LlamadaWriter(Protocol):
    """Interface solo para escribir videollamadas."""
    def create(self, data: VideollamadaCreate) -> Videollamada: ...
    def update(self, id: UUID, data: VideollamadaUpdate) -> Videollamada: ...
    def delete(self, id: UUID) -> None: ...

class LlamadaAnalytics(Protocol):
    """Interface solo para analytics."""
    def get_estadisticas(self, sala_id: UUID) -> Dict: ...
    def get_duracion_promedio(self) -> float: ...

# ❌ MALO: Interface gigante que obliga a implementar todo
class IVideollamadaRepository(Protocol):
    def get(self, id: UUID) -> Optional[Videollamada]: ...
    def create(self, data: VideollamadaCreate) -> Videollamada: ...
    def update(self, id: UUID, data: VideollamadaUpdate) -> Videollamada: ...
    def delete(self, id: UUID) -> None: ...
    def get_activas(self) -> List[Videollamada]: ...
    def get_estadisticas(self, sala_id: UUID) -> Dict: ...
    def get_duracion_promedio(self) -> float: ...
    def export_to_csv(self) -> str: ...
    def import_from_json(self, data: str) -> None: ...
    # 20 métodos más...
```

#### **D - Dependency Inversion Principle**
```python
# ✅ BUENO: Depender de abstracciones, no de implementaciones concretas

from abc import ABC, abstractmethod

class IStorageService(ABC):
    """Abstracción para servicio de almacenamiento."""
    
    @abstractmethod
    async def upload(self, file: bytes, filename: str) -> str:
        """Sube un archivo y retorna la URL."""
        pass
    
    @abstractmethod
    async def delete(self, url: str) -> bool:
        """Elimina un archivo."""
        pass

class S3StorageService(IStorageService):
    """Implementación concreta con AWS S3."""
    
    async def upload(self, file: bytes, filename: str) -> str:
        # Lógica de S3
        pass
    
    async def delete(self, url: str) -> bool:
        # Lógica de S3
        pass

class MinIOStorageService(IStorageService):
    """Implementación concreta con MinIO."""
    
    async def upload(self, file: bytes, filename: str) -> str:
        # Lógica de MinIO
        pass
    
    async def delete(self, url: str) -> bool:
        # Lógica de MinIO
        pass

class GrabacionService:
    """Servicio que depende de la abstracción, no de implementación."""
    
    def __init__(self, storage: IStorageService):
        self.storage = storage  # Depende de la abstracción
    
    async def guardar_grabacion(self, video: bytes, nombre: str) -> str:
        url = await self.storage.upload(video, nombre)
        return url

# Uso - fácil cambiar la implementación
# Con S3:
servicio = GrabacionService(S3StorageService())

# O con MinIO:
servicio = GrabacionService(MinIOStorageService())

# ❌ MALO: Depender directamente de implementación concreta
class GrabacionService:
    def __init__(self):
        self.s3_client = boto3.client('s3')  # Acoplamiento fuerte
```

### **3. DRY (Don't Repeat Yourself)**

```python
# ✅ BUENO: Extraer lógica común
class BaseService:
    """Servicio base con lógica común."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validar_existe(self, model, id: UUID, error_message: str):
        """Valida que un registro exista o lanza excepción."""
        obj = self.db.query(model).filter(model.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=error_message)
        return obj
    
    def validar_permisos(self, usuario: Usuario, accion: str):
        """Valida permisos de usuario."""
        if not usuario.tiene_permiso(accion):
            raise HTTPException(status_code=403, detail="Sin permisos")

class VideollamadaService(BaseService):
    """Hereda lógica común."""
    
    def get_videollamada(self, id: UUID) -> Videollamada:
        return self.validar_existe(
            Videollamada,
            id,
            "Videollamada no encontrada"
        )

# ❌ MALO: Repetir la misma lógica en cada servicio
class VideollamadaService:
    def get(self, id: UUID):
        obj = self.db.query(Videollamada).filter(Videollamada.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="No encontrado")
        return obj

class GrabacionService:
    def get(self, id: UUID):
        obj = self.db.query(Grabacion).filter(Grabacion.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="No encontrado")
        return obj
```

### **4. TESTING BEST PRACTICES**

```python
# ✅ BUENO: Tests organizados con AAA pattern (Arrange, Act, Assert)

def test_iniciar_videollamada_exitoso():
    """
    Test: Un usuario con permisos puede iniciar una videollamada.
    
    Given: Un usuario con permisos en una sala
    When: Inicia una videollamada
    Then: Se crea la videollamada correctamente
    """
    # Arrange - Preparar datos de prueba
    db = crear_db_test()
    sala = crear_sala_test(db)
    usuario = crear_usuario_test(db)
    agregar_participante_con_permisos(db, sala, usuario)
    servicio = VideollamadaService(db)
    
    # Act - Ejecutar la acción
    videollamada = servicio.iniciar_llamada(
        sala_id=sala.id,
        usuario_id=usuario.id,
        tipo="video"
    )
    
    # Assert - Verificar resultados
    assert videollamada is not None
    assert videollamada.sala_id == sala.id
    assert videollamada.iniciada_por_id == usuario.id
    assert videollamada.tipo_llamada == "video"
    assert videollamada.esta_activa is True
    assert videollamada.jitsi_room_name.startswith("acadify_")

def test_iniciar_videollamada_sin_permisos():
    """
    Test: Un usuario sin permisos NO puede iniciar videollamada.
    
    Given: Un usuario sin permisos en una sala
    When: Intenta iniciar una videollamada
    Then: Se lanza excepción PermissionDenied
    """
    # Arrange
    db = crear_db_test()
    sala = crear_sala_test(db)
    usuario = crear_usuario_test(db)
    # No agregamos permisos
    servicio = VideollamadaService(db)
    
    # Act & Assert
    with pytest.raises(PermissionDenied) as exc_info:
        servicio.iniciar_llamada(
            sala_id=sala.id,
            usuario_id=usuario.id,
            tipo="video"
        )
    
    assert "Sin permisos" in str(exc_info.value)
```

---

## 📅 FASES DE IMPLEMENTACIÓN

### **FASE 0: Setup y Configuración (1 día)**
- ⚙️ Configurar variables de entorno
- ⚙️ Setup Jitsi (self-hosted o cloud)
- ⚙️ Configurar OpenAI API keys
- ⚙️ Setup storage (MinIO/S3)
- ⚙️ Configurar CI/CD pipeline
- ⚙️ Setup testing environment

### **FASE 1: Backend - Fundamentos (3 días)**
- 🗄️ Migraciones de base de datos (Alembic)
- 📊 Modelos SQLAlchemy
- 📝 Schemas Pydantic
- 🔧 CRUD operations
- 🔐 JWT generator para Jitsi
- 🌐 API endpoints básicos

### **FASE 2: Backend - WebSocket y Tiempo Real (2 días)**
- ⚡ Extender WebSocket Manager
- 📡 Eventos de videollamadas
- 🔔 Sistema de notificaciones
- 👥 Gestión de participantes
- 📊 Métricas en tiempo real

### **FASE 3: Backend - Integración IA (3 días)**
- 🤖 Transcripción con Whisper
- 🤖 Rutilio en videollamadas
- 🤖 Resumen automático post-llamada
- 🎙️ Text-to-Speech para Rutilio
- 💬 Context-aware responses

### **FASE 4: Backend - Grabación y Storage (2 días)**
- 🎥 Servicio de grabación
- 💾 Integración con storage
- 📹 Procesamiento de videos
- 🖼️ Generación de thumbnails
- 📊 Analytics de grabaciones

### **FASE 5: Frontend - Componentes Base (2 días)**
- 🎨 VideollamadaButton
- 🎨 JitsiMeetModal
- 🎨 ParticipantesCallList
- 🎨 Hook useVideollamada
- 🎨 Integración en ChatView

### **FASE 6: Frontend - IA y Transcripción (2 días)**
- 🎨 TranscripcionLive component
- 🎨 RutilioAssistant component
- 🎨 Voice activation UI
- 🎨 Resumen post-llamada view

### **FASE 7: Testing Completo (3 días)**
- 🧪 Unit tests (modelos, CRUD, services)
- 🧪 Integration tests (API, WebSocket)
- 🧪 E2E tests (frontend)
- 🧪 Performance tests
- 🧪 Manual QA

### **FASE 8: Documentación y Entrega (1 día)**
- 📄 Documentación técnica
- 📄 API documentation
- 📄 User guide
- 📄 Deployment guide
- 📄 Reporte final

**Total Estimado**: **12-15 días laborales**

---

