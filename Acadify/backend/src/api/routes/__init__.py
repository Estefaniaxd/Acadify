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

routers = []
# Academic
if 'curso_docente' in locals():
    routers.append((curso_docente.router, "/cursos-docentes", ["CursoDocente"]))
if 'curso' in locals():
    routers.append((curso.router, "/academic/cursos", ["Cursos"]))
if 'estudiante_grupo' in locals():
    routers.append((estudiante_grupo.router, "/estudiantes-grupos", ["EstudianteGrupo"]))
if 'grupo_curso' in locals():
    routers.append((grupo_curso.router, "/grupos-cursos", ["GrupoCurso"]))
if 'grupo' in locals():
    routers.append((grupo.router, "/grupos", ["Grupo"]))
if 'institucion' in locals():
    routers.append((institucion.router, "/instituciones", ["Institucion"]))
if 'material_clase' in locals():
    routers.append((material_clase.router, "/materiales-clases", ["MaterialClase"]))
if 'material_curso' in locals():
    routers.append((material_curso.router, "/materiales-cursos", ["MaterialCurso"]))
if 'material_educativo' in locals():
    routers.append((material_educativo.router, "/materiales-educativos", ["MaterialEducativo"]))
if 'programa' in locals():
    routers.append((programa.router, "/programas", ["Programa"]))
# Assessment
if 'escala_calificacion' in locals():
    routers.append((escala_calificacion.router, "/escalas-calificacion", ["EscalaCalificacion"]))
if 'valor_calificacion' in locals():
    routers.append((valor_calificacion.router, "/valores-calificacion", ["ValorCalificacion"]))
# Auth
if 'auth_router' in locals():
    routers.append((auth_router, "/auth", ["Autenticación"]))
# Classes
if 'asistencia' in locals():
    routers.append((asistencia.router, "/asistencias", ["Asistencia"]))
if 'clase' in locals():
    routers.append((clase.router, "/clases", ["Clase"]))
if 'entregar_tarea' in locals():
    routers.append((entregar_tarea.router, "/entregas", ["EntregarTarea"]))
if 'plataforma' in locals():
    routers.append((plataforma.router, "/plataformas", ["Plataforma"]))
if 'tarea' in locals():
    routers.append((tarea.router, "/tareas", ["Tarea"]))
# Communication
if 'archivo_chat' in locals():
    routers.append((archivo_chat.router, "/archivos-chats", ["ArchivoChat"]))
if 'chat_bot' in locals():
    routers.append((chat_bot.router, "/chat-bot", ["ChatBot"]))
if 'chat_grupo' in locals():
    routers.append((chat_grupo.router, "/chats-grupos", ["ChatGrupo"]))
if 'faq_bot' in locals():
    routers.append((faq_bot.router, "/faq-bot", ["FaqBot"]))
if 'mensaje_bot' in locals():
    routers.append((mensaje_bot.router, "/mensajes-bot", ["MensajeBot"]))
if 'mensaje' in locals():
    routers.append((mensaje.router, "/mensajes", ["Mensaje"]))
# Gamification
if 'gamificacion' in locals():
    routers.append((gamificacion.router, "/gamificaciones", ["Gamificacion"]))
if 'insignias' in locals():
    routers.append((insignias.router, "/insignias", ["Insignia"]))
if 'puntos' in locals():
    routers.append((puntos.router, "/puntos", ["Punto"]))
if 'recompensas' in locals():
    routers.append((recompensas.router, "/recompensas", ["Recompensa"]))
if 'temas' in locals():
    routers.append((temas.router, "/temas", ["Tema"]))
# Users
if 'usuario' in locals():
    routers.append((usuario.router, "/usuarios", ["Usuario"]))
# Admin - Instituciones y Coordinadores
if 'admin_institucion_router' in locals():
    routers.append((admin_institucion_router, "/admin", ["Administrador"]))
if 'coordinador_invitacion_router' in locals():
    routers.append((coordinador_invitacion_router, "/coordinador", ["Coordinador"]))
# Debug
if 'debug_router' in locals():
    routers.append((debug_router, "/debug", ["Depuración"]))
# Avatar
if 'avatar_available' in locals() and avatar_available and 'avatar_router' in locals() and avatar_router:
    routers.append((avatar_router, "/avatar", ["Avatar"]))
