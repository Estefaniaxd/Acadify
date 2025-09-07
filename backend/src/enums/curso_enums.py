import enum


class ModalidadCurso(str, enum.Enum):
    anual = "anual"
    semestral = "semestral"
    trimestral = "trimestral"
    cuatrimestral = "cuatrimestral"
    bimestral = "bimestral"
    mensual = "mensual"
    modular = "modular"
    flexible = "flexible"
    otro = "otro"
