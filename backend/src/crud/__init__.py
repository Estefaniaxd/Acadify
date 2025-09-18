from .auth.user_crud import UserCRUD
from .auth.oauth_crud import OAuthCRUD

# Imports de CRUD - Modulo de academic

from src.crud.academic.crud_curso_docente import curso_docente
from src.crud.academic.crud_curso import curso
from src.crud.academic.crud_estudiante_grupo import estudiante_grupo
from src.crud.academic.crud_grupo_curso import grupo_curso
from src.crud.academic.crud_grupo import grupo
from src.crud.academic.crud_institucion import institucion
from src.crud.academic.crud_material_clase import material_clase
from src.crud.academic.crud_material_curso import material_curso
from src.crud.academic.crud_material_educativo import material_educativo
from src.crud.academic.crud_programa import programa

# Imports de CRUD - Modulo de assessment

from src.crud.assessment.escala_calificacion import escala_calificacion
from src.crud.assessment.valor_calificacion import valor_calificacion

# Imports de CRUD - Modulo de classes

from src.crud.classes import asistencia
from src.crud.classes.clase import clase
from src.crud.classes.entregar_tarea import entregar_tarea
from src.crud.classes.plataforma import plataforma
from src.crud.classes.tarea import tarea

# Imports de CRUD - Modulo de comunication

from src.crud.communication import archivo_chat
from src.crud.communication.chat_bot import chat_bot
from src.crud.communication.chat_grupo import chat_grupo
from src.crud.communication.faq_bot import faq_bot
from src.crud.communication.mensaje_bot import mensaje_bot
from src.crud.communication.mensaje import mensaje

__all__ = [
    "curso_docente",
    "curso",
    "estudiante_grupo",
    "grupo_curso",
    "grupo",
    "institucion",
    "material_clase",
    "material_curso",
    "material_educativo",
    "programa",
    "escala_calificacion",
    "valor_calificacion",
    "asistencia",
    "clase",
    "entregar_tarea",
    "plataforma",
    "tarea",
    "archivo_chat",
    "chat_bot",
    "chat_grupo",
    "faq_bot",
    "mensaje_bot",
    "mensaje",
]
