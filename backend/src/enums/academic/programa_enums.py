import enum


class NivelPrograma(str, enum.Enum):
    """Nivel académico del programa - Compatible con sistemas educativos internacionales."""

    # Educación Básica y Media
    preescolar = "preescolar"
    primaria = "primaria"
    secundaria = "secundaria"
    media = "media"
    bachillerato = "bachillerato"

    # Formación Técnica y Tecnológica
    tecnico_laboral = "tecnico_laboral"
    tecnico_profesional = "tecnico_profesional"
    tecnologico = "tecnologico"

    # Educación Superior
    pregrado = "pregrado"
    profesional = "profesional"
    licenciatura = "licenciatura"  # Para países latinoamericanos

    # Posgrados
    especializacion = "especializacion"
    maestria = "maestria"
    doctorado = "doctorado"
    postdoctorado = "postdoctorado"

    # Formación Complementaria
    diplomado = "diplomado"
    certificacion = "certificacion"
    curso_corto = "curso_corto"
    bootcamp = "bootcamp"
    taller = "taller"
    seminario = "seminario"

    # Otros
    educacion_continua = "educacion_continua"
    formacion_empresarial = "formacion_empresarial"
    otro = "otro"


class TipoPrograma(str, enum.Enum):
    """Modalidad de enseñanza del programa."""

    presencial = "presencial"
    virtual = "virtual"
    hibrido = "hibrido"
    mixto = "mixto"
    a_distancia = "a_distancia"
    dual = "dual"
    por_ciclos = "por_ciclos"
    continuo = "continuo"
    semipresencial = "semipresencial"
    otro = "otro"


class EstadoPrograma(str, enum.Enum):
    """Estado actual del programa académico."""

    activo = "activo"
    inactivo = "inactivo"
    en_proceso_apertura = "en_proceso_apertura"
    suspendido_temporalmente = "suspendido_temporalmente"
    en_liquidacion = "en_liquidacion"
    cerrado = "cerrado"


class DuracionPrograma(str, enum.Enum):
    """Tipo de duración del programa."""

    semestral = "semestral"
    trimestral = "trimestral"
    cuatrimestral = "cuatrimestral"
    anual = "anual"
    bianual = "bianual"
    modular = "modular"
    flexible = "flexible"
    continuo = "continuo"
