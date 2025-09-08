import enum


class TipoMensaje(enum.Enum):
    texto = "texto"
    archivo = "archivo"
    imagen = "imagen"
    audio = "audio"
