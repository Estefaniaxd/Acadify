import enum


class TipoRecompensa(str, enum.Enum):
    foto_perfil = "foto_perfil"
    foto_portada = "foto_portada"
    estilo_chat = "estilo_chat"
    sticker = "sticker"
    otro = "otro"
