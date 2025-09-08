import enum


class EstadoCoordinador(str, enum.Enum):
    activo = "activo"
    invitado = "invitado"
    expirado = "expirado"
    retirado = "retirado"
