import enum


class TipoDocumentoUsuario(str, enum.Enum):
    cc = "cc"
    ti = "ti"
    ce = "ce"


class RolUsuario(str, enum.Enum):
    administrador = "administrador"
    coordinador = "coordinador"
    docente = "docente"
    estudiante = "estudiante"


class EstadoCuentaUsuario(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"
    suspendido = "suspendido"
    eliminado = "eliminado"
