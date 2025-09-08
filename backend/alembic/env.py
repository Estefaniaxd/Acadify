from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os 
from dotenv import load_dotenv
from src.db.base_class import Base

# Cargar los 38 mkodelos 

from src.models.administrador_sistema import AdministradorSistema
from src.models.archivo_chat import ArchivoChat
from src.models.asistencia import Asistencia
from src.models.chat_bot import ChatBot
from src.models.chat_grupo import ChatGrupo
from src.models.clase import Clase
from src.models.coordinador import Coordinador
from src.models.curso_docente import CursoDocente
from src.models.curso import Curso
from src.models.docente import Docente
from src.models.entregar_tarea import EntregarTarea
from src.models.escala_calificacion import EscalaCalificacion
from src.models.estudiante_grupo import EstudianteGrupo
from src.models.estudiante import Estudiante
from src.models.faqbot_id import FAQBot
from src.models.grupo_curso import GrupoCurso
from src.models.grupo import Grupo
from src.models.historial_puntos import HistorialPuntos
from src.models.insignia import Insignia
from src.models.institucion_coordinador import InstitucionCoordinador
from src.models.institucion import Institucion
from src.models.material_educativo import MaterialEducativo
from src.models.material_clase import MaterialClase
from src.models.material_curso import MaterialCurso
from src.models.mensaje_bot import MensajeBot
from src.models.mensaje import Mensaje
from src.models.plataforma import Platafroma
from src.models.programa import Programa
from src.models.recompensa import Recompensa
from src.models.tarea import Tarea
from src.models.tema_personalizado import TemaPersonalizado
from src.models.tema_predefinido import TemaPredefinido
from src.models.tema import Tema
from src.models.usuario_insignia import UsuarioInsignia
from src.models.usuario_puntos import UsuarioPuntos
from src.models.usuario_recompensa import UsuarioRecompensa
from src.models.usuario import Usuario
from src.models.valor_calificacion import ValorCalificacion

load_dotenv()
config = context.config

config.set_main_option(
    "sqlalchemy.url", os.environ.get("DATABASE_URL")
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
