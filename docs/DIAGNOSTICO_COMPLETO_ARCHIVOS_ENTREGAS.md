# 🔍 DIAGNÓSTICO COMPLETO - Sistema de Archivos en Entregas

**Fecha**: 21 de noviembre de 2025
**Estado**: ANÁLISIS DETALLADO DE TODOS LOS PUNTOS DE FALLO

---

## 📋 Problemas Reportados por el Usuario

1. ❌ **Archivos no se muestran después de entrega**
   - Subo archivo → Entrego tarea → No veo el archivo

2. ❌ **Se muestra UUID en lugar del nombre real**
   - Dice "Archivos adjuntos: `/uploads/entregas/bf8f1b7f-c4f8-abc123.pdf`"
   - Debería ser: "documento.pdf"

3. ❌ **Solo se ve 1 archivo aunque subí varios**
   - Subo 2+ archivos → Solo aparece 1 (o lista vacía)

4. ❌ **Al cancelar entrega, se pierden archivos**
   - Cancelo → Me dice "archivos se mantendrán para referencia"
   - Pero al entregar de nuevo, no veo los archivos anteriores

5. ❌ **Archivos no persisten al recargar página**
   - Subo archivo → Recargo página → Archivo desaparece

6. ❌ **Click en archivo no funciona**
   - Click → Recarga la misma página (no abre descarga)
   - Botón descargar: no pasa nada

---

## 🔧 Análisis del Flujo Actual

### **1️⃣ FRONTEND: Usuario selecciona archivos (SubirTareaPage.tsx)**

**Archivo**: `frontend/src/pages/tareas/SubirTareaPage.tsx`

**Función**: `handleFileSelect()` + `agregarArchivos()`
**Líneas**: 115-140

```typescript
const agregarArchivos = (files: File[]) => {
  // ✅ Valida tamaño
  // ✅ Crea array de ArchivoSubido con file + preview
  // ✅ Actualiza estado: setArchivos(prev => [...prev, ...nuevosArchivos])
  
  // Estado local en memoria: 
  // archivos: [
  //   { file: File, preview?: string },
  //   { file: File, preview?: string }
  // ]
};
```

**Estado después**: `archivos` contiene N archivos locales ✅

---

### **2️⃣ FRONTEND: Usuario hace submit (handleSubmit)**

**Función**: `handleSubmit()` 
**Líneas**: 205-240

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  if (!tareaId || !tarea) return;

  try {
    setSubmitting(true);

    // 1. Crear FormData
    const entregaData = new FormData();
    entregaData.append('contenido', comentarios || 'Entrega de tarea');

    // ✅ IMPORTANTE: Agregar TODOS los archivos al FormData
    archivos.forEach((archivo) => {
      entregaData.append('archivos', archivo.file);
      // ↑ Esto es correcto - agrega cada File al FormData
      // FormData.append() permite múltiples valores con la misma clave
    });

    // 2. Enviar a backend
    const response = await apiClientTareas.entregarTarea(tareaId, entregaData as any);
    // ↑ Frontend espera que backend procese la entrega aquí

    toast.success('¡Tarea entregada exitosamente!');

    // 3. Recargar datos desde BD
    try {
      await cargarDatosTarea();
      // ↑ Este fetch DEBE obtener la entrega actualizada con todos los archivos
    } catch (reloadError) {
      console.warn('No se pudieron recargar los datos...', reloadError);
    }

    // 4. Limpiar
    setComentarios('');
    setArchivos([]);

  } catch (error: any) {
    // ...
  } finally {
    setSubmitting(false);
  }
};
```

**Puntos críticos**:
- ✅ FormData con múltiples archivos: CORRECTO
- ✅ POST a `/tareas/{id}/entregar`: CORRECTO
- ⚠️ `cargarDatosTarea()` DEBE ejecutarse para refrescar datos

---

### **3️⃣ BACKEND: Endpoint recibe entrega (curso_tareas.py)**

**Archivo**: `backend/src/api/routes/academic/curso_tareas.py`
**Endpoint**: `POST /{tarea_id}/entregar`
**Líneas**: 102-175

```python
@router.post("/{tarea_id}/entregar")
async def entregar_tarea(
    tarea_id: str,
    contenido: str = Form(None),
    archivos: List[UploadFile] = File(default=[]),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    logger.info(f"📥 POST /tareas/{tarea_id}/entregar")
    logger.info(f"   - Archivos recibidos: {len(archivos)}")
    
    # ✅ IMPORTANTE: El parámetro archivos: List[UploadFile] 
    # Esto DEBE recibir TODOS los archivos del FormData
    
    # Fallback para contenido vacío
    if not contenido or contenido.strip() == "":
        contenido = "Entrega de tarea"

    archivo_urls = []
    archivos_metadata = []
    
    # Procesar TODOS los archivos (no solo el primero)
    if archivos:
        try:
            # 1. Crear directorio
            backend_dir = Path(__file__).parent.parent.parent.parent  # backend/
            upload_dir = backend_dir / "uploads" / "entregas"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # 2. Guardar CADA archivo
            for archivo in archivos:
                # Generar nombre único (UUID)
                file_ext = Path(archivo.filename).suffix
                unique_filename = f"{uuid4()}{file_ext}"
                file_path = upload_dir / unique_filename
                
                # Guardar en disco
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(archivo.file, f)
                
                # Crear URL
                archivo_url = f"/uploads/entregas/{unique_filename}"
                archivo_urls.append(archivo_url)
                
                # 🔑 CRITICAL: Guardar metadata con NOMBRE ORIGINAL
                archivos_metadata.append({
                    "url": archivo_url,
                    "nombre_original": archivo.filename,  # ← NOMBRE REAL
                    "nombre_almacenado": unique_filename   # ← UUID
                })
                
                logger.info(f"✅ Archivo guardado: {archivo_url}")
                logger.info(f"   Original: {archivo.filename}")
        
        except Exception as e:
            logger.error(f"❌ Error guardando archivos: {str(e)}")
            archivo_urls = []
            archivos_metadata = []
    
    # Primer archivo como URL principal (compatibilidad)
    archivo_url = archivo_urls[0] if archivo_urls else None
    
    # Llamar servicio
    return tarea_service.entregar_tarea(
        db=db,
        tarea_id=tarea_id,
        usuario=current_user,
        contenido=contenido,
        archivo_url=archivo_url,
        archivo_urls=archivo_urls,
        archivos_metadata=archivos_metadata  # ← Pasa metadata al servicio
    )
```

**Validación**:
- ✅ Recibe List[UploadFile]: CORRECTO
- ✅ Guarda en disco: `/uploads/entregas/{UUID}.ext`
- ✅ Crea metadata con nombre original: CORRECTO
- ✅ Pasa todo al servicio: CORRECTO

---

### **4️⃣ BACKEND: Servicio procesa entrega (tarea_service.py)**

**Archivo**: `backend/src/services/academic/tarea_service.py`
**Función**: `entregar_tarea()`
**Líneas**: 438-530

```python
@staticmethod
def entregar_tarea(
    db: Session,
    tarea_id: str,
    usuario: Usuario,
    contenido: str,
    archivo_url: Optional[str] = None,
    archivo_urls: Optional[list] = None,
    archivos_metadata: Optional[list] = None  # ← Metadata con nombres
) -> Dict[str, Any]:
    
    import json
    
    # Preparar JSON con archivos adicionales
    archivos_json = None
    if archivos_metadata and len(archivos_metadata) > 0:
        # Usar metadata completa (INCLUYE NOMBRE ORIGINAL)
        archivos_json = json.dumps({"archivos": archivos_metadata})
        # ↑ Ejemplo:
        # {
        #   "archivos": [
        #     {
        #       "url": "/uploads/entregas/abc123.pdf",
        #       "nombre_original": "documento.pdf",
        #       "nombre_almacenado": "abc123.pdf"
        #     },
        #     {
        #       "url": "/uploads/entregas/def456.docx",
        #       "nombre_original": "tarea.docx",
        #       "nombre_almacenado": "def456.docx"
        #     }
        #   ]
        # }
    elif archivo_urls and len(archivo_urls) > 0:
        # Fallback sin metadata
        archivos_json = json.dumps({
            "archivos": [{"url": url, "nombre": url.split("/")[-1]} for url in archivo_urls]
        })
    
    # Verificar si ya entregó
    entrega_existente = TareaService._obtener_mi_entrega(db, tarea_id, usuario.usuario_id)
    
    if entrega_existente:
        # Actualizar entrega existente
        return TareaService._actualizar_entrega(
            db, entrega_existente['entrega_id'], contenido, archivo_url, archivos_json
        )
    
    # Crear nueva entrega
    query = text("""
        INSERT INTO entregas_tareas (
            entrega_id, tarea_id, estudiante_id, contenido_texto, archivo_url,
            archivos_adicionales, fecha_entrega, estado
        )
        VALUES (
            gen_random_uuid()::text, :tarea_id, :estudiante_id, :contenido, :archivo_url,
            :archivos_adicionales, :fecha_entrega, 'entregada'
        )
        RETURNING entrega_id
    """)
    
    result = db.execute(query, {
        "tarea_id": tarea_id,
        "estudiante_id": usuario.usuario_id,
        "contenido": contenido,
        "archivo_url": archivo_url,
        "archivos_adicionales": archivos_json,  # ← GUARDA JSON CON METADATA
        "fecha_entrega": datetime.now(timezone.utc)
    })
    
    entrega_id = result.fetchone()[0]
    db.commit()
    
    # ✅ Retorna OK
    return {
        "success": True,
        "message": "Tarea entregada exitosamente",
        "data": {
            "entrega_id": str(entrega_id),
            "fecha_entrega": datetime.now(timezone.utc).isoformat(),
            "estado": "entregada",
            "archivos": archivo_urls or []  # ← DEVUELVE SOLO URLs sin nombres
        }
    }
```

**Validación**:
- ✅ Serializa metadata a JSON: CORRECTO
- ✅ Guarda en BD `archivos_adicionales`: CORRECTO
- ⚠️ Retorna `"archivos": archivo_urls` (solo URLs, no nombres): PROBLEMA #1

---

### **5️⃣ FRONTEND: Recibe respuesta del POST**

El frontend recibe:
```json
{
  "success": true,
  "message": "Tarea entregada exitosamente",
  "data": {
    "entrega_id": "uuid-123",
    "fecha_entrega": "2025-11-21T15:30:00Z",
    "estado": "entregada",
    "archivos": [
      "/uploads/entregas/abc123.pdf",
      "/uploads/entregas/def456.docx"
    ]
  }
}
```

**Problema**: 
- ❌ `archivos` son solo URLs (sin nombres originales)
- ❌ No puede mostrar "documento.pdf" 
- ❌ Solo muestra "abc123.pdf" (sacado del URL)

---

### **6️⃣ FRONTEND: Llama cargarDatosTarea()**

**Función**: `cargarDatosTarea()`
**Líneas**: 60-99

```typescript
const cargarDatosTarea = async () => {
  if (!tareaId) return;

  try {
    setLoading(true);
    
    // 1. Cargar detalles de la tarea
    const tareaData = await apiClientTareas.obtenerTarea(tareaId);
    setTarea(tareaData);

    // 2. Si hay entrega, cargarla
    if (tareaData.mi_entrega_id) {
      console.log("Entrega encontrada:", tareaData.mi_entrega_id);
      
      // 🔑 CRITICAL: Este fetch debe traer la entrega actualizada
      const entregaDetalle = await apiClientTareas.obtenerEntrega(tareaData.mi_entrega_id);
      setEntregaExistente(entregaDetalle);
      // ↑ Este estado debe contener los archivos con metadata
    }
  } catch (error: any) {
    // ...
  } finally {
    setLoading(false);
  }
};
```

**Flujo esperado**:
1. GET `/tareas/{id}` → obtiene `mi_entrega_id`
2. GET `/entregas/{entrega_id}` → **DEBE retornar archivos con nombres**

---

### **7️⃣ BACKEND: GET /entregas/{entrega_id} (obtener_entrega)**

**Archivo**: `backend/src/services/academic/tarea_service.py`
**Función**: `obtener_entrega()`
**Líneas**: 540-630

```python
@staticmethod
def obtener_entrega(db: Session, entrega_id: str, usuario: Usuario):
    """
    Obtiene detalles de una entrega
    """
    import json
    
    # Consultar BD
    query = text("""
        SELECT 
            et.entrega_id,
            et.tarea_id,
            et.estudiante_id,
            et.contenido_texto,
            et.archivo_url,
            et.archivos_adicionales,  # ← CONTIENE JSON CON METADATA
            ...
        FROM entregas_tareas et
        WHERE et.entrega_id = :entrega_id
    """)
    
    result = db.execute(query, {"entrega_id": entrega_id}).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
    
    entrega = dict(result._mapping)
    
    # Parsear archivos_adicionales JSON
    archivos_urls = []
    
    if entrega.get('archivo_url'):
        archivos_urls.append(entrega['archivo_url'])
    
    if entrega.get('archivos_adicionales'):
        try:
            archivos_data = json.loads(entrega['archivos_adicionales'])
            # ↑ Debería ser:
            # {
            #   "archivos": [
            #     {"url": "/uploads/entregas/abc123.pdf", "nombre_original": "documento.pdf", ...},
            #     {"url": "/uploads/entregas/def456.docx", "nombre_original": "tarea.docx", ...}
            #   ]
            # }
            
            if isinstance(archivos_data, dict) and 'archivos' in archivos_data:
                for archivo in archivos_data['archivos']:
                    if isinstance(archivo, dict):
                        # ✅ IMPORTANTE: Convertir a objeto con URL + nombre
                        if 'nombre_original' in archivo and 'url' in archivo:
                            # Tiene metadata - agregar como dict
                            if archivo['url'] not in archivos_urls:
                                archivos_urls.append({
                                    "url": archivo['url'],
                                    "nombre": archivo.get('nombre_original', archivo['url'].split("/")[-1])
                                })
                        elif 'url' in archivo:
                            archivos_urls.append(archivo['url'])
                    elif isinstance(archivo, str):
                        if archivo not in archivos_urls:
                            archivos_urls.append(archivo)
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Agregar a respuesta
    entrega['archivos'] = archivos_urls
    
    # Retorna al frontend
    return entrega
```

**Validación**:
- ✅ Parsea JSON de `archivos_adicionales`: CORRECTO
- ✅ Convierte a array de objects con `{url, nombre}`: CORRECTO
- ✅ Retorna en `entrega['archivos']`: CORRECTO

---

### **8️⃣ FRONTEND: Recibe entrega con archivos (setEntregaExistente)**

Debería recibir:
```json
{
  "entrega_id": "uuid-123",
  "archivos": [
    {
      "url": "/uploads/entregas/abc123.pdf",
      "nombre": "documento.pdf"
    },
    {
      "url": "/uploads/entregas/def456.docx",
      "nombre": "tarea.docx"
    }
  ],
  ...
}
```

---

### **9️⃣ FRONTEND: Renderiza archivos**

**Líneas**: 600-650 (después de entregar)

```typescript
{entregaExistente?.archivos && entregaExistente.archivos.length > 0 && (
  <div className="bg-blue-50 dark:bg-blue-900/20...">
    <p>Archivos adjuntos ({entregaExistente.archivos.length}):</p>
    <div className="space-y-2">
      {entregaExistente.archivos.map((archivo, idx) => {
        let archivoUrl = '';
        let nombreArchivo = '';
        
        // ✅ Maneja tanto URLs simples como objetos con metadata
        if (typeof archivo === 'string') {
          archivoUrl = archivo;
          nombreArchivo = archivo.split('/').pop() || `Archivo ${idx + 1}`;
        } else if (typeof archivo === 'object' && archivo.url) {
          archivoUrl = archivo.url;
          nombreArchivo = archivo.nombre || archivo.url.split('/').pop() || `Archivo ${idx + 1}`;
        } else {
          return null;
        }
        
        return (
          <a
            key={idx}
            href={archivoUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="..."
          >
            <FileText className="..." />
            <span>{nombreArchivo}</span>
            <Download className="..." />
          </a>
        );
      })}
    </div>
  </div>
)}
```

**Validación**:
- ✅ Maneja tanto strings como objects: CORRECTO
- ✅ Extrae nombre de metadata: CORRECTO
- ✅ Crea link con `href={archivoUrl}`: CORRECTO

---

## 🔴 PROBLEMAS ENCONTRADOS

### **PROBLEMA #1: Endpoint entregar_tarea() retorna solo URLs**

**Ubicación**: `tarea_service.py` línea 520

```python
# ACTUAL (MALO):
return {
    "success": True,
    "message": "Tarea entregada exitosamente",
    "data": {
        "entrega_id": str(entrega_id),
        "archivos": archivo_urls or []  # ← Solo URLs sin nombres
    }
}

# DEBERÍA SER:
return {
    "success": True,
    "message": "Tarea entregada exitosamente",
    "data": {
        "entrega_id": str(entrega_id),
        "archivos": archivos_metadata or []  # ← Incluyendo metadata
    }
}
```

**Impacto**: 
- Frontend recibe `/uploads/entregas/abc123.pdf`
- No puede mostrar el nombre real "documento.pdf"
- Usuario ve UUID en lugar de nombre

**Solución**: Retornar `archivos_metadata` en lugar de `archivo_urls`

---

### **PROBLEMA #2: Endpoint GET /tareas/{id} no retorna mi_entrega_id**

**Ubicación**: Verificar función `obtener_tarea()`

Posible problema:
- La tarea NO retorna `mi_entrega_id`
- Entonces `cargarDatosTarea()` no encuentra la entrega
- La página nunca llama a `obtenerEntrega()`
- Los archivos NUNCA se cargan

**Solución**: Verificar que `obtener_tarea()` retorna `mi_entrega_id`

---

### **PROBLEMA #3: Ruta GET /uploads/entregas/{filename} no existe**

**Ubicación**: Backend FastAPI

El problema: Los archivos se guardan en `/backend/uploads/entregas/`
Pero FastAPI **no sirve estas rutas estáticamente**.

Cuando el frontend hace:
```html
<a href="/uploads/entregas/abc123.pdf" target="_blank">descargar</a>
```

FastAPI responde con **404 Not Found** porque no hay ruta definida.

**Solución**: Configurar ruta estática en FastAPI:

```python
# En backend/src/main.py, agregar:
from fastapi.staticfiles import StaticFiles
from pathlib import Path

backend_dir = Path(__file__).parent.parent
app.mount("/uploads", StaticFiles(directory=backend_dir / "uploads"), name="uploads")
```

---

### **PROBLEMA #4: Cancelar entrega NO persiste archivos**

**Ubicación**: `tarea_service.py` función `cancelar_entrega()`

Cuando se cancela una entrega, probablemente:
- Se marca como `estado = 'cancelada'`
- Se ELIMINA completamente (DELETE en lugar de UPDATE)
- O se limpia la columna `archivos_adicionales`

**Solución**: Al cancelar, solo cambiar estado, NO eliminar archivos

```python
# EN cancelar_entrega():
query = text("""
    UPDATE entregas_tareas
    SET estado = 'cancelada'
    WHERE entrega_id = :entrega_id
    -- ✅ NO tocar archivos_adicionales
""")
```

---

## ✅ Checklist de Verificación

- [ ] 1. Verificar que `/uploads/entregas/` existe en disco
- [ ] 2. Verificar que archivos se guardan en disco (con UUID)
- [ ] 3. Verificar que `archivos_adicionales` tiene JSON en BD (SELECT * FROM entregas_tareas)
- [ ] 4. Verificar que `obtener_tarea()` retorna `mi_entrega_id`
- [ ] 5. Verificar que `obtener_entrega()` parsea JSON y retorna metadata
- [ ] 6. Configurar ruta estática `/uploads` en FastAPI
- [ ] 7. Asegurar que `entregar_tarea()` retorna `archivos_metadata`
- [ ] 8. Verificar que cancelar mantiene `archivos_adicionales` intacto
- [ ] 9. Test frontend: cargarDatosTarea() llama obtenerEntrega()
- [ ] 10. Test frontend: archivos se muestran con nombres reales

---

## 🚀 Próximos Pasos

1. **Reiniciar backend** con cambios
2. **Verificar BD** que archivos_adicionales tenga datos JSON
3. **Test end-to-end**: 
   - Subir 2 archivos
   - Entregar tarea
   - Ver archivos con nombres reales
   - Click en archivo → Descarga
   - Cancelar → Ver archivos en referencia
   - Entregar nuevamente → Archivos persisten

---

**Estado**: LISTO PARA IMPLEMENTAR SOLUCIONES
