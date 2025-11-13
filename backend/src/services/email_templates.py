import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.services.email_service import enviar_email


TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../templates/emails")
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def enviar_invitacion_coordinador(
    destinatario, institucion_nombre, codigo, fecha_expiracion, url_registro
) -> None:
    template = env.get_template("invitacion_coordinador.html")
    html_content = template.render(
        institucion_nombre=institucion_nombre,
        codigo=codigo,
        fecha_expiracion=fecha_expiracion.strftime("%Y-%m-%d %H:%M"),
        url_registro=url_registro,
    )
    asunto = f"Invitación para ser coordinador en {institucion_nombre}"
    enviar_email(
        destinatario=destinatario, asunto=asunto, cuerpo=html_content, html=True
    )
