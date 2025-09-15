# SOLUCIÓN A ERRORES DE LOGIN - FASE 2

## Problemas Identificados en los Logs

### 1. Error de bcrypt
```
(trapped) error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'
```

**Causa:** Falta la dependencia `bcrypt` o versión incompatible con `passlib`.

### 2. Error del CRUD
```
Error en login: type object 'Usuario' has no attribute 'id'
```

**Causa:** El CRUD base usa `self.model.id` pero el modelo `Usuario` usa `usuario_id` como primary key.

## Soluciones Implementadas

### 1. Dependencias Actualizadas

**Archivo:** `requirements.txt`

Agregué las dependencias faltantes:
```
passlib[bcrypt]==1.7.4    # En lugar de solo passlib
bcrypt==4.0.1             # Dependencia explícita
python-jose[cryptography]==3.3.0  # Para JWT tokens
redis==5.0.1              # Para Redis async
aiosmtplib==3.0.1        # Para envío de emails async
jinja2==3.1.2            # Para templates de email
pyotp==2.9.0             # Para TOTP 2FA
```

### 2. CRUD Corregido

**Archivo:** `/src/crud/user/usuario.py`

Agregué override del método `get` para usar `usuario_id`:

```python
class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    """CRUD operations for Usuario model"""
    
    # ===============================
    # Override Base Methods for usuario_id
    # ===============================
    
    def get(self, db: Session, id: UUID) -> Optional[Usuario]:
        """Get user by usuario_id (override base method)"""
        return db.query(Usuario).filter(Usuario.usuario_id == id).first()
    
    def exists(self, db: Session, *, id: UUID) -> bool:
        """Check if user exists by usuario_id"""
        return db.query(Usuario).filter(Usuario.usuario_id == id).first() is not None
```

## Análisis de los Logs Exitosos

Los logs muestran que ahora la búsqueda SÍ está funcionando correctamente:

```sql
SELECT ... FROM "Usuario" WHERE "Usuario".username ILIKE 'estebanAdmin' LIMIT 1
```

- ✅ Usa `ILIKE` (case-insensitive)
- ✅ Busca `'estebanAdmin'` (preserva case original)
- ✅ La consulta se ejecuta correctamente

## Instrucciones para Probar

### 1. Reinstalar Dependencias

```bash
cd /home/esteban/Acadify/backend
pip install -r requirements.txt
```

### 2. Verificar que Redis está funcionando

```bash
redis-cli ping
```

Debería responder: `PONG`

### 3. Iniciar el servidor

```bash
uvicorn src.main:app --reload
```

### 4. Probar login

- URL: http://127.0.0.1:8000/docs
- Endpoint: POST `/auth/login`
- JSON:
```json
{
  "identifier": "estebanAdmin",
  "password": "TuPasswordReal"
}
```

## Logs Esperados (Exitosos)

```
INFO: Buscando usuario con identifier: 'estebanAdmin' (tipo: username)
INFO: Usuario encontrado: [UUID] - username: 'estebanAdmin' - email: 'None'
INFO: Login para usuario [UUID] (estebanAdmin), twofa_enabled=False
INFO: Usuario [UUID] inicia sesión SIN 2FA
```

## Si Aún Hay Problemas

### 1. Verificar usuario en base de datos

```sql
SELECT usuario_id, username, correo_institucional, rol, estado_cuenta 
FROM "Usuario" 
WHERE username ILIKE 'estebanadmin';
```

### 2. Verificar password hash

El problema podría ser que el password almacenado no coincide. Puedes verificar:

```python
from src.utils.security import security_manager

# Verificar si el hash coincide
password_correcto = security_manager.verify_password("TuPassword", hash_en_db)
print(f"Password válido: {password_correcto}")
```

### 3. Si el usuario no existe

Debes registrar el usuario primero usando el endpoint POST `/auth/register`.

## Próximos Pasos

1. **Instalar dependencias actualizadas**
2. **Verificar que Redis esté corriendo**  
3. **Probar login con credenciales exactas de la base de datos**
4. **Revisar logs para confirmar que usuario se encuentra**

Si persisten problemas, necesitaríamos ver:
- Estado exacto de la base de datos (qué usuarios existen)
- Logs completos del intento de login
- Verificación de que Redis está funcionando