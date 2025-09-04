import enum

class NivelPrograma(enum.Enum):
    basico = "basico"
    media = "media"
    tecnico = "tecnico"
    tecnologico = "tecnologico"
    profesional = "profesional"
    especializacion = "especializacion"
    maestria = "maestria"
    doctorado = "doctorado"
    otro = "otro"

class TipoPrograma(enum.Enum):
    presencial = "presencial"
    virtual = "virtual"
    mixto = "mixto"
    a_distancia = "a_distancia"
    dual = "dual"
    por_ciclos = "por_ciclos"
    continuo = "continuo"
    otro = "otro"
