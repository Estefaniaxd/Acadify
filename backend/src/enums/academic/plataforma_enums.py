import enum


class TipoIntegracionPlataforma(str, enum.Enum):
    api = "api"
    manual = "manual"
    embebido = "embebido"
    otro = "otro"
