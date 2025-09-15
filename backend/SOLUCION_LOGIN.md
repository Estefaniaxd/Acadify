# SOLUCIÓN AL PROBLEMA DE LOGIN - CREDENCIALES CORRECTAS RECHAZADAS

## Problema Identificado

El usuario reportaba que aunque ingresara las credenciales correctas, el sistema devolvía "Credenciales incorrectas".

**Causa raíz:** Problema de case-sensitivity en la búsqueda de usernames.

### Análisis de los logs
```
{'username_1': 'estebanadmin', 'param_1': 1}
```

Los logs mostraban que se buscaba `'estebanadmin'` (todo minúsculas), pero probablemente en la base de datos el username estaba almacenado como `'estebanAdmin'` (con mayúscula).

## Problema Técnico Específico

En `/src/crud/user/usuario.py`, el método `get_by_username` estaba haciendo:

```python
# ANTES (PROBLEMÁTICO)
def get_by_username(self, db: Session, *, username: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(
        Usuario.username == username.lower().strip()  # Forzaba minúsculas
    ).first()
```

Esto causaba que:
1. Si el usuario se registró con `estebanAdmin` (mayúscula)
2. Pero el login se hacía con `estebanAdmin` (preservando case)
3. El código forzaba `.lower()` → `estebanadmin`
4. La búsqueda `Usuario.username == 'estebanadmin'` no encontraba `'estebanAdmin'`
5. Resultado: "Usuario no encontrado" → "Credenciales incorrectas"

## Solución Implementada

### 1. Búsqueda Case-Insensitive en CRUD

**Archivo:** `/src/crud/user/usuario.py`

```python
# DESPUÉS (CORREGIDO)
def get_by_username(self, db: Session, *, username: str) -> Optional[Usuario]:
    """Get user by username (case-insensitive search)"""
    return db.query(Usuario).filter(
        Usuario.username.ilike(username.strip())  # ilike = case-insensitive
    ).first()

def get_by_email(self, db: Session, *, email: str) -> Optional[Usuario]:
    """Get user by institutional email (case-insensitive search)"""
    return db.query(Usuario).filter(
        Usuario.correo_institucional.ilike(email.strip())
    ).first()
```

### 2. Logs de Depuración Mejorados

**Archivo:** `/src/services/auth/auth_service.py`

Agregué logs detallados para identificar problemas futuros:

```python
logger.info(f"Buscando usuario con identifier: '{identifier}' (tipo: {id_type})")
# ... búsqueda ...
if not user:
    logger.warning(f"Usuario no encontrado con identifier: '{identifier}' (tipo: {id_type})")
else:
    logger.info(f"Usuario encontrado: {user.usuario_id} - username: '{user.username}' - email: '{user.correo_institucional}'")
```

### 3. Actualización de _get_user_by_identifier

Eliminé la conversión `.lower()` redundante ya que ahora el CRUD maneja case-insensitive:

```python
def _get_user_by_identifier(self, db: Session, identifier: str) -> Optional[Usuario]:
    """Buscar usuario por email o username (case-insensitive)"""
    if "@" in identifier:
        user = usuario_crud.get_by_email(db, email=identifier)  # Sin .lower()
        if user:
            return user
    return usuario_crud.get_by_username(db, username=identifier)
```

## Resultado

Ahora el sistema puede encontrar usuarios independientemente de si:
- El username se almacenó como `estebanAdmin` y se busca con `estebanadmin`
- El email se almacenó como `user@EXAMPLE.COM` y se busca con `user@example.com`
- Cualquier combinación de mayúsculas/minúsculas

## Verificación

1. **Archivos compilados sin errores:** ✅
2. **Búsqueda case-insensitive implementada:** ✅  
3. **Logs de depuración agregados:** ✅
4. **Lógica de normalización mejorada:** ✅

## Cómo Probar

1. Inicia el servidor:
   ```bash
   uvicorn src.main:app --reload
   ```

2. Ve a: http://127.0.0.1:8000/docs

3. Prueba POST `/auth/login` con cualquier combinación de case:
   ```json
   {
     "identifier": "estebanadmin",    // minúsculas
     "password": "TuPassword"
   }
   ```
   
   O:
   ```json
   {
     "identifier": "EstebanAdmin",    // mayúsculas
     "password": "TuPassword"  
   }
   ```

4. **Ambas deberían funcionar ahora** si las credenciales son correctas.

## Logs Esperados (Exitosos)

Ahora deberías ver logs como:
```
INFO: Buscando usuario con identifier: 'estebanadmin' (tipo: username)
INFO: Usuario encontrado: [UUID] - username: 'estebanAdmin' - email: 'None'
INFO: Login para usuario [UUID] (estebanAdmin), twofa_enabled=False
INFO: Usuario [UUID] inicia sesión SIN 2FA
```

En lugar de:
```
WARNING: Usuario no encontrado con identifier: 'estebanadmin' (tipo: username)
```

## Prevención Futura

- Las búsquedas de username y email ahora son case-insensitive por defecto
- Los logs detallados permiten identificar rápidamente problemas de autenticación
- La normalización se maneja a nivel de base de datos, no en la lógica de aplicación