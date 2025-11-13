# email_service.py
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from src.core.config import settings


def enviar_email(
    destinatario: str, asunto: str, cuerpo: str, html: bool = False
) -> None:
    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = destinatario
    msg["Subject"] = asunto
    if html:
        msg.attach(MIMEText(cuerpo, "html"))
    else:
        msg.attach(MIMEText(cuerpo, "plain"))
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_TLS:
            server.starttls()
        if settings.SMTP_USER and settings.SMTP_PASS:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg)
