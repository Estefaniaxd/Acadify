--
-- PostgreSQL database dump
--

\restrict fgrE8ATlgdBfIeltkZvTfJNEXj9bZoyNrky7fVziech0IQCKz7n7a1ocRm9JnDr

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: contexto_mensaje; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.contexto_mensaje AS ENUM (
    'publico',
    'grupo',
    'directo'
);


ALTER TYPE public.contexto_mensaje OWNER TO postgres;

--
-- Name: estado_asistencia; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_asistencia AS ENUM (
    'presente',
    'ausente',
    'justificado'
);


ALTER TYPE public.estado_asistencia OWNER TO postgres;

--
-- Name: estado_chat_grupo; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_chat_grupo AS ENUM (
    'activo',
    'archivado',
    'eliminado'
);


ALTER TYPE public.estado_chat_grupo OWNER TO postgres;

--
-- Name: estado_coordinador; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_coordinador AS ENUM (
    'activo',
    'invitado',
    'expirado',
    'retirado'
);


ALTER TYPE public.estado_coordinador OWNER TO postgres;

--
-- Name: estado_cuenta_usuario; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_cuenta_usuario AS ENUM (
    'activo',
    'inactivo',
    'suspendido',
    'eliminado'
);


ALTER TYPE public.estado_cuenta_usuario OWNER TO postgres;

--
-- Name: etapa_formativa_estudiante; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.etapa_formativa_estudiante AS ENUM (
    'i',
    'ii',
    'iii',
    'iv',
    'v',
    'vi',
    'vii',
    'viii',
    'ix',
    'x',
    'xi',
    'xii'
);


ALTER TYPE public.etapa_formativa_estudiante OWNER TO postgres;

--
-- Name: jornada_grupo; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.jornada_grupo AS ENUM (
    'mañana',
    'tarde',
    'nocturna'
);


ALTER TYPE public.jornada_grupo OWNER TO postgres;

--
-- Name: modalidad_curso; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.modalidad_curso AS ENUM (
    'anual',
    'semestral',
    'trimestral',
    'cuatrimestral',
    'bimestral',
    'mensual',
    'modular',
    'flexible',
    'otro'
);


ALTER TYPE public.modalidad_curso OWNER TO postgres;

--
-- Name: nivel_educativo_institucion; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.nivel_educativo_institucion AS ENUM (
    'basica',
    'media',
    'tecnica',
    'tecnologica',
    'superior'
);


ALTER TYPE public.nivel_educativo_institucion OWNER TO postgres;

--
-- Name: nivel_programa; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.nivel_programa AS ENUM (
    'basico',
    'media',
    'tecnico',
    'tecnologico',
    'profesional',
    'especializacion',
    'maestria',
    'doctorado',
    'otro'
);


ALTER TYPE public.nivel_programa OWNER TO postgres;

--
-- Name: rol_usuario; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.rol_usuario AS ENUM (
    'administrador',
    'coordinador',
    'docente',
    'estudiante'
);


ALTER TYPE public.rol_usuario OWNER TO postgres;

--
-- Name: sector_institucion; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.sector_institucion AS ENUM (
    'publico',
    'privado'
);


ALTER TYPE public.sector_institucion OWNER TO postgres;

--
-- Name: tipo_documento_usuario; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_documento_usuario AS ENUM (
    'ti',
    'cc',
    'ce'
);


ALTER TYPE public.tipo_documento_usuario OWNER TO postgres;

--
-- Name: tipo_escalafon; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_escalafon AS ENUM (
    'numerica',
    'letras',
    'cualitativa'
);


ALTER TYPE public.tipo_escalafon OWNER TO postgres;

--
-- Name: tipo_insignia; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_insignia AS ENUM (
    'objetivo',
    'calificacion',
    'racha',
    'manual'
);


ALTER TYPE public.tipo_insignia OWNER TO postgres;

--
-- Name: tipo_institucion; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_institucion AS ENUM (
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


ALTER TYPE public.tipo_institucion OWNER TO postgres;

--
-- Name: tipo_integracion_plataforma; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_integracion_plataforma AS ENUM (
    'api',
    'manual',
    'embebido',
    'otro'
);


ALTER TYPE public.tipo_integracion_plataforma OWNER TO postgres;

--
-- Name: tipo_material_educativo; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_material_educativo AS ENUM (
    'pdf',
    'video',
    'audio',
    'imagen',
    'presentacion',
    'documento',
    'hoja_de_calculo',
    'enlace',
    'interactivo',
    'codigo_fuente',
    'otro'
);


ALTER TYPE public.tipo_material_educativo OWNER TO postgres;

--
-- Name: tipo_mensaje; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_mensaje AS ENUM (
    'texto',
    'archivo',
    'imagen',
    'audio'
);


ALTER TYPE public.tipo_mensaje OWNER TO postgres;

--
-- Name: tipo_programa; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_programa AS ENUM (
    'presencial',
    'virtual',
    'mixto',
    'a_distancia',
    'dual',
    'por_ciclos',
    'continuo',
    'otro'
);


ALTER TYPE public.tipo_programa OWNER TO postgres;

--
-- Name: tipo_vinculacion_institucion; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_vinculacion_institucion AS ENUM (
    'planta',
    'catedra',
    'ocasional',
    'visitante',
    'honorario'
);


ALTER TYPE public.tipo_vinculacion_institucion OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: AdministradorSistema; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."AdministradorSistema" (
    administrador_id uuid NOT NULL
);


ALTER TABLE public."AdministradorSistema" OWNER TO postgres;

--
-- Name: ArchivoChat; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."ArchivoChat" (
    archivo_id uuid NOT NULL,
    chat_grupo_id uuid,
    usuario_id uuid,
    nombre_archivo text NOT NULL,
    url_archivo text NOT NULL,
    fecha_envio timestamp with time zone DEFAULT now() NOT NULL,
    tipo_archivo text
);


ALTER TABLE public."ArchivoChat" OWNER TO postgres;

--
-- Name: Asistencia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Asistencia" (
    asistencia_id uuid NOT NULL,
    clase_id uuid,
    estudiante_id uuid,
    estado public.estado_asistencia NOT NULL
);


ALTER TABLE public."Asistencia" OWNER TO postgres;

--
-- Name: ChatBot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."ChatBot" (
    chat_bot_id uuid NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text NOT NULL,
    foto_perfil_url text NOT NULL,
    activo boolean,
    fecha_registro date DEFAULT now()
);


ALTER TABLE public."ChatBot" OWNER TO postgres;

--
-- Name: ChatGrupo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."ChatGrupo" (
    chat_grupo_id uuid NOT NULL,
    grupo_id uuid,
    fecha_creacion timestamp with time zone DEFAULT now() NOT NULL,
    descripcion text,
    foto_perfil text,
    permite_archivos boolean DEFAULT true NOT NULL,
    capacidad_almacenamiento integer DEFAULT 52428800 NOT NULL,
    estado_chat public.estado_chat_grupo DEFAULT 'activo'::public.estado_chat_grupo NOT NULL
);


ALTER TABLE public."ChatGrupo" OWNER TO postgres;

--
-- Name: Clase; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Clase" (
    clase_id uuid NOT NULL,
    grupo_curso_id uuid,
    plataforma_id uuid,
    titulo text NOT NULL,
    descripcion text,
    hora_inicio timestamp with time zone DEFAULT now() NOT NULL,
    duracion interval NOT NULL,
    link_videollamada text NOT NULL
);


ALTER TABLE public."Clase" OWNER TO postgres;

--
-- Name: Coordinador; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Coordinador" (
    coordinador_id uuid NOT NULL,
    institucion_id uuid,
    horario_atencion character varying(50),
    fecha_inicio_carrera date NOT NULL
);


ALTER TABLE public."Coordinador" OWNER TO postgres;

--
-- Name: Curso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Curso" (
    curso_id uuid NOT NULL,
    institucion_id uuid,
    coordinador_id uuid,
    programa_id uuid,
    nombre character varying(50) NOT NULL,
    descripcion text,
    modalidad public.modalidad_curso NOT NULL,
    fecha_inicio date,
    fecha_fin date
);


ALTER TABLE public."Curso" OWNER TO postgres;

--
-- Name: CursoDocente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."CursoDocente" (
    curso_id uuid NOT NULL,
    docente_id uuid NOT NULL,
    fecha_asignacion date
);


ALTER TABLE public."CursoDocente" OWNER TO postgres;

--
-- Name: Docente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Docente" (
    docente_id uuid NOT NULL,
    area_conocimiento character varying(50) NOT NULL,
    fecha_vinculacion date NOT NULL,
    tipo_vinculacion public.tipo_vinculacion_institucion DEFAULT 'planta'::public.tipo_vinculacion_institucion NOT NULL,
    titulo_academico character varying(50),
    horas_semanales smallint
);


ALTER TABLE public."Docente" OWNER TO postgres;

--
-- Name: EntregarTarea; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."EntregarTarea" (
    entrega_id uuid NOT NULL,
    tarea_id uuid,
    estudiante_id uuid,
    archivo text NOT NULL,
    fecha_envio timestamp with time zone DEFAULT now() NOT NULL,
    calificacion numeric(3,1),
    fecha_revision timestamp with time zone,
    CONSTRAINT "EntregarTarea_calificacion_check" CHECK (((calificacion >= (0)::numeric) AND (calificacion <= (5)::numeric)))
);


ALTER TABLE public."EntregarTarea" OWNER TO postgres;

--
-- Name: EscalaCalificacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."EscalaCalificacion" (
    escala_id uuid NOT NULL,
    institucion_id uuid,
    nombre character varying(50) NOT NULL,
    tipo public.tipo_escalafon NOT NULL,
    min_valor numeric(5,2),
    max_valor numeric(5,2)
);


ALTER TABLE public."EscalaCalificacion" OWNER TO postgres;

--
-- Name: Estudiante; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Estudiante" (
    estudiante_id uuid NOT NULL,
    programa_id uuid,
    fecha_ingreso date NOT NULL,
    creditos_aprobados smallint,
    etapa_formativa public.etapa_formativa_estudiante DEFAULT 'i'::public.etapa_formativa_estudiante NOT NULL,
    promedio_acumulado numeric(3,2)
);


ALTER TABLE public."Estudiante" OWNER TO postgres;

--
-- Name: EstudianteGrupo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."EstudianteGrupo" (
    estudiante_grupo_id uuid NOT NULL,
    grupo_id uuid,
    estudiante_id uuid,
    fecha_vinculacion date NOT NULL
);


ALTER TABLE public."EstudianteGrupo" OWNER TO postgres;

--
-- Name: FAQBot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."FAQBot" (
    faq_id uuid NOT NULL,
    pregunta text NOT NULL,
    respuesta text NOT NULL,
    categoria character varying(50) NOT NULL,
    ultima_actualizacion timestamp without time zone
);


ALTER TABLE public."FAQBot" OWNER TO postgres;

--
-- Name: Grupo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Grupo" (
    grupo_id uuid NOT NULL,
    programa_id uuid,
    docente_tutor_id uuid,
    nombre character varying(50) NOT NULL,
    jornada public.jornada_grupo DEFAULT 'mañana'::public.jornada_grupo NOT NULL
);


ALTER TABLE public."Grupo" OWNER TO postgres;

--
-- Name: GrupoCurso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."GrupoCurso" (
    grupo_curso_id uuid NOT NULL,
    grupo_id uuid,
    curso_id uuid,
    docente_id uuid,
    fecha_asignacion date
);


ALTER TABLE public."GrupoCurso" OWNER TO postgres;

--
-- Name: Insignia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Insignia" (
    insignia_id uuid NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    imagen_url text,
    tipo public.tipo_insignia DEFAULT 'manual'::public.tipo_insignia NOT NULL,
    es_unica boolean NOT NULL
);


ALTER TABLE public."Insignia" OWNER TO postgres;

--
-- Name: Institucion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Institucion" (
    institucion_id uuid NOT NULL,
    administrador_id uuid,
    nombre character varying(150) NOT NULL,
    sigla character varying(20),
    lema character varying(255),
    tipo_institucion public.tipo_institucion NOT NULL,
    usa_programas boolean NOT NULL,
    nivel_educativo public.nivel_educativo_institucion NOT NULL,
    sector public.sector_institucion NOT NULL,
    direccion character varying(255),
    ciudad character varying(100),
    pais character varying(100) NOT NULL,
    correo_institucional character varying(100) NOT NULL,
    telefono character varying(20) NOT NULL,
    nit character varying(20)
);


ALTER TABLE public."Institucion" OWNER TO postgres;

--
-- Name: InstitucionCoordinador; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."InstitucionCoordinador" (
    institucion_coordinador_id uuid,
    institucion_id uuid,
    coordinador_id uuid,
    fecha_asignacion date NOT NULL,
    estado public.estado_coordinador DEFAULT 'activo'::public.estado_coordinador NOT NULL
);


ALTER TABLE public."InstitucionCoordinador" OWNER TO postgres;

--
-- Name: MaterialClase; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."MaterialClase" (
    material_clase_id uuid NOT NULL,
    clase_id uuid
);


ALTER TABLE public."MaterialClase" OWNER TO postgres;

--
-- Name: MaterialCurso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."MaterialCurso" (
    material_curso_id uuid NOT NULL,
    curso_id uuid NOT NULL
);


ALTER TABLE public."MaterialCurso" OWNER TO postgres;

--
-- Name: MaterialEducativo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."MaterialEducativo" (
    material_id uuid NOT NULL,
    titulo character varying(100) NOT NULL,
    descripcion text,
    tipo_material public.tipo_material_educativo NOT NULL,
    url_archivo character varying(255) NOT NULL,
    formato_archivo character varying(10) NOT NULL
);


ALTER TABLE public."MaterialEducativo" OWNER TO postgres;

--
-- Name: Mensaje; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Mensaje" (
    mensaje_id uuid NOT NULL,
    chat_grupo_id uuid,
    emisor_id uuid,
    fecha_hora timestamp with time zone DEFAULT now() NOT NULL,
    tipo public.tipo_mensaje NOT NULL,
    contenido text NOT NULL
);


ALTER TABLE public."Mensaje" OWNER TO postgres;

--
-- Name: MensajeBot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."MensajeBot" (
    mensaje_bot_id uuid NOT NULL,
    usuario_id uuid,
    chat_grupo_id uuid,
    referencia_material_id uuid,
    contenido text NOT NULL,
    respuesta text NOT NULL,
    contexto public.contexto_mensaje NOT NULL,
    fecha_hora timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public."MensajeBot" OWNER TO postgres;

--
-- Name: Plataforma; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Plataforma" (
    plataforma_id uuid NOT NULL,
    nombre character varying(50) NOT NULL,
    url_base text NOT NULL,
    tipo_integracion public.tipo_integracion_plataforma NOT NULL,
    requiere_cuenta boolean NOT NULL,
    es_gratuita boolean
);


ALTER TABLE public."Plataforma" OWNER TO postgres;

--
-- Name: Programa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Programa" (
    programa_id uuid NOT NULL,
    institucion_id uuid,
    nombre character varying(100) NOT NULL,
    descripcion text,
    nivel public.nivel_programa NOT NULL,
    tipo public.tipo_programa NOT NULL
);


ALTER TABLE public."Programa" OWNER TO postgres;

--
-- Name: Recompensa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Recompensa" (
    recompensa_id uuid NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    costo_puntos integer NOT NULL,
    CONSTRAINT "Recompensa_costo_puntos_check" CHECK ((costo_puntos >= 0))
);


ALTER TABLE public."Recompensa" OWNER TO postgres;

--
-- Name: Tarea; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Tarea" (
    tarea_id uuid NOT NULL,
    docente_id uuid,
    clase_id uuid,
    titulo character varying(50) NOT NULL,
    descripcion text,
    fecha_asignacion timestamp with time zone DEFAULT now() NOT NULL,
    fecha_limite timestamp with time zone,
    archivo_adjunto text,
    permite_entregas_tardias boolean NOT NULL
);


ALTER TABLE public."Tarea" OWNER TO postgres;

--
-- Name: Tema; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Tema" (
    tema_id uuid NOT NULL,
    nombre character varying(100) NOT NULL,
    emoji character varying(8) NOT NULL,
    es_personalizado boolean NOT NULL
);


ALTER TABLE public."Tema" OWNER TO postgres;

--
-- Name: Usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Usuario" (
    usuario_id uuid NOT NULL,
    correo_institucional character varying(100),
    username character varying(50),
    nombres character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    tipo_documento public.tipo_documento_usuario NOT NULL,
    numero_documento character varying(20) NOT NULL,
    rol public.rol_usuario NOT NULL,
    password_hash character varying(255) NOT NULL,
    estado_cuenta public.estado_cuenta_usuario DEFAULT 'activo'::public.estado_cuenta_usuario NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now() NOT NULL,
    ultimo_acceso timestamp with time zone NOT NULL,
    perfil_url text,
    portada_url text,
    telefono character varying(20),
    descripcion text,
    CONSTRAINT chk_login CHECK ((((rol = 'administrador'::public.rol_usuario) AND (username IS NOT NULL) AND (correo_institucional IS NULL)) OR ((rol <> 'administrador'::public.rol_usuario) AND (correo_institucional IS NOT NULL) AND (username IS NULL))))
);


ALTER TABLE public."Usuario" OWNER TO postgres;

--
-- Name: UsuarioInsignia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."UsuarioInsignia" (
    usuario_insignia_id uuid NOT NULL,
    usuario_id uuid,
    insignia_id uuid,
    otorgada_por uuid,
    fecha_otorgada timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public."UsuarioInsignia" OWNER TO postgres;

--
-- Name: UsuarioPuntos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."UsuarioPuntos" (
    usuario_id uuid NOT NULL,
    puntos_acumulados integer DEFAULT 0 NOT NULL
);


ALTER TABLE public."UsuarioPuntos" OWNER TO postgres;

--
-- Name: UsuarioRecompensa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."UsuarioRecompensa" (
    usuario_id uuid NOT NULL,
    recompensa_id uuid NOT NULL,
    fecha_canje timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public."UsuarioRecompensa" OWNER TO postgres;

--
-- Name: UsuarioTema; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."UsuarioTema" (
    usuario_id uuid NOT NULL,
    tema_id uuid NOT NULL
);


ALTER TABLE public."UsuarioTema" OWNER TO postgres;

--
-- Name: ValorCalificacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."ValorCalificacion" (
    valor_id uuid NOT NULL,
    escala_id uuid,
    valor character varying(10) NOT NULL,
    descripcion character varying(100),
    orden smallint
);


ALTER TABLE public."ValorCalificacion" OWNER TO postgres;

--
-- Data for Name: AdministradorSistema; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."AdministradorSistema" (administrador_id) FROM stdin;
21dd8d08-0b4d-4656-b1f5-462350e4dcec
\.


--
-- Data for Name: ArchivoChat; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."ArchivoChat" (archivo_id, chat_grupo_id, usuario_id, nombre_archivo, url_archivo, fecha_envio, tipo_archivo) FROM stdin;
\.


--
-- Data for Name: Asistencia; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Asistencia" (asistencia_id, clase_id, estudiante_id, estado) FROM stdin;
\.


--
-- Data for Name: ChatBot; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."ChatBot" (chat_bot_id, nombre, descripcion, foto_perfil_url, activo, fecha_registro) FROM stdin;
\.


--
-- Data for Name: ChatGrupo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."ChatGrupo" (chat_grupo_id, grupo_id, fecha_creacion, descripcion, foto_perfil, permite_archivos, capacidad_almacenamiento, estado_chat) FROM stdin;
\.


--
-- Data for Name: Clase; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Clase" (clase_id, grupo_curso_id, plataforma_id, titulo, descripcion, hora_inicio, duracion, link_videollamada) FROM stdin;
637b5dc5-0f62-42bb-a454-c2fb55cc6f53	b147bfaa-293a-4368-8199-da4149ba3bf3	ff3709b1-dc83-4ae2-88b2-b30f72ccc637	Clase 1: Introducción a las Bases de Datos	Conceptos básicos de sistemas de gestión de bases de datos.	2025-08-30 19:30:40.169805-05	01:30:30	https://meet.google.com/sam-xbnz-svz
\.


--
-- Data for Name: Coordinador; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Coordinador" (coordinador_id, institucion_id, horario_atencion, fecha_inicio_carrera) FROM stdin;
4812f594-e714-47b9-bcf8-f9079661ae78	765680fa-1b6b-4f16-ab1d-9f106cc4da8b	7:00 AM - 1:30 PM	2009-04-16
9b1244f4-eb41-4599-975e-f491d681d090	cf003e1c-6ebd-4952-a3d9-8602269d35da	8:20 AM - 02:00 PM	2010-06-11
\.


--
-- Data for Name: Curso; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Curso" (curso_id, institucion_id, coordinador_id, programa_id, nombre, descripcion, modalidad, fecha_inicio, fecha_fin) FROM stdin;
99382aca-967f-4fe8-9b2b-a2d61baf0121	765680fa-1b6b-4f16-ab1d-9f106cc4da8b	4812f594-e714-47b9-bcf8-f9079661ae78	f9612058-ccf5-4694-9a2f-f99b60aaea41	Lógica de Programación I	Curso enfocado en la contextualización dealgoritmos y lógca informática.	semestral	2010-06-16	\N
\.


--
-- Data for Name: CursoDocente; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."CursoDocente" (curso_id, docente_id, fecha_asignacion) FROM stdin;
99382aca-967f-4fe8-9b2b-a2d61baf0121	8be3abbb-fadc-4433-a85a-8e2c32cad666	2018-02-15
\.


--
-- Data for Name: Docente; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Docente" (docente_id, area_conocimiento, fecha_vinculacion, tipo_vinculacion, titulo_academico, horas_semanales) FROM stdin;
8be3abbb-fadc-4433-a85a-8e2c32cad666	Ingeniería de Software	2020-02-15	planta	Ingeniero de Sistemas	48
\.


--
-- Data for Name: EntregarTarea; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."EntregarTarea" (entrega_id, tarea_id, estudiante_id, archivo, fecha_envio, calificacion, fecha_revision) FROM stdin;
\.


--
-- Data for Name: EscalaCalificacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."EscalaCalificacion" (escala_id, institucion_id, nombre, tipo, min_valor, max_valor) FROM stdin;
\.


--
-- Data for Name: Estudiante; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Estudiante" (estudiante_id, programa_id, fecha_ingreso, creditos_aprobados, etapa_formativa, promedio_acumulado) FROM stdin;
7fa83309-71b3-4558-91a0-7999bdfc74bc	f9612058-ccf5-4694-9a2f-f99b60aaea41	2023-02-15	\N	i	\N
\.


--
-- Data for Name: EstudianteGrupo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."EstudianteGrupo" (estudiante_grupo_id, grupo_id, estudiante_id, fecha_vinculacion) FROM stdin;
\.


--
-- Data for Name: FAQBot; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."FAQBot" (faq_id, pregunta, respuesta, categoria, ultima_actualizacion) FROM stdin;
\.


--
-- Data for Name: Grupo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Grupo" (grupo_id, programa_id, docente_tutor_id, nombre, jornada) FROM stdin;
4e4ccb3c-c715-456a-a077-3df682afa0c2	f9612058-ccf5-4694-9a2f-f99b60aaea41	8be3abbb-fadc-4433-a85a-8e2c32cad666	105	mañana
\.


--
-- Data for Name: GrupoCurso; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."GrupoCurso" (grupo_curso_id, grupo_id, curso_id, docente_id, fecha_asignacion) FROM stdin;
b147bfaa-293a-4368-8199-da4149ba3bf3	4e4ccb3c-c715-456a-a077-3df682afa0c2	99382aca-967f-4fe8-9b2b-a2d61baf0121	8be3abbb-fadc-4433-a85a-8e2c32cad666	2019-02-15
\.


--
-- Data for Name: Insignia; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Insignia" (insignia_id, nombre, descripcion, imagen_url, tipo, es_unica) FROM stdin;
\.


--
-- Data for Name: Institucion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Institucion" (institucion_id, administrador_id, nombre, sigla, lema, tipo_institucion, usa_programas, nivel_educativo, sector, direccion, ciudad, pais, correo_institucional, telefono, nit) FROM stdin;
765680fa-1b6b-4f16-ab1d-9f106cc4da8b	21dd8d08-0b4d-4656-b1f5-462350e4dcec	Colegio Técnico Aldemar Rojas Plazas CED	ARP	Por una Colombia Productiva y en Paz	colegio	t	tecnica	publico	Cra. 10 #13 Sur-52	Bogotá	Colombia	@arp.edu.co	12788854	\N
cf003e1c-6ebd-4952-a3d9-8602269d35da	21dd8d08-0b4d-4656-b1f5-462350e4dcec	Servicio Nacional de Aprendizaje SENA - Centro de Gestión de Mercados, Logística y Tenologías de la Información - Regional Distrito Capital	SENA - CGMLTI	Una entidad de clase mundial	centro_de_formacion	t	tecnologica	publico	Cl 52 #13-65	Bogotá	Colombia	@soy.sena.edu.co	3112545028	899999034-1
\.


--
-- Data for Name: InstitucionCoordinador; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."InstitucionCoordinador" (institucion_coordinador_id, institucion_id, coordinador_id, fecha_asignacion, estado) FROM stdin;
97638fde-92ff-4841-96c0-8ff6bdee7874	cf003e1c-6ebd-4952-a3d9-8602269d35da	9b1244f4-eb41-4599-975e-f491d681d090	2021-08-07	activo
\.


--
-- Data for Name: MaterialClase; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."MaterialClase" (material_clase_id, clase_id) FROM stdin;
\.


--
-- Data for Name: MaterialCurso; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."MaterialCurso" (material_curso_id, curso_id) FROM stdin;
\.


--
-- Data for Name: MaterialEducativo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."MaterialEducativo" (material_id, titulo, descripcion, tipo_material, url_archivo, formato_archivo) FROM stdin;
\.


--
-- Data for Name: Mensaje; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Mensaje" (mensaje_id, chat_grupo_id, emisor_id, fecha_hora, tipo, contenido) FROM stdin;
\.


--
-- Data for Name: MensajeBot; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."MensajeBot" (mensaje_bot_id, usuario_id, chat_grupo_id, referencia_material_id, contenido, respuesta, contexto, fecha_hora) FROM stdin;
\.


--
-- Data for Name: Plataforma; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Plataforma" (plataforma_id, nombre, url_base, tipo_integracion, requiere_cuenta, es_gratuita) FROM stdin;
ff3709b1-dc83-4ae2-88b2-b30f72ccc637	Google Classroom	https://classroom.google.com	api	t	t
\.


--
-- Data for Name: Programa; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Programa" (programa_id, institucion_id, nombre, descripcion, nivel, tipo) FROM stdin;
f9612058-ccf5-4694-9a2f-f99b60aaea41	765680fa-1b6b-4f16-ab1d-9f106cc4da8b	Diseño y Desarrollo de Software	La Técnica en Diseño y Desarrollo de software, es una especialidad que brinda los conocimientos necesarios para diseñar y desarrollar Sistemas de Información, manejándolos por Páginas Web, desarrollando aplicaciones específicas a través de los lenguajes de programación y los motores de bases de datos.	tecnico	presencial
\.


--
-- Data for Name: Recompensa; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Recompensa" (recompensa_id, nombre, descripcion, costo_puntos) FROM stdin;
\.


--
-- Data for Name: Tarea; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Tarea" (tarea_id, docente_id, clase_id, titulo, descripcion, fecha_asignacion, fecha_limite, archivo_adjunto, permite_entregas_tardias) FROM stdin;
\.


--
-- Data for Name: Tema; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Tema" (tema_id, nombre, emoji, es_personalizado) FROM stdin;
\.


--
-- Data for Name: Usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Usuario" (usuario_id, correo_institucional, username, nombres, apellidos, tipo_documento, numero_documento, rol, password_hash, estado_cuenta, fecha_creacion, ultimo_acceso, perfil_url, portada_url, telefono, descripcion) FROM stdin;
21dd8d08-0b4d-4656-b1f5-462350e4dcec	\N	HarryDev_2006	Harrison David	Guerrero Palacios	cc	1034284499	administrador	$2a$06$cRj6bWCoZRHGdxBeRMDDKuyTnCQwjcGzEL5WBm0FuJ/W/Kq4SnX2G	activo	2025-08-30 13:49:17.589119-05	2025-08-30 13:49:17.589119-05	data:image/jpeg;base64,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	\N	3045955299	Hola, soy Admin
8be3abbb-fadc-4433-a85a-8e2c32cad666	jlopez@arp.edu.co	\N	Jose	López	cc	123456789	docente	$2a$06$FCmUwgL3x.E.shmIJIZt..Dr4rvwsdSQXLalvqqrqwOq5whe1Qfee	activo	2025-08-30 16:15:22.601017-05	2025-08-30 16:15:22.601017-05	\N	\N	3001234567	\N
7fa83309-71b3-4558-91a0-7999bdfc74bc	mgarcia@arp.edu.co	\N	María	García	ti	987654321	estudiante	$2a$06$dhtFB045gMLn9OV.piNfw.5Nk4HJ3jOO68at5Lx2o34Gz40ifWj4a	activo	2025-08-30 16:15:41.765389-05	2025-08-30 16:15:41.765389-05	\N	\N	3019876543	\N
9b1244f4-eb41-4599-975e-f491d681d090	jesus_valencia@uni.edu.co	\N	Jesus	Valnecia	cc	1029384756	coordinador	$2a$06$1HOCY2KMf902RSJomBC9mOQBbnbJmbh55MTtmWzhUP0tjBxzbRjs6	activo	2025-08-30 17:24:01.504938-05	2025-08-30 17:24:01.504938-05	\N	\N	3011234567	Coordinador académico de la facultad de ingeniería
4812f594-e714-47b9-bcf8-f9079661ae78	carlos_guerrero@arp.edu.co	\N	Carlos Alberto	Guerrero	cc	79526879	coordinador	$2a$06$ebITUsg0BpDQ72vyCNkuHuX5SPlyIXJHlc87QKkT2oh7RuNaYufGK	activo	2025-08-30 14:04:57.262313-05	2025-08-30 14:04:57.262313-05	\N	\N	3194874153	Hola, soy Coordinador
\.


--
-- Data for Name: UsuarioInsignia; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."UsuarioInsignia" (usuario_insignia_id, usuario_id, insignia_id, otorgada_por, fecha_otorgada) FROM stdin;
\.


--
-- Data for Name: UsuarioPuntos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."UsuarioPuntos" (usuario_id, puntos_acumulados) FROM stdin;
\.


--
-- Data for Name: UsuarioRecompensa; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."UsuarioRecompensa" (usuario_id, recompensa_id, fecha_canje) FROM stdin;
\.


--
-- Data for Name: UsuarioTema; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."UsuarioTema" (usuario_id, tema_id) FROM stdin;
\.


--
-- Data for Name: ValorCalificacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."ValorCalificacion" (valor_id, escala_id, valor, descripcion, orden) FROM stdin;
\.


--
-- Name: ChatBot ChatBot_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ChatBot"
    ADD CONSTRAINT "ChatBot_nombre_key" UNIQUE (nombre);


--
-- Name: Insignia Insignia_imagen_url_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Insignia"
    ADD CONSTRAINT "Insignia_imagen_url_key" UNIQUE (imagen_url);


--
-- Name: Insignia Insignia_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Insignia"
    ADD CONSTRAINT "Insignia_nombre_key" UNIQUE (nombre);


--
-- Name: Institucion Institucion_correo_institucional_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Institucion"
    ADD CONSTRAINT "Institucion_correo_institucional_key" UNIQUE (correo_institucional);


--
-- Name: Institucion Institucion_nit_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Institucion"
    ADD CONSTRAINT "Institucion_nit_key" UNIQUE (nit);


--
-- Name: Institucion Institucion_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Institucion"
    ADD CONSTRAINT "Institucion_nombre_key" UNIQUE (nombre);


--
-- Name: Institucion Institucion_sigla_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Institucion"
    ADD CONSTRAINT "Institucion_sigla_key" UNIQUE (sigla);


--
-- Name: Institucion Institucion_telefono_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Institucion"
    ADD CONSTRAINT "Institucion_telefono_key" UNIQUE (telefono);


--
-- Name: MaterialCurso MaterialCurso_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."MaterialCurso"
    ADD CONSTRAINT "MaterialCurso_pkey" PRIMARY KEY (material_curso_id, curso_id);


--
-- Name: Plataforma Plataforma_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Plataforma"
    ADD CONSTRAINT "Plataforma_nombre_key" UNIQUE (nombre);


--
-- Name: Tema Tema_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Tema"
    ADD CONSTRAINT "Tema_nombre_key" UNIQUE (nombre);


--
-- Name: Usuario Usuario_correo_institucional_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Usuario"
    ADD CONSTRAINT "Usuario_correo_institucional_key" UNIQUE (correo_institucional);


--
-- Name: Usuario Usuario_telefono_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Usuario"
    ADD CONSTRAINT "Usuario_telefono_key" UNIQUE (telefono);


--
-- Name: Usuario Usuario_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Usuario"
    ADD CONSTRAINT "Usuario_username_key" UNIQUE (username);


--
-- Name: AdministradorSistema pk_administrador_sistema; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."AdministradorSistema"
    ADD CONSTRAINT pk_administrador_sistema PRIMARY KEY (administrador_id);


--
-- Name: ArchivoChat pk_archivo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ArchivoChat"
    ADD CONSTRAINT pk_archivo PRIMARY KEY (archivo_id);


--
-- Name: Asistencia pk_asistencia; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Asistencia"
    ADD CONSTRAINT pk_asistencia PRIMARY KEY (asistencia_id);


--
-- Name: ChatBot pk_chat_bot; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ChatBot"
    ADD CONSTRAINT pk_chat_bot PRIMARY KEY (chat_bot_id);


--
-- Name: ChatGrupo pk_chat_grupo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ChatGrupo"
    ADD CONSTRAINT pk_chat_grupo PRIMARY KEY (chat_grupo_id);


--
-- Name: Clase pk_clase; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Clase"
    ADD CONSTRAINT pk_clase PRIMARY KEY (clase_id);


--
-- Name: Coordinador pk_coordinador; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Coordinador"
    ADD CONSTRAINT pk_coordinador PRIMARY KEY (coordinador_id);


--
-- Name: Curso pk_curso; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Curso"
    ADD CONSTRAINT pk_curso PRIMARY KEY (curso_id);


--
-- Name: CursoDocente pk_curso_docente; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CursoDocente"
    ADD CONSTRAINT pk_curso_docente PRIMARY KEY (curso_id, docente_id);


--
-- Name: Docente pk_docente; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Docente"
    ADD CONSTRAINT pk_docente PRIMARY KEY (docente_id);


--
-- Name: EntregarTarea pk_entrega; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."EntregarTarea"
    ADD CONSTRAINT pk_entrega PRIMARY KEY (entrega_id);


--
-- Name: EscalaCalificacion pk_escala; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."EscalaCalificacion"
    ADD CONSTRAINT pk_escala PRIMARY KEY (escala_id);


--
-- Name: Estudiante pk_estudiante; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Estudiante"
    ADD CONSTRAINT pk_estudiante PRIMARY KEY (estudiante_id);


--
-- Name: EstudianteGrupo pk_estudiante_grupo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."EstudianteGrupo"
    ADD CONSTRAINT pk_estudiante_grupo PRIMARY KEY (estudiante_grupo_id);


--
-- Name: FAQBot pk_faq_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."FAQBot"
    ADD CONSTRAINT pk_faq_id PRIMARY KEY (faq_id);


--
-- Name: Grupo pk_grupo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Grupo"
    ADD CONSTRAINT pk_grupo PRIMARY KEY (grupo_id);


--
-- Name: GrupoCurso pk_grupo_curso; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."GrupoCurso"
    ADD CONSTRAINT pk_grupo_curso PRIMARY KEY (grupo_curso_id);


--
-- Name: Insignia pk_insignia; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Insignia"
    ADD CONSTRAINT pk_insignia PRIMARY KEY (insignia_id);


--
-- Name: Institucion pk_institucion; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Institucion"
    ADD CONSTRAINT pk_institucion PRIMARY KEY (institucion_id);


--
-- Name: MaterialClase pk_material_clase; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."MaterialClase"
    ADD CONSTRAINT pk_material_clase PRIMARY KEY (material_clase_id);


--
-- Name: MaterialEducativo pk_material_educativo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."MaterialEducativo"
    ADD CONSTRAINT pk_material_educativo PRIMARY KEY (material_id);


--
-- Name: Mensaje pk_mensaje; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Mensaje"
    ADD CONSTRAINT pk_mensaje PRIMARY KEY (mensaje_id);


--
-- Name: MensajeBot pk_mensaje_bot; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."MensajeBot"
    ADD CONSTRAINT pk_mensaje_bot PRIMARY KEY (mensaje_bot_id);


--
-- Name: Plataforma pk_plataforma; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Plataforma"
    ADD CONSTRAINT pk_plataforma PRIMARY KEY (plataforma_id);


--
-- Name: Programa pk_programa; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Programa"
    ADD CONSTRAINT pk_programa PRIMARY KEY (programa_id);


--
-- Name: Recompensa pk_recompensa; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Recompensa"
    ADD CONSTRAINT pk_recompensa PRIMARY KEY (recompensa_id);


--
-- Name: Tarea pk_tarea; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Tarea"
    ADD CONSTRAINT pk_tarea PRIMARY KEY (tarea_id);


--
-- Name: Tema pk_tema; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Tema"
    ADD CONSTRAINT pk_tema PRIMARY KEY (tema_id);


--
-- Name: Usuario pk_usuario; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Usuario"
    ADD CONSTRAINT pk_usuario PRIMARY KEY (usuario_id);


--
-- Name: UsuarioInsignia pk_usuario_insignia; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioInsignia"
    ADD CONSTRAINT pk_usuario_insignia PRIMARY KEY (usuario_insignia_id);


--
-- Name: UsuarioPuntos pk_usuario_puntos; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioPuntos"
    ADD CONSTRAINT pk_usuario_puntos PRIMARY KEY (usuario_id);


--
-- Name: UsuarioRecompensa pk_usuario_recompensa; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioRecompensa"
    ADD CONSTRAINT pk_usuario_recompensa PRIMARY KEY (usuario_id, recompensa_id);


--
-- Name: UsuarioTema pk_usuario_tema; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioTema"
    ADD CONSTRAINT pk_usuario_tema PRIMARY KEY (usuario_id, tema_id);


--
-- Name: ValorCalificacion pk_valor; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ValorCalificacion"
    ADD CONSTRAINT pk_valor PRIMARY KEY (valor_id);


--
-- Name: ChatGrupo uq_chat_grupo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ChatGrupo"
    ADD CONSTRAINT uq_chat_grupo UNIQUE (grupo_id);


--
-- Name: Curso uq_curso_nombre; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Curso"
    ADD CONSTRAINT uq_curso_nombre UNIQUE (institucion_id, nombre);


--
-- Name: EntregarTarea uq_entrega; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."EntregarTarea"
    ADD CONSTRAINT uq_entrega UNIQUE (tarea_id, estudiante_id);


--
-- Name: GrupoCurso uq_grupo_curso; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."GrupoCurso"
    ADD CONSTRAINT uq_grupo_curso UNIQUE (curso_id, grupo_id);


--
-- Name: Grupo uq_grupo_tutor; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Grupo"
    ADD CONSTRAINT uq_grupo_tutor UNIQUE (grupo_id, docente_tutor_id);


--
-- Name: Programa uq_programa_nombre; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Programa"
    ADD CONSTRAINT uq_programa_nombre UNIQUE (institucion_id, nombre);


--
-- Name: AdministradorSistema AdministradorSistema_administrador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."AdministradorSistema"
    ADD CONSTRAINT "AdministradorSistema_administrador_id_fkey" FOREIGN KEY (administrador_id) REFERENCES public."Usuario"(usuario_id) ON DELETE CASCADE;


--
-- Name: ArchivoChat ArchivoChat_chat_grupo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ArchivoChat"
    ADD CONSTRAINT "ArchivoChat_chat_grupo_id_fkey" FOREIGN KEY (chat_grupo_id) REFERENCES public."ChatGrupo"(chat_grupo_id) ON DELETE CASCADE;


--
-- Name: ArchivoChat ArchivoChat_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ArchivoChat"
    ADD CONSTRAINT "ArchivoChat_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES public."Usuario"(usuario_id) ON DELETE SET NULL;


--
-- Name: Asistencia Asistencia_clase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Asistencia"
    ADD CONSTRAINT "Asistencia_clase_id_fkey" FOREIGN KEY (clase_id) REFERENCES public."Clase"(clase_id) ON DELETE CASCADE;


--
-- Name: ChatGrupo ChatGrupo_grupo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ChatGrupo"
    ADD CONSTRAINT "ChatGrupo_grupo_id_fkey" FOREIGN KEY (grupo_id) REFERENCES public."Grupo"(grupo_id) ON DELETE CASCADE;


--
-- Name: Clase Clase_grupo_curso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Clase"
    ADD CONSTRAINT "Clase_grupo_curso_id_fkey" FOREIGN KEY (grupo_curso_id) REFERENCES public."GrupoCurso"(grupo_curso_id) ON DELETE CASCADE;


--
-- Name: Coordinador Coordinador_coordinador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Coordinador"
    ADD CONSTRAINT "Coordinador_coordinador_id_fkey" FOREIGN KEY (coordinador_id) REFERENCES public."Usuario"(usuario_id);


--
-- Name: Coordinador Coordinador_institucion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Coordinador"
    ADD CONSTRAINT "Coordinador_institucion_id_fkey" FOREIGN KEY (institucion_id) REFERENCES public."Institucion"(institucion_id) ON DELETE CASCADE;


--
-- Name: CursoDocente CursoDocente_curso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CursoDocente"
    ADD CONSTRAINT "CursoDocente_curso_id_fkey" FOREIGN KEY (curso_id) REFERENCES public."Curso"(curso_id) ON DELETE CASCADE;


--
-- Name: CursoDocente CursoDocente_docente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CursoDocente"
    ADD CONSTRAINT "CursoDocente_docente_id_fkey" FOREIGN KEY (docente_id) REFERENCES public."Docente"(docente_id) ON DELETE CASCADE;


--
-- Name: Curso Curso_coordinador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Curso"
    ADD CONSTRAINT "Curso_coordinador_id_fkey" FOREIGN KEY (coordinador_id) REFERENCES public."Coordinador"(coordinador_id) ON DELETE SET NULL;


--
-- Name: Curso Curso_institucion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Curso"
    ADD CONSTRAINT "Curso_institucion_id_fkey" FOREIGN KEY (institucion_id) REFERENCES public."Institucion"(institucion_id) ON DELETE CASCADE;


--
-- Name: Curso Curso_programa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Curso"
    ADD CONSTRAINT "Curso_programa_id_fkey" FOREIGN KEY (programa_id) REFERENCES public."Programa"(programa_id) ON DELETE CASCADE;


--
-- Name: Docente Docente_docente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Docente"
    ADD CONSTRAINT "Docente_docente_id_fkey" FOREIGN KEY (docente_id) REFERENCES public."Usuario"(usuario_id);


--
-- Name: EntregarTarea EntregarTarea_tarea_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."EntregarTarea"
    ADD CONSTRAINT "EntregarTarea_tarea_id_fkey" FOREIGN KEY (tarea_id) REFERENCES public."Tarea"(tarea_id) ON DELETE CASCADE;


--
-- Name: EscalaCalificacion EscalaCalificacion_institucion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."EscalaCalificacion"
    ADD CONSTRAINT "EscalaCalificacion_institucion_id_fkey" FOREIGN KEY (institucion_id) REFERENCES public."Institucion"(institucion_id) ON DELETE CASCADE;


--
-- Name: EstudianteGrupo EstudianteGrupo_grupo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."EstudianteGrupo"
    ADD CONSTRAINT "EstudianteGrupo_grupo_id_fkey" FOREIGN KEY (grupo_id) REFERENCES public."Grupo"(grupo_id) ON DELETE CASCADE;


--
-- Name: Estudiante Estudiante_estudiante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Estudiante"
    ADD CONSTRAINT "Estudiante_estudiante_id_fkey" FOREIGN KEY (estudiante_id) REFERENCES public."Usuario"(usuario_id);


--
-- Name: Estudiante Estudiante_programa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Estudiante"
    ADD CONSTRAINT "Estudiante_programa_id_fkey" FOREIGN KEY (programa_id) REFERENCES public."Programa"(programa_id);


--
-- Name: GrupoCurso GrupoCurso_curso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."GrupoCurso"
    ADD CONSTRAINT "GrupoCurso_curso_id_fkey" FOREIGN KEY (curso_id) REFERENCES public."Curso"(curso_id) ON DELETE CASCADE;


--
-- Name: GrupoCurso GrupoCurso_docente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."GrupoCurso"
    ADD CONSTRAINT "GrupoCurso_docente_id_fkey" FOREIGN KEY (docente_id) REFERENCES public."Docente"(docente_id) ON DELETE CASCADE;


--
-- Name: GrupoCurso GrupoCurso_grupo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."GrupoCurso"
    ADD CONSTRAINT "GrupoCurso_grupo_id_fkey" FOREIGN KEY (grupo_id) REFERENCES public."Grupo"(grupo_id) ON DELETE CASCADE;


--
-- Name: Grupo Grupo_docente_tutor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Grupo"
    ADD CONSTRAINT "Grupo_docente_tutor_id_fkey" FOREIGN KEY (docente_tutor_id) REFERENCES public."Docente"(docente_id);


--
-- Name: Grupo Grupo_programa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Grupo"
    ADD CONSTRAINT "Grupo_programa_id_fkey" FOREIGN KEY (programa_id) REFERENCES public."Programa"(programa_id) ON DELETE CASCADE;


--
-- Name: InstitucionCoordinador InstitucionCoordinador_coordinador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."InstitucionCoordinador"
    ADD CONSTRAINT "InstitucionCoordinador_coordinador_id_fkey" FOREIGN KEY (coordinador_id) REFERENCES public."Coordinador"(coordinador_id);


--
-- Name: InstitucionCoordinador InstitucionCoordinador_institucion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."InstitucionCoordinador"
    ADD CONSTRAINT "InstitucionCoordinador_institucion_id_fkey" FOREIGN KEY (institucion_id) REFERENCES public."Institucion"(institucion_id);


--
-- Name: Institucion Institucion_administrador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Institucion"
    ADD CONSTRAINT "Institucion_administrador_id_fkey" FOREIGN KEY (administrador_id) REFERENCES public."AdministradorSistema"(administrador_id) ON DELETE SET NULL;


--
-- Name: MaterialClase MaterialClase_clase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."MaterialClase"
    ADD CONSTRAINT "MaterialClase_clase_id_fkey" FOREIGN KEY (clase_id) REFERENCES public."Clase"(clase_id) ON DELETE SET NULL;


--
-- Name: MaterialClase MaterialClase_material_clase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."MaterialClase"
    ADD CONSTRAINT "MaterialClase_material_clase_id_fkey" FOREIGN KEY (material_clase_id) REFERENCES public."MaterialEducativo"(material_id) ON DELETE CASCADE;


--
-- Name: MaterialCurso MaterialCurso_curso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."MaterialCurso"
    ADD CONSTRAINT "MaterialCurso_curso_id_fkey" FOREIGN KEY (curso_id) REFERENCES public."Curso"(curso_id) ON DELETE SET NULL;


--
-- Name: MaterialCurso MaterialCurso_material_curso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."MaterialCurso"
    ADD CONSTRAINT "MaterialCurso_material_curso_id_fkey" FOREIGN KEY (material_curso_id) REFERENCES public."MaterialEducativo"(material_id) ON DELETE CASCADE;


--
-- Name: MensajeBot MensajeBot_chat_grupo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."MensajeBot"
    ADD CONSTRAINT "MensajeBot_chat_grupo_id_fkey" FOREIGN KEY (chat_grupo_id) REFERENCES public."ChatGrupo"(chat_grupo_id);


--
-- Name: MensajeBot MensajeBot_referencia_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."MensajeBot"
    ADD CONSTRAINT "MensajeBot_referencia_material_id_fkey" FOREIGN KEY (referencia_material_id) REFERENCES public."MaterialEducativo"(material_id);


--
-- Name: MensajeBot MensajeBot_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."MensajeBot"
    ADD CONSTRAINT "MensajeBot_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES public."Usuario"(usuario_id);


--
-- Name: Mensaje Mensaje_chat_grupo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Mensaje"
    ADD CONSTRAINT "Mensaje_chat_grupo_id_fkey" FOREIGN KEY (chat_grupo_id) REFERENCES public."ChatGrupo"(chat_grupo_id) ON DELETE CASCADE;


--
-- Name: Mensaje Mensaje_emisor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Mensaje"
    ADD CONSTRAINT "Mensaje_emisor_id_fkey" FOREIGN KEY (emisor_id) REFERENCES public."Usuario"(usuario_id) ON DELETE SET NULL;


--
-- Name: Programa Programa_institucion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Programa"
    ADD CONSTRAINT "Programa_institucion_id_fkey" FOREIGN KEY (institucion_id) REFERENCES public."Institucion"(institucion_id) ON DELETE CASCADE;


--
-- Name: Tarea Tarea_clase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Tarea"
    ADD CONSTRAINT "Tarea_clase_id_fkey" FOREIGN KEY (clase_id) REFERENCES public."Clase"(clase_id) ON DELETE CASCADE;


--
-- Name: Tarea Tarea_docente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Tarea"
    ADD CONSTRAINT "Tarea_docente_id_fkey" FOREIGN KEY (docente_id) REFERENCES public."Docente"(docente_id) ON DELETE SET NULL;


--
-- Name: UsuarioInsignia UsuarioInsignia_insignia_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioInsignia"
    ADD CONSTRAINT "UsuarioInsignia_insignia_id_fkey" FOREIGN KEY (insignia_id) REFERENCES public."Insignia"(insignia_id) ON DELETE CASCADE;


--
-- Name: UsuarioInsignia UsuarioInsignia_otorgada_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioInsignia"
    ADD CONSTRAINT "UsuarioInsignia_otorgada_por_fkey" FOREIGN KEY (otorgada_por) REFERENCES public."Usuario"(usuario_id) ON DELETE SET NULL;


--
-- Name: UsuarioInsignia UsuarioInsignia_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioInsignia"
    ADD CONSTRAINT "UsuarioInsignia_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES public."Usuario"(usuario_id) ON DELETE CASCADE;


--
-- Name: UsuarioPuntos UsuarioPuntos_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioPuntos"
    ADD CONSTRAINT "UsuarioPuntos_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES public."Usuario"(usuario_id) ON DELETE CASCADE;


--
-- Name: UsuarioRecompensa UsuarioRecompensa_recompensa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioRecompensa"
    ADD CONSTRAINT "UsuarioRecompensa_recompensa_id_fkey" FOREIGN KEY (recompensa_id) REFERENCES public."Recompensa"(recompensa_id) ON DELETE CASCADE;


--
-- Name: UsuarioRecompensa UsuarioRecompensa_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioRecompensa"
    ADD CONSTRAINT "UsuarioRecompensa_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES public."Usuario"(usuario_id) ON DELETE CASCADE;


--
-- Name: UsuarioTema UsuarioTema_tema_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioTema"
    ADD CONSTRAINT "UsuarioTema_tema_id_fkey" FOREIGN KEY (tema_id) REFERENCES public."Tema"(tema_id) ON DELETE CASCADE;


--
-- Name: UsuarioTema UsuarioTema_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."UsuarioTema"
    ADD CONSTRAINT "UsuarioTema_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES public."Usuario"(usuario_id) ON DELETE CASCADE;


--
-- Name: ValorCalificacion ValorCalificacion_escala_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ValorCalificacion"
    ADD CONSTRAINT "ValorCalificacion_escala_id_fkey" FOREIGN KEY (escala_id) REFERENCES public."EscalaCalificacion"(escala_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict fgrE8ATlgdBfIeltkZvTfJNEXj9bZoyNrky7fVziech0IQCKz7n7a1ocRm9JnDr

