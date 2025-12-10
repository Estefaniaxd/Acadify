# 🔧 Configuración Final de OAuth - Redirect URI

## ✅ Configuración Correcta

### Backend `.env`
```bash
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

### Google Cloud Console

**Authorized redirect URIs:**
```
http://localhost:8000/api/v1/auth/google/callback
```

**Authorized JavaScript origins:**
```
http://localhost:5173
```

---

## 🔄 Flujo Correcto

1. Usuario hace clic en "Continuar con Google"
2. Redirige a Google para autorización
3. **Google redirige al BACKEND**: `http://localhost:8000/api/v1/auth/google/callback?code=XXX`
4. Backend procesa código y genera JWT
5. **Backend redirige al FRONTEND**: `http://localhost:5173/auth/google/callback?token=YYY`
6. Frontend procesa token y hace login automático
7. Frontend redirige al dashboard

---

## 📝 Pasos para Actualizar

### 1. Actualizar `.env` del Backend

Ya actualizado a:
```bash
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

### 2. Actualizar Google Cloud Console

1. Ve a [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Haz clic en tu OAuth 2.0 Client ID
3. En **"Authorized redirect URIs"**:
   - **Elimina**: `http://localhost:5173/auth/google/callback`
   - **Agrega**: `http://localhost:8000/api/v1/auth/google/callback`
4. **SAVE**

### 3. Reiniciar Backend

```bash
cd backend
# Ctrl+C para detener
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ Verificación

Después de actualizar:

1. Ve a `http://localhost:5173/login`
2. Haz clic en "Continuar con Google"
3. Deberías ver:
   - Redirección a Google ✓
   - Autorización en Google ✓
   - Redirección al backend (invisible) ✓
   - Redirección al frontend con token ✓
   - Login automático y redirección al dashboard ✓

---

## 🐛 Si Sigue Sin Funcionar

Verifica que:
1. El `.env` tiene la URI correcta del backend
2. Google Cloud Console tiene la URI correcta del backend
3. El backend se reinició después del cambio
4. No hay errores en la consola del navegador
