# backend/app/utils/logger.py
import logging
from datetime import datetime
from typing import Optional, Dict

# -------------------------------
# Configuración general del logger
# -------------------------------
logger = logging.getLogger("acadify")
logger.setLevel(logging.INFO)

# Formato estándar
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# En producción se puede agregar FileHandler o sistemas externos (Graylog, Sentry, etc.)


# -------------------------------
# Funciones de logging específicas de la app
# -------------------------------

def log_user_action(user_id: str, action: str, details: Optional[Dict] = None, level: str = "info") -> None:
    """
    Loguea acciones de usuarios en la aplicación.
    
    Args:
        user_id (str): ID del usuario que realiza la acción.
        action (str): Nombre de la acción (creación, eliminación, actualización, login, etc.).
        details (dict, opcional): Información adicional relacionada con la acción.
        level (str): Nivel de log ("info", "warning", "error", "debug").
    
    Ejemplo:
        log_user_action("123", "USER_LOGIN", {"ip": "127.0.0.1"})
    """
    log_message = {
        "user_id": user_id,
        "action": action,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }

    if level == "info":
        logger.info(f"USER_ACTION | {log_message}")
    elif level == "warning":
        logger.warning(f"USER_ACTION | {log_message}")
    elif level == "error":
        logger.error(f"USER_ACTION | {log_message}")
    elif level == "debug":
        logger.debug(f"USER_ACTION | {log_message}")
    else:
        logger.info(f"USER_ACTION | {log_message}")


def log_security_event(event: str, details: Optional[Dict] = None, level: str = "warning") -> None:
    """
    Loguea eventos de seguridad importantes.
    
    Args:
        event (str): Nombre del evento de seguridad.
        details (dict, opcional): Información adicional sobre el evento.
        level (str): Nivel de log ("info", "warning", "error", "debug").
    
    Ejemplo:
        log_security_event("FAILED_LOGIN", {"user": "123", "ip": "127.0.0.1"})
    """
    log_message = {
        "event": event,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }

    if level == "info":
        logger.info(f"SECURITY_EVENT | {log_message}")
    elif level == "warning":
        logger.warning(f"SECURITY_EVENT | {log_message}")
    elif level == "error":
        logger.error(f"SECURITY_EVENT | {log_message}")
    elif level == "debug":
        logger.debug(f"SECURITY_EVENT | {log_message}")
    else:
        logger.warning(f"SECURITY_EVENT | {log_message}")


# -------------------------------
# Función genérica para logging escalable
# -------------------------------
def log_event(category: str, message: str, details: Optional[Dict] = None, level: str = "info") -> None:
    """
    Función genérica de logging para cualquier tipo de evento.

    Args:
        category (str): Categoría del evento (USER_ACTION, SECURITY_EVENT, SYSTEM_EVENT, etc.)
        message (str): Mensaje descriptivo.
        details (dict, opcional): Datos adicionales relacionados con el evento.
        level (str): Nivel de log ("info", "warning", "error", "debug").
    """
    log_message = {
        "category": category,
        "message": message,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }

    if level == "info":
        logger.info(log_message)
    elif level == "warning":
        logger.warning(log_message)
    elif level == "error":
        logger.error(log_message)
    elif level == "debug":
        logger.debug(log_message)
    else:
        logger.info(log_message)
