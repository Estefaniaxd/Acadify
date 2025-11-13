# 🗺️ Roadmap de Desarrollo - Acadify

**Fecha de inicio:** 28 de octubre de 2025  
**Estado actual:** En desarrollo activo  
**Progreso general:** 40% completado

---

## 📋 Estado Actual del Proyecto

### ✅ Completado (40%)

1. **Arquitectura Base**
   - ✅ Estructura de proyecto con FastAPI
   - ✅ Base de datos PostgreSQL (57 tablas)
   - ✅ Sistema de autenticación
   - ✅ Modelo de usuarios y roles

2. **Refactorización y Optimización**
   - ✅ 6 servicios con SOLID principles (2,469 líneas)
   - ✅ 49 índices de BD aplicados
   - ✅ Eliminación de N+1 queries
   - ✅ Paginación global (24 endpoints)
   - ✅ Documentación técnica completa

3. **Funcionalidades Básicas**
   - ✅ Gestión de cursos (básica)
   - ✅ Comentarios y reacciones
   - ✅ Sistema de tareas (básico)
   - ✅ Inscripciones con códigos de invitación
   - ✅ Sistema de archivos

---

## 🔧 En Progreso (10%)

### 1. Tests Unitarios (En curso)
- 🔄 Setup de pytest configurado
- 🔄 Tests de utilidades (pagination)
- ⏳ Tests de servicios (0/6)
- ⏳ Tests de routes (0/24)
- ⏳ Tests de CRUD (0/15)

**Meta:** 70% code coverage  
**Tiempo estimado:** 1 semana

---

## 🚧 Pendiente - Alta Prioridad (25%)

### 2. Sistema de Avatares (Arreglar) 🎭
**Prioridad:** 🔴 ALTA  
**Estado:** Bugs reportados  
**Tiempo estimado:** 3-4 días

**Problemas a resolver:**
- [ ] Errores en creación de avatares personalizados
- [ ] Sistema de categorías de ítems (cabeza, cuerpo, piernas, etc.)
- [ ] Gestión de assets de avatares
- [ ] Serialización y deserialización de configuración
- [ ] Preview de avatar en tiempo real

**Tareas:**
```python
# Estructura objetivo
Avatar:
  - base_avatar_id (plantilla base)
  - customizations:
    - head_item_id
    - body_item_id
    - legs_item_id
    - accessories[]
  - colors:
    - skin_color
    - hair_color
    - outfit_color
```

**Archivos a revisar:**
- `src/models/gamification/avatar.py`
- `src/schemas/gamification/avatar.py`
- `src/crud/gamification/avatar.py`
- `src/api/routes/gamification/avatares.py`

---

### 3. Gestión de Cursos (Mejorar) 📚
**Prioridad:** 🔴 ALTA  
**Estado:** Funcional pero incompleto  
**Tiempo estimado:** 5-7 días

**Funcionalidades a agregar:**
- [ ] Sistema de módulos/unidades dentro de cursos
- [ ] Prerrequisitos de cursos
- [ ] Duplicación de cursos (plantillas)
- [ ] Exportar/Importar contenido de curso
- [ ] Sistema de versiones de curso
- [ ] Estadísticas avanzadas del curso
- [ ] Certificados de finalización
- [ ] Progreso del estudiante (%)

**Estructura nueva:**
```
Curso
└── Módulos (orden secuencial)
    └── Lecciones/Clases
        ├── Contenido (texto, video, archivos)
        ├── Tareas
        ├── Exámenes
        └── Recursos adicionales
```

---

### 4. Sistema de Instituciones (Mejorar) 🏫
**Prioridad:** 🔴 ALTA  
**Estado:** Básico, necesita expansión  
**Tiempo estimado:** 3-4 días

**Funcionalidades pendientes:**
- [ ] Configuración personalizada por institución
  - [ ] Logo, colores, branding
  - [ ] Políticas de calificación
  - [ ] Formatos de documento
- [ ] Dashboard de administración institucional
- [ ] Reportes y analytics institucionales
- [ ] Gestión de períodos académicos
- [ ] Gestión de sedes/campus
- [ ] Configuración de horarios institucionales

---

### 5. Sistema de Tareas (Mejorar) 📝
**Prioridad:** 🟡 MEDIA-ALTA  
**Estado:** Básico, necesita expansión  
**Tiempo estimado:** 4-5 días

**Funcionalidades a agregar:**
- [ ] Tipos de tareas:
  - [ ] Tarea individual
  - [ ] Tarea grupal
  - [ ] Quiz/Examen
  - [ ] Proyecto
  - [ ] Presentación
- [ ] Rúbricas de calificación
- [ ] Peer review (evaluación entre pares)
- [ ] Entregas múltiples/iteraciones
- [ ] Plagio detection (integración con Turnitin o similar)
- [ ] Comentarios inline en entregas
- [ ] Estadísticas de tareas:
  - [ ] Tiempo promedio de entrega
  - [ ] Distribución de calificaciones
  - [ ] Tasa de entregas tardías

---

## 🎮 Pendiente - Gamificación (15%)

### 6. Sistema de Puntos y Categorías ⭐
**Prioridad:** 🟡 MEDIA  
**Estado:** Básico, necesita categorías  
**Tiempo estimado:** 3-4 días

**Categorías de usuarios:**
- [ ] **Novato** (0-100 puntos)
  - Color: Gris
  - Insignia: 🌱
  
- [ ] **Aprendiz** (101-500 puntos)
  - Color: Verde
  - Insignia: 📚
  
- [ ] **Competente** (501-1,500 puntos)
  - Color: Azul
  - Insignia: ⚡
  
- [ ] **Experto** (1,501-5,000 puntos)
  - Color: Púrpura
  - Insignia: 🏆
  
- [ ] **Épico** (5,001-15,000 puntos)
  - Color: Dorado
  - Insignia: 👑
  - Beneficios especiales
  
- [ ] **Legendario** (15,001+ puntos)
  - Color: Arcoíris/Platino
  - Insignia: 💎
  - Beneficios premium
  - Hall of Fame

**Funcionalidades:**
```python
# Sistema de niveles
class NivelUsuario:
    nivel: str
    puntos_minimos: int
    puntos_maximos: int
    color: str
    insignia: str
    beneficios: List[str]
    multiplicador_puntos: float  # 1.0 - 2.0

# Eventos que otorgan puntos
PUNTOS_EVENTOS = {
    "completar_tarea": 10,
    "entregar_a_tiempo": 5,
    "comentario_util": 2,
    "ayudar_compañero": 15,
    "excelencia_academica": 50,  # 100% en tarea
    "racha_entregas": 25,  # 5 tareas seguidas
    "participacion_activa": 3,  # Por comentario
}
```

---

### 7. Sistema de Insignias Mejorado 🏅
**Prioridad:** 🟡 MEDIA  
**Estado:** Básico  
**Tiempo estimado:** 2-3 días

**Tipos de insignias:**
- [ ] **Por logros académicos**
  - 📖 "Estudiante Dedicado" (10 tareas completadas)
  - 🎯 "Perfeccionista" (5 tareas con 100%)
  - 🔥 "En Racha" (Entregas a tiempo 10 días seguidos)
  - 📚 "Enciclopedia" (Completar 5 cursos)

- [ ] **Por participación**
  - 💬 "Conversador" (50 comentarios)
  - 🤝 "Colaborador" (Ayudar a 10 compañeros)
  - ⭐ "Mentor" (Respuestas útiles votadas)

- [ ] **Por tiempo**
  - 🎂 "Veterano" (1 año en plataforma)
  - 🌟 "Pionero" (Usuario de los primeros 100)

- [ ] **Especiales/Raras**
  - 🏆 "Excelencia Académica" (Promedio 95%+)
  - 💎 "Contribuidor Épico" (Otorgada por admins)
  - 🎓 "Graduado con Honores"

---

### 8. Sistema de Recompensas Expandido 🎁
**Prioridad:** 🟢 MEDIA-BAJA  
**Estado:** Básico  
**Tiempo estimado:** 2-3 días

**Recompensas canjeables:**
- [ ] **Virtuales**
  - Avatares premium
  - Marcos/bordes especiales
  - Temas de interfaz personalizados
  - Emojis exclusivos
  - Stickers personalizados

- [ ] **Académicas**
  - Extensión de plazo (1 tarea)
  - Segundo intento en examen
  - Consulta privada con docente
  - Acceso anticipado a material

- [ ] **Físicas** (si aplica)
  - Merchandising institucional
  - Descuentos en cafetería
  - Vouchers

---

## 💬 Pendiente - Comunicación en Tiempo Real (20%)

### 9. Sistema de Chat en Tiempo Real 💬
**Prioridad:** 🔴 ALTA  
**Estado:** No implementado  
**Tiempo estimado:** 2 semanas

**Tecnologías:**
- WebSockets (FastAPI WebSocket)
- Redis para pub/sub
- PostgreSQL para persistencia

**Funcionalidades:**
```
Chat Features:
├── Chat 1-a-1 (privado)
│   ├── Mensajes de texto
│   ├── Emojis y reacciones
│   ├── Archivos adjuntos
│   ├── Estados: enviado, leído
│   └── Notificaciones push
│
├── Chat grupal (curso/grupo)
│   ├── Canales por tema
│   ├── Mensajes fijados
│   ├── Menciones (@usuario)
│   ├── Hilos de conversación
│   └── Roles y permisos
│
└── Características avanzadas
    ├── Búsqueda de mensajes
    ├── Historial persistente
    ├── Indicador "escribiendo..."
    ├── Presencia (online/offline)
    └── Encriptación E2E (opcional)
```

**Estructura de Base de Datos:**
```sql
CREATE TABLE "Sala" (
    sala_id UUID PRIMARY KEY,
    tipo VARCHAR(20),  -- 'privado', 'grupo', 'curso'
    nombre VARCHAR(100),
    curso_id UUID REFERENCES "Curso",
    creado_por UUID REFERENCES "Usuario",
    fecha_creacion TIMESTAMP
);

CREATE TABLE "SalaMiembro" (
    sala_id UUID REFERENCES "Sala",
    usuario_id UUID REFERENCES "Usuario",
    rol VARCHAR(20),  -- 'admin', 'miembro'
    fecha_union TIMESTAMP,
    PRIMARY KEY (sala_id, usuario_id)
);

CREATE TABLE "Mensaje" (
    mensaje_id UUID PRIMARY KEY,
    sala_id UUID REFERENCES "Sala",
    usuario_id UUID REFERENCES "Usuario",
    contenido TEXT,
    tipo VARCHAR(20),  -- 'texto', 'archivo', 'imagen'
    archivo_url TEXT,
    respondiendo_a UUID REFERENCES "Mensaje",
    fecha_envio TIMESTAMP,
    editado BOOLEAN,
    eliminado BOOLEAN
);

CREATE TABLE "MensajeLeido" (
    mensaje_id UUID REFERENCES "Mensaje",
    usuario_id UUID REFERENCES "Usuario",
    fecha_lectura TIMESTAMP,
    PRIMARY KEY (mensaje_id, usuario_id)
);
```

**Implementación:**
```python
# backend/src/api/routes/chat/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import redis

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis = redis.Redis(host='localhost', port=6379)
    
    async def connect(self, websocket: WebSocket, sala_id: str):
        await websocket.accept()
        if sala_id not in self.active_connections:
            self.active_connections[sala_id] = set()
        self.active_connections[sala_id].add(websocket)
    
    async def broadcast(self, sala_id: str, message: dict):
        if sala_id in self.active_connections:
            for connection in self.active_connections[sala_id]:
                await connection.send_json(message)
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/chat/{sala_id}")
async def websocket_chat(
    websocket: WebSocket,
    sala_id: str,
    current_user: Usuario = Depends(get_current_user_ws)
):
    await manager.connect(websocket, sala_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Procesar mensaje
            mensaje = {
                "mensaje_id": str(uuid4()),
                "sala_id": sala_id,
                "usuario_id": str(current_user.usuario_id),
                "usuario_nombre": current_user.nombres,
                "contenido": data["contenido"],
                "fecha_envio": datetime.now().isoformat(),
                "tipo": data.get("tipo", "texto")
            }
            
            # Guardar en BD
            await save_mensaje_db(mensaje)
            
            # Broadcast a sala
            await manager.broadcast(sala_id, mensaje)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, sala_id)
```

---

### 10. Sistema de Videollamadas con Jitsi 📹
**Prioridad:** 🔴 ALTA  
**Estado:** No implementado  
**Tiempo estimado:** 1.5 semanas

**Tecnología:** Jitsi Meet (Self-hosted o Jitsi as a Service)

**Funcionalidades:**
```
Video Features:
├── Reuniones 1-a-1
├── Reuniones grupales (hasta 100 personas)
├── Compartir pantalla
├── Grabación de sesiones
├── Chat durante videollamada
├── Levantar mano
├── Encuestas/Votaciones en vivo
├── Breakout rooms (salas de grupos)
└── Whiteboard colaborativo
```

**Configuración de Jitsi:**
```yaml
# docker-compose.yml para Jitsi
version: '3.8'
services:
  jitsi-web:
    image: jitsi/web:latest
    ports:
      - "8443:443"
    environment:
      - PUBLIC_URL=https://meet.acadify.com
      - ENABLE_RECORDING=1
      - ENABLE_TRANSCRIPTIONS=1
    volumes:
      - ./jitsi-config:/config
  
  jitsi-prosody:
    image: jitsi/prosody:latest
    expose:
      - "5222"
      - "5347"
      - "5280"
    environment:
      - AUTH_TYPE=jwt
      - JWT_APP_ID=acadify
      - JWT_APP_SECRET=${JWT_SECRET}
  
  jitsi-jicofo:
    image: jitsi/jicofo:latest
    depends_on:
      - prosody
  
  jitsi-jvb:
    image: jitsi/jvb:latest
    ports:
      - "10000:10000/udp"
    environment:
      - JVB_AUTH_USER=jvb
      - JVB_AUTH_PASSWORD=${JVB_PASSWORD}
```

**Integración con Backend:**
```python
# backend/src/services/communication/jitsi_service.py
import jwt
from datetime import datetime, timedelta
from typing import Optional

class JitsiService:
    def __init__(self):
        self.app_id = settings.JITSI_APP_ID
        self.secret = settings.JITSI_SECRET
        self.domain = settings.JITSI_DOMAIN
    
    def generar_token_reunion(
        self,
        room_name: str,
        usuario: Usuario,
        moderador: bool = False,
        duracion_minutos: int = 120
    ) -> str:
        """Genera JWT token para acceso a Jitsi"""
        payload = {
            "context": {
                "user": {
                    "id": str(usuario.usuario_id),
                    "name": f"{usuario.nombres} {usuario.apellidos}",
                    "email": usuario.correo_institucional,
                    "avatar": usuario.perfil_url,
                },
                "group": room_name
            },
            "aud": self.app_id,
            "iss": self.app_id,
            "sub": self.domain,
            "room": room_name,
            "exp": datetime.utcnow() + timedelta(minutes=duracion_minutos),
            "moderator": moderador
        }
        
        return jwt.encode(payload, self.secret, algorithm="HS256")
    
    def crear_reunion(
        self,
        curso_id: str,
        titulo: str,
        creador_id: str,
        fecha_inicio: datetime,
        duracion_minutos: int,
        db: Session
    ) -> dict:
        """Crea una nueva reunión programada"""
        room_name = f"curso_{curso_id}_{datetime.now().timestamp()}"
        
        reunion = Reunion(
            reunion_id=uuid4(),
            curso_id=curso_id,
            titulo=titulo,
            room_name=room_name,
            creador_id=creador_id,
            fecha_inicio=fecha_inicio,
            duracion_minutos=duracion_minutos,
            estado="programada"
        )
        
        db.add(reunion)
        db.commit()
        
        return {
            "reunion_id": str(reunion.reunion_id),
            "room_name": room_name,
            "url_reunion": f"https://{self.domain}/{room_name}",
            "fecha_inicio": fecha_inicio.isoformat(),
            "duracion_minutos": duracion_minutos
        }
    
    def obtener_url_reunion(
        self,
        room_name: str,
        usuario: Usuario,
        moderador: bool = False
    ) -> str:
        """Obtiene URL con JWT para unirse a reunión"""
        token = self.generar_token_reunion(room_name, usuario, moderador)
        return f"https://{self.domain}/{room_name}?jwt={token}"

# backend/src/models/communication/reunion.py
class Reunion(Base):
    __tablename__ = "Reunion"
    
    reunion_id = Column(UUID, primary_key=True, default=uuid4)
    curso_id = Column(UUID, ForeignKey("Curso.curso_id"))
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    room_name = Column(String(100), unique=True, nullable=False)
    creador_id = Column(UUID, ForeignKey("Usuario.usuario_id"))
    fecha_inicio = Column(DateTime, nullable=False)
    duracion_minutos = Column(Integer, default=60)
    estado = Column(String(20))  # programada, en_curso, finalizada, cancelada
    grabacion_url = Column(Text)
    participantes_esperados = Column(Integer)
    requiere_confirmacion = Column(Boolean, default=False)
    recordatorio_enviado = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    curso = relationship("Curso")
    creador = relationship("Usuario")
    participantes = relationship("ReunionParticipante", back_populates="reunion")

class ReunionParticipante(Base):
    __tablename__ = "ReunionParticipante"
    
    reunion_id = Column(UUID, ForeignKey("Reunion.reunion_id"), primary_key=True)
    usuario_id = Column(UUID, ForeignKey("Usuario.usuario_id"), primary_key=True)
    confirmado = Column(Boolean, default=False)
    asistio = Column(Boolean, default=False)
    tiempo_conexion = Column(Integer)  # minutos conectado
    fecha_confirmacion = Column(DateTime)
    fecha_ingreso = Column(DateTime)
    fecha_salida = Column(DateTime)
    
    reunion = relationship("Reunion", back_populates="participantes")
    usuario = relationship("Usuario")
```

**Frontend Integration (React):**
```tsx
// frontend/src/components/VideoCall/JitsiMeeting.tsx
import React, { useEffect, useRef } from 'react';

interface JitsiMeetingProps {
  roomName: string;
  token: string;
  displayName: string;
  onClose: () => void;
}

export const JitsiMeeting: React.FC<JitsiMeetingProps> = ({
  roomName,
  token,
  displayName,
  onClose
}) => {
  const jitsiContainer = useRef<HTMLDivElement>(null);
  const jitsiApi = useRef<any>(null);
  
  useEffect(() => {
    if (!jitsiContainer.current) return;
    
    const domain = 'meet.acadify.com';
    const options = {
      roomName: roomName,
      jwt: token,
      width: '100%',
      height: '100%',
      parentNode: jitsiContainer.current,
      configOverwrite: {
        startWithAudioMuted: false,
        startWithVideoMuted: false,
        enableWelcomePage: false,
        enableClosePage: false,
        prejoinPageEnabled: false,
        toolbarButtons: [
          'microphone', 'camera', 'desktop', 'fullscreen',
          'fodeviceselection', 'hangup', 'profile',
          'chat', 'recording', 'livestreaming', 'etherpad',
          'sharedvideo', 'settings', 'raisehand',
          'videoquality', 'filmstrip', 'stats', 'shortcuts',
          'tileview', 'videobackgroundblur', 'download', 'help'
        ]
      },
      interfaceConfigOverwrite: {
        SHOW_JITSI_WATERMARK: false,
        SHOW_WATERMARK_FOR_GUESTS: false,
        DEFAULT_BACKGROUND: '#474747',
        DISABLE_JOIN_LEAVE_NOTIFICATIONS: false,
        FILM_STRIP_MAX_HEIGHT: 120,
      },
      userInfo: {
        displayName: displayName
      }
    };
    
    jitsiApi.current = new (window as any).JitsiMeetExternalAPI(domain, options);
    
    // Event listeners
    jitsiApi.current.on('readyToClose', () => {
      onClose();
    });
    
    jitsiApi.current.on('participantJoined', (participant: any) => {
      console.log('Participante unido:', participant);
    });
    
    return () => {
      jitsiApi.current?.dispose();
    };
  }, [roomName, token, displayName, onClose]);
  
  return (
    <div style={{ height: '100vh', width: '100%' }}>
      <div ref={jitsiContainer} style={{ height: '100%', width: '100%' }} />
    </div>
  );
};
```

---

## 📊 Cronograma Estimado

### Fase 1: Estabilización (2 semanas)
**Semana 1-2:**
- ✅ Tests unitarios (70% coverage)
- 🔧 Arreglar avatares
- 🔧 Mejorar gestión de cursos

### Fase 2: Gamificación (1.5 semanas)
**Semana 3-4:**
- ⭐ Sistema de puntos con categorías (Épico, Legendario, etc.)
- 🏅 Sistema de insignias mejorado
- 🎁 Recompensas expandidas

### Fase 3: Comunicación (3 semanas)
**Semana 5-7:**
- 💬 Chat en tiempo real (WebSockets + Redis)
- 📹 Integración con Jitsi Meet
- 🎥 Sistema de reuniones programadas
- 📝 Notificaciones push

### Fase 4: Mejoras Institucionales (1 semana)
**Semana 8:**
- 🏫 Dashboard institucional
- 📊 Reportes y analytics
- ⚙️ Configuraciones personalizadas

### Fase 5: Mejoras Académicas (2 semanas)
**Semana 9-10:**
- 📚 Sistema de módulos en cursos
- 📝 Mejoras en tareas (rúbricas, peer review)
- 🎓 Certificados de finalización
- 📈 Progreso del estudiante

### Fase 6: Testing y Deploy (1 semana)
**Semana 11:**
- 🧪 Tests de integración
- 🚀 Deploy a staging
- 📊 Monitoreo y ajustes

**TOTAL: 11 semanas (~2.5 meses)**

---

## 📈 Métricas de Progreso

| Componente | Completado | Pendiente | Progreso |
|------------|------------|-----------|----------|
| Arquitectura Base | ✅ 100% | - | ████████████████████ |
| Optimización | ✅ 100% | - | ████████████████████ |
| Tests | 🔄 20% | 80% | ████░░░░░░░░░░░░░░░░ |
| Avatares | ❌ 30% | 70% | ██████░░░░░░░░░░░░░░ |
| Cursos | 🔄 60% | 40% | ████████████░░░░░░░░ |
| Instituciones | 🔄 50% | 50% | ██████████░░░░░░░░░░ |
| Tareas | 🔄 50% | 50% | ██████████░░░░░░░░░░ |
| Gamificación | 🔄 40% | 60% | ████████░░░░░░░░░░░░ |
| Chat | ❌ 0% | 100% | ░░░░░░░░░░░░░░░░░░░░ |
| Videollamadas | ❌ 0% | 100% | ░░░░░░░░░░░░░░░░░░░░ |

**Progreso General:** ████████░░░░░░░░░░░░ 40%

---

## 🎯 Priorización de Tareas

### Sprint 1 (Esta semana)
1. 🔴 Completar tests unitarios básicos
2. 🔴 Arreglar sistema de avatares
3. 🟡 Documentar bugs y errores actuales

### Sprint 2 (Próxima semana)
1. 🔴 Implementar chat en tiempo real
2. 🔴 Integrar Jitsi Meet básico
3. 🟡 Mejorar gestión de cursos

### Sprint 3
1. 🟡 Sistema de puntos con categorías
2. 🟡 Insignias mejoradas
3. 🟢 Dashboard institucional

---

## 💡 Notas Técnicas

### Tecnologías a Integrar

**Backend:**
- FastAPI WebSockets (chat)
- Redis (pub/sub, cache)
- Celery (tareas asíncronas)
- FFmpeg (procesamiento de video)

**Frontend:**
- Socket.IO o WebSocket nativo
- Jitsi Meet External API
- React Query (state management)
- Tailwind CSS (UI)

**Infraestructura:**
- Docker containers
- Nginx (reverse proxy)
- PostgreSQL (persistencia)
- Redis (cache + pub/sub)
- Jitsi Meet (self-hosted)

### Consideraciones de Escalabilidad

1. **Chat:** Redis pub/sub + PostgreSQL
2. **Video:** Jitsi con múltiples JVB nodes
3. **Archivos:** S3-compatible storage
4. **Notificaciones:** FCM para push notifications

---

## ✅ Siguiente Acción Inmediata

**AHORA MISMO:**
1. Ejecutar tests existentes
2. Identificar errores específicos en avatares
3. Crear branch para desarrollo de chat

¿Comenzamos con los tests o prefieres que identifique primero los errores en avatares? 🤔
