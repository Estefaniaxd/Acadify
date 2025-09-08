import enum


class TipoMensaje(str, enum.Enum):
    texto = "texto"
    archivo = "archivo"
    imagen = "imagen"
    audio = "audio"
