"""Enumeraciones para el sistema de Chat de Grupo.

Define los estados posibles para los chats de grupo.
"""

import enum


class EstadoChatGrupo(str, enum.Enum):
    """Estados posibles para un chat de grupo.

    Attributes:
        activo: El chat está activo y operativo
        archivado: El chat ha sido archivado (no se puede usar pero se conserva)
    """

    activo = "activo"
    archivado = "archivado"

    def __str__(self) -> str:
        return self.value
