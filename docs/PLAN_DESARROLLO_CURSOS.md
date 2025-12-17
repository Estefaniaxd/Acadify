# 🎓 Plan de Desarrollo Completo - Módulo Cursos

> **Fecha**: 15 de noviembre de 2025  
> **Estado**: En desarrollo activo  
> **Prioridad**: CRÍTICA

---

## 📋 Resumen Ejecutivo

Desarrollo y mejora integral del módulo de **Cursos** y su **Detalle**, incluyendo:
- ✅ Corrección de bugs críticos (archivos, respuestas, reacciones)
- 🔨 Sistema completo de tareas con IA
- 🎨 Mejoras UX/UI (calendario, estadísticas, personas)
- 📊 Barra de progreso proporcional por días

---

## 🔴 FASE 1: CORRECCIONES CRÍTICAS (En Progreso)

### 1.1 ✅ Persistencia de Archivos en Comentarios
**Estado**: COMPLETADO  
**Cambios**:
- ✅ Backend: `_enriquecer_archivos_adjuntos()` implementado
- ✅ Backend: Fallback cuando metadata no existe
- ✅ Frontend: Mapeo correcto de `archivos_adjuntos`
- ✅ Tests de integración: PASSING

---

### 1.2 🔧 Respuestas a Comentarios - Persistencia Correcta
**Estado**: EN PROGRESO  
**Problema**: Al responder un comentario, aparece correctamente pero al recargar se muestra como mensaje nuevo en lugar de respuesta anidada.

**Análisis**:
```typescript
// Frontend envía correctamente:
{
  contenido: "Respuesta",
  tipo: "comentario",
  comentario_padre_id: parentPostId  // ✅ Correcto
}

// Backend persiste correctamente en Comentario:
comentario_padre_id: UUID(comentario_padre_id)  // ✅ Correcto

// Backend carga respuestas con:
ComentarioService.obtener_respuestas(db, comentario_id, usuario)  // ✅ Correcto
```

**Root Cause**: El query en `obtener_respuestas` usa `WHERE c.comentario_padre_id = :comentario_padre_id` que es correcto, PERO puede estar fallando silenciosamente y retornando array vacío.

**Solución Implementada**:
1. ✅ Agregar logging en `obtener_comentarios_curso` para ver qué respuestas se cargan
2. ✅ Agregar manejo de errores robusto en `obtener_respuestas`
3. 🔧 **PENDIENTE**: Verificar que el tipo de `comentario_padre_id` en query sea UUID string correcto

**Archivos a Modificar**:
- `backend/src/services/academic/comentario_service.py` - Líneas 430-438
- Tests: `backend/tests/services/test_comentario_service.py`

---

### 1.3 📎 Subida de Archivos - Validar Flujo Completo
**Estado**: PENDIENTE  
**Tareas**:
1. Verificar que `archivo_service` registre correctamente en `archivos_curso` al subir
2. Confirmar transacción DB commit después de upload
3. Agregar test de integración: upload → create comment → reload → verify archivo persists

---

### 1.4 😀 Sistema de Reacciones - Rediseño Completo
**Estado**: PENDIENTE - PRIORIDAD ALTA  
**Problema Actual**:
- UI horrible (botón azul a la derecha)
- No funciona la lógica
- No hay diseño estilo Discord

**Diseño Propuesto** (estilo Discord):
```
💙 Me gusta (5)  😂 Risa (3)  🎉 Celebración (1)
```

**Backend Necesario**:
```python
# Modelo Reaccion ya existe, verificar campos:
- reaccion_id (UUID)
- comentario_id (FK)
- usuario_id (FK)
- tipo_reaccion (String: emoji unicode o nombre)
- fecha_creacion

# Endpoints nuevos:
POST   /api/comentarios/{id}/reacciones  # Agregar/toggle reacción
GET    /api/comentarios/{id}/reacciones  # Listar reacciones agrupadas
DELETE /api/comentarios/{id}/reacciones/{tipo}  # Remover mi reacción

# Response format:
{
  "reacciones": {
    "❤️": { "count": 5, "usuarios": ["Juan", "María", ...], "yo_reaccione": true },
    "😂": { "count": 3, "usuarios": ["Pedro", ...], "yo_reaccione": false }
  }
}
```

**Frontend Necesario**:
```tsx
// Componente ReactionBar.tsx
<div className="flex gap-1 items-center">
  {reactions.map(r => (
    <button
      onClick={() => toggleReaction(r.emoji)}
      className={cn(
        "flex items-center gap-1 px-2 py-1 rounded-full",
        "border border-gray-300 hover:border-blue-500 transition",
        r.yo_reaccione && "bg-blue-100 border-blue-500"
      )}
    >
      <span className="text-lg">{r.emoji}</span>
      <span className="text-xs font-medium">{r.count}</span>
    </button>
  ))}
  <EmojiPicker onSelect={addReaction} />
</div>
```

**Librerías Sugeridas**:
- `emoji-picker-react` - Selector de emojis
- O usar API nativa: `<input type="text" inputMode="emoji" />`

---

## 🟡 FASE 2: SISTEMA DE TAREAS (Crítico para Funcionalidad Core)

### 2.1 📝 Vista Estudiante

**Interfaz Propuesta**:
```
┌─────────────────────────────────────────────┐
│ 📚 Tareas del Curso                         │
├─────────────────────────────────────────────┤
│                                             │
│ ▼ Tarea 1: Desarrollo de API REST          │
│   📅 Entrega: 20 Nov 2025                   │
│   ✅ Entregada | 🌟 Calificación: 4.5/5.0  │
│   [ Ver detalles ]                          │
│                                             │
│ ▼ Tarea 2: Frontend con React              │
│   📅 Entrega: 27 Nov 2025                   │
│   ⏰ Pendiente | 📅 Faltan 12 días          │
│   [ Ver detalles ] [ Entregar ]             │
│                                             │
│ ▶ Tarea 3: Testing E2E                     │
│   📅 Entrega: 4 Dic 2025                    │
│   🔴 Fuera de plazo                         │
│   [ Ver detalles ]                          │
│                                             │
└─────────────────────────────────────────────┘
```

**Vista Detalle Tarea (Modal o Página)**:
```
┌─────────────────────────────────────────────┐
│ Tarea: Desarrollo de API REST              │
├─────────────────────────────────────────────┤
│ 📋 Descripción:                             │
│ Desarrollar una API REST con FastAPI...    │
│                                             │
│ 📎 Archivos Adjuntos:                       │
│ - enunciado.pdf (1.2 MB)                    │
│ - rubrica.xlsx (45 KB)                      │
│                                             │
│ 📅 Fecha límite: 20 Nov 2025 23:59         │
│ 📊 Calificación: 4.5/5.0                    │
│                                             │
│ ─────────────────────                       │
│                                             │
│ 📤 Mi Entrega:                              │
│ - proyecto-api.zip (5.3 MB)                │
│ 💬 Comentario: "Implementé autenticación..." │
│                                             │
│ 🤖 Retroalimentación IA:                    │
│ "Excelente implementación de endpoints..."  │
│                                             │
│ [ Descargar mi entrega ]                    │
│                                             │
└─────────────────────────────────────────────┘
```

**Componentes Nuevos Necesarios**:
- `TaskList.tsx` - Lista de tareas con acordeón
- `TaskCard.tsx` - Preview colapsable de tarea
- `TaskDetail.tsx` - Vista completa de tarea
- `TaskSubmission.tsx` - Form para entregar tarea
- `TaskFeedback.tsx` - Mostrar retroalimentación IA

**Endpoints Backend**:
```python
GET    /api/cursos/{curso_id}/tareas
GET    /api/cursos/{curso_id}/tareas/{tarea_id}
POST   /api/cursos/{curso_id}/tareas/{tarea_id}/entregar
GET    /api/cursos/{curso_id}/tareas/{tarea_id}/mi-entrega
```

---

### 2.2 👨‍🏫 Vista Profesor

**Interfaz Creación de Tarea**:
```
┌─────────────────────────────────────────────┐
│ ➕ Crear Nueva Tarea                        │
├─────────────────────────────────────────────┤
│                                             │
│ Título*                                     │
│ [________________________]                  │
│                                             │
│ Descripción*                                │
│ [___________________________________]       │
│ |                                   |       │
│ |___________________________________|       │
│                                             │
│ 📅 Fecha de Asignación*                     │
│ [15/11/2025 10:00]                          │
│                                             │
│ 📅 Fecha Límite*                            │
│ [22/11/2025 23:59]                          │
│                                             │
│ 📎 Archivos Adjuntos                        │
│ [ Subir archivos ]                          │
│                                             │
│ ─── Parámetros para IA ───                  │
│                                             │
│ 🤖 Calificación Automática                  │
│ ☐ Usar IA para calificar                   │
│                                             │
│ 📋 Criterios de Evaluación:                 │
│ [___________________________________]       │
│ Ejemplo: "Funcionalidad completa,          │
│ código limpio, documentación..."           │
│                                             │
│ 🎯 Puntos Clave a Evaluar:                  │
│ [___________________________________]       │
│ Ejemplo: "Uso correcto de FastAPI,         │
│ validación con Pydantic..."                │
│                                             │
│ ⚖️ Rubrica (JSON):                          │
│ {                                           │
│   "funcionalidad": 40,                      │
│   "calidad_codigo": 30,                     │
│   "documentacion": 20,                      │
│   "pruebas": 10                             │
│ }                                           │
│                                             │
│ [ Cancelar ]  [ Guardar ] [ Crear y Asignar]│
│                                             │
└─────────────────────────────────────────────┘
```

**Vista Lista de Entregas**:
```
┌─────────────────────────────────────────────┐
│ Tarea: Desarrollo de API REST              │
│ 📊 Entregas: 15/20 (75%)                    │
├─────────────────────────────────────────────┤
│                                             │
│ ✅ Entregadas a tiempo: 12                  │
│ ⏰ Entregadas tarde: 3                      │
│ 🔴 Sin entregar: 5                          │
│                                             │
│ [ 📋 Ver todas ] [ 🤖 Calificar con IA ]   │
│                                             │
│ ─── Entregas Recientes ───                  │
│                                             │
│ 👤 Juan Pérez                               │
│    ✅ A tiempo • 📅 18/11/2025             │
│    📊 Sin calificar                         │
│    [ Calificar ] [ Ver entrega ]           │
│                                             │
│ 👤 María García                             │
│    ✅ A tiempo • 📅 19/11/2025             │
│    ⭐ 4.5/5.0                               │
│    [ Ver calificación ]                     │
│                                             │
│ ...                                         │
│                                             │
└─────────────────────────────────────────────┘
```

**Componentes Nuevos**:
- `TaskCreateForm.tsx` - Formulario creación tarea
- `TaskSubmissionsList.tsx` - Lista de entregas
- `TaskGradingPanel.tsx` - Panel para calificar
- `AIGradingButton.tsx` - Botón + modal calificación IA
- `TaskStatistics.tsx` - Estadísticas de entregas

**Endpoints Backend**:
```python
# Gestión de tareas
POST   /api/cursos/{curso_id}/tareas
PUT    /api/cursos/{curso_id}/tareas/{tarea_id}
DELETE /api/cursos/{curso_id}/tareas/{tarea_id}

# Entregas
GET    /api/cursos/{curso_id}/tareas/{tarea_id}/entregas
GET    /api/cursos/{curso_id}/tareas/{tarea_id}/entregas/{estudiante_id}
PUT    /api/cursos/{curso_id}/tareas/{tarea_id}/entregas/{estudiante_id}/calificar

# Calificación IA
POST   /api/cursos/{curso_id}/tareas/{tarea_id}/calificar-con-ia
POST   /api/cursos/{curso_id}/tareas/{tarea_id}/entregas/{estudiante_id}/retroalimentacion-ia

# Estadísticas
GET    /api/cursos/{curso_id}/tareas/estadisticas
GET    /api/cursos/{curso_id}/tareas/{tarea_id}/estadisticas
```

**Schema Tarea con IA**:
```python
class TareaCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=200)
    descripcion: str
    fecha_asignacion: datetime
    fecha_limite: datetime
    archivos_adjuntos: list[str] = []  # IDs de archivos
    
    # Parámetros para IA
    usar_calificacion_ia: bool = False
    criterios_evaluacion: str | None = None  # Texto libre
    puntos_clave: str | None = None  # JSON o texto
    rubrica: dict[str, int] | None = None  # {"categoria": peso}
    
    # Validaciones adicionales
    valor_max_calificacion: float = 5.0
    permite_entregas_tarde: bool = True
    descuento_entrega_tarde: float = 0.1  # 10% descuento

class TareaCalificarIA(BaseModel):
    entrega_id: str
    archivo_entrega_id: str
    prompt_adicional: str | None = None

class TareaRetroalimentacionIA(BaseModel):
    entrega_id: str
    incluir_sugerencias: bool = True
    nivel_detalle: str = "medio"  # bajo, medio, alto
```

---

## 🟢 FASE 3: MEJORAS UX/UI

### 3.1 📊 Barra de Progreso del Curso

**Cálculo**:
```python
def calcular_progreso_curso(curso: Curso) -> float:
    """Calcula progreso como % de días transcurridos."""
    hoy = datetime.now(UTC).date()
    
    fecha_inicio = curso.fecha_inicio.date()
    fecha_fin = curso.fecha_fin.date()
    
    if hoy < fecha_inicio:
        return 0.0
    elif hoy > fecha_fin:
        return 100.0
    
    dias_totales = (fecha_fin - fecha_inicio).days
    dias_transcurridos = (hoy - fecha_inicio).days
    
    if dias_totales == 0:
        return 100.0
    
    progreso = (dias_transcurridos / dias_totales) * 100
    return round(min(progreso, 100.0), 1)
```

**UI en CourseCard**:
```tsx
<div className="mt-4">
  <div className="flex justify-between text-sm mb-1">
    <span className="text-gray-600">Progreso del curso</span>
    <span className="font-semibold">{progreso}%</span>
  </div>
  <div className="w-full bg-gray-200 rounded-full h-2">
    <div
      className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all"
      style={{ width: `${progreso}%` }}
    />
  </div>
  <div className="flex justify-between text-xs text-gray-500 mt-1">
    <span>{formatDate(fecha_inicio)}</span>
    <span>{formatDate(fecha_fin)}</span>
  </div>
</div>
```

---

### 3.2 ⚙️ Menú Contextual en Comentarios

**UI**:
```tsx
<div className="relative">
  <button
    onClick={() => setShowMenu(!showMenu)}
    className="p-1 hover:bg-gray-100 rounded"
  >
    <MoreVertical className="w-4 h-4" />
  </button>
  
  {showMenu && (
    <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border z-10">
      <button className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2">
        <Edit2 className="w-4 h-4" />
        Editar
      </button>
      <button className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2">
        <Trash2 className="w-4 h-4 text-red-500" />
        <span className="text-red-500">Eliminar</span>
      </button>
      <button className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2">
        <Flag className="w-4 h-4" />
        Reportar
      </button>
    </div>
  )}
</div>
```

**Backend ya existe**:
- `PUT /api/comentarios/{id}` - Actualizar
- `DELETE /api/comentarios/{id}` - Eliminar (soft delete)
- Pendiente: `POST /api/comentarios/{id}/reportar` - Reportar

---

### 3.3 👥 Personas - Estado Online/Offline Real

**Opciones de Implementación**:

**Opción A: WebSocket (Recomendado)**
```python
# Backend: WebSocket para presencia
@router.websocket("/ws/presencia/{curso_id}")
async def websocket_presencia(websocket: WebSocket, curso_id: str):
    await websocket.accept()
    usuario_id = await authenticate_websocket(websocket)
    
    # Registrar conexión
    await redis.hset(f"presencia:{curso_id}", usuario_id, datetime.now().isoformat())
    
    try:
        while True:
            # Heartbeat cada 30s
            await asyncio.sleep(30)
            await redis.hset(f"presencia:{curso_id}", usuario_id, datetime.now().isoformat())
    except WebSocketDisconnect:
        await redis.hdel(f"presencia:{curso_id}", usuario_id)

# GET /api/cursos/{curso_id}/presencia
async def obtener_presencia(curso_id: str):
    presencia = await redis.hgetall(f"presencia:{curso_id}")
    ahora = datetime.now()
    
    usuarios_online = []
    for usuario_id, ultimo_ping in presencia.items():
        ultimo = datetime.fromisoformat(ultimo_ping)
        if (ahora - ultimo).seconds < 60:  # Online si < 1 min
            usuarios_online.append(usuario_id)
    
    return usuarios_online
```

**Opción B: Polling de Última Actividad**
```python
# Actualizar última actividad en cada request (middleware)
@app.middleware("http")
async def update_last_activity(request: Request, call_next):
    response = await call_next(request)
    
    if hasattr(request.state, "user"):
        await redis.set(
            f"last_activity:{request.state.user.usuario_id}",
            datetime.now().isoformat(),
            ex=300  # Expire en 5 min
        )
    
    return response

# Endpoint para verificar estado
GET /api/usuarios/{user_id}/estado
{
  "online": true,
  "ultima_actividad": "2025-11-15T10:30:00"
}
```

---

### 3.4 📅 Calendario Mejorado

**Librerías Recomendadas**:
- `react-big-calendar` - Calendario completo con vistas mensual/semanal/diaria
- O `@fullcalendar/react` - FullCalendar con muchas features

**Eventos a Mostrar**:
- 📝 Tareas (fecha límite)
- 📅 Evaluaciones
- 🎓 Clases programadas
- 🎉 Eventos especiales del curso

**UI Propuesta**:
```tsx
<Calendar
  localizer={localizer}
  events={events}
  startAccessor="start"
  endAccessor="end"
  style={{ height: 600 }}
  onSelectEvent={handleEventClick}
  onSelectSlot={handleNewEvent}  // Profesor puede crear
  eventPropGetter={(event) => ({
    style: {
      backgroundColor: getEventColor(event.type),
      borderRadius: '4px',
      border: 'none'
    }
  })}
  views={['month', 'week', 'day', 'agenda']}
/>
```

**Backend**:
```python
# Modelo Evento
class EventoCurso(Base):
    evento_id: UUID
    curso_id: UUID
    tipo: EventoTipo  # tarea, evaluacion, clase, evento
    titulo: str
    descripcion: str
    fecha_inicio: datetime
    fecha_fin: datetime
    created_by: UUID  # Profesor
    
# Endpoints
GET  /api/cursos/{curso_id}/eventos
POST /api/cursos/{curso_id}/eventos  # Solo profesor
PUT  /api/cursos/{curso_id}/eventos/{evento_id}
DELETE /api/cursos/{curso_id}/eventos/{evento_id}
```

---

### 3.5 📈 Estadísticas del Curso

**Estadísticas Generales (Visible para todos)**:
```
┌─────────────────────────────────────────────┐
│ 📊 Estadísticas del Curso                   │
├─────────────────────────────────────────────┤
│                                             │
│ 👥 Estudiantes Inscritos: 24               │
│ 📝 Tareas Asignadas: 8                     │
│ ✅ Tasa de Entrega: 87%                     │
│ 📊 Promedio General: 4.2/5.0               │
│ 🏆 Estudiante Destacado: María García      │
│                                             │
│ ─── Actividad Reciente ───                  │
│ 📈 Entregas última semana: 15               │
│ 💬 Comentarios nuevos: 23                   │
│ 📎 Archivos subidos: 42                     │
│                                             │
└─────────────────────────────────────────────┘
```

**Estadísticas Personales (Estudiante)**:
```
┌─────────────────────────────────────────────┐
│ 📊 Mi Progreso                               │
├─────────────────────────────────────────────┤
│                                             │
│ 📝 Tareas Entregadas: 7/8 (87.5%)          │
│ ⏰ Entregas a Tiempo: 6/7 (85.7%)          │
│ 📊 Mi Promedio: 4.5/5.0                     │
│ 🎯 Posición: 3° de 24                       │
│                                             │
│ ─── Calificaciones ───                      │
│ Tarea 1: ⭐⭐⭐⭐⭐ (5.0)                   │
│ Tarea 2: ⭐⭐⭐⭐☆ (4.0)                     │
│ Tarea 3: ⭐⭐⭐⭐⭐ (4.8)                   │
│ ...                                         │
│                                             │
│ ─── Próximas Entregas ───                   │
│ 📅 Tarea 8: Faltan 5 días                   │
│                                             │
└─────────────────────────────────────────────┘
```

**Backend**:
```python
GET /api/cursos/{curso_id}/estadisticas
{
  "generales": {
    "total_estudiantes": 24,
    "total_tareas": 8,
    "tasa_entrega": 0.87,
    "promedio_general": 4.2,
    "estudiante_destacado": {...}
  },
  "actividad_reciente": {
    "entregas_semana": 15,
    "comentarios_nuevos": 23,
    "archivos_subidos": 42
  }
}

GET /api/cursos/{curso_id}/estadisticas/personales
{
  "tareas_entregadas": 7,
  "tareas_totales": 8,
  "entregas_a_tiempo": 6,
  "promedio": 4.5,
  "posicion": 3,
  "calificaciones": [...],
  "proximas_entregas": [...]
}
```

---

## 🎯 Plan de Ejecución

### Semana 1 (18-22 Nov)
- [x] ✅ Persistencia archivos (COMPLETADO)
- [ ] 🔧 Fix respuestas comentarios
- [ ] 😀 Sistema reacciones básico
- [ ] 📊 Barra progreso curso

### Semana 2 (25-29 Nov)
- [ ] 📝 Sistema tareas - Vista estudiante (MVP)
- [ ] ⚙️ Menú contextual comentarios
- [ ] 📎 Tests integración archivos

### Semana 3 (2-6 Dic)
- [ ] 👨‍🏫 Sistema tareas - Vista profesor
- [ ] 🤖 Integración IA para calificación
- [ ] 📈 Estadísticas básicas

### Semana 4 (9-13 Dic)
- [ ] 👥 Estado online/offline real
- [ ] 📅 Calendario mejorado
- [ ] 🎨 Polish UI/UX general

---

## 📚 Documentación de Referencia

### Archivos Clave Backend
- `backend/src/models/academic/tarea.py` - Modelo Tarea
- `backend/src/services/academic/tarea_service.py` - Lógica tareas
- `backend/src/services/ai/calificacion_service.py` - IA calificación
- `backend/src/api/routes/academic/curso_tareas.py` - Endpoints tareas

### Archivos Clave Frontend
- `frontend/src/modules/academico/CourseDetail.tsx` - Vista detalle curso
- `frontend/src/modules/academico/components/TaskList.tsx` - **CREAR**
- `frontend/src/modules/academico/services/taskService.ts` - **CREAR**

### APIs Externas
- OpenAI GPT-4 - Calificación automática
- OpenAI Whisper - Transcripción (si audio)

---

## 🚀 Próximos Pasos Inmediatos

1. **Ejecutar tests actuales**:
   ```bash
   cd backend
   pytest tests/services/test_comentario_service.py -v
   pytest tests/api/test_academic_api.py::TestCursosAPI::test_create_comment_with_attachment_and_get -v
   ```

2. **Fix respuestas comentarios**:
   - Agregar logging detallado
   - Verificar tipo UUID en queries
   - Ejecutar test de integración

3. **Iniciar sistema reacciones**:
   - Diseñar UI en Figma/sketch
   - Implementar endpoints backend
   - Crear componente ReactionBar

4. **Documentar decisiones arquitectónicas**:
   - Usar Memory MCP para guardar decisiones
   - Documentar en `.copilot/decisions/`

---

**✅ Este documento será actualizado conforme avancemos en cada fase.**
