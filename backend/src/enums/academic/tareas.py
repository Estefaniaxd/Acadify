from enum import Enum


class EstadoTarea(str, Enum):
    ASIGNADA = "asignada"
    EN_PROGRESO = "en_progreso"
    ENTREGADA = "entregada"
    CALIFICADA = "calificada"
    VENCIDA = "vencida"
    CANCELADA = "cancelada"


class TipoTarea(str, Enum):
    ENSAYO = "ensayo"
    PROYECTO = "proyecto"
    EJERCICIOS = "ejercicios"
    INVESTIGACION = "investigacion"
    PRESENTACION = "presentacion"
    LABORATORIO = "laboratorio"
    LECTURA = "lectura"
    EXAMEN = "examen"
    OTRO = "otro"


class PrioridadTarea(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class EstadoEntrega(str, Enum):
    BORRADOR = "borrador"
    ENTREGADA = "entregada"
    CALIFICADA = "calificada"
    DEVUELTA = "devuelta"
    REENTREGADA = "reentregada"
    CANCELADA = "cancelada"
