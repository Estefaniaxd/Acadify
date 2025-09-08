import enum


class TipoVinculacionDocente(str, enum.Enum):
    planta = "planta"
    catedra = "catedra"
    ocasional = "ocasional"
    visitante = "visitante"
    honorario = "honorario"
