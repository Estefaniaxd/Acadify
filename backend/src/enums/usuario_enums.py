import enum

class TipoDocumentoUsuario(enum.Enum):
    cc = "cc"
    ti = "ti"
    ce = "ce"

class RolUsuario(enum.Enum):
    administrador = "administrador"
    coordinador = "coordinador"
    docente = "docente"
    estudiante = "estudiante"

class EstadoCuentaUsuario(enum.Enum):
    activo = "activo"
    inactivo = "inactivo"
    suspendido = "suspendido"
    eliminado = "eliminado"