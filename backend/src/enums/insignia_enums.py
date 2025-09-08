import enum


class TipoInsignia(str, enum.Enum):
    objetivo = "objetivo"
    calificacion = "calificacion"
    racha = "racha"
    manual = "manual"
