"""
Sistema de notificaciones por email y tareas programadas
Incluye notificaciones de vencimiento de tareas, menciones y resúmenes
"""

import asyncio
import smtplib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template
import logging

from sqlalchemy.orm import Session
from celery import Celery
from celery.schedules import crontab

from db.session import SessionLocal
from core.config import settings
from models.academic.tarea import Tarea, EstadoTarea
from models.communication.chat import Notificacion, ConfiguracionNotificaciones
from crud.academic.tarea import crud_tarea
from crud.communication.chat import crud_notificacion, crud_config_notificaciones
from schemas.communication.chat_schemas import NotificacionCreate

logger = logging.getLogger(__name__)

# Configurar Celery para tareas asíncronas
celery_app = Celery(
    "acadify_notifications",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configurar tareas periódicas
celery_app.conf.beat_schedule = {
    'check-task-deadlines': {
        'task': 'services.notification_service.check_task_deadlines',
        'schedule': crontab(minute=0),  # Cada hora
    },
    'check-urgent-deadlines': {
        'task': 'services.notification_service.check_urgent_deadlines', 
        'schedule': crontab(minute='*/15'),  # Cada 15 minutos
    },
    'send-daily-summary': {
        'task': 'services.notification_service.send_daily_summary',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM todos los días
    },
    'cleanup-old-notifications': {
        'task': 'services.notification_service.cleanup_old_notifications',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Domingo 2:00 AM
    }
}

celery_app.conf.timezone = 'America/Bogota'


class EmailService:
    """Servicio para envío de emails"""
    
    def __init__(self):
        self.smtp_server = settings.EMAIL_HOST
        self.smtp_port = settings.EMAIL_PORT
        self.username = settings.EMAIL_USER
        self.password = settings.EMAIL_PASSWORD
        self.use_tls = settings.EMAIL_USE_TLS
        self.from_email = settings.EMAIL_FROM
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: str = None,
        attachments: List[Dict[str, Any]] = None
    ) -> bool:
        """Enviar email"""
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Agregar contenido de texto plano si se proporciona
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)
            
            # Agregar contenido HTML
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)
            
            # Agregar archivos adjuntos
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)
            
            # Conectar y enviar
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            logger.info(f"Email enviado exitosamente a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {e}")
            return False
    
    def send_bulk_email(self, emails: List[Dict[str, Any]]) -> Dict[str, int]:
        """Enviar emails masivos"""
        results = {"sent": 0, "failed": 0}
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            
            for email_data in emails:
                try:
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = email_data['subject']
                    msg['From'] = self.from_email
                    msg['To'] = email_data['to_email']
                    
                    if email_data.get('text_content'):
                        part1 = MIMEText(email_data['text_content'], 'plain', 'utf-8')
                        msg.attach(part1)
                    
                    part2 = MIMEText(email_data['html_content'], 'html', 'utf-8')
                    msg.attach(part2)
                    
                    server.sendmail(self.from_email, email_data['to_email'], msg.as_string())
                    results["sent"] += 1
                    
                except Exception as e:
                    logger.error(f"Error enviando email individual: {e}")
                    results["failed"] += 1
            
            server.quit()
            
        except Exception as e:
            logger.error(f"Error en envío masivo: {e}")
            results["failed"] = len(emails) - results["sent"]
        
        return results


class NotificationService:
    """Servicio principal de notificaciones"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    def create_notification(
        self, 
        db: Session,
        usuario_id: str,
        titulo: str,
        mensaje: str,
        tipo_notificacion: str,
        **kwargs
    ) -> Notificacion:
        """Crear notificación en base de datos"""
        notif_data = NotificacionCreate(
            usuario_id=usuario_id,
            titulo=titulo,
            mensaje=mensaje,
            tipo_notificacion=tipo_notificacion,
            **kwargs
        )
        
        return crud_notificacion.create(db=db, obj_in=notif_data)
    
    def should_send_email_notification(
        self, 
        db: Session,
        usuario_id: str,
        tipo_notificacion: str
    ) -> bool:
        """Verificar si debe enviar notificación por email según configuración"""
        config = crud_config_notificaciones.get_by_usuario(
            db=db, 
            usuario_id=usuario_id
        )
        
        if not config.notificaciones_activas:
            return False
        
        # Verificar horario permitido
        now = datetime.now().time()
        hora_inicio = datetime.strptime(config.horario_inicio, "%H:%M").time()
        hora_fin = datetime.strptime(config.horario_fin, "%H:%M").time()
        
        if not (hora_inicio <= now <= hora_fin):
            return False
        
        # Verificar día de la semana (1=Lun, 7=Dom)
        dia_actual = datetime.now().weekday() + 1  # Python: 0=Lun, 6=Dom
        if dia_actual not in config.dias_activos:
            return False
        
        # Verificar tipo específico de notificación
        if tipo_notificacion == "tarea_vencimiento_24h":
            return config.tareas_vencimiento_24h and config.urgentes_email
        elif tipo_notificacion == "tarea_vencimiento_1h":
            return config.tareas_vencimiento_1h and config.urgentes_email
        elif tipo_notificacion == "mencion":
            return config.menciones and config.menciones_email
        elif tipo_notificacion == "tarea_nueva":
            return config.tareas_nuevas
        elif tipo_notificacion == "tarea_calificada":
            return config.tareas_calificadas
        elif tipo_notificacion == "mensaje_directo":
            return config.mensajes_directos
        
        return config.urgentes_email  # Por defecto para otros tipos
    
    def render_email_template(
        self, 
        template_name: str, 
        context: Dict[str, Any]
    ) -> tuple[str, str]:
        """Renderizar template de email"""
        # Templates básicos - en producción usar archivos separados
        templates = {
            "task_deadline_24h": {
                "subject": "⏰ Tarea vence en 24 horas: {{ tarea.titulo }}",
                "html": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">⏰ Recordatorio de Tarea</h1>
                    </div>
                    <div style="background: white; padding: 20px; border: 1px solid #ddd; border-radius: 0 0 8px 8px;">
                        <h2 style="color: #333; margin-top: 0;">{{ tarea.titulo }}</h2>
                        <div style="background: #fff3cd; border: 1px solid #ffeeba; padding: 15px; border-radius: 6px; margin: 15px 0;">
                            <strong>⚠️ Tu tarea vence en menos de 24 horas</strong>
                        </div>
                        <p><strong>Fecha límite:</strong> {{ tarea.fecha_limite.strftime('%d/%m/%Y %H:%M') }}</p>
                        <p><strong>Curso:</strong> {{ tarea.grupo_nombre or 'N/A' }}</p>
                        {% if tarea.descripcion %}
                        <p><strong>Descripción:</strong></p>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 6px;">
                            {{ tarea.descripcion }}
                        </div>
                        {% endif %}
                        <div style="margin: 25px 0;">
                            <a href="{{ base_url }}/tareas/{{ tarea.id }}" 
                               style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                                Ver Tarea
                            </a>
                        </div>
                        <p style="color: #666; font-size: 14px;">
                            Este es un recordatorio automático de Acadify. Si no deseas recibir estos emails, 
                            puedes <a href="{{ base_url }}/configuracion/notificaciones">cambiar tus preferencias</a>.
                        </p>
                    </div>
                </div>
                """,
                "text": """
                RECORDATORIO DE TAREA - ACADIFY
                
                Tu tarea "{{ tarea.titulo }}" vence en menos de 24 horas.
                
                Fecha límite: {{ tarea.fecha_limite.strftime('%d/%m/%Y %H:%M') }}
                Curso: {{ tarea.grupo_nombre or 'N/A' }}
                
                {% if tarea.descripcion %}
                Descripción: {{ tarea.descripcion }}
                {% endif %}
                
                Ver tarea: {{ base_url }}/tareas/{{ tarea.id }}
                
                Configurar notificaciones: {{ base_url }}/configuracion/notificaciones
                """
            },
            "task_deadline_1h": {
                "subject": "🚨 URGENTE: Tarea vence en 1 hora: {{ tarea.titulo }}",
                "html": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">🚨 ALERTA URGENTE</h1>
                    </div>
                    <div style="background: white; padding: 20px; border: 1px solid #ddd; border-radius: 0 0 8px 8px;">
                        <h2 style="color: #dc3545; margin-top: 0;">{{ tarea.titulo }}</h2>
                        <div style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 6px; margin: 15px 0; color: #721c24;">
                            <strong>🚨 TU TAREA VENCE EN MENOS DE 1 HORA</strong><br>
                            Fecha límite: {{ tarea.fecha_limite.strftime('%d/%m/%Y %H:%M') }}
                        </div>
                        <div style="margin: 25px 0;">
                            <a href="{{ base_url }}/tareas/{{ tarea.id }}" 
                               style="background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                                ENTREGAR AHORA
                            </a>
                        </div>
                        <p style="color: #666; font-size: 14px;">
                            Este es un recordatorio urgente de Acadify.
                        </p>
                    </div>
                </div>
                """
            },
            "mention_notification": {
                "subject": "💬 Te mencionaron en {{ sala_nombre }}",
                "html": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #4ecdc4 0%, #56ab2f 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">💬 Nueva Mención</h1>
                    </div>
                    <div style="background: white; padding: 20px; border: 1px solid #ddd; border-radius: 0 0 8px 8px;">
                        <p><strong>{{ autor_nombre }}</strong> te mencionó en <strong>{{ sala_nombre }}</strong></p>
                        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #4ecdc4; margin: 15px 0;">
                            {{ mensaje_contenido }}
                        </div>
                        <div style="margin: 25px 0;">
                            <a href="{{ base_url }}/salas/{{ sala_id }}" 
                               style="background: #4ecdc4; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                                Ver Conversación
                            </a>
                        </div>
                    </div>
                </div>
                """
            },
            "daily_summary": {
                "subject": "📊 Tu resumen diario - Acadify",
                "html": """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                        <h1 style="margin: 0; font-size: 24px;">📊 Tu Resumen Diario</h1>
                        <p style="margin: 5px 0 0 0; opacity: 0.9;">{{ fecha.strftime('%d de %B, %Y') }}</p>
                    </div>
                    <div style="background: white; padding: 20px; border: 1px solid #ddd; border-radius: 0 0 8px 8px;">
                        
                        {% if tareas_vencen_pronto %}
                        <h3 style="color: #dc3545;">⏰ Tareas que vencen pronto</h3>
                        <ul>
                        {% for tarea in tareas_vencen_pronto %}
                            <li>{{ tarea.titulo }} - vence {{ tarea.fecha_limite.strftime('%d/%m %H:%M') }}</li>
                        {% endfor %}
                        </ul>
                        {% endif %}
                        
                        {% if mensajes_nuevos > 0 %}
                        <h3 style="color: #007bff;">💬 Actividad en chat</h3>
                        <p>Tienes {{ mensajes_nuevos }} mensajes nuevos sin leer.</p>
                        {% endif %}
                        
                        {% if notificaciones_pendientes > 0 %}
                        <h3 style="color: #28a745;">🔔 Notificaciones</h3>
                        <p>{{ notificaciones_pendientes }} notificaciones pendientes de revisar.</p>
                        {% endif %}
                        
                        <div style="margin: 25px 0;">
                            <a href="{{ base_url }}/dashboard" 
                               style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                                Ir a mi Dashboard
                            </a>
                        </div>
                    </div>
                </div>
                """
            }
        }
        
        template_data = templates.get(template_name, {})
        
        # Renderizar subject
        subject_template = Template(template_data.get("subject", "Notificación de Acadify"))
        subject = subject_template.render(**context)
        
        # Renderizar HTML
        html_template = Template(template_data.get("html", "<p>{{ mensaje }}</p>"))
        html_content = html_template.render(**context)
        
        # Renderizar texto plano si existe
        text_content = ""
        if "text" in template_data:
            text_template = Template(template_data["text"])
            text_content = text_template.render(**context)
        
        return subject, html_content, text_content


# Instancia global del servicio
notification_service = NotificationService()


# ==================== TAREAS CELERY ====================

@celery_app.task(bind=True, max_retries=3)
def check_task_deadlines(self):
    """Verificar tareas que vencen en 24 horas"""
    try:
        db = SessionLocal()
        
        # Calcular rango de tiempo (23-25 horas desde ahora)
        now = datetime.now()
        desde = now + timedelta(hours=23)
        hasta = now + timedelta(hours=25)
        
        # Buscar tareas que vencen en este rango
        tareas = (
            db.query(Tarea)
            .filter(
                Tarea.fecha_limite.between(desde, hasta),
                Tarea.estado.in_([EstadoTarea.PUBLICADA, EstadoTarea.EN_PROGRESO])
            )
            .all()
        )
        
        emails_sent = 0
        notifications_created = 0
        
        for tarea in tareas:
            # Obtener estudiantes asignados (simplificado)
            # TODO: Implementar lógica real para obtener estudiantes de una tarea
            estudiantes = []  # get_students_for_task(tarea.id)
            
            for estudiante in estudiantes:
                # Verificar si debe enviar email
                if notification_service.should_send_email_notification(
                    db, str(estudiante.id), "tarea_vencimiento_24h"
                ):
                    # Crear contexto para el template
                    context = {
                        "tarea": tarea,
                        "estudiante": estudiante,
                        "base_url": settings.FRONTEND_URL
                    }
                    
                    # Renderizar email
                    subject, html_content, text_content = notification_service.render_email_template(
                        "task_deadline_24h", context
                    )
                    
                    # Enviar email
                    if notification_service.email_service.send_email(
                        to_email=estudiante.email,
                        subject=subject,
                        html_content=html_content,
                        text_content=text_content
                    ):
                        emails_sent += 1
                
                # Crear notificación en app
                notification_service.create_notification(
                    db=db,
                    usuario_id=str(estudiante.id),
                    titulo=f"Tarea vence en 24 horas: {tarea.titulo}",
                    mensaje=f"Tu tarea '{tarea.titulo}' vence el {tarea.fecha_limite.strftime('%d/%m/%Y a las %H:%M')}",
                    tipo_notificacion="tarea_vencimiento_24h",
                    tarea_id=tarea.id,
                    url_accion=f"/tareas/{tarea.id}",
                    icono="clock",
                    color="#FFC107"
                )
                notifications_created += 1
        
        db.close()
        
        logger.info(f"Check deadlines 24h: {emails_sent} emails enviados, {notifications_created} notificaciones creadas")
        return {"emails_sent": emails_sent, "notifications_created": notifications_created}
        
    except Exception as e:
        logger.error(f"Error en check_task_deadlines: {e}")
        db.rollback()
        db.close()
        raise self.retry(countdown=300, exc=e)  # Reintentar en 5 minutos


@celery_app.task(bind=True, max_retries=3)
def check_urgent_deadlines(self):
    """Verificar tareas que vencen en 1 hora"""
    try:
        db = SessionLocal()
        
        # Calcular rango de tiempo (45 min - 75 min desde ahora)
        now = datetime.now()
        desde = now + timedelta(minutes=45)
        hasta = now + timedelta(minutes=75)
        
        # Buscar tareas urgentes
        tareas = (
            db.query(Tarea)
            .filter(
                Tarea.fecha_limite.between(desde, hasta),
                Tarea.estado.in_([EstadoTarea.PUBLICADA, EstadoTarea.EN_PROGRESO])
            )
            .all()
        )
        
        emails_sent = 0
        notifications_created = 0
        
        for tarea in tareas:
            # Obtener estudiantes asignados
            estudiantes = []  # get_students_for_task(tarea.id)
            
            for estudiante in estudiantes:
                # Verificar configuración para notificaciones urgentes
                if notification_service.should_send_email_notification(
                    db, str(estudiante.id), "tarea_vencimiento_1h"
                ):
                    context = {
                        "tarea": tarea,
                        "estudiante": estudiante,
                        "base_url": settings.FRONTEND_URL
                    }
                    
                    subject, html_content, _ = notification_service.render_email_template(
                        "task_deadline_1h", context
                    )
                    
                    if notification_service.email_service.send_email(
                        to_email=estudiante.email,
                        subject=subject,
                        html_content=html_content
                    ):
                        emails_sent += 1
                
                # Crear notificación urgente
                notification_service.create_notification(
                    db=db,
                    usuario_id=str(estudiante.id),
                    titulo=f"🚨 URGENTE: Tarea vence en 1 hora",
                    mensaje=f"Tu tarea '{tarea.titulo}' vence el {tarea.fecha_limite.strftime('%d/%m/%Y a las %H:%M')}",
                    tipo_notificacion="tarea_vencimiento_1h",
                    tarea_id=tarea.id,
                    url_accion=f"/tareas/{tarea.id}",
                    icono="exclamation-triangle",
                    color="#DC3545"
                )
                notifications_created += 1
        
        db.close()
        
        logger.info(f"Check urgent deadlines: {emails_sent} emails enviados, {notifications_created} notificaciones creadas")
        return {"emails_sent": emails_sent, "notifications_created": notifications_created}
        
    except Exception as e:
        logger.error(f"Error en check_urgent_deadlines: {e}")
        db.rollback()
        db.close()
        raise self.retry(countdown=60, exc=e)  # Reintentar en 1 minuto


@celery_app.task(bind=True)
def send_daily_summary(self):
    """Enviar resumen diario a usuarios que lo tengan activado"""
    try:
        db = SessionLocal()
        
        # Obtener usuarios con resumen diario activado
        configs = (
            db.query(ConfiguracionNotificaciones)
            .filter(ConfiguracionNotificaciones.resumen_diario_email == True)
            .all()
        )
        
        emails_sent = 0
        
        for config in configs:
            try:
                # Preparar datos del resumen
                context = {
                    "fecha": datetime.now(),
                    "base_url": settings.FRONTEND_URL,
                    "tareas_vencen_pronto": [],  # get_upcoming_tasks(config.usuario_id),
                    "mensajes_nuevos": 0,  # get_unread_messages_count(config.usuario_id),
                    "notificaciones_pendientes": 0  # get_unread_notifications_count(config.usuario_id)
                }
                
                subject, html_content, _ = notification_service.render_email_template(
                    "daily_summary", context
                )
                
                # TODO: Obtener email del usuario
                user_email = "user@example.com"
                
                if notification_service.email_service.send_email(
                    to_email=user_email,
                    subject=subject,
                    html_content=html_content
                ):
                    emails_sent += 1
                    
            except Exception as e:
                logger.error(f"Error enviando resumen diario a usuario {config.usuario_id}: {e}")
                continue
        
        db.close()
        
        logger.info(f"Daily summary: {emails_sent} resúmenes enviados")
        return {"emails_sent": emails_sent}
        
    except Exception as e:
        logger.error(f"Error en send_daily_summary: {e}")
        return {"error": str(e)}


@celery_app.task
def cleanup_old_notifications():
    """Limpiar notificaciones antiguas"""
    try:
        db = SessionLocal()
        
        # Eliminar notificaciones leídas de más de 30 días
        cutoff_date = datetime.now() - timedelta(days=30)
        
        deleted_count = (
            db.query(Notificacion)
            .filter(
                Notificacion.leida == True,
                Notificacion.fecha_creacion < cutoff_date
            )
            .delete(synchronize_session=False)
        )
        
        db.commit()
        db.close()
        
        logger.info(f"Cleanup: {deleted_count} notificaciones antiguas eliminadas")
        return {"deleted_count": deleted_count}
        
    except Exception as e:
        logger.error(f"Error en cleanup_old_notifications: {e}")
        return {"error": str(e)}


@celery_app.task
def send_mention_notification(usuario_id: str, mensaje_id: str, sala_id: str):
    """Enviar notificación de mención por email"""
    try:
        db = SessionLocal()
        
        # Verificar si debe enviar email
        if notification_service.should_send_email_notification(
            db, usuario_id, "mencion"
        ):
            # Obtener datos necesarios
            # TODO: Implementar obtención de datos reales
            context = {
                "autor_nombre": "Usuario",
                "sala_nombre": "Sala de Chat",
                "mensaje_contenido": "Contenido del mensaje...",
                "sala_id": sala_id,
                "base_url": settings.FRONTEND_URL
            }
            
            subject, html_content, _ = notification_service.render_email_template(
                "mention_notification", context
            )
            
            # TODO: Obtener email del usuario
            user_email = "user@example.com"
            
            notification_service.email_service.send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content
            )
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error enviando notificación de mención: {e}")


# Función auxiliar para iniciar el worker de Celery
def start_celery_worker():
    """Iniciar worker de Celery"""
    celery_app.start(['worker', '--loglevel=info', '--beat'])


# Función auxiliar para testing
def send_test_email(to_email: str) -> bool:
    """Enviar email de prueba"""
    email_service = EmailService()
    
    html_content = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #007bff;">🎉 Email de Prueba - Acadify</h1>
        <p>Si recibes este email, la configuración de notificaciones está funcionando correctamente.</p>
        <p><strong>Fecha:</strong> {}</p>
    </div>
    """.format(datetime.now().strftime('%d/%m/%Y %H:%M'))
    
    return email_service.send_email(
        to_email=to_email,
        subject="✅ Prueba de Notificaciones - Acadify",
        html_content=html_content,
        text_content="Este es un email de prueba de Acadify. Configuración funcionando correctamente."
    )