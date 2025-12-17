"""Endpoints para coordinadores.

Rutas protegidas que requieren autenticación y rol de coordinador.
"""

import logging
from typing import Any
from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from src.api.dependencies import get_current_user
from src.api.deps import get_db
from src.models.users.usuario import Usuario, RolUsuario
from src.models.users.coordinador import Coordinador
from src.models.users.institucion_coordinador import InstitucionCoordinador
from src.models.academic.institucion import Institucion
from src.models.academic.curso import Curso
from src.models.academic.programa import Programa
from src.models.auth.invitation_token import InvitationToken, EstadoInvitacion
from src.utils.security import SecurityManager
from datetime import date

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["Coordinador"])


class AceptarCodigoSchema(BaseModel):
    codigo: str


def get_current_coordinador(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.rol not in [RolUsuario.coordinador, RolUsuario.administrador]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los coordinadores pueden acceder a este recurso"
        )
    return current_user


@router.post("/aceptar-codigo", response_model=dict[str, Any])
def aceptar_codigo_invitacion(
    data: AceptarCodigoSchema,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"Usuario {current_user.correo_institucional} aceptando código: {data.codigo}")
    
    try:
        invitacion = (
            db.query(InvitationToken)
            .filter(InvitationToken.codigo == data.codigo)
            .filter(InvitationToken.estado == EstadoInvitacion.pendiente)
            .first()
        )
        
        if not invitacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Código inválido o ya utilizado"
            )
        
        if invitacion.email_destino != current_user.correo_institucional:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Este código no fue enviado a tu correo electrónico"
            )
        
        if invitacion.fecha_expiracion < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código de invitación ha expirado"
            )
        
        # Actualizar rol del usuario a coordinador
        if current_user.rol != RolUsuario.coordinador:
            current_user.rol = RolUsuario.coordinador
        current_user.estado_cuenta = "activo"
        
        # Crear registro en tabla Coordinador si no existe
        coordinador_existe = db.query(Coordinador).filter(
            Coordinador.coordinador_id == current_user.usuario_id
        ).first()
        
        if not coordinador_existe:
            nuevo_coordinador = Coordinador(
                coordinador_id=current_user.usuario_id,
                fecha_inicio_carrera=date.today()
            )
            db.add(nuevo_coordinador)
            db.flush()  # Asegurar que se crea antes de la relación
        
        # Crear relación InstitucionCoordinador si no existe
        relacion_existe = db.query(InstitucionCoordinador).filter(
            InstitucionCoordinador.coordinador_id == current_user.usuario_id,
            InstitucionCoordinador.institucion_id == invitacion.institucion_id
        ).first()
        
        if not relacion_existe:
            nueva_relacion = InstitucionCoordinador(
                institucion_id=invitacion.institucion_id,
                coordinador_id=current_user.usuario_id,
                fecha_asignacion=date.today(),
                estado="activo"
            )
            db.add(nueva_relacion)
        
        # Marcar invitación como usada
        invitacion.estado = EstadoInvitacion.usado
        invitacion.fecha_uso = datetime.now(UTC)
        invitacion.usuario_id = current_user.usuario_id
        
        institucion = (
            db.query(Institucion)
            .filter(Institucion.institucion_id == invitacion.institucion_id)
            .first()
        )
        
        if institucion:
            institucion.estado = "activa"
            if not institucion.fecha_activacion:
                institucion.fecha_activacion = datetime.now(UTC)
        
        db.commit()
        db.refresh(current_user)
        db.refresh(institucion)
        
        # Generar nuevo token con datos actualizados
        security_manager = SecurityManager()
        new_token = security_manager.create_access_token(
            subject=str(current_user.usuario_id),
            additional_claims={
                "rol": current_user.rol.value,
                "email": current_user.correo_institucional,
                "username": current_user.username,
            }
        )
        
        logger.info(f"Código aceptado exitosamente para {current_user.correo_institucional}")
        
        return {
            "message": "Invitación aceptada exitosamente",
            "access_token": new_token,
            "token_type": "bearer",
            "institucion": {
                "id": institucion.institucion_id,
                "nombre": institucion.nombre,
                "tipo": institucion.tipo_institucion
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"Error al aceptar código: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al procesar la invitación: {str(e)}"
        )


@router.get("/mi-institucion", response_model=dict[str, Any])
def obtener_mi_institucion(
    current_user: Usuario = Depends(get_current_coordinador),
    db: Session = Depends(get_db),
):
    logger.info(f"Obteniendo institución de coordinador: {current_user.correo_institucional}")
    
    # Buscar la relación InstitucionCoordinador
    relacion = (
        db.query(InstitucionCoordinador)
        .filter(InstitucionCoordinador.coordinador_id == current_user.usuario_id)
        .filter(InstitucionCoordinador.estado == "activo")
        .first()
    )
    
    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes una institución asignada"
        )
    
    # Obtener la institución
    institucion = (
        db.query(Institucion)
        .filter(Institucion.institucion_id == relacion.institucion_id)
        .first()
    )
    
    if not institucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institución no encontrada"
        )
    
    return {
        "id": institucion.institucion_id,
        "nombre": institucion.nombre,
        "tipo": institucion.tipo_institucion,
        "ubicacion": f"{institucion.ciudad}, {institucion.pais}" if institucion.ciudad and institucion.pais else None,
        "estado": institucion.estado,
        "created_at": institucion.fecha_creacion.isoformat() if institucion.fecha_creacion else None
    }


@router.get("/institucion/{institucion_id}/estadisticas", response_model=dict[str, Any])
def obtener_estadisticas_institucion(
    institucion_id: str,  # Cambiar a str porque es UUID
    current_user: Usuario = Depends(get_current_coordinador),
    db: Session = Depends(get_db),
):
    logger.info(f"Obteniendo estadísticas de institución {institucion_id}")
    
    # Verificar que el coordinador pertenece a esta institución
    relacion = (
        db.query(InstitucionCoordinador)
        .filter(InstitucionCoordinador.coordinador_id == current_user.usuario_id)
        .filter(InstitucionCoordinador.institucion_id == institucion_id)
        .filter(InstitucionCoordinador.estado == "activo")
        .first()
    )
    
    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta institución"
        )
    
    try:
        # Contar programas de la institución
        total_programas = (
            db.query(func.count(Programa.programa_id))
            .filter(Programa.institucion_id == institucion_id)
            .scalar() or 0
        )
        
        # Contar cursos de la institución
        total_cursos = (
            db.query(func.count(Curso.curso_id))
            .filter(Curso.institucion_id == institucion_id)
            .scalar() or 0
        )
        
        # Por ahora devolver 0 para estudiantes/profesores
        # TODO: Implementar conteo real a través de Programa/CursoDocente
        total_estudiantes = 0
        total_profesores = 0
        
        return {
            "total_estudiantes": total_estudiantes,
            "total_profesores": total_profesores,
            "total_cursos": total_cursos,
            "total_programas": total_programas
        }
        
    except Exception as e:
        logger.exception(f"Error al obtener estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas"
        )


@router.get("/dashboard-stats", response_model=dict[str, Any])
def obtener_estadisticas_dashboard(
    current_user: Usuario = Depends(get_current_coordinador),
    db: Session = Depends(get_db),
):
    """Obtener estadísticas completas para el dashboard del coordinador.
    
    Utiliza el procedimiento almacenado sp_obtener_dashboard_coordinador.
    """
    logger.info(f"Obteniendo estadísticas dashboard de coordinador: {current_user.correo_institucional}")
    
    try:
        # Llamar al procedimiento almacenado
        from sqlalchemy import text
        
        query = text("""
            SELECT * FROM sp_obtener_dashboard_coordinador(:usuario_id)
        """)
        
        result = db.execute(query, {"usuario_id": str(current_user.usuario_id)}).fetchone()
        
        if not result:
            # Si no hay resultado, devolver valores por defecto
            return {
                "institucion_nombre": "Sin institución asignada",
                "total_programas": 0,
                "total_cursos": 0,
                "total_docentes": 0,
                "total_estudiantes": 0,
                "cursos_activos": 0,
                "estudiantes_activos_mes": 0,
                "tareas_pendiente_revision": 0
            }
        
        # Convertir el resultado a diccionario
        return {
            "institucion_nombre": result[0],
            "total_programas": result[1],
            "total_cursos": result[2],
            "total_docentes": result[3],
            "total_estudiantes": result[4],
            "cursos_activos": result[5],
            "estudiantes_activos_mes": result[6],
            "tareas_pendiente_revision": result[7]
        }
        
    except Exception as e:
        logger.exception(f"Error al obtener estadísticas dashboard: {e}")
        # Devolver valores por defecto en caso de error
        return {
            "institucion_nombre": "Sin institución asignada",
            "total_programas": 0,
            "total_cursos": 0,
            "total_docentes": 0,
            "total_estudiantes": 0,
            "cursos_activos": 0,
            "estudiantes_activos_mes": 0,
            "tareas_pendiente_revision": 0
        }
