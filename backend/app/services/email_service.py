# backend/app/services/email_service.py
"""
Servicio de envío de emails avanzado y escalable
Gestión de notificaciones, confirmaciones y comunicaciones
"""

import os
from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.core.logging import app_logger, log_error


class EmailService:
    """Servicio de envío de emails profesional"""

    def __init__(self):
        self.smtp_host = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM or self.username

        # Templates Jinja2
        template_dir = os.path.join(os.path.dirname(__file__), "../templates/email")
        if os.path.exists(template_dir):
            self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        else:
            self.jinja_env = None
            app_logger.warning("Directorio de templates de email no encontrado")

    # --------------------------
    # ENVÍO GENÉRICO
    # --------------------------
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Envía un email con soporte para HTML y adjuntos"""
        if not self.username or not self.password:
            app_logger.warning("Configuración SMTP incompleta")
            return False

        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject

            # Texto plano
            message.attach(MIMEText(body, "plain", "utf-8"))
            # HTML
            if html_body:
                message.attach(MIMEText(html_body, "html", "utf-8"))
            # Adjuntos
            if attachments:
                for att in attachments:
                    self._add_attachment(message, att)

            # Envío async
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                start_tls=True
            )

            app_logger.info(f"Email enviado a {to_email}")
            return True
        except Exception as e:
            log_error(e, f"EMAIL_SERVICE_SEND_EMAIL to {to_email}")
            return False

    # --------------------------
    # MÉTODOS ESPECÍFICOS
    # --------------------------
    async def send_welcome_email(self, user_email: str, user_name: str, temporary_password: str) -> bool:
        subject = f"Bienvenido a {settings.PROJECT_NAME}"
        html_body = self._render_template("welcome.html", user_name=user_name,
                                          project_name=settings.PROJECT_NAME,
                                          login_url=settings.LOGIN_URL,
                                          temporary_password=temporary_password)
        body = f"""
¡Hola {user_name}!
Bienvenido a {settings.PROJECT_NAME}.
Email: {user_email}
Contraseña temporal: {temporary_password}
Por favor, cambia tu contraseña en el primer acceso.
Saludos,
El equipo de {settings.PROJECT_NAME}
        """.strip()
        return await self.send_email(user_email, subject, body, html_body)

    async def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        subject = f"Reseteo de contraseña - {settings.PROJECT_NAME}"
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        body = f"""
Hola {user_name},
Recibimos una solicitud para resetear tu contraseña en {settings.PROJECT_NAME}.
Para crear una nueva contraseña, haz clic en: {reset_url}
Si no solicitaste el cambio, ignora este mensaje.
Saludos,
El equipo de {settings.PROJECT_NAME}
        """.strip()
        return await self.send_email(user_email, subject, body)

    async def send_welcome_oauth_email(self, user_email: str, user_name: str, provider: str) -> bool:
        provider_display = {"google": "Google", "github": "GitHub", "microsoft": "Microsoft"}.get(provider, provider.title())
        subject = f"Bienvenido a {settings.PROJECT_NAME}"
        body = f"""
¡Hola {user_name}!
Tu cuenta ha sido creada usando {provider_display}.
Email: {user_email}
Proveedor: {provider_display}
Rol inicial: Estudiante
Saludos,
El equipo de {settings.PROJECT_NAME}
        """.strip()
        return await self.send_email(user_email, subject, body)

    # --------------------------
    # UTILIDADES
    # --------------------------
    def _render_template(self, template_name: str, **context) -> Optional[str]:
        if not self.jinja_env:
            return None
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            log_error(e, f"TEMPLATE_RENDER_ERROR {template_name}")
            return None

    def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """Agrega archivo adjunto"""
        file_content = attachment.get("content")
        filename = attachment.get("filename", "attachment")
        mimetype = attachment.get("mimetype", "application/octet-stream")

        part = MIMEBase(*mimetype.split("/"))
        part.set_payload(file_content)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        message.attach(part)


# Instancia global
email_service = EmailService()
