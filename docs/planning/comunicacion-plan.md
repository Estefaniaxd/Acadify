# 🚀 PLAN EXHAUSTIVO: SISTEMA DE COMUNICACIÓN EN TIEMPO REAL - ACADIFY

## 📋 ÍNDICE

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Análisis del Estado Actual](#análisis-del-estado-actual)
3. [Arquitectura Propuesta](#arquitectura-propuesta)
4. [Tecnologías y Stack Técnico](#tecnologías-y-stack-técnico)
5. [Plan de Desarrollo Detallado](#plan-de-desarrollo-detallado)
6. [Testing y QA](#testing-y-qa)
7. [Deployment y Escalabilidad](#deployment-y-escalabilidad)
8. [Timeline y Estimaciones](#timeline-y-estimaciones)
9. [Riesgos y Mitigación](#riesgos-y-mitigación)

---

## 📊 RESUMEN EJECUTIVO

### Objetivo
Desarrollar un sistema de comunicación en tiempo real de clase mundial para Acadify que incluya:
- ✅ Chats privados y grupales
- ✅ Mensajería instantánea con WebSockets
- ✅ Videollamadas y llamadas de voz
- ✅ Compartir archivos multimedia
- ✅ Notificaciones push en tiempo real
- ✅ Integración con IA (Rutilio)

### Alcance del Proyecto
- **Backend**: FastAPI + WebSockets + Redis + PostgreSQL
- **Comunicación en tiempo real**: WebSocket bidireccional
- **Videollamadas**: WebRTC (Jitsi Meet / LiveKit / Agora)
- **Tiempo estimado**: 4-6 semanas de desarrollo intensivo
- **Complejidad**: Alta (⭐⭐⭐⭐⭐)

---

## 🔍 ANÁLISIS DEL ESTADO ACTUAL

### ✅ Lo que YA está implementado

#### 1. **Modelos de Base de Datos**
```python
# src/models/communication/chat.py
- SalaChat: Sistema de salas con tipos (curso, grupo, tarea, privado, general)
- ParticipanteSala: Gestión de participantes con roles
- MensajeChat: Mensajes con tipos, hilos, reacciones, menciones
- LecturaMensaje: Control de mensajes leídos
- Notificacion: Sistema de notificaciones
- ConfiguracionNotificaciones: Preferencias por usuario
```

**⚠️ PROBLEMA DETECTADO**: Existe duplicación de modelos:
- `chat.py` tiene `MensajeChat` y `SalaChat`
- `mensaje.py` tiene `Mensaje` con referencia a `ChatGrupo`
- `chat_grupo.py` tiene `ChatGrupo` con otra estructura

**ACCIÓN REQUERIDA**: Unificar modelos antes de continuar.

#### 2. **WebSocket Manager**
```python
# src/services/websocket_manager.py
- ConnectionManager: Gestión de conexiones en memoria
- WebSocketHandler: Manejo de eventos
- Soporte para: envío de mensajes, join/leave sala, typing indicators, reacciones
```

**✅ FORTALEZAS**:
- Arquitectura clara con separación de responsabilidades
- Eventos bien definidos
- Manejo de presencia básico

**⚠️ LIMITACIONES**:
- Conexiones en memoria (no escala a múltiples instancias)
- No hay persistencia de estado
- Falta manejo de reconexión automática
- No hay rate limiting

#### 3. **CRUD Operations**
```python
# src/crud/communication/chat.py
- CRUDSalaChat: Operaciones de salas
- CRUDParticipanteSala: Gestión de participantes
- CRUDMensaje: CRUD de mensajes con procesamiento de menciones
- CRUDLecturaMensaje: Control de lecturas
- CRUDNotificacion: Sistema de notificaciones
```

**✅ FORTALEZAS**:
- SOLID principles aplicados
- Métodos bien organizados
- Filtros avanzados implementados

#### 4. **API REST Endpoints**
```python
# src/api/routes/communication/chat.py
- Endpoints completos para salas, mensajes, participantes
- WebSocket endpoint básico
- Sistema de notificaciones
```

**✅ COBERTURA**: ~80% de funcionalidad REST implementada

### ❌ Lo que FALTA implementar

1. **Videollamadas y Audio**
   - ❌ No hay integración con WebRTC
   - ❌ No hay servidor de señalización
   - ❌ No hay STUN/TURN servers configurados

2. **Archivos Multimedia**
   - ❌ Upload de archivos sin implementar completamente
   - ❌ No hay generación de thumbnails
   - ❌ No hay previews de imágenes
   - ❌ Falta soporte para archivos grandes (chunked upload)

3. **Escalabilidad**
   - ❌ WebSocket manager usa memoria local
   - ❌ No hay soporte multi-instancia con Redis
   - ❌ Falta implementación de pub/sub para broadcast

4. **Features Avanzadas**
   - ❌ Mensajes de voz
   - ❌ Compartir pantalla
   - ❌ Formateo de texto enriquecido
   - ❌ Preview de enlaces
   - ❌ Búsqueda full-text
   - ❌ Encriptación E2E

5. **Optimizaciones**
   - ❌ Virtual scrolling en frontend
   - ❌ Cache agresivo de mensajes
   - ❌ Compresión de mensajes WebSocket
   - ❌ Batch updates

6. **Testing**
   - ❌ Tests unitarios para comunicación
   - ❌ Tests de integración WebSocket
   - ❌ Tests E2E
   - ❌ Load testing

---

## 🏗️ ARQUITECTURA PROPUESTA

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React/Vue)                     │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │   Chat UI   │  │  Video Call  │  │  File Upload/Preview   │ │
│  └──────┬──────┘  └──────┬───────┘  └────────────┬───────────┘ │
│         │                 │                        │              │
└─────────┼─────────────────┼────────────────────────┼─────────────┘
          │                 │                        │
          ▼                 ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NGINX / Load Balancer                         │
│              (Sticky Sessions para WebSocket)                    │
└─────────────────────────────────────────────────────────────────┘
          │                 │                        │
          ▼                 ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND - FastAPI                           │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              WebSocket Server (WS)                       │   │
│  │  - Connection Manager (Redis-backed)                     │   │
│  │  - Message Handler                                       │   │
│  │  - Presence Tracking                                     │   │
│  │  - Room Management                                       │   │
│  └────────────┬────────────────────────────────────────────┘   │
│               │                                                  │
│  ┌────────────▼─────────────────────────────────────────────┐  │
│  │              REST API Endpoints                           │  │
│  │  - /api/communication/salas                              │  │
│  │  - /api/communication/mensajes                           │  │
│  │  - /api/communication/archivos                           │  │
│  │  - /api/communication/notificaciones                     │  │
│  └────────────┬─────────────────────────────────────────────┘  │
│               │                                                  │
└───────────────┼──────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                 │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ PostgreSQL   │  │    Redis     │  │  File Storage (S3)   │   │
│  │              │  │              │  │                       │   │
│  │ - Mensajes   │  │ - Sessions   │  │ - Archivos adjuntos  │   │
│  │ - Salas      │  │ - Presence   │  │ - Imágenes           │   │
│  │ - Usuarios   │  │ - Cache      │  │ - Videos             │   │
│  │ - Archivos   │  │ - Pub/Sub    │  │ - Documentos         │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────────┐
│                    SERVICIOS EXTERNOS                              │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ WebRTC (SFU) │  │  STUN/TURN   │  │  Push Notifications  │   │
│  │ Jitsi/LiveKit│  │   Servers    │  │   (FCM / APNS)       │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  OpenAI API  │  │   CDN        │  │   Monitoring         │   │
│  │  (Rutilio)   │  │ (CloudFlare) │  │ (Prometheus/Grafana) │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

### Flujo de Mensajes en Tiempo Real

```
Usuario A (Frontend)                                  Usuario B (Frontend)
       │                                                     │
       │ 1. Envía mensaje via WebSocket                     │
       ▼                                                     │
   WebSocket                                                 │
   Connection                                                │
       │                                                     │
       │ 2. Valida y autentica                              │
       ▼                                                     │
 WebSocketHandler                                            │
       │                                                     │
       │ 3. Procesa mensaje                                 │
       │    - Sanitiza contenido                            │
       │    - Detecta menciones                             │
       │    - Valida permisos                               │
       ▼                                                     │
    CRUD Mensaje                                             │
       │                                                     │
       │ 4. Persiste en DB                                  │
       ▼                                                     │
   PostgreSQL                                                │
       │                                                     │
       │ 5. Publica evento                                  │
       ▼                                                     │
  Redis Pub/Sub ─────────────────────────────────────────► ConnectionManager
       │                                                     │
       │ 6. Notifica a otras instancias                     │
       │                                                     │
       │                                           7. Broadcast a sala
       │                                                     ▼
       │                                              WebSocket Connection
       │                                                     │
       │                                           8. Envía a Usuario B
       │                                                     ▼
       │                                             Usuario B (Frontend)
       │                                             Actualiza UI en tiempo real
```

---

## 💻 TECNOLOGÍAS Y STACK TÉCNICO

### Backend

#### Core Framework
- **FastAPI** 0.104+
  - WebSocket support nativo
  - Async/await
  - Pydantic para validación
  - OpenAPI docs automática

#### Base de Datos
- **PostgreSQL** 15+
  - JSONB para metadatos flexibles
  - Full-text search para búsqueda de mensajes
  - Índices GiST para queries geoespaciales (si se necesita ubicación)
  - Índices compuestos para queries optimizadas

```sql
-- Índices críticos
CREATE INDEX idx_mensajes_sala_fecha ON mensajes(sala_id, fecha_creacion DESC);
CREATE INDEX idx_mensajes_usuario ON mensajes(usuario_id);
CREATE INDEX idx_mensajes_sala_no_leidos ON mensajes(sala_id) WHERE estado != 'leido';
CREATE INDEX idx_mensajes_fts ON mensajes USING gin(to_tsvector('spanish', contenido));
CREATE INDEX idx_participantes_sala ON participantes_sala(sala_id, usuario_id) WHERE esta_activo = true;
```

#### Cache y Pub/Sub
- **Redis** 7+
  - WebSocket connections tracking
  - Pub/Sub para multi-instancia broadcast
  - Cache de mensajes recientes
  - Presence tracking con TTL
  - Rate limiting

```python
# Estructura de datos en Redis
# Connections: Hash
"ws:connections:{usuario_id}" -> {
    "connection_id": "timestamp",
    ...
}

# Presence: String con TTL
"presence:{usuario_id}" -> "online" (TTL: 30s)

# Room participants: Set
"room:{sala_id}:participants" -> Set[usuario_id]

# Cache de mensajes recientes: List
"room:{sala_id}:messages:recent" -> [mensaje_id, ...]

# Rate limiting: String con TTL
"ratelimit:messages:{usuario_id}" -> count (TTL: 60s)
```

#### File Storage
- **Local Filesystem** (desarrollo)
  - Path: `/static/uploads/{tipo}/{año}/{mes}/{filename}`
  - Servido por FastAPI StaticFiles

- **AWS S3** / **MinIO** (producción)
  - Bucket organizado por tipo de archivo
  - Presigned URLs para acceso temporal
  - CDN para distribución global

#### WebRTC y Videollamadas

##### Opción 1: Jitsi Meet (RECOMENDADO para MVP)
**✅ PROS**:
- Open source y gratuito
- Infraestructura probada
- Fácil integración (iframe o React SDK)
- Auto-hosted o Jitsi Cloud
- Soporta grabación

**❌ CONTRAS**:
- Menos control sobre la UI
- Límites en customización
- Puede requerir servidores TURN propios para producción

**IMPLEMENTACIÓN**:
```python
# Backend endpoint para crear sala de videollamada
@router.post("/videocall/create")
async def create_videocall(sala_id: UUID, db: Session = Depends(get_db)):
    # Generar JWT token para Jitsi
    room_name = f"acadify_{sala_id}"
    jwt_token = generate_jitsi_jwt(room_name, user_info)
    
    return {
        "room_name": room_name,
        "jwt": jwt_token,
        "url": f"https://meet.jit.si/{room_name}"
    }
```

```javascript
// Frontend - React
import { JitsiMeeting } from '@jitsi/react-sdk';

<JitsiMeeting
    domain="meet.jit.si"
    roomName={roomName}
    jwt={jwtToken}
    configOverwrite={{
        startWithAudioMuted: true,
        disableModeratorIndicator: true,
        startScreenSharing: true,
        enableEmailInStats: false
    }}
    interfaceConfigOverwrite={{
        DISABLE_JOIN_LEAVE_NOTIFICATIONS: true
    }}
    onApiReady={(externalApi) => {
        // Manejar eventos
    }}
/>
```

##### Opción 2: LiveKit (ESCALABLE)
**✅ PROS**:
- Moderna, cloud-native
- SDKs para múltiples plataformas
- SFU de alto rendimiento
- Mejor para personalización

**❌ CONTRAS**:
- Más complejo de configurar
- Requiere servidor propio o LiveKit Cloud (de pago)

##### Opción 3: Agora (COMERCIAL)
**✅ PROS**:
- SDK muy robusto
- Soporte 24/7
- SDKs nativos (iOS, Android)
- Excelente calidad

**❌ CONTRAS**:
- De pago desde el inicio
- Lock-in con vendor

**RECOMENDACIÓN FINAL**: Jitsi Meet para MVP, migrar a LiveKit si se necesita más control.

#### IA Integration
- **OpenAI API** / **Anthropic Claude**
  - Rutilio: Asistente IA educativo
  - Context-aware responses
  - Rate limiting: 10 req/min por usuario

```python
async def process_rutilio_mention(mensaje: str, context: dict) -> str:
    """Procesar mención de Rutilio"""
    
    # Build context from conversation history
    conversation_history = await get_recent_messages(context['sala_id'], limit=10)
    
    # Call OpenAI API
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": RUTILIO_SYSTEM_PROMPT},
            *[{"role": "user" if m.usuario_id != "rutilio" else "assistant", 
               "content": m.contenido} for m in conversation_history],
            {"role": "user", "content": mensaje}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content
```

---

## 📅 PLAN DE DESARROLLO DETALLADO

### FASE 1: FUNDAMENTOS Y REFACTORING (Semana 1)

#### 🎯 Objetivos
- Resolver duplicaciones y problemas de arquitectura
- Establecer base sólida para desarrollo futuro
- Configurar entorno de desarrollo

#### Tareas Detalladas

##### 1.1 Auditoría y Limpieza de Código ⏱️ 1 día
```bash
# Acción
1. Analizar todos los archivos en /models/communication
2. Identificar modelos duplicados
3. Crear matriz de compatibilidad
4. Documentar decisiones

# Entregable
- COMMUNICATION_AUDIT_REPORT.md
- Diagrama ER unificado
```

##### 1.2 Unificación de Modelos ⏱️ 2 días
```python
# Decisión: Usar chat.py como base canónica

# Acción
1. Migrar datos de ChatGrupo/Mensaje a SalaChat/MensajeChat
2. Actualizar todas las referencias en CRUD
3. Actualizar schemas
4. Deprecar archivos antiguos

# Script de migración
"""
alembic revision --autogenerate -m "Unificar modelos de comunicación"
"""

# Validación
- Todos los tests pasan
- No hay referencias a modelos deprecated
- Migraciones reversibles
```

##### 1.3 Migración de Base de Datos ⏱️ 1 día
```python
# alembic/versions/xxx_unificar_comunicacion.py

def upgrade():
    # 1. Crear nuevas tablas
    op.create_table('salas_chat', ...)
    op.create_table('mensajes', ...)
    op.create_table('participantes_sala', ...)
    
    # 2. Migrar datos
    op.execute("""
        INSERT INTO salas_chat (id, nombre, tipo_sala, ...)
        SELECT chat_grupo_id, ..., 'grupo' 
        FROM ChatGrupo
    """)
    
    op.execute("""
        INSERT INTO mensajes (id, sala_id, contenido, ...)
        SELECT mensaje_id, chat_grupo_id, contenido, ...
        FROM Mensaje
    """)
    
    # 3. Crear índices
    op.create_index('idx_mensajes_sala_fecha', 'mensajes', 
                    ['sala_id', 'fecha_creacion'])
    op.create_index('idx_mensajes_fts', 'mensajes', 
                    [text('to_tsvector(\'spanish\', contenido)')], 
                    postgresql_using='gin')
    
    # 4. Eliminar tablas antiguas
    op.drop_table('ChatGrupo')
    op.drop_table('Mensaje')

def downgrade():
    # Reversión completa
    ...
```

##### 1.4 Mejorar Autenticación WebSocket ⏱️ 1 día
```python
# src/api/dependencies.py

async def get_current_user_websocket(
    token: str,
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Autenticar usuario en WebSocket
    
    Soporta:
    - JWT access token
    - Refresh token con renovación automática
    - Validación de permisos
    """
    credentials_exception = WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION,
        reason="Could not validate credentials"
    )
    
    try:
        # Validar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        
        if usuario_id is None:
            raise credentials_exception
        
        # Verificar que no esté en blacklist (Redis)
        if await redis_client.sismember("token:blacklist", token):
            raise credentials_exception
        
        # Obtener usuario
        usuario = crud_usuario.get(db, id=usuario_id)
        if usuario is None or not usuario.is_active:
            raise credentials_exception
        
        # Renovar token si está próximo a expirar
        exp = datetime.fromtimestamp(payload.get("exp"))
        if exp - datetime.now() < timedelta(minutes=5):
            new_token = create_access_token(data={"sub": usuario_id})
            # Notificar al cliente del nuevo token
            await send_token_refresh(usuario_id, new_token)
        
        return usuario
        
    except jwt.JWTError:
        raise credentials_exception
```

##### 1.5 Configuración de Redis para Producción ⏱️ 0.5 días
```python
# src/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Redis para WebSocket
    REDIS_WS_HOST: str = "localhost"
    REDIS_WS_PORT: int = 6379
    REDIS_WS_DB: int = 1  # DB separada para WebSocket
    REDIS_WS_PASSWORD: Optional[str] = None
    
    # Configuración de conexiones
    REDIS_WS_MAX_CONNECTIONS: int = 100
    REDIS_WS_SOCKET_KEEPALIVE: bool = True
    REDIS_WS_SOCKET_KEEPALIVE_OPTIONS: dict = {
        "socket.TCP_KEEPIDLE": 1,
        "socket.TCP_KEEPINTVL": 3,
        "socket.TCP_KEEPCNT": 5
    }
    
    # Pub/Sub channels
    REDIS_CHANNEL_MESSAGES: str = "acadify:messages"
    REDIS_CHANNEL_PRESENCE: str = "acadify:presence"
    REDIS_CHANNEL_TYPING: str = "acadify:typing"

# src/services/redis_ws_manager.py

class RedisWebSocketManager:
    """Manager de WebSocket respaldado por Redis"""
    
    def __init__(self):
        self.redis_client = None
        self.pubsub = None
        self.local_connections: Dict[str, WebSocket] = {}
    
    async def connect(self):
        """Conectar a Redis"""
        self.redis_client = await aioredis.create_redis_pool(
            f"redis://{settings.REDIS_WS_HOST}:{settings.REDIS_WS_PORT}",
            db=settings.REDIS_WS_DB,
            password=settings.REDIS_WS_PASSWORD,
            maxsize=settings.REDIS_WS_MAX_CONNECTIONS
        )
        
        # Iniciar listener de pub/sub
        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe(settings.REDIS_CHANNEL_MESSAGES)
        asyncio.create_task(self._listen_pubsub())
    
    async def register_connection(
        self, 
        usuario_id: str, 
        connection_id: str,
        websocket: WebSocket
    ):
        """Registrar conexión en Redis"""
        # Guardar localmente
        self.local_connections[connection_id] = websocket
        
        # Registrar en Redis
        await self.redis_client.hset(
            f"ws:connections:{usuario_id}",
            connection_id,
            time.time()
        )
        
        # Actualizar presencia
        await self.redis_client.setex(
            f"presence:{usuario_id}",
            30,  # TTL 30 segundos
            "online"
        )
    
    async def broadcast_to_room(
        self,
        sala_id: str,
        message: dict,
        exclude_user: str = None
    ):
        """Broadcast mensaje a todos en una sala (multi-instancia)"""
        # Publicar en Redis para que todas las instancias lo reciban
        await self.redis_client.publish(
            settings.REDIS_CHANNEL_MESSAGES,
            json.dumps({
                "type": "room_broadcast",
                "sala_id": sala_id,
                "message": message,
                "exclude_user": exclude_user
            })
        )
    
    async def _listen_pubsub(self):
        """Escuchar mensajes de pub/sub"""
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                await self._handle_pubsub_message(
                    json.loads(message['data'])
                )
    
    async def _handle_pubsub_message(self, data: dict):
        """Manejar mensaje de pub/sub"""
        if data['type'] == 'room_broadcast':
            # Obtener participantes de la sala
            participants = await self.redis_client.smembers(
                f"room:{data['sala_id']}:participants"
            )
            
            # Enviar a conexiones locales
            for usuario_id in participants:
                if usuario_id == data.get('exclude_user'):
                    continue
                
                # Obtener conexiones del usuario
                connections = await self.redis_client.hgetall(
                    f"ws:connections:{usuario_id}"
                )
                
                # Enviar a conexiones locales
                for conn_id in connections.keys():
                    if conn_id in self.local_connections:
                        websocket = self.local_connections[conn_id]
                        try:
                            await websocket.send_json(data['message'])
                        except:
                            await self.unregister_connection(usuario_id, conn_id)

# Instancia global
redis_ws_manager = RedisWebSocketManager()
```

---

### FASE 2: CHAT BÁSICO MEJORADO (Semana 2)

#### 🎯 Objetivos
- Mejorar experiencia de chat en tiempo real
- Implementar features críticas de mensajería
- Optimizar performance

#### Tareas Detalladas

##### 2.1 Chats Privados 1-a-1 ⏱️ 2 días
```python
# src/models/communication/chat.py

class SalaChat(Base):
    # ... campos existentes ...
    
    # Para chats privados
    es_privada = Column(Boolean, default=False)
    participante_1_id = Column(UUID(as_uuid=True))
    participante_2_id = Column(UUID(as_uuid=True))
    
    # Constraint único para evitar duplicados
    __table_args__ = (
        UniqueConstraint(
            'participante_1_id', 
            'participante_2_id',
            name='uq_chat_privado'
        ),
    )

# src/api/routes/communication/chat_privado.py

@router.post("/chats/privados/iniciar", response_model=SalaChatResponse)
async def iniciar_chat_privado(
    destinatario_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Iniciar chat privado con otro usuario
    
    - Verifica si ya existe una sala entre ambos usuarios
    - Si no existe, la crea automáticamente
    - Agrega ambos participantes
    - Retorna la sala
    """
    # Ordenar IDs para búsqueda consistente
    user1_id = min(current_user.id, destinatario_id)
    user2_id = max(current_user.id, destinatario_id)
    
    # Buscar sala existente
    sala = (
        db.query(SalaChat)
        .filter(
            SalaChat.es_privada == True,
            SalaChat.participante_1_id == user1_id,
            SalaChat.participante_2_id == user2_id
        )
        .first()
    )
    
    if sala:
        return SalaChatResponse.from_orm(sala)
    
    # Crear nueva sala
    destinatario = crud_usuario.get(db, id=destinatario_id)
    if not destinatario:
        raise HTTPException(404, "Usuario no encontrado")
    
    sala = SalaChat(
        nombre=f"Chat: {current_user.nombre} & {destinatario.nombre}",
        tipo_sala=TipoSala.PRIVADO,
        es_privada=True,
        es_publica=False,
        participante_1_id=user1_id,
        participante_2_id=user2_id,
        creador_id=current_user.id,
        permite_archivos=True,
        max_participantes=2
    )
    
    db.add(sala)
    db.flush()
    
    # Agregar participantes
    for user_id in [current_user.id, destinatario_id]:
        participante = ParticipanteSala(
            sala_id=sala.id,
            usuario_id=user_id,
            puede_escribir=True,
            es_admin=False
        )
        db.add(participante)
    
    db.commit()
    db.refresh(sala)
    
    # Notificar al destinatario via WebSocket
    await redis_ws_manager.send_to_user(
        str(destinatario_id),
        {
            "type": "new_chat",
            "sala": SalaChatResponse.from_orm(sala).dict()
        }
    )
    
    return SalaChatResponse.from_orm(sala)


@router.get("/chats/privados", response_model=List[SalaChatResponse])
async def listar_chats_privados(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    buscar: Optional[str] = None,
    solo_activos: bool = True,
    limite: int = 50,
    offset: int = 0
):
    """Listar todos los chats privados del usuario"""
    query = (
        db.query(SalaChat)
        .join(ParticipanteSala)
        .filter(
            SalaChat.es_privada == True,
            ParticipanteSala.usuario_id == current_user.id,
            ParticipanteSala.esta_activo == True
        )
    )
    
    if solo_activos:
        query = query.filter(SalaChat.esta_activa == True)
    
    if buscar:
        # Buscar en nombre de la sala o del otro participante
        busqueda = f"%{buscar}%"
        query = query.filter(
            or_(
                SalaChat.nombre.ilike(busqueda),
                # JOIN con Usuario para buscar por nombre
            )
        )
    
    # Ordenar por último mensaje
    query = query.order_by(
        desc(SalaChat.fecha_ultima_actividad)
    )
    
    salas = query.offset(offset).limit(limite).all()
    
    return [SalaChatResponse.from_orm(sala) for sala in salas]
```

##### 2.2 Indicadores de Escritura ⏱️ 1 día
```python
# src/services/websocket_manager.py

class TypingManager:
    """Manager para indicadores de escritura"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.typing_timeouts: Dict[str, asyncio.Task] = {}
    
    async def user_typing(
        self,
        sala_id: str,
        usuario_id: str,
        is_typing: bool
    ):
        """Registrar que usuario está escribiendo"""
        key = f"typing:{sala_id}:{usuario_id}"
        
        if is_typing:
            # Guardar en Redis con TTL de 3 segundos
            await self.redis.setex(key, 3, "1")
            
            # Broadcast a la sala
            await redis_ws_manager.broadcast_to_room(
                sala_id,
                {
                    "type": "user_typing",
                    "usuario_id": usuario_id,
                    "is_typing": True
                },
                exclude_user=usuario_id
            )
            
            # Programar auto-cancelación
            if key in self.typing_timeouts:
                self.typing_timeouts[key].cancel()
            
            self.typing_timeouts[key] = asyncio.create_task(
                self._auto_cancel_typing(sala_id, usuario_id, key)
            )
        else:
            # Cancelar inmediatamente
            await self.redis.delete(key)
            
            await redis_ws_manager.broadcast_to_room(
                sala_id,
                {
                    "type": "user_typing",
                    "usuario_id": usuario_id,
                    "is_typing": False
                },
                exclude_user=usuario_id
            )
    
    async def _auto_cancel_typing(
        self,
        sala_id: str,
        usuario_id: str,
        key: str
    ):
        """Auto-cancelar typing después de 3 segundos"""
        await asyncio.sleep(3)
        await self.redis.delete(key)
        
        await redis_ws_manager.broadcast_to_room(
            sala_id,
            {
                "type": "user_typing",
                "usuario_id": usuario_id,
                "is_typing": False
            },
            exclude_user=usuario_id
        )
        
        del self.typing_timeouts[key]
    
    async def get_typing_users(self, sala_id: str) -> List[str]:
        """Obtener usuarios escribiendo en una sala"""
        pattern = f"typing:{sala_id}:*"
        keys = await self.redis.keys(pattern)
        
        return [key.split(":")[-1] for key in keys]

# Integrar en WebSocket handler
class WebSocketHandler:
    # ... existing code ...
    
    async def _handle_typing(self, data: Dict[str, Any]):
        """Manejar indicador de escritura con optimización"""
        sala_id = data["sala_id"]
        is_typing = data.get("is_typing", False)
        
        # Rate limiting: máximo 1 evento cada 500ms
        cache_key = f"typing_ratelimit:{self.usuario.id}:{sala_id}"
        if await redis_client.exists(cache_key):
            return  # Ignorar evento duplicado
        
        await redis_client.setex(cache_key, 1, "1")  # TTL 1 segundo
        
        await typing_manager.user_typing(
            sala_id=sala_id,
            usuario_id=str(self.usuario.id),
            is_typing=is_typing
        )
```

##### 2.3 Estados de Mensajes (Doble Check) ⏱️ 1.5 días
```python
# src/models/communication/chat.py

class EstadoMensaje(str, enum.Enum):
    ENVIANDO = "enviando"      # Cliente enviando
    ENVIADO = "enviado"        # Servidor recibió
    ENTREGADO = "entregado"    # Entregado a destinatario(s)
    LEIDO = "leido"            # Usuario(s) leyeron
    ERROR = "error"            # Error al enviar

class MensajeChat(Base):
    # ... campos existentes ...
    
    estado = Column(Enum(EstadoMensaje), default=EstadoMensaje.ENVIADO)
    fecha_entrega = Column(DateTime)
    fecha_lectura = Column(DateTime)
    
    # Tracking de entrega/lectura por usuario
    entregas = Column(JSON, default=dict)  # {usuario_id: timestamp}
    lecturas = Column(JSON, default=dict)  # {usuario_id: timestamp}

# src/crud/communication/chat.py

class CRUDMensaje(CRUDBase[Mensaje, MensajeCreate, MensajeUpdate]):
    
    async def marcar_entregado(
        self,
        db: Session,
        mensaje_id: str,
        usuario_id: str
    ):
        """Marcar mensaje como entregado a usuario"""
        mensaje = await self.get(db, id=mensaje_id)
        if not mensaje:
            return False
        
        entregas = mensaje.entregas or {}
        if usuario_id not in entregas:
            entregas[usuario_id] = datetime.now().isoformat()
            mensaje.entregas = entregas
            
            # Actualizar estado general si todos lo recibieron
            participantes = await crud_participante_sala.get_participantes_sala(
                db, sala_id=str(mensaje.sala_id)
            )
            
            if len(entregas) >= len(participantes) - 1:  # -1 por el remitente
                mensaje.estado = EstadoMensaje.ENTREGADO
                mensaje.fecha_entrega = datetime.now()
            
            db.commit()
            
            # Notificar cambio de estado al remitente
            await redis_ws_manager.send_to_user(
                str(mensaje.usuario_id),
                {
                    "type": "message_delivered",
                    "mensaje_id": mensaje_id,
                    "usuario_id": usuario_id,
                    "timestamp": entregas[usuario_id]
                }
            )
        
        return True
    
    async def marcar_leido(
        self,
        db: Session,
        mensaje_id: str,
        usuario_id: str
    ):
        """Marcar mensaje como leído por usuario"""
        mensaje = await self.get(db, id=mensaje_id)
        if not mensaje:
            return False
        
        lecturas = mensaje.lecturas or {}
        if usuario_id not in lecturas:
            lecturas[usuario_id] = datetime.now().isoformat()
            mensaje.lecturas = lecturas
            
            # Actualizar estado general
            participantes = await crud_participante_sala.get_participantes_sala(
                db, sala_id=str(mensaje.sala_id)
            )
            
            if len(lecturas) >= len(participantes) - 1:
                mensaje.estado = EstadoMensaje.LEIDO
                mensaje.fecha_lectura = datetime.now()
            
            db.commit()
            
            # Notificar cambio de estado al remitente
            await redis_ws_manager.send_to_user(
                str(mensaje.usuario_id),
                {
                    "type": "message_read",
                    "mensaje_id": mensaje_id,
                    "usuario_id": usuario_id,
                    "timestamp": lecturas[usuario_id]
                }
            )
        
        return True

# WebSocket handler
async def _handle_message_delivered(self, data: Dict[str, Any]):
    """Cliente confirma que recibió mensaje"""
    mensaje_id = data["mensaje_id"]
    
    await crud_mensaje.marcar_entregado(
        self.db,
        mensaje_id=mensaje_id,
        usuario_id=str(self.usuario.id)
    )

async def _handle_message_read(self, data: Dict[str, Any]):
    """Cliente confirma que leyó mensaje(s)"""
    mensajes_ids = data.get("mensajes_ids", [])
    
    for mensaje_id in mensajes_ids:
        await crud_mensaje.marcar_leido(
            self.db,
            mensaje_id=mensaje_id,
            usuario_id=str(self.usuario.id)
        )
```

##### 2.4 Sistema de Reacciones Mejorado ⏱️ 1 día
```python
# src/models/communication/chat.py

class ReaccionMensaje(Base):
    """Tabla dedicada para reacciones (mejor que JSON)"""
    __tablename__ = "reacciones_mensajes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mensaje_id = Column(UUID(as_uuid=True), ForeignKey("mensajes.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False)
    emoji = Column(String(10), nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now())
    
    # Constraint único: un usuario solo puede reaccionar una vez con el mismo emoji
    __table_args__ = (
        UniqueConstraint('mensaje_id', 'usuario_id', name='uq_reaccion_usuario'),
    )
    
    # Relaciones
    mensaje = relationship("MensajeChat", back_populates="reacciones_rel")
    usuario = relationship("Usuario")

class MensajeChat(Base):
    # ... campos existentes ...
    
    # Relación con reacciones
    reacciones_rel = relationship(
        "ReaccionMensaje",
        back_populates="mensaje",
        cascade="all, delete-orphan"
    )

# src/crud/communication/reacciones.py

class CRUDReaccion(CRUDBase[ReaccionMensaje, None, None]):
    
    async def toggle_reaccion(
        self,
        db: Session,
        mensaje_id: str,
        usuario_id: str,
        emoji: str
    ) -> Tuple[bool, int]:
        """
        Toggle reacción (agregar o quitar)
        
        Returns:
            Tuple[agregado: bool, total_reacciones: int]
        """
        # Buscar reacción existente
        reaccion = (
            db.query(ReaccionMensaje)
            .filter(
                ReaccionMensaje.mensaje_id == mensaje_id,
                ReaccionMensaje.usuario_id == usuario_id,
                ReaccionMensaje.emoji == emoji
            )
            .first()
        )
        
        if reaccion:
            # Quitar reacción
            db.delete(reaccion)
            agregado = False
        else:
            # Agregar reacción
            reaccion = ReaccionMensaje(
                mensaje_id=mensaje_id,
                usuario_id=usuario_id,
                emoji=emoji
            )
            db.add(reaccion)
            agregado = True
        
        db.commit()
        
        # Contar total de reacciones
        total = (
            db.query(func.count(ReaccionMensaje.id))
            .filter(ReaccionMensaje.mensaje_id == mensaje_id)
            .scalar()
        )
        
        return agregado, total
    
    def get_reacciones_agrupadas(
        self,
        db: Session,
        mensaje_id: str
    ) -> Dict[str, List[str]]:
        """
        Obtener reacciones agrupadas por emoji
        
        Returns:
            {emoji: [usuario_id, ...]}
        """
        reacciones = (
            db.query(ReaccionMensaje)
            .filter(ReaccionMensaje.mensaje_id == mensaje_id)
            .all()
        )
        
        agrupadas = {}
        for reaccion in reacciones:
            if reaccion.emoji not in agrupadas:
                agrupadas[reaccion.emoji] = []
            agrupadas[reaccion.emoji].append(str(reaccion.usuario_id))
        
        return agrupadas

crud_reaccion = CRUDReaccion(ReaccionMensaje)

# API endpoint
@router.post("/mensajes/{mensaje_id}/reaccion")
async def toggle_reaccion_mensaje(
    mensaje_id: UUID,
    emoji: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Toggle reacción en mensaje"""
    agregado, total = await crud_reaccion.toggle_reaccion(
        db,
        mensaje_id=str(mensaje_id),
        usuario_id=str(current_user.id),
        emoji=emoji
    )
    
    # Obtener reacciones actualizadas
    reacciones = crud_reaccion.get_reacciones_agrupadas(
        db, mensaje_id=str(mensaje_id)
    )
    
    # Broadcast actualización
    mensaje = crud_mensaje.get(db, id=str(mensaje_id))
    await redis_ws_manager.broadcast_to_room(
        str(mensaje.sala_id),
        {
            "type": "message_reaction_update",
            "mensaje_id": str(mensaje_id),
            "reacciones": reacciones,
            "usuario_id": str(current_user.id),
            "emoji": emoji,
            "action": "added" if agregado else "removed"
        }
    )
    
    return {
        "action": "added" if agregado else "removed",
        "total_reacciones": total,
        "reacciones": reacciones
    }


@router.get("/mensajes/{mensaje_id}/reacciones")
async def obtener_reacciones_mensaje(
    mensaje_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener todas las reacciones de un mensaje"""
    reacciones = crud_reaccion.get_reacciones_agrupadas(
        db, mensaje_id=str(mensaje_id)
    )
    
    return {
        "mensaje_id": str(mensaje_id),
        "reacciones": reacciones
    }
```

##### 2.5 Hilos de Conversación (Threads) ⏱️ 1.5 días
```python
# Modelo ya existe en chat.py, mejorar funcionalidad

# src/crud/communication/chat.py

class CRUDMensaje(CRUDBase[Mensaje, MensajeCreate, MensajeUpdate]):
    # ... existing methods ...
    
    async def get_hilo_completo(
        self,
        db: Session,
        mensaje_padre_id: str,
        usuario_id: str,
        limite: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Obtener hilo completo de conversación
        
        Returns:
            {
                "mensaje_padre": {...},
                "respuestas": [...],
                "total_respuestas": int,
                "participantes": [...]
            }
        """
        # Verificar acceso
        mensaje_padre = self.get(db, id=mensaje_padre_id)
        if not mensaje_padre:
            return None
        
        participante = crud_participante_sala.get_participante(
            db,
            sala_id=str(mensaje_padre.sala_id),
            usuario_id=usuario_id
        )
        if not participante:
            return None
        
        # Obtener respuestas
        respuestas = (
            db.query(self.model)
            .filter(self.model.mensaje_padre_id == mensaje_padre_id)
            .order_by(asc(self.model.fecha_creacion))
            .offset(offset)
            .limit(limite)
            .all()
        )
        
        # Contar total
        total = (
            db.query(func.count(self.model.id))
            .filter(self.model.mensaje_padre_id == mensaje_padre_id)
            .scalar()
        )
        
        # Obtener participantes únicos del hilo
        participantes_ids = {str(mensaje_padre.usuario_id)}
        for respuesta in respuestas:
            participantes_ids.add(str(respuesta.usuario_id))
        
        participantes = (
            db.query(Usuario)
            .filter(Usuario.usuario_id.in_(participantes_ids))
            .all()
        )
        
        return {
            "mensaje_padre": mensaje_padre,
            "respuestas": respuestas,
            "total_respuestas": total,
            "participantes": participantes
        }
    
    async def crear_respuesta(
        self,
        db: Session,
        mensaje_padre_id: str,
        obj_in: MensajeCreate,
        usuario_id: str
    ) -> Mensaje:
        """Crear respuesta en hilo"""
        # Validar que mensaje padre existe
        mensaje_padre = self.get(db, id=mensaje_padre_id)
        if not mensaje_padre:
            raise HTTPException(404, "Mensaje padre no encontrado")
        
        # Heredar sala del mensaje padre
        obj_in.sala_id = mensaje_padre.sala_id
        obj_in.mensaje_padre_id = mensaje_padre_id
        
        # Crear respuesta
        respuesta = await self.create_mensaje(db, obj_in=obj_in, usuario_id=usuario_id)
        
        # Actualizar contador del padre
        mensaje_padre.total_respuestas = (mensaje_padre.total_respuestas or 0) + 1
        mensaje_padre.fecha_ultima_respuesta = datetime.now()
        db.commit()
        
        # Notificar a participantes del hilo
        await self._notificar_nueva_respuesta(db, mensaje_padre, respuesta)
        
        return respuesta
    
    async def _notificar_nueva_respuesta(
        self,
        db: Session,
        mensaje_padre: Mensaje,
        respuesta: Mensaje
    ):
        """Notificar nueva respuesta en hilo"""
        # Obtener usuarios que participaron en el hilo
        participantes_ids = set()
        participantes_ids.add(str(mensaje_padre.usuario_id))
        
        respuestas_previas = (
            db.query(self.model.usuario_id)
            .filter(self.model.mensaje_padre_id == mensaje_padre.id)
            .distinct()
            .all()
        )
        
        for (uid,) in respuestas_previas:
            participantes_ids.add(str(uid))
        
        # Notificar a cada participante (excepto el autor de la respuesta)
        for usuario_id in participantes_ids:
            if usuario_id == str(respuesta.usuario_id):
                continue
            
            # Notificación
            notificacion = NotificacionCreate(
                usuario_id=usuario_id,
                titulo="Nueva respuesta en hilo",
                mensaje=f"{respuesta.usuario.nombre} respondió en un hilo donde participaste",
                tipo_notificacion="hilo_respuesta",
                sala_id=respuesta.sala_id,
                mensaje_id=respuesta.id,
                url_accion=f"/salas/{respuesta.sala_id}/hilo/{mensaje_padre.id}"
            )
            
            await crud_notificacion.create(db, obj_in=notificacion)
            
            # Push notification via WebSocket
            await redis_ws_manager.send_to_user(
                usuario_id,
                {
                    "type": "thread_reply",
                    "hilo_id": str(mensaje_padre.id),
                    "respuesta": MensajeResponse.from_orm(respuesta).dict()
                }
            )

# API endpoints
@router.get("/mensajes/{mensaje_id}/hilo")
async def obtener_hilo(
    mensaje_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    limite: int = 50,
    offset: int = 0
):
    """Obtener hilo completo de conversación"""
    hilo = await crud_mensaje.get_hilo_completo(
        db,
        mensaje_padre_id=str(mensaje_id),
        usuario_id=str(current_user.id),
        limite=limite,
        offset=offset
    )
    
    if not hilo:
        raise HTTPException(404, "Hilo no encontrado o sin acceso")
    
    return {
        "mensaje_padre": MensajeDetallado.from_orm(hilo["mensaje_padre"]),
        "respuestas": [MensajeResponse.from_orm(r) for r in hilo["respuestas"]],
        "total_respuestas": hilo["total_respuestas"],
        "participantes": [UsuarioBasico.from_orm(u) for u in hilo["participantes"]]
    }


@router.post("/mensajes/{mensaje_id}/responder", response_model=MensajeResponse)
async def responder_mensaje(
    mensaje_id: UUID,
    respuesta: MensajeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crear respuesta en hilo"""
    mensaje = await crud_mensaje.crear_respuesta(
        db,
        mensaje_padre_id=str(mensaje_id),
        obj_in=respuesta,
        usuario_id=str(current_user.id)
    )
    
    return MensajeResponse.from_orm(mensaje)
```

*(Continuará en el siguiente mensaje debido a límites de longitud...)*

---

### NOTA IMPORTANTE

Este plan tiene **50 tareas específicas** organizadas en **5 fases** principales:

1. **FASE 1**: Fundamentos y Refactoring (Semana 1)
2. **FASE 2**: Chat Básico Mejorado (Semana 2)
3. **FASE 3**: Multimedia y Archivos (Semana 3)
4. **FASE 4**: Videollamadas y Audio (Semana 4)
5. **FASE 5**: Testing, Optimización y Deploy (Semanas 5-6)

Cada tarea incluye:
- ⏱️ Estimación de tiempo
- 📝 Código de implementación completo
- ✅ Criterios de aceptación
- 🧪 Tests sugeridos

**¿Quieres que continúe con las fases restantes (3, 4 y 5)?** Incluyen:
- Sistema de archivos adjuntos
- Mensajes de voz
- Integración de videollamadas con Jitsi/LiveKit
- Testing completo
- Performance optimizations
- Deploy y escalabilidad

