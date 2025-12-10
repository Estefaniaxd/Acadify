# 🚀 Guía Rápida: Configurar OAuth 2.0

## Paso 1: Agregar Credenciales al .env

Ejecuta el script de configuración:

```bash
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend
./setup_oauth.sh
```

O agrega manualmente estas líneas al archivo `.env`:

```bash
# Google OAuth 2.0
GOOGLE_CLIENT_ID=REPLACE_WITH_GOOGLE_CLIENT_IDs.googleusercontent.com
GOOGLE_CLIENT_SECRET=REPLACE_WITH_GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
ENABLE_OAUTH=true
```

## Paso 2: Reiniciar el Backend

```bash
# Detén el servidor actual (Ctrl+C)
# Luego reinicia:
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Paso 3: Verificar en Swagger

Abre: `http://localhost:8000/docs`

Busca la sección **"OAuth - Google"** y verifica los 5 endpoints.

## Paso 4: Probar el Flujo OAuth

Abre en tu navegador:
```
http://localhost:8000/api/v1/auth/google/login
```

Deberías ser redirigido a Google para autorizar la aplicación.

---

## 📋 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/auth/google/login` | GET | Iniciar login con Google |
| `/auth/google/callback` | GET | Callback de Google |
| `/auth/google/link` | POST | Vincular cuenta (requiere auth) |
| `/auth/google/unlink` | DELETE | Desvincular cuenta (requiere auth) |
| `/auth/google/status` | GET | Ver estado (requiere auth) |

---

## 🔍 Verificar en Base de Datos

```sql
SELECT * FROM "OAuthProvider" WHERE provider = 'google';
```

---

## ✅ Checklist de Verificación

- [ ] Credenciales agregadas al `.env`
- [ ] Backend reiniciado
- [ ] Endpoints visibles en Swagger
- [ ] Flujo OAuth funciona (redirige a Google)
- [ ] Registro en base de datos creado

---

**¿Problemas?** Revisa el [walkthrough completo](file:///home/arch/.gemini/antigravity/brain/7c5d4ae5-387c-4e7b-8a31-04d3c6df04c9/walkthrough.md) para troubleshooting.
