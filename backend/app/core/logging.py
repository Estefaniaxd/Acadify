"""
Logging avanzado para Acadify
- Logs estructurados (JSON en producción, legible en desarrollo)
- Persistencia opcional en DB para errores críticos
- Alertas automáticas para errores críticos
- Middleware y decoradores para logging de funciones y requests
- Filtrado de información sensible
"""

import logging
import logging.handlers
import structlog
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import asyncio
import uuid

from .config import settings

# -----------------------------------------
# Configuración base de structlog
# -----------------------------------------
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if not settings.DEBUG else structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# -----------------------------------------
# Formateador y filtrado de seguridad
# -----------------------------------------
class AcadifyFormatter(logging.Formatter):
    SENSITIVE_FIELDS = {'password', 'token', 'secret', 'api_key', 'key', 'access_token', 'refresh_token'}

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Filtrar campos sensibles
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            filtered = {}
            for k, v in record.extra_data.items():
                filtered[k] = "[REDACTED]" if k.lower() in self.SENSITIVE_FIELDS else v
            log_data.update(filtered)

        if settings.DEBUG:
            return f"{log_data['timestamp']} | {log_data['level']:<8} | {log_data['logger']:<20} | {log_data['message']}"
        return json.dumps(log_data, ensure_ascii=False)

# -----------------------------------------
# Logger principal y loggers especializados
# -----------------------------------------
def setup_logging(
    logger_name: str = "acadify",
    db_session_factory: Optional[callable] = None
) -> logging.Logger:

    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    logger.handlers.clear()

    # Archivo rotativo principal
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE, maxBytes=50 * 1024 * 1024, backupCount=10, encoding="utf-8"
    )
    file_handler.setFormatter(AcadifyFormatter())
    logger.addHandler(file_handler)

    # Consola en desarrollo
    if settings.DEBUG:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(AcadifyFormatter())
        logger.addHandler(console_handler)

    # Logger de seguridad
    sec_logger = logging.getLogger("acadify.security")
    sec_logger.setLevel(logging.WARNING)
    sec_file = logging.handlers.RotatingFileHandler(
        log_dir / "security.log", maxBytes=20 * 1024 * 1024, backupCount=20, encoding="utf-8"
    )
    sec_file.setFormatter(AcadifyFormatter())
    sec_logger.addHandler(sec_file)

    # Logger de auditoría
    audit_logger = logging.getLogger("acadify.audit")
    audit_logger.setLevel(logging.INFO)
    audit_file = logging.handlers.RotatingFileHandler(
        log_dir / "audit.log", maxBytes=100 * 1024 * 1024, backupCount=50, encoding="utf-8"
    )
    audit_file.setFormatter(AcadifyFormatter())
    audit_logger.addHandler(audit_file)

    # Reducir logs de terceros
    for third_party in ["uvicorn", "sqlalchemy.engine", "fastapi"]:
        logging.getLogger(third_party).setLevel(logging.WARNING)

    logger.info("Sistema de logging configurado correctamente")
    return logger

app_logger = setup_logging()
security_logger = logging.getLogger("acadify.security")
audit_logger = logging.getLogger("acadify.audit")

# -----------------------------------------
# Handler opcional para persistencia en DB
# -----------------------------------------
class DatabaseLogHandler(logging.Handler):
    """Guarda logs críticos en la base de datos"""
    def __init__(self, db_session_factory):
        super().__init__()
        self.db_session_factory = db_session_factory

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            try:
                db = self.db_session_factory()
                # Aquí podrías crear un modelo LogEntry para persistir logs críticos
                # ejemplo: db.add(LogEntry.from_record(record))
                db.commit()
                db.close()
            except Exception:
                pass  # Evitar loops de logging

# -----------------------------------------
# Funciones de logging unificadas
# -----------------------------------------
def log_event(
    logger: logging.Logger,
    message: str,
    level: str = "INFO",
    extra_data: Optional[Dict[str, Any]] = None
):
    logger.log(getattr(logging, level.upper(), logging.INFO), message, extra={"extra_data": extra_data or {}})

def log_user_action(user_id: str, action: str, extra_data: Optional[Dict[str, Any]] = None):
    log_event(audit_logger, f"Acción de usuario: {action}", "INFO", {"user_id": user_id, "action": action, **(extra_data or {})})

def log_security_event(event_type: str, details: Dict[str, Any], severity: str = "WARNING"):
    log_event(security_logger, f"Evento de seguridad: {event_type}", severity, {"event_type": event_type, **details})

def log_error(error: Exception, context: str = "", user_id: Optional[str] = None, extra_data: Optional[Dict[str, Any]] = None):
    log_event(app_logger, f"Error en {context}: {str(error)}", "ERROR", {"user_id": user_id, "error_type": type(error).__name__, **(extra_data or {})})
    # Alertas automáticas: ejemplo consola
    print(f"[ALERTA] ERROR CRÍTICO: {error}")

# -----------------------------------------
# Decorador de funciones async/sync
# -----------------------------------------
def log_function_call(log_args: bool = False, log_result: bool = False):
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start = datetime.utcnow()
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.utcnow() - start).total_seconds() * 1000
                log_event(app_logger, f"Función {func.__name__} completada", "DEBUG",
                          {"duration_ms": duration, "result": str(result)[:200] if log_result else None})
                return result
            except Exception as e:
                duration = (datetime.utcnow() - start).total_seconds() * 1000
                log_error(e, f"Función {func.__name__}", extra_data={"duration_ms": duration})
                raise

        def sync_wrapper(*args, **kwargs):
            start = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start).total_seconds() * 1000
                log_event(app_logger, f"Función {func.__name__} completada", "DEBUG", {"duration_ms": duration})
                return result
            except Exception as e:
                duration = (datetime.utcnow() - start).total_seconds() * 1000
                log_error(e, f"Función {func.__name__}", extra_data={"duration_ms": duration})
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# -----------------------------------------
# Context manager para operaciones
# -----------------------------------------
class LogOperation:
    def __init__(self, operation_name: str, user_id: Optional[str] = None, extra_data: Optional[Dict[str, Any]] = None):
        self.operation_name = operation_name
        self.user_id = user_id
        self.extra_data = extra_data or {}

    def __enter__(self):
        self.start = datetime.utcnow()
        log_event(app_logger, f"Operación iniciada: {self.operation_name}", "INFO",
                  {"user_id": self.user_id, **self.extra_data})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start).total_seconds() * 1000
        if exc_type:
            log_error(exc_val, f"Operación fallida: {self.operation_name}",
                      extra_data={"user_id": self.user_id, "duration_ms": duration})
        else:
            log_event(app_logger, f"Operación completada: {self.operation_name}", "INFO",
                      {"user_id": self.user_id, "duration_ms": duration, **self.extra_data})

# -----------------------------------------
# Middleware para logging de requests HTTP
# -----------------------------------------
class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request_id = str(uuid.uuid4())[:8]
        method, path = scope["method"], scope["path"]
        client_ip = self._get_client_ip(scope)
        start_time = datetime.utcnow()

        log_event(app_logger, f"Request iniciado: {method} {path}", "INFO",
                  {"request_id": request_id, "method": method, "path": path, "ip": client_ip})

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status = message["status"]
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                level = "INFO"
                if status >= 500:
                    level = "ERROR"
                elif status >= 400:
                    level = "WARNING"
                log_event(app_logger, f"Request completado: {method} {path} - {status}", level,
                          {"request_id": request_id, "status_code": status, "duration_ms": duration})
            await send(message)

        await self.app(scope, receive, send_wrapper)

    def _get_client_ip(self, scope: Dict[str, Any]) -> str:
        for name, value in scope.get("headers", []):
            if name in (b"x-forwarded-for", b"x-real-ip"):
                return value.decode().split(",")[0].strip()
        client = scope.get("client")
        return client[0] if client else "unknown"
