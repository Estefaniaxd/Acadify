from .academic import (
    curso_docente,
    curso,
    estudiante_grupo,
    grupo_curso,
    grupo,
    institucion,
    material_clase,
    material_curso,
    material_educativo,
    programa,
)

from .assessment import escala_calificacion, valor_calificacion

from .auth import auth

from .classes import (
    asistencia,
    clase,
    entregar_tarea,
    plataforma,
    tarea,
)

from .communication import (
    archivo_chat,
    chat_bot,
    chat_grupo,
    faq_bot,
    mensaje_bot,
    mensaje,
)

from .gamification import (
    gamificacion,
    insignias,
    puntos,
    recompensas,
    temas,
)

from .users import usuario

routers = [
    # Academic
    (curso_docente.router, "/cursos-docentes", ["CursoDocente"]),
    (curso.router, "/cursos", ["Curso"]),
    (estudiante_grupo.router, "/estudiantes-grupos", ["EstudianteGrupo"]),
    (grupo_curso.router, "/grupos-cursos", ["GupoCurso"]),
    (grupo.router, "/grupos", ["Grupo"]),
    (institucion.router, "/instituciones", ["Institucion"]),
    (material_clase.router, "/materiales-clases", ["MaterialClase"]),
    (material_curso.router, "/materiales-cursos", ["MaterialCurso"]),
    (material_educativo.router, "/materiales-educativos", ["MaterialEducativo"]),
    (programa.router, "/programas", ["Programa"]),
    # Assessment
    (escala_calificacion.router, "/escalas-calificacion", ["EscalaCalificacion"]),
    (valor_calificacion.router, "/valores-calificacion", ["ValorCalificacion"]),
    # Auth
    (auth.router, "/auths", ["Auth"]),
    # Classes
    (asistencia.router, "/asistencias", ["Asistencia"]),
    (clase.router, "/clases", ["Clase"]),
    (entregar_tarea.router, "/entregas", ["EntregarTarea"]),
    (plataforma.router, "/plataformas", ["Plataforma"]),
    (tarea.router, "/tareas", ["Tarea"]),
    # Communication
    (archivo_chat.router, "/archivos-chats", ["ArchivoChat"]),
    (chat_bot.router, "/chat-bot", ["ChatBot"]),
    (chat_grupo.router, "/chats-grupos", ["ChatGrupo"]),
    (faq_bot.router, "/faq-bot", ["FaqBot"]),
    (mensaje_bot.router, "/mensajes-bot", ["MensajeBot"]),
    (mensaje.router, "/mensajes", ["Mensaje"]),
    # Gamification
    (gamificacion.router, "/gamificaciones", ["Gamificacion"]),
    (insignias.router, "/insignias", ["Insignia"]),
    (puntos.router, "/puntos", ["Punto"]),
    (recompensas.router, "/recompensas", ["Recompensa"]),
    (temas.router, "/temas", ["Tema"]),
    # Users
    (usuario.router, "/usuarios", ["Usuario"]),
]
