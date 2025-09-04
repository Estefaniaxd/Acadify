import enum

class TipoInstitucion(enum.Enum):
    escuela = "escuela"
    colegio = "colegio"
    instituto = "instituto"
    universidad = "universidad"
    politecnico = "politecnico"
    centro_de_formacion = "centro_de_formacion"
    corporacion = "corporacion"
    fundacion = "fundacion"
    academia = "academia"

class NivelEducativoInstitucion(enum.Enum):
    basica = "basica"
    media = "media"
    tecnica = "tecnica"
    tecnologica = "tecnologica"
    superior = "superior"

class SectorInstitucion(enum.Enum):
    publico = "publico"
    privado = "privado"
