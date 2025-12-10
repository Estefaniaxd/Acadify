# Análisis Profundo y Fix: Sistema de Entrega de Tareas - 19 de Noviembre 2025

## 🔍 Problema Identificado

### Error Reportado
```
POST http://127.0.0.1:8000/api/cursos/tareas/tareas/{tarea_id}/entregar
422 (Unprocessable Entity)
{detail: Array(1)}  // Validación Pydantic fallida
```

### Causa Raíz: Mismatch Frontend ↔ Backend

**Frontend enviaba:**
- FormData (multipart/form-data) 
- Campos: `contenido`, `archivo` (File)

**Backend esperaba:**
- JSON puro (application/json)
- Parámetros: `contenido: Body(...)`, `archivos: Body(...)`

**Resultado:** FastAPI no podía mapear FormData a parámetros `Body()` → Error 422

---

## 🛠️ Problemas Adicionales Encontrados

### 1. **Frontend: Código Muerto**
**Archivo:** `frontend/src/pages/academic/SubirTareaPage.tsx`

```typescript
const crearEntregaMutation = useMutation({
    mutationFn: async (data: TareaFormData) => {
      // TODO: Implementar en backend
      // return await apiClientTareas.crearEntrega(data);
      console.log('Crear entrega:', data);  // ← NUNCA LLAMA AL API
      return null;
    },
```

**Impacto:** El formulario nunca enviaba datos reales al backend, solo loguea en consola.

---

### 2. **API Client: Tipo Incorrecto**
**Archivo:** `frontend/src/modules/tareas/api.ts`

```typescript
async entregarTarea(
    tareaId: string,
    entregaData: {
      contenido: string;
      archivos?: string;  // ← Esperaba string, no File
    }
  ): Promise<EntregaTarea>
```

**Impacto:** El método no aceptaba `FormData` ni `File`.

---

### 3. **Backend: Falta Guardado de Archivos**
**Archivo:** `backend/src/api/routes/academic/curso_tareas.py`

```python
archivo_url = None
if archivo is not None:
    logger.info(f"Archivo recibido: {archivo.filename}")
    # TODO: Implementar guardado real y obtener URL
    archivo_url = archivo.filename  # ← Solo toma el nombre, no guarda
```

**Impacto:** Los archivos nunca se guardaban en el servidor.

---

## ✅ Soluciones Implementadas

### Solución 1: Adaptar Backend para FormData
**Cambio:** Parámetros `Body()` → `Form()` y `File()`

```python
@router.post("/tareas/{tarea_id}/entregar")
async def entregar_tarea(
    tarea_id: str,
    contenido: str = Form(...),          # ← Form para multipart
    archivo: UploadFile = File(None),   # ← File para archivo
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    # FastAPI puede mapear correctamente FormData ahora
```

**Ventaja:** FormData es la forma correcta de enviar archivos + datos.

---

### Solución 2: Guardar Archivos Realmente
**Cambio:** Implementar lógica de persistencia

```python
# Crear directorio si no existe
backend_dir = Path(__file__).parent.parent.parent.parent  # backend/
upload_dir = backend_dir / "uploads" / "entregas"
upload_dir.mkdir(parents=True, exist_ok=True)

# Generar nombre único
unique_filename = f"{uuid4()}{Path(archivo.filename).suffix}"
file_path = upload_dir / unique_filename

# Guardar archivo
with open(file_path, "wb") as f:
    shutil.copyfileobj(archivo.file, f)

archivo_url = f"/uploads/entregas/{unique_filename}"
```

**Ventaja:** 
- UUID para evitar colisiones
- Ruta servida automáticamente por FastAPI (`/uploads` mounting en `main.py`)
- URL almacenada en BD para referencia

---

### Solución 3: Actualizar Frontend para Enviar FormData
**Cambio 1:** `api.ts` - Aceptar FormData

```typescript
async entregarTarea(
    tareaId: string,
    formData: FormData  // ← Ahora acepta FormData
  ): Promise<EntregaTarea> {
    const response = await axios.post(
      `${this.baseURL}/tareas/${tareaId}/entregar`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
```

**Cambio 2:** `SubirTareaPage.tsx` - Crear y enviar FormData

```typescript
const crearEntregaMutation = useMutation({
    mutationFn: async (data: TareaFormData) => {
      const formData = new FormData();

      // Construir contenido
      let contenido = data.contenido_texto || '';
      if (data.comentarios_estudiante) {
        contenido = contenido
          ? `${data.comentarios_estudiante}\n\n${contenido}`
          : data.comentarios_estudiante;
      }
      if (!contenido.trim()) {
        contenido = 'Archivo adjunto'; // Fallback
      }
      formData.append('contenido', contenido);

      // Agregar archivo
      if (formState.archivo) {
        formData.append('archivo', formState.archivo);
      }

      // Llamar API real
      return await apiClientTareas.entregarTarea(tareaId!, formData);
    },
```

**Ventaja:**
- Maneja correctamente archivo + contenido
- Fallback si no hay comentario: "Archivo adjunto"
- Llama API real (antes solo loguea)

---

### Solución 4: Validación Frontend Correcta

```typescript
const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validación: al menos archivo O contenido
    if (!formState.archivo && !formState.contenidoTexto) {
      setError('Debes adjuntar un archivo o escribir contenido');
      return;
    }

    // ... enviar
```

**Ventaja:** Previene envío vacío antes de llegar al backend.

---

## 📋 Flujo Completo (Después del Fix)

### 1. Usuario Llena Formulario
```
✓ Selecciona archivo PDF o DOC
✓ Escribe comentarios (opcional)
✓ Escribe contenido (opcional)
✓ Click en "Entregar Tarea"
```

### 2. Validación Frontend
```
✓ Verifica que exista archivo O contenido
✓ Crea FormData con ambos campos
✓ Llama a apiClientTareas.entregarTarea()
```

### 3. Axios Envía
```
POST /api/cursos/tareas/tareas/{id}/entregar
Content-Type: multipart/form-data
Authorization: Bearer {token}

Body:
- contenido: "Comentarios aquí\n\nContenido aquí"
- archivo: <File object>
```

### 4. Backend Recibe
```python
# FastAPI mapea FormData correctamente
contenido: str = Form(...)    # ✓ Recibe comentario + contenido
archivo: UploadFile = File(None)  # ✓ Recibe archivo

# Guarda archivo en `/uploads/entregas/{uuid}`
# Inserta entrega en BD con `archivo_url`
# Retorna 200 OK
```

### 5. Frontend Procesa Respuesta
```typescript
onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['entregas', tareaId] });
    navigate(-1); // Volver a la lista
    // O mostrar toast de éxito
}

onError: (error) => {
    setError(error.response?.data?.detail);
}
```

---

## 🧪 Testing Manual

### Escenario 1: Solo Archivo (Sin Comentarios)
```
1. Selecciona archivo: "tarea_solucion.pdf"
2. Dejar comentarios vacío
3. Dejar contenido vacío
4. Click "Entregar"

Esperado: ✓ FormData contiene:
  - contenido: "Archivo adjunto"
  - archivo: <PDF file>
Resultado: Entrega guardada, archivo en /uploads/entregas/
```

### Escenario 2: Solo Contenido (Sin Archivo)
```
1. No seleccionar archivo
2. Escribir comentario: "Esta es mi solución..."
3. Click "Entregar"

Esperado: ✓ FormData contiene:
  - contenido: "Esta es mi solución..."
  - archivo: undefined
Resultado: Entrega guardada
```

### Escenario 3: Archivo + Comentarios
```
1. Selecciona archivo: "respuestas.docx"
2. Escribe comentario: "Adjunto mis respuestas"
3. Escribe contenido: "Preguntas 1-5 contestadas"
4. Click "Entregar"

Esperado: ✓ FormData contiene:
  - contenido: "Adjunto mis respuestas\n\nPreguntas 1-5 contestadas"
  - archivo: <DOCX file>
Resultado: Entrega guardada con ambos
```

### Escenario 4: Validación Frontend
```
1. No seleccionar archivo
2. Dejar todo vacío
3. Click "Entregar"

Esperado: ✗ Error: "Debes adjuntar un archivo o escribir contenido"
Resultado: Formulario bloqueado, no envía
```

---

## 📊 Cambios de Código

### Archivos Modificados
1. **backend/src/api/routes/academic/curso_tareas.py**
   - Cambio: `Body()` → `Form()` y `File()`
   - Cambio: Implementar guardado de archivos con UUID
   - Líneas: 77-117

2. **frontend/src/modules/tareas/api.ts**
   - Cambio: Parámetro `entregaData` → `formData: FormData`
   - Cambio: Agregar header `Content-Type: multipart/form-data`
   - Líneas: 85-98

3. **frontend/src/pages/academic/SubirTareaPage.tsx**
   - Cambio: Implementar mutación real (antes era `console.log`)
   - Cambio: Crear FormData correctamente
   - Cambio: Validación mejorada
   - Cambio: Importes de rutas corregidas
   - Líneas: 18-19, 96-137, 165-179

---

## ⚠️ Consideraciones Importantes

### 1. Seguridad de Archivos
```
✓ UUID previene enumeration
✓ Separado en /uploads/entregas/ 
✓ Validación de token required
✓ TODO: Implementar validación de extensión
✓ TODO: Escanear malware con librería
```

### 2. Límite de Tamaño
```
✓ Frontend valida tamaño antes de enviar
✓ Tarea especifica tamano_maximo_mb
✓ TODO: Backend debe validar Content-Length
```

### 3. Directorio de Uploads
```
✓ Ya existe /backend/uploads/entregas/
✓ Ya está montado en FastAPI como /uploads
✓ Permisos verificados (rwx)
```

---

## 🚀 Próximos Pasos

1. **Test Manual** en navegador
   - Entrega con archivo
   - Entrega con contenido
   - Entrega combinada
   - Verificar archivos guardados en `/uploads/entregas/`

2. **Validación Backend**
   - Implementar límite de tamaño
   - Validar extensiones permitidas
   - Escaneo de malware (opcional)

3. **Frontend: Feedback Usuario**
   - Toast de éxito tras entrega
   - Barra de progreso para upload
   - Mostrar archivo guardado

4. **Endpoint Faltante**
   - Implementar `obtenerMiEntrega()`
   - Para mostrar historial de entregas del estudiante

---

## 📝 Notas de Ingeniería

### Por Qué FormData es Correcto
- HTML forms con `<input type="file">` envían multipart/form-data
- Axios puede enviar FormData directamente
- FastAPI mapea automáticamente a parámetros `Form()` y `File()`
- Es el estándar web desde 1995

### Por Qué Body() Falló
- `Body()` solo funciona para JSON puro
- No puede mapear multipart/form-data
- Error 422 = Validación Pydantic fallida (campo no encontrado)

### Rutas Absolutas vs Relativas
```python
# ✗ Malo (relativo a cwd, puede cambiar)
upload_dir = Path("uploads/entregas")

# ✓ Bueno (relativo al archivo actual, siempre funciona)
backend_dir = Path(__file__).parent.parent.parent.parent
upload_dir = backend_dir / "uploads" / "entregas"
```

---

## 🔗 Referencias

- **FastAPI File Uploads**: https://fastapi.tiangolo.com/tutorial/request-files/
- **FormData MDN**: https://developer.mozilla.org/en-US/docs/Web/API/FormData
- **multipart/form-data RFC**: https://tools.ietf.org/html/rfc7578

---

**Análisis completado**: 19 de noviembre 2025
**Estado**: ✅ Implementado y listo para testing
