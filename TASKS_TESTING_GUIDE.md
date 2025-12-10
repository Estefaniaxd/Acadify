# Testing Guide: Task Creation Fix

**Objective**: Verify that the form-API mismatch fix works correctly  
**Duration**: ~15 minutes  
**Prerequisites**: Backend running on `localhost:8000`, Frontend on `localhost:5173`

---

## 🧪 Test Scenarios

### **Test 1: Happy Path - Create Task Successfully** ✅

**Steps**:
1. Open frontend: `http://localhost:5173`
2. Navigate to a course (e.g., `/clase/123/tareas`)
3. Click "Crear Nueva Tarea" button
4. Fill form:
   - **Título**: "Test Task 1"
   - **Descripción**: "This is a test task"
   - **Fecha Límite**: Tomorrow at 23:59
   - **Puntos Máximos**: 100
   - **Tipo**: "Ejercicios"
   - **Prioridad**: "Media"
5. Click "Crear Tarea" button

**Expected Results**:
- ✅ No error messages
- ✅ Modal closes after ~2 seconds
- ✅ Task appears in the list
- ✅ Browser console shows NO errors
- ✅ Status code 200/201 in Network tab

**Backend Check**:
```bash
# Check backend logs for success message
tail -f /path/to/backend.log | grep "Tarea creada"
```

**Database Check**:
```sql
SELECT titulo, fecha_limite, puntos_max FROM tareas 
WHERE titulo = 'Test Task 1' 
ORDER BY fecha_creacion DESC 
LIMIT 1;
```

---

### **Test 2: Validation - Missing Required Field** ❌

**Steps**:
1. Open create task form
2. Leave **Título** empty
3. Fill other fields as in Test 1
4. Try to submit form

**Expected Results**:
- ✅ Error message appears in form: "El título es obligatorio" (or similar)
- ✅ Modal stays open
- ✅ Form data is preserved
- ✅ No task created in database
- ✅ Status code 422 in Network tab

**Frontend Console Check**:
- Look for validation error log

---

### **Test 3: Validation - Invalid Date** ❌

**Steps**:
1. Open create task form
2. Fill title and other fields
3. Set **Fecha Límite** to a date in the PAST
4. Submit form

**Expected Results**:
- ✅ Error message appears: "La fecha límite debe ser en el futuro" (or similar)
- ✅ Modal stays open
- ✅ No task created

---

### **Test 4: Optional Fields** ✅

**Steps**:
1. Open create task form
2. Fill ONLY required fields:
   - Título: "Minimal Task"
   - Fecha Límite: Tomorrow at 23:59
3. Leave Descripción, Puntos, Tipo, Prioridad as defaults
4. Submit

**Expected Results**:
- ✅ Task created successfully
- ✅ Defaults are used:
  - Descripción: ""
  - Puntos: 100
  - Tipo: "ejercicios"
  - Prioridad: "media"

**Database Check**:
```sql
SELECT titulo, descripcion, puntos_max, tipo FROM tareas 
WHERE titulo = 'Minimal Task' 
LIMIT 1;
```

Expected output:
```
titulo       | Minimal Task
descripcion  | (empty or NULL)
puntos_max   | 100
tipo         | ejercicios
```

---

### **Test 5: Multiple Tasks** ✅

**Steps**:
1. Create 5 tasks with different titles and descriptions
2. Verify each one creates successfully
3. Check list shows all 5 tasks

**Expected Results**:
- ✅ All 5 tasks appear in list
- ✅ Each has correct data
- ✅ IDs are unique
- ✅ Timestamps are recent

---

### **Test 6: Type & Priority Fields** ✅

**Steps**:
1. Create tasks with different combinations:
   - Task A: tipo="ensayo", prioridad="alta"
   - Task B: tipo="proyecto", prioridad="baja"
   - Task C: tipo="investigacion", prioridad="media"
2. Check database values

**Database Check**:
```sql
SELECT titulo, tipo, prioridad FROM tareas 
WHERE titulo LIKE 'Task %' 
ORDER BY fecha_creacion DESC 
LIMIT 3;
```

Expected output shows correct tipo and prioridad values.

---

## 🔍 Debugging Checklist

If tests fail, check these in order:

### **Frontend Issues**

- [ ] **Browser Console**
  ```javascript
  // Check if form data is correct
  console.log("Form Data:", formData);
  
  // Check API response
  console.log("API Response:", response);
  ```

- [ ] **Network Tab**
  - Click "Crear Tarea"
  - Open Network tab
  - Look for POST request to `/api/cursos/tareas/{curso_id}/tareas`
  - Check:
    - Status code (should be 200 or 201)
    - Request payload (correct JSON?)
    - Response body (error message?)

- [ ] **Redux DevTools** (if using Redux)
  - Check form state before submit
  - Check API state after response

### **Backend Issues**

- [ ] **Check Backend Logs**
  ```bash
  # Look for request log
  grep "POST tarea curso" /path/to/backend.log
  
  # Look for validation errors
  grep "HTTPException\|ValidationError" /path/to/backend.log
  ```

- [ ] **Test Endpoint with cURL**
  ```bash
  curl -X POST http://localhost:8000/api/cursos/tareas/123/tareas \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
    -d '{
      "titulo": "cURL Test",
      "descripcion": "Testing with curl",
      "fecha_limite": "2025-12-31T23:59:59",
      "puntos_max": 100,
      "tipo": "ejercicios",
      "prioridad": "media"
    }' | jq
  ```

- [ ] **Database Connection**
  ```bash
  # Test database connection
  psql -U acadify_user -d acadify -c "SELECT version();"
  ```

- [ ] **Check Service Logic**
  ```python
  # Add debug logging in tarea_service.crear_tarea
  logger.debug(f"Received data: {titulo}, {descripcion}, {fecha_limite}")
  logger.debug(f"User: {usuario.usuario_id}")
  logger.debug(f"Database execute...")
  ```

### **API Client Issues**

- [ ] **Check API Client Initialization**
  ```typescript
  // In api.ts
  console.log("API Base URL:", this.baseURL);
  console.log("Token:", localStorage.getItem('access_token'));
  ```

- [ ] **Test API Client Directly**
  ```typescript
  import { apiClientTareas } from '@/modules/tareas/api';
  
  const result = await apiClientTareas.crearTarea('curso123', {
    titulo: 'Test from Console',
    descripcion: 'Test',
    fecha_limite: '2025-12-31T23:59:59',
  });
  
  console.log('Result:', result);
  ```

---

## 📊 Expected Behavior Chart

### Form Submission Flow

```
User fills form
    ↓
Clicks "Crear Tarea"
    ↓
Frontend validates (titulo, fecha_limite required)
    ↓
If valid → Send axios.post() with JSON
    ↓
Backend receives TareaCreateRequest
    ↓
Pydantic validates schema
    ↓
If valid → Insert into database
    ↓
Return 200 + task data
    ↓
Frontend: Close modal + Update list
    ↓
Success! ✅

If error at any step → Show error message + Don't close modal
```

---

## 🚨 Common Issues & Solutions

### Issue: "422 Unprocessable Entity"

**Cause**: Pydantic validation failed

**Solution**:
- Check the error message in response body
- Look for which field failed
- Verify data types (dates should be ISO format strings)

Example fix:
```typescript
// ❌ Wrong
fecha_limite: new Date().toString()

// ✅ Correct
fecha_limite: new Date().toISOString()
```

---

### Issue: "403 Forbidden"

**Cause**: User is not authorized (not a docente)

**Solution**:
- Verify user role in database
- Check JWT token is valid
- Ensure `current_user` is extracted correctly in route

---

### Issue: "500 Internal Server Error"

**Cause**: Backend exception

**Solution**:
- Check backend logs for stack trace
- Common causes:
  - Database connection failed
  - Missing required columns in INSERT
  - Foreign key constraint violation
  - Type conversion error

---

### Issue: "No response" / Request timeout

**Cause**: Backend not running or network issue

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/api/healthz

# Check network connectivity
ping localhost
```

---

## 📈 Performance Benchmarks

After fix is working, expected performance:

| Metric | Target | Acceptable |
|--------|--------|-----------|
| Form Submit Time | <500ms | <1000ms |
| Database Insert | <100ms | <500ms |
| Total Response Time | <1000ms | <2000ms |
| Concurrent Creates | 10+/sec | 5+/sec |

---

## ✅ Test Completion Checklist

- [ ] Test 1 (Happy Path) ✅
- [ ] Test 2 (Missing Field) ✅
- [ ] Test 3 (Invalid Date) ✅
- [ ] Test 4 (Optional Fields) ✅
- [ ] Test 5 (Multiple Tasks) ✅
- [ ] Test 6 (Type & Priority) ✅
- [ ] No browser console errors ✅
- [ ] Backend logs look clean ✅
- [ ] Database has correct data ✅
- [ ] UI updates correctly ✅

Once all pass: **PHASE 2 is COMPLETE** ✅

---

**Test Date**: ___________  
**Tested By**: ___________  
**Result**: ✅ PASS / ❌ FAIL  
**Notes**: ___________

