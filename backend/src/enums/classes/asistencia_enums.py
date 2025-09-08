import enum

class EstadoAsistencia(str, enum.Enum):
    presente = "presente"
    ausente = "ausente"
    justificado = "justificado"
    
