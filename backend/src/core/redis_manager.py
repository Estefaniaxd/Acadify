import json
from typing import Any

import redis

from src.core.config import settings


class RedisManager:
    def __init__(self) -> None:
        """Inicializa la conexión con Redis."""
        self.redis_client = redis.Redis(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            db=getattr(settings, "REDIS_DB", 0),
            password=getattr(settings, "REDIS_PASSWORD", None),
            decode_responses=True,
        )

    # Gestión de códigos de acceso a clases
    def guardar_codigo_clase(
        self, codigo: str, clase_data: dict[str, Any], expiration: int = 3600
    ) -> bool:
        """Guarda información de código de clase en Redis con expiración."""
        try:
            key = f"codigo_clase:{codigo}"
            self.redis_client.setex(key, expiration, json.dumps(clase_data))
            return True
        except Exception:
            return False

    def obtener_clase_por_codigo(self, codigo: str) -> dict[str, Any] | None:
        """Obtiene información de clase por código."""
        try:
            key = f"codigo_clase:{codigo}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    def invalidar_codigo_clase(self, codigo: str) -> bool:
        """Invalida un código de clase."""
        try:
            key = f"codigo_clase:{codigo}"
            return bool(self.redis_client.delete(key))
        except Exception:
            return False

    # Cache de material educativo
    def cache_material(
        self, material_id: str, material_data: dict[str, Any], expiration: int = 1800
    ) -> bool:
        """Cachea información de material educativo."""
        try:
            key = f"material:{material_id}"
            self.redis_client.setex(key, expiration, json.dumps(material_data))
            return True
        except Exception:
            return False

    def obtener_material_cache(self, material_id: str) -> dict[str, Any] | None:
        """Obtiene material del cache."""
        try:
            key = f"material:{material_id}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    def invalidar_cache_material(self, material_id: str) -> bool:
        """Invalida cache de material."""
        try:
            key = f"material:{material_id}"
            return bool(self.redis_client.delete(key))
        except Exception:
            return False

    # Cache de cursos
    def cache_curso(
        self, curso_id: str, curso_data: dict[str, Any], expiration: int = 3600
    ) -> bool:
        """Cachea información de curso."""
        try:
            key = f"curso:{curso_id}"
            self.redis_client.setex(key, expiration, json.dumps(curso_data))
            return True
        except Exception:
            return False

    def obtener_curso_cache(self, curso_id: str) -> dict[str, Any] | None:
        """Obtiene curso del cache."""
        try:
            key = f"curso:{curso_id}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    def invalidar_cache_curso(self, curso_id: str) -> bool:
        """Invalida cache de curso."""
        try:
            key = f"curso:{curso_id}"
            return bool(self.redis_client.delete(key))
        except Exception:
            return False

    # Sesiones de estudiantes en clases
    def registrar_sesion_estudiante(
        self,
        clase_id: str,
        estudiante_id: str,
        session_data: dict[str, Any],
        expiration: int = 7200,  # 2 horas
    ) -> bool:
        """Registra sesión activa de estudiante en clase."""
        try:
            key = f"sesion_clase:{clase_id}:{estudiante_id}"
            self.redis_client.setex(key, expiration, json.dumps(session_data))

            # Agregar a lista de estudiantes activos en la clase
            list_key = f"estudiantes_activos:{clase_id}"
            self.redis_client.sadd(list_key, estudiante_id)
            self.redis_client.expire(list_key, expiration)

            return True
        except Exception:
            return False

    def obtener_estudiantes_activos(self, clase_id: str) -> list[str]:
        """Obtiene lista de estudiantes activos en una clase."""
        try:
            key = f"estudiantes_activos:{clase_id}"
            return list(self.redis_client.smembers(key))
        except Exception:
            return []

    def cerrar_sesion_estudiante(self, clase_id: str, estudiante_id: str) -> bool:
        """Cierra sesión de estudiante en clase."""
        try:
            # Eliminar sesión individual
            session_key = f"sesion_clase:{clase_id}:{estudiante_id}"
            self.redis_client.delete(session_key)

            # Remover de lista de activos
            list_key = f"estudiantes_activos:{clase_id}"
            self.redis_client.srem(list_key, estudiante_id)

            return True
        except Exception:
            return False

    # Estadísticas en tiempo real
    def incrementar_contador(self, key: str, amount: int = 1) -> int:
        """Incrementa un contador."""
        try:
            return self.redis_client.incr(key, amount)
        except Exception:
            return 0

    def obtener_contador(self, key: str) -> int:
        """Obtiene valor de contador."""
        try:
            value = self.redis_client.get(key)
            return int(value) if value else 0
        except Exception:
            return 0

    def resetear_contador(self, key: str) -> bool:
        """Resetea un contador."""
        try:
            self.redis_client.set(key, 0)
            return True
        except Exception:
            return False

    # Notificaciones en tiempo real
    def publicar_notificacion(self, canal: str, mensaje: dict[str, Any]) -> bool:
        """Publica una notificación en un canal."""
        try:
            self.redis_client.publish(canal, json.dumps(mensaje))
            return True
        except Exception:
            return False

    def suscribirse_canal(self, canal: str):
        """Se suscribe a un canal para recibir notificaciones."""
        try:
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe(canal)
            return pubsub
        except Exception:
            return None

    # Utilidades generales
    def set_with_expiry(self, key: str, value: Any, expiration: int) -> bool:
        """Guarda un valor con expiración."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            self.redis_client.setex(key, expiration, value)
            return True
        except Exception:
            return False

    def get_value(self, key: str) -> Any | None:
        """Obtiene un valor."""
        try:
            value = self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception:
            return None

    def delete_key(self, key: str) -> bool:
        """Elimina una clave."""
        try:
            return bool(self.redis_client.delete(key))
        except Exception:
            return False

    def existe_key(self, key: str) -> bool:
        """Verifica si existe una clave."""
        try:
            return bool(self.redis_client.exists(key))
        except Exception:
            return False

    def limpiar_cache_patron(self, patron: str) -> int:
        """Limpia cache basado en un patrón."""
        try:
            keys = self.redis_client.keys(patron)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception:
            return 0

    def ping(self) -> bool:
        """Verifica conectividad con Redis."""
        try:
            return self.redis_client.ping()
        except Exception:
            return False


# Instancia global
redis_manager = RedisManager()
