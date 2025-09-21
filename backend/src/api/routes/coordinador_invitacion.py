from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.schemas.invitacion import InvitacionAceptar
from src.services.invitation_service import InvitationService
from src.models.auth.invitation_token import InvitationToken, EstadoInvitacion
from src.models.users.usuario import Usuario, RolUsuario
from src.models.academic.institucion import Institucion
from src.services.email_service import enviar_email
from uuid import UUID
from datetime import datetime
from passlib.context import CryptContext

router = APIRouter(prefix="/coordinador", tags=["Coordinador"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/aceptar-invitacion")
def aceptar_invitacion(
    data: InvitacionAceptar,
    db: Session = Depends(get_db)
):
    try:
        # Validar código
        invitacion = InvitationService.validar_codigo(db, data.codigo)
        
        # Verificar si ya existe un usuario con este email
        usuario_existente = db.query(Usuario).filter_by(correo_institucional=invitacion.email_destino).first()
        
        if usuario_existente:
            # El usuario ya existe, debe verificar su contraseña actual
            if not pwd_context.verify(data.password, usuario_existente.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Contraseña incorrecta. Usa la contraseña de tu cuenta existente."
                )
            
            # Verificar si ya está vinculado a esta institución específica
            invitaciones_previas = db.query(InvitationToken).filter_by(
                email_destino=invitacion.email_destino,
                institucion_id=invitacion.institucion_id,
                estado=EstadoInvitacion.usado
            ).first()
            
            if invitaciones_previas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Este usuario ya está vinculado como coordinador de esta institución"
                )
            
            # Si el usuario no es coordinador, lo convertimos en coordinador
            if usuario_existente.rol != RolUsuario.coordinador:
                usuario_existente.rol = RolUsuario.coordinador
            
            usuario_existente.estado_cuenta = "activo"
            db.commit()
            db.refresh(usuario_existente)
            usuario = usuario_existente
            
        else:
            # No existe usuario con ese email, error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No existe una cuenta con el email de la invitación. Por favor, crea una cuenta primero."
            )
        
        # Marcar invitación como usada
        InvitationService.marcar_usado(db, invitacion, usuario.usuario_id)
        
        # Activar institución
        institucion = db.query(Institucion).filter_by(institucion_id=invitacion.institucion_id).first()
        if institucion:
            institucion.estado = "activa"
            from datetime import timezone
            institucion.fecha_activacion = datetime.now(timezone.utc)
            db.commit()
        
        return {
            "mensaje": "¡Invitación aceptada exitosamente! Ahora eres coordinador y la institución está activa.",
            "usuario_id": str(usuario.usuario_id),
            "email": usuario.correo_institucional,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "institucion": institucion.nombre if institucion else None
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
