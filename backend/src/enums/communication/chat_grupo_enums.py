import enum


class EstadoChatGrupo(str, enum.Enum):
    activo = "activo"
    archivado = "archivado"
    eliminado = "eliminado"
