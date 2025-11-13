"""ENUMs del módulo académico.

Exporta todos los enums relacionados con el sistema académico.
"""

from enum import Enum


# Integración de plataformas
class TipoIntegracionPlataforma(Enum):
    MOODLE = "moodle"
    GOOGLE_CLASSROOM = "google_classroom"
    CANVAS = "canvas"
    OTRO = "otro"


# Programas
# Cursos
from .curso_enums import (
    CategoriaCurso,
    EstadoCurso,
    IdiomaCurso,
    ModalidadCurso,
    NivelDificultad,
    TipoCurso,
)

# Grupos/Secciones
from .grupo_enums import (
    EstadoGrupo,
    FormatoEvaluacion,
    JornadaGrupo,
    ModalidadAsistencia,
    TipoGrupo,
)

# Horarios
from .horario_enums import (
    DiaSemana,
    EstadoSesion,
    ModalidadSesion,
    TipoAula,
    TipoRecurrencia,
    TipoSesion,
)

# Inscripciones
from .inscripcion_enums import (
    EstadoInscripcion,
    FormaPago,
    MotivoRechazo,
    MotivoRetiro,
    TipoInscripcion,
)

# Períodos Académicos
from .periodo_enums import EstadoPeriodo, TipoPeriodo
from .programa_enums import (
    DuracionPrograma,
    EstadoPrograma,
    NivelPrograma,
    TipoPrograma,
)


__all__ = [
    "CategoriaCurso",
    # Horarios
    "DiaSemana",
    "DuracionPrograma",
    "EstadoCurso",
    "EstadoGrupo",
    # Inscripciones
    "EstadoInscripcion",
    "EstadoPeriodo",
    "EstadoPrograma",
    "EstadoSesion",
    "FormaPago",
    "FormatoEvaluacion",
    "IdiomaCurso",
    # Grupos
    "JornadaGrupo",
    "ModalidadAsistencia",
    # Cursos
    "ModalidadCurso",
    "ModalidadSesion",
    "MotivoRechazo",
    "MotivoRetiro",
    "NivelDificultad",
    # Programas
    "NivelPrograma",
    "TipoAula",
    "TipoCurso",
    "TipoGrupo",
    "TipoInscripcion",
    # Integración
    "TipoIntegracionPlataforma",
    # Períodos
    "TipoPeriodo",
    "TipoPrograma",
    "TipoRecurrencia",
    "TipoSesion",
]
