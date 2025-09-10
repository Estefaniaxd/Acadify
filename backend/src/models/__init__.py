from src.models.users.usuario import Usuario
from src.models.users.administrador_sistema import AdministradorSistema
from src.models.users.coordinador import Coordinador
from src.models.users.docente import Docente
from src.models.users.estudiante import Estudiante
from src.models.users.institucion_coordinador import InstitucionCoordinador
from src.models.users.oauth_provider import OAuthProvider

from src.models.academic.curso import Curso
from src.models.academic.curso_docente import CursoDocente
from src.models.academic.estudiante_grupo import EstudianteGrupo
from src.models.academic.grupo import Grupo
from src.models.academic.grupo_curso import GrupoCurso
from src.models.academic.institucion import Institucion
from src.models.academic.material_clase import MaterialClase
from src.models.academic.material_curso import MaterialCurso
from src.models.academic.material_educativo import MaterialEducativo
from src.models.academic.programa import Programa

from src.models.communication.archivo_chat import ArchivoChat
from src.models.communication.chat_bot import ChatBot
from src.models.communication.chat_grupo import ChatGrupo
from src.models.communication.faqbot_id import FAQBot
from src.models.communication.mensaje import Mensaje

from src.models.gamification.historial_puntos import HistorialPuntos
from src.models.gamification.insignia import Insignia
from src.models.gamification.recompensa import Recompensa
from src.models.gamification.tema import Tema
from src.models.gamification.tema_personalizado import TemaPersonalizado
from src.models.gamification.tema_predefinido import TemaPredefinido
from src.models.gamification.usuario_insignia import UsuarioInsignia
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.models.gamification.usuario_recompensa import UsuarioRecompensa

from src.models.assessment.escala_calificacion import EscalaCalificacion
from src.models.assessment.valor_calificacion import ValorCalificacion

from src.models.classes.asistencia import Asistencia
from src.models.classes.clase import Clase
from src.models.classes.entregar_tarea import EntregarTarea
from src.models.classes.tarea import Tarea

from src.models.plataforma import Plataforma
