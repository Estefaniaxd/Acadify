from .auth.user_crud import UserCRUD
from .auth.oauth_crud import OAuthCRUD

# Imports de CRUD - Modulo de assessment
from src.crud.assessment.escala_calificacion import escala_calificacion
from src.crud.assessment.valor_calificacion import valor_calificacion


# Imports de CRUD - Modulo de classes

from src.crud.classes.asistencia import CRUDAsistencia
from src.crud.classes.clase import CRUDClase
from src.crud.classes.entregar_tarea import CRUDEntregarTarea
from src.crud.classes.tarea import CRUDTarea

# Imports de CRUD - Modulo de comunication

from src.crud.communication.chat_bot import CRUDChatBot
from src.crud.communication.chat_grupo import CRUDChatGrupo
from src.crud.communication.faqbot import CRUDFAQBot
from src.crud.communication.mensaje_bot import CRUDMensajeBot
from src.crud.communication.mensaje import CRUDMensaje

# Instancias - Modulo de assessment
escala_calificacion = escala_calificacion
valor_calificacion = valor_calificacion


# Instancias - Modulo de classes

asistencia = CRUDAsistencia()
clase = CRUDClase()
entregar_tarea = CRUDEntregarTarea()
tarea = CRUDTarea()

# Instancias- Modulos de Communication

chatbot = CRUDChatBot()
chat_grupo = CRUDChatGrupo()
faq_bot = CRUDFAQBot()
mensaje_bot = CRUDMensajeBot()
mensaje = CRUDMensaje()


from .academic.crud_institucion import institucion_crud
from .academic.crud_programa import programa_crud
from .academic.crud_curso import curso_crud
from .academic.crud_curso_docente import curso_docente_crud
from .academic.crud_estudiante_grupo import estudiante_curso_crud
from .academic.crud_estudiante_grupo import estudiante_grupo_crud
from .academic.crud_grupo import grupo_crud
from .academic.crud_grupo_curso import grupo_curso_crud
from .academic.crud_material_educativo import material_educativo_crud
from .academic.crud_material_clase import material_clase_crud
from .academic.crud_material_curso import material_curso_crud
