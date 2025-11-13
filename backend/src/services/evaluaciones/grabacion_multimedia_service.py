"""Servicio de Grabación Multimedia para Evaluaciones.
Funcionalidades:
- Grabación de cámara en tiempo real
- Grabación de audio
- Capturas periódicas (snapshots)
- Verificación de identidad facial
- Detección de múltiples personas
- Almacenamiento seguro y encriptado
- Eliminación automática según política de retención.
"""

import base64
from datetime import UTC, datetime, timedelta
import hashlib
from typing import Any
from uuid import UUID


try:
    import face_recognition  # Para detección facial
except ImportError:
    face_recognition = None  # Mock para tests
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None  # Mock para tests
try:
    import cv2
except ImportError:
    cv2 = None  # Mock para tests
try:
    import numpy as np
except ImportError:
    np = None  # Mock para tests

from src.core.config import settings
from src.core.storage import storage_manager


class GrabacionMultimediaService:
    """Servicio para grabación y análisis multimedia durante evaluaciones."""

    def __init__(self) -> None:
        """Inicializa el servicio."""
        self.storage = storage_manager
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)

    # ==========================================
    # GESTIÓN DE CAPTURAS DE WEBCAM
    # ==========================================

    async def guardar_captura_webcam(
        self,
        intento_id: UUID,
        imagen_base64: str,
        timestamp: datetime,
        metadata: dict[str, Any] | None = None,
        encriptar: bool = True,
    ) -> dict[str, Any]:
        """Guarda una captura de webcam del estudiante.

        Args:
            intento_id: ID del intento de examen
            imagen_base64: Imagen en formato base64
            timestamp: Momento de la captura
            metadata: Metadatos adicionales
            encriptar: Si se debe encriptar la imagen

        Returns:
            {
                "captura_id": "...",
                "ruta": "...",
                "timestamp": "...",
                "analisis": {...}  # Análisis facial si está habilitado
            }
        """
        try:
            # Decodificar imagen
            imagen_bytes = base64.b64decode(imagen_base64)

            # Generar ID único para la captura
            captura_id = hashlib.sha256(
                f"{intento_id}{timestamp}".encode()
            ).hexdigest()[:16]

            # Analizar imagen (detección facial)
            analisis = await self._analizar_imagen_webcam(imagen_bytes)

            # Encriptar si está habilitado
            if encriptar:
                imagen_bytes = self.fernet.encrypt(imagen_bytes)
                extension = ".enc"
            else:
                extension = ".jpg"

            # Construir ruta de almacenamiento
            ruta = f"evaluaciones/capturas/{intento_id}/{captura_id}{extension}"

            # Guardar en storage
            url = await self.storage.upload_file(
                file_content=imagen_bytes,
                file_path=ruta,
                content_type=(
                    "image/jpeg" if not encriptar else "application/octet-stream"
                ),
            )

            # Guardar metadata
            metadata_completa = {
                "captura_id": captura_id,
                "intento_id": str(intento_id),
                "timestamp": timestamp.isoformat(),
                "ruta": ruta,
                "url": url,
                "encriptada": encriptar,
                "analisis_facial": analisis,
                "metadata_adicional": metadata or {},
            }

            await self._guardar_metadata_captura(
                intento_id, captura_id, metadata_completa
            )

            return {
                "captura_id": captura_id,
                "ruta": ruta,
                "url": url,
                "timestamp": timestamp.isoformat(),
                "analisis": analisis,
                "exito": True,
            }

        except Exception as e:
            return {"exito": False, "error": str(e)}

    async def _analizar_imagen_webcam(self, imagen_bytes: bytes) -> dict[str, Any]:
        """Analiza una imagen de webcam para detectar:
        - Número de personas
        - Ubicación de rostros
        - Identidad (si hay referencia).
        """
        try:
            # Convertir bytes a numpy array para OpenCV
            nparr = np.frombuffer(imagen_bytes, np.uint8)
            imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Convertir BGR a RGB (face_recognition usa RGB)
            rgb_imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

            # Detectar rostros
            ubicaciones_rostros = face_recognition.face_locations(rgb_imagen)
            encodings_rostros = face_recognition.face_encodings(
                rgb_imagen, ubicaciones_rostros
            )

            num_personas = len(ubicaciones_rostros)

            # Analizar calidad de la imagen
            calidad = self._evaluar_calidad_imagen(imagen)

            return {
                "num_personas_detectadas": num_personas,
                "rostros_ubicaciones": [
                    {"top": loc[0], "right": loc[1], "bottom": loc[2], "left": loc[3]}
                    for loc in ubicaciones_rostros
                ],
                "rostros_encodings": [enc.tolist() for enc in encodings_rostros],
                "calidad_imagen": calidad,
                "alerta": self._generar_alerta_analisis(num_personas, calidad),
            }

        except Exception as e:
            return {
                "error": str(e),
                "num_personas_detectadas": 0,
                "analisis_fallido": True,
            }

    def _evaluar_calidad_imagen(self, imagen: np.ndarray) -> dict[str, Any]:
        """Evalúa la calidad de una imagen (brillo, contraste, nitidez)."""
        # Convertir a escala de grises
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

        # Calcular brillo (promedio de intensidad)
        brillo = np.mean(gris)

        # Calcular nitidez (usando Laplacian)
        nitidez = cv2.Laplacian(gris, cv2.CV_64F).var()

        return {
            "brillo": float(brillo),  # 0-255
            "nitidez": float(nitidez),  # Valores altos = más nítida
            "es_aceptable": brillo > 50 and brillo < 200 and nitidez > 100,
        }

    def _generar_alerta_analisis(
        self, num_personas: int, calidad: dict[str, Any]
    ) -> str | None:
        """Genera alertas basadas en el análisis."""
        if num_personas == 0:
            return "ALERTA: No se detectó ninguna persona en la imagen"
        if num_personas > 1:
            return f"ALERTA: Se detectaron {num_personas} personas en la imagen"
        if not calidad.get("es_aceptable", True):
            return "ADVERTENCIA: Calidad de imagen deficiente (iluminación o enfoque)"

        return None

    # ==========================================
    # VERIFICACIÓN DE IDENTIDAD FACIAL
    # ==========================================

    async def verificar_identidad_facial(
        self,
        imagen_actual: str,  # base64
        imagen_referencia: str,  # base64 de foto de perfil
        umbral_similitud: float = 0.6,
    ) -> dict[str, Any]:
        """Verifica que la persona en la imagen actual sea la misma que en la referencia.

        Returns:
            {
                "coincide": bool,
                "similitud": 0.0-1.0,
                "confianza": "baja|media|alta",
                "mensaje": "..."
            }
        """
        try:
            # Decodificar imágenes
            img_actual_bytes = base64.b64decode(imagen_actual)
            img_ref_bytes = base64.b64decode(imagen_referencia)

            # Convertir a arrays
            nparr_actual = np.frombuffer(img_actual_bytes, np.uint8)
            nparr_ref = np.frombuffer(img_ref_bytes, np.uint8)

            img_actual = cv2.imdecode(nparr_actual, cv2.IMREAD_COLOR)
            img_ref = cv2.imdecode(nparr_ref, cv2.IMREAD_COLOR)

            # Convertir a RGB
            rgb_actual = cv2.cvtColor(img_actual, cv2.COLOR_BGR2RGB)
            rgb_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2RGB)

            # Obtener encodings faciales
            encoding_actual = face_recognition.face_encodings(rgb_actual)
            encoding_ref = face_recognition.face_encodings(rgb_ref)

            if not encoding_actual or not encoding_ref:
                return {
                    "coincide": False,
                    "similitud": 0.0,
                    "confianza": "baja",
                    "mensaje": "No se pudo detectar rostro en una o ambas imágenes",
                    "error": "rostro_no_detectado",
                }

            # Comparar rostros
            distancia = face_recognition.face_distance(
                [encoding_ref[0]], encoding_actual[0]
            )[0]
            similitud = 1 - distancia  # Convertir distancia a similitud

            coincide = similitud >= umbral_similitud

            # Determinar confianza
            if similitud >= 0.8:
                confianza = "alta"
            elif similitud >= 0.6:
                confianza = "media"
            else:
                confianza = "baja"

            mensaje = (
                "Identidad verificada correctamente"
                if coincide
                else "La identidad no coincide con la esperada"
            )

            return {
                "coincide": coincide,
                "similitud": float(similitud),
                "confianza": confianza,
                "mensaje": mensaje,
                "umbral_usado": umbral_similitud,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            return {
                "coincide": False,
                "similitud": 0.0,
                "confianza": "baja",
                "mensaje": f"Error al verificar identidad: {e!s}",
                "error": str(e),
            }

    # ==========================================
    # GRABACIÓN DE VIDEO COMPLETO
    # ==========================================

    async def iniciar_grabacion_video(
        self, intento_id: UUID, duracion_maxima_minutos: int = 180
    ) -> dict[str, Any]:
        """Inicia una grabación de video continua para toda la evaluación.

        Returns:
            {
                "sesion_id": "...",
                "estado": "grabando",
                "timestamp_inicio": "..."
            }
        """
        sesion_id = hashlib.sha256(
            f"{intento_id}{datetime.now(UTC)}".encode()
        ).hexdigest()[:16]

        sesion_info = {
            "sesion_id": sesion_id,
            "intento_id": str(intento_id),
            "timestamp_inicio": datetime.now(UTC).isoformat(),
            "duracion_maxima_minutos": duracion_maxima_minutos,
            "estado": "grabando",
            "chunks_recibidos": 0,
            "ruta_base": f"evaluaciones/videos/{intento_id}/{sesion_id}",
        }

        # Guardar info de sesión (en Redis o DB)
        await self._guardar_sesion_grabacion(sesion_id, sesion_info)

        return {
            "sesion_id": sesion_id,
            "estado": "grabando",
            "timestamp_inicio": sesion_info["timestamp_inicio"],
            "instrucciones": "Enviar chunks de video cada 10 segundos",
        }

    async def procesar_chunk_video(
        self, sesion_id: str, chunk_data: bytes, chunk_numero: int
    ) -> dict[str, Any]:
        """Procesa un chunk de video de la grabación en progreso."""
        try:
            sesion = await self._obtener_sesion_grabacion(sesion_id)

            if not sesion:
                return {"error": "Sesión no encontrada"}

            # Guardar chunk
            ruta_chunk = f"{sesion['ruta_base']}/chunk_{chunk_numero:04d}.webm"

            await self.storage.upload_file(
                file_content=chunk_data, file_path=ruta_chunk, content_type="video/webm"
            )

            # Actualizar contador
            sesion["chunks_recibidos"] = chunk_numero
            await self._actualizar_sesion_grabacion(sesion_id, sesion)

            return {
                "exito": True,
                "chunk_numero": chunk_numero,
                "chunks_totales": sesion["chunks_recibidos"],
            }

        except Exception as e:
            return {"exito": False, "error": str(e)}

    async def finalizar_grabacion_video(
        self, sesion_id: str, encriptar: bool = True
    ) -> dict[str, Any]:
        """Finaliza una grabación de video y opcionalmente la encripta."""
        try:
            sesion = await self._obtener_sesion_grabacion(sesion_id)

            if not sesion:
                return {"error": "Sesión no encontrada"}

            sesion["estado"] = "finalizando"
            sesion["timestamp_fin"] = datetime.now(UTC).isoformat()

            # Actualizar sesión
            await self._actualizar_sesion_grabacion(sesion_id, sesion)

            # TODO: Opcionalmente, combinar chunks en un solo video
            # Esto se puede hacer de forma asíncrona en background

            return {
                "exito": True,
                "sesion_id": sesion_id,
                "estado": "finalizado",
                "chunks_totales": sesion["chunks_recibidos"],
                "ruta_video": sesion["ruta_base"],
                "timestamp_inicio": sesion["timestamp_inicio"],
                "timestamp_fin": sesion["timestamp_fin"],
            }

        except Exception as e:
            return {"exito": False, "error": str(e)}

    # ==========================================
    # GRABACIÓN DE AUDIO
    # ==========================================

    async def guardar_audio(
        self,
        intento_id: UUID,
        audio_data: bytes,
        formato: str = "webm",
        timestamp: datetime | None = None,
    ) -> dict[str, Any]:
        """Guarda un archivo de audio de la evaluación."""
        timestamp = timestamp or datetime.now(UTC)
        audio_id = hashlib.sha256(f"{intento_id}{timestamp}".encode()).hexdigest()[:16]

        ruta = f"evaluaciones/audio/{intento_id}/{audio_id}.{formato}"

        try:
            url = await self.storage.upload_file(
                file_content=audio_data, file_path=ruta, content_type=f"audio/{formato}"
            )

            return {
                "exito": True,
                "audio_id": audio_id,
                "ruta": ruta,
                "url": url,
                "timestamp": timestamp.isoformat(),
            }
        except Exception as e:
            return {"exito": False, "error": str(e)}

    # ==========================================
    # RECUPERACIÓN Y ELIMINACIÓN
    # ==========================================

    async def obtener_capturas_intento(
        self, intento_id: UUID, incluir_imagenes: bool = False
    ) -> list[dict[str, Any]]:
        """Obtiene todas las capturas de un intento."""
        metadata_list = await self._listar_metadata_capturas(intento_id)

        if incluir_imagenes:
            for metadata in metadata_list:
                if metadata.get("encriptada"):
                    # Desencriptar imagen
                    imagen_bytes = await self.storage.download_file(metadata["ruta"])
                    imagen_desencriptada = self.fernet.decrypt(imagen_bytes)
                    metadata["imagen_base64"] = base64.b64encode(
                        imagen_desencriptada
                    ).decode()
                else:
                    imagen_bytes = await self.storage.download_file(metadata["ruta"])
                    metadata["imagen_base64"] = base64.b64encode(imagen_bytes).decode()

        return metadata_list

    async def eliminar_grabaciones_antiguas(
        self, dias_retencion: int = 30
    ) -> dict[str, Any]:
        """Elimina grabaciones más antiguas que el período de retención."""
        fecha_limite = datetime.now(UTC) - timedelta(days=dias_retencion)

        # TODO: Implementar lógica de búsqueda y eliminación
        # Por ahora retorna info placeholder

        return {
            "exito": True,
            "fecha_limite": fecha_limite.isoformat(),
            "archivos_eliminados": 0,
            "espacio_liberado_mb": 0,
        }

    # ==========================================
    # UTILIDADES PRIVADAS
    # ==========================================

    def _get_or_create_encryption_key(self) -> bytes:
        """Obtiene o crea la clave de encriptación."""
        # En producción, esto debería estar en variables de entorno o secret manager
        key_str = getattr(settings, "MULTIMEDIA_ENCRYPTION_KEY", None)

        if key_str:
            return key_str.encode()
        # Generar nueva clave (solo para desarrollo)
        return Fernet.generate_key()

    async def _guardar_metadata_captura(
        self, intento_id: UUID, captura_id: str, metadata: dict[str, Any]
    ) -> None:
        """Guarda metadata de captura (en Redis o DB)."""
        # TODO: Implementar persistencia real

    async def _listar_metadata_capturas(self, intento_id: UUID) -> list[dict[str, Any]]:
        """Lista metadata de capturas de un intento."""
        # TODO: Implementar recuperación real
        return []

    async def _guardar_sesion_grabacion(
        self, sesion_id: str, sesion_info: dict[str, Any]
    ) -> None:
        """Guarda info de sesión de grabación."""
        # TODO: Implementar en Redis

    async def _obtener_sesion_grabacion(self, sesion_id: str) -> dict[str, Any] | None:
        """Obtiene info de sesión de grabación."""
        # TODO: Implementar desde Redis
        return None

    async def _actualizar_sesion_grabacion(
        self, sesion_id: str, sesion_info: dict[str, Any]
    ) -> None:
        """Actualiza info de sesión de grabación."""
        # TODO: Implementar en Redis


# Singleton
grabacion_multimedia_service = GrabacionMultimediaService()
