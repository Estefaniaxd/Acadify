from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ...db.session import get_db
from ...api.dependencies import get_current_user, require_roles
from ...schemas.academic.clase import (
    Clase, ClaseCreate, ClaseUpdate, ClaseDetallada, CodigoAccesoResponse,
    HistorialAcceso, EstudianteUnirse, RespuestaUnirse, ClaseConHistorial
)
from ...crud.academic.crud_clase import clase
from ...core.redis_manager import redis_manager
from ...models.users.usuario import Usuario
from ...enums.users.usuario_enums import TipoUsuario

router = APIRouter()
security = HTTPBearer()

@router.post("/", response_model=Clase, status_code=status.HTTP_201_CREATED)
async def crear_clase(
    *,
    db: Session = Depends(get_db),
    clase_in: ClaseCreate,
    current_user: Usuario = Depends(require_roles([TipoUsuario.docente, TipoUsuario.coordinador]))
):
    """
    Crear nueva clase.
    Solo docentes pueden crear clases.
    """
    try:
        # Verificar que el docente tenga permisos para el grupo
        # (aquí podrías agregar validación adicional)
        
        nueva_clase = clase.create(db=db, obj_in=clase_in)
        
        # Cachear la clase en Redis
        clase_data = {
            "clase_id": str(nueva_clase.clase_id),
            "titulo": nueva_clase.titulo,
            "grupo_id": str(nueva_clase.grupo_id),
            "docente_id": str(nueva_clase.docente_id),
            "codigo_acceso": nueva_clase.codigo_acceso,
            "fecha_inicio": nueva_clase.fecha_inicio.isoformat() if nueva_clase.fecha_inicio else None,
            "estado": nueva_clase.estado.value
        }
        
        redis_manager.cache_curso(str(nueva_clase.clase_id), clase_data)
        redis_manager.guardar_codigo_clase(nueva_clase.codigo_acceso, clase_data)
        
        # Notificar creación de clase
        redis_manager.publicar_notificacion(
            f"grupo_{nueva_clase.grupo_id}",
            {
                "tipo": "nueva_clase",
                "clase_id": str(nueva_clase.clase_id),
                "titulo": nueva_clase.titulo,
                "docente": f"{current_user.nombre} {current_user.apellido}",
                "fecha": datetime.now().isoformat()
            }
        )
        
        return nueva_clase
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando clase: {str(e)}"
        )

@router.get("/{clase_id}", response_model=ClaseDetallada)
async def obtener_clase(
    clase_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener detalles de una clase"""
    
    # Verificar cache primero
    cached_data = redis_manager.obtener_curso_cache(str(clase_id))
    
    clase_obj = clase.get(db=db, clase_id=clase_id)
    if not clase_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada"
        )
    
    # Verificar permisos
    if current_user.tipo_usuario == TipoUsuario.estudiante:
        # Verificar si el estudiante está inscrito en el grupo
        # (aquí agregar lógica de verificación)
        pass
    
    return clase_obj

@router.put("/{clase_id}", response_model=Clase)
async def actualizar_clase(
    *,
    db: Session = Depends(get_db),
    clase_id: UUID,
    clase_in: ClaseUpdate,
    current_user: Usuario = Depends(require_roles([TipoUsuario.docente, TipoUsuario.coordinador]))
):
    """Actualizar información de clase"""
    
    clase_obj = clase.get(db=db, clase_id=clase_id)
    if not clase_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada"
        )
    
    # Verificar permisos: solo el docente de la clase puede editarla
    if current_user.tipo_usuario == TipoUsuario.docente and str(clase_obj.docente_id) != str(current_user.usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar esta clase"
        )
    
    clase_actualizada = clase.update(db=db, db_obj=clase_obj, obj_in=clase_in)
    
    # Invalidar cache
    redis_manager.invalidar_cache_curso(str(clase_id))
    
    return clase_actualizada

@router.delete("/{clase_id}")
async def eliminar_clase(
    clase_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles([TipoUsuario.docente, TipoUsuario.coordinador]))
):
    """Eliminar una clase"""
    
    clase_obj = clase.get(db=db, clase_id=clase_id)
    if not clase_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada"
        )
    
    # Verificar permisos
    if current_user.tipo_usuario == TipoUsuario.docente and str(clase_obj.docente_id) != str(current_user.usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar esta clase"
        )
    
    clase.remove(db=db, id=clase_id)
    
    # Limpiar cache
    redis_manager.invalidar_cache_curso(str(clase_id))
    redis_manager.invalidar_codigo_clase(clase_obj.codigo_acceso)
    
    return {"message": "Clase eliminada exitosamente"}

@router.post("/{clase_id}/regenerar-codigo", response_model=CodigoAccesoResponse)
async def regenerar_codigo_acceso(
    clase_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles([TipoUsuario.docente, TipoUsuario.coordinador]))
):
    """Regenerar código de acceso de una clase"""
    
    clase_obj = clase.get(db=db, clase_id=clase_id)
    if not clase_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada"
        )
    
    # Verificar permisos
    if current_user.tipo_usuario == TipoUsuario.docente and str(clase_obj.docente_id) != str(current_user.usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para regenerar el código de esta clase"
        )
    
    # Invalidar código anterior
    redis_manager.invalidar_codigo_clase(clase_obj.codigo_acceso)
    
    # Generar nuevo código
    nuevo_codigo = clase.regenerar_codigo_acceso(db=db, clase_id=clase_id)
    
    # Actualizar cache
    clase_data = {
        "clase_id": str(clase_id),
        "titulo": clase_obj.titulo,
        "grupo_id": str(clase_obj.grupo_id),
        "docente_id": str(clase_obj.docente_id),
        "codigo_acceso": nuevo_codigo,
        "fecha_inicio": clase_obj.fecha_inicio.isoformat() if clase_obj.fecha_inicio else None,
        "estado": clase_obj.estado.value
    }
    
    redis_manager.guardar_codigo_clase(nuevo_codigo, clase_data)
    
    return {
        "codigo_acceso": nuevo_codigo,
        "estado_codigo": clase_obj.estado_codigo,
        "fecha_vencimiento": clase_obj.fecha_vencimiento_codigo,
        "fecha_generacion": datetime.now()
    }

@router.post("/unirse", response_model=RespuestaUnirse)
async def unirse_a_clase(
    *,
    db: Session = Depends(get_db),
    request: Request,
    estudiante_data: EstudianteUnirse,
    current_user: Usuario = Depends(require_roles([TipoUsuario.estudiante]))
):
    """Permite a un estudiante unirse a una clase usando el código"""
    
    # Obtener IP del usuario
    ip_cliente = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Intentar unirse a la clase
    exito, mensaje, clase_obj = clase.unirse_a_clase(
        db=db,
        codigo=estudiante_data.codigo_acceso,
        estudiante_id=current_user.usuario_id,
        ip_acceso=ip_cliente,
        user_agent=user_agent
    )
    
    if exito and clase_obj:
        # Registrar sesión activa en Redis
        session_data = {
            "estudiante_id": str(current_user.usuario_id),
            "nombre_estudiante": f"{current_user.nombre} {current_user.apellido}",
            "fecha_union": datetime.now().isoformat(),
            "ip_acceso": ip_cliente
        }
        
        redis_manager.registrar_sesion_estudiante(
            str(clase_obj.clase_id),
            str(current_user.usuario_id),
            session_data
        )
        
        # Notificar al docente
        redis_manager.publicar_notificacion(
            f"clase_{clase_obj.clase_id}",
            {
                "tipo": "estudiante_unido",
                "estudiante": f"{current_user.nombre} {current_user.apellido}",
                "fecha": datetime.now().isoformat()
            }
        )
    
    return {
        "success": exito,
        "message": mensaje,
        "clase": clase_obj
    }

@router.get("/{clase_id}/estudiantes-activos", response_model=List[dict])
async def obtener_estudiantes_activos(
    clase_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles([TipoUsuario.docente, TipoUsuario.coordinador]))
):
    """Obtener lista de estudiantes actualmente conectados a la clase"""
    
    estudiantes_ids = redis_manager.obtener_estudiantes_activos(str(clase_id))
    
    # Obtener información detallada de cada estudiante
    estudiantes_info = []
    for estudiante_id in estudiantes_ids:
        session_data = redis_manager.get_value(f"sesion_clase:{clase_id}:{estudiante_id}")
        if session_data:
            estudiantes_info.append(session_data)
    
    return estudiantes_info

@router.get("/{clase_id}/historial", response_model=List[HistorialAcceso])
async def obtener_historial_accesos(
    clase_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles([TipoUsuario.docente, TipoUsuario.coordinador]))
):
    """Obtener historial completo de accesos a la clase"""
    
    historial = clase.get_historial_accesos(db=db, clase_id=clase_id)
    return historial

@router.get("/{clase_id}/estadisticas")
async def obtener_estadisticas_clase(
    clase_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles([TipoUsuario.docente, TipoUsuario.coordinador]))
):
    """Obtener estadísticas de la clase"""
    
    estadisticas = clase.get_estadisticas_clase(db=db, clase_id=clase_id)
    return estadisticas

@router.get("/grupo/{grupo_id}", response_model=List[Clase])
async def obtener_clases_grupo(
    grupo_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener todas las clases de un grupo"""
    
    clases = clase.get_multi_by_grupo(
        db=db, 
        grupo_id=grupo_id, 
        skip=skip, 
        limit=limit
    )
    
    return clases

@router.get("/docente/{docente_id}", response_model=List[Clase])
async def obtener_clases_docente(
    docente_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles([TipoUsuario.docente, TipoUsuario.coordinador]))
):
    """Obtener todas las clases de un docente"""
    
    # Verificar que solo pueda ver sus propias clases si es docente
    if current_user.tipo_usuario == TipoUsuario.docente and str(current_user.usuario_id) != str(docente_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver las clases de otro docente"
        )
    
    clases = clase.get_multi_by_docente(
        db=db, 
        docente_id=docente_id, 
        skip=skip, 
        limit=limit
    )
    
    return clases