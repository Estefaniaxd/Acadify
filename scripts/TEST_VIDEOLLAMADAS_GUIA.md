# 🧪 Guía de Testing - Sistema de Videollamadas

## ✅ Instalación Completada

### Estado de la Configuración
- [x] **Jitsi External API**: Script agregado a `index.html`
- [x] **Dependencias**: date-fns y lucide-react instaladas
- [x] **React Query**: Configurado en `main.tsx`
- [x] **Ruta**: `/videollamadas` agregada a `App.tsx`
- [x] **Variables de entorno**: `.env` configurado
- [x] **Contexto Auth**: Integrado en `VideollamadasPage`

---

## 🚀 Pasos para Probar el Sistema

### 1️⃣ Iniciar el Backend

```bash
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Verificar que esté corriendo:**
- Abrir en navegador: http://localhost:8000/docs
- Debería mostrar la documentación de Swagger UI
- Verificar que aparezcan los endpoints `/api/communication/videollamadas/*`

### 2️⃣ Iniciar el Frontend

**En otra terminal:**

```bash
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/frontend
npm run dev
```

**Verificar que esté corriendo:**
- Debería mostrar: `Local: http://localhost:5173/`
- Abrir en navegador: http://localhost:5173

### 3️⃣ Autenticarse en el Sistema

1. Ir a: http://localhost:5173/login
2. Iniciar sesión con credenciales de prueba:
   - **Usuario**: (usar uno existente en tu BD)
   - **Contraseña**: (la contraseña correspondiente)

3. **Verificar que el token se guardó:**
   - Abrir DevTools (F12)
   - Ir a **Application → Local Storage**
   - Buscar: `access_token` y `refresh_token`
   - Debería haber tokens JWT

---

## 🎬 Escenarios de Prueba

### ✅ Test 1: Cargar Página de Videollamadas

**Pasos:**
1. Una vez autenticado, ir a: http://localhost:5173/videollamadas
2. Debería cargar la página sin errores

**Resultado Esperado:**
- ✅ Título "📹 Videollamadas"
- ✅ Descripción "Crea y únete a videollamadas con Jitsi Meet"
- ✅ Lista de videollamadas (puede estar vacía)
- ✅ Botón "+ Crear Videollamada" o similar
- ✅ Panel de información con instrucciones

**Verificar en Console (F12):**
- No debería haber errores rojos
- Puede haber logs de React Query

---

### ✅ Test 2: Crear Nueva Videollamada

**Pasos:**
1. Hacer clic en botón para crear videollamada
2. Debería aparecer un formulario o selector de tipo:
   - **Opción Video** 📹
   - **Opción Audio** 🎙️
3. Seleccionar tipo (ej: Video)
4. La videollamada debería crearse automáticamente

**Resultado Esperado:**
- ✅ Se crea la videollamada en el backend
- ✅ Aparece en la lista con estado "ACTIVA"
- ✅ Muestra:
  - Room name (nombre de sala)
  - Tipo (VIDEO o VOZ)
  - Badge verde "Activa"
  - 0 participantes
  - Botón "Unirse"

**Verificar en Backend:**
```bash
# En otra terminal, consultar la API:
curl http://localhost:8000/api/communication/videollamadas/ \
  -H "Authorization: Bearer <TU_TOKEN_AQUI>"
```

Debería devolver un JSON con la videollamada creada.

---

### ✅ Test 3: Unirse a Videollamada

**Pasos:**
1. Hacer clic en botón "Unirse" de una videollamada ACTIVA
2. Debería aparecer la ventana de Jitsi Meet

**Resultado Esperado:**
- ✅ Ventana completa con Jitsi Meet embebido
- ✅ Header con:
  - Nombre de sala
  - Contador de duración (00:00)
  - Indicador de calidad de conexión (color verde/amarillo/rojo)
  - Badge "Moderador" (si es el creador)
- ✅ Área principal: Jitsi Meet cargando
- ✅ Sidebar: Panel de participantes (1 participante: tú)
- ✅ Footer: Indicadores de audio/video
- ✅ Botón "Salir"

**Verificar en Jitsi:**
- Debe pedir permisos de cámara/micrófono
- Debe mostrar tu video (si aceptas permisos)
- Debe aparecer tu nombre de usuario
- Controles de Jitsi deben funcionar:
  - Mute/unmute micrófono
  - Activar/desactivar video
  - Pantalla compartida
  - Chat
  - Levantar mano

---

### ✅ Test 4: Múltiples Participantes

**Pasos:**
1. Con una videollamada activa, abrir **segunda pestaña del navegador**
2. Ir a: http://localhost:5173/videollamadas
3. Unirse a la **misma videollamada**

**Resultado Esperado:**
- ✅ En pestaña 1: Panel de participantes muestra 2 usuarios
- ✅ En pestaña 2: Panel de participantes muestra 2 usuarios
- ✅ Ambos usuarios se ven y escuchan (si hay permisos)
- ✅ Cambios en audio/video se reflejan en ambas ventanas

**Verificar Backend:**
```bash
# Obtener participantes activos:
curl http://localhost:8000/api/communication/videollamadas/<ID>/participantes/activos \
  -H "Authorization: Bearer <TU_TOKEN_AQUI>"
```

Debería devolver 2 participantes.

---

### ✅ Test 5: Monitoreo de Calidad de Conexión

**Pasos:**
1. Mientras estás en videollamada, observar el indicador de calidad
2. Simular cambios de red:
   - Abrir DevTools (F12) → Network tab
   - Cambiar throttling: "Fast 3G" o "Slow 3G"

**Resultado Esperado:**
- ✅ Indicador de calidad cambia de color:
  - **Verde**: Excelente
  - **Amarillo**: Buena/Regular
  - **Rojo**: Mala
- ✅ Tooltip muestra el estado al hacer hover

**Verificar Backend:**
- Se reporta la calidad cada 5 segundos
- Se puede consultar en tabla `participantes`:
```sql
SELECT id, usuario_id, calidad_conexion FROM participantes 
WHERE videollamada_id = '<ID>';
```

---

### ✅ Test 6: Salir de Videollamada

**Pasos:**
1. Hacer clic en botón "Salir" o "← Volver"
2. Debe regresar a la lista de videollamadas

**Resultado Esperado:**
- ✅ Sale de la videollamada (Jitsi se desconecta)
- ✅ Vuelve a la vista de lista
- ✅ La videollamada sigue ACTIVA (si hay otros participantes)
- ✅ Contador de participantes se actualiza (-1)

**Verificar Backend:**
```bash
# El participante debe tener fecha_salida:
curl http://localhost:8000/api/communication/videollamadas/<ID>/participantes/activos \
  -H "Authorization: Bearer <TU_TOKEN_AQUI>"
```

Ya no debería aparecer en la lista de activos.

---

### ✅ Test 7: Finalizar Videollamada (Moderador)

**Pasos:**
1. Como creador/moderador, unirse a videollamada
2. Buscar opción para finalizar (puede estar en menú de Jitsi)
3. O llamar al endpoint manualmente:

```bash
curl -X PUT http://localhost:8000/api/communication/videollamadas/<ID>/finalizar \
  -H "Authorization: Bearer <TU_TOKEN_AQUI>" \
  -H "Content-Type: application/json" \
  -d '{"resumen_ia": "Videollamada de prueba finalizada"}'
```

**Resultado Esperado:**
- ✅ La videollamada cambia a estado "FINALIZADA"
- ✅ Todos los participantes son expulsados
- ✅ No se puede volver a unir
- ✅ Badge cambia a gris "Finalizada"

---

## 🔍 Debugging: Verificar Errores Comunes

### ❌ Error: "Cannot read property 'JitsiMeetExternalAPI' of undefined"

**Causa**: Jitsi script no cargó correctamente

**Solución**:
1. Verificar `frontend/index.html` tiene:
   ```html
   <script src="https://meet.jit.si/external_api.js"></script>
   ```
2. Recargar página con Ctrl+Shift+R (hard refresh)
3. Verificar en Console: `console.log(window.JitsiMeetExternalAPI)`

---

### ❌ Error: "Network Error" o "Failed to fetch"

**Causa**: Backend no está corriendo o URL incorrecta

**Solución**:
1. Verificar backend: http://localhost:8000/docs
2. Verificar `.env`:
   ```env
   VITE_API_URL=http://127.0.0.1:8000
   ```
3. Reiniciar frontend: `npm run dev`

---

### ❌ Error: "401 Unauthorized"

**Causa**: Token JWT expirado o inválido

**Solución**:
1. Cerrar sesión y volver a iniciar sesión
2. Verificar token en DevTools → Application → Local Storage
3. Si token falta, hacer login nuevamente

---

### ❌ Error: "useAuth() must be used within an AuthProvider"

**Causa**: Componente no está dentro de AuthProvider

**Solución**:
1. Verificar `main.tsx` tiene:
   ```tsx
   <AuthProvider>
     <App />
   </AuthProvider>
   ```
2. Ya está configurado ✅

---

### ❌ Error: "No QueryClient set, use QueryClientProvider"

**Causa**: React Query no configurado

**Solución**:
1. Verificar `main.tsx` tiene:
   ```tsx
   <QueryClientProvider client={queryClient}>
     <App />
   </QueryClientProvider>
   ```
2. Ya está configurado ✅

---

## 📊 Verificación en Base de Datos

### Consultar Videollamadas Creadas

```sql
SELECT 
  id,
  room_name,
  tipo_llamada,
  estado,
  fecha_inicio,
  fecha_fin,
  duracion_total
FROM videollamadas
ORDER BY fecha_creacion DESC
LIMIT 10;
```

### Consultar Participantes

```sql
SELECT 
  p.id,
  p.videollamada_id,
  u.nombre as usuario,
  p.fecha_union,
  p.fecha_salida,
  p.es_moderador,
  p.calidad_conexion
FROM participantes p
JOIN usuarios u ON p.usuario_id = u.id
WHERE p.videollamada_id = '<ID_VIDEOLLAMADA>'
ORDER BY p.fecha_union;
```

### Consultar Estadísticas

```sql
SELECT * FROM get_estadisticas_videollamada('<ID_VIDEOLLAMADA>');
```

---

## 🎉 Checklist de Éxito

- [ ] ✅ Backend corriendo sin errores
- [ ] ✅ Frontend corriendo sin errores
- [ ] ✅ Login funciona correctamente
- [ ] ✅ Página `/videollamadas` carga sin errores
- [ ] ✅ Puedes crear videollamadas (Video y Audio)
- [ ] ✅ Puedes unirte a videollamadas
- [ ] ✅ Jitsi Meet se embebe correctamente
- [ ] ✅ Audio y video funcionan
- [ ] ✅ Panel de participantes muestra usuarios
- [ ] ✅ Indicador de calidad funciona
- [ ] ✅ Puedes salir de videollamada
- [ ] ✅ Moderador puede finalizar videollamada
- [ ] ✅ Múltiples pestañas funcionan simultáneamente

---

## 🚀 Próximos Pasos

Una vez completado el testing exitosamente:

### Opción A: Phase 2.3 - Grabaciones con Jibri
- Configurar Jibri para grabaciones
- Implementar procesamiento de videos
- Transcripciones con Whisper
- Resúmenes con GPT

### Opción B: Phase 3 - Sistema de Notificaciones
- Push notifications en tiempo real
- Integración con WebSockets
- Notificaciones de videollamadas
- Preferencias de usuario

### Opción C: Pulir Sistema Actual
- Mejorar UI/UX
- Agregar tests unitarios
- Optimizar rendimiento
- Documentación adicional

---

## 📝 Notas Finales

- **Jitsi meet.jit.si**: Gratis pero limitado a 50 participantes
- **Producción**: Considera usar servidor Jitsi propio para mayor control
- **Grabaciones**: Requieren Jibri (Phase 2.3)
- **JWT**: Para servidor propio, configurar JWT en backend

¡Mucha suerte con las pruebas! 🎬✨
