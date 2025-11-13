# 📹 ANÁLISIS FASE 2 - Sistema de Videollamadas
## WebRTC + Real-Time Communication

**Fecha**: 9 de noviembre de 2025  
**Estado**: 🚧 EN PLANIFICACIÓN  
**Prioridad**: ALTA

---

## 🎯 Objetivos de la Fase 2

### Objetivo Principal
Implementar un sistema completo de videollamadas peer-to-peer usando **WebRTC**, integrado con el sistema de chat existente.

### Objetivos Específicos
1. ✅ Videollamadas 1 a 1 (peer-to-peer)
2. ✅ Videollamadas grupales (hasta 8 participantes)
3. ✅ Screen sharing (compartir pantalla)
4. ✅ Grabación de llamadas
5. ✅ Chat durante la llamada (integrado con Fase 1)
6. ✅ Controles de audio/video (mute, camera on/off)
7. ✅ Estadísticas de calidad (latencia, bitrate, packet loss)

---

## 🏗️ Arquitectura Propuesta

### Stack Tecnológico

#### Backend
- **WebRTC Signaling Server**: WebSocket (ya implementado)
- **STUN/TURN Server**: Coturn (para NAT traversal)
- **Media Server** (opcional): Mediasoup o Janus (para optimización grupal)
- **Storage**: PostgreSQL (metadata), S3/MinIO (grabaciones)

#### Frontend
- **WebRTC API**: Native browser API
- **Peer Connection**: RTCPeerConnection
- **Media Streams**: getUserMedia, getDisplayMedia
- **UI**: React + Tailwind + Framer Motion

### Opciones de Arquitectura

#### Opción A: Peer-to-Peer Puro (Recomendado para MVP)
```
Usuario A <--WebRTC--> Usuario B
     ^                      ^
     |                      |
     +--WebSocket Signaling-+
              |
         Backend Server
```

**Ventajas**:
- ✅ Menor latencia
- ✅ Menor carga en servidor
- ✅ Implementación más simple
- ✅ No requiere media server

**Desventajas**:
- ❌ Escala mal (>4 usuarios)
- ❌ Problemas con NATs estrictos
- ❌ No permite grabación centralizada

**Casos de Uso**:
- Videollamadas 1 a 1
- Grupos pequeños (2-4 personas)
- Clases particulares

#### Opción B: SFU (Selective Forwarding Unit)
```
Usuario A ----\
              |
Usuario B ----+--- Media Server (SFU) --- Recording
              |
Usuario C ----/
              ^
              |
         WebSocket
```

**Ventajas**:
- ✅ Escala bien (10+ usuarios)
- ✅ Menor uso de bandwidth del cliente
- ✅ Grabación centralizada fácil
- ✅ Mejor control de calidad

**Desventajas**:
- ❌ Mayor latencia
- ❌ Requiere infraestructura adicional
- ❌ Más complejo de implementar
- ❌ Costo de servidor media

**Casos de Uso**:
- Clases grupales (5-20 estudiantes)
- Webinars
- Conferencias

#### Opción C: MCU (Multipoint Control Unit)
```
Usuarios --> MCU (mezcla audio/video) --> Usuarios
```

**Ventajas**:
- ✅ Un solo stream por cliente
- ✅ Menor uso de bandwidth

**Desventajas**:
- ❌ Mayor latencia
- ❌ Alta carga en servidor
- ❌ Pérdida de calidad (encoding/decoding)
- ❌ Muy complejo

**No recomendado para este proyecto**

---

## 📋 Plan de Implementación

### FASE 2.1: Base WebRTC (P2P) - 1-2 días
**Prioridad**: CRÍTICA

#### Backend
1. **Signaling Server** (WebSocket)
   ```
   Eventos:
   - call.offer → Iniciar llamada
   - call.answer → Aceptar llamada
   - call.ice-candidate → Intercambio ICE
   - call.end → Terminar llamada
   ```

2. **CRUD de Videollamadas**
   ```python
   Modelo: Videollamada
   - id, sala_id, iniciador_id
   - participantes[]
   - estado (pendiente, activa, finalizada)
   - fecha_inicio, fecha_fin, duracion
   - url_grabacion (opcional)
   ```

3. **STUN Server Configuration**
   ```
   - Google STUN: stun:stun.l.google.com:19302
   - Propio TURN (Coturn): turn:acadify.com:3478
   ```

#### Frontend
1. **WebRTC Service** (`webrtcService.ts`)
   ```typescript
   - createPeerConnection()
   - handleOffer()
   - handleAnswer()
   - addIceCandidate()
   - getLocalStream()
   - close()
   ```

2. **Video Call Hook** (`useVideoCall.ts`)
   ```typescript
   - startCall(salaId, usuarioId)
   - answerCall()
   - endCall()
   - toggleMic()
   - toggleCamera()
   - shareScreen()
   ```

3. **UI Components**
   ```
   - VideoCallWindow.tsx
   - LocalVideoPreview.tsx
   - RemoteVideoGrid.tsx
   - CallControls.tsx
   - CallStats.tsx
   ```

### FASE 2.2: Videollamadas Grupales - 1 día
**Prioridad**: ALTA

#### Implementación Mesh (Primer enfoque)
```typescript
// Cada peer conecta con todos los demás
Peer A <-> Peer B
Peer A <-> Peer C
Peer B <-> Peer C
```

**Limitación**: Máximo 4 usuarios

#### Migración a SFU (Si se requiere)
- Implementar Mediasoup server
- Configurar producción/consumo de streams
- Actualizar frontend para usar SFU

### FASE 2.3: Screen Sharing - 0.5 días
**Prioridad**: MEDIA

```typescript
// API simple
const displayStream = await navigator.mediaDevices.getDisplayMedia({
    video: { cursor: 'always' },
    audio: true
});
```

### FASE 2.4: Grabación - 1 día
**Prioridad**: MEDIA

#### Opción A: Grabación del Cliente
```typescript
const mediaRecorder = new MediaRecorder(stream);
// Enviar chunks al servidor
```

**Ventajas**: Simple, no requiere media server  
**Desventajas**: Solo graba el stream local

#### Opción B: Grabación del Servidor (Requiere SFU)
```python
# En el media server
ffmpeg -i rtmp://input -c copy output.mp4
```

**Ventajas**: Graba todos los participantes  
**Desventajas**: Requiere infraestructura adicional

### FASE 2.5: Estadísticas y Calidad - 0.5 días
**Prioridad**: BAJA

```typescript
const stats = await pc.getStats();
// Extraer métricas:
// - bitrate, latency, packet loss
// - resolution, framerate
// - jitter, network type
```

---

## 📊 Modelos de Base de Datos

### 1. Videollamada
```python
class Videollamada(Base):
    __tablename__ = 'videollamadas'
    
    id: UUID
    sala_id: UUID  # FK a SalaChat
    iniciador_id: UUID  # FK a Usuario
    
    # Estado
    estado: Enum('pendiente', 'activa', 'finalizada', 'cancelada')
    
    # Tiempos
    fecha_creacion: DateTime
    fecha_inicio: DateTime | None
    fecha_fin: DateTime | None
    duracion_segundos: Integer | None
    
    # Configuración
    tiene_video: Boolean = True
    tiene_audio: Boolean = True
    permite_compartir_pantalla: Boolean = True
    max_participantes: Integer = 8
    
    # Grabación
    se_graba: Boolean = False
    url_grabacion: String | None
    
    # Relaciones
    participantes: List[ParticipanteVideollamada]
    eventos: List[EventoVideollamada]
```

### 2. ParticipanteVideollamada
```python
class ParticipanteVideollamada(Base):
    __tablename__ = 'participantes_videollamada'
    
    id: UUID
    videollamada_id: UUID
    usuario_id: UUID
    
    # Estado
    estado: Enum('invitado', 'conectado', 'desconectado')
    
    # Tiempos
    fecha_ingreso: DateTime | None
    fecha_salida: DateTime | None
    tiempo_conectado_segundos: Integer
    
    # Configuración
    tiene_audio_activado: Boolean = True
    tiene_video_activado: Boolean = True
    esta_compartiendo_pantalla: Boolean = False
    
    # Estadísticas
    calidad_promedio: Float  # 0-100
    packet_loss_promedio: Float
```

### 3. EventoVideollamada
```python
class EventoVideollamada(Base):
    __tablename__ = 'eventos_videollamada'
    
    id: UUID
    videollamada_id: UUID
    usuario_id: UUID | None
    
    # Evento
    tipo_evento: Enum(
        'inicio', 'fin', 'union', 'salida',
        'mute_audio', 'unmute_audio',
        'apagar_video', 'encender_video',
        'compartir_pantalla', 'dejar_compartir_pantalla',
        'error_conexion'
    )
    
    # Metadata
    fecha_evento: DateTime
    detalles: JSON
```

---

## 🔌 API Endpoints

### REST API

#### Gestión de Videollamadas
```
POST   /api/videollamadas                    # Crear videollamada
GET    /api/videollamadas/{id}               # Obtener info
PUT    /api/videollamadas/{id}               # Actualizar
DELETE /api/videollamadas/{id}               # Cancelar/eliminar

GET    /api/videollamadas/{id}/participantes # Listar participantes
POST   /api/videollamadas/{id}/participantes # Invitar participante
DELETE /api/videollamadas/{id}/participantes/{usuario_id} # Expulsar

POST   /api/videollamadas/{id}/iniciar       # Iniciar llamada
POST   /api/videollamadas/{id}/finalizar     # Finalizar llamada

GET    /api/videollamadas/{id}/grabacion     # Descargar grabación (si existe)
GET    /api/videollamadas/{id}/estadisticas  # Obtener estadísticas
```

### WebSocket Events

#### Signaling (Nuevo namespace)
```
Namespace: /ws/videollamada/{videollamada_id}

Cliente → Servidor:
- call.offer        → {offer: RTCSessionDescription}
- call.answer       → {answer: RTCSessionDescription}
- call.ice-candidate → {candidate: RTCIceCandidate, target: usuario_id}
- call.end          → {}

Servidor → Cliente:
- call.incoming     → {from: usuario_id, offer: RTCSessionDescription}
- call.answered     → {from: usuario_id, answer: RTCSessionDescription}
- call.ice-candidate → {from: usuario_id, candidate: RTCIceCandidate}
- call.participant-joined → {usuario: Usuario}
- call.participant-left → {usuario_id: string}
- call.ended        → {razon: string}
```

---

## 🎨 Interfaces de Usuario

### 1. Botón de Videollamada (en ChatWindow)
```tsx
<button onClick={startVideoCall}>
  <Video /> Iniciar Videollamada
</button>
```

### 2. Modal de Llamada Entrante
```
┌─────────────────────────────────┐
│  📹 Videollamada Entrante       │
│                                 │
│  Prof. García te está llamando │
│                                 │
│  [Rechazar]  [Aceptar 📹]      │
└─────────────────────────────────┘
```

### 3. Ventana de Videollamada
```
┌───────────────────────────────────────┐
│ 📹 Matemáticas 11A          [X]      │
├───────────────────────────────────────┤
│                                       │
│   ┌─────┐  ┌─────┐  ┌─────┐        │
│   │ A   │  │ B   │  │ C   │        │
│   └─────┘  └─────┘  └─────┘        │
│                                       │
│   ┌─────────────────────────┐       │
│   │    [Pantalla compartida]│       │
│   └─────────────────────────┘       │
│                                       │
├───────────────────────────────────────┤
│ [🎤] [📹] [🖥️] [💬] [📊] [❌]       │
│  Mic  Cam Share Chat Stats  End     │
└───────────────────────────────────────┘
```

### 4. Controles
- 🎤 Mute/Unmute
- 📹 Camera On/Off
- 🖥️ Share Screen
- 💬 Open Chat
- 📊 Show Stats
- ❌ End Call

---

## 🔒 Seguridad

### 1. Autenticación
- JWT token en WebSocket signaling
- Validar permisos de sala antes de permitir videollamada

### 2. Autorización
```python
# Solo pueden iniciar videollamadas:
- Profesores/Administradores (siempre)
- Estudiantes (si la sala lo permite)

# Solo pueden unirse:
- Participantes de la sala
- Invitados con link específico (feature futuro)
```

### 3. Encriptación
- WebRTC usa DTLS/SRTP por defecto (encriptado end-to-end)
- No necesita implementación adicional

### 4. Rate Limiting
```python
# Límites:
- Máx 10 videollamadas por usuario por día
- Máx 2 videollamadas simultáneas por usuario
- Duración máxima: 4 horas
```

---

## 📊 Métricas y Monitoreo

### KPIs Importantes
1. **Calidad de Conexión**
   - Latencia promedio (target: <150ms)
   - Packet loss (target: <2%)
   - Bitrate promedio (video: 500kbps-2Mbps)

2. **Uso**
   - Videollamadas activas simultáneas
   - Duración promedio de llamadas
   - Usuarios activos en llamadas

3. **Errores**
   - Tasa de fallo de conexión
   - Desconexiones inesperadas
   - Errores de signaling

---

## 🚀 Plan de Despliegue

### Desarrollo (Local)
```bash
# STUN Server
- Google STUN gratuito

# Signaling Server
- WebSocket existente (puerto 8000)

# Frontend
- localhost:5173
```

### Staging
```bash
# STUN/TURN Server
- Coturn en servidor dedicado
- turn.staging.acadify.com

# Backend
- staging-api.acadify.com

# Frontend
- staging.acadify.com
```

### Producción
```bash
# STUN/TURN Server
- Coturn cluster (alta disponibilidad)
- turn1.acadify.com, turn2.acadify.com

# Backend
- api.acadify.com (load balanced)

# Frontend
- acadify.com

# Monitoreo
- Grafana + Prometheus
- Alertas en Slack/Email
```

---

## 💰 Costos Estimados

### Infraestructura Adicional

#### TURN Server (Coturn)
- **Servidor**: $20-40/mes (2 CPU, 4GB RAM)
- **Bandwidth**: $0.08/GB (~$50-200/mes según uso)
- **Total**: ~$70-240/mes

#### Media Server (Si se usa SFU)
- **Servidor**: $80-150/mes (4-8 CPU, 8-16GB RAM)
- **Bandwidth**: $0.08/GB (~$200-500/mes)
- **Total**: ~$280-650/mes

#### Storage (Grabaciones)
- **S3/MinIO**: $0.023/GB almacenamiento + $0.09/GB transferencia
- **Estimado**: ~$50-200/mes (según uso)

### Total Estimado
- **MVP (P2P sin grabaciones)**: $70-240/mes
- **Producción (SFU + grabaciones)**: $400-1000/mes

---

## ⚠️ Riesgos y Mitigaciones

### Riesgo 1: NAT Traversal
**Problema**: Algunos usuarios detrás de NATs estrictos no pueden conectar  
**Mitigación**: TURN server obligatorio, no opcional  
**Probabilidad**: Media  
**Impacto**: Alto

### Riesgo 2: Escalabilidad
**Problema**: P2P no escala >4 usuarios  
**Mitigación**: Implementar SFU desde el inicio o tener plan de migración  
**Probabilidad**: Alta  
**Impacto**: Alto

### Riesgo 3: Calidad de Red
**Problema**: Usuarios con conexión pobre degradan la experiencia  
**Mitigación**: Adaptive bitrate, fallback a audio-only  
**Probabilidad**: Alta  
**Impacto**: Medio

### Riesgo 4: Compatibilidad de Navegadores
**Problema**: Navegadores antiguos no soportan WebRTC  
**Mitigación**: Detección y mensaje de navegador no soportado  
**Probabilidad**: Baja  
**Impacto**: Bajo

---

## 📅 Cronograma Detallado

### Semana 1: Base WebRTC
- **Día 1**: Backend signaling + CRUD videollamadas
- **Día 2**: Frontend webrtcService.ts + useVideoCall.ts
- **Día 3**: UI components (VideoCallWindow, controls)
- **Día 4**: Testing videollamadas 1 a 1
- **Día 5**: Bug fixes + polish

### Semana 2: Features Avanzados
- **Día 1**: Videollamadas grupales (mesh)
- **Día 2**: Screen sharing
- **Día 3**: Grabación de llamadas
- **Día 4**: Estadísticas y calidad
- **Día 5**: Testing integración completa

---

## ✅ Criterios de Aceptación

### Funcionales
- [ ] Usuario puede iniciar videollamada desde chat
- [ ] Usuario puede aceptar/rechazar llamada entrante
- [ ] Audio y video funcionan en ambas direcciones
- [ ] Controles de mute/camera on-off funcionan
- [ ] Screen sharing funciona
- [ ] Máximo 4 usuarios en llamada P2P
- [ ] Grabación de llamadas (opcional)
- [ ] Estadísticas de calidad visibles

### No Funcionales
- [ ] Latencia < 200ms (90 percentil)
- [ ] Packet loss < 3%
- [ ] Video 480p @ 30fps mínimo
- [ ] Audio 48kHz mínimo
- [ ] Funciona en Chrome, Firefox, Safari
- [ ] Responsive (desktop + tablet, NO mobile MVP)

---

## 🎯 Decisión: Arquitectura Inicial

**RECOMENDACIÓN**: Empezar con **P2P Mesh** + **Google STUN**

**Justificación**:
1. ✅ Implementación más rápida (3-5 días)
2. ✅ Sin costos de infraestructura inicial
3. ✅ Suficiente para MVP (1-4 usuarios)
4. ✅ Migración a SFU posible después

**Plan de Migración a SFU**:
- Cuando >30% de llamadas tengan >4 participantes
- Cuando calidad sea problema frecuente
- Implementar Mediasoup server
- Actualizar frontend gradualmente

---

## 📝 Próximos Pasos Inmediatos

1. ✅ **Aprobar este análisis**
2. 🔨 **Crear modelos de BD** (Videollamada, Participante, Evento)
3. 🔨 **Implementar signaling server** (WebSocket events)
4. 🔨 **Crear webrtcService.ts** (Frontend)
5. 🔨 **UI básica** (VideoCallWindow)
6. 🧪 **Test videollamada 1 a 1**

---

**¿Procedemos con la implementación?** 🚀
