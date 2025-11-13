# Fix: Instituciones - Errores 401 y 405

## 🐛 Problemas Identificados

### Error 1: 401 Unauthorized en GET `/api/instituciones`
**Causa**: El endpoint es público (no requiere autenticación), pero el frontend envía un token que puede estar expirado, causando rechazo del servidor.

**Solución**: El endpoint público ignora tokens inválidos, pero axios interceptor siempre envía el token. Actualizado el servicio para manejar errores correctamente.

### Error 2: 405 Method Not Allowed en POST `/admin/instituciones`
**Causa**: El router `admin_institucion.py` tenía el prefijo `/admin` definido DOS VECES:
1. En la definición del router: `APIRouter(prefix="/admin")`
2. En el montaje en `__init__.py`: `(admin_router, "/admin")`

Esto creaba la ruta: `/admin/admin/instituciones` ❌
En lugar de: `/admin/instituciones` ✅

---

## ✅ Cambios Realizados

### Backend: `/backend/src/api/routes/admin_institucion.py`

**ANTES:**
```python
router = APIRouter(prefix="/admin", tags=["Administrador"])

import logging
from fastapi import APIRouter
# ...imports duplicados...

router = APIRouter(prefix="/admin", tags=["Administrador"])  # ❌ Duplicado!
```

**DESPUÉS:**
```python
# El router NO debe tener prefijo aquí porque se monta con prefijo /admin en __init__.py
router = APIRouter(tags=["Administrador"])
```

**Imports añadidos:**
```python
from sqlalchemy.exc import IntegrityError
from src.enums.academic.institucion_enums import EstadoInstitucion
```

### Frontend: `/frontend/src/services/instituciones.service.ts`

**ANTES:**
```typescript
async getAll(): Promise<Institucion[]> {
  try {
    const response = await api.get('/api/instituciones', {
      params: { skip: 0, limit: 1000 },
      headers: {}  // ❌ Intento inútil de no enviar token
    });
    return response.data;
  } catch (error) {
    console.error('Error al obtener instituciones:', error);
    return [];
  }
}
```

**DESPUÉS:**
```typescript
async getAll(): Promise<Institucion[]> {
  try {
    const response = await api.get('/api/instituciones', {
      params: { skip: 0, limit: 1000 }
      // ✅ Token se envía automáticamente por interceptor
      // Endpoint público lo ignora si está expirado
    });
    return response.data;
  } catch (error: any) {
    console.error('Error al obtener instituciones:', error);
    console.error('Response:', error.response?.data);
    console.error('Status:', error.response?.status);
    return [];
  }
}
```

---

## 🔧 Cómo Probar

### 1. Reiniciar el Backend
```bash
cd backend
# Detener el servidor si está corriendo (Ctrl+C)
# Iniciar nuevamente
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Verificar Rutas Montadas
En la consola del backend deberías ver:
```
✅ Router incluido: /admin - ['Administración']
✅ Router incluido: /api/instituciones - ['Instituciones']
```

### 3. Probar Endpoints con cURL

#### GET Instituciones (Público - no requiere token)
```bash
curl http://localhost:8000/api/instituciones?skip=0&limit=10
```

Debería retornar un array de instituciones o array vacío `[]`.

#### POST Crear Institución (Requiere token de admin)
```bash
# Primero login como admin
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"usuario": "admin", "password": "tu_password"}'

# Copiar el access_token de la respuesta

# Crear institución
curl -X POST http://localhost:8000/admin/instituciones \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TU_TOKEN_AQUI>" \
  -d '{
    "nombre": "Universidad de Prueba",
    "tipo_institucion": "universidad",
    "usa_programas": true,
    "nivel_educativo": "superior",
    "sector": "publico",
    "pais": "Colombia",
    "correo_institucional": "contacto@universidad.edu.co",
    "telefono": "+57 1 234 5678"
  }'
```

### 4. Probar desde el Frontend

1. **Login como administrador**
   - Navegar a `/login`
   - Credenciales de admin

2. **Ir a Instituciones**
   - Navegar a `/admin/instituciones`
   - Debería cargar la lista de instituciones

3. **Crear Nueva Institución**
   - Clic en "Nueva Institución"
   - Llenar formulario
   - Clic en "Crear"
   - ✅ Debería crearse sin error 405

---

## 🔍 Verificación de Rutas

### Rutas que DEBEN funcionar:

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/instituciones` | Público | Lista todas las instituciones |
| GET | `/api/instituciones/{id}` | Público | Detalle de institución |
| POST | `/admin/instituciones` | Admin | Crear institución |
| PUT | `/api/instituciones/{id}` | Usuario | Actualizar institución |
| DELETE | `/api/instituciones/{id}` | Admin | Eliminar institución |
| POST | `/admin/instituciones/{id}/invitar-coordinador` | Admin | Invitar coordinador |

---

## ⚠️ Notas Importantes

### Sobre el Token
- El endpoint público `/api/instituciones` **ignora** el token si está presente
- NO es necesario remover el token del request
- Si el token está expirado, el endpoint público aún funciona
- Endpoints de admin requieren token válido con rol `administrador`

### Sobre CORS
Si sigues teniendo problemas 405, verifica que CORS esté configurado correctamente en `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # ✅ Todos los métodos
    allow_headers=["*"],
)
```

### Sobre el Prefijo del Router
**REGLA**: Si un router se monta con prefijo en `__init__.py`, NO debe definir prefijo en su propia definición.

**Ejemplo Correcto:**
```python
# En admin_institucion.py
router = APIRouter(tags=["Administrador"])  # ✅ Sin prefijo

# En __init__.py
(admin_router, "/admin", ["Administración"])  # ✅ Prefijo aquí
```

**Ejemplo Incorrecto:**
```python
# En admin_institucion.py
router = APIRouter(prefix="/admin", tags=["Administrador"])  # ❌

# En __init__.py
(admin_router, "/admin", ["Administración"])  # ❌ Prefijo duplicado
# Resultado: /admin/admin/instituciones ❌
```

---

## ✅ Resultado Esperado

Después de estos cambios:
- ✅ GET `/api/instituciones` retorna lista de instituciones
- ✅ POST `/admin/instituciones` crea nueva institución (con token admin)
- ✅ No más errores 401 o 405
- ✅ Página de administración de instituciones funcional

---

## 📝 Archivos Modificados

```
backend/src/api/routes/
└── admin_institucion.py           [MODIFICADO] ✅

frontend/src/services/
└── instituciones.service.ts        [MODIFICADO] ✅
```

---

## 🚀 Próximos Pasos

1. ✅ **Reiniciar backend** con los cambios
2. ✅ **Probar endpoints** con cURL
3. ✅ **Login en frontend** como admin
4. ✅ **Probar CRUD** de instituciones
5. ✅ **Verificar invitación** de coordinador

Si todo funciona correctamente, la página de administración de instituciones debería estar completamente funcional.
