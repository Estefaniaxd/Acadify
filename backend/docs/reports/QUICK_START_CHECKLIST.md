# ✅ QUICK START CHECKLIST - VIDEOLLAMADAS

**Para empezar la implementación HOY mismo** 🚀

---

## 📦 PREPARACIÓN (30 minutos)

### 1. Instalar Dependencias Backend
```bash
cd backend

# Instalar nuevas dependencias
pip install openai==1.3.0
pip install python-jose[cryptography]==3.3.0
pip install Pillow==10.1.0
pip install moviepy==1.0.3
pip install python-multipart==0.0.6

# Verificar instalación
pip list | grep -E "openai|jose|Pillow|moviepy"
```

### 2. Instalar Dependencias Frontend
```bash
cd frontend

# Instalar dependencias (si hace falta)
npm install date-fns

# Agregar Jitsi External API al HTML
# Ya está en index.html (verificar)
```

### 3. Configurar Variables de Entorno
```bash
# Editar backend/.env
nano backend/.env
```

Agregar:
```env
# ==================== JITSI ====================
JITSI_APP_ID=acadify
JITSI_APP_SECRET=tu_secret_aqui_generar_con_openssl
JITSI_DOMAIN=meet.jit.si

# ==================== OPENAI ====================
OPENAI_API_KEY=sk-proj-tu_key_aqui

# ==================== STORAGE ====================
STORAGE_TYPE=local  # o 's3' o 'minio'
STORAGE_PATH=./storage/videollamadas

# ==================== FEATURES ====================
RECORDING_ENABLED=true
TRANSCRIPTION_ENABLED=true
RUTILIO_IN_CALLS_ENABLED=true
AUTO_DELETE_RECORDINGS_DAYS=30
```

### 4. Generar Secret para Jitsi
```bash
# Generar secret aleatorio
openssl rand -hex 32
# Copiar el output y ponerlo en JITSI_APP_SECRET
```

### 5. Crear Directorio de Storage
```bash
cd backend
mkdir -p storage/videollamadas/{videos,audios,thumbnails}
chmod 755 storage/videollamadas
```

---

## 🚀 IMPLEMENTACIÓN DÍA A DÍA

### **DÍA 1: Base de Datos (4 horas)**

#### ✅ Tarea 1: Crear Migración (2h)
```bash
# Crear nueva migración
cd backend
alembic revision -m "add videollamadas system"

# Editar archivo generado en alembic/versions/
# Copiar código de PLAN_DETALLADO_TAREAS.md Tarea 1.1

# Aplicar migración
alembic upgrade head

# Verificar tablas creadas
psql -U postgres -d acadify_db -c "\dt *videollamadas*"
```

**Resultado esperado**: 5 tablas nuevas creadas

#### ✅ Tarea 2: Crear Modelos (2h)
```bash
# Crear archivo de modelos
touch backend/src/models/communication/videollamada.py

# Editar archivo (copiar de PLAN_DETALLADO_TAREAS.md Tarea 1.2)
# Implementar clase Videollamada completa
```

**Resultado esperado**: Modelo funcional sin errores de import

---

### **DÍA 2: CRUD y Schemas (4 horas)**

#### ✅ Tarea 3: Crear Schemas Pydantic (2h)
```bash
# Crear archivo de schemas
touch backend/src/schemas/communication/videollamada_schemas.py

# Implementar:
# - VideollamadaCreate
# - VideollamadaUpdate
# - VideollamadaResponse
# - VideollamadaInDB
```

**Resultado esperado**: Schemas con validaciones funcionando

#### ✅ Tarea 4: Implementar CRUD (2h)
```bash
# Crear archivo CRUD
touch backend/src/crud/communication/videollamada.py

# Implementar clase CRUDVideollamada
# Heredar de CRUDBase
```

**Test rápido**:
```python
# En Python REPL
from src.crud.communication.videollamada import crud_videollamada
from src.db.session import SessionLocal

db = SessionLocal()
activas = crud_videollamada.get_activas(db)
print(activas)  # Debe retornar []
```

---

### **DÍA 3: JWT y API Endpoints (4 horas)**

#### ✅ Tarea 5: Generador JWT (1h)
```bash
# Crear archivo
touch backend/src/utils/jitsi_jwt.py

# Implementar función generate_jitsi_jwt()
```

**Test**:
```python
from src.utils.jitsi_jwt import generate_jitsi_jwt

token = generate_jitsi_jwt(
    room_name="test_room",
    user_id="123",
    user_name="Juan Test",
    is_moderator=True
)
print(token)  # Debe imprimir JWT válido
```

#### ✅ Tarea 6: API Endpoints (3h)
```bash
# Crear archivo de rutas
touch backend/src/api/routes/communication/videollamadas.py

# Implementar endpoints:
# - POST /videollamadas/iniciar
# - POST /videollamadas/{id}/unirse
# - POST /videollamadas/{id}/finalizar
# - GET /videollamadas/activas
```

**Test con curl**:
```bash
# Test endpoint activas
curl -X GET http://localhost:8000/api/communication/videollamadas/activas \
  -H "Authorization: Bearer YOUR_TOKEN"

# Debe retornar: []
```

---

### **DÍA 4-5: WebSocket y Service Layer (8 horas)**

#### ✅ Tarea 7: WebSocket Events (4h)
```bash
# Editar archivo existente
nano backend/src/services/websocket_manager.py

# Agregar nuevos eventos en WebSocketHandler:
# - videollamada_iniciada
# - user_joined_call
# - user_left_call
# - call_ended
```

#### ✅ Tarea 8: Service Layer (4h)
```bash
# Crear service
touch backend/src/services/videollamada_service.py

# Implementar clase VideollamadaService con:
# - iniciar_llamada()
# - unirse_a_llamada()
# - finalizar_llamada()
```

---

### **DÍA 6-8: Integración IA (12 horas)**

#### ✅ Tarea 9: Transcripción (4h)
```bash
# Crear servicio
mkdir -p backend/src/services/ia
touch backend/src/services/ia/__init__.py
touch backend/src/services/ia/transcripcion_service.py

# Implementar TranscripcionService
```

**Test con audio real**:
```bash
# Descargar audio de prueba
wget https://example.com/sample.mp3 -O test_audio.mp3

# Test en Python
from src.services.ia.transcripcion_service import transcribir_audio
texto = await transcribir_audio("test_audio.mp3")
print(texto)
```

#### ✅ Tarea 10: Rutilio en Llamadas (4h)
```bash
# Crear servicio
touch backend/src/services/ia/rutilio_videollamada_service.py

# Implementar:
# - detectar_mencion()
# - procesar_pregunta()
# - generar_respuesta()
# - text_to_speech()
```

#### ✅ Tarea 11: Resumen Automático (4h)
```bash
# Crear servicio
touch backend/src/services/ia/resumen_llamadas.py

# Implementar generar_resumen_ejecutivo()
```

---

### **DÍA 9-10: Frontend Base (8 horas)**

#### ✅ Tarea 12: Botón Videollamada (2h)
```bash
cd frontend

# Crear componente
mkdir -p src/components/communication
touch src/components/communication/VideollamadaButton.tsx

# Implementar con dropdown
```

#### ✅ Tarea 13: Modal Jitsi (3h)
```bash
# Crear componente
touch src/components/communication/JitsiMeetModal.tsx

# Implementar con Jitsi External API
```

**Test en navegador**:
1. Abrir http://localhost:5173/chat/[sala-id]
2. Click en botón videollamada
3. Debe abrir modal con Jitsi

#### ✅ Tarea 14: Hook useVideollamada (2h)
```bash
# Crear hook
mkdir -p src/hooks
touch src/hooks/useVideollamada.ts

# Implementar custom hook
```

#### ✅ Tarea 15: Integrar en ChatView (1h)
```bash
# Editar archivo existente
nano src/pages/ChatView.tsx

# Agregar:
# - <VideollamadaButton> en header
# - Estado para modal
# - WebSocket listeners
```

---

### **DÍA 11-12: Frontend IA UI (8 horas)**

#### ✅ Tarea 16: Transcripción Live (3h)
```bash
# Crear componente
touch src/components/communication/TranscripcionLive.tsx
```

#### ✅ Tarea 17: Rutilio Assistant (3h)
```bash
# Crear componente
mkdir -p src/components/ia
touch src/components/ia/RutilioAssistant.tsx
```

#### ✅ Tarea 18: Lista Participantes (2h)
```bash
# Crear componente
touch src/components/communication/ParticipantesCallList.tsx
```

---

### **DÍA 13-15: Testing (12 horas)**

#### ✅ Tests Unitarios (4h)
```bash
cd backend

# Crear archivos de tests
mkdir -p TEST/unit
touch TEST/unit/test_videollamada_model.py
touch TEST/unit/test_videollamada_crud.py
touch TEST/unit/test_videollamada_service.py

# Ejecutar tests
pytest TEST/unit/ -v --cov=src --cov-report=html
```

#### ✅ Tests Integración (4h)
```bash
# Crear archivos
mkdir -p TEST/integration
touch TEST/integration/test_videollamada_api.py
touch TEST/integration/test_videollamada_websocket.py
touch TEST/integration/test_rutilio_videollamadas.py

# Ejecutar
pytest TEST/integration/ -v
```

#### ✅ Tests E2E Frontend (2h)
```bash
cd frontend

# Crear test
mkdir -p tests/e2e
touch tests/e2e/videollamadas.spec.ts

# Ejecutar con Playwright
npm run test:e2e
```

#### ✅ Testing Manual (2h)
Ver checklist de Tarea 35 en TODO list

---

### **DÍA 16: Documentación (4 horas)**

#### ✅ Setup Guide
```bash
# Crear/actualizar documentación
cd backend/Docs
touch VIDEOLLAMADAS_SETUP.md
# Copiar de PLAN_DETALLADO_TAREAS.md Tarea 25
```

#### ✅ API Documentation
```bash
# Verificar Swagger
# Abrir http://localhost:8000/docs
# Verificar que todos los endpoints estén documentados
```

#### ✅ Reporte Final
```bash
# Crear reporte
touch backend/REPORTE_FINAL_VIDEOLLAMADAS.md
# Incluir:
# - Features completadas
# - Tests passing
# - Performance metrics
# - Known issues
```

---

## 🎯 VERIFICACIÓN FINAL

### ✅ Checklist de Funcionalidad

#### Backend
- [ ] Migraciones aplicadas sin errores
- [ ] Modelos creados y funcionando
- [ ] CRUD operations funcionan
- [ ] JWT generator funciona
- [ ] API endpoints responden correctamente
- [ ] WebSocket events se envían
- [ ] Transcripción funciona (test con audio real)
- [ ] Rutilio responde (test con @mencion)
- [ ] Resumen se genera correctamente

#### Frontend
- [ ] Botón de videollamada visible
- [ ] Modal de Jitsi se abre
- [ ] Video/audio funciona
- [ ] Participantes se listan
- [ ] Transcripción se muestra en vivo
- [ ] Rutilio widget funciona
- [ ] Notificaciones aparecen

#### Tests
- [ ] Unit tests > 85% passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Manual QA completado

#### Documentación
- [ ] Setup guide completo
- [ ] API docs actualizados
- [ ] Reporte final creado

---

## 🚨 TROUBLESHOOTING COMÚN

### Problema: Jitsi no carga
**Solución**:
```javascript
// Verificar que el script esté cargado
console.log(window.JitsiMeetExternalAPI); // No debe ser undefined

// Verificar JWT
console.log(jwtToken); // Debe ser un string largo

// Verificar room_name
console.log(roomName); // Debe ser único
```

### Problema: OpenAI API error
**Solución**:
```bash
# Verificar API key
echo $OPENAI_API_KEY

# Test rápido
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Problema: WebSocket no conecta
**Solución**:
```python
# Backend: Verificar que WebSocket esté habilitado
# main.py debe tener:
app.add_route("/ws", websocket_endpoint)

# Frontend: Verificar URL
const ws = new WebSocket('ws://localhost:8000/ws?token=...')
```

### Problema: Storage no guarda archivos
**Solución**:
```bash
# Verificar permisos
ls -la storage/videollamadas/
chmod -R 755 storage/videollamadas/

# Verificar espacio en disco
df -h
```

---

## 📞 AYUDA

### Recursos
- 📄 Plan completo: `PLAN_IMPLEMENTACION_VIDEOLLAMADAS.md`
- 📝 Tareas detalladas: `PLAN_DETALLADO_TAREAS.md`
- 📊 Resumen ejecutivo: `RESUMEN_EJECUTIVO_VIDEOLLAMADAS.md`
- 🏗️ Diagramas: `DIAGRAMAS_ARQUITECTURA.md`

### Links Útiles
- Jitsi External API: https://jitsi.github.io/handbook/docs/dev-guide/dev-guide-iframe
- OpenAI Whisper: https://platform.openai.com/docs/guides/speech-to-text
- OpenAI GPT-4: https://platform.openai.com/docs/guides/text-generation
- FastAPI WebSocket: https://fastapi.tiangolo.com/advanced/websockets/

---

## 🎉 LISTO PARA EMPEZAR

**Comando para comenzar**:
```bash
# 1. Activar entorno virtual
cd backend
source venv/bin/activate  # o venv/Scripts/activate en Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env (ver arriba)

# 4. Crear primera migración
alembic revision -m "add videollamadas system"

# 5. ¡A programar! 🚀
```

---

**¿Listo para comenzar?** 🚀  
**Próximo paso**: Marcar Tarea #2 como "in-progress" y empezar con la migración de BD.

