"""Validador profesional de archivos para entregas de tareas.

Módulo que implementa validación completa y segura de archivos subidos,
siguiendo SOLID principles y buenas prácticas de seguridad.

Author: Acadify Team
Version: 1.0.0
"""

import os
import logging
import mimetypes
from typing import Optional, Set, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TipoExtensionPermitida(str, Enum):
    """Extensiones permitidas para entregas."""
    # Documentos
    PDF = ".pdf"
    DOCX = ".docx"
    DOC = ".doc"
    TXT = ".txt"
    
    # Hojas de cálculo
    XLSX = ".xlsx"
    XLS = ".xls"
    CSV = ".csv"
    
    # Presentaciones
    PPTX = ".pptx"
    PPT = ".ppt"
    
    # Imágenes
    PNG = ".png"
    JPG = ".jpg"
    JPEG = ".jpeg"
    GIF = ".gif"
    WEBP = ".webp"
    
    # Código
    PY = ".py"
    JS = ".js"
    HTML = ".html"
    CSS = ".css"
    JSON = ".json"
    XML = ".xml"
    SQL = ".sql"
    
    # Comprimidos
    ZIP = ".zip"
    RAR = ".rar"
    

class EstadoValidacion(str, Enum):
    """Estados posibles de validación."""
    VALIDO = "valido"
    EXTENSION_NO_PERMITIDA = "extension_no_permitida"
    MIME_TYPE_NO_COINCIDE = "mime_type_no_coincide"
    TAMAÑO_EXCEDIDO = "tamaño_excedido"
    ARCHIVO_VACIO = "archivo_vacio"
    PATH_TRAVERSAL_DETECTADO = "path_traversal_detectado"
    ERROR_LECTURA = "error_lectura"


@dataclass
class MetadatosArchivo:
    """Metadatos de un archivo validado."""
    nombre_original: str
    nombre_seguro: str
    extension: str
    mime_type: str
    tamaño_bytes: int
    fecha_subida: str
    validez: EstadoValidacion
    detalles_error: Optional[str] = None


@dataclass
class ConfiguracionValidacion:
    """Configuración de restricciones de archivos."""
    extensiones_permitidas: Set[str]
    tamaño_maximo_mb: int
    tamaño_maximo_bytes: int = None
    
    def __post_init__(self):
        """Calcula tamaño máximo en bytes."""
        if self.tamaño_maximo_bytes is None:
            self.tamaño_maximo_bytes = self.tamaño_maximo_mb * 1024 * 1024


class ValidadorArchivos:
    """Validador profesional y seguro de archivos.
    
    Implementa principios SOLID:
    - Single Responsibility: Solo valida archivos
    - Open/Closed: Fácil de extender sin modificar
    - Liskov Substitution: Cumple interfaz consistente
    - Interface Segregation: Métodos específicos
    - Dependency Inversion: Usa configuración, no hardcoding
    
    Características:
    - Sanitización de nombres (prevención de path traversal)
    - Validación de extensión (whitelist)
    - Validación de MIME type
    - Validación de tamaño
    - Generación de nombres seguros (UUID)
    """
    
    # MIME types válidos (whitelist)
    MIME_TYPES_VALIDOS: Dict[str, str] = {
        # Documentos
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/msword": ".doc",
        "text/plain": ".txt",
        
        # Hojas de cálculo
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/vnd.ms-excel": ".xls",
        "text/csv": ".csv",
        
        # Presentaciones
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
        "application/vnd.ms-powerpoint": ".ppt",
        
        # Imágenes
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/gif": ".gif",
        "image/webp": ".webp",
        
        # Código
        "text/x-python": ".py",
        "application/x-python": ".py",
        "text/javascript": ".js",
        "application/javascript": ".js",
        "text/html": ".html",
        "text/css": ".css",
        "application/json": ".json",
        "application/xml": ".xml",
        "text/xml": ".xml",
        "application/sql": ".sql",
        "text/x-sql": ".sql",
        
        # Comprimidos
        "application/zip": ".zip",
        "application/x-zip-compressed": ".zip",
        "application/x-rar-compressed": ".rar",
    }
    
    # Configuración por defecto
    EXTENSIONES_PERMITIDAS_DEFAULT = {
        ext.value for ext in TipoExtensionPermitida
    }
    
    TAMAÑO_MAXIMO_MB_DEFAULT = 50  # 50MB por defecto
    
    def __init__(
        self,
        extensiones_permitidas: Optional[Set[str]] = None,
        tamaño_maximo_mb: int = TAMAÑO_MAXIMO_MB_DEFAULT
    ):
        """Inicializa validador con configuración.
        
        Args:
            extensiones_permitidas: Set de extensiones válidas (ej: {'.pdf', '.docx'})
            tamaño_maximo_mb: Tamaño máximo en MB
        """
        self.config = ConfiguracionValidacion(
            extensiones_permitidas=extensiones_permitidas or self.EXTENSIONES_PERMITIDAS_DEFAULT,
            tamaño_maximo_mb=tamaño_maximo_mb
        )
    
    def sanitizar_nombre(self, nombre: str) -> str:
        """Sanitiza nombre de archivo eliminando paths peligrosos.
        
        Previene ataques de path traversal:
        - "../../../etc/passwd"
        - "..\\..\\windows\\system32"
        - "/etc/shadow"
        
        Args:
            nombre: Nombre original del archivo
            
        Returns:
            Nombre sanitizado (solo basename)
        """
        # Obtener solo el nombre del archivo (no el path)
        nombre_limpio = os.path.basename(nombre)
        
        # Eliminar caracteres peligrosos
        caracteres_peligrosos = ['/', '\\', '\x00', '\n', '\r', '\t']
        for char in caracteres_peligrosos:
            nombre_limpio = nombre_limpio.replace(char, '_')
        
        # Limitar longitud
        nombre_limpio = nombre_limpio[:255]
        
        logger.debug(f"Nombre sanitizado: '{nombre}' → '{nombre_limpio}'")
        return nombre_limpio
    
    def generar_nombre_seguro(
        self,
        nombre_original: str,
        usar_uuid: bool = True
    ) -> tuple[str, str]:
        """Genera nombre seguro para archivo (con o sin UUID).
        
        Args:
            nombre_original: Nombre original del archivo
            usar_uuid: Si True, prepend UUID para evitar colisiones
            
        Returns:
            Tupla (nombre_seguro, extension)
        """
        import uuid
        from datetime import datetime
        
        # Sanitizar nombre
        nombre_limpio = self.sanitizar_nombre(nombre_original)
        
        # Obtener extensión
        _, extension = os.path.splitext(nombre_limpio)
        extension = extension.lower()
        
        if usar_uuid:
            # Formato: {uuid}_{timestamp}_{nombre_original_limpio}
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            nombre_sin_ext = os.path.splitext(nombre_limpio)[0][:50]  # Max 50 chars
            nombre_seguro = f"{uuid.uuid4().hex[:8]}_{timestamp}_{nombre_sin_ext}{extension}"
        else:
            # Solo sanitizar
            nombre_seguro = nombre_limpio
        
        logger.debug(f"Nombre seguro generado: '{nombre_seguro}'")
        return nombre_seguro, extension
    
    def validar_extension(self, nombre: str) -> tuple[bool, str]:
        """Valida que extensión está en whitelist.
        
        Args:
            nombre: Nombre del archivo
            
        Returns:
            Tupla (es_válida, extensión)
        """
        _, extension = os.path.splitext(nombre)
        extension = extension.lower()
        
        # Extensión vacía
        if not extension:
            logger.warning(f"Archivo sin extensión: {nombre}")
            return False, ""
        
        # Verificar extensión
        es_valida = extension in self.config.extensiones_permitidas
        
        if not es_valida:
            logger.warning(
                f"Extensión no permitida: {extension}. "
                f"Permitidas: {self.config.extensiones_permitidas}"
            )
        
        return es_valida, extension
    
    def validar_mime_type(
        self,
        nombre: str,
        mime_type: str
    ) -> tuple[bool, str]:
        """Valida MIME type contra extensión.
        
        Args:
            nombre: Nombre del archivo
            mime_type: MIME type reportado
            
        Returns:
            Tupla (es_válido, mensaje)
        """
        _, extension = os.path.splitext(nombre)
        extension = extension.lower()
        
        # Verificar MIME type en whitelist
        if mime_type not in self.MIME_TYPES_VALIDOS:
            logger.warning(f"MIME type no permitido: {mime_type}")
            return False, f"MIME type no soportado: {mime_type}"
        
        # Verificar que el MIME type coincida con la extensión
        extension_esperada = self.MIME_TYPES_VALIDOS[mime_type]
        if extension != extension_esperada:
            logger.warning(
                f"MIME type no coincide con extensión. "
                f"Extensión: {extension}, "
                f"esperada para MIME {mime_type}: {extension_esperada}"
            )
            # Nota: Es solo una advertencia, permitimos proceder
            # (algunos MIME types pueden tener múltiples extensiones)
        
        return True, ""
    
    def validar_tamaño(self, tamaño_bytes: int) -> tuple[bool, str]:
        """Valida tamaño del archivo.
        
        Args:
            tamaño_bytes: Tamaño en bytes
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        if tamaño_bytes == 0:
            return False, "El archivo está vacío"
        
        if tamaño_bytes > self.config.tamaño_maximo_bytes:
            tamaño_mb = tamaño_bytes / (1024 * 1024)
            return (
                False,
                f"Archivo demasiado grande: {tamaño_mb:.2f}MB. "
                f"Máximo: {self.config.tamaño_maximo_mb}MB"
            )
        
        return True, ""
    
    def validar(
        self,
        nombre: str,
        contenido: bytes,
        mime_type: str
    ) -> MetadatosArchivo:
        """Validación COMPLETA de archivo.
        
        Implementa todas las validaciones en orden:
        1. Path traversal
        2. Extensión
        3. MIME type
        4. Tamaño
        
        Args:
            nombre: Nombre original
            contenido: Contenido binario
            mime_type: MIME type
            
        Returns:
            MetadatosArchivo con resultado de validación
        """
        from datetime import datetime
        
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # 1. Detectar path traversal
            nombre_sanitizado = self.sanitizar_nombre(nombre)
            if nombre_sanitizado != os.path.basename(nombre):
                # Hubo path traversal, pero ya fue sanitizado
                pass  # Continuar con validación
            
            # 2. Validar extensión
            es_ext_valida, extension = self.validar_extension(nombre_sanitizado)
            if not es_ext_valida:
                return MetadatosArchivo(
                    nombre_original=nombre,
                    nombre_seguro="",
                    extension="",
                    mime_type=mime_type,
                    tamaño_bytes=len(contenido),
                    fecha_subida=timestamp,
                    validez=EstadoValidacion.EXTENSION_NO_PERMITIDA,
                    detalles_error=f"Extensión '{extension}' no permitida"
                )
            
            # 3. Validar MIME type
            es_mime_valido, error_mime = self.validar_mime_type(
                nombre_sanitizado,
                mime_type
            )
            if not es_mime_valido:
                return MetadatosArchivo(
                    nombre_original=nombre,
                    nombre_seguro="",
                    extension=extension,
                    mime_type=mime_type,
                    tamaño_bytes=len(contenido),
                    fecha_subida=timestamp,
                    validez=EstadoValidacion.MIME_TYPE_NO_COINCIDE,
                    detalles_error=error_mime
                )
            
            # 4. Validar tamaño
            es_tamaño_valido, error_tamaño = self.validar_tamaño(len(contenido))
            if not es_tamaño_valido:
                return MetadatosArchivo(
                    nombre_original=nombre,
                    nombre_seguro="",
                    extension=extension,
                    mime_type=mime_type,
                    tamaño_bytes=len(contenido),
                    fecha_subida=timestamp,
                    validez=EstadoValidacion.TAMAÑO_EXCEDIDO,
                    detalles_error=error_tamaño
                )
            
            # ✅ VALIDACIÓN EXITOSA
            nombre_seguro, _ = self.generar_nombre_seguro(nombre_sanitizado)
            
            return MetadatosArchivo(
                nombre_original=nombre,
                nombre_seguro=nombre_seguro,
                extension=extension,
                mime_type=mime_type,
                tamaño_bytes=len(contenido),
                fecha_subida=timestamp,
                validez=EstadoValidacion.VALIDO,
                detalles_error=None
            )
        
        except Exception as e:
            logger.error(f"Error durante validación de archivo: {e}", exc_info=True)
            return MetadatosArchivo(
                nombre_original=nombre,
                nombre_seguro="",
                extension="",
                mime_type=mime_type,
                tamaño_bytes=len(contenido),
                fecha_subida=timestamp,
                validez=EstadoValidacion.ERROR_LECTURA,
                detalles_error=str(e)
            )
    
    def crear_ruta_almacenamiento(
        self,
        base_dir: str,
        entrega_id: str,
        nombre_seguro: str
    ) -> str:
        """Crea ruta segura para almacenar archivo.
        
        Estructura: {base_dir}/entregas/{entrega_id}/{nombre_seguro}
        
        Args:
            base_dir: Directorio base
            entrega_id: ID de la entrega
            nombre_seguro: Nombre seguro del archivo
            
        Returns:
            Ruta completa segura
        """
        # Construir path de forma segura (evitar path traversal)
        ruta_relativa = Path("entregas") / entrega_id / nombre_seguro
        ruta_segura = Path(base_dir) / ruta_relativa
        
        # Validar que no escapa del base_dir
        try:
            ruta_segura.resolve().relative_to(Path(base_dir).resolve())
        except ValueError:
            logger.error(f"Intento de escape detectado: {ruta_segura}")
            raise ValueError(f"Ruta no segura: {ruta_segura}")
        
        return str(ruta_segura)
