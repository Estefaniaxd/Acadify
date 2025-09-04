import enum

class EstadoCoordinador(enum.Enum):
    activo = "activo"
    invitado = "invitado"
    expirado = "expirado"
    retirado = "retirado"
