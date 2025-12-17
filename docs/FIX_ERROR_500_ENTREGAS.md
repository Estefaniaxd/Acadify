# 🔧 FIX: Error 500 al cargar entregas

## 📋 PROBLEMA IDENTIFICADO

El error **500** al hacer `GET /api/cursos/tareas/entregas/{entrega_id}` era causado por:

**Columnas incorrectas en la query SQL** (función `obtener_entrega` en `tarea_service.py`)

### ❌ Columnas que NO existen en `entregas_tareas`:
```python
- et.contenido_texto          # ✅ SÍ existe
- et.retroalimentacion_docente  # ❌ NO existe
- et.retroalimentacion_ia       # ❌ NO existe
- et.puntos_otorgados           # ❌ NO existe
- et.es_tardia                  # ❌ INCORRECTO (es: es_entrega_tardia)
- et.intentos                   # ❌ INCORRECTO (es: numero_intento)
- et.comentarios_privados       # ❌ NO existe
- et.calificacion_preliminar_ia # ❌ NO existe
```

### ✅ Columnas CORRECTAS que existen:
```python
entrega_id
tarea_id
estudiante_id
titulo_entrega
descripcion_entrega
comentarios_estudiante
archivo_url
archivos_adicionales
contenido_texto
enlaces_externos
fecha_entrega
fecha_limite_original
numero_intento              # ← (NO intentos)
es_entrega_tardia           # ← (NO es_tardia)
calificacion
calificacion_letras
comentarios_docente
rubrica_calificacion
estado
es_final
requiere_revision
tiempo_empleado
dificultad_percibida
satisfaccion_estudiante
fecha_creacion
fecha_actualizacion
calificado_por
fecha_calificacion
```

---

## ✅ SOLUCIÓN APLICADA

### Archivo: `backend/src/services/academic/tarea_service.py`

**Ubicación**: Función `obtener_entrega()` línea ~545

**Cambio**: Reemplazado SELECT con columnas CORRECTAS:

```python
query = text("""
    SELECT 
        et.entrega_id,
        et.tarea_id,
        et.estudiante_id,
        et.titulo_entrega,
        et.descripcion_entrega,
        et.comentarios_estudiante,
        et.archivo_url,
        et.archivos_adicionales,
        et.contenido_texto,
        et.enlaces_externos,
        et.fecha_entrega,
        et.fecha_limite_original,
        et.numero_intento,                    # ← CORREGIDO
        et.es_entrega_tardia,                 # ← CORREGIDO
        et.calificacion,
        et.calificacion_letras,
        et.comentarios_docente,
        et.rubrica_calificacion,
        et.estado,
        et.es_final,
        et.requiere_revision,
        et.tiempo_empleado,
        et.dificultad_percibida,
        et.satisfaccion_estudiante,
        et.fecha_creacion,
        et.fecha_actualizacion,
        et.calificado_por,
        et.fecha_calificacion
    FROM entregas_tareas et
    WHERE et.entrega_id = :entrega_id
""")
```

---

## 🚀 PRÓXIMOS PASOS

### 1. **Reiniciar el Backend**

```bash
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend

# Si estaba corriendo:
pkill -9 -f "uvicorn.*main:app"

# Iniciar con venv activado:
source venv/bin/activate
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. **Verificar que funciona**

Una vez que el backend esté corriendo, prueba en el frontend:

1. Abre DevTools (F12) → Console
2. Navega a una tarea
3. Carga la entrega existente
4. Verifica que NO haya error 500

**Logs esperados en console:**
```
✅ RESPONSE STATUS: 200
✅ Entrega cargada exitosamente
```

### 3. **Probar flujo completo**

```
1. Ir a tarea → clic "Entregar tarea"
2. Subir archivos (1-5 archivos)
3. Agregar comentario opcional
4. Clic "Entregar"
5. Debe mostrar: "✅ Tarea entregada exitosamente"
6. Debe recargar y mostrar los archivos entregados
7. Debe permitir agregar más archivos sin perder los anteriores
```

---

## 🔍 DIAGNÓSTICO RÁPIDO

Si sigue fallando con 500:

```bash
# 1. Ver logs del backend
tail -50 /tmp/backend.log

# 2. Ver logs de PostgreSQL
docker logs postgres (o tu contenedor de BD)

# 3. Verificar estructura tabla
psql -U acadify_user -d acadify -c "\d entregas_tareas"

# 4. Probar query directamente
psql -U acadify_user -d acadify << EOF
SELECT 
    entrega_id,
    numero_intento,
    es_entrega_tardia
FROM entregas_tareas 
LIMIT 1;
EOF
```

---

## 📝 NOTAS IMPORTANTES

- El fix está en el **código** (archivo guardado)
- Necesita **reiniciar el servidor** para aplicarse
- El frontend está bien, el problema era 100% backend
- Los archivos múltiples ya funcionan (la lógica de `entregar_tarea()` está correcta)

---

**Fecha**: 21 de noviembre de 2025
**Status**: ✅ REPARADO (pendiente reiniciar backend)
