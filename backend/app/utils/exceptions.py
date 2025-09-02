# backend/app/utils/exceptions.py
from fastapi import HTTPException, status
from typing import Any, Dict, List, Optional


# -------------------------------
# Excepciones personalizadas para usuarios
# -------------------------------

class UserNotFoundException(HTTPException):
    """Excepción lanzada cuando un usuario no existe en la base de datos."""
    def __init__(self, user_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID '{user_id}' no encontrado."
        )


class DuplicateEmailException(HTTPException):
    """Excepción lanzada cuando un email ya está registrado."""
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email '{email}' ya está registrado en el sistema."
        )


class InsufficientPermissionsException(HTTPException):
    """Excepción lanzada cuando un usuario no tiene permisos suficientes."""
    def __init__(self, role_required: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permisos insuficientes. Se requiere: {role_required}."
        )


class ValidationException(HTTPException):
    """Excepción lanzada cuando hay un error de validación en los datos."""
    def __init__(self, field: str, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={field: message}
        )


# -------------------------------
# Excepciones generales
# -------------------------------

class ResourceNotFoundException(HTTPException):
    """Recurso no encontrado genérico."""
    def __init__(self, resource_name: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name} con identificador '{identifier}' no encontrado."
        )


class UnauthorizedException(HTTPException):
    """Excepción para acceso no autorizado."""
    def __init__(self, message: str = "No autorizado"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )


class ConflictException(HTTPException):
    """Excepción para conflictos, por ejemplo, datos duplicados."""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )


# -------------------------------
# Manejo de errores de subida de archivos
# -------------------------------

class FileTooLargeException(HTTPException):
    """Excepción lanzada cuando un archivo supera el tamaño permitido."""
    def __init__(self, max_size: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Archivo demasiado grande. Tamaño máximo permitido: {max_size} bytes."
        )


class FileTypeNotAllowedException(HTTPException):
    """Excepción lanzada cuando un archivo no tiene un tipo permitido."""
    def __init__(self, allowed_types: List[str]):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(allowed_types)}."
        )


# -------------------------------
# Utilidad para errores dinámicos
# -------------------------------

def raise_custom_error(
    status_code: int,
    message: str,
    extra: Optional[Dict[str, Any]] = None
):
    """
    Permite lanzar un HTTPException con información extra opcional.

    Args:
        status_code: Código HTTP
        message: Mensaje principal del error
        extra: Diccionario con información adicional (opcional)
    """
    detail: Dict[str, Any] = {"message": message}
    if extra:
        detail.update(extra)
    raise HTTPException(status_code=status_code, detail=detail)


# -------------------------------
# Excepción personalizada genérica para toda la app
# -------------------------------

class AcadifyException(HTTPException):
    """
    Excepción genérica para manejar errores de la aplicación con códigos personalizados.

    Args:
        message: Mensaje de error
        status_code: Código HTTP
        error_code: Código interno del error (string)
        extra: Información adicional opcional
    """
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "ERROR",
        extra: Optional[Dict[str, Any]] = None
    ):
        detail: Dict[str, Any] = {"message": message, "error_code": error_code}
        if extra:
            detail.update(extra)
        super().__init__(status_code=status_code, detail=detail)
