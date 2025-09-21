import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from src.models.auth.invitation_token import InvitationToken, EstadoInvitacion
from src.models.academic.institucion import Institucion
from src.models.users.usuario import Usuario

from src.services.email_service import enviar_email

class InvitationService:
    @staticmethod
    def generar_codigo_unico(db: Session) -> str:
        """Genera un código único de 6 dígitos"""
        while True:
            codigo = f"{random.randint(100000, 999999)}"
            existe = db.query(InvitationToken).filter_by(codigo=codigo).first()
            if not existe:
                return codigo

    @staticmethod
    def crear_invitacion(db: Session, email_destino: str, institucion_id, fecha_expiracion=None) -> InvitationToken:
        codigo = InvitationService.generar_codigo_unico(db)
        if not fecha_expiracion:
            ahora = datetime.now(timezone.utc)
            fecha_expiracion = ahora + timedelta(hours=72)  # 3 días
            print(f"DEBUG - Creando invitación - Fecha actual: {ahora}")
            print(f"DEBUG - Creando invitación - Fecha expiración: {fecha_expiracion}")
        
        invitacion = InvitationToken(
            codigo=codigo,
            email_destino=email_destino,
            institucion_id=institucion_id,
            estado=EstadoInvitacion.pendiente,
            fecha_expiracion=fecha_expiracion,
        )
        db.add(invitacion)
        db.commit()
        db.refresh(invitacion)
        return invitacion

    @staticmethod
    def enviar_invitacion_email(invitacion: InvitationToken, db: Session):
        institucion = db.query(Institucion).filter_by(institucion_id=invitacion.institucion_id).first()
        asunto = f"Invitación para ser coordinador en {institucion.nombre}"
        cuerpo = f"""
        Hola,
        Has sido invitado como coordinador principal de la institución {institucion.nombre}.
        Tu código de invitación es: {invitacion.codigo}
        Este código expira el {invitacion.fecha_expiracion.strftime('%Y-%m-%d %H:%M')} UTC.
        Ingresa al sistema y completa tu registro usando este código.
        """
        enviar_email(destinatario=invitacion.email_destino, asunto=asunto, cuerpo=cuerpo)

    @staticmethod
    def validar_codigo(db: Session, codigo: str) -> InvitationToken:
        invitacion = db.query(InvitationToken).filter_by(codigo=codigo).first()
        if not invitacion:
            raise ValueError("Código inválido")
        if invitacion.estado != EstadoInvitacion.pendiente:
            raise ValueError("El código ya fue usado o expiró")
        
        # Debug: imprimir fechas para verificar
        ahora = datetime.now(timezone.utc)
        print(f"DEBUG - Fecha actual UTC: {ahora}")
        print(f"DEBUG - Fecha expiración: {invitacion.fecha_expiracion}")
        print(f"DEBUG - ¿Expirado?: {invitacion.fecha_expiracion < ahora}")
        
        if invitacion.fecha_expiracion < ahora:
            invitacion.estado = EstadoInvitacion.expirado
            db.commit()
            raise ValueError(f"El código ha expirado. Expiró el {invitacion.fecha_expiracion.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        return invitacion

    @staticmethod
    def marcar_usado(db: Session, invitacion: InvitationToken, coordinador_id):
        invitacion.estado = EstadoInvitacion.usado
        invitacion.coordinador_id = coordinador_id
        invitacion.usado_en = datetime.now(timezone.utc)
        db.commit()
        db.refresh(invitacion)
