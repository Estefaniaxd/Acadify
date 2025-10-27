import enum


class ContextoMensaje(str, enum.Enum):
    general = "general"
    academico = "academico"
    tarea = "tarea"
    material = "material"
    faq = "faq"
