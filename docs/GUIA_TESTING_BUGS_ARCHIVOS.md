# ✅ GUÍA DE TESTING END-TO-END
## Bugs de Archivos en Entregas - 21 de noviembre de 2025

---

## 🎯 OBJETIVO

Verificar que **TODOS los bugs identificados** han sido corregidos:

1. ✅ Contador de archivos correcto
2. ✅ Nombres de archivos originales (no UUIDs)
3. ✅ Todos los archivos visibles después de cancelar
4. ✅ Re-entregar sin agregar archivos nuevos
5. ✅ Estado cambia de 'cancelada' a 'entregada'

---

## 🔧 PRE-REQUISITOS

### **Backend**
```bash
cd backend
# Asegurar que el servidor esté corriendo con los fixes aplicados
# Si no está corriendo, iniciarlo:
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

### **Frontend**
```bash
cd frontend
# Asegurar que el servidor esté corriendo
npm run dev
# Debería estar en http://localhost:5173
```

### **Base de Datos**
```bash
# Ejecutar script de diagnóstico ANTES del test
psql -U acadify_user -d acadify -f diagnostico_archivos_entregas.sql > diagnostico_antes.txt

# Guardar para comparar después
```

---

## 📝 TEST CASE #1: Subir 4 Archivos y Verificar Contador

### **Pasos:**

1. **Login** como estudiante
   - Email: `estudiante@test.com`
   - Password: `password123`

2. **Navegar a una tarea**
   - Dashboard → Cursos → Seleccionar curso
   - Tareas → Clic en tarea sin entregar

3. **Subir 4 archivos**
   - Preparar 4 archivos de prueba:
     - `Archivo_1_Test.pdf`
     - `Archivo_2_Test.docx`
     - `Archivo_3_Test.jpg`
     - `Archivo_4_Test.txt`
   - Hacer clic en "Añadir archivo"
   - Seleccionar los 4 archivos desde el explorador

4. **Agregar comentario** (opcional)
   - "Esta es mi entrega de prueba con 4 archivos"

5. **Hacer clic en "Entregar Tarea"**

### **Resultado Esperado:**

✅ **Toast muestra**: `"¡Tarea entregada con 4 archivos! ✅"`

❌ **NO debe mostrar**: `"¡Tarea entregada exitosamente!"` (sin mencionar cantidad)

### **Verificación en Browser Console:**

```javascript
// Abrir DevTools (F12) → Console
// Buscar línea con response.data
// Debería mostrar:
{
  success: true,
  message: "Tarea entregada exitosamente",
  data: {
    entrega_id: "...",
    archivos: [
      {url: "...", nombre: "Archivo_1_Test.pdf", nombre_original: "Archivo_1_Test.pdf"},
      {url: "...", nombre: "Archivo_2_Test.docx", nombre_original: "Archivo_2_Test.docx"},
      {url: "...", nombre: "Archivo_3_Test.jpg", nombre_original: "Archivo_3_Test.jpg"},
      {url: "...", nombre: "Archivo_4_Test.txt", nombre_original: "Archivo_4_Test.txt"}
    ]
  }
}
```

### **Verificación en Backend Logs:**

```bash
# En terminal del backend (uvicorn), buscar:
grep "archivos_json creado con" backend.log | tail -n 1

# Debería mostrar:
#    ✅ archivos_json creado con 4 archivos:
#       {"archivos":[...]}
```

---

## 📝 TEST CASE #2: Verificar Nombres Originales (No UUIDs)

### **Pasos:**

1. **Después de entregar** (continuar desde Test Case #1)
2. **Verificar lista de archivos** en la interfaz

### **Resultado Esperado:**

✅ **Debe mostrar**:
- 📎 Archivos subidos (4):
  - `Archivo_1_Test.pdf`
  - `Archivo_2_Test.docx`
  - `Archivo_3_Test.jpg`
  - `Archivo_4_Test.txt`

❌ **NO debe mostrar**:
- `a3b7c9d1-4e5f-6789-abcd-ef1234567890.pdf`
- UUIDs o nombres con caracteres aleatorios

### **Verificación en Browser Console:**

```javascript
// En Console, ejecutar:
console.log('Archivos mostrados:', entregaExistente.archivos);

// Debería mostrar:
[
  {url: "/uploads/...", nombre: "Archivo_1_Test.pdf", nombre_original: "Archivo_1_Test.pdf"},
  {url: "/uploads/...", nombre: "Archivo_2_Test.docx", nombre_original: "Archivo_2_Test.docx"},
  ...
]

// Verificar que NINGUNO tenga UUID como nombre
entregaExistente.archivos.forEach((archivo, idx) => {
  const esUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i.test(archivo.nombre);
  console.log(`Archivo ${idx + 1}: ${archivo.nombre} - Es UUID: ${esUUID ? '❌ MAL' : '✅ BIEN'}`);
});
```

### **Verificación en Backend Logs:**

```bash
# Buscar logs del parsing:
grep "PARSEANDO ARCHIVOS" backend.log | tail -n 50

# Debería mostrar:
#    🔍 PARSEANDO ARCHIVOS para entrega xxx:
#       📄 Archivo 1:
#          - nombre_original: Archivo_1_Test.pdf
#          ➡️ Nombre final elegido: Archivo_1_Test.pdf
#       📄 Archivo 2:
#          - nombre_original: Archivo_2_Test.docx
#          ➡️ Nombre final elegido: Archivo_2_Test.docx
#       ...
#    ✅ Total archivos procesados: 4
```

---

## 📝 TEST CASE #3: Cancelar Entrega y Verificar Archivos

### **Pasos:**

1. **Hacer clic en "Cancelar Entrega"**
2. **Confirmar** en el modal
3. **Verificar que aparecen los 4 archivos** en color AZUL (indicando entrega cancelada)

### **Resultado Esperado:**

✅ **Debe mostrar**:
- Mensaje: "Entrega cancelada. Tus archivos se mantienen disponibles, puedes entregar nuevamente."
- Lista de archivos (en azul/diferente color):
  - `Archivo_1_Test.pdf` con botones Descargar y Eliminar
  - `Archivo_2_Test.docx` con botones Descargar y Eliminar
  - `Archivo_3_Test.jpg` con botones Descargar y Eliminar
  - `Archivo_4_Test.txt` con botones Descargar y Eliminar

❌ **NO debe mostrar**:
- Solo 1 archivo
- Lista vacía
- Mensaje de error

### **Verificación en Browser Console:**

```javascript
// Después de cancelar, verificar estado:
console.log('Estado entrega:', entregaExistente.estado);  // Debe ser 'cancelada'
console.log('Archivos preservados:', entregaExistente.archivos);
console.log('Total archivos:', entregaExistente.archivos?.length);  // Debe ser 4

// ❌ Si es undefined o 0: BUG no corregido
// ✅ Si es 4: Fix exitoso
```

### **Verificación en Backend Logs:**

```bash
# Buscar logs de cancelación:
grep "Entrega cancelada" backend.log | tail -n 1

# Debería mostrar:
# Entrega cancelada: xxx por usuario yyy - Archivos preservados para referencia
```

---

## 📝 TEST CASE #4: Re-entregar SIN Agregar Archivos Nuevos

### **Pasos:**

1. **Después de cancelar** (continuar desde Test Case #3)
2. **NO agregar archivos nuevos**
3. **Opcional**: Agregar comentario: "Re-entrega usando archivos anteriores"
4. **Verificar texto del botón**:
   - Debe decir: "Re-entregar con archivos anteriores"
5. **Hacer clic en el botón**

### **Resultado Esperado:**

✅ **Debe permitir entregar** sin errores

✅ **Toast muestra**: `"¡Tarea entregada con 4 archivos! ✅"`

✅ **Backend logs muestran**:
```
♻️ REUSANDO 4 archivos de entrega cancelada xxx
🔄 RE-ENTREGA detectada - entrega xxx estaba cancelada
```

❌ **NO debe**:
- Deshabilitar el botón
- Mostrar error
- Requerir agregar archivos nuevos

### **Verificación en Browser Console:**

```javascript
// Verificar que el botón NO está disabled:
document.querySelector('button[type="submit"]').disabled  // Debe ser false

// Después de re-entregar:
console.log('Estado entrega:', entregaExistente.estado);  // Debe ser 'entregada'
console.log('Archivos:', entregaExistente.archivos.length);  // Debe ser 4
```

### **Verificación en BD:**

```sql
-- Ejecutar en psql:
SELECT 
    entrega_id,
    estado,
    jsonb_array_length((archivos_adicionales::jsonb->'archivos')::jsonb) AS total_archivos
FROM entregas_tareas
WHERE estudiante_id = 'TU_ESTUDIANTE_ID'
  AND tarea_id = 'TU_TAREA_ID'
ORDER BY fecha_entrega DESC
LIMIT 1;

-- Resultado esperado:
-- entrega_id | estado    | total_archivos
-- ---------- | --------- | --------------
-- xxx        | entregada | 4
```

---

## 📝 TEST CASE #5: Verificar Estado en BD

### **Pasos:**

1. **Ejecutar script SQL de diagnóstico DESPUÉS del test**:

```bash
psql -U acadify_user -d acadify -f diagnostico_archivos_entregas.sql > diagnostico_despues.txt
```

2. **Comparar resultados**:

```bash
diff diagnostico_antes.txt diagnostico_despues.txt
```

### **Resultado Esperado:**

✅ En `diagnostico_despues.txt` debe mostrar:

```
🔍 2. VERIFICANDO ESTRUCTURA JSON DE archivos_adicionales:

 entrega_id | estado    | total_archivos_en_json | diagnostico
------------+-----------+------------------------+----------------
 xxx        | entregada | 4                      | ✅ 4 archivos
```

✅ En la sección 3 (METADATA), debe mostrar:

```json
{
  "archivos": [
    {
      "url": "/uploads/entregas/...",
      "nombre": "Archivo_1_Test.pdf",
      "nombre_original": "Archivo_1_Test.pdf",
      "nombre_almacenado": "uuid.pdf"
    },
    ...
  ]
}
```

❌ **NO debe mostrar**:
- `total_archivos_en_json` = 1 (cuando subiste 4)
- `archivos` sin key `nombre_original`
- Estado = `'cancelada'` después de re-entregar

---

## 📊 CHECKLIST DE VERIFICACIÓN FINAL

Después de completar TODOS los test cases, verificar:

- [ ] **Test #1**: Toast muestra cantidad correcta (4 archivos) ✅
- [ ] **Test #2**: Archivos se muestran con nombres originales (no UUIDs) ✅
- [ ] **Test #2**: Browser console muestra `nombre_original` en todos los archivos ✅
- [ ] **Test #3**: Después de cancelar, se muestran 4 archivos (no solo 1) ✅
- [ ] **Test #3**: Backend logs confirman "Archivos preservados" ✅
- [ ] **Test #4**: Botón "Re-entregar con archivos anteriores" está habilitado ✅
- [ ] **Test #4**: Re-entregar funciona SIN agregar archivos nuevos ✅
- [ ] **Test #4**: Backend logs muestran "♻️ REUSANDO 4 archivos" ✅
- [ ] **Test #5**: BD muestra estado = 'entregada' después de re-entregar ✅
- [ ] **Test #5**: BD muestra `total_archivos_en_json` = 4 ✅
- [ ] **Test #5**: BD muestra `nombre_original` en todos los archivos ✅

---

## 🐛 TROUBLESHOOTING

### **Problema: Toast sigue mostrando "Archivos subidos: 1"**

**Solución**:
1. Verificar que el fix se aplicó en `SubirTareaPage.tsx` línea 248-260
2. Recargar el frontend (Ctrl+R con caché limpio: Ctrl+Shift+R)
3. Verificar en console que `response.data.archivos.length` es 4

### **Problema: Archivos se muestran como UUIDs**

**Solución**:
1. Verificar logs del backend: `grep "PARSEANDO ARCHIVOS" backend.log | tail -n 50`
2. Si logs muestran `nombre_original: null`: Problema en guardado inicial
3. Si logs muestran `nombre_original: "Archivo..."`: Problema en frontend
4. Ejecutar SQL diagnóstico para ver BD

### **Problema: Solo 1 archivo visible después de cancelar**

**Solución**:
1. Verificar logs: `grep "Total archivos procesados" backend.log | tail -n 1`
2. Si dice "Total archivos procesados: 1": Problema en BD (JSON mal guardado)
3. Si dice "Total archivos procesados: 4": Problema en frontend (display)
4. Ejecutar SQL diagnóstico sección 2 y 3

### **Problema: No puede re-entregar sin archivos nuevos**

**Solución**:
1. Verificar que fix se aplicó en `SubirTareaPage.tsx` línea 820-840
2. Verificar en console que `entregaExistente.archivos.length > 0`
3. Verificar logs backend: `grep "REUSANDO" backend.log | tail -n 1`

---

## 📞 CONTACTO

Si algún test falla:
1. Capturar screenshot del error
2. Copiar logs del backend (últimas 100 líneas)
3. Ejecutar script SQL diagnóstico
4. Documentar en issue de GitHub con etiqueta `bug-archivos-entregas`

---

**Última actualización**: 21 de noviembre de 2025, 11:20 PM  
**Versión**: 1.0.0  
**Estado**: ✅ Todos los fixes implementados - Listo para testing
