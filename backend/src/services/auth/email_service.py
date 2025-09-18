<<<<<<< HEAD
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.core.config import settings


class EmailService:
    """Servicio para envío de emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.frontend_url = settings.FRONTEND_URL
    
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Crear conexión SMTP"""
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            raise ValueError("Configuración SMTP incompleta")
        
        smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
        smtp.starttls()
        smtp.login(self.smtp_user, self.smtp_password)
        return smtp
    
    def generate_reset_token(self) -> str:
        """Generar token seguro para reset de contraseña"""
        return secrets.token_urlsafe(32)
    
    def send_password_reset_email(
        self, 
        to_email: str, 
        user_name: str, 
        reset_token: str
    ) -> bool:
        """
        Enviar email de reset de contraseña
        
        Args:
            to_email: Email destinatario
            user_name: Nombre del usuario
            reset_token: Token de reset
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            reset_url = f"{self.frontend_url}/auth/password-reset?token={reset_token}"
            
            subject = "Restablecer contraseña - Acadify"
            
            html_body = f"""
            <html>
                <body>
                    <h2>Restablecimiento de contraseña</h2>
                    <p>Hola {user_name},</p>
                    <p>Recibimos una solicitud para restablecer tu contraseña en Acadify.</p>
                    <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
                    <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Restablecer Contraseña</a></p>
                    <p>Este enlace expirará en 30 minutos.</p>
                    <p>Si no solicitaste este cambio, puedes ignorar este email.</p>
                    <br>
                    <p>Saludos,<br>El equipo de Acadify</p>
                </body>
            </html>
            """
            
            text_body = f"""
            Restablecimiento de contraseña - Acadify
            
            Hola {user_name},
            
            Recibimos una solicitud para restablecer tu contraseña en Acadify.
            
            Copia y pega el siguiente enlace en tu navegador para crear una nueva contraseña:
            {reset_url}
            
            Este enlace expirará en 30 minutos.
            
            Si no solicitaste este cambio, puedes ignorar este email.
            
            Saludos,
            El equipo de Acadify
            """
            
            return self._send_email(to_email, subject, text_body, html_body)
            
        except Exception as e:
            print(f"Error enviando email de reset: {e}")
            return False
    
    def send_verification_email(
        self, 
        to_email: str, 
        user_name: str, 
        verification_token: str
    ) -> bool:
        """
        Enviar email de verificación de cuenta
        
        Args:
            to_email: Email destinatario
            user_name: Nombre del usuario
            verification_token: Token de verificación
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            verification_url = f"{self.frontend_url}/auth/verify-email?token={verification_token}"
            
            subject = "Verificar cuenta - Acadify"
            
            html_body = f"""
            <html>
                <body>
                    <h2>Verificación de cuenta</h2>
                    <p>¡Bienvenido a Acadify, {user_name}!</p>
                    <p>Para completar tu registro, necesitas verificar tu dirección de email.</p>
                    <p>Haz clic en el siguiente enlace para verificar tu cuenta:</p>
                    <p><a href="{verification_url}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verificar Cuenta</a></p>
                    <p>Este enlace expirará en 24 horas.</p>
                    <br>
                    <p>¡Bienvenido a bordo!<br>El equipo de Acadify</p>
                </body>
            </html>
            """
            
            text_body = f"""
            Verificación de cuenta - Acadify
            
            ¡Bienvenido a Acadify, {user_name}!
            
            Para completar tu registro, necesitas verificar tu dirección de email.
            
            Copia y pega el siguiente enlace en tu navegador:
            {verification_url}
            
            Este enlace expirará en 24 horas.
            
            ¡Bienvenido a bordo!
            El equipo de Acadify
            """
            
            return self._send_email(to_email, subject, text_body, html_body)
            
        except Exception as e:
            print(f"Error enviando email de verificación: {e}")
            return False
    
    def _send_email(
        self, 
        to_email: str, 
        subject: str, 
        text_body: str, 
        html_body: str = None
    ) -> bool:
        """
        Enviar email con contenido texto y/o HTML
        
        Returns:
            bool: True si se envió correctamente
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            
            # Agregar contenido texto
            text_part = MIMEText(text_body, "plain", "utf-8")
            msg.attach(text_part)
            
            # Agregar contenido HTML si se proporciona
            if html_body:
                html_part = MIMEText(html_body, "html", "utf-8")
                msg.attach(html_part)
            
            # Enviar email
            smtp = self._create_smtp_connection()
            smtp.send_message(msg)
            smtp.quit()
            
            return True
            
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False
=======
>>>>>>> origin/fix-auth
