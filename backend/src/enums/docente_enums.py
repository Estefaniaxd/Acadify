import enum

class TipoVinculacionDocente(enum.Enum):
    planta = "planta"
    catedra = "catedra"
    ocasional = "ocasional"
    visitante = "visitante"
    honorario = "honorario"