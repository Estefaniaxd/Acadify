# 🎓 Plan de Desarrollo Completo - Módulo Cursos & Detalle

**Fecha**: 15 de noviembre de 2025  
**Estado**: EN DESARROLLO  
**Versión**: 1.0.0

---

## 📋 Índice

1. [Visión General](#visión-general)
2. [Arquitectura Actual](#arquitectura-actual)
3. [Problemas Identificados](#problemas-identificados)
4. [Soluciones Propuestas](#soluciones-propuestas)
5. [Fases de Implementación](#fases-de-implementación)
6. [Especificaciones Detalladas](#especificaciones-detalladas)

---

## 🎯 Visión General

El módulo de **Cursos** es el corazón de Acadify. Debe proporcionar:

- ✅ **Vista de Cursos**: Listado con tarjetas mostrando progreso, estudiantes, estadísticas
- ✅ **Detalle de Curso**: Vista completa con 4 secciones principales:
  - 📢 **Stream** (Comentarios/Anuncios/Preguntas) con respuestas anidadas
  - 📝 **Tareas** (crear, entregar, calificar, IA feedback)
  - 👥 **Personas** (lista de estudiantes/profesores, estado online, perfil)
  - 📅 **Calendario** (eventos, evaluaciones, plazos)

---

## 🏗️ Arquitectura Actual

### Backend Stack
- **Framework**: FastAPI + SQLAlchemy
- **DB**: PostgreSQL con JSONB, arrays, enums
- **Key Models**: `Curso`, `Comentario`, `Tarea`, `EntregaTarea`, `Usuario`
- **Services**: `CursoService`, `ComentarioService`, `TareaService`

### Frontend Stack
- **Framework**: React 18 + TypeScript + Vite
- **State**: TanStack Query + Zustand
- **Components**: `CourseCard`, `CourseDetail`, `CourseStream`
- **Styling**: TailwindCSS + Framer Motion

---

## 🐛 Problemas Identificados

### CRÍTICO (Bloquea uso)

| # | Problema | Impacto | Solución |
|---|----------|--------|----------|
| 1 | 📎 Archivos adjuntos desaparecen al recargar | Datos perdidos | ✅ RESUELTO - Enriquecimiento en DB |
| 2 | 💬 Respuestas a comentarios aparecen como nuevos msgs | UX confusa | 🔧 En progreso - Logging + fix tipos |
| 3 | 📤 No se pueden subir archivos a comentarios | Feature rota | 🔧 Relacionado con #2 |
| 4 | 😑 Reacciones no funcionan | Feature rota | 🔴 TODO - Rediseño + Backend |

### ALTA PRIORIDAD

| # | Problema | Impacto | Solución |
|---|----------|--------|----------|
| 5 | 📊 Barra progreso no existe | Info incompleta | 🔴 TODO - Helper + UI |
| 6 | 📝 Sistema de tareas muy básico | Funcionalidad limitada | 🔴 TODO - Rediseño completo |
| 7 | 🤖 IA para calificación no integrada | Feature no funcional | 🔴 TODO - Integration |
| 8 | 🟢 Estado online/offline no real | UX confusa | 🔴 TODO - WebSocket |

### MEJORAS UX

| # | Problema | Impacto | Solución |
|---|----------|--------|----------|
| 9 | 📅 Calendario muy simple | UX pobre | 🔴 TODO - Rediseño |
| 10 | 📈 Sin estadísticas | Info faltante | 🔴 TODO - Dashboard |

---

## 💡 Soluciones Propuestas

### 1. Persistencia de Archivos ✅

**Status**: RESUELTO  
**Implementación**: Backend enriquece archivos adjuntos desde `archivos_curso` tabla

```sql
-- DB: Tabla de archivos adjuntos
CREATE TABLE archivos_curso (
    archivo_id UUID PRIMARY KEY,
    curso_id UUID NOT NULL,
    nombre_original VARCHAR(255),
    url TEXT,
    tipo VARCHAR(100),
    tamaño INTEGER,
    fecha_subida TIMESTAMP,
    subido_por UUID
);

-- Relación: Comentario.archivos_adjuntos → archivos_curso
```

**Validación**: Test `test_create_comment_with_attachment_and_get` ✅ PASSING

---

### 2. Respuestas Anidadas a Comentarios 🔧

**Status**: En progreso  
**Diseño**:

```
Comentario Principal (padre)
├── Respuesta 1
├── Respuesta 2
└── Respuesta 3 (mostrar 2, "Ver más")
```

**Model**:
```python
class Comentario(Base):
    comentario_id: UUID
    comentario_padre_id: UUID | None  # None = es comentario, != None = es respuesta
    contenido: str
    archivos_adjuntos: JSON  # [{"archivo_id", "nombre", "url"...}]
    fecha_creacion: DateTime
```

**Endpoints**:
- `POST /cursos/{id}/comentarios` - crear comentario (o respuesta si incluye `comentario_padre_id`)
- `GET /cursos/{id}/comentarios` - listar comentarios con respuestas anidadas (eager load)
- `GET /comentarios/{id}/respuestas?limit=5&offset=0` - paginar respuestas

**Frontend Flow**:
```typescript
// Load principal comments + all nested replies
const comments = await courseService.getComments(courseId);
// comments[0] = { comentario_id, contenido, respuestas: [...] }

// When user clicks "Reply"
await courseService.createComment(courseId, {
  contenido: "Mi respuesta",
  comentario_padre_id: comments[0].comentario_id,  // <-- Key!
  archivos_adjuntos: [...]
});

// Refresh will show reply as child, not new top-level
```

**Test**: Crear test que verifique:
1. ✅ Crear comentario principal
2. ✅ Crear respuesta (`comentario_padre_id` != null)
3. ✅ GET comentarios retorna respuestas anidadas
4. ✅ Reload página → respuesta sigue siendo hijo

---

### 3. Sistema de Reacciones estilo Discord 🔴

**UI Diseño**:
```
Comment Card
├── Content
├── Attachments
└── Reactions Bar
    ├── 👍 3        <- Hover: "Tú, Juan, María"
    ├── ❤️ 2         <- Hover: "Tú, Pedro"
    ├── 😂 1         <- Hover: "Sofia"
    └── [+ Agregar]  <- EmojiPicker Modal
```

**Backend API**:
```python
# POST /comentarios/{id}/reacciones
{
  "tipo_emoji": "👍"  # Unicode emoji
}

# GET /comentarios/{id}/reacciones
# Response:
{
  "reacciones": [
    {
      "tipo_emoji": "👍",
      "count": 3,
      "mi_reaccion": true,  # Usuario actual reaccionó?
      "usuarios": ["juan_id", "maria_id", "tu_id"]
    }
  ]
}

# DELETE /comentarios/{id}/reacciones/{emoji}
# Remueve tu reacción de ese emoji
```

**DB**:
```sql
CREATE TABLE reacciones (
    reaccion_id UUID PRIMARY KEY,
    comentario_id UUID NOT NULL,
    usuario_id UUID NOT NULL,
    tipo_emoji VARCHAR(10),  -- "👍", "❤️", "😂", etc
    fecha_creacion TIMESTAMP,
    UNIQUE(comentario_id, usuario_id, tipo_emoji)
);
```

**Frontend**:
- Usar `emoji-picker-react` para modal
- Groupby emoji en GET respuesta
- Counter + hover tooltip

---

### 4. Barra de Progreso del Curso 📊

**Cálculo**:
```
progreso (%) = (hoy - fecha_inicio) / (fecha_fin - fecha_inicio) * 100

Ejemplo:
- Curso inicia: 1 Nov
- Curso termina: 30 Nov (30 días)
- Hoy: 15 Nov (14 días transcurridos)
- Progreso: 14/30 = 46.7%
```

**UI en CourseCard**:
```jsx
<div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
  <div 
    className="h-full bg-gradient-to-r from-blue-400 to-blue-600"
    style={{ width: `${progreso}%` }}
  />
</div>
<span className="text-sm text-gray-600">{progreso}% completado</span>
```

**Backend Helper**:
```python
@staticmethod
def calcular_progreso_curso(curso: Curso) -> float:
    """Calcula progreso del curso (0-100%)"""
    if not curso.fecha_inicio or not curso.fecha_fin:
        return 0.0
    
    hoy = date.today()
    if hoy < curso.fecha_inicio:
        return 0.0
    if hoy > curso.fecha_fin:
        return 100.0
    
    total_dias = (curso.fecha_fin - curso.fecha_inicio).days
    dias_transcurridos = (hoy - curso.fecha_inicio).days
    
    return (dias_transcurridos / total_dias) * 100
```

---

### 5. Sistema de Tareas Completo 📝

#### A. Vista Estudiante

**Listado** (Accordion):
```
[▼] ✅ Tarea 1: Implementar API         | 95/100 | Entregada a tiempo
[►] ⏰ Tarea 2: Database Design         | Pendiente | Vence hoy
[►] 🔴 Tarea 3: Frontend Components     | Fuera de plazo | -20 pts
```

**Detalle Modal**:
```
Tarea: Implementar API
Vencimiento: 10 Nov 2025
Estado: ✅ Entregada

Descripción:
[Task content here]

Archivos adjuntos:
[link] requirements.txt
[link] main.py

Mi Entrega (10 Nov):
[link] my_implementation.zip
[Reeditar Entrega] [Eliminar Entrega]

Retroalimentación IA:
⭐ Puntos fuertes:
- Código bien estructurado
- Comentarios claros

⚠️ Áreas de mejora:
- Agregar validación de errores

Calificación: 95/100
```

**Endpoints**:
```
GET /cursos/{curso_id}/tareas
  ?estado=pendiente|entregada|fuera_plazo
  ?ordenar=fecha_vencimiento|titulo

GET /tareas/{tarea_id}

GET /tareas/{tarea_id}/mi-entrega

POST /tareas/{tarea_id}/entregar
  {
    archivos: [archivo_ids],
    comentario?: string
  }

DELETE /tareas/{tarea_id}/entrega
```

#### B. Vista Profesor

**Crear Tarea Form**:
```
Título: [input]
Descripción: [rich editor]
Fecha vencimiento: [date picker]

---

⚙️ Configuración IA:
□ Calificar con IA
  └─ Si está marcado:
     ├─ Criterios de evaluación: [textarea]
     ├─ Rúbrica (JSON): [json editor]
     ├─ Puntos clave: [textarea]
     └─ Puntos máximos: [number]

Ejemplo:
Criterios: "Funcionalidad, Código limpio, Documentación"
Rúbrica: {
  "Funcionalidad": {"Excelente": 40, "Bueno": 30, "Regular": 20},
  "Código": {"Excelente": 35, "Bueno": 25, "Regular": 15},
  "Docs": {"Completa": 25, "Parcial": 15, "Mínima": 5}
}
Puntos clave:
- Debe tener manejo de excepciones
- API debe validar inputs
- Debe incluir al menos 3 endpoints

[Crear Tarea]
```

**Vista Entregas**:
```
Entregas: 18/20 estudiantes (90%)

Filtros: [Todas] [Entregadas] [Pendientes] [Calificadas] [Sin revisar]

┌─ Juan Pérez (juan@example.com)
│  Estado: ✅ Entregada
│  Fecha: 10 Nov, 14:30
│  Archivos: [link] submission.zip
│  Calificación: 92/100
│  [Ver Detalle] [Editar Calificación]
│
└─ María García (maria@example.com)
   Estado: 🔴 Sin entregar
   Plazo vencía: 10 Nov
   [Recordar] [Extender plazo]
```

**Panel Calificación Individual**:
```
Estudiante: Juan Pérez
Entrega: submission.zip (10 MB)

Previsualización:
[Código/Archivo embebido]

Calificación Manual:
- Funcionalidad: [5/5] ⭐⭐⭐⭐⭐
- Código limpio: [4/5] ⭐⭐⭐⭐
- Documentación: [3/5] ⭐⭐⭐

Puntuación final: 92/100

Retroalimentación:
[Rich editor]

[Generar Feedback con IA] [Guardar Calificación]
```

**Calificación Masiva con IA**:
```
[Calificar con IA - Entregas sin revisar (3)]
  └─ Selecciona criterios de arriba
  └─ [Generar Calificaciones]
     (Procesa 3 entregas, ~2-3 min)
  └─ Resultado: Modal con lista de calificaciones para revisar
     ├─ Juan Pérez: 92/100 ✅ [Aceptar] [Editar]
     ├─ María García: 78/100 ⚠️ [Aceptar] [Editar]
     └─ Pedro López: 85/100 ✅ [Aceptar] [Editar]
```

**Endpoints Profesor**:
```
POST /cursos/{curso_id}/tareas
  {
    titulo, descripcion, fecha_vencimiento,
    usar_ia_calificacion: true,
    criterios_evaluacion?: string,
    rubrica?: JSON,
    puntos_clave?: string,
    puntos_maximos: 100
  }

GET /tareas/{tarea_id}/entregas
  ?estudiante_id=?
  ?estado=entregada|pendiente|fuera_plazo
  ?ordenar=fecha_entrega

POST /tareas/{tarea_id}/entregas/{entrega_id}/calificar
  {
    puntos: 92,
    retroalimentacion: "Excelente trabajo...",
    usar_ia: false
  }

POST /tareas/{tarea_id}/calificar-lote-con-ia
  {
    entrega_ids: [id1, id2, id3],
    sobrescribir_calificaciones_existentes: false
  }

GET /tareas/{tarea_id}/estadisticas
  Response: {
    total_estudiantes: 20,
    entregadas: 18,
    pendientes: 2,
    promedio: 86.5,
    calificadas: 15,
    sin_revisar: 3
  }
```

---

### 6. Menú Contextual (3 puntos) 📋

**UI**:
```
Comment Card
├── Content
├── Attachments
├── Footer
│  ├── Reactions
│  └── [More ⋯] ← onClick
│     ├── Editar (pencil icon)
│     ├── Eliminar (trash icon, red text)
│     └── Reportar (flag icon)
```

**Endpoints**:
```
PUT /comentarios/{id}
  { contenido: string }

DELETE /comentarios/{id}

POST /comentarios/{id}/reportar
  { razon: string }
```

---

### 7. Estado Online/Offline Real 🟢

**Opción A: WebSocket + Redis** (RECOMENDADO)
```typescript
// frontend
const ws = new WebSocket('wss://api.acadify.com/ws/presencia/curso-123?token=xyz');

ws.onopen = () => {
  // Heartbeat cada 30 seg
  setInterval(() => ws.send(JSON.stringify({ type: 'heartbeat' })), 30000);
};

ws.onmessage = (event) => {
  const { usuarios_online } = JSON.parse(event.data);
  setOnlineUsers(usuarios_online);
};

// En Personas.tsx
<div className="flex items-center gap-2">
  <img src={usuario.avatar} />
  <div>
    {usuario.nombre}
    <span className={`inline-block w-2 h-2 rounded-full ${onlineUsers.includes(usuario.id) ? 'bg-green-500' : 'bg-gray-400'}`} />
  </div>
</div>
```

```python
# backend - WebSocket handler
@app.websocket("/ws/presencia/{curso_id}")
async def presencia_ws(websocket: WebSocket, curso_id: str, token: str):
    user = await get_user_from_token(token)
    await websocket.accept()
    
    # Redis: HSET curso:123:presencia juan_id timestamp
    await redis.hset(f"curso:{curso_id}:presencia", user.usuario_id, time.time())
    
    try:
        while True:
            # Espera heartbeat cada 30 seg
            data = await asyncio.wait_for(websocket.receive_text(), timeout=35)
            if data.get('type') == 'heartbeat':
                await redis.hset(f"curso:{curso_id}:presencia", user.usuario_id, time.time())
                
                # Broadcast lista online a todos
                usuarios_online = await redis.hkeys(f"curso:{curso_id}:presencia")
                await websocket.send_json({"usuarios_online": usuarios_online})
    except:
        await redis.hdel(f"curso:{curso_id}:presencia", user.usuario_id)
```

---

### 8. Calendario Mejorado 📅

**Stack**: `@fullcalendar/react` con plugins

**Tipos de eventos**:
```python
class TipoEvento(str, Enum):
    TAREA = "tarea"
    EVALUACION = "evaluacion"
    CLASE = "clase"
    EVENTO = "evento"

class EventoCurso(Base):
    evento_id: UUID
    curso_id: UUID
    titulo: str
    descripcion: str
    tipo: TipoEvento
    fecha_inicio: DateTime
    fecha_fin: DateTime | None
    color: str  # hex
    ubicacion: str | None
```

**UI**:
```
Calendar con colores:
- 📝 Rojo: Tareas
- 📅 Azul: Evaluaciones
- 🎓 Verde: Clases
- 🎉 Amarillo: Eventos

Click en día:
├─ Muestra eventos del día
├─ Botón [+ Agregar evento] (solo profesor)
└─ Modal crear con tipo, fecha, descripción
```

**Endpoints**:
```
GET /cursos/{curso_id}/eventos
  ?tipo=tarea|evaluacion|clase|evento

POST /cursos/{curso_id}/eventos
  {
    titulo, descripcion, tipo,
    fecha_inicio, fecha_fin?,
    ubicacion?
  }
  (solo profesor)

PUT /eventos/{evento_id}
PUT /eventos/{evento_id}/color
DELETE /eventos/{evento_id}
```

---

### 9. Estadísticas 📊

**Endpoint General**:
```
GET /cursos/{curso_id}/estadisticas
Response:
{
  "generales": {
    "total_estudiantes": 25,
    "estudiantes_activos": 23,
    "tasa_asistencia": 92,
    "promedio_calificaciones": 86.5,
    "tasa_entrega_tareas": 88,
    "estudiante_destacado": {
      "nombre": "Juan Pérez",
      "promedio": 98
    }
  },
  "tareas": {
    "total": 8,
    "completadas": 7,
    "pendientes": 1,
    "fuera_plazo": 0
  },
  "comentarios": {
    "total": 145,
    "por_dia": 18.125,
    "preguntas": 32,
    "anuncios": 18
  }
}
```

**Endpoint Personal (Estudiante)**:
```
GET /estadisticas/personales
Response:
{
  "tareas": {
    "entregadas": 7,
    "a_tiempo": 6,
    "fuera_plazo": 1,
    "promedio": 84.3
  },
  "siguiente_tarea": {
    "titulo": "Database Design",
    "vencimiento": "2025-11-20"
  },
  "posicion": {
    "puesto": 5,
    "total_estudiantes": 25,
    "promedio_curso": 86.5
  }
}
```

---

## 📅 Fases de Implementación

### ✅ FASE 1: Bugs Críticos (Semana 1)
- [ ] 1.1: Fix respuestas anidadas (logging + tipos)
- [ ] 1.2: Fix persistencia archivos (ya pasó test)
- [ ] 1.3: Menú contextual (3 puntos)
- [ ] 1.4: Tests E2E de flujos

**Deliverable**: Funcionalidad comentarios estable

---

### 🔴 FASE 2: Reacciones + Progreso (Semana 2)
- [ ] 2.1: Reacciones backend + frontend
- [ ] 2.2: Barra progreso UI + backend helper
- [ ] 2.3: Styling mejorado

**Deliverable**: Interactividad completa en stream

---

### 🔴 FASE 3: Tareas - MVP Estudiante (Semana 3)
- [ ] 3.1: TaskList accordion UI
- [ ] 3.2: TaskDetail modal
- [ ] 3.3: Endpoints GET/POST entregas
- [ ] 3.4: Styling + animations

**Deliverable**: Estudiantes pueden ver y entregar tareas

---

### 🔴 FASE 4: Tareas - Profesor (Semana 4)
- [ ] 4.1: TaskCreateForm con parámetros IA
- [ ] 4.2: TaskSubmissionsList + estadísticas
- [ ] 4.3: TaskGradingPanel manual
- [ ] 4.4: IA grading integration
- [ ] 4.5: Tests

**Deliverable**: Profesor puede crear, calificar, usar IA

---

### 🔴 FASE 5: Presencia + Calendario (Semana 5)
- [ ] 5.1: WebSocket presencia
- [ ] 5.2: Calendario con @fullcalendar
- [ ] 5.3: Eventos CRUD

**Deliverable**: Presencia real + calendario funcional

---

### 🔴 FASE 6: Estadísticas + Polish (Semana 6)
- [ ] 6.1: Dashboard estadísticas
- [ ] 6.2: Estadísticas personales
- [ ] 6.3: UX polish (transiciones, hover, loading)
- [ ] 6.4: Documentación completa

**Deliverable**: Sistema de cursos completo y pulido

---

## 📚 Archivos a Crear/Modificar

### Backend

```
src/
├── models/
│   ├── academic/
│   │   ├── curso.py               (ADD: fecha_inicio, fecha_fin)
│   │   ├── tarea.py               (CREATE NEW)
│   │   ├── entrega_tarea.py        (CREATE NEW)
│   │   └── reaccion.py            (CREATE NEW)
│   └── communication/
│       └── evento_curso.py         (CREATE NEW)
├── services/
│   ├── academic/
│   │   ├── curso_service.py       (ADD: calcular_progreso_curso)
│   │   ├── tarea_service.py        (CREATE NEW)
│   │   └── calificacion_ia_service.py (CREATE NEW)
│   └── communication/
│       └── reaccion_service.py    (CREATE NEW)
├── api/routes/
│   └── academic/
│       ├── tareas.py              (CREATE NEW)
│       ├── reacciones.py          (CREATE NEW)
│       └── eventos.py             (CREATE NEW)
└── schemas/
    ├── academic/
    │   ├── tarea.py               (CREATE NEW)
    │   └── entrega.py             (CREATE NEW)
    └── communication/
        └── reaccion.py            (CREATE NEW)
```

### Frontend

```
src/
├── modules/academico/
│   ├── components/
│   │   ├── CourseCard.tsx         (UPDATE: add progress bar)
│   │   ├── CourseDetail.tsx       (UPDATE: layout improvements)
│   │   ├── CourseStream.tsx       (UPDATE: nested replies, reactions)
│   │   ├── TaskList.tsx           (CREATE NEW)
│   │   ├── TaskDetail.tsx         (CREATE NEW)
│   │   ├── TaskCreate.tsx         (CREATE NEW)
│   │   ├── TaskSubmissionsList.tsx (CREATE NEW)
│   │   ├── TaskGradePanel.tsx     (CREATE NEW)
│   │   ├── ReactionBar.tsx        (CREATE NEW)
│   │   ├── ContextMenu.tsx        (CREATE NEW)
│   │   ├── Personas.tsx           (UPDATE: real online status)
│   │   ├── CalendarCurso.tsx      (CREATE NEW)
│   │   └── EstadisticasCurso.tsx  (CREATE NEW)
│   └── services/
│       ├── courseService.ts       (UPDATE: endpoints)
│       ├── taskService.ts         (CREATE NEW)
│       ├── reactionService.ts     (CREATE NEW)
│       └── presenceService.ts     (CREATE NEW)
├── types/
│   ├── curso.ts                   (UPDATE)
│   ├── tarea.ts                   (CREATE NEW)
│   ├── reaccion.ts                (CREATE NEW)
│   └── evento.ts                  (CREATE NEW)
└── hooks/
    ├── useComments.ts             (CREATE/UPDATE)
    ├── useTasks.ts                (CREATE NEW)
    ├── useReactions.ts            (CREATE NEW)
    └── usePresence.ts             (CREATE NEW)
```

---

## ✅ Checklist de Implementación

### FASE 1

- [ ] Logging agregado en `obtener_respuestas`
- [ ] Fix tipos UUID en comentario_padre_id
- [ ] Test E2E: Crear comentario → Responder → Recargar → Verifica nesting
- [ ] Menú (3 puntos) implementado
- [ ] Tests unitarios de reacciones service (mock)

### FASE 2+

- [ ] Tests pasan: 100%
- [ ] Documentación actualizada
- [ ] Funcionalidad verificada en dev + staging
- [ ] Performance aceptable (< 2s en queries)
- [ ] Responsive design (mobile + tablet + desktop)

---

## 📞 Contacto & Preguntas

Para clarificaciones sobre especificaciones:
- Revisar `.github/copilot-instructions.md`
- Revisar `.github/instructions/mcp.instructions.md`
- Memory MCP para decisiones arquitectónicas

**Last Updated**: 15 Nov 2025
