from .auth.user_crud import UserCRUD
from .auth.oauth_crud import OAuthCRUD

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