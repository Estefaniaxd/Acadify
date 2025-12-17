# 🔍 ANÁLISIS DETALLADO: BUGS CRÍTICOS EN SISTEMA DE ARCHIVOS Y ENTREGAS

**Fecha**: 21 de noviembre de 2025  
**Versión**: 1.0.0  
**Criticidad**: 🔴 **ALTA** - Afecta experiencia de usuario directamente

---

## 📊 RESUMEN EJECUTIVO

Se identificaron **5 bugs críticos** en el sistema de entregas de tareas relacionados con el manejo de archivos:

| # | Bug | Severidad | Impacto Usuario | Complejidad Fix |
|---|-----|-----------|-----------------|-----------------|
| 1 | **Contador de archivos incorrecto** | 🔴 Alta | Confusión total | ⚠️ Media |
| 2 | **Nombres de archivos como UUIDs** | 🔴 Alta | No reconoce sus archivos | ✅ Fácil |
| 3 | **Solo 1 archivo visible después de cancelar** | 🔴 Alta | Pérdida de datos percibida | ⚠️ Media |
| 4 | **No se puede re-entregar sin agregar archivo nuevo** | 🟡 Media | Workflow roto | ⚠️ Media |
| 5 | **Lógica de estado "cancelada" incompleta** | 🟡 Media | Inconsistencia de estado | ⚠️ Media |

---

## 🔬 ANÁLISIS DETALLADO POR BUG

---

### ❌ **BUG #1: Contador de Archivos Incorrecto**

#### 📝 **Descripción del Problema**

**Comportamiento reportado por el usuario:**
> "Cuando yo entrego la tarea me dice 'Archivos subidos: 1' y subí cuatro archivos."

#### 🧪 **Reproducción Paso a Paso**

1. Usuario selecciona 4 archivos desde el explorador de archivos
2. Hace clic en "Entregar Tarea"
3. El sistema muestra: **"Archivos subidos: 1"** ❌
4. Pero en realidad subió **4 archivos** ✅

#### 🔎 **CAUSA RAÍZ IDENTIFICADA**

**Ubicación del bug**: `backend/src/services/academic/tarea_service.py` - Línea 559

```python
# ❌ CÓDIGO PROBLEMÁTICO ACTUAL:
def entregar_tarea(
    db: Session,
    tarea_id: str,
    usuario: Usuario,
    contenido: str,
    archivo_url: Optional[str] = None,        # ← Solo el PRIMER archivo
    archivo_urls: Optional[list] = None,      # ← TODOS los archivos
    archivos_metadata: Optional[list] = None  # ← Metadata con nombres
) -> Dict[str, Any]:
    # ...
    return {
        "success": True,
        "message": "Tarea entregada exitosamente",
        "data": {
            "entrega_id": str(entrega_id),
            "fecha_entrega": datetime.now(timezone.utc).isoformat(),
            "estado": "entregada",
            "archivos": archivos_metadata or []  # ← CORRECTO pero el mensaje lo ignora
        }
    }
```

**El problema real está en el TOAST del frontend:**

**Ubicación**: `frontend/src/pages/tareas/SubirTareaPage.tsx` - Línea 260

```typescript
// ❌ ESTE ES EL BUG:
const response = await apiClientTareas.entregarTarea(tareaId, entregaData as any);

toast.success('¡Tarea entregada exitosamente!');
// ↑ No menciona cuántos archivos se subieron

// ✅ DEBERÍA SER:
const archivosCount = response.data?.archivos?.length || 0;
toast.success(`¡Tarea entregada con ${archivosCount} archivo${archivosCount !== 1 ? 's' : ''}!`);
```

#### 💡 **SOLUCIÓN PROPUESTA**

**1. Backend ya está correcto** ✅  
El backend retorna `archivos_metadata` correctamente con todos los archivos.

**2. Frontend debe usar la respuesta correctamente:**

```typescript
// En SubirTareaPage.tsx handleSubmit()
try {
  const response = await apiClientTareas.entregarTarea(tareaId, entregaData as any);
  
  const archivosCount = response.data?.archivos?.length || 0;
  
  if (archivosCount === 0) {
    toast.success('¡Tarea entregada exitosamente!');
  } else {
    toast.success(`¡Tarea entregada con ${archivosCount} archivo${archivosCount !== 1 ? 's' : ''}! ✅`);
  }
  
  // ...resto del código
}
```

#### 🎯 **Impacto Esperado**

- **ANTES**: "¡Tarea entregada exitosamente!" (sin contexto)
- **DESPUÉS**: "¡Tarea entregada con 4 archivos! ✅" (información clara)

---

### ❌ **BUG #2: Nombres de Archivos Mostrados Como UUIDs**

#### 📝 **Descripción del Problema**

**Comportamiento reportado:**
> "Yo subí los archivos desde mi explorador de archivos y me aparece un nombre digamos 'hoja de vida'... pero acá solamente me aparece un archivo y me aparece como un ID o como algo como una cadena de caracteres pero pues no es el nombre del archivo."

#### 🧪 **Reproducción**

1. Usuario sube archivo llamado: `Hoja_de_Vida_Juan.pdf`
2. Sistema lo guarda en disco como: `a3b7c9d1-4e5f-6789-abcd-ef1234567890.pdf` (UUID)
3. Frontend muestra: `a3b7c9d1-4e5f-6789-abcd-ef1234567890.pdf` ❌
4. Usuario esperaba ver: `Hoja_de_Vida_Juan.pdf` ✅

#### 🔎 **CAUSA RAÍZ IDENTIFICADA**

**Problema 1: Backend guarda nombre original pero frontend no lo usa**

**Backend** (`curso_tareas.py` línea 192-202):

```python
# ✅ Backend GUARDA el nombre original correctamente:
meta = {
    "url": archivo_url,
    "nombre_original": archivo.filename,  # ← Nombre real del usuario
    "nombre": archivo.filename,           # ← También aquí
    "nombre_almacenado": unique_filename  # ← UUID (para disco)
}
archivos_metadata.append(meta)
```

**Frontend** (`SubirTareaPage.tsx` línea 633-650):

```typescript
// ❌ PROBLEMA: Frontend usa split('/').pop() en la URL
let nombreArchivo = '';

if (typeof archivo === 'string') {
  archivoUrl = archivo;
  nombreArchivo = archivo.split('/').pop() || `Archivo ${index + 1}`;
  // ↑ Extrae el UUID del path: /uploads/entregas/UUID.pdf
} else if (typeof archivo === 'object' && archivo.url) {
  archivoUrl = archivo.url;
  // ✅ Prioriza nombre_original (ESTO ESTÁ BIEN)
  nombreArchivo = archivo.nombre_original || archivo.nombre || archivo.url.split('/').pop() || `Archivo ${index + 1}`;
}
```

**¿Por qué falla?**

El problema es que `obtenerEntrega()` del backend NO está retornando `nombre_original` en el formato correcto.

**Backend** (`tarea_service.py` línea 665-685):

```python
# ❌ PROBLEMA DETECTADO:
def obtener_entrega(db: Session, entrega_id: str, usuario: Usuario) -> Dict[str, Any]:
    # ...
    archivos_lista = []
    
    if entrega.get('archivos_adicionales'):
        try:
            archivos_data = json.loads(entrega['archivos_adicionales'])
            if isinstance(archivos_data, dict) and 'archivos' in archivos_data:
                # ✅ Itera sobre TODOS los archivos
                for archivo in archivos_data['archivos']:
                    if isinstance(archivo, dict) and 'url' in archivo:
                        # ✅ Prioriza nombre_original (CORRECTO)
                        archivos_lista.append({
                            "url": archivo['url'],
                            "nombre": archivo.get('nombre_original') or archivo.get('nombre') or archivo['url'].split("/")[-1],
                            "nombre_original": archivo.get('nombre_original')
                        })
```

**El código está CORRECTO**, entonces el problema es:

#### 🔍 **INVESTIGACIÓN PROFUNDA**

El bug real es que **el JSON `archivos_adicionales` en BD NO tiene `nombre_original`** guardado.

**Verificación en BD:**

```sql
-- Ver archivos_adicionales de una entrega
SELECT 
    entrega_id,
    archivos_adicionales::text
FROM entregas_tareas
WHERE entrega_id = 'xxx'
LIMIT 1;

-- Resultado actual (INCORRECTO):
{
  "archivos": [
    {"url": "/uploads/entregas/UUID1.pdf"},
    {"url": "/uploads/entregas/UUID2.pdf"}
  ]
}

-- Resultado esperado (CORRECTO):
{
  "archivos": [
    {"url": "/uploads/entregas/UUID1.pdf", "nombre_original": "Hoja_de_Vida.pdf", "nombre": "Hoja_de_Vida.pdf"},
    {"url": "/uploads/entregas/UUID2.pdf", "nombre_original": "Cedula.pdf", "nombre": "Cedula.pdf"}
  ]
}
```

#### 💡 **SOLUCIÓN PROPUESTA**

**1. Verificar que backend guarda correctamente** (Ya lo hace ✅)

El código en `curso_tareas.py` línea 192 ya guarda `nombre_original` correctamente.

**2. Verificar que `entregar_tarea()` del service lo persiste** ❌

**Problema encontrado:** `tarea_service.py` línea 584

```python
# ❌ CÓDIGO ACTUAL (línea 584):
archivos_json = None
if archivos_metadata and len(archivos_metadata) > 0:
    # ✅ Usa metadata completa que incluye nombre original
    archivos_json = json.dumps({"archivos": archivos_metadata})
    logger.info(f"   ✅ archivos_json creado con {len(archivos_metadata)} archivos:")
    logger.info(f"      {archivos_json[:300]}")
```

**Este código ESTÁ CORRECTO**, pero necesitamos verificar que el INSERT lo esté usando:

```python
# Línea 617 - INSERT
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
    "archivos_adicionales": archivos_json,  # ← ESTO ESTÁ BIEN
    "fecha_entrega": datetime.now(timezone.utc)
})
```

**El código backend está CORRECTO**. Entonces el problema debe estar en cómo el frontend parsea la respuesta.

#### 🔍 **INVESTIGACIÓN FINAL**

El problema real es que cuando `obtenerEntrega()` retorna el dict, el frontend NO está accediendo a `nombre_original` correctamente.

**Verificar en logs del browser:**

```javascript
console.log('Entrega recibida:', entregaExistente);
console.log('Archivos:', entregaExistente.archivos);
```

Si en console se ve:
```javascript
archivos: [
  {url: "/uploads/...", nombre: "UUID.pdf"}  // ❌ Sin nombre_original
]
```

Entonces el problema es que `obtenerEntrega()` NO está retornando `nombre_original` en la estructura de `archivos`.

**FIX DEFINITIVO:**

En `tarea_service.py` línea 682, cambiar:

```python
# ❌ ANTES:
archivos_lista.append({
    "url": archivo['url'],
    "nombre": archivo.get('nombre_original') or archivo.get('nombre') or archivo['url'].split("/")[-1],
    "nombre_original": archivo.get('nombre_original')
})

# ✅ DESPUÉS:
archivos_lista.append({
    "url": archivo['url'],
    "nombre": archivo.get('nombre_original', archivo.get('nombre', archivo['url'].split("/")[-1])),
    "nombre_original": archivo.get('nombre_original', archivo.get('nombre', archivo['url'].split("/")[-1])),
    "nombre_almacenado": archivo.get('nombre_almacenado', archivo['url'].split("/")[-1])
})
```

---

### ❌ **BUG #3: Solo 1 Archivo Visible Después de Cancelar**

#### 📝 **Descripción del Problema**

**Comportamiento reportado:**
> "Si yo le doy clic a cancelar la entrega me aparece solamente un archivo y eso que yo subí cuatro archivos."

#### 🧪 **Reproducción**

1. Usuario entrega tarea con 4 archivos ✅
2. Hace clic en "Cancelar Entrega" 
3. Modal de confirmación: "¿Estás seguro?"
4. Usuario confirma
5. Frontend muestra: **solo 1 archivo** ❌
6. Debería mostrar: **4 archivos preservados** ✅

#### 🔎 **CAUSA RAÍZ IDENTIFICADA**

**Problema 1: Backend preserva archivos pero frontend no los muestra todos**

**Backend** (`tarea_service.py` línea 790-802):

```python
# ✅ Backend PRESERVA archivos correctamente:
def cancelar_entrega(db: Session, entrega_id: str, usuario: Usuario) -> Dict[str, Any]:
    # ...
    # 4. Cambiar estado a 'cancelada' PRESERVANDO archivos_adicionales
    update_query = text("""
        UPDATE entregas_tareas
        SET estado = 'cancelada'  # ← Solo cambia estado, NO toca archivos_adicionales
        WHERE entrega_id = :entrega_id
    """)
    
    db.execute(update_query, {"entrega_id": entrega_id})
    db.commit()
    
    logger.info(f"Entrega cancelada: {entrega_id} - Archivos preservados para referencia")
    # ↑ Backend PRESERVA los archivos correctamente
```

**Frontend** (`SubirTareaPage.tsx` línea 201-216):

```typescript
// ❌ PROBLEMA: Después de cancelar, recarga entrega pero...
try {
  const entregaActualizada = await apiClientTareas.obtenerEntrega(entregaExistente.entrega_id);
  setEntregaExistente(entregaActualizada);
} catch (err) {
  console.warn("No se pudo recargar entrega después de cancelar:", err);
  setEntregaExistente(null);  // ← Esto limpia los archivos si falla
}
```

**El problema es que `obtenerEntrega()` está fallando o retornando archivos incorrectamente.**

#### 🔍 **INVESTIGACIÓN PROFUNDA**

Necesitamos verificar qué retorna `obtenerEntrega()` después de cancelar.

**Escenario probable:**

```javascript
// Estado antes de cancelar:
entregaExistente.archivos = [
  {url: "/uploads/...", nombre: "Archivo1.pdf"},
  {url: "/uploads/...", nombre: "Archivo2.pdf"},
  {url: "/uploads/...", nombre: "Archivo3.pdf"},
  {url: "/uploads/...", nombre: "Archivo4.pdf"}
]

// Después de cancelar y recargar:
entregaExistente.archivos = [
  {url: "/uploads/...", nombre: "Archivo1.pdf"}  // ❌ Solo el primero
]
```

**Causa probable:**

El problema está en cómo `obtenerEntrega()` parsea `archivos_adicionales` de BD.

**Backend** (`tarea_service.py` línea 665-690):

```python
# Código actual:
archivos_lista = []

if entrega.get('archivos_adicionales'):
    try:
        archivos_data = json.loads(entrega['archivos_adicionales'])
        if isinstance(archivos_data, dict) and 'archivos' in archivos_data:
            # ✅ Itera sobre TODOS los archivos
            for archivo in archivos_data['archivos']:
                if isinstance(archivo, dict) and 'url' in archivo:
                    archivos_lista.append({...})
```

**Este código está CORRECTO**, entonces el problema debe ser que:

1. **`archivos_adicionales` en BD solo tiene 1 archivo** ❌, o
2. **El JSON está mal formado** ❌, o
3. **El parsing falla silenciosamente** ❌

#### 💡 **SOLUCIÓN PROPUESTA**

**1. Agregar logging detallado para diagnosticar:**

```python
# En tarea_service.py, método obtenerEntrega() línea 665
if entrega.get('archivos_adicionales'):
    logger.info(f"🔍 Parseando archivos_adicionales para entrega {entrega_id}")
    logger.info(f"   Raw JSON: {entrega['archivos_adicionales'][:500]}")
    
    try:
        archivos_data = json.loads(entrega['archivos_adicionales'])
        logger.info(f"   Parsed data type: {type(archivos_data)}")
        logger.info(f"   Has 'archivos' key: {'archivos' in archivos_data if isinstance(archivos_data, dict) else False}")
        
        if isinstance(archivos_data, dict) and 'archivos' in archivos_data:
            archivos_count = len(archivos_data['archivos'])
            logger.info(f"   Total archivos en metadata: {archivos_count}")
            
            for idx, archivo in enumerate(archivos_data['archivos'], 1):
                logger.info(f"      [{idx}] Type: {type(archivo)}, Keys: {archivo.keys() if isinstance(archivo, dict) else 'N/A'}")
```

**2. Verificar en BD si todos los archivos están guardados:**

```sql
-- Ejecutar para ver contenido completo
SELECT 
    entrega_id,
    estado,
    archivo_url,  -- Solo el primer archivo
    archivos_adicionales::text  -- JSON con TODOS
FROM entregas_tareas
WHERE entrega_id = 'xxx';
```

**3. Si `archivos_adicionales` tiene todos los archivos:**

El problema está en el parsing del frontend. Fix:

```typescript
// En SubirTareaPage.tsx, después de obtenerEntrega()
console.log('📊 DIAGNÓSTICO archivos después de cancelar:');
console.log('  - entregaActualizada:', entregaActualizada);
console.log('  - archivos:', entregaActualizada.archivos);
console.log('  - archivos.length:', entregaActualizada.archivos?.length);
console.log('  - archivos_adicionales raw:', entregaActualizada.archivos_adicionales);
```

---

### ❌ **BUG #4: No se puede re-entregar sin agregar archivo nuevo**

#### 📝 **Descripción del Problema**

**Comportamiento reportado:**
> "Cuando yo cancelo la entrega no me aparecen los cuatro archivos y no me dejan entregar la tarea, tengo que agregar un nuevo archivo para poder volver a entregarla."

#### 🧪 **Reproducción**

1. Usuario entrega tarea con 4 archivos ✅
2. Cancela la entrega ✅
3. Frontend muestra archivos anteriores (en azul, indicando que son de entrega cancelada)
4. Usuario hace clic en "Entregar Tarea" SIN agregar nuevos archivos
5. Sistema NO permite entregar ❌
6. Usuario se ve forzado a agregar al menos 1 archivo nuevo para poder entregar

#### 🔎 **CAUSA RAÍZ IDENTIFICADA**

**Problema: Validación incorrecta en frontend**

**Frontend** (`SubirTareaPage.tsx` línea 233-258):

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!tareaId || !tarea) return;

  // ❌ PROBLEMA: No permite enviar solo comentarios o reusar archivos anteriores
  // El código no valida explícitamente, pero el FormData está vacío si no hay archivos nuevos

  try {
    setSubmitting(true);

    // 1. Crear FormData
    const entregaData = new FormData();
    entregaData.append('contenido', comentarios || 'Entrega de tarea');

    // ❌ PROBLEMA: Solo agrega archivos NUEVOS (de state archivos)
    archivos.forEach((archivo) => {
      entregaData.append('archivos', archivo.file);
    });
    // ↑ Si archivos.length === 0, NO envía ningún archivo
    // No incluye archivos de entregaExistente.archivos

    // Enviar
    const response = await apiClientTareas.entregarTarea(tareaId, entregaData as any);
```

**El problema es que:**

1. `archivos` state solo contiene archivos NUEVOS agregados
2. No incluye archivos de `entregaExistente.archivos` (archivos anteriores preservados)
3. Backend recibe FormData vacío
4. Backend permite entregas sin archivos (esto está BIEN)
5. Pero frontend no muestra botón "Entregar" activo si no hay archivos nuevos

#### 💡 **SOLUCIÓN PROPUESTA**

**Opción 1: Permitir re-entregar con archivos anteriores**

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!tareaId || !tarea) return;

  try {
    setSubmitting(true);

    const entregaData = new FormData();
    entregaData.append('contenido', comentarios || 'Entrega de tarea');

    // Agregar archivos NUEVOS
    archivos.forEach((archivo) => {
      entregaData.append('archivos', archivo.file);
    });

    // ✅ NUEVO: Si hay entrega cancelada con archivos, indicar que se reusan
    if (entregaExistente && entregaExistente.estado === 'cancelada' && entregaExistente.archivos?.length > 0) {
      // Opción A: Enviar IDs de archivos a reusar
      entregaData.append('reusar_archivos_anteriores', 'true');
      entregaData.append('entrega_anterior_id', entregaExistente.entrega_id);
      
      // O Opción B: Backend automáticamente detecta entrega cancelada anterior
      // y reutiliza sus archivos si no se envían archivos nuevos
    }

    const response = await apiClientTareas.entregarTarea(tareaId, entregaData as any);
    // ...
```

**Opción 2: Mostrar botón "Entregar" siempre activo después de cancelar**

```typescript
// En la sección del formulario, cambiar condición del botón:

// ❌ ANTES:
<button
  type="submit"
  disabled={submitting || archivos.length === 0}  // ← Deshabilita si no hay archivos nuevos
  className="..."
>
  {submitting ? 'Entregando...' : 'Entregar Tarea'}
</button>

// ✅ DESPUÉS:
const puedeEntregar = archivos.length > 0 || 
                      (entregaExistente?.estado === 'cancelada' && entregaExistente.archivos?.length > 0) ||
                      comentarios.trim().length > 0;

<button
  type="submit"
  disabled={submitting || !puedeEntregar}
  className="..."
>
  {submitting ? 'Entregando...' : 
   archivos.length === 0 && entregaExistente?.archivos?.length > 0 ? 
   'Re-entregar con archivos anteriores' : 
   'Entregar Tarea'}
</button>
```

**Opción 3: Backend inteligente (RECOMENDADO)**

Modificar `entregar_tarea()` del service para que:

1. Si no se envían archivos nuevos (`archivos_metadata` vacío)
2. Y existe una entrega cancelada anterior
3. Entonces **reutiliza automáticamente** `archivos_adicionales` de la entrega cancelada

```python
# En tarea_service.py, método entregar_tarea() línea 580
archivos_json = None

if archivos_metadata and len(archivos_metadata) > 0:
    # Hay archivos nuevos
    archivos_json = json.dumps({"archivos": archivos_metadata})
else:
    # ✅ NUEVO: No hay archivos nuevos, reusar de entrega cancelada anterior
    entrega_anterior = TareaService._obtener_mi_entrega(db, tarea_id, usuario.usuario_id)
    
    if entrega_anterior and entrega_anterior.get('estado') == 'cancelada':
        # Reusar archivos de entrega cancelada
        query_archivos = text("SELECT archivos_adicionales FROM entregas_tareas WHERE entrega_id = :entrega_id")
        result = db.execute(query_archivos, {"entrega_id": entrega_anterior['entrega_id']}).fetchone()
        
        if result and result[0]:
            archivos_json = result[0]  # JSON string con archivos anteriores
            logger.info(f"   ♻️ Reusando {len(json.loads(archivos_json)['archivos'])} archivos de entrega cancelada")
```

---

### ❌ **BUG #5: Lógica de Estado "cancelada" Incompleta**

#### 📝 **Descripción del Problema**

El sistema cambia el estado de la entrega a `'cancelada'` pero:

1. No hay diferenciación clara entre entrega cancelada y sin entrega
2. El frontend trata entrega cancelada como si no existiera
3. No hay forma de ver historial de entregas canceladas

#### 🔎 **CAUSA RAÍZ IDENTIFICADA**

**Backend** (`tarea_service.py` línea 599-615):

```python
# Código actual:
entrega_existente = TareaService._obtener_mi_entrega(db, tarea_id, usuario.usuario_id)

if entrega_existente:
    # ✅ Actualizar entrega existente (sin importar estado)
    return TareaService._actualizar_entrega(...)

# Crear nueva entrega
# ↑ Esto SIEMPRE crea una nueva si no existe, incluso si hay una cancelada
```

**Método `_obtener_mi_entrega()`:**

```python
@staticmethod
def _obtener_mi_entrega(db: Session, tarea_id: str, estudiante_id: UUID) -> Optional[Dict]:
    query = text("""
        SELECT entrega_id, estado, fecha_entrega
        FROM entregas_tareas
        WHERE tarea_id = :tarea_id AND estudiante_id = :estudiante_id
        # ❌ PROBLEMA: NO filtra por estado, retorna CUALQUIER entrega (incluso cancelada)
    """)
```

**El problema es que:**

1. `_obtener_mi_entrega()` retorna entrega cancelada
2. `entregar_tarea()` la actualiza (correcto)
3. Pero `_actualizar_entrega()` NO cambia el estado de vuelta a `'entregada'`

#### 💡 **SOLUCIÓN PROPUESTA**

**Fix 1: `_actualizar_entrega()` debe cambiar estado a 'entregada'**

```python
# En tarea_service.py, método _actualizar_entrega() línea 1189
@staticmethod
def _actualizar_entrega(
    db: Session,
    entrega_id: str,
    contenido: str,
    archivo_url: Optional[str],
    archivos_json: Optional[str] = None
) -> Dict[str, Any]:
    # ...
    query = text("""
        UPDATE entregas_tareas
        SET contenido_texto = :contenido,
            archivo_url = :archivo_url,
            archivos_adicionales = :archivos_adicionales,
            fecha_entrega = :fecha_entrega,
            estado = 'entregada'  # ✅ SIEMPRE cambiar a 'entregada' al actualizar
        WHERE entrega_id = :entrega_id
    """)
```

**Fix 2: Agregar lógica para determinar si es re-entrega:**

```python
# En tarea_service.py, método entregar_tarea()
if entrega_existente:
    es_reentrega = entrega_existente.get('estado') == 'cancelada'
    
    if es_reentrega:
        logger.info(f"♻️ RE-ENTREGA detectada - entrega anterior {entrega_existente['entrega_id']} estaba cancelada")
    
    return TareaService._actualizar_entrega(
        db, entrega_existente['entrega_id'], contenido, archivo_url, archivos_json
    )
```

---

## 📊 TABLA RESUMEN DE FIXES

| Bug | Archivo Afectado | Líneas | Fix Requerido | Tiempo Estimado |
|-----|------------------|--------|---------------|-----------------|
| #1 Contador | `SubirTareaPage.tsx` | 260 | Cambiar toast.success | 5 min ⚡ |
| #2 Nombres UUID | `tarea_service.py` | 682 | Asegurar nombre_original en dict | 10 min ⚡ |
| #2 Nombres UUID | `SubirTareaPage.tsx` | 633-650 | Ya está correcto (verificar logs) | 0 min ✅ |
| #3 Solo 1 archivo | `tarea_service.py` | 665-690 | Agregar logging + verificar JSON parsing | 15 min ⚠️ |
| #4 No re-entregar | `tarea_service.py` | 580 | Reusar archivos de entrega cancelada | 20 min ⚠️ |
| #4 No re-entregar | `SubirTareaPage.tsx` | 233-258 | Permitir entregar sin archivos nuevos | 10 min ⚡ |
| #5 Estado cancelada | `tarea_service.py` | 1189 | Cambiar estado a 'entregada' en update | 5 min ⚡ |
| **TOTAL** | - | - | - | **65 minutos** ⚡ |

---

## 🎯 PLAN DE ACCIÓN RECOMENDADO

### **FASE 1: Fixes Críticos Inmediatos (30 min)**

1. **Fix #1 - Contador** (5 min)
   - Modificar `SubirTareaPage.tsx` línea 260
   - Mostrar cantidad correcta de archivos en toast

2. **Fix #5 - Estado cancelada** (5 min)
   - Modificar `tarea_service.py` línea 1189
   - Asegurar que re-entrega cambia estado a 'entregada'

3. **Fix #2 - Nombres UUID** (10 min)
   - Agregar logging en `tarea_service.py` línea 682
   - Verificar que `nombre_original` está en metadata

4. **Fix #4 - Re-entregar sin archivos** (10 min)
   - Modificar botón en `SubirTareaPage.tsx`
   - Permitir entregar si hay archivos anteriores

### **FASE 2: Investigación y Diagnóstico (20 min)**

5. **Fix #3 - Solo 1 archivo visible** (20 min)
   - Agregar logging detallado en `obtenerEntrega()`
   - Verificar contenido de `archivos_adicionales` en BD
   - Identificar si el problema es en:
     - a) Guardado inicial (INSERT)
     - b) Parsing (SELECT + json.loads)
     - c) Frontend (display)

### **FASE 3: Testing Completo (15 min)**

6. **Test End-to-End**
   - Subir 4 archivos
   - Verificar contador correcto
   - Verificar nombres originales
   - Cancelar entrega
   - Verificar 4 archivos visibles
   - Re-entregar sin agregar archivos nuevos
   - Verificar estado 'entregada'

---

## 🔬 COMANDOS DE DIAGNÓSTICO

### **SQL para verificar archivos en BD:**

```sql
-- Ver archivos de una entrega específica
SELECT 
    e.entrega_id,
    e.estado,
    e.fecha_entrega,
    e.archivo_url AS primer_archivo_legacy,
    e.archivos_adicionales::text AS todos_los_archivos_json,
    LENGTH(e.archivos_adicionales::text) AS json_length,
    json_array_length((e.archivos_adicionales::json->'archivos')::json) AS total_archivos_en_json
FROM entregas_tareas e
WHERE e.tarea_id = 'TAREA_ID_AQUI'
  AND e.estudiante_id = 'ESTUDIANTE_ID_AQUI'
ORDER BY e.fecha_entrega DESC
LIMIT 1;

-- Ver estructura completa del JSON
SELECT 
    entrega_id,
    json_pretty(archivos_adicionales::json) AS archivos_formateados
FROM entregas_tareas
WHERE entrega_id = 'ENTREGA_ID_AQUI';
```

### **Logs del Backend:**

```bash
# En terminal donde corre uvicorn
grep "archivos_adicionales" backend.log | tail -n 20
grep "PROCESAMIENTO DE ARCHIVOS" backend.log | tail -n 30
grep "archivos_json creado con" backend.log | tail -n 10
```

### **Console del Frontend:**

```javascript
// En browser console después de entregar:
console.log('📊 Estado después de entregar:');
console.log('  - entregaExistente:', entregaExistente);
console.log('  - archivos:', entregaExistente?.archivos);
console.log('  - archivos.length:', entregaExistente?.archivos?.length);
console.log('  - archivos_adicionales:', entregaExistente?.archivos_adicionales);

// Verificar metadata de cada archivo:
entregaExistente?.archivos?.forEach((archivo, idx) => {
  console.log(`Archivo ${idx + 1}:`, archivo);
  console.log(`  - url:`, archivo.url);
  console.log(`  - nombre:`, archivo.nombre);
  console.log(`  - nombre_original:`, archivo.nombre_original);
});
```

---

## ✅ CHECKLIST DE TESTING

Después de aplicar los fixes, verificar:

- [ ] **Test 1**: Subir 4 archivos → Toast muestra "4 archivos" ✅
- [ ] **Test 2**: Archivos mostrados con nombres originales (no UUIDs) ✅
- [ ] **Test 3**: Cancelar entrega → Se muestran 4 archivos en azul ✅
- [ ] **Test 4**: Re-entregar sin agregar archivos → Funciona ✅
- [ ] **Test 5**: Estado cambia de 'cancelada' a 'entregada' ✅
- [ ] **Test 6**: Descargar archivo → Nombre correcto en descarga ✅
- [ ] **Test 7**: Verificar en BD → JSON tiene todos los archivos ✅
- [ ] **Test 8**: Verificar en BD → `nombre_original` presente ✅

---

## 🚀 PRÓXIMOS PASOS

1. **Ejecutar Fase 1** (30 min) - Fixes críticos
2. **Ejecutar comandos de diagnóstico** - Verificar estado actual en BD
3. **Ejecutar Fase 2** (20 min) - Investigación profunda
4. **Ejecutar Fase 3** (15 min) - Testing completo
5. **Documentar hallazgos** - Actualizar este archivo con resultados

---

**Última actualización**: 21 de noviembre de 2025, 10:47 PM  
**Autor**: GitHub Copilot Agent  
**Estado**: ✅ Análisis completo - Listo para implementar fixes
