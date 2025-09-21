import enum


class TipoInstitucion(str, enum.Enum):
    escuela = "escuela"
    colegio = "colegio"
    instituto = "instituto"
    universidad = "universidad"
    politecnico = "politecnico"
    centro_de_formacion = "centro_de_formacion"
    corporacion = "corporacion"
    fundacion = "fundacion"
    academia = "academia"


class NivelEducativoInstitucion(str, enum.Enum):
    basica = "basica"
    media = "media"
    tecnica = "tecnica"
    tecnologica = "tecnologica"
    superior = "superior"


class SectorInstitucion(str, enum.Enum):
    publico = "publico"
    privado = "privado"


class EstadoInstitucion(str, enum.Enum):
    pendiente = "pendiente"
    activa = "activa"
    suspendida = "suspendida"
    inactiva = "inactiva"
