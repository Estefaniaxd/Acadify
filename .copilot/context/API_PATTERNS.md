# 🛣️ API Patterns - Acadify

> **Patrones reutilizables para endpoints FastAPI**

---

## 📋 Patrón Completo: Endpoint CRUD

### **1. Endpoint CREATE (POST)**

```python
# src/api/routers/cursos.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, get_current_user
from src.models.usuario import Usuario, RolUsuario
from src.schemas.curso import CursoCreate, CursoResponse
from src.services.curso_service import CursoService

router = APIRouter(prefix="/api/cursos", tags=["cursos"])

@router.post("/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def crear_curso(
    data: CursoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> CursoResponse:
    """Crea un nuevo curso.

    Permisos: ADMIN, DOCENTE

    Args:
        data: Datos del curso a crear
        db: Sesión de base de datos
        current_user: Usuario autenticado

    Returns:
        Curso creado con todos los campos

    Raises:
        HTTPException 403: Si el usuario no tiene permisos
        HTTPException 404: Si la institución no existe
        HTTPException 400: Si los datos son inválidos
    """
    # Verificar permisos
    if current_user.rol not in [RolUsuario.ADMIN, RolUsuario.DOCENTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear cursos"
        )

    service = CursoService(db)
    curso = await service.crear_curso(data, docente_id=current_user.id)
    return curso
```

---

### **2. Endpoint READ (GET Single)**

```python
@router.get("/{curso_id}", response_model=CursoResponse)
async def obtener_curso(
    curso_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> CursoResponse:
    """Obtiene un curso por ID.

    Permisos: Todos los usuarios autenticados

    Args:
        curso_id: ID del curso
        db: Sesión de base de datos
        current_user: Usuario autenticado

    Returns:
        Curso con todos los detalles

    Raises:
        HTTPException 404: Si el curso no existe
    """
    service = CursoService(db)
    curso = await service.obtener_curso(curso_id)

    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {curso_id} no encontrado"
        )

    return curso
```

---

### **3. Endpoint LIST (GET Collection con Paginación)**

```python
from typing import List
from fastapi import Query

@router.get("/", response_model=List[CursoResponse])
async def listar_cursos(
    skip: int = Query(0, ge=0, description="Offset para paginación"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    institucion_id: int | None = Query(None, description="Filtrar por institución"),
    activo: bool | None = Query(None, description="Filtrar por estado activo"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> List[CursoResponse]:
    """Lista cursos con filtros y paginación.

    Permisos: Todos los usuarios autenticados

    Args:
        skip: Número de registros a omitir
        limit: Número máximo de registros a retornar
        institucion_id: Filtro opcional por institución
        activo: Filtro opcional por estado
        db: Sesión de base de datos
        current_user: Usuario autenticado

    Returns:
        Lista de cursos que cumplen los filtros
    """
    service = CursoService(db)
    cursos = await service.listar_cursos(
        skip=skip,
        limit=limit,
        institucion_id=institucion_id,
        activo=activo
    )
    return cursos
```

---

### **4. Endpoint UPDATE (PATCH/PUT)**

```python
from src.schemas.curso import CursoUpdate

@router.patch("/{curso_id}", response_model=CursoResponse)
async def actualizar_curso(
    curso_id: int,
    data: CursoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> CursoResponse:
    """Actualiza un curso existente.

    Permisos: ADMIN o DOCENTE del curso

    Args:
        curso_id: ID del curso a actualizar
        data: Datos a actualizar (campos opcionales)
        db: Sesión de base de datos
        current_user: Usuario autenticado

    Returns:
        Curso actualizado

    Raises:
        HTTPException 404: Si el curso no existe
        HTTPException 403: Si el usuario no tiene permisos
    """
    service = CursoService(db)
    curso = await service.obtener_curso(curso_id)

    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {curso_id} no encontrado"
        )

    # Verificar permisos (admin o docente del curso)
    if current_user.rol != RolUsuario.ADMIN and curso.docente_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este curso"
        )

    curso_actualizado = await service.actualizar_curso(curso_id, data)
    return curso_actualizado
```

---

### **5. Endpoint DELETE**

```python
@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_curso(
    curso_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> None:
    """Elimina un curso (soft delete).

    Permisos: Solo ADMIN

    Args:
        curso_id: ID del curso a eliminar
        db: Sesión de base de datos
        current_user: Usuario autenticado

    Raises:
        HTTPException 404: Si el curso no existe
        HTTPException 403: Si el usuario no es admin
    """
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden eliminar cursos"
        )

    service = CursoService(db)
    curso = await service.obtener_curso(curso_id)

    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {curso_id} no encontrado"
        )

    await service.eliminar_curso(curso_id)
```

---

## 🎯 Patrón: Endpoint con Relaciones (Nested Resources)

### **Ejemplo: Obtener estudiantes de un curso**

```python
@router.get("/{curso_id}/estudiantes", response_model=List[UsuarioResponse])
async def obtener_estudiantes_curso(
    curso_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> List[UsuarioResponse]:
    """Obtiene la lista de estudiantes inscritos en un curso.

    Permisos: ADMIN, DOCENTE del curso, o ESTUDIANTE inscrito

    Args:
        curso_id: ID del curso
        skip: Offset para paginación
        limit: Límite de resultados
        db: Sesión de base de datos
        current_user: Usuario autenticado

    Returns:
        Lista de estudiantes inscritos

    Raises:
        HTTPException 404: Si el curso no existe
        HTTPException 403: Si el usuario no tiene permisos
    """
    service = CursoService(db)
    curso = await service.obtener_curso(curso_id)

    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {curso_id} no encontrado"
        )

    # Verificar permisos
    es_admin = current_user.rol == RolUsuario.ADMIN
    es_docente = curso.docente_id == current_user.id
    es_estudiante = await service.es_estudiante_curso(curso_id, current_user.id)

    if not (es_admin or es_docente or es_estudiante):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver los estudiantes de este curso"
        )

    estudiantes = await service.obtener_estudiantes(curso_id, skip=skip, limit=limit)
    return estudiantes
```

---

## 🔒 Patrón: Autorización con Dependency

### **Dependency reutilizable para verificar permisos**

```python
# src/core/dependencies.py
from typing import Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.curso import Curso
from src.models.usuario import Usuario, RolUsuario
from src.core.dependencies import get_db, get_current_user

def require_admin(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """Requiere que el usuario sea administrador."""
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere permisos de administrador"
        )
    return current_user

def require_docente_or_admin(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """Requiere que el usuario sea docente o admin."""
    if current_user.rol not in [RolUsuario.ADMIN, RolUsuario.DOCENTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere permisos de docente o administrador"
        )
    return current_user

async def require_docente_curso(
    curso_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Curso:
    """Verifica que el usuario sea docente del curso o admin."""
    curso = await db.get(Curso, curso_id)

    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {curso_id} no encontrado"
        )

    es_admin = current_user.rol == RolUsuario.ADMIN
    es_docente = curso.docente_id == current_user.id

    if not (es_admin or es_docente):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres docente de este curso"
        )

    return curso

# Uso en endpoint:
@router.patch("/{curso_id}")
async def actualizar_curso(
    data: CursoUpdate,
    curso: Curso = Depends(require_docente_curso)  # ← Autorización automática
):
    # 'curso' ya está validado y autorizado
    service = CursoService(db)
    return await service.actualizar_curso(curso.id, data)
```

---

## 📊 Patrón: Response con Metadatos (Paginación)

```python
from pydantic import BaseModel

class PaginatedResponse(BaseModel):
    """Response con metadatos de paginación."""
    items: List[CursoResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

@router.get("/", response_model=PaginatedResponse)
async def listar_cursos_paginados(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse:
    """Lista cursos con metadatos de paginación."""
    service = CursoService(db)

    # Obtener items
    items = await service.listar_cursos(skip=skip, limit=limit)

    # Obtener total
    total = await service.contar_cursos()

    return PaginatedResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )
```

---

## 🔍 Patrón: Search/Filter Complejo

```python
from pydantic import BaseModel

class CursoFiltros(BaseModel):
    """Filtros para búsqueda de cursos."""
    nombre: str | None = None
    institucion_id: int | None = None
    docente_id: int | None = None
    activo: bool | None = None
    fecha_inicio_desde: date | None = None
    fecha_inicio_hasta: date | None = None

@router.get("/search", response_model=List[CursoResponse])
async def buscar_cursos(
    filtros: CursoFiltros = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[CursoResponse]:
    """Busca cursos con filtros múltiples.

    Query params:
        - nombre: Búsqueda por nombre (LIKE)
        - institucion_id: Filtro por institución
        - docente_id: Filtro por docente
        - activo: Filtro por estado
        - fecha_inicio_desde/hasta: Rango de fechas
    """
    service = CursoService(db)
    cursos = await service.buscar_cursos(
        filtros=filtros,
        skip=skip,
        limit=limit
    )
    return cursos
```

---

## ⚡ Patrón: Bulk Operations

```python
from typing import List

class BulkCreateResponse(BaseModel):
    """Response de operación bulk."""
    created: int
    failed: int
    errors: List[str]

@router.post("/bulk", response_model=BulkCreateResponse, status_code=status.HTTP_207_MULTI_STATUS)
async def crear_cursos_bulk(
    cursos: List[CursoCreate],
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
) -> BulkCreateResponse:
    """Crea múltiples cursos en una sola request.

    Permisos: Solo ADMIN

    Returns:
        207 Multi-Status con conteo de éxitos/fallos
    """
    service = CursoService(db)

    created = 0
    failed = 0
    errors = []

    for idx, curso_data in enumerate(cursos):
        try:
            await service.crear_curso(curso_data, docente_id=current_user.id)
            created += 1
        except Exception as e:
            failed += 1
            errors.append(f"Curso {idx}: {str(e)}")

    return BulkCreateResponse(
        created=created,
        failed=failed,
        errors=errors
    )
```

---

## 🔄 Patrón: Operaciones Complejas (Actions)

```python
from pydantic import BaseModel

class InscribirEstudianteRequest(BaseModel):
    """Request para inscribir estudiante."""
    estudiante_id: int
    rol_estudiante: str = "REGULAR"  # REGULAR, OYENTE, MONITOR

@router.post("/{curso_id}/inscribir", response_model=dict)
async def inscribir_estudiante(
    curso_id: int,
    data: InscribirEstudianteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_docente_or_admin)
) -> dict:
    """Inscribe un estudiante en el curso.

    Permisos: ADMIN o DOCENTE del curso

    Business Logic:
        1. Verificar que el curso existe
        2. Verificar que el estudiante existe
        3. Verificar que no está ya inscrito
        4. Verificar cupo disponible
        5. Crear inscripción
        6. Enviar notificación al estudiante

    Returns:
        dict con mensaje de éxito y datos de la inscripción
    """
    service = CursoService(db)

    try:
        inscripcion = await service.inscribir_estudiante(
            curso_id=curso_id,
            estudiante_id=data.estudiante_id,
            rol=data.rol_estudiante
        )

        return {
            "message": "Estudiante inscrito exitosamente",
            "inscripcion_id": inscripcion.id,
            "curso_id": curso_id,
            "estudiante_id": data.estudiante_id
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

---

## 📝 Patrón: File Upload

```python
from fastapi import File, UploadFile
import aiofiles

@router.post("/{curso_id}/avatar", response_model=dict)
async def subir_avatar_curso(
    curso_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_docente_curso)
) -> dict:
    """Sube avatar/imagen del curso.

    Permisos: ADMIN o DOCENTE del curso

    Validaciones:
        - Tamaño máximo: 5MB
        - Formatos: JPG, PNG, WEBP

    Returns:
        URL del archivo subido
    """
    # Validar tamaño
    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    content = await file.read()

    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Archivo muy grande. Máximo {MAX_SIZE} bytes"
        )

    # Validar tipo
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Permitidos: {ALLOWED_TYPES}"
        )

    service = CursoService(db)
    file_url = await service.guardar_avatar(curso_id, content, file.filename)

    return {
        "message": "Avatar subido exitosamente",
        "url": file_url
    }
```

---

## 🎯 Checklist de Endpoint Completo

Al crear un endpoint nuevo, verificar:

✅ **Docstring** con descripción, permisos, args, returns, raises
✅ **Response model** definido en el decorador
✅ **Status code** apropiado (200, 201, 204, etc.)
✅ **Validación de permisos** con Dependencies
✅ **Manejo de errores** con HTTPException descriptivos
✅ **Paginación** si retorna lista (skip, limit)
✅ **Type hints** en todos los parámetros
✅ **Async/await** correctamente usado
✅ **Logging** de operaciones importantes
✅ **Tests** unitarios + integración

---

**Usa estos patrones como base para todos los endpoints nuevos de Acadify.**
