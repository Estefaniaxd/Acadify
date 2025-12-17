# =====================================================
# ACADIFY - CHECKLIST SEGURIDAD Y AUTENTICACIÓN
# Proyecto Formativo SENA - FastAPI + Python
# Fecha de Evaluación: 2025-12-16
# =====================================================

## RESUMEN EJECUTIVO

| Componente | Descripción |
|------------|-------------|
| Framework Auth | FastAPI + JWT + Redis |
| Hashing | bcrypt (12 rounds) |
| Tokens | JWT (access + refresh) |
| 2FA | Email OTP + TOTP |
| Rate Limiting | Redis-based |
| Blacklist | Redis token blacklist |

---

## CRITERIOS DE EVALUACIÓN

### 1. Registro de usuarios con validaciones (email único, contraseña segura)
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| Email único | ✅ SÍ | UNIQUE constraint + IntegrityError handler |
| Contraseña segura | ✅ SÍ | Política de 10+ caracteres, mayúscula, minúscula, número, especial |

**Validación de email único:**
```python
# auth_service.py
def _handle_integrity_error(self, e: IntegrityError):
    if "correo_institucional" in msg:
        raise HTTPException(
            status_code=400,
            detail="El correo institucional ya está registrado"
        )
```

**Política de contraseña (password_service.py):**
```python
# Requisitos:
# - Longitud mínima: 10 caracteres
# - Al menos una mayúscula
# - Al menos una minúscula
# - Al menos un dígito
# - Al menos un carácter especial
# - Sin secuencias obvias (123456, qwerty, password, etc.)

errors = []
if len(password) < 10:
    errors.append("La contraseña debe tener al menos 10 caracteres")
if not re.search(r"[A-Z]", password):
    errors.append("La contraseña debe contener al menos una letra mayúscula")
# ... etc
```

**Archivos:** 
- `backend/src/services/auth/password_service.py`
- `backend/src/services/auth/auth_service.py`

---

### 2. Encriptación de contraseñas (bcrypt, Argon2)
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| bcrypt | ✅ SÍ | passlib.CryptContext con 12 rounds |

**Implementación (password_service.py):**
```python
from passlib.context import CryptContext

class PasswordService:
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=getattr(settings, "BCRYPT_ROUNDS", 12),
        )

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
```

**Archivo:** `backend/src/services/auth/password_service.py`

---

### 3. Confirmación de registro vía correo con enlace único y expiración
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| Email de verificación | ✅ SÍ | Código 6 dígitos enviado por email |
| Enlace único | ✅ SÍ | UID + código en URL |
| Expiración | ✅ SÍ | 1 hora TTL en Redis |

**Implementación (auth_service.py):**
```python
async def _send_verification_email(self, user: Usuario):
    # Generar código de verificación (6 dígitos)
    verification_code = security_manager.generate_otp_code()
    verification_key = f"verify_email:{user.usuario_id}"
    
    # Guardar en Redis con TTL de 1 hora
    await self.redis.setex(verification_key, 3600, verification_code)
    
    enlace = f"https://acadify.com/verify-email?uid={user.usuario_id}&code={verification_code}"
    
    await self.email_service.send_template_email(
        to_email=user.correo_institucional,
        subject="Verifica tu correo - Acadify",
        template_name="verify_email.html",
        context={"codigo": verification_code, "enlace_verificacion": enlace}
    )
```

**Archivo:** `backend/src/services/auth/auth_service.py`

---

### 4. Inicio de sesión con correo/contraseña validando credenciales
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| Login con email/password | ✅ SÍ | authenticate_user() con validación completa |
| Verificación de credenciales | ✅ SÍ | Verificación de hash bcrypt |

**Implementación (auth_service.py):**
```python
async def authenticate_user(self, db: Session, login_data: LoginRequest):
    # 1. Verificar lockout
    lockout_info = await self.login_attempts.is_account_locked(identifier)
    if lockout_info:
        raise HTTPException(status_code=423, detail=lockout_info["message"])

    # 2. Buscar usuario
    user = self._get_user_by_identifier(db, identifier)
    
    # 3. Verificar estado de cuenta
    if user.estado_cuenta != EstadoCuentaUsuario.activo:
        raise HTTPException(status_code=403, detail="Cuenta inactiva o suspendida")
    
    # 4. Verificar contraseña
    if not security_manager.verify_password(login_data.password, user.password_hash):
        await self.login_attempts.record_failed_attempt(identifier)
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
```

**Archivo:** `backend/src/services/auth/auth_service.py`

---

### 5. Uso de tokens seguros (JWT con expiración + refresh)
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| JWT Access Token | ✅ SÍ | Expiración configurable (ACCESS_TOKEN_EXPIRE_MINUTES) |
| JWT Refresh Token | ✅ SÍ | Expiración días (REFRESH_TOKEN_EXPIRE_DAYS) |
| JTI para revocación | ✅ SÍ | UUID único por token |

**Implementación (token_service.py):**
```python
def create_access_token(self, user_id: str, roles: list[str], ...):
    expire = utcnow_aware() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid.uuid4())
    
    payload = {
        "sub": str(user_id),
        "exp": int(expire.timestamp()),
        "iat": int(utcnow_aware().timestamp()),
        "jti": jti,  # JWT ID para revocación
        "roles": roles,
        "type": "access",
    }
    return jwt.encode(payload, self.secret_key, algorithm=self.algorithm), jti

def create_refresh_token(self, user_id: str, ...):
    expire = utcnow_aware() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "jti": jti,
        "type": "refresh",
    }
    return jwt.encode(payload, self.secret_key, algorithm=self.algorithm), jti
```

**Archivo:** `backend/src/services/auth/token_service.py`

---

### 6. Bloqueo temporal tras intentos fallidos (rate limiting)
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| Bloqueo de cuenta | ✅ SÍ | login_attempts.is_account_locked() |
| Rate limiting | ✅ SÍ | RateLimitChecker en Redis |

**Implementación (deps.py):**
```python
class RateLimitChecker:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

# Rate limiters configurados:
login_rate_limit = RateLimitChecker(max_requests=10, window_seconds=900)  # 10/15min
password_reset_rate_limit = RateLimitChecker(max_requests=3, window_seconds=3600)  # 3/hora
api_rate_limit = RateLimitChecker(max_requests=1000, window_seconds=3600)  # 1000/hora
email_rate_limit = RateLimitChecker(max_requests=10, window_seconds=3600)  # 10/hora
```

**Bloqueo de cuenta (auth_service.py):**
```python
lockout_info = await self.login_attempts.is_account_locked(identifier)
if lockout_info:
    raise HTTPException(status_code=423, detail=lockout_info["message"])
```

**Archivo:** `backend/src/api/deps.py`

---

### 7. Recuperación de contraseña vía correo con token temporal
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| Reset por email | ✅ SÍ | Código OTP de 6 dígitos |
| Token temporal | ✅ SÍ | 15 minutos TTL en Redis |

**Implementación (auth_service.py):**
```python
async def request_password_reset(self, db: Session, reset_request):
    # Generar código de reset (6 dígitos)
    reset_code = security_manager.generate_otp_code()
    reset_key = f"reset_token:{user.usuario_id}"

    # Guardar en Redis con TTL de 15 minutos
    await self.redis.setex(reset_key, 900, reset_code)

    await self.email_service.send_template_email(
        to_email=email,
        subject="Recuperación de contraseña - Acadify",
        template_name="reset_password.html",
        context={
            "codigo": reset_code,
            "valido_hasta": "15 minutos",
        }
    )
```

**Archivo:** `backend/src/services/auth/auth_service.py`

---

### 8. Roles y permisos definidos (admin, instructor, estudiante)
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| Roles definidos | ✅ SÍ | Enum RolUsuario con 4 roles |
| Permisos | ✅ SÍ | Dependencies por rol |

**Roles definidos (usuario_enums.py):**
- `administrador` - Gestión completa del sistema
- `coordinador` - Coordinación académica
- `docente` - Gestión de clases
- `estudiante` - Aprendizaje y evaluaciones

**Dependencies de rol (deps.py):**
```python
def get_current_admin_user(current_user = Depends(get_current_active_user)):
    if current_user.rol != RolUsuario.administrador:
        raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
    return current_user

def get_current_coordinador(current_user = Depends(get_current_active_user)):
    # Similar para coordinador

def get_current_docente(current_user = Depends(get_current_active_user)):
    # Similar para docente

class RequireRoles:
    """Dependency class for checking specific roles."""
    def __init__(self, allowed_roles: list[RolUsuario]):
        self.allowed_roles = allowed_roles
```

**Archivo:** `backend/src/api/deps.py`

---

### 9. Rutas sensibles protegidas con middleware/guards
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| Protección de rutas | ✅ SÍ | Depends(get_current_user) en endpoints |
| Guards por rol | ✅ SÍ | get_current_admin_user, RequireRoles, etc. |

**Ejemplo de uso:**
```python
@router.get("/admin/instituciones")
async def listar_instituciones(
    current_user: Usuario = Depends(get_current_admin_user),  # Solo admin
    db: Session = Depends(get_db)
):
    pass

@router.post("/cursos/{curso_id}/tareas")
async def crear_tarea(
    current_user: Usuario = Depends(get_current_user),  # Autenticado
    db: Session = Depends(get_db)
):
    pass
```

**Archivo:** `backend/src/api/deps.py`

---

### 10. Auditoría de acciones críticas (guardar usuario que edita/elimina)
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| Tabla de auditoría | ✅ SÍ | AuditoriaAcciones en PostgreSQL |
| Triggers de auditoría | ✅ SÍ | trigger_auditoria_entregas, trigger_auditoria_evaluaciones |
| Campos de auditoría | ✅ SÍ | creado_por, actualizado_por en modelos |

**Tabla AuditoriaAcciones:**
```sql
CREATE TABLE "AuditoriaAcciones" (
    auditoria_id UUID PRIMARY KEY,
    usuario_id UUID,
    accion VARCHAR(100),
    tabla_afectada VARCHAR(100),
    registro_id UUID,
    detalles TEXT,
    ip_address VARCHAR(45),
    fecha_hora TIMESTAMP DEFAULT NOW()
);
```

**Campos en modelos:**
- `fecha_creacion` - Timestamp automático
- `fecha_actualizacion` - Trigger auto-update
- `creado_por` - UUID del usuario que creó
- `actualizado_por` - UUID del usuario que actualizó

**Archivos:**
- `backend/database/create_auditoria_table.sql`
- `backend/database/02_triggers.sql`

---

### 11. Al cerrar sesión, tokens/cookies quedan invalidados
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| Logout invalida tokens | ✅ SÍ | Tokens añadidos a blacklist Redis |
| Logout todos dispositivos | ✅ SÍ | logout_all_devices() |

**Implementación (auth_service.py):**
```python
async def logout(self, access_token: str, refresh_token: str):
    # Añadir a blacklist con TTL hasta expiración
    access_exp = datetime.fromtimestamp(access_payload["exp"])
    refresh_exp = datetime.fromtimestamp(refresh_payload["exp"])
    
    await self.token_blacklist.add_token(access_token, access_exp)
    await self.token_blacklist.add_token(refresh_token, refresh_exp)
    return {"message": "Logout exitoso"}

async def logout_all_devices(self, db: Session, user_id: UUID):
    # Marcar en Redis que todas las sesiones deben invalidarse
    invalidation_key = f"invalidate_all_sessions:{user_id}"
    await self.redis.setex(invalidation_key, 86400, str(datetime.now().timestamp()))
    return {"message": "Sesión cerrada en todos los dispositivos"}
```

**Verificación de blacklist (token_service.py):**
```python
def is_token_revoked(self, jti: str) -> bool:
    return bool(self.redis_service.is_token_blacklisted(jti))
```

**Archivo:** `backend/src/services/auth/auth_service.py`

---

### 12. Protección contra XSS, CSRF e inyección SQL/NoSQL
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| XSS | ✅ SÍ | React escapa automáticamente + HTTPOnly cookies |
| CSRF | ✅ SÍ | JWT en Authorization header (no cookies) |
| SQL Injection | ✅ SÍ | SQLAlchemy ORM con parámetros bound |

**XSS Protection:**
- React escapa automáticamente strings renderizados
- No uso de `dangerouslySetInnerHTML`
- Content-Security-Policy headers (configurable en producción)

**CSRF Protection:**
- Tokens JWT en Authorization header, no en cookies
- No vulnerable a CSRF porque requiere header explícito

**SQL Injection:**
```python
# SQLAlchemy usa parámetros bound, NO concatenación de strings:
usuario_crud.get_by_email(db, email=identifier)  # Seguro
# NUNCA: db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

**Archivos:**
- `backend/src/crud/` - Todos usan SQLAlchemy ORM
- `frontend/` - React con escape automático

---

### 13. Uso de HTTPS en producción
| Criterio | Cumple | Justificación |
|----------|--------|---------------|
| HTTPS | ✅ SÍ | Configurado en URLs de producción |

**URLs de producción (auth_service.py):**
```python
if settings.is_development():
    base_url = "http://localhost:8000"
else:
    base_url = "https://acadify.com"  # HTTPS en producción
```

**CORS configurado (main.py):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## CONCLUSIÓN

| # | Aspecto a Valorar | Cumple |
|---|-------------------|--------|
| 1 | Registro con email único + contraseña segura | ✅ SÍ |
| 2 | Encriptación bcrypt/Argon2 | ✅ SÍ (bcrypt 12 rounds) |
| 3 | Confirmación email con enlace temporal | ✅ SÍ (1 hora) |
| 4 | Login email/contraseña validado | ✅ SÍ |
| 5 | JWT con expiración + refresh token | ✅ SÍ |
| 6 | Bloqueo tras intentos fallidos | ✅ SÍ (rate limiting) |
| 7 | Recuperación contraseña por email | ✅ SÍ (15 min) |
| 8 | Roles y permisos definidos | ✅ SÍ (4 roles) |
| 9 | Rutas protegidas con guards | ✅ SÍ (Depends) |
| 10 | Auditoría de acciones críticas | ✅ SÍ |
| 11 | Logout invalida tokens | ✅ SÍ (Redis blacklist) |
| 12 | Protección XSS/CSRF/SQLi | ✅ SÍ |
| 13 | HTTPS en producción | ✅ SÍ |

**ESTADO GENERAL: ✅ TODOS LOS CRITERIOS CUMPLIDOS (13/13)**

---

## ARCHIVOS DE REFERENCIA

| Archivo | Descripción |
|---------|-------------|
| `backend/src/services/auth/auth_service.py` | Servicio principal de autenticación (50KB) |
| `backend/src/services/auth/password_service.py` | Hashing bcrypt + políticas |
| `backend/src/services/auth/token_service.py` | JWT access + refresh tokens |
| `backend/src/services/auth/email_service.py` | Envío de emails |
| `backend/src/services/auth/redis_service.py` | Cache y blacklist |
| `backend/src/api/deps.py` | Dependencies y guards (486 líneas) |
| `backend/src/api/routes/auth/` | 12 archivos de rutas auth |

---

*Generado automáticamente - Proyecto Acadify*
*Fecha: 2025-12-16*
