# 📐 DIAGRAMAS Y ARQUITECTURA - SISTEMA DE VIDEOLLAMADAS

**Proyecto**: Acadify - Videollamadas con IA  
**Versión**: 1.0  
**Fecha**: 1 de Noviembre de 2025  

---

## 📋 TABLA DE CONTENIDOS

1. [Arquitectura General](#arquitectura-general)
2. [Flujos de Usuario](#flujos-de-usuario)
3. [Diagramas de Secuencia](#diagramas-de-secuencia)
4. [Modelo de Datos](#modelo-de-datos)
5. [Componentes Frontend](#componentes-frontend)
6. [Integraciones](#integraciones)

---

## 🏗️ ARQUITECTURA GENERAL

### **Vista de Alto Nivel**

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React)                           │
│                                                                       │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────┐ │
│  │   ChatView Page    │  │  JitsiMeetModal    │  │ Rutilio Widget │ │
│  │  - Botón Llamada   │  │  - Video/Audio     │  │ - Voice Input  │ │
│  │  - Participantes   │  │  - Compartir       │  │ - Respuestas   │ │
│  │  - Notificaciones  │  │  - Controls        │  │ - Context      │ │
│  └────────┬───────────┘  └────────┬───────────┘  └────────┬───────┘ │
│           │                       │                       │          │
│           └───────────────────────┴───────────────────────┘          │
│                                   │                                  │
│                         ┌─────────▼─────────┐                        │
│                         │  WebSocket Client │                        │
│                         │  + HTTP Client    │                        │
│                         └─────────┬─────────┘                        │
└───────────────────────────────────┼──────────────────────────────────┘
                                    │
                         WSS + HTTPS│
                                    │
┌───────────────────────────────────▼──────────────────────────────────┐
│                        BACKEND (FastAPI)                              │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                   API Gateway Layer                            │  │
│  │  /videollamadas/*   /grabaciones/*   /transcripciones/*        │  │
│  └────────────────────────┬───────────────────────────────────────┘  │
│                           │                                           │
│           ┌───────────────┼───────────────┐                          │
│           │               │               │                          │
│  ┌────────▼─────┐  ┌──────▼──────┐  ┌────▼──────────┐              │
│  │ Videollamada │  │  WebSocket  │  │      IA       │              │
│  │   Service    │  │   Manager   │  │   Services    │              │
│  │              │  │             │  │  - Whisper    │              │
│  │ - Iniciar    │  │ - Broadcast │  │  - GPT-4      │              │
│  │ - Unirse     │  │ - Presence  │  │  - TTS        │              │
│  │ - Finalizar  │  │ - Events    │  │  - Resumen    │              │
│  └────────┬─────┘  └──────┬──────┘  └────┬──────────┘              │
│           │               │               │                          │
│           └───────────────┼───────────────┘                          │
│                           │                                           │
│  ┌────────────────────────▼───────────────────────────────────────┐  │
│  │                    CRUD Layer (Repository)                     │  │
│  │  - VideollamadaCRUD  - GrabacionCRUD  - TranscripcionCRUD     │  │
│  └────────────────────────┬───────────────────────────────────────┘  │
│                           │                                           │
│  ┌────────────────────────▼───────────────────────────────────────┐  │
│  │                  ORM Layer (SQLAlchemy)                        │  │
│  │  Models: Videollamada, Grabacion, Transcripcion, Interaccion  │  │
│  └────────────────────────┬───────────────────────────────────────┘  │
└───────────────────────────┼───────────────────────────────────────────┘
                            │
                ┌───────────┴──────────┐
                │                      │
       ┌────────▼────────┐    ┌────────▼────────┐
       │   PostgreSQL    │    │     Redis       │
       │                 │    │                 │
       │ - videollamadas │    │ - WS Sessions   │
       │ - grabaciones   │    │ - Cache         │
       │ - transcripcion │    │ - Celery Queue  │
       └─────────────────┘    └─────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      SERVICIOS EXTERNOS                              │
│                                                                       │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│  │  Jitsi Meet    │  │   OpenAI API   │  │  Storage       │        │
│  │                │  │                │  │  (MinIO/S3)    │        │
│  │ - WebRTC       │  │ - Whisper      │  │                │        │
│  │ - Recording    │  │ - GPT-4 Turbo  │  │ - Videos       │        │
│  │ - Streaming    │  │ - TTS          │  │ - Audios       │        │
│  │ - Screen Share │  │                │  │ - Thumbnails   │        │
│  └────────────────┘  └────────────────┘  └────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 👤 FLUJOS DE USUARIO

### **Flujo 1: Iniciar Videollamada**

```
┌─────────┐
│ Usuario │
│   A     │
└────┬────┘
     │
     │ 1. Entra al chat de la sala
     ▼
┌─────────────────────────┐
│  Vista de Chat          │
│  ┌───────────────────┐  │
│  │ [📹 Videollamada]│  │← 2. Click en botón
│  └───────────────────┘  │
└────────┬────────────────┘
         │
         │ 3. Modal de confirmación
         ▼
┌─────────────────────────┐
│  Modal: Tipo de llamada │
│  ○ Videollamada 🎥      │← 4. Selecciona tipo
│  ○ Solo Voz 🎙️         │
│  ○ Compartir Pantalla 🖥️│
│  [Iniciar]              │
└────────┬────────────────┘
         │
         │ 5. POST /videollamadas/iniciar
         ▼
┌─────────────────────────┐
│  Backend procesa:       │
│  - Valida permisos      │
│  - Crea registro BD     │
│  - Genera JWT Jitsi     │
│  - Genera room_name     │
└────────┬────────────────┘
         │
         │ 6. Response con datos
         ▼
┌─────────────────────────┐
│  Frontend recibe:       │
│  {                      │
│    jwt_token: "...",    │
│    room_name: "...",    │
│    jitsi_url: "..."     │
│  }                      │
└────────┬────────────────┘
         │
         │ 7. WebSocket: broadcast a sala
         ▼
┌─────────────────────────┐
│  Otros usuarios ven:    │
│  ┌───────────────────┐  │
│  │ 🔴 Juan inició    │  │
│  │ una videollamada  │  │
│  │ [Unirse]          │  │
│  └───────────────────┘  │
└────────┬────────────────┘
         │
         │ 8. Abrir Jitsi Modal
         ▼
┌─────────────────────────┐
│  JitsiMeetModal         │
│  ┌───────────────────┐  │
│  │                   │  │
│  │   [Video Feed]    │  │
│  │                   │  │
│  │ 🎤 🎥 🖥️ 💬 ⚙️   │  │
│  └───────────────────┘  │
└─────────────────────────┘
```

### **Flujo 2: Interactuar con Rutilio en Llamada**

```
┌─────────┐
│ Usuario │
│   B     │
└────┬────┘
     │
     │ 1. Está en videollamada
     ▼
┌─────────────────────────┐
│  Jitsi Meet activa      │
│  [Usuario B - Video ON] │
└────────┬────────────────┘
         │
         │ 2. Usuario dice: "@Rutilio, ¿cuál es el tema de hoy?"
         ▼
┌─────────────────────────┐
│  Detección de mención   │
│  - Audio capturado      │
│  - "@Rutilio" detectado │
└────────┬────────────────┘
         │
         │ 3. Transcribir con Whisper
         ▼
┌─────────────────────────┐
│  Whisper API            │
│  Audio → Text           │
│  "cuál es el tema       │
│   de hoy"               │
└────────┬────────────────┘
         │
         │ 4. Enviar a GPT-4 con contexto
         ▼
┌─────────────────────────┐
│  GPT-4 Turbo            │
│  Context: Clase de      │
│           Matemáticas   │
│  Question: "¿cuál es    │
│            el tema...?" │
│                         │
│  Response: "Hoy veremos │
│  ecuaciones lineales"   │
└────────┬────────────────┘
         │
         │ 5. Convertir respuesta a audio
         ▼
┌─────────────────────────┐
│  TTS API                │
│  Text → Audio           │
│  🔊 "Hoy veremos..."    │
└────────┬────────────────┘
         │
         │ 6. Reproducir en Jitsi
         ▼
┌─────────────────────────┐
│  Rutilio "habla" en     │
│  la videollamada        │
│  🤖💬 "Hoy veremos     │
│        ecuaciones..."   │
└────────┬────────────────┘
         │
         │ 7. Guardar interacción en BD
         ▼
┌─────────────────────────┐
│  interacciones_ia_...   │
│  - timestamp: 05:23     │
│  - user: Usuario B      │
│  - question: "¿cuál..." │
│  - answer: "Hoy..."     │
│  - confidence: 0.95     │
└─────────────────────────┘
```

### **Flujo 3: Finalizar y Ver Resumen**

```
┌─────────┐
│ Usuario │
│   A     │
│(admin)  │
└────┬────┘
     │
     │ 1. Click "Finalizar Llamada"
     ▼
┌─────────────────────────┐
│  Modal confirmación     │
│  "¿Finalizar llamada    │
│   para todos?"          │
│  [Sí] [No]              │
└────────┬────────────────┘
         │
         │ 2. POST /videollamadas/{id}/finalizar
         ▼
┌─────────────────────────┐
│  Backend procesa:       │
│  - Marca como finalizada│
│  - Calcula duración     │
│  - Inicia procesamiento │
│    async                │
└────────┬────────────────┘
         │
         │ 3. Celery Task: Procesar grabación
         ▼
┌─────────────────────────┐
│  Task: procesar_video   │
│  - Extraer metadatos    │
│  - Generar thumbnail    │
│  - Comprimir si necesario│
│  - Upload a storage     │
└────────┬────────────────┘
         │
         │ 4. Celery Task: Transcribir completo
         ▼
┌─────────────────────────┐
│  Task: transcribir      │
│  - Whisper en todo audio│
│  - Segmentar por speaker│
│  - Añadir timestamps    │
│  - Generar VTT/SRT      │
└────────┬────────────────┘
         │
         │ 5. Celery Task: Generar resumen
         ▼
┌─────────────────────────┐
│  Task: generar_resumen  │
│  GPT-4 analiza:         │
│  - Temas principales    │
│  - Decisiones tomadas   │
│  - Action items         │
│  - Participación        │
└────────┬────────────────┘
         │
         │ 6. Notificar participantes
         ▼
┌─────────────────────────┐
│  Notificaciones:        │
│  📧 Email a todos       │
│  🔔 In-app notification │
│  "Tu resumen está listo"│
└────────┬────────────────┘
         │
         │ 7. Usuario abre resumen
         ▼
┌─────────────────────────────────────┐
│  Vista de Resumen                   │
│  ┌───────────────────────────────┐  │
│  │ 📊 Resumen de Videollamada    │  │
│  │                               │  │
│  │ ⏱️ Duración: 45 minutos       │  │
│  │ 👥 Participantes: 12          │  │
│  │                               │  │
│  │ 📝 Temas Principales:         │  │
│  │ • Ecuaciones lineales         │  │
│  │ • Sistemas 2x2                │  │
│  │ • Método de sustitución       │  │
│  │                               │  │
│  │ ✅ Decisiones:                │  │
│  │ • Tarea para el viernes       │  │
│  │ • Examen el próximo martes    │  │
│  │                               │  │
│  │ 📋 Action Items:              │  │
│  │ ☐ Revisar capítulo 5          │  │
│  │ ☐ Hacer ejercicios 1-10       │  │
│  │                               │  │
│  │ 🎤 Más Activos:               │  │
│  │ 1. Juan (23 intervenciones)   │  │
│  │ 2. María (18 intervenciones)  │  │
│  │                               │  │
│  │ [📥 Descargar PDF]            │  │
│  │ [🎥 Ver Grabación]            │  │
│  │ [📜 Ver Transcripción]        │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## 🔄 DIAGRAMAS DE SECUENCIA

### **Secuencia 1: Iniciar Videollamada Completa**

```
Usuario    Frontend    Backend    PostgreSQL    Jitsi    WebSocket    Otros
  │           │           │            │          │         │       Usuarios
  │           │           │            │          │         │          │
  ├─Click────>│           │            │          │         │          │
  │           │           │            │          │         │          │
  │           ├─POST /videollamadas/iniciar───────>         │          │
  │           │           │            │          │         │          │
  │           │           ├─validar_permisos()    │         │          │
  │           │           │<───────────┤          │         │          │
  │           │           │            │          │         │          │
  │           │           ├─INSERT videollamada───>         │          │
  │           │           │<──────────OK          │         │          │
  │           │           │            │          │         │          │
  │           │           ├─generar_jwt_token()   │         │          │
  │           │           │            │          │         │          │
  │           │           ├─generar_room_name()   │         │          │
  │           │           │            │          │         │          │
  │           │<─Response─{jwt, room}─┤          │         │          │
  │           │           │            │          │         │          │
  │           │           ├─broadcast("videollamada_iniciada")────────>│
  │           │           │            │          │         │          │
  │<─Response─┤           │            │          │         │          │
  │  {jwt,    │           │            │          │         │          │
  │   room}   │           │            │          │         │          │
  │           │           │            │          │         │          │
  │           ├─Init Jitsi External API─────────>│         │          │
  │           │           │            │          │         │          │
  │           │           │  join room with JWT──>│         │          │
  │           │           │            │         <┤         │          │
  │           │           │            │  connected│        │          │
  │           │           │            │          │         │          │
  │           │<─Jitsi Ready────────────────────<┤         │          │
  │           │           │            │          │         │          │
  │<─Modal───┤            │            │          │         │          │
  │  Abierto │            │            │          │         │          │
  │           │            │            │          │         │          │
  │           │            │            │          │         │  <─Notification─┤
  │           │            │            │          │         │   "Juan inició  │
  │           │            │            │          │         │    llamada"     │
```

### **Secuencia 2: Rutilio Responde en Videollamada**

```
Usuario  Jitsi   Backend   Whisper   GPT-4    TTS    Storage    DB
  │       │        │         │         │       │       │         │
  │──Habla────────>│         │         │       │       │         │
  │ "@Rutilio     │         │         │       │       │         │
  │  ayuda"       │         │         │       │       │         │
  │       │        │         │         │       │       │         │
  │       ├─Audio captured──>         │       │       │         │
  │       │        │         │         │       │       │         │
  │       │        ├─Detect @Rutilio  │       │       │         │
  │       │        │         │         │       │       │         │
  │       │        ├─POST /transcribe─>        │       │         │
  │       │        │         │         │       │       │         │
  │       │        │         ├─Whisper API     │       │         │
  │       │        │         │   (Speech2Text) │       │         │
  │       │        │         │         │       │       │         │
  │       │        │<────Text:"ayuda"─┤       │       │         │
  │       │        │         │         │       │       │         │
  │       │        ├─get_context()────────────────────────────>│
  │       │        │         │         │       │       │  SELECT │
  │       │        │<────Context: "Clase de Matemáticas"───────┤
  │       │        │         │         │       │       │         │
  │       │        ├─POST /gpt4/complete─────>│       │         │
  │       │        │    {text, context}        │       │         │
  │       │        │         │         │       │       │         │
  │       │        │         │         ├─GPT-4 Turbo   │         │
  │       │        │         │         │  (Generate)   │         │
  │       │        │         │         │       │       │         │
  │       │        │<────Response:"Las ecuaciones..."──┤         │
  │       │        │         │         │       │       │         │
  │       │        ├─POST /tts/synthesize──────────>│  │         │
  │       │        │    {text: "Las ecuaciones..."}  │  │         │
  │       │        │         │         │       │       │         │
  │       │        │         │         │       ├─TTS   │         │
  │       │        │         │         │       │  API  │         │
  │       │        │         │         │       │       │         │
  │       │        │<────Audio file URL────────┤       │         │
  │       │        │         │         │       │       │         │
  │       │        ├─Upload audio─────────────────────>│         │
  │       │        │         │         │       │   S3  │         │
  │       │        │<────URL─────────────────────────<┤         │
  │       │        │         │         │       │       │         │
  │       │        ├─INSERT interaccion────────────────────────>│
  │       │        │  {user, question, answer, audio} │         │
  │       │        │<────OK───────────────────────────────────<┤
  │       │        │         │         │       │       │         │
  │       ├─Play audio──────>│         │       │       │         │
  │       │  in Jitsi        │         │       │       │         │
  │       │        │         │         │       │       │         │
  │<──Escucha─────┤          │         │       │       │         │
  │  a Rutilio    │          │         │       │       │         │
  │  hablando     │          │         │       │       │         │
```

---

## 🗄️ MODELO DE DATOS

### **Diagrama Entidad-Relación**

```
┌────────────────────────┐
│      SalaChat          │
│────────────────────────│
│ id (PK)                │
│ nombre                 │
│ tipo_sala              │
└───────┬────────────────┘
        │
        │ 1:N
        │
┌───────▼────────────────┐
│    Videollamada        │
│────────────────────────│
│ id (PK)                │◄────────────┐
│ sala_chat_id (FK)      │             │
│ jitsi_room_name (UQ)   │             │ 1:N
│ iniciada_por_id (FK)   │             │
│ tipo_llamada           │     ┌───────┴──────────────┐
│ estado                 │     │  GrabacionVL         │
│ participantes_ids[]    │     │──────────────────────│
│ permite_grabar         │     │ id (PK)              │
│ transcripcion_habilitada│    │ videollamada_id (FK) │
│ rutilio_habilitado     │     │ url_archivo          │
│ fecha_inicio           │     │ duracion_segundos    │
│ duracion_segundos      │     │ tamano_bytes         │
└───────┬────────────────┘     │ estado_procesamiento │
        │                      └──────────────────────┘
        │ 1:N
        │
┌───────▼────────────────┐
│  TranscripcionVL       │
│────────────────────────│
│ id (PK)                │
│ videollamada_id (FK)   │
│ transcripcion_completa │
│ segmentos [JSON]       │◄────────────┐
│ resumen_ia             │             │
│ temas_principales[]    │             │
│ action_items [JSON]    │             │ N:1
│ search_vector          │             │
└───────┬────────────────┘     ┌───────┴──────────────┐
        │                      │  Usuario             │
        │                      │──────────────────────│
┌───────▼────────────────┐     │ id (PK)              │
│  InteraccionIAVL       │     │ nombre               │
│────────────────────────│     │ email                │
│ id (PK)                │     │ rol                  │
│ videollamada_id (FK)   ├────>│                      │
│ usuario_id (FK)        │     └──────────────────────┘
│ tipo_interaccion       │
│ texto_usuario          │
│ texto_ia               │
│ audio_ia_url           │
│ tiempo_respuesta_ms    │
└────────────────────────┘

┌────────────────────────┐
│  NotificacionVL        │
│────────────────────────│
│ id (PK)                │
│ videollamada_id (FK)   │
│ usuario_id (FK)        │
│ tipo_notificacion      │
│ titulo                 │
│ mensaje                │
│ es_leida               │
│ fecha_creacion         │
└────────────────────────┘
```

### **Relaciones Clave**

```
SalaChat ──1:N──> Videollamada
Usuario  ──1:N──> Videollamada (iniciada_por)
Videollamada ──1:N──> GrabacionVideollamada
Videollamada ──1:N──> TranscripcionVideollamada
Videollamada ──1:N──> InteraccionIAVideollamada
Videollamada ──1:N──> NotificacionVideollamada
Usuario ──1:N──> InteraccionIAVideollamada
Usuario ──1:N──> NotificacionVideollamada
```

---

## 🎨 COMPONENTES FRONTEND

### **Estructura de Componentes**

```
src/
├── pages/
│   └── ChatView.tsx
│       ├── <ChatHeader>
│       │   └── <VideollamadaButton>  ← Botón principal
│       │
│       ├── <ChatMessages>
│       │   └── (mensajes del chat)
│       │
│       └── <ChatInput>
│
├── components/
│   ├── communication/
│   │   ├── VideollamadaButton.tsx
│   │   │   Props: salaId, onIniciar
│   │   │   State: loading, error
│   │   │   │
│   │   │   ├── <Dropdown>
│   │   │   │   ├── Videollamada 🎥
│   │   │   │   ├── Solo Voz 🎙️
│   │   │   │   └── Compartir 🖥️
│   │   │   │
│   │   │   └── onClick → iniciarVideollamada()
│   │   │
│   │   ├── JitsiMeetModal.tsx
│   │   │   Props: roomName, jwtToken, onClose
│   │   │   State: api, participants
│   │   │   │
│   │   │   ├── <div ref={jitsiContainer}>
│   │   │   │   └── (Jitsi renders here)
│   │   │   │
│   │   │   ├── <CallControls>
│   │   │   │   ├── Mute/Unmute
│   │   │   │   ├── Video On/Off
│   │   │   │   ├── Compartir Pantalla
│   │   │   │   └── Salir
│   │   │   │
│   │   │   └── <ParticipantesCallList>
│   │   │
│   │   ├── ParticipantesCallList.tsx
│   │   │   Props: participants[]
│   │   │   │
│   │   │   └── participants.map(p =>
│   │   │       <ParticipantCard>
│   │   │         ├── Avatar
│   │   │         ├── Nombre
│   │   │         ├── 🎤 (muted indicator)
│   │   │         ├── 🎥 (video indicator)
│   │   │         └── Admin actions (si admin)
│   │   │       </ParticipantCard>
│   │   │     )
│   │   │
│   │   └── TranscripcionLive.tsx
│   │       Props: videollamadaId
│   │       State: segments[], autoScroll
│   │       │
│   │       ├── <Header>
│   │       │   ├── "Transcripción en vivo"
│   │       │   ├── <SearchBox>
│   │       │   └── <ExportButton>
│   │       │
│   │       └── <SegmentsList>
│   │           └── segments.map(s =>
│   │               <Segment>
│   │                 ├── [HH:MM:SS]
│   │                 ├── Speaker: Juan
│   │                 └── "Hoy veremos..."
│   │               </Segment>
│   │             )
│   │
│   └── ia/
│       └── RutilioAssistant.tsx
│           Props: videollamadaId
│           State: listening, speaking, messages[]
│           │
│           ├── <FloatingWidget>
│           │   ├── 🤖 Avatar
│           │   ├── Status indicator
│           │   └── onClick → expandir()
│           │
│           ├── <Expanded> (cuando activo)
│           │   ├── <MessageList>
│           │   │   └── messages.map(m =>
│           │   │       <Message>
│           │   │         ├── User: "¿tema?"
│           │   │         └── Rutilio: "Ecuaciones"
│           │   │       </Message>
│           │   │     )
│           │   │
│           │   ├── <VoiceButton>
│           │   │   └── "@Rutilio..." (hint)
│           │   │
│           │   └── <Settings>
│           │       ├── TTS toggle
│           │       └── Auto-respond
│           │
│           └── useEffect(() => {
│               ws.on('ia_response', handleResponse)
│             })
│
└── hooks/
    └── useVideollamada.ts
        Return: {
          videollamada,
          loading,
          error,
          iniciar(),
          unirse(),
          finalizar(),
          toggleAudio(),
          toggleVideo(),
          participants
        }
```

### **Estado Global (Context)**

```typescript
// VideollamadaContext
{
  // Estado de la llamada actual
  videollamadaActiva: Videollamada | null,
  
  // WebSocket connection
  ws: WebSocket,
  
  // Participantes en tiempo real
  participants: Participant[],
  
  // Transcripción en vivo
  transcripcionSegments: Segment[],
  
  // Interacciones IA
  iaMessages: IAMessage[],
  
  // Métodos
  iniciarLlamada: (tipo) => Promise<void>,
  unirseALlamada: (id) => Promise<void>,
  finalizarLlamada: () => Promise<void>,
  mencionarRutilio: (texto) => Promise<void>
}
```

---

## 🔌 INTEGRACIONES

### **Integración con Jitsi Meet**

```typescript
// Inicialización de Jitsi
const options = {
  roomName: 'acadify_sala123_xyz',
  parentNode: containerRef.current,
  jwt: 'eyJhbGciOiJIUzI1NiIsInR5cCI6...',
  
  configOverwrite: {
    startWithAudioMuted: false,
    startWithVideoMuted: false,
    enableWelcomePage: false,
    prejoinPageEnabled: true,
    disableDeepLinking: true,
    
    // Features
    toolbarButtons: [
      'microphone', 'camera', 'desktop',
      'fullscreen', 'hangup', 'settings',
      'raisehand', 'videoquality', 'filmstrip',
      'invite', 'recording', 'chat'
    ]
  },
  
  interfaceConfigOverwrite: {
    SHOW_JITSI_WATERMARK: false,
    BRAND_WATERMARK_LINK: '',
    DEFAULT_LOGO_URL: '/logo-acadify.png',
    APP_NAME: 'Acadify'
  }
};

const api = new JitsiMeetExternalAPI('meet.jit.si', options);

// Event listeners
api.on('videoConferenceJoined', (data) => {
  console.log('Usuario se unió:', data);
});

api.on('participantJoined', (data) => {
  agregarParticipante(data.id, data.displayName);
});

api.on('participantLeft', (data) => {
  removerParticipante(data.id);
});

api.on('audioMuteStatusChanged', (data) => {
  actualizarEstadoAudio(data.muted);
});
```

### **Integración con OpenAI APIs**

```python
# Transcripción con Whisper
import openai

async def transcribir_audio(audio_file_path: str) -> str:
    """
    Transcribe audio usando Whisper API.
    
    Args:
        audio_file_path: Path al archivo de audio
        
    Returns:
        Texto transcrito
    """
    with open(audio_file_path, 'rb') as audio_file:
        transcript = await openai.Audio.atranscribe(
            model="whisper-1",
            file=audio_file,
            language="es",  # Español
            response_format="verbose_json",  # Con timestamps
            timestamp_granularities=["word", "segment"]
        )
    
    return transcript.text

# Respuestas con GPT-4
async def generar_respuesta(pregunta: str, contexto: dict) -> str:
    """
    Genera respuesta inteligente con GPT-4.
    
    Args:
        pregunta: Pregunta del usuario
        contexto: Contexto de la llamada (tema, participantes, etc.)
        
    Returns:
        Respuesta generada
    """
    messages = [
        {
            "role": "system",
            "content": f"""Eres Rutilio, un asistente IA para educación.
            Contexto: {contexto['tema']}
            Participantes: {', '.join(contexto['participantes'])}
            Responde de forma clara, concisa y educativa."""
        },
        {
            "role": "user",
            "content": pregunta
        }
    ]
    
    response = await openai.ChatCompletion.acreate(
        model="gpt-4-turbo-preview",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Text-to-Speech
async def generar_audio(texto: str) -> bytes:
    """
    Convierte texto a audio con TTS.
    
    Args:
        texto: Texto a convertir
        
    Returns:
        Audio en bytes
    """
    response = await openai.Audio.speech.acreate(
        model="tts-1",
        voice="alloy",  # Voz masculina clara
        input=texto,
        speed=1.0
    )
    
    return response.content
```

### **Integración con Storage (MinIO/S3)**

```python
from minio import Minio
from datetime import timedelta

class StorageService:
    """Servicio para almacenar archivos."""
    
    def __init__(self):
        self.client = Minio(
            "storage.acadify.com",
            access_key="ACCESSKEY",
            secret_key="SECRETKEY",
            secure=True
        )
        self.bucket = "videollamadas"
    
    async def upload_video(
        self,
        file: bytes,
        filename: str
    ) -> str:
        """
        Sube video a storage.
        
        Args:
            file: Contenido del archivo en bytes
            filename: Nombre del archivo
            
        Returns:
            URL pública del archivo
        """
        # Subir archivo
        self.client.put_object(
            self.bucket,
            filename,
            file,
            length=len(file),
            content_type="video/mp4"
        )
        
        # Generar URL pre-firmada (válida 7 días)
        url = self.client.presigned_get_object(
            self.bucket,
            filename,
            expires=timedelta(days=7)
        )
        
        return url
    
    async def delete_video(self, filename: str) -> bool:
        """
        Elimina video del storage.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            self.client.remove_object(self.bucket, filename)
            return True
        except Exception as e:
            logger.error(f"Error eliminando video: {e}")
            return False
```

---

## 📱 INTERFACES DE USUARIO (Mockups)

### **Vista: Chat con Botón de Videollamada**

```
┌─────────────────────────────────────────────────┐
│ ◀ Matemáticas 101                  👤 [📹] ⚙️  │← Botón videollamada
├─────────────────────────────────────────────────┤
│                                                 │
│  Juan: Hola a todos                             │
│  [10:30 AM]                                     │
│                                                 │
│  María: Buenos días profesor                    │
│  [10:31 AM]                                     │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ 🔴 Profesor inició una videollamada      │ │← Alerta llamada activa
│  │ 12 participantes conectados               │ │
│  │ [Unirse a la llamada]                     │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Pedro: ¿Alguien tiene dudas?                  │
│  [10:35 AM]                                     │
│                                                 │
├─────────────────────────────────────────────────┤
│ 💬 Escribe un mensaje...            📎 😊 🎤  │
└─────────────────────────────────────────────────┘
```

### **Vista: Modal de Jitsi con Rutilio**

```
┌───────────────────────────────────────────────────────────────┐
│ Matemáticas 101 - Videollamada            ⚙️  📊  ✕          │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │                 │  │                 │  │              │ │
│  │   Profesor      │  │     María       │  │    Juan      │ │
│  │   [Video]       │  │   [Video]       │  │   [Video]    │ │
│  │                 │  │                 │  │              │ │
│  │  🎤            │  │  🎤 🔇         │  │  🎤         │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │                 │  │                 │                   │
│  │     Pedro       │  │     Ana         │                   │
│  │   [Video]       │  │   [Video]       │                   │
│  │                 │  │                 │                   │
│  │  🎤            │  │  🎤            │                   │
│  └─────────────────┘  └─────────────────┘                   │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│  🎤  🎥  🖥️  💬  👥  🎨  ⚙️  📞                           │← Controls
└───────────────────────────────────────────────────────────────┘
                                   │
                                   │  ┌──────────────────────┐
                                   └─→│ 🤖 Rutilio          │
                                      │                      │
                                      │ "Estoy escuchando    │
                                      │  mencióname con      │
                                      │  @Rutilio"           │
                                      │                      │
                                      │ [🎤 Activar voz]    │
                                      └──────────────────────┘
```

### **Vista: Panel de Transcripción**

```
┌─────────────────────────────────────────┐
│ 📝 Transcripción en vivo          🔍 ⚙️ │
├─────────────────────────────────────────┤
│                                         │
│ [00:00:15] Profesor:                    │
│ "Hoy vamos a ver ecuaciones lineales"   │
│                                         │
│ [00:00:32] María:                       │
│ "¿Empezamos con ejemplos?"              │
│                                         │
│ [00:00:45] Profesor:                    │
│ "Sí, veamos el primer ejemplo"          │
│                                         │
│ [00:01:10] Juan:                        │
│ "@Rutilio, ¿qué es una ecuación?"       │
│                                         │
│ [00:01:13] 🤖 Rutilio:                  │
│ "Una ecuación es una igualdad entre    │
│  dos expresiones matemáticas..."        │
│                                         │
│ [00:01:45] Profesor:                    │
│ "Exacto, gracias Rutilio"               │
│                                         │
│ ───────────────────────────────────────│← Auto-scroll
│ [Exportar] [Buscar] [Pausar Auto-scroll]│
└─────────────────────────────────────────┘
```

---

**Fin del Documento de Diagramas**

📌 **Nota**: Estos diagramas son representaciones visuales en ASCII. En la documentación final se pueden crear con herramientas como:
- Draw.io / diagrams.net
- Lucidchart
- Mermaid.js
- PlantUML

