from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.api.api.dependencies import get_current_user, require_roles
from src.api.core.redis_manager import redis_manager
from src.api.crud.academic.crud_material_educativo import material_educativo_crud
from src.api.db.session import get_db
from src.api.enums.academic.material_educativo_enums import (
    CarpetaMaterial,
    EstadoMaterial,
    TipoMaterialEducativo,
)
from src.api.enums.users.usuario_enums import TipoUsuario
from src.api.models.users.usuario import Usuario
from src.api.schemas.academic.material_educativo import (
    EstadisticasMaterial,
    MaterialEducativo,
    MaterialEducativoCreate,
    MaterialEducativoDetallado,
    MaterialEducativoSubirVersion,
    MaterialEducativoUpdate,
    SincronizacionDrive,
)


router = APIRouter()
security = HTTPBearer()


@router.post("/", response_model=MaterialEducativo, status_code=status.HTTP_201_CREATED)
async def crear_material(
    *,
    db: Session = Depends(get_db),
    material_in: MaterialEducativoCreate,
    current_user: Usuario = Depends(
        require_roles([TipoUsuario.docente, TipoUsuario.coordinador])
    ),
):
    """Crear nuevo material educativo."""
    try:
        # Asignar autor automáticamente
        material_in.autor_id = current_user.usuario_id

        nuevo_material = material_educativo_crud.create(db=db, obj_in=material_in)

        # Cachear el material en Redis
        material_data = {
            "material_id": str(nuevo_material.material_id),
            "titulo": nuevo_material.titulo,
            "tipo_material": nuevo_material.tipo_material.value,
            "carpeta": nuevo_material.carpeta.value,
            "autor_id": (
                str(nuevo_material.autor_id) if nuevo_material.autor_id else None
            ),
            "estado": nuevo_material.estado.value,
            "version": nuevo_material.version,
        }

        redis_manager.cache_material(str(nuevo_material.material_id), material_data)

        # Notificar nuevo material
        redis_manager.publicar_notificacion(
            "nuevo_material",
            {
                "tipo": "material_creado",
                "material_id": str(nuevo_material.material_id),
                "titulo": nuevo_material.titulo,
                "carpeta": nuevo_material.carpeta.value,
                "autor": f"{current_user.nombre} {current_user.apellido}",
                "fecha": nuevo_material.fecha_creacion.isoformat(),
            },
        )

        return nuevo_material

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando material: {e!s}",
        ) from e


@router.get("/{material_id}", response_model=MaterialEducativoDetallado)
async def obtener_material(
    material_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener detalles de material educativo."""
    # Verificar cache primero
    redis_manager.obtener_material_cache(str(material_id))

    material = material_educativo_crud.get(db=db, material_id=material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado"
        )

    # Verificar permisos de acceso
    if (
        material.estado != EstadoMaterial.activo
        and material.autor_id != current_user.usuario_id
    ) and current_user.tipo_usuario not in [
        TipoUsuario.coordinador,
        TipoUsuario.admin,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este material",
        )

    # Registrar acceso para estadísticas
    material_educativo_crud.registrar_descarga(db=db, material_id=material_id)

    return material


@router.put("/{material_id}", response_model=MaterialEducativo)
async def actualizar_material(
    *,
    db: Session = Depends(get_db),
    material_id: UUID,
    material_in: MaterialEducativoUpdate,
    current_user: Usuario = Depends(
        require_roles([TipoUsuario.docente, TipoUsuario.coordinador])
    ),
):
    """Actualizar material educativo."""
    material = material_educativo_crud.get(db=db, material_id=material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado"
        )

    # Verificar permisos: solo el autor o coordinador puede editar
    if (
        material.autor_id != current_user.usuario_id
        and current_user.tipo_usuario != TipoUsuario.coordinador
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar este material",
        )

    material_actualizado = material_educativo_crud.update(
        db=db, db_obj=material, obj_in=material_in
    )

    # Invalidar cache
    redis_manager.invalidar_cache_material(str(material_id))

    return material_actualizado


@router.delete("/{material_id}")
async def eliminar_material(
    material_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles([TipoUsuario.docente, TipoUsuario.coordinador])
    ),
):
    """Eliminar material educativo (cambiar estado a archivado)."""
    material = material_educativo_crud.get(db=db, material_id=material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado"
        )

    # Verificar permisos
    if (
        material.autor_id != current_user.usuario_id
        and current_user.tipo_usuario != TipoUsuario.coordinador
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este material",
        )

    # Archivar en lugar de eliminar
    material_educativo_crud.update(
        db=db,
        db_obj=material,
        obj_in=MaterialEducativoUpdate(estado=EstadoMaterial.archivado),
    )

    # Limpiar cache
    redis_manager.invalidar_cache_material(str(material_id))

    return {"message": "Material archivado exitosamente"}


@router.post("/{material_id}/nueva-version", response_model=MaterialEducativo)
async def subir_nueva_version(
    *,
    db: Session = Depends(get_db),
    material_id: UUID,
    nueva_version: MaterialEducativoSubirVersion,
    current_user: Usuario = Depends(
        require_roles([TipoUsuario.docente, TipoUsuario.coordinador])
    ),
):
    """Subir nueva versión de material educativo."""
    material_original = material_educativo_crud.get(db=db, material_id=material_id)
    if not material_original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material original no encontrado",
        )

    # Verificar permisos
    if (
        material_original.autor_id != current_user.usuario_id
        and current_user.tipo_usuario != TipoUsuario.coordinador
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear una nueva versión de este material",
        )

    try:
        nueva_version_material = material_educativo_crud.subir_nueva_version(
            db=db,
            material_id=material_id,
            nueva_version=nueva_version,
            autor_id=current_user.usuario_id,
        )

        # Invalidar cache del material original
        redis_manager.invalidar_cache_material(str(material_id))

        # Notificar nueva versión
        redis_manager.publicar_notificacion(
            "nueva_version_material",
            {
                "tipo": "nueva_version",
                "material_id": str(material_id),
                "nueva_version_id": str(nueva_version_material.material_id),
                "titulo": nueva_version_material.titulo,
                "version": nueva_version_material.version,
                "autor": f"{current_user.nombre} {current_user.apellido}",
                "fecha": nueva_version_material.fecha_creacion.isoformat(),
            },
        )

        return nueva_version_material

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando nueva versión: {e!s}",
        ) from e


@router.get("/", response_model=list[MaterialEducativo])
async def listar_material(
    skip: int = 0,
    limit: int = 100,
    carpeta: CarpetaMaterial | None = None,
    tipo_material: TipoMaterialEducativo | None = None,
    autor_id: UUID | None = None,
    solo_activos: bool = True,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar material educativo con filtros."""
    if carpeta:
        materiales = material_educativo_crud.get_multi_by_carpeta(
            db=db, carpeta=carpeta, skip=skip, limit=limit, solo_activos=solo_activos
        )
    elif autor_id:
        materiales = material_educativo_crud.get_multi_by_autor(
            db=db, autor_id=autor_id, skip=skip, limit=limit
        )
    else:
        # Listar todo el material (aquí podrías agregar más filtros)
        materiales = []

    return materiales


@router.get("/buscar/{termino}")
async def buscar_material(
    termino: str,
    skip: int = 0,
    limit: int = 100,
    carpeta: CarpetaMaterial | None = None,
    tipo_material: TipoMaterialEducativo | None = None,
    autor_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Buscar material educativo por término."""
    if len(termino) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El término de búsqueda debe tener al menos 2 caracteres",
        )

    return material_educativo_crud.buscar_material(
        db=db,
        termino_busqueda=termino,
        carpeta=carpeta,
        tipo_material=tipo_material,
        autor_id=autor_id,
        skip=skip,
        limit=limit,
    )


@router.get("/carpeta/{carpeta}", response_model=list[MaterialEducativo])
async def obtener_material_por_carpeta(
    carpeta: CarpetaMaterial,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener material de una carpeta específica."""
    return material_educativo_crud.get_multi_by_carpeta(
        db=db, carpeta=carpeta, skip=skip, limit=limit, solo_activos=True
    )


@router.get("/popular/", response_model=list[MaterialEducativo])
async def obtener_material_popular(
    limit: int = 10,
    carpeta: CarpetaMaterial | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener material más popular por descargas."""
    return material_educativo_crud.get_material_popular(
        db=db, limit=limit, carpeta=carpeta
    )


@router.get("/estadisticas/", response_model=EstadisticasMaterial)
async def obtener_estadisticas_material(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles([TipoUsuario.coordinador, TipoUsuario.admin])
    ),
):
    """Obtener estadísticas generales del material educativo."""
    return material_educativo_crud.get_estadisticas_material(db=db)


@router.get("/{material_id}/versiones", response_model=list[MaterialEducativo])
async def obtener_versiones_material(
    material_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener todas las versiones de un material."""
    material = material_educativo_crud.get(db=db, material_id=material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado"
        )

    # Verificar permisos para ver versiones
    if (
        material.autor_id != current_user.usuario_id
        and current_user.tipo_usuario
        not in [TipoUsuario.coordinador, TipoUsuario.admin]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver las versiones de este material",
        )

    return material_educativo_crud.get_versiones_material(
        db=db, material_id=material_id
    )


@router.post("/{material_id}/sincronizar-drive")
async def sincronizar_con_google_drive(
    material_id: UUID,
    sync_data: SincronizacionDrive,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_roles([TipoUsuario.coordinador, TipoUsuario.admin])
    ),
):
    """Sincronizar material con Google Drive."""
    material = material_educativo_crud.get(db=db, material_id=material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado"
        )

    try:
        # Aquí implementar la lógica de sincronización con Google Drive
        # Por ahora solo actualizamos los campos

        material_educativo_crud.update(
            db=db,
            db_obj=material,
            obj_in=MaterialEducativoUpdate(
                google_drive_id=sync_data.google_drive_id,
                google_drive_url=sync_data.google_drive_url,
                sincronizado_drive=True,
            ),
        )

        # Invalidar cache
        redis_manager.invalidar_cache_material(str(material_id))

        return {
            "message": "Material sincronizado con Google Drive",
            "drive_id": sync_data.google_drive_id,
            "drive_url": sync_data.google_drive_url,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error sincronizando con Google Drive: {e!s}",
        ) from e
