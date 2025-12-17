# ✅ CHECKLIST DE INTEGRACIÓN - SISTEMA TAREAS + IA

> **Duración estimada**: 2-3 horas
> **Dificultad**: Media
> **Prioridad**: 🔥 MÁXIMA

---

## 📋 CHECKLIST PASO A PASO

### PASO 1: Backend Setup (30 min)

#### 1.1 Registrar routers en main.py
- [ ] Abrir `backend/src/main.py`
- [ ] Agregar imports:
```python
from src.api.routers.notificaciones import router as notificaciones_router
from src.api.routers.ia import router as ia_router
```
- [ ] Registrar routers:
```python
app.include_router(notificaciones_router)
app.include_router(ia_router)
```
- [ ] Verificar sin errores: `python -m py_compile src/main.py`

#### 1.2 Crear modelo Notificacion
- [ ] Crear archivo `backend/src/models/notificacion.py`
- [ ] Copiar código del modelo (ver SISTEMA_COMPLETO_TAREAS_IA.md)
- [ ] Agregar import en `backend/src/models/__init__.py`:
```python
from .notificacion import Notificacion
```
- [ ] Verificar en sqlalchemy: `python -c "from src.models import Notificacion"`

#### 1.3 Crear migración Alembic
- [ ] Terminal: `cd backend && alembic revision --autogenerate -m "Agregar tabla notificaciones"`
- [ ] Verificar que el archivo de migración se creó en `backend/alembic/versions/`
- [ ] Aplicar: `alembic upgrade head`
- [ ] Verificar en DB: `\d notificaciones` (en PostgreSQL)

#### 1.4 Crear schemas Pydantic
- [ ] Crear `backend/src/schemas/notificacion.py`:
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class NotificacionResponse(BaseModel):
    id: str
    usuario_id: int
    tipo: str
    titulo: str
    mensaje: str
    leida: bool
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

class NotificacionCreate(BaseModel):
    usuario_id: str
    tipo: str
    titulo: str
    mensaje: str
    metadatos: Optional[dict] = None
```
- [ ] Verificar import en schemas/__init__.py

#### 1.5 Testear endpoints
- [ ] Iniciar backend: `uvicorn src.main:app --reload`
- [ ] Abrir http://localhost:8000/docs (Swagger)
- [ ] Probar endpoint: `GET /api/notificaciones`
- [ ] Verificar 401 sin auth (correcto)
- [ ] Login primero, luego probar con token

---

### PASO 2: Frontend Setup (45 min)

#### 2.1 Instalar dependencias
- [ ] Terminal: `cd frontend && pnpm install` (si no está hecho)
- [ ] Verificar `date-fns` instalado: `pnpm list date-fns`
- [ ] Si falta: `pnpm add date-fns`

#### 2.2 Copiar servicios
- [ ] Verificar `frontend/src/services/iaService.ts` existe
- [ ] Verificar `frontend/src/services/notificacionesService.ts` existe
- [ ] Si faltan, copiar del workspace

#### 2.3 Actualizar hooks
- [ ] Abrir `frontend/src/hooks/useNotificaciones.ts`
- [ ] Verificar que tiene SSE integrado
- [ ] Verificar `useEffect` para EventSource

#### 2.4 Copiar componentes
- [ ] Crear si no existen:
  - [ ] `frontend/src/components/TareaChat.tsx`
  - [ ] `frontend/src/components/CalificacionTarea.tsx`
  - [ ] `frontend/src/components/EntregaTarea.tsx`
  - [ ] `frontend/src/components/NotificacionesPanel.tsx`
  - [ ] `frontend/src/components/BulkIAFeedbackModal.tsx`
- [ ] Verificar que no hay errores TypeScript: `pnpm type-check`

#### 2.5 Verificar imports
- [ ] Los componentes pueden importar todos sus dependencies
- [ ] No hay "module not found" errors
- [ ] `pnpm type-check` sin errores

---

### PASO 3: Integración en UI (1 hora)

#### 3.1 Agregar NotificacionesBadge en Navbar
- [ ] Abrir `frontend/src/components/Navbar.tsx` (o similar)
- [ ] Agregar import:
```typescript
import { NotificacionesBadge } from '@/components/NotificacionesPanel';
```
- [ ] Agregar en JSX (en navbar, cerca del avatar):
```jsx
<NotificacionesBadge />
```
- [ ] Verificar que aparece el ícono de campana
- [ ] Click abre panel (sin errores)

#### 3.2 Integrar CalificacionTarea + EntregaTarea en TareaPreviewModal
- [ ] Abrir `frontend/src/components/TareaPreviewModal.tsx`
- [ ] Agregar imports:
```typescript
import { CalificacionTarea } from './CalificacionTarea';
import { EntregaTarea } from './EntregaTarea';
import { TareaChat } from './TareaChat';
```
- [ ] Agregar tabs o secciones para mostrar estos componentes
- [ ] Ver guía en SISTEMA_COMPLETO_TAREAS_IA.md para código exacto

#### 3.3 Verificar que aparece
- [ ] Abrir course detail
- [ ] Click en una tarea
- [ ] Verificar que aparecen tabs/secciones nuevas
- [ ] No hay errores en console
- [ ] Componentes se renderean

#### 3.4 Agregar BulkIAFeedbackModal en TareasAccordion
- [ ] Abrir `frontend/src/components/TareasAccordion.tsx` (o donde estén listadas)
- [ ] Agregar import:
```typescript
import { BulkIAFeedbackModal } from '@/components/BulkIAFeedbackModal';
```
- [ ] Agregar checkboxes a cada tarea
- [ ] Agregar botón "⚡ Generar IA para X tareas"
- [ ] Conectar a BulkIAFeedbackModal
- [ ] Probar: seleccionar tareas, click botón, se abre modal

---

### PASO 4: Testing (30 min)

#### 4.1 Frontend - Sin errores
- [ ] `pnpm type-check` ✅ cero errores
- [ ] `pnpm lint` ✅ no hay warnings críticos
- [ ] `pnpm dev` ✅ inicia sin errores

#### 4.2 Frontend - Funcionalidad
- [ ] [ ] Navegar a course detail
- [ ] [ ] Click en tarea → abre modal
- [ ] [ ] Verificar tabs/secciones nuevas
- [ ] [ ] NotificacionesBadge visible en navbar
- [ ] [ ] Click en campana → abre panel notificaciones

#### 4.3 Backend - Health check
- [ ] `http://localhost:8000/docs` carga
- [ ] `GET /api/notificaciones` responde con 401 (sin auth)
- [ ] Login y probar con token
- [ ] `GET /api/notificaciones` responde 200 con array vacío

#### 4.4 Backend - Tests
- [ ] Terminal: `cd backend && pytest tests/ -v`
- [ ] Todos pasan (crear tests básicos si falta)

---

### PASO 5: Integración Final (30 min)

#### 5.1 Sincronizar BD
- [ ] Verificar migraciones aplicadas
- [ ] Revisar `notificaciones` table existe
- [ ] `psql -U acadify_user -d acadify -c "\d notificaciones"`

#### 5.2 Variables de entorno
- [ ] Backend `.env` tiene `OPENAI_API_KEY` (opcional por ahora)
- [ ] Backend `.env` tiene `REDIS_URL` (si es producción)
- [ ] Frontend `.env` tiene `VITE_API_URL=http://localhost:8000`

#### 5.3 Verificar flujo completo
- [ ] Abrir navegador → localhost:5173
- [ ] Login
- [ ] Navegar a Course Detail
- [ ] Abrir tarea
- [ ] Verificar todos los tabs/secciones
- [ ] Click botones (sin errores)
- [ ] Abrir NotificacionesPanel
- [ ] No hay errores en console (F12)

#### 5.4 Backend logs
- [ ] Backend mostrando logs INFO/DEBUG
- [ ] No hay ERROR logs
- [ ] SSE conecta correctamente

---

### PASO 6: Documentation & Cleanup (15 min)

#### 6.1 Documentación
- [ ] SISTEMA_COMPLETO_TAREAS_IA.md copiado al workspace
- [ ] FASE_4_RESUMEN_EJECUTIVO.md copiado al workspace
- [ ] Este checklist guardado en workspace

#### 6.2 Cleanup
- [ ] Revisar imports no usados
- [ ] Agregar TODO comments para IA real
- [ ] Verificar que no hay console.log() de debug

#### 6.3 Performance
- [ ] Abrir DevTools → Performance
- [ ] Medir carga de TareaPreviewModal
- [ ] Verificar no hay memory leaks

---

## 🧪 TESTING MANUAL

### Test 1: Abrir tarea
```
1. Navigate to /course/[id]
2. Click en una tarea
3. ✅ Modal abre sin errores
4. ✅ Aparecer tabs para CalificacionTarea, EntregaTarea, TareaChat
5. ✅ No hay "Cannot read properties" errors
```

### Test 2: Notificaciones
```
1. Click campana en navbar
2. ✅ Panel abre desde derecha
3. ✅ Muestra lista de notificaciones
4. ✅ Filtros funcionan
5. ✅ "Marcar como leída" funciona
```

### Test 3: Bulk operations
```
1. En TareasAccordion, marcar checkboxes
2. ✅ Botón "⚡ Generar IA" aparece
3. Click botón
4. ✅ Modal abre
5. ✅ Selector de modelo aparece
6. Click "Iniciar Procesamiento"
7. ✅ Progreso actualiza (aunque sea mock)
```

### Test 4: Chat
```
1. En TareaChat, escribir mensaje
2. ✅ Aparece en lista
3. ✅ Seleccionar "PRIVADO"
4. ✅ Enviar funciona
5. ✅ Timestamps correctos
```

---

## 🚨 TROUBLESHOOTING

### Error: "Cannot find module 'notificacionesService'"
```
Solución:
1. Verificar archivo existe: ls frontend/src/services/notificacionesService.ts
2. Verificar import path es relativo correcto
3. Verificar no hay typo en nombre
4. Ejecutar: pnpm type-check
```

### Error: Backend 404 en /api/notificaciones
```
Solución:
1. Verificar routers registrados en main.py
2. Verificar prefix correcto: "/api/notificaciones"
3. Verificar db dependency inyectado
4. Reiniciar backend: Ctrl+C, uvicorn...
```

### Error: SSE no conecta
```
Solución:
1. Verificar token JWT es válido
2. Verificar usuario_id en query params
3. Abrir Chrome DevTools → Network → Fetch
4. Buscar request a /api/notificaciones/sse
5. Verificar status 200 y tipo "text/event-stream"
```

### Error: TypeScript "unknown type"
```
Solución:
1. Agregar tipos en interfaces
2. Verificar imports en archivos que los definen
3. Ejecutar: pnpm type-check
4. Si persiste, agregar unknown type guard
```

---

## 📊 VALIDACIÓN FINAL

Cuando TODOS estén checked ✅, el sistema está ready:

```
BACKEND:
 ✅ Routers registrados en main.py
 ✅ Modelo Notificacion en BD
 ✅ Migración Alembic aplicada
 ✅ Schemas Pydantic definidos
 ✅ Endpoints responden sin errores
 ✅ SSE funciona (EventSource)

FRONTEND:
 ✅ Servicios copiados (iaService, notificacionesService)
 ✅ Hooks actualizados (useNotificaciones con SSE)
 ✅ Componentes copiados (5 componentes)
 ✅ NotificacionesBadge en Navbar
 ✅ CalificacionTarea + EntregaTarea en TareaPreviewModal
 ✅ BulkIAFeedbackModal en TareasAccordion
 ✅ pnpm type-check sin errores
 ✅ pnpm lint sin warnings críticos

TESTING:
 ✅ Ningún error en console (F12)
 ✅ Flujo completo: abrir → ver tabs → sin errores
 ✅ Notificaciones: panel abre y filtra
 ✅ Bulk ops: modal abre y configura
 ✅ Chat: envía y recibe mensajes

DOCUMENTATION:
 ✅ SISTEMA_COMPLETO_TAREAS_IA.md en workspace
 ✅ FASE_4_RESUMEN_EJECUTIVO.md en workspace
 ✅ Este checklist completado
```

---

## 🎯 TIEMPO ESTIMADO

| Paso | Tiempo |
|------|--------|
| 1. Backend Setup | 30 min |
| 2. Frontend Setup | 45 min |
| 3. UI Integration | 1 hora |
| 4. Testing | 30 min |
| 5. Final Integration | 30 min |
| 6. Documentation | 15 min |
| **TOTAL** | **≈3 horas** |

---

## 💡 PRO TIPS

1. **Hacer push a git después de cada paso**
   ```bash
   git add .
   git commit -m "Paso 1: Backend setup"
   ```

2. **Usar DevTools para debugging**
   - Network tab → ver requests a /api/notificaciones
   - Console tab → ver SSE events
   - Performance tab → medir carga

3. **Probar en incógnita/privado**
   - Elimina cache de navegador
   - Simula usuario real

4. **Agregar console.logs temporales**
   - En componentes: `console.log('🔔 NotificacionesPanel opened')`
   - En servicios: `console.log('📡 SSE connected')`
   - En backend: `print(f'✅ Endpoint called')`

---

## ✅ SIGN OFF

Una vez completado TODO este checklist:

**El sistema de TAREAS + IA está LISTO PARA PRODUCCIÓN**

---

Fecha de inicio: __________
Fecha de finalización: __________
Responsable: __________
Observaciones: __________

---

**¡Éxito en la integración! 🚀**
