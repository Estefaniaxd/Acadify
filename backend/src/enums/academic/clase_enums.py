import enum


class EstadoClase(str, enum.Enum):
    programada = "programada"
    en_progreso = "en_progreso"
    finalizada = "finalizada"
    cancelada = "cancelada"


class TipoClase(str, enum.Enum):
    teorica = "teorica"
    practica = "practica"
    laboratorio = "laboratorio"
    taller = "taller"
    seminario = "seminario"
    conferencia = "conferencia"
    examen = "examen"
    otro = "otro"


class EstadoCodigoAcceso(str, enum.Enum):
    activo = "activo"
    vencido = "vencido"
    deshabilitado = "deshabilitado"
