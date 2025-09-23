# Importar las rutas correctamente
try:
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
except ImportError as e:
    import logging
    logging.error(f"Error al importar módulos académicos: {e}")

try:
    from .assessment import escala_calificacion, valor_calificacion
except ImportError as e:
    import logging
    logging.error(f"Error al importar módulos de evaluación: {e}")

try:
    from .auth_main import router as auth_router
except ImportError as e:
    import logging
    logging.error(f"Error al importar módulos de autenticación: {e}")

try:
    from .classes import (
        asistencia,
        clase,
        entregar_tarea,
        plataforma,
        tarea,
    )
except ImportError as e:
    import logging
    logging.error(f"Error al importar módulos de clases: {e}")

try:
    from .communication import (
        archivo_chat,
        chat_bot,
        chat_grupo,
        faq_bot,
        mensaje_bot,
        mensaje,
    )
except ImportError as e:
    import logging
    logging.error(f"Error al importar módulos de comunicación: {e}")

try:
    from .gamification import (
        gamificacion,
        insignias,
        puntos,
        recompensas,
        temas,
    )
except ImportError as e:
    import logging
    logging.error(f"Error al importar módulos de gamificación: {e}")

try:
    from .users import usuario
    from .admin_institucion import router as admin_institucion_router
    from .coordinador_invitacion import router as coordinador_invitacion_router
    from .debug import router as debug_router
    # from .avatar import router as avatar_router
except ImportError as e:
    import logging
    logging.error(f"Error al importar módulos de usuarios: {e}")

# Importar avatar por separado para debugging
try:
    from .avatar import router as avatar_router
    avatar_available = True
except ImportError as e:
    import logging
    logging.error(f"Error al importar avatar router: {e}")
    avatar_router = None
    avatar_available = False

# Lista de rutas disponibles
routers = [
    # Academic
    (curso_docente.router, "/cursos-docentes", ["CursoDocente"]),
    (curso.router, "/cursos", ["Curso"]),
    (estudiante_grupo.router, "/estudiantes-grupos", ["EstudianteGrupo"]),
    (grupo_curso.router, "/grupos-cursos", ["GrupoCurso"]),
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
    (auth_router, "/auth", ["Autenticación"]),
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
    # Admin - Instituciones y Coordinadores
    (admin_institucion_router, "/admin", ["Administrador"]),
    (coordinador_invitacion_router, "/coordinador", ["Coordinador"]),
    # Debug
    (debug_router, "/debug", ["Depuración"]),
]

# Agregar avatar router si está disponible
if avatar_available and avatar_router:
    routers.append((avatar_router, "/avatar", ["Avatar"]))
