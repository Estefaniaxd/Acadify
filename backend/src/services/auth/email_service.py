import asyncio
from concurrent.futures import ThreadPoolExecutor
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import secrets
import smtplib

from src.core.config import settings


class EmailService:
    """Servicio para envío de emails."""

    def __init__(self) -> None:
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = (
            settings.SMTP_PASS
        )  # Corregido: SMTP_PASS en lugar de SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.frontend_url = settings.FRONTEND_URL
        # ThreadPoolExecutor para envío asíncrono
        self._executor = ThreadPoolExecutor(max_workers=5)

    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Crear conexión SMTP."""
        smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
        smtp.starttls()
        smtp.login(self.smtp_user, self.smtp_password)
        return smtp

    def _send_email_sync(self, to_email: str, subject: str, html_content: str) -> bool:
        """Enviar email de forma síncrona (uso interno)."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            with self._create_smtp_connection() as smtp:
                smtp.send_message(msg)

            return True
        except Exception:
            return False

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Enviar email genérico (síncrono para compatibilidad)."""
        return self._send_email_sync(to_email, subject, html_content)

    async def send_email_async(
        self, to_email: str, subject: str, html_content: str
    ) -> None:
        """Enviar email de forma asíncrona (no bloquea la respuesta)."""
        loop = asyncio.get_event_loop()
        try:
            # Ejecutar en thread pool para no bloquear el event loop
            await loop.run_in_executor(
                self._executor, self._send_email_sync, to_email, subject, html_content
            )
        except Exception:
            pass

    def send_verification_email(self, to_email: str, verification_code: str) -> bool:
        """Enviar email de verificación de cuenta (síncrono)."""
        subject = "Verificación de cuenta - Acadify"
        verification_url = f"{self.frontend_url}/verify-email?code={verification_code}"

        html_content = f"""
        <html>
            <body>
                <h2>Verificación de cuenta</h2>
                <p>Hola,</p>
                <p>Por favor verifica tu cuenta haciendo clic en el siguiente enlace:</p>
                <p><a href="{verification_url}">Verificar cuenta</a></p>
                <p>O usa este código: <strong>{verification_code}</strong></p>
                <p>Este código expira en 10 minutos.</p>
                <p>Si no solicitaste esta verificación, ignora este email.</p>
                <br>
                <p>Saludos,<br>El equipo de Acadify</p>
            </body>
        </html>
        """

        return self.send_email(to_email, subject, html_content)

    async def send_verification_email_async(
        self, to_email: str, verification_code: str
    ) -> None:
        """Enviar email de verificación de cuenta (asíncrono - no bloquea)."""
        subject = "Verificación de cuenta - Acadify"
        verification_url = f"{self.frontend_url}/verify-email?code={verification_code}"

        html_content = f"""
        <html>
            <body>
                <h2>Verificación de cuenta</h2>
                <p>Hola,</p>
                <p>Por favor verifica tu cuenta haciendo clic en el siguiente enlace:</p>
                <p><a href="{verification_url}">Verificar cuenta</a></p>
                <p>O usa este código: <strong>{verification_code}</strong></p>
                <p>Este código expira en 10 minutos.</p>
                <p>Si no solicitaste esta verificación, ignora este email.</p>
                <br>
                <p>Saludos,<br>El equipo de Acadify</p>
            </body>
        </html>
        """

        await self.send_email_async(to_email, subject, html_content)

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Enviar email de recuperación de contraseña (síncrono)."""
        subject = "Recuperación de contraseña - Acadify"
        reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"

        html_content = f"""
        <html>
            <body>
                <h2>Recuperación de contraseña</h2>
                <p>Hola,</p>
                <p>Recibimos una solicitud para restablecer tu contraseña.</p>
                <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
                <p><a href="{reset_url}">Restablecer contraseña</a></p>
                <p>Este enlace expira en 1 hora.</p>
                <p>Si no solicitaste este cambio, ignora este email.</p>
                <br>
                <p>Saludos,<br>El equipo de Acadify</p>
            </body>
        </html>
        """

        return self.send_email(to_email, subject, html_content)

    async def send_password_reset_email_async(
        self, to_email: str, reset_token: str
    ) -> None:
        """Enviar email de recuperación de contraseña (asíncrono - no bloquea)."""
        subject = "Recuperación de contraseña - Acadify"
        reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"

        html_content = f"""
        <html>
            <body>
                <h2>Recuperación de contraseña</h2>
                <p>Hola,</p>
                <p>Recibimos una solicitud para restablecer tu contraseña.</p>
                <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
                <p><a href="{reset_url}">Restablecer contraseña</a></p>
                <p>Este enlace expira en 1 hora.</p>
                <p>Si no solicitaste este cambio, ignora este email.</p>
                <br>
                <p>Saludos,<br>El equipo de Acadify</p>
            </body>
        </html>
        """

        await self.send_email_async(to_email, subject, html_content)

    def send_2fa_code(self, to_email: str, code: str) -> bool:
        """Enviar código 2FA por email."""
        subject = "Código de verificación - Acadify"

        html_content = f"""
        <html>
            <body>
                <h2>Código de verificación</h2>
                <p>Tu código de verificación es:</p>
                <h1 style="color: #007bff; font-size: 32px; letter-spacing: 4px;">{code}</h1>
                <p>Este código expira en 10 minutos.</p>
                <p>No compartas este código con nadie.</p>
                <br>
                <p>Saludos,<br>El equipo de Acadify</p>
            </body>
        </html>
        """

        return self.send_email(to_email, subject, html_content)

    def generate_verification_code(self) -> str:
        """Generar código de verificación de 6 dígitos."""
        return f"{secrets.randbelow(900000) + 100000}"
