CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE tipo_documento_usuario AS ENUM('ti', 'cc', 'ce');
CREATE TYPE rol_usuario AS ENUM('administrador', 'coordinador', 'docente', 'estudiante');
CREATE TYPE estado_cuenta_usuario AS ENUM('activo', 'inactivo', 'suspendido', 'eliminado');

CREATE TABLE "Usuario"(
    usuario_id UUID DEFAULT gen_random_uuid(),
    correo_institucional VARCHAR(100) UNIQUE,
    username VARCHAR(50) UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    tipo_documento tipo_documento_usuario NOT NULL,
    numero_documento VARCHAR(20) NOT NULL,
    rol rol_usuario NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    estado_cuenta estado_cuenta_usuario NOT NULL DEFAULT 'activo',
    fecha_creacion TIMESTAMPTZ DEFAULT now() NOT NULL,
    ultimo_acceso TIMESTAMPTZ NOT NULL,
    perfil_url TEXT,
    portada_url TEXT,
    telefono VARCHAR(20) UNIQUE,
    descripcion TEXT,
    CONSTRAINT pk_usuario PRIMARY KEY (usuario_id),

    CONSTRAINT chk_login
        CHECK (
            (rol = 'administrador' AND username IS NOT NULL AND correo_institucional IS NULL)
            OR
            (rol <> 'administrador' AND correo_institucional IS NOT NULL AND username IS NULL)
        )
);

INSERT INTO "Usuario"(
	usuario_id,
	correo_institucional,
	username,
	nombres,
	apellidos,
	tipo_documento,
	numero_documento,
	rol,
	password_hash,
	estado_cuenta,
	fecha_creacion,
	ultimo_acceso,
	perfil_url,
	portada_url,
	telefono,
	descripcion
) VALUES (
	'8be3abbb-fadc-4433-a85a-8e2c32cad666',
	NULL,
	'HarryDev_2006',
	'Harrison David',
	'Guerrero Palacios',
	'cc',
	'1034284499',
	'administrador',
	crypt('MiClaveEsReSegura', gen_salt('bf')),
	'activo',
	now(),
	now(),
	'',
	NULL,
	'3045955299',
	'Hola, soy Admin'
);

CREATE TABLE "AdministradorSistema"(
	administrador_id UUID REFERENCES "Usuario" (usuario_id) ON DELETE CASCADE,
	CONSTRAINT pk_administrador_sistema PRIMARY KEY (administrador_id)
);

INSERT INTO "AdministradorSistema"(	
	administrador_id
) VALUES (
	'8be3abbb-fadc-4433-a85a-8e2c32cad666'
);

CREATE TYPE tipo_vinculacion_docente AS ENUM('planta', 'catedra', 'ocasional', 'visitante', 'honorario');

CREATE TABLE "Docente"(
	docente_id UUID REFERENCES "Usuario" (usuario_id) ON DELETE CASCADE,
	area_conocimiento VARCHAR(50) NOT NULL,
	fecha_vinculacion DATE NOT NULL,
	tipo_vinculacion tipo_vinculacion_docente DEFAULT 'planta' NOT NULL,
	titulo_academico VARCHAR(50),
	horas_semanales SMALLINT,
	CONSTRAINT pk_docente PRIMARY KEY (docente_id)
);

CREATE TYPE tipo_institucion AS ENUM(
    'escuela',
    'colegio',
    'instituto',
    'universidad',
    'politecnico',
    'centro_de_formacion',
    'corporacion',
    'fundacion',
    'academia'
);

CREATE TYPE nivel_educativo_institucion AS ENUM('basica', 'media', 'tecnica', 'tecnologica', 'superior');

CREATE TYPE sector_institucion AS ENUM('publico', 'privado');

CREATE TABLE "Institucion"(
	institucion_id UUID DEFAULT gen_random_uuid(),
	administrador_id_creador UUID REFERENCES "AdministradorSistema" (administrador_id) ON DELETE SET NULL, 
	nombre VARCHAR(150) NOT NULL UNIQUE,
	sigla VARCHAR(20) UNIQUE,
	lema VARCHAR(255),
	tipo_institucion tipo_institucion NOT NULL,
	usa_programas BOOLEAN NOT NULL,
	nivel_educativo nivel_educativo_institucion NOT NULL,
	sector sector_institucion NOT NULL,
	direccion VARCHAR(255),
	ciudad VARCHAR(100),
	pais VARCHAR(100) NOT NULL,
	correo_institucional VARCHAR(100) NOT NULL UNIQUE,
	telefono VARCHAR(25-30) NOT NULL,
	nit VARCHAR(20) UNIQUE,
	CONSTRAINT pk_institucion PRIMARY KEY (institucion_id)
);

CREATE TYPE tipo_escalafon AS ENUM('numerica', 'letras', 'cualitativa');

CREATE TABLE "EscalaCalificacion"(
    escala_id UUID DEFAULT gen_random_uuid(),
    institucion_id UUID NOT NULL REFERENCES "Institucion"(institucion_id) ON DELETE CASCADE,
    nombre VARCHAR(50) NOT NULL, 
    tipo tipo_escalafon NOT NULL,
    min_valor NUMERIC(5,2),   
    max_valor NUMERIC(5,2),   
    CONSTRAINT pk_escala PRIMARY KEY (escala_id)
);

CREATE TABLE "ValorCalificacion"(
    valor_id UUID DEFAULT gen_random_uuid(),
    escala_id UUID REFERENCES "EscalaCalificacion"(escala_id) ON DELETE CASCADE,
    valor VARCHAR(10) NOT NULL,        
    descripcion VARCHAR(100),          
    orden SMALLINT,                  
    CONSTRAINT pk_valor PRIMARY KEY (valor_id)
);


CREATE TABLE "Coordinador"(
	coordinador_id UUID REFERENCES "Usuario" (usuario_id) ON DELETE CASCADE, 
	horario_atencion VARCHAR(50),
	fecha_inicio_carrera DATE NOT NULL,
	CONSTRAINT pk_coordinador PRIMARY KEY (coordinador_id)
);

CREATE TYPE estado_coordinador AS ENUM('activo', 'invitado', 'expirado', 'retirado');

CREATE TABLE "InstitucionCoordinador"(
	institucion_id UUID NOT NULL REFERENCES "Institucion" (institucion_id) ON DELETE CASCADE,
	coordinador_id UUID NOT NULL REFERENCES "Coordinador" (coordinador_id) ON DELETE CASCADE,
	fecha_asignacion DATE NOT NULL,
	estado estado_coordinador DEFAULT 'activo' NOT NULL,
	CONSTRAINT pk_institucion_coordinador PRIMARY KEY (institucion_id, coordinador_id)
);

CREATE TYPE nivel_programa AS ENUM('basico', 'media', 'tecnico', 'tecnologico', 'profesional', 'especializacion', 'maestria', 'doctorado', 'otro');
CREATE TYPE tipo_programa AS ENUM('presencial', 'virtual', 'mixto', 'a_distancia', 'dual', 'por_ciclos', 'continuo', 'otro');

CREATE TABLE "Programa"(
	programa_id UUID DEFAULT gen_random_uuid(),
	institucion_id UUID REFERENCES "Institucion" (institucion_id) ON DELETE CASCADE,
	nombre VARCHAR(100) NOT NULL,
	descripcion TEXT,
	nivel nivel_programa NOT NULL,
	tipo tipo_programa NOT NULL,
	CONSTRAINT pk_programa PRIMARY KEY (programa_id),
	CONSTRAINT uq_programa_nombre UNIQUE (institucion_id, nombre)
);

CREATE TYPE etapa_formativa_estudiante AS ENUM('i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii');

CREATE TABLE "Estudiante"(
	estudiante_id UUID REFERENCES "Usuario" (usuario_id) ON DELETE CASCADE,
	programa_id UUID REFERENCES "Programa" (programa_id) ON DELETE SET NULL,
	fecha_ingreso DATE NOT NULL,
	creditos_aprobados SMALLINT,
	etapa_formativa etapa_formativa_estudiante DEFAULT 'i' NOT NULL,
	promedio_acumulado DECIMAL(3,2),
	CONSTRAINT pk_estudiante PRIMARY KEY (estudiante_id)
);

CREATE TYPE jornada_grupo AS ENUM('manana', 'tarde', 'nocturna');

CREATE TABLE "Grupo"(
	grupo_id UUID DEFAULT gen_random_uuid(),
	programa_id UUID NOT NULL REFERENCES "Programa" (programa_id) ON DELETE CASCADE,
	docente_tutor_id UUID REFERENCES "Docente" (docente_id) ON DELETE SET NULL,
	nombre VARCHAR(50) NOT NULL,
	jornada jornada_grupo DEFAULT 'mañana' NOT NULL,
	CONSTRAINT pk_grupo PRIMARY KEY (grupo_id),
	CONSTRAINT uq_grupo_docente_tutor UNIQUE(docente_tutor_id)
);

CREATE TABLE "EstudianteGrupo"(
	grupo_id UUID REFERENCES "Grupo" (grupo_id) ON DELETE CASCADE,
	estudiante_id UUID REFERENCES "Estudiante" (estudiante_id) ON DELETE CASCADE,
	fecha_vinculacion DATE NOT NULL,
	CONSTRAINT pk_estudiante_grupo PRIMARY KEY (grupo_id, estudiante_id)
);

CREATE TYPE modalidad_curso AS ENUM('anual', 'semestral', 'trimestral', 'cuatrimestral', 'bimestral', 'mensual', 'modular', 'flexible', 'otro'); 

CREATE TABLE "Curso"(
	curso_id DEFAULT gen_random_uuid(),
	institucion_id UUID NOT NULL REFERENCES "Institucion" (institucion_id) ON DELETE CASCADE,
	coordinador_id UUID REFERENCES "Coordinador" (coordinador_id) ON DELETE SET NULL,
	programa_id UUID NOT NULL REFERENCES "Programa" (programa_id) ON DELETE CASCADE,
	nombre VARCHAR(50) NOT NULL,
	descripcion TEXT,
	modalidad modalidad_curso NOT NULL,
	fecha_inicio DATE,
	fecha_fin DATE,
	CONSTRAINT pk_curso PRIMARY KEY (curso_id),
	CONSTRAINT uq_curso_nombre UNIQUE (institucion_id, nombre)
);

CREATE TABLE "CursoDocente"(
    curso_id UUID REFERENCES "Curso" (curso_id) ON DELETE CASCADE,
    docente_id UUID NOT NULL REFERENCES "Docente" (docente_id) ON DELETE CASCADE,
    fecha_asignacion DATE,
    CONSTRAINT pk_curso_docente PRIMARY KEY (curso_id, docente_id)
);

CREATE TABLE "GrupoCurso"(
	grupo_curso_id UUID DEFAULT gen_random_uuid(),
	grupo_id UUID REFERENCES "Grupo" (grupo_id) ON DELETE CASCADE,
	curso_id UUID REFERENCES "Curso" (curso_id) ON DELETE CASCADE,
	docente_id UUID REFERENCES "Docente" (docente_id) ON DELETE CASCADE,
	fecha_asignacion DATE,
	CONSTRAINT pk_grupo_curso PRIMARY KEY (grupo_curso_id),
	CONSTRAINT uq_grupo_curso UNIQUE (curso_id, grupo_id)
);

CREATE TYPE estado_chat_grupo AS ENUM('activo', 'archivado', 'eliminado');

CREATE TABLE "ChatGrupo"(
	chat_grupo_id UUID DEFAULT gen_random_uuid(),
	grupo_id UUID NOT NULL REFERENCES "Grupo" (grupo_id) ON DELETE CASCADE,
	fecha_creacion TIMESTAMPTZ DEFAULT now() NOT NULL,
	descripcion TEXT,
	foto_perfil TEXT,
	permite_archivos BOOLEAN NOT NULL DEFAULT TRUE,
	capacidad_almacenamiento INT DEFAULT 52428800 NOT NULL,
	estado_chat estado_chat_grupo DEFAULT 'activo' NOT NULL,
	CONSTRAINT pk_chat_grupo PRIMARY KEY (chat_grupo_id)
);

CREATE TYPE tipo_mensaje AS ENUM('texto', 'archivo', 'imagen', 'audio');

CREATE TABLE "Mensaje"(
	mensaje_id UUID DEFAULT gen_random_uuid(),
	chat_grupo_id UUID REFERENCES "ChatGrupo" (chat_grupo_id) ON DELETE CASCADE,
	emisor_id UUID REFERENCES "Usuario" (usuario_id) ON DELETE SET NULL,
	fecha_hora TIMESTAMPTZ DEFAULT now() NOT NULL,
	tipo tipo_mensaje NOT NULL,
	contenido TEXT NOT NULL,
	CONSTRAINT pk_mensaje PRIMARY KEY (mensaje_id)
);

CREATE TABLE "ArchivoChat"(
	archivo_id UUID DEFAULT gen_random_uuid(),
	chat_grupo_id UUID REFERENCES "ChatGrupo" (chat_grupo_id) ON DELETE CASCADE,
	usuario_id UUID REFERENCES "Usuario" (usuario_id) ON DELETE SET NULL,
	nombre_archivo TEXT NOT NULL,
	url_archivo TEXT NOT NULL,
	fecha_envio TIMESTAMPTZ DEFAULT now() NOT NULL,
	tipo_archivo TEXT,
	CONSTRAINT pk_archivo PRIMARY KEY (archivo_id)
);

CREATE TYPE tipo_integracion_plataforma AS ENUM('api', 'manual', 'embebido', 'otro');

CREATE TABLE "Plataforma"(
	plataforma_id UUID DEFAULT gen_random_uuid(),
	nombre VARCHAR(50) NOT NULL UNIQUE,
	url_base TEXT NOT NULL,
	tipo_integracion tipo_integracion_plataforma NOT NULL,
	requiere_cuenta BOOLEAN NOT NULL,
	es_gratuita BOOLEAN,
	CONSTRAINT pk_plataforma PRIMARY KEY (plataforma_id)
);

CREATE TABLE "Clase"(
	clase_id UUID DEFAULT gen_random_uuid(),
	grupo_curso_id UUID NOT NULL REFERENCES "GrupoCurso" (grupo_curso_id) ON DELETE CASCADE,
	plataforma_id UUID REFERENCES "Plataforma" (plataforma_id) ON DELETE SET NULL,
	titulo TEXT NOT NULL,
	descripcion TEXT,
	hora_inicio TIMESTAMPTZ DEFAULT now() NOT NULL,
	duracion INTERVAL NOT NULL,
	link_videollamada TEXT NOT NULL,
	CONSTRAINT pk_clase PRIMARY KEY (clase_id)
);


CREATE TYPE estado_asistencia AS ENUM ('presente', 'ausente', 'justificado');

CREATE TABLE "Asistencia" (
	asistencia_id UUID DEFUALT gen_random_uuid(),
	clase_id UUID NOT NULL REFERENCES "Clase" (clase_id) ON DELETE CASCADE,
	estudiante_id UUID NOT NULL REFERENCES "Estudiante" (estudiante_id) ON DELETE CASCADE,
	estado estado_asistencia NOT NULL,
	CONSTRAINT pk_asistencia PRIMARY KEY (asistencia_id)
);

CREATE TYPE tipo_insignia AS ENUM ('objetivo', 'calificacion', 'racha', 'manual');

CREATE TABLE "Insignia" (
    insignia_id UUID DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    imagen_url TEXT,
    tipo tipo_insignia NOT NULL DEFAULT 'manual',
    es_unica BOOLEAN NOT NULL,
    CONSTRAINT pk_insignia PRIMARY KEY (insignia_id)
);

CREATE TABLE "UsuarioInsignia" (
    usuario_id UUID REFERENCES "Usuario" (usuario_id) ON DELETE CASCADE, 
    insignia_id UUID REFERENCES "Insignia" (insignia_id) ON DELETE CASCADE,
    otorgada_por UUID REFERENCES "Usuario" (usuario_id) ON DELETE SET NULL,
    fecha_otorgada TIMESTAMPTZ DEFAULT now() NOT NULL,
	CONSTRAINT pk_usuario_insignia PRIMARY KEY (usuario_id, insignia_id)
);

CREATE TYPE tipo_recompensa AS ENUM (
    'foto_perfil',
    'foto_portada',
    'estilo_chat',
    'sticker',
    'otro'
);

CREATE TABLE "Recompensa" (
    recompensa_id UUID DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    costo_puntos INT NOT NULL CHECK (costo_puntos >= 0),
    tipo tipo_recompensa NOT NULL DEFAULT 'otro',
    CONSTRAINT pk_recompensa PRIMARY KEY (recompensa_id)
);

CREATE TABLE "UsuarioRecompensa" (
    usuario_recompensa_id UUID DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES "Usuario" (usuario_id) ON DELETE CASCADE,
    recompensa_id UUID NOT NULL REFERENCES "Recompensa" (recompensa_id) ON DELETE CASCADE,
    fecha_canje TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT pk_usuario_recompensa PRIMARY KEY (usuario_recompensa_id)
);

CREATE TABLE "UsuarioPuntos" (
    usuario_id UUID REFERENCES "Usuario" (usuario_id) ON DELETE CASCADE,
    puntos_acumulados INT NOT NULL DEFAULT 0,
    CONSTRAINT pk_usuario_puntos PRIMARY KEY (usuario_id)
);

CREATE TABLE "HistorialPuntos" (
    historial_id UUID DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES "Usuario"(usuario_id) ON DELETE CASCADE,
    cambio INT NOT NULL CHECK (cambio <> 0),
    motivo TEXT NOT NULL,
    fecha TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT pk_historial_puntos PRIMARY KEY (historial_id)
);


CREATE TABLE "Tema" (
    tema_id UUID DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    emoji VARCHAR(8) NOT NULL,
    CONSTRAINT pk_tema PRIMARY KEY (tema_id)
);


CREATE TABLE "TemaPredefinido" (
    tema_id UUID PRIMARY KEY REFERENCES "Tema"(tema_id) ON DELETE CASCADE,
    CONSTRAINT uq_nombre_predefinido UNIQUE (tema_id)
);


CREATE TABLE "TemaPersonalizado" (
    tema_id UUID PRIMARY KEY REFERENCES "Tema"(tema_id) ON DELETE CASCADE,
    usuario_id UUID NOT NULL REFERENCES "Usuario"(usuario_id) ON DELETE CASCADE,
    CONSTRAINT uq_usuario_nombre UNIQUE (usuario_id, tema_id)
);
 
CREATE TYPE tipo_material_educativo AS ENUM('pdf', 'video', 'audio', 'imagen', 'presentacion', 'documento', 'hoja_de_calculo', 'enlace', 'interactivo', 'codigo_fuente', 'otro');

CREATE TABLE "MaterialEducativo" (
	material_id UUID DEFAULT gen_random_uuid(),
	titulo VARCHAR(100) NOT NULL,
	descripcion TEXT,
	tipo_material tipo_material_educativo NOT NULL,
	url_archivo VARCHAR(255) NOT NULL,
	formato_archivo VARCHAR(10) NOT NULL,
	CONSTRAINT pk_material_educativo PRIMARY KEY (material_id) 
);

CREATE TABLE "MaterialClase" (
	material_clase_id UUID REFERENCES "MaterialEducativo" (material_id) ON DELETE CASCADE,
	clase_id UUID REFERENCES "Clase" (clase_id) ON DELETE SET NULL,
	CONSTRAINT pk_material_clase PRIMARY KEY (material_clase_id)
);

CREATE TABLE "MaterialCurso" (
	material_curso_id UUID REFERENCES "MaterialEducativo" (material_id) ON DELETE CASCADE,
	curso_id UUID REFERENCES "Curso" (curso_id) ON DELETE SET NULL,
	PRIMARY KEY (material_curso_id, curso_id)
);

CREATE TABLE "Tarea"(
	tarea_id UUID DEFAULT gen_random_uuid(),
	docente_id UUID REFERENCES "Docente" (docente_id) ON DELETE SET NULL,
	clase_id UUID REFERENCES "Clase" (clase_id) ON DELETE CASCADE,
	titulo VARCHAR(50) NOT NULL,
	descripcion TEXT,
	fecha_asignacion TIMESTAMPTZ DEFAULT now() NOT NULL,
	fecha_limite TIMESTAMPTZ, 
	archivo_adjunto TEXT,
	permite_entregas_tardias BOOLEAN NOT NULL,
	CONSTRAINT pk_tarea PRIMARY KEY (tarea_id)
);

CREATE TABLE "EntregarTarea"(
    entrega_id UUID DEFAULT gen_random_uuid(),
    tarea_id UUID REFERENCES "Tarea" (tarea_id) ON DELETE CASCADE,
    estudiante_id UUID REFERENCES "Estudiante" (estudiante_id) ON DELETE CASCADE,
    archivo TEXT NOT NULL,
    fecha_envio TIMESTAMPTZ DEFAULT now() NOT NULL,
    calificacion NUMERIC(3,1) CHECK (calificacion >= 0 AND calificacion <= 5),
    fecha_revision TIMESTAMPTZ, -- null = sin revisar, con valor = revisado
    CONSTRAINT pk_entrega PRIMARY KEY (entrega_id),
    CONSTRAINT uq_entrega UNIQUE (tarea_id, estudiante_id) -- evita duplicados
);

CREATE TABLE "ChatBot" (
	chat_bot_id UUID DEFAULT gen_random_uuid(),
	nombre VARCHAR(100) NOT NULL UNIQUE,
	descripcion TEXT NOT NULL,
	foto_perfil_url TEXT NOT NULL,
	activo BOOLEAN,
	fecha_registro DATE DEFAULT now(),
	CONSTRAINT pk_chat_bot PRIMARY KEY (chat_bot_id)
);

CREATE TABLE "FAQBot" (
	faq_id UUID DEFAULT gen_random_uuid(),
	pregunta TEXT NOT NULL,
	respuesta TEXT NOT NULL,
	categoria VARCHAR(50) NOT NULL,
	ultima_actualizacion TIMESTAMP,
	CONSTRAINT pk_faq_id PRIMARY KEY (faq_id)
);

CREATE TYPE contexto_mensaje AS ENUM('publico', 'grupo', 'directo');

CREATE TABLE "MensajeBot" (
    mensaje_bot_id UUID DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES "Usuario" (usuario_id) ON DELETE SET NULL,
    chat_grupo_id UUID REFERENCES "ChatGrupo" (chat_grupo_id) ON DELETE CASCADE,
    referencia_material_id UUID REFERENCES "MaterialEducativo" (material_id),
    contenido TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    contexto contexto_mensaje NOT NULL,
    fecha_hora TIMESTAMP DEFAULT now() NOT NULL,
    CONSTRAINT pk_mensaje_bot PRIMARY KEY (mensaje_bot_id)
);
