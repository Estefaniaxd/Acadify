import enum


class TipoInstitucion(str, enum.Enum):
    """Tipos de instituciones educativas - Ampliado para mayor cobertura."""

    escuela = "escuela"
    colegio = "colegio"
    instituto = "instituto"
    universidad = "universidad"
    politecnico = "politecnico"
    centro_de_formacion = "centro_de_formacion"
    corporacion = "corporacion"
    fundacion = "fundacion"
    academia = "academia"
    # Nuevos tipos para mayor granularidad
    centro_idiomas = "centro_idiomas"
    centro_deportivo = "centro_deportivo"
    seminario = "seminario"
    conservatorio = "conservatorio"  # Música, artes
    escuela_militar = "escuela_militar"
    otro = "otro"  # Catch-all para casos especiales


class NivelEducativoInstitucion(str, enum.Enum):
    """Niveles educativos que ofrece la institución."""

    basica = "basica"
    media = "media"
    tecnica = "tecnica"
    tecnologica = "tecnologica"
    superior = "superior"


class SectorInstitucion(str, enum.Enum):
    """Sector al que pertenece la institución."""

    publico = "publico"
    privado = "privado"


class EstadoInstitucion(str, enum.Enum):
    """Estados del ciclo de vida de una institución."""

    pendiente = "pendiente"  # Recién creada, esperando aceptación de coordinador
    activa = "activa"  # Operando normalmente
    suspendida = "suspendida"  # Temporalmente inactiva
    inactiva = "inactiva"  # Permanentemente cerrada


class ModalidadEnsenanza(str, enum.Enum):
    """Modalidad de enseñanza ofrecida por la institución."""

    presencial = "presencial"  # 100% presencial
    virtual = "virtual"  # 100% online
    hibrida = "hibrida"  # Combinación de presencial y virtual
    dual = "dual"  # Teoría-práctica alternada


class TipoCalendario(str, enum.Enum):
    """Tipo de calendario académico que maneja la institución."""

    semestral = "semestral"  # 2 períodos por año
    trimestral = "trimestral"  # 3 períodos por año
    bimestral = "bimestral"  # 6 períodos por año
    cuatrimestral = "cuatrimestral"  # 3 períodos de 4 meses
    anual = "anual"  # 1 período continuo
    modular = "modular"  # Por módulos independientes (ej: SENA)
