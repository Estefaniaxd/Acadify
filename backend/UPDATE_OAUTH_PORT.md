# 🔧 Actualización de Puerto - OAuth Redirect URI

## ✅ Cambio Realizado en Backend

El archivo `.env` del backend se actualizó de:
```
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

A:
```
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/google/callback
```

---

## 🔄 Pasos para Completar la Configuración

### 1. Reiniciar el Backend

El servidor backend necesita reiniciarse para cargar el nuevo valor:

```bash
# En la terminal donde está corriendo uvicorn:
# Presiona Ctrl+C

# Luego reinicia:
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Actualizar Google Cloud Console

**IMPORTANTE**: Debes actualizar la URI de redirección en Google Cloud Console:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto
3. Ve a **APIs & Services** → **Credentials**
4. Haz clic en tu **OAuth 2.0 Client ID** (el que tiene ID: `227277361049-a5204uua6dclcvp8g6lnn5ijpce6oqi0`)
5. En la sección **Authorized redirect URIs**:
   - **Elimina**: `http://localhost:3000/auth/google/callback`
   - **Agrega**: `http://localhost:5173/auth/google/callback`
6. Haz clic en **SAVE**

### 3. Probar el Flujo OAuth

Después de actualizar Google Cloud Console y reiniciar el backend:

1. Ve a `http://localhost:5173/login`
2. Haz clic en "Continuar con Google"
3. Autoriza la aplicación
4. Deberías ser redirigido a: `http://localhost:5173/auth/google/callback?code=...`
5. La página de callback procesará el código

---

## ✅ Checklist

- [x] Actualizar `.env` del backend (YA HECHO)
- [ ] Reiniciar servidor backend
- [ ] Actualizar URI en Google Cloud Console
- [ ] Probar flujo OAuth completo

---

## 🎯 URLs Correctas

| Componente | URL |
|------------|-----|
| Frontend | `http://localhost:5173` |
| Backend | `http://localhost:8000` |
| OAuth Login | `http://localhost:8000/auth/google/login` |
| OAuth Callback | `http://localhost:5173/auth/google/callback` |

---

## 🐛 Si Sigue Sin Funcionar

Verifica que:
1. El backend se haya reiniciado correctamente
2. La URI en Google Cloud Console esté exactamente como: `http://localhost:5173/auth/google/callback`
3. El frontend esté corriendo en el puerto 5173
4. No haya errores en la consola del navegador
