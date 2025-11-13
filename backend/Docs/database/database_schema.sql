-- =====================================================
-- ESQUEMA COMPLETO DE BASE DE DATOS - ACADIFY
-- =====================================================
-- Generado automáticamente
-- Fecha: 2025-10-29
-- Total de tablas: 53
-- =====================================================

-- NOTA: Este archivo contiene el esquema completo.
-- Para DDL individual, ver carpeta tables/

============================================================

-- =====================================================
-- Tabla: AdministradorSistema
-- =====================================================

CREATE TABLE IF NOT EXISTS AdministradorSistema (
    administrador_id uuid NOT NULL
,
    PRIMARY KEY (administrador_id)
);

-- Foreign Keys de AdministradorSistema
ALTER TABLE AdministradorSistema ADD CONSTRAINT AdministradorSistema_administrador_id_fkey FOREIGN KEY (administrador_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de AdministradorSistema
ALTER TABLE AdministradorSistema ADD CONSTRAINT 39558_39730_1_not_null CHECK (administrador_id IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: ArchivoChat
-- =====================================================

CREATE TABLE IF NOT EXISTS ArchivoChat (
    archivo_id uuid NOT NULL DEFAULT gen_random_uuid(),
    chat_grupo_id uuid NOT NULL,
    usuario_id uuid,
    nombre_archivo text NOT NULL,
    url_archivo text NOT NULL,
    fecha_envio timestamp with time zone NOT NULL DEFAULT now(),
    tipo_archivo text
,
    PRIMARY KEY (archivo_id)
);

-- Foreign Keys de ArchivoChat
ALTER TABLE ArchivoChat ADD CONSTRAINT ArchivoChat_chat_grupo_id_fkey FOREIGN KEY (chat_grupo_id) REFERENCES ChatGrupo(chat_grupo_id);
ALTER TABLE ArchivoChat ADD CONSTRAINT ArchivoChat_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de ArchivoChat
ALTER TABLE ArchivoChat ADD CONSTRAINT 39558_40252_1_not_null CHECK (archivo_id IS NOT NULL);
ALTER TABLE ArchivoChat ADD CONSTRAINT 39558_40252_2_not_null CHECK (chat_grupo_id IS NOT NULL);
ALTER TABLE ArchivoChat ADD CONSTRAINT 39558_40252_4_not_null CHECK (nombre_archivo IS NOT NULL);
ALTER TABLE ArchivoChat ADD CONSTRAINT 39558_40252_5_not_null CHECK (url_archivo IS NOT NULL);
ALTER TABLE ArchivoChat ADD CONSTRAINT 39558_40252_6_not_null CHECK (fecha_envio IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: Asistencia
-- =====================================================

CREATE TABLE IF NOT EXISTS Asistencia (
    asistencia_id uuid NOT NULL DEFAULT gen_random_uuid(),
    clase_id uuid NOT NULL,
    estudiante_id uuid NOT NULL,
    estado USER-DEFINED NOT NULL
,
    PRIMARY KEY (asistencia_id)
);

-- Foreign Keys de Asistencia
ALTER TABLE Asistencia ADD CONSTRAINT Asistencia_clase_id_fkey FOREIGN KEY (clase_id) REFERENCES Clase(clase_id);
ALTER TABLE Asistencia ADD CONSTRAINT Asistencia_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES Estudiante(estudiante_id);

-- Check Constraints de Asistencia
ALTER TABLE Asistencia ADD CONSTRAINT 39558_40325_1_not_null CHECK (asistencia_id IS NOT NULL);
ALTER TABLE Asistencia ADD CONSTRAINT 39558_40325_2_not_null CHECK (clase_id IS NOT NULL);
ALTER TABLE Asistencia ADD CONSTRAINT 39558_40325_3_not_null CHECK (estudiante_id IS NOT NULL);
ALTER TABLE Asistencia ADD CONSTRAINT 39558_40325_4_not_null CHECK (estado IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: ChatBot
-- =====================================================

CREATE TABLE IF NOT EXISTS ChatBot (
    chat_bot_id uuid NOT NULL DEFAULT gen_random_uuid(),
    nombre character varying(100) NOT NULL,
    descripcion text NOT NULL,
    foto_perfil_url text NOT NULL,
    activo boolean,
    fecha_registro date DEFAULT now()
,
    PRIMARY KEY (chat_bot_id)
);

-- Unique Constraints de ChatBot
ALTER TABLE ChatBot ADD CONSTRAINT ChatBot_nombre_key UNIQUE (nombre);

-- Check Constraints de ChatBot
ALTER TABLE ChatBot ADD CONSTRAINT 39558_39564_1_not_null CHECK (chat_bot_id IS NOT NULL);
ALTER TABLE ChatBot ADD CONSTRAINT 39558_39564_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE ChatBot ADD CONSTRAINT 39558_39564_3_not_null CHECK (descripcion IS NOT NULL);
ALTER TABLE ChatBot ADD CONSTRAINT 39558_39564_4_not_null CHECK (foto_perfil_url IS NOT NULL);

-- Índices de ChatBot
CREATE UNIQUE INDEX "ChatBot_nombre_key" ON public."ChatBot" USING btree (nombre);


============================================================

-- =====================================================
-- Tabla: ChatGrupo
-- =====================================================

CREATE TABLE IF NOT EXISTS ChatGrupo (
    chat_grupo_id uuid NOT NULL DEFAULT gen_random_uuid(),
    grupo_id uuid NOT NULL,
    fecha_creacion timestamp with time zone NOT NULL DEFAULT now(),
    descripcion text,
    foto_perfil text,
    permite_archivos boolean NOT NULL DEFAULT true,
    capacidad_almacenamiento integer NOT NULL DEFAULT 52428800,
    estado_chat USER-DEFINED NOT NULL DEFAULT 'activo'::estado_chat_grupo
,
    PRIMARY KEY (chat_grupo_id)
);

-- Foreign Keys de ChatGrupo
ALTER TABLE ChatGrupo ADD CONSTRAINT ChatGrupo_grupo_id_fkey FOREIGN KEY (grupo_id) REFERENCES Grupo(grupo_id);

-- Check Constraints de ChatGrupo
ALTER TABLE ChatGrupo ADD CONSTRAINT 39558_40167_1_not_null CHECK (chat_grupo_id IS NOT NULL);
ALTER TABLE ChatGrupo ADD CONSTRAINT 39558_40167_2_not_null CHECK (grupo_id IS NOT NULL);
ALTER TABLE ChatGrupo ADD CONSTRAINT 39558_40167_3_not_null CHECK (fecha_creacion IS NOT NULL);
ALTER TABLE ChatGrupo ADD CONSTRAINT 39558_40167_6_not_null CHECK (permite_archivos IS NOT NULL);
ALTER TABLE ChatGrupo ADD CONSTRAINT 39558_40167_7_not_null CHECK (capacidad_almacenamiento IS NOT NULL);
ALTER TABLE ChatGrupo ADD CONSTRAINT 39558_40167_8_not_null CHECK (estado_chat IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: Clase
-- =====================================================

CREATE TABLE IF NOT EXISTS Clase (
    clase_id uuid NOT NULL DEFAULT gen_random_uuid(),
    grupo_curso_id uuid NOT NULL,
    plataforma_id uuid,
    titulo text NOT NULL,
    descripcion text,
    hora_inicio timestamp with time zone NOT NULL DEFAULT now(),
    duracion interval NOT NULL,
    link_videollamada text NOT NULL
,
    PRIMARY KEY (clase_id)
);

-- Foreign Keys de Clase
ALTER TABLE Clase ADD CONSTRAINT Clase_grupo_curso_id_fkey FOREIGN KEY (grupo_curso_id) REFERENCES GrupoCurso(grupo_curso_id);
ALTER TABLE Clase ADD CONSTRAINT Clase_plataforma_id_fkey FOREIGN KEY (plataforma_id) REFERENCES Plataforma(plataforma_id);

-- Check Constraints de Clase
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_1_not_null CHECK (clase_id IS NOT NULL);
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_2_not_null CHECK (grupo_curso_id IS NOT NULL);
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_4_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_6_not_null CHECK (hora_inicio IS NOT NULL);
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_7_not_null CHECK (duracion IS NOT NULL);
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_8_not_null CHECK (link_videollamada IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: Comentario
-- =====================================================

CREATE TABLE IF NOT EXISTS Comentario (
    comentario_id uuid NOT NULL DEFAULT gen_random_uuid(),
    curso_id uuid NOT NULL,
    autor_id uuid NOT NULL,
    contenido text NOT NULL,
    tipo USER-DEFINED NOT NULL DEFAULT 'comentario'::tipocomentario,
    archivos_adjuntos json,
    comentario_padre_id uuid,
    fecha_creacion timestamp with time zone NOT NULL DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    fecha_eliminacion timestamp with time zone,
    esta_eliminado boolean NOT NULL DEFAULT false,
    editado boolean NOT NULL DEFAULT false,
    activo boolean NOT NULL DEFAULT true
,
    PRIMARY KEY (comentario_id)
);

-- Foreign Keys de Comentario
ALTER TABLE Comentario ADD CONSTRAINT Comentario_curso_id_fkey FOREIGN KEY (curso_id) REFERENCES Curso(curso_id);
ALTER TABLE Comentario ADD CONSTRAINT Comentario_autor_id_fkey FOREIGN KEY (autor_id) REFERENCES Usuario(usuario_id);
ALTER TABLE Comentario ADD CONSTRAINT Comentario_comentario_padre_id_fkey FOREIGN KEY (comentario_padre_id) REFERENCES Comentario(comentario_id);

-- Check Constraints de Comentario
ALTER TABLE Comentario ADD CONSTRAINT 39558_40707_11_not_null CHECK (esta_eliminado IS NOT NULL);
ALTER TABLE Comentario ADD CONSTRAINT 39558_40707_12_not_null CHECK (editado IS NOT NULL);
ALTER TABLE Comentario ADD CONSTRAINT 39558_40707_13_not_null CHECK (activo IS NOT NULL);
ALTER TABLE Comentario ADD CONSTRAINT 39558_40707_1_not_null CHECK (comentario_id IS NOT NULL);
ALTER TABLE Comentario ADD CONSTRAINT 39558_40707_2_not_null CHECK (curso_id IS NOT NULL);
ALTER TABLE Comentario ADD CONSTRAINT 39558_40707_3_not_null CHECK (autor_id IS NOT NULL);
ALTER TABLE Comentario ADD CONSTRAINT 39558_40707_4_not_null CHECK (contenido IS NOT NULL);
ALTER TABLE Comentario ADD CONSTRAINT 39558_40707_5_not_null CHECK (tipo IS NOT NULL);
ALTER TABLE Comentario ADD CONSTRAINT 39558_40707_8_not_null CHECK (fecha_creacion IS NOT NULL);

-- Índices de Comentario
CREATE INDEX idx_comentarios_curso_id ON public."Comentario" USING btree (curso_id) WHERE (comentario_padre_id IS NULL);
CREATE INDEX idx_comentarios_padre_id ON public."Comentario" USING btree (comentario_padre_id) WHERE (comentario_padre_id IS NOT NULL);
CREATE INDEX idx_comentarios_autor_id ON public."Comentario" USING btree (autor_id);
CREATE INDEX idx_comentarios_fecha_creacion ON public."Comentario" USING btree (fecha_creacion DESC);
CREATE INDEX idx_comentarios_curso_tipo_fecha ON public."Comentario" USING btree (curso_id, tipo, fecha_creacion DESC) WHERE (comentario_padre_id IS NULL);
CREATE INDEX idx_comentario_curso_id ON public."Comentario" USING btree (curso_id);
CREATE INDEX idx_comentario_autor_id ON public."Comentario" USING btree (autor_id);
CREATE INDEX idx_comentario_fecha_creacion ON public."Comentario" USING btree (fecha_creacion);
CREATE INDEX idx_comentario_tipo ON public."Comentario" USING btree (tipo);
CREATE INDEX idx_comentario_activo ON public."Comentario" USING btree (activo);
CREATE INDEX idx_comentario_curso_fecha ON public."Comentario" USING btree (curso_id, fecha_creacion);
CREATE INDEX idx_comentario_autor_fecha ON public."Comentario" USING btree (autor_id, fecha_creacion);
CREATE INDEX idx_comentario_tipo_activo ON public."Comentario" USING btree (tipo, activo);
CREATE INDEX idx_comentario_padre ON public."Comentario" USING btree (comentario_padre_id);


============================================================

-- =====================================================
-- Tabla: Coordinador
-- =====================================================

CREATE TABLE IF NOT EXISTS Coordinador (
    coordinador_id uuid NOT NULL,
    horario_atencion character varying(50),
    fecha_inicio_carrera date NOT NULL
,
    PRIMARY KEY (coordinador_id)
);

-- Foreign Keys de Coordinador
ALTER TABLE Coordinador ADD CONSTRAINT Coordinador_coordinador_id_fkey FOREIGN KEY (coordinador_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de Coordinador
ALTER TABLE Coordinador ADD CONSTRAINT 39558_39740_1_not_null CHECK (coordinador_id IS NOT NULL);
ALTER TABLE Coordinador ADD CONSTRAINT 39558_39740_3_not_null CHECK (fecha_inicio_carrera IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: Curso
-- =====================================================

CREATE TABLE IF NOT EXISTS Curso (
    curso_id uuid NOT NULL DEFAULT gen_random_uuid(),
    institucion_id uuid NOT NULL,
    coordinador_id uuid,
    programa_id uuid NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion text,
    modalidad USER-DEFINED NOT NULL,
    fecha_inicio date,
    fecha_fin date,
    objetivos text,
    codigo_curso character varying(20),
    codigo_acceso character varying(10),
    creditos integer DEFAULT 0,
    horas_academicas integer DEFAULT 0,
    activo boolean NOT NULL DEFAULT true,
    permite_inscripcion boolean NOT NULL DEFAULT true,
    maximo_estudiantes integer,
    minimo_estudiantes integer DEFAULT 1,
    permite_material_estudiantes boolean NOT NULL DEFAULT false,
    requiere_aprobacion_material boolean NOT NULL DEFAULT true
,
    PRIMARY KEY (curso_id)
);

-- Foreign Keys de Curso
ALTER TABLE Curso ADD CONSTRAINT Curso_coordinador_id_fkey FOREIGN KEY (coordinador_id) REFERENCES Coordinador(coordinador_id);
ALTER TABLE Curso ADD CONSTRAINT Curso_institucion_id_fkey FOREIGN KEY (institucion_id) REFERENCES Institucion(institucion_id);
ALTER TABLE Curso ADD CONSTRAINT Curso_programa_id_fkey FOREIGN KEY (programa_id) REFERENCES Programa(programa_id);

-- Unique Constraints de Curso
ALTER TABLE Curso ADD CONSTRAINT Curso_codigo_acceso_key UNIQUE (codigo_acceso);
ALTER TABLE Curso ADD CONSTRAINT uq_curso_nombre UNIQUE (institucion_id, nombre);

-- Check Constraints de Curso
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_15_not_null CHECK (activo IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_16_not_null CHECK (permite_inscripcion IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_19_not_null CHECK (permite_material_estudiantes IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_1_not_null CHECK (curso_id IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_20_not_null CHECK (requiere_aprobacion_material IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_2_not_null CHECK (institucion_id IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_4_not_null CHECK (programa_id IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_5_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Curso ADD CONSTRAINT 39558_40055_7_not_null CHECK (modalidad IS NOT NULL);

-- Índices de Curso
CREATE UNIQUE INDEX "Curso_codigo_acceso_key" ON public."Curso" USING btree (codigo_acceso);
CREATE UNIQUE INDEX idx_curso_codigo_acceso ON public."Curso" USING btree (codigo_acceso);
CREATE INDEX idx_curso_institucion_id ON public."Curso" USING btree (institucion_id);
CREATE INDEX idx_curso_programa_id ON public."Curso" USING btree (programa_id);
CREATE INDEX idx_curso_coordinador_id ON public."Curso" USING btree (coordinador_id) WHERE (coordinador_id IS NOT NULL);
CREATE INDEX idx_curso_institucion_programa ON public."Curso" USING btree (institucion_id, programa_id);
CREATE UNIQUE INDEX uq_curso_nombre ON public."Curso" USING btree (institucion_id, nombre);


============================================================

-- =====================================================
-- Tabla: CursoDocente
-- =====================================================

CREATE TABLE IF NOT EXISTS CursoDocente (
    curso_id uuid NOT NULL,
    docente_id uuid NOT NULL,
    fecha_asignacion date
,
    PRIMARY KEY (curso_id, docente_id)
);

-- Foreign Keys de CursoDocente
ALTER TABLE CursoDocente ADD CONSTRAINT CursoDocente_curso_id_fkey FOREIGN KEY (curso_id) REFERENCES Curso(curso_id);
ALTER TABLE CursoDocente ADD CONSTRAINT CursoDocente_docente_id_fkey FOREIGN KEY (docente_id) REFERENCES Docente(docente_id);

-- Check Constraints de CursoDocente
ALTER TABLE CursoDocente ADD CONSTRAINT 39558_40184_1_not_null CHECK (curso_id IS NOT NULL);
ALTER TABLE CursoDocente ADD CONSTRAINT 39558_40184_2_not_null CHECK (docente_id IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: Docente
-- =====================================================

CREATE TABLE IF NOT EXISTS Docente (
    docente_id uuid NOT NULL,
    area_conocimiento character varying(50) NOT NULL,
    fecha_vinculacion date NOT NULL,
    tipo_vinculacion USER-DEFINED NOT NULL DEFAULT 'planta'::tipo_vinculacion_institucion,
    titulo_academico character varying(50),
    horas_semanales smallint
,
    PRIMARY KEY (docente_id)
);

-- Foreign Keys de Docente
ALTER TABLE Docente ADD CONSTRAINT Docente_docente_id_fkey FOREIGN KEY (docente_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de Docente
ALTER TABLE Docente ADD CONSTRAINT 39558_39761_1_not_null CHECK (docente_id IS NOT NULL);
ALTER TABLE Docente ADD CONSTRAINT 39558_39761_2_not_null CHECK (area_conocimiento IS NOT NULL);
ALTER TABLE Docente ADD CONSTRAINT 39558_39761_3_not_null CHECK (fecha_vinculacion IS NOT NULL);
ALTER TABLE Docente ADD CONSTRAINT 39558_39761_4_not_null CHECK (tipo_vinculacion IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: EscalaCalificacion
-- =====================================================

CREATE TABLE IF NOT EXISTS EscalaCalificacion (
    escala_id uuid NOT NULL DEFAULT gen_random_uuid(),
    institucion_id uuid NOT NULL,
    nombre character varying(50) NOT NULL,
    tipo USER-DEFINED NOT NULL,
    min_valor numeric,
    max_valor numeric
,
    PRIMARY KEY (escala_id)
);

-- Foreign Keys de EscalaCalificacion
ALTER TABLE EscalaCalificacion ADD CONSTRAINT EscalaCalificacion_institucion_id_fkey FOREIGN KEY (institucion_id) REFERENCES Institucion(institucion_id);

-- Check Constraints de EscalaCalificacion
ALTER TABLE EscalaCalificacion ADD CONSTRAINT 39558_39947_1_not_null CHECK (escala_id IS NOT NULL);
ALTER TABLE EscalaCalificacion ADD CONSTRAINT 39558_39947_2_not_null CHECK (institucion_id IS NOT NULL);
ALTER TABLE EscalaCalificacion ADD CONSTRAINT 39558_39947_3_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE EscalaCalificacion ADD CONSTRAINT 39558_39947_4_not_null CHECK (tipo IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: Estudiante
-- =====================================================

CREATE TABLE IF NOT EXISTS Estudiante (
    estudiante_id uuid NOT NULL,
    programa_id uuid,
    fecha_ingreso date NOT NULL,
    creditos_aprobados smallint,
    etapa_formativa USER-DEFINED NOT NULL DEFAULT 'i'::etapa_formativa_estudiante,
    promedio_acumulado numeric
,
    PRIMARY KEY (estudiante_id)
);

-- Foreign Keys de Estudiante
ALTER TABLE Estudiante ADD CONSTRAINT Estudiante_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES Usuario(usuario_id);
ALTER TABLE Estudiante ADD CONSTRAINT Estudiante_programa_id_fkey FOREIGN KEY (programa_id) REFERENCES Programa(programa_id);

-- Check Constraints de Estudiante
ALTER TABLE Estudiante ADD CONSTRAINT 39558_40105_1_not_null CHECK (estudiante_id IS NOT NULL);
ALTER TABLE Estudiante ADD CONSTRAINT 39558_40105_3_not_null CHECK (fecha_ingreso IS NOT NULL);
ALTER TABLE Estudiante ADD CONSTRAINT 39558_40105_5_not_null CHECK (etapa_formativa IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: EstudianteGrupo
-- =====================================================

CREATE TABLE IF NOT EXISTS EstudianteGrupo (
    grupo_id uuid NOT NULL,
    estudiante_id uuid NOT NULL,
    fecha_vinculacion date NOT NULL
,
    PRIMARY KEY (grupo_id, estudiante_id)
);

-- Foreign Keys de EstudianteGrupo
ALTER TABLE EstudianteGrupo ADD CONSTRAINT EstudianteGrupo_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES Estudiante(estudiante_id);
ALTER TABLE EstudianteGrupo ADD CONSTRAINT EstudianteGrupo_grupo_id_fkey FOREIGN KEY (grupo_id) REFERENCES Grupo(grupo_id);

-- Check Constraints de EstudianteGrupo
ALTER TABLE EstudianteGrupo ADD CONSTRAINT 39558_40199_1_not_null CHECK (grupo_id IS NOT NULL);
ALTER TABLE EstudianteGrupo ADD CONSTRAINT 39558_40199_2_not_null CHECK (estudiante_id IS NOT NULL);
ALTER TABLE EstudianteGrupo ADD CONSTRAINT 39558_40199_3_not_null CHECK (fecha_vinculacion IS NOT NULL);

-- Índices de EstudianteGrupo
CREATE INDEX idx_estudiante_grupo_grupo_id ON public."EstudianteGrupo" USING btree (grupo_id);
CREATE INDEX idx_estudiante_grupo_estudiante_id ON public."EstudianteGrupo" USING btree (estudiante_id);
CREATE INDEX idx_estudiante_grupo_estudiante_grupo ON public."EstudianteGrupo" USING btree (estudiante_id, grupo_id);


============================================================

-- =====================================================
-- Tabla: FAQBot
-- =====================================================

CREATE TABLE IF NOT EXISTS FAQBot (
    faq_id uuid NOT NULL DEFAULT gen_random_uuid(),
    pregunta text NOT NULL,
    respuesta text NOT NULL,
    categoria character varying(50) NOT NULL,
    ultima_actualizacion timestamp without time zone
,
    PRIMARY KEY (faq_id)
);

-- Check Constraints de FAQBot
ALTER TABLE FAQBot ADD CONSTRAINT 39558_39575_1_not_null CHECK (faq_id IS NOT NULL);
ALTER TABLE FAQBot ADD CONSTRAINT 39558_39575_2_not_null CHECK (pregunta IS NOT NULL);
ALTER TABLE FAQBot ADD CONSTRAINT 39558_39575_3_not_null CHECK (respuesta IS NOT NULL);
ALTER TABLE FAQBot ADD CONSTRAINT 39558_39575_4_not_null CHECK (categoria IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: Grupo
-- =====================================================

CREATE TABLE IF NOT EXISTS Grupo (
    grupo_id uuid NOT NULL DEFAULT gen_random_uuid(),
    programa_id uuid NOT NULL,
    docente_tutor_id uuid,
    nombre character varying(50) NOT NULL,
    jornada USER-DEFINED NOT NULL DEFAULT 'manana'::jornada_grupo
,
    PRIMARY KEY (grupo_id)
);

-- Foreign Keys de Grupo
ALTER TABLE Grupo ADD CONSTRAINT Grupo_docente_tutor_id_fkey FOREIGN KEY (docente_tutor_id) REFERENCES Docente(docente_id);
ALTER TABLE Grupo ADD CONSTRAINT Grupo_programa_id_fkey FOREIGN KEY (programa_id) REFERENCES Programa(programa_id);

-- Unique Constraints de Grupo
ALTER TABLE Grupo ADD CONSTRAINT Grupo_docente_tutor_id_key UNIQUE (docente_tutor_id);

-- Check Constraints de Grupo
ALTER TABLE Grupo ADD CONSTRAINT 39558_40129_1_not_null CHECK (grupo_id IS NOT NULL);
ALTER TABLE Grupo ADD CONSTRAINT 39558_40129_2_not_null CHECK (programa_id IS NOT NULL);
ALTER TABLE Grupo ADD CONSTRAINT 39558_40129_4_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Grupo ADD CONSTRAINT 39558_40129_5_not_null CHECK (jornada IS NOT NULL);

-- Índices de Grupo
CREATE UNIQUE INDEX "Grupo_docente_tutor_id_key" ON public."Grupo" USING btree (docente_tutor_id);


============================================================

-- =====================================================
-- Tabla: GrupoCurso
-- =====================================================

CREATE TABLE IF NOT EXISTS GrupoCurso (
    grupo_curso_id uuid NOT NULL DEFAULT gen_random_uuid(),
    grupo_id uuid NOT NULL,
    curso_id uuid NOT NULL,
    docente_id uuid NOT NULL,
    fecha_asignacion date
,
    PRIMARY KEY (grupo_curso_id)
);

-- Foreign Keys de GrupoCurso
ALTER TABLE GrupoCurso ADD CONSTRAINT GrupoCurso_curso_id_fkey FOREIGN KEY (curso_id) REFERENCES Curso(curso_id);
ALTER TABLE GrupoCurso ADD CONSTRAINT GrupoCurso_docente_id_fkey FOREIGN KEY (docente_id) REFERENCES Docente(docente_id);
ALTER TABLE GrupoCurso ADD CONSTRAINT GrupoCurso_grupo_id_fkey FOREIGN KEY (grupo_id) REFERENCES Grupo(grupo_id);

-- Unique Constraints de GrupoCurso
ALTER TABLE GrupoCurso ADD CONSTRAINT uq_grupo_curso UNIQUE (curso_id, grupo_id);

-- Check Constraints de GrupoCurso
ALTER TABLE GrupoCurso ADD CONSTRAINT 39558_40214_1_not_null CHECK (grupo_curso_id IS NOT NULL);
ALTER TABLE GrupoCurso ADD CONSTRAINT 39558_40214_2_not_null CHECK (grupo_id IS NOT NULL);
ALTER TABLE GrupoCurso ADD CONSTRAINT 39558_40214_3_not_null CHECK (curso_id IS NOT NULL);
ALTER TABLE GrupoCurso ADD CONSTRAINT 39558_40214_4_not_null CHECK (docente_id IS NOT NULL);

-- Índices de GrupoCurso
CREATE INDEX idx_grupo_curso_curso_id ON public."GrupoCurso" USING btree (curso_id);
CREATE INDEX idx_grupo_curso_docente_id ON public."GrupoCurso" USING btree (docente_id);
CREATE UNIQUE INDEX uq_grupo_curso ON public."GrupoCurso" USING btree (curso_id, grupo_id);


============================================================

-- =====================================================
-- Tabla: HistorialPuntos
-- =====================================================

CREATE TABLE IF NOT EXISTS HistorialPuntos (
    historial_id uuid NOT NULL DEFAULT gen_random_uuid(),
    usuario_id uuid,
    cambio integer NOT NULL,
    motivo text,
    fecha timestamp with time zone NOT NULL DEFAULT now()
,
    PRIMARY KEY (historial_id)
);

-- Foreign Keys de HistorialPuntos
ALTER TABLE HistorialPuntos ADD CONSTRAINT HistorialPuntos_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de HistorialPuntos
ALTER TABLE HistorialPuntos ADD CONSTRAINT 39558_39772_1_not_null CHECK (historial_id IS NOT NULL);
ALTER TABLE HistorialPuntos ADD CONSTRAINT 39558_39772_3_not_null CHECK (cambio IS NOT NULL);
ALTER TABLE HistorialPuntos ADD CONSTRAINT 39558_39772_5_not_null CHECK (fecha IS NOT NULL);
ALTER TABLE HistorialPuntos ADD CONSTRAINT HistorialPuntos_cambio_check CHECK ((cambio <> 0));


============================================================

-- =====================================================
-- Tabla: Insignia
-- =====================================================

CREATE TABLE IF NOT EXISTS Insignia (
    insignia_id uuid NOT NULL DEFAULT gen_random_uuid(),
    nombre character varying(100) NOT NULL,
    descripcion text,
    imagen_url text,
    tipo USER-DEFINED NOT NULL DEFAULT 'manual'::tipo_insignia,
    es_unica boolean NOT NULL
,
    PRIMARY KEY (insignia_id)
);

-- Unique Constraints de Insignia
ALTER TABLE Insignia ADD CONSTRAINT Insignia_nombre_key UNIQUE (nombre);

-- Check Constraints de Insignia
ALTER TABLE Insignia ADD CONSTRAINT 39558_39593_1_not_null CHECK (insignia_id IS NOT NULL);
ALTER TABLE Insignia ADD CONSTRAINT 39558_39593_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Insignia ADD CONSTRAINT 39558_39593_5_not_null CHECK (tipo IS NOT NULL);
ALTER TABLE Insignia ADD CONSTRAINT 39558_39593_6_not_null CHECK (es_unica IS NOT NULL);

-- Índices de Insignia
CREATE UNIQUE INDEX "Insignia_nombre_key" ON public."Insignia" USING btree (nombre);


============================================================

-- =====================================================
-- Tabla: Institucion
-- =====================================================

CREATE TABLE IF NOT EXISTS Institucion (
    institucion_id uuid NOT NULL DEFAULT gen_random_uuid(),
    administrador_id_creador uuid,
    nombre character varying(150) NOT NULL,
    sigla character varying(20),
    lema character varying(255),
    tipo_institucion USER-DEFINED NOT NULL,
    usa_programas boolean NOT NULL,
    nivel_educativo USER-DEFINED NOT NULL,
    sector USER-DEFINED NOT NULL,
    direccion character varying(255),
    ciudad character varying(100),
    pais character varying(100) NOT NULL,
    correo_institucional character varying(100) NOT NULL,
    telefono character varying(30) NOT NULL,
    nit character varying(20),
    estado USER-DEFINED NOT NULL DEFAULT 'pendiente'::estado_institucion,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_activacion timestamp with time zone,
    dominio character varying(255)
,
    PRIMARY KEY (institucion_id)
);

-- Foreign Keys de Institucion
ALTER TABLE Institucion ADD CONSTRAINT Institucion_administrador_id_creador_fkey FOREIGN KEY (administrador_id_creador) REFERENCES Usuario(usuario_id);

-- Unique Constraints de Institucion
ALTER TABLE Institucion ADD CONSTRAINT Institucion_correo_institucional_key UNIQUE (correo_institucional);
ALTER TABLE Institucion ADD CONSTRAINT Institucion_nit_key UNIQUE (nit);
ALTER TABLE Institucion ADD CONSTRAINT Institucion_nombre_key UNIQUE (nombre);
ALTER TABLE Institucion ADD CONSTRAINT Institucion_sigla_key UNIQUE (sigla);

-- Check Constraints de Institucion
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_12_not_null CHECK (pais IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_13_not_null CHECK (correo_institucional IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_14_not_null CHECK (telefono IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_16_not_null CHECK (estado IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_1_not_null CHECK (institucion_id IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_3_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_6_not_null CHECK (tipo_institucion IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_7_not_null CHECK (usa_programas IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_8_not_null CHECK (nivel_educativo IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_9_not_null CHECK (sector IS NOT NULL);

-- Índices de Institucion
CREATE INDEX idx_institucion_dominio ON public."Institucion" USING btree (dominio);
CREATE UNIQUE INDEX "Institucion_correo_institucional_key" ON public."Institucion" USING btree (correo_institucional);
CREATE UNIQUE INDEX "Institucion_nit_key" ON public."Institucion" USING btree (nit);
CREATE UNIQUE INDEX "Institucion_nombre_key" ON public."Institucion" USING btree (nombre);
CREATE UNIQUE INDEX "Institucion_sigla_key" ON public."Institucion" USING btree (sigla);


============================================================

-- =====================================================
-- Tabla: InstitucionCoordinador
-- =====================================================

CREATE TABLE IF NOT EXISTS InstitucionCoordinador (
    institucion_id uuid NOT NULL,
    coordinador_id uuid NOT NULL,
    fecha_asignacion date NOT NULL,
    estado USER-DEFINED NOT NULL DEFAULT 'activo'::estado_coordinador
,
    PRIMARY KEY (institucion_id, coordinador_id)
);

-- Foreign Keys de InstitucionCoordinador
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT InstitucionCoordinador_coordinador_id_fkey FOREIGN KEY (coordinador_id) REFERENCES Coordinador(coordinador_id);
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT InstitucionCoordinador_institucion_id_fkey FOREIGN KEY (institucion_id) REFERENCES Institucion(institucion_id);

-- Check Constraints de InstitucionCoordinador
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT 39558_39967_1_not_null CHECK (institucion_id IS NOT NULL);
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT 39558_39967_2_not_null CHECK (coordinador_id IS NOT NULL);
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT 39558_39967_3_not_null CHECK (fecha_asignacion IS NOT NULL);
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT 39558_39967_4_not_null CHECK (estado IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: MaterialClase
-- =====================================================

CREATE TABLE IF NOT EXISTS MaterialClase (
    material_clase_id uuid NOT NULL,
    clase_id uuid
,
    PRIMARY KEY (material_clase_id)
);

-- Foreign Keys de MaterialClase
ALTER TABLE MaterialClase ADD CONSTRAINT MaterialClase_clase_id_fkey FOREIGN KEY (clase_id) REFERENCES Clase(clase_id);
ALTER TABLE MaterialClase ADD CONSTRAINT MaterialClase_material_clase_id_fkey FOREIGN KEY (material_clase_id) REFERENCES MaterialEducativo(material_id);

-- Check Constraints de MaterialClase
ALTER TABLE MaterialClase ADD CONSTRAINT 39558_40341_1_not_null CHECK (material_clase_id IS NOT NULL);

-- Índices de MaterialClase
CREATE INDEX idx_material_clase_clase_id ON public."MaterialClase" USING btree (clase_id);


============================================================

-- =====================================================
-- Tabla: MaterialCurso
-- =====================================================

CREATE TABLE IF NOT EXISTS MaterialCurso (
    material_curso_id uuid NOT NULL,
    curso_id uuid NOT NULL
,
    PRIMARY KEY (material_curso_id, curso_id)
);

-- Foreign Keys de MaterialCurso
ALTER TABLE MaterialCurso ADD CONSTRAINT MaterialCurso_curso_id_fkey FOREIGN KEY (curso_id) REFERENCES Curso(curso_id);
ALTER TABLE MaterialCurso ADD CONSTRAINT MaterialCurso_material_curso_id_fkey FOREIGN KEY (material_curso_id) REFERENCES MaterialEducativo(material_id);

-- Check Constraints de MaterialCurso
ALTER TABLE MaterialCurso ADD CONSTRAINT 39558_40237_1_not_null CHECK (material_curso_id IS NOT NULL);
ALTER TABLE MaterialCurso ADD CONSTRAINT 39558_40237_2_not_null CHECK (curso_id IS NOT NULL);

-- Índices de MaterialCurso
CREATE INDEX idx_material_curso_curso_id ON public."MaterialCurso" USING btree (curso_id);


============================================================

-- =====================================================
-- Tabla: MaterialEducativo
-- =====================================================

CREATE TABLE IF NOT EXISTS MaterialEducativo (
    material_id uuid NOT NULL DEFAULT gen_random_uuid(),
    titulo character varying(100) NOT NULL,
    descripcion text,
    tipo_material USER-DEFINED NOT NULL,
    url_archivo character varying(255) NOT NULL,
    formato_archivo character varying(10) NOT NULL
,
    PRIMARY KEY (material_id)
);

-- Check Constraints de MaterialEducativo
ALTER TABLE MaterialEducativo ADD CONSTRAINT 39558_39627_1_not_null CHECK (material_id IS NOT NULL);
ALTER TABLE MaterialEducativo ADD CONSTRAINT 39558_39627_2_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE MaterialEducativo ADD CONSTRAINT 39558_39627_4_not_null CHECK (tipo_material IS NOT NULL);
ALTER TABLE MaterialEducativo ADD CONSTRAINT 39558_39627_5_not_null CHECK (url_archivo IS NOT NULL);
ALTER TABLE MaterialEducativo ADD CONSTRAINT 39558_39627_6_not_null CHECK (formato_archivo IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: OAuthProvider
-- =====================================================

CREATE TABLE IF NOT EXISTS OAuthProvider (
    oauth_provider_id uuid NOT NULL DEFAULT gen_random_uuid(),
    usuario_id uuid NOT NULL,
    provider character varying(50) NOT NULL,
    provider_user_id character varying(255) NOT NULL,
    provider_email character varying(255) NOT NULL,
    fecha_vinculacion timestamp with time zone NOT NULL DEFAULT now()
,
    PRIMARY KEY (oauth_provider_id)
);

-- Foreign Keys de OAuthProvider
ALTER TABLE OAuthProvider ADD CONSTRAINT OAuthProvider_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Unique Constraints de OAuthProvider
ALTER TABLE OAuthProvider ADD CONSTRAINT uq_provider_user UNIQUE (provider, provider_user_id);

-- Check Constraints de OAuthProvider
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_1_not_null CHECK (oauth_provider_id IS NOT NULL);
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_2_not_null CHECK (usuario_id IS NOT NULL);
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_3_not_null CHECK (provider IS NOT NULL);
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_4_not_null CHECK (provider_user_id IS NOT NULL);
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_5_not_null CHECK (provider_email IS NOT NULL);
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_6_not_null CHECK (fecha_vinculacion IS NOT NULL);

-- Índices de OAuthProvider
CREATE UNIQUE INDEX uq_provider_user ON public."OAuthProvider" USING btree (provider, provider_user_id);


============================================================

-- =====================================================
-- Tabla: Plataforma
-- =====================================================

CREATE TABLE IF NOT EXISTS Plataforma (
    plataforma_id uuid NOT NULL DEFAULT gen_random_uuid(),
    nombre character varying(50) NOT NULL,
    url_base text NOT NULL,
    tipo_integracion USER-DEFINED NOT NULL,
    requiere_cuenta boolean NOT NULL,
    es_gratuita boolean
,
    PRIMARY KEY (plataforma_id)
);

-- Unique Constraints de Plataforma
ALTER TABLE Plataforma ADD CONSTRAINT Plataforma_nombre_key UNIQUE (nombre);

-- Check Constraints de Plataforma
ALTER TABLE Plataforma ADD CONSTRAINT 39558_39645_1_not_null CHECK (plataforma_id IS NOT NULL);
ALTER TABLE Plataforma ADD CONSTRAINT 39558_39645_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Plataforma ADD CONSTRAINT 39558_39645_3_not_null CHECK (url_base IS NOT NULL);
ALTER TABLE Plataforma ADD CONSTRAINT 39558_39645_4_not_null CHECK (tipo_integracion IS NOT NULL);
ALTER TABLE Plataforma ADD CONSTRAINT 39558_39645_5_not_null CHECK (requiere_cuenta IS NOT NULL);

-- Índices de Plataforma
CREATE UNIQUE INDEX "Plataforma_nombre_key" ON public."Plataforma" USING btree (nombre);


============================================================

-- =====================================================
-- Tabla: Programa
-- =====================================================

CREATE TABLE IF NOT EXISTS Programa (
    programa_id uuid NOT NULL DEFAULT gen_random_uuid(),
    institucion_id uuid NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    nivel USER-DEFINED NOT NULL,
    tipo USER-DEFINED NOT NULL
,
    PRIMARY KEY (programa_id)
);

-- Foreign Keys de Programa
ALTER TABLE Programa ADD CONSTRAINT Programa_institucion_id_fkey FOREIGN KEY (institucion_id) REFERENCES Institucion(institucion_id);

-- Unique Constraints de Programa
ALTER TABLE Programa ADD CONSTRAINT uq_programa_nombre UNIQUE (institucion_id, nombre);

-- Check Constraints de Programa
ALTER TABLE Programa ADD CONSTRAINT 39558_40021_1_not_null CHECK (programa_id IS NOT NULL);
ALTER TABLE Programa ADD CONSTRAINT 39558_40021_2_not_null CHECK (institucion_id IS NOT NULL);
ALTER TABLE Programa ADD CONSTRAINT 39558_40021_3_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Programa ADD CONSTRAINT 39558_40021_5_not_null CHECK (nivel IS NOT NULL);
ALTER TABLE Programa ADD CONSTRAINT 39558_40021_6_not_null CHECK (tipo IS NOT NULL);

-- Índices de Programa
CREATE UNIQUE INDEX uq_programa_nombre ON public."Programa" USING btree (institucion_id, nombre);


============================================================

-- =====================================================
-- Tabla: Reacciones
-- =====================================================

CREATE TABLE IF NOT EXISTS Reacciones (
    reaccion_id uuid NOT NULL,
    comentario_id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    emoji character varying(10) NOT NULL,
    tipo character varying(20),
    fecha_creacion timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activo boolean NOT NULL DEFAULT true
,
    PRIMARY KEY (reaccion_id)
);

-- Foreign Keys de Reacciones
ALTER TABLE Reacciones ADD CONSTRAINT Reacciones_comentario_id_fkey FOREIGN KEY (comentario_id) REFERENCES Comentario(comentario_id);
ALTER TABLE Reacciones ADD CONSTRAINT Reacciones_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Unique Constraints de Reacciones
ALTER TABLE Reacciones ADD CONSTRAINT uq_user_emoji_per_comment UNIQUE (comentario_id, usuario_id, emoji);

-- Check Constraints de Reacciones
ALTER TABLE Reacciones ADD CONSTRAINT 39558_40744_1_not_null CHECK (reaccion_id IS NOT NULL);
ALTER TABLE Reacciones ADD CONSTRAINT 39558_40744_2_not_null CHECK (comentario_id IS NOT NULL);
ALTER TABLE Reacciones ADD CONSTRAINT 39558_40744_3_not_null CHECK (usuario_id IS NOT NULL);
ALTER TABLE Reacciones ADD CONSTRAINT 39558_40744_4_not_null CHECK (emoji IS NOT NULL);
ALTER TABLE Reacciones ADD CONSTRAINT 39558_40744_6_not_null CHECK (fecha_creacion IS NOT NULL);
ALTER TABLE Reacciones ADD CONSTRAINT 39558_40744_7_not_null CHECK (activo IS NOT NULL);

-- Índices de Reacciones
CREATE INDEX idx_reacciones_comentario_usuario ON public."Reacciones" USING btree (comentario_id, usuario_id);
CREATE UNIQUE INDEX uq_user_emoji_per_comment ON public."Reacciones" USING btree (comentario_id, usuario_id, emoji);
CREATE INDEX idx_reacciones_comentario_id ON public."Reacciones" USING btree (comentario_id);
CREATE INDEX idx_reacciones_usuario_id ON public."Reacciones" USING btree (usuario_id);
CREATE INDEX idx_reacciones_emoji ON public."Reacciones" USING btree (emoji);
CREATE INDEX idx_reacciones_activo ON public."Reacciones" USING btree (activo);


============================================================

-- =====================================================
-- Tabla: Recompensa
-- =====================================================

CREATE TABLE IF NOT EXISTS Recompensa (
    recompensa_id uuid NOT NULL DEFAULT gen_random_uuid(),
    nombre character varying(100) NOT NULL,
    descripcion text,
    costo_puntos integer NOT NULL,
    tipo USER-DEFINED NOT NULL DEFAULT 'otro'::tipo_recompensa_enum
,
    PRIMARY KEY (recompensa_id)
);

-- Check Constraints de Recompensa
ALTER TABLE Recompensa ADD CONSTRAINT 39558_39667_1_not_null CHECK (recompensa_id IS NOT NULL);
ALTER TABLE Recompensa ADD CONSTRAINT 39558_39667_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Recompensa ADD CONSTRAINT 39558_39667_4_not_null CHECK (costo_puntos IS NOT NULL);
ALTER TABLE Recompensa ADD CONSTRAINT 39558_39667_5_not_null CHECK (tipo IS NOT NULL);
ALTER TABLE Recompensa ADD CONSTRAINT check_costo_puntos_positivo CHECK ((costo_puntos >= 0));


============================================================

-- =====================================================
-- Tabla: Tema
-- =====================================================

CREATE TABLE IF NOT EXISTS Tema (
    tema_id uuid NOT NULL DEFAULT gen_random_uuid(),
    nombre character varying(100) NOT NULL,
    emoji character varying(8) NOT NULL
,
    PRIMARY KEY (tema_id)
);

-- Check Constraints de Tema
ALTER TABLE Tema ADD CONSTRAINT 39558_39677_1_not_null CHECK (tema_id IS NOT NULL);
ALTER TABLE Tema ADD CONSTRAINT 39558_39677_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Tema ADD CONSTRAINT 39558_39677_3_not_null CHECK (emoji IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: TemaPersonalizado
-- =====================================================

CREATE TABLE IF NOT EXISTS TemaPersonalizado (
    tema_id uuid NOT NULL,
    usuario_id uuid
,
    PRIMARY KEY (tema_id)
);

-- Foreign Keys de TemaPersonalizado
ALTER TABLE TemaPersonalizado ADD CONSTRAINT TemaPersonalizado_tema_id_fkey FOREIGN KEY (tema_id) REFERENCES Tema(tema_id);
ALTER TABLE TemaPersonalizado ADD CONSTRAINT TemaPersonalizado_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Unique Constraints de TemaPersonalizado
ALTER TABLE TemaPersonalizado ADD CONSTRAINT uq_nombre_predefinido UNIQUE (usuario_id, tema_id);

-- Check Constraints de TemaPersonalizado
ALTER TABLE TemaPersonalizado ADD CONSTRAINT 39558_39803_1_not_null CHECK (tema_id IS NOT NULL);

-- Índices de TemaPersonalizado
CREATE UNIQUE INDEX uq_nombre_predefinido ON public."TemaPersonalizado" USING btree (usuario_id, tema_id);


============================================================

-- =====================================================
-- Tabla: TemaPredefinido
-- =====================================================

CREATE TABLE IF NOT EXISTS TemaPredefinido (
    tema_id uuid NOT NULL
,
    PRIMARY KEY (tema_id)
);

-- Foreign Keys de TemaPredefinido
ALTER TABLE TemaPredefinido ADD CONSTRAINT TemaPredefinido_tema_id_fkey FOREIGN KEY (tema_id) REFERENCES Tema(tema_id);

-- Unique Constraints de TemaPredefinido
ALTER TABLE TemaPredefinido ADD CONSTRAINT TemaPredefinido_tema_id_key UNIQUE (tema_id);

-- Check Constraints de TemaPredefinido
ALTER TABLE TemaPredefinido ADD CONSTRAINT 39558_39820_1_not_null CHECK (tema_id IS NOT NULL);

-- Índices de TemaPredefinido
CREATE UNIQUE INDEX "TemaPredefinido_tema_id_key" ON public."TemaPredefinido" USING btree (tema_id);


============================================================

-- =====================================================
-- Tabla: Usuario
-- =====================================================

CREATE TABLE IF NOT EXISTS Usuario (
    usuario_id uuid NOT NULL DEFAULT gen_random_uuid(),
    correo_institucional character varying(100),
    username character varying(50),
    nombres character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    tipo_documento USER-DEFINED NOT NULL,
    numero_documento character varying(20) NOT NULL,
    rol USER-DEFINED NOT NULL,
    password_hash character varying(255) NOT NULL,
    estado_cuenta USER-DEFINED NOT NULL DEFAULT 'activo'::estado_cuenta_usuario,
    fecha_creacion timestamp with time zone DEFAULT now(),
    ultimo_acceso timestamp with time zone DEFAULT now(),
    perfil_url text,
    portada_url text,
    telefono character varying(20),
    descripcion text,
    email_verified boolean NOT NULL DEFAULT false,
    failed_login_attempts smallint NOT NULL DEFAULT 0,
    locked_until timestamp with time zone,
    twofa_enabled boolean NOT NULL DEFAULT false,
    twofa_secret character varying(32)
,
    PRIMARY KEY (usuario_id)
);

-- Check Constraints de Usuario
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_10_not_null CHECK (estado_cuenta IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_17_not_null CHECK (email_verified IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_18_not_null CHECK (failed_login_attempts IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_1_not_null CHECK (usuario_id IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_20_not_null CHECK (twofa_enabled IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_4_not_null CHECK (nombres IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_5_not_null CHECK (apellidos IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_6_not_null CHECK (tipo_documento IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_7_not_null CHECK (numero_documento IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_8_not_null CHECK (rol IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_9_not_null CHECK (password_hash IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT chk_login CHECK ((((rol = 'administrador'::rol_usuario) AND (username IS NOT NULL) AND (correo_institucional IS NULL)) OR ((rol <> 'administrador'::rol_usuario) AND (correo_institucional IS NOT NULL) AND (username IS NULL))));

-- Índices de Usuario
CREATE INDEX idx_usuario_rol ON public."Usuario" USING btree (rol);
CREATE INDEX idx_usuario_estado_cuenta ON public."Usuario" USING btree (estado_cuenta);
CREATE INDEX idx_usuario_rol_estado ON public."Usuario" USING btree (rol, estado_cuenta);
CREATE INDEX idx_usuario_nombres_busqueda ON public."Usuario" USING gin (to_tsvector('spanish'::regconfig, (((nombres)::text || ' '::text) || (apellidos)::text)));
CREATE UNIQUE INDEX "ix_Usuario_correo_institucional" ON public."Usuario" USING btree (correo_institucional);
CREATE INDEX "ix_Usuario_numero_documento" ON public."Usuario" USING btree (numero_documento);
CREATE UNIQUE INDEX "ix_Usuario_username" ON public."Usuario" USING btree (username);
CREATE INDEX "ix_Usuario_usuario_id" ON public."Usuario" USING btree (usuario_id);


============================================================

-- =====================================================
-- Tabla: UsuarioInsignia
-- =====================================================

CREATE TABLE IF NOT EXISTS UsuarioInsignia (
    usuario_id uuid NOT NULL,
    insignia_id uuid NOT NULL,
    otorgada_por uuid,
    fecha_otorgada timestamp with time zone NOT NULL DEFAULT now()
,
    PRIMARY KEY (usuario_id, insignia_id)
);

-- Foreign Keys de UsuarioInsignia
ALTER TABLE UsuarioInsignia ADD CONSTRAINT UsuarioInsignia_insignia_id_fkey FOREIGN KEY (insignia_id) REFERENCES Insignia(insignia_id);
ALTER TABLE UsuarioInsignia ADD CONSTRAINT UsuarioInsignia_otorgada_por_fkey FOREIGN KEY (otorgada_por) REFERENCES Usuario(usuario_id);
ALTER TABLE UsuarioInsignia ADD CONSTRAINT UsuarioInsignia_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de UsuarioInsignia
ALTER TABLE UsuarioInsignia ADD CONSTRAINT 39558_39830_1_not_null CHECK (usuario_id IS NOT NULL);
ALTER TABLE UsuarioInsignia ADD CONSTRAINT 39558_39830_2_not_null CHECK (insignia_id IS NOT NULL);
ALTER TABLE UsuarioInsignia ADD CONSTRAINT 39558_39830_4_not_null CHECK (fecha_otorgada IS NOT NULL);

-- Índices de UsuarioInsignia
CREATE INDEX idx_insignias_usuario_usuario_id ON public."UsuarioInsignia" USING btree (usuario_id);


============================================================

-- =====================================================
-- Tabla: UsuarioPuntos
-- =====================================================

CREATE TABLE IF NOT EXISTS UsuarioPuntos (
    usuario_id uuid NOT NULL,
    puntos_acumulados integer NOT NULL DEFAULT 0,
    cambio integer NOT NULL,
    motivo text,
    fecha timestamp with time zone NOT NULL DEFAULT now()
,
    PRIMARY KEY (usuario_id)
);

-- Foreign Keys de UsuarioPuntos
ALTER TABLE UsuarioPuntos ADD CONSTRAINT UsuarioPuntos_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de UsuarioPuntos
ALTER TABLE UsuarioPuntos ADD CONSTRAINT 39558_39851_1_not_null CHECK (usuario_id IS NOT NULL);
ALTER TABLE UsuarioPuntos ADD CONSTRAINT 39558_39851_2_not_null CHECK (puntos_acumulados IS NOT NULL);
ALTER TABLE UsuarioPuntos ADD CONSTRAINT 39558_39851_3_not_null CHECK (cambio IS NOT NULL);
ALTER TABLE UsuarioPuntos ADD CONSTRAINT 39558_39851_5_not_null CHECK (fecha IS NOT NULL);
ALTER TABLE UsuarioPuntos ADD CONSTRAINT UsuarioPuntos_cambio_check CHECK ((cambio <> 0));

-- Índices de UsuarioPuntos
CREATE INDEX idx_usuario_puntos_usuario_id ON public."UsuarioPuntos" USING btree (usuario_id);


============================================================

-- =====================================================
-- Tabla: UsuarioRecompensa
-- =====================================================

CREATE TABLE IF NOT EXISTS UsuarioRecompensa (
    usuario_recompensa_id uuid NOT NULL,
    usuario_id uuid,
    recompensa_id uuid,
    fecha_canje timestamp with time zone DEFAULT now()
,
    PRIMARY KEY (usuario_recompensa_id)
);

-- Foreign Keys de UsuarioRecompensa
ALTER TABLE UsuarioRecompensa ADD CONSTRAINT UsuarioRecompensa_recompensa_id_fkey FOREIGN KEY (recompensa_id) REFERENCES Recompensa(recompensa_id);
ALTER TABLE UsuarioRecompensa ADD CONSTRAINT UsuarioRecompensa_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de UsuarioRecompensa
ALTER TABLE UsuarioRecompensa ADD CONSTRAINT 39558_39866_1_not_null CHECK (usuario_recompensa_id IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: ValorCalificacion
-- =====================================================

CREATE TABLE IF NOT EXISTS ValorCalificacion (
    valor_id uuid NOT NULL DEFAULT gen_random_uuid(),
    escala_id uuid NOT NULL,
    valor character varying(10) NOT NULL,
    descripcion character varying(100),
    orden smallint
,
    PRIMARY KEY (valor_id)
);

-- Foreign Keys de ValorCalificacion
ALTER TABLE ValorCalificacion ADD CONSTRAINT ValorCalificacion_escala_id_fkey FOREIGN KEY (escala_id) REFERENCES EscalaCalificacion(escala_id);

-- Check Constraints de ValorCalificacion
ALTER TABLE ValorCalificacion ADD CONSTRAINT 39558_40148_1_not_null CHECK (valor_id IS NOT NULL);
ALTER TABLE ValorCalificacion ADD CONSTRAINT 39558_40148_2_not_null CHECK (escala_id IS NOT NULL);
ALTER TABLE ValorCalificacion ADD CONSTRAINT 39558_40148_3_not_null CHECK (valor IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: avatar_asset
-- =====================================================

CREATE TABLE IF NOT EXISTS avatar_asset (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    category character varying(50) NOT NULL,
    filename character varying(255) NOT NULL,
    display_name character varying(100),
    file_size integer NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    meta_info json,
    is_active character varying(1) NOT NULL DEFAULT 'Y'::character varying,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    target_gender character varying(20) NOT NULL DEFAULT 'unisex'::character varying
,
    PRIMARY KEY (id)
);

-- Unique Constraints de avatar_asset
ALTER TABLE avatar_asset ADD CONSTRAINT avatar_asset_filename_key UNIQUE (filename);

-- Check Constraints de avatar_asset
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_10_not_null CHECK (created_at IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_11_not_null CHECK (updated_at IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_12_not_null CHECK (target_gender IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_1_not_null CHECK (id IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_2_not_null CHECK (category IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_3_not_null CHECK (filename IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_5_not_null CHECK (file_size IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_6_not_null CHECK (width IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_7_not_null CHECK (height IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_9_not_null CHECK (is_active IS NOT NULL);

-- Índices de avatar_asset
CREATE UNIQUE INDEX avatar_asset_filename_key ON public.avatar_asset USING btree (filename);
CREATE INDEX ix_avatar_asset_id ON public.avatar_asset USING btree (id);
CREATE INDEX ix_avatar_asset_category ON public.avatar_asset USING btree (category);
CREATE INDEX ix_avatar_asset_target_gender ON public.avatar_asset USING btree (target_gender);


============================================================

-- =====================================================
-- Tabla: banco_preguntas
-- =====================================================

CREATE TABLE IF NOT EXISTS banco_preguntas (
    pregunta_id character varying NOT NULL,
    titulo text NOT NULL,
    descripcion text,
    tipo_pregunta character varying(50) NOT NULL,
    dificultad character varying(50) DEFAULT 'medio'::character varying,
    materia character varying(100),
    tema character varying(200),
    subtema character varying(200),
    opciones_respuesta json,
    respuesta_correcta json,
    explicacion text,
    imagen_url character varying(500),
    audio_url character varying(500),
    video_url character varying(500),
    archivos_adjuntos json,
    creado_por character varying NOT NULL,
    institucion_id character varying,
    es_publica boolean DEFAULT false,
    tags json,
    categoria character varying(100),
    nivel_educativo character varying(50),
    puntuacion_sugerida double precision DEFAULT '1'::double precision,
    tiempo_estimado_segundos integer,
    veces_utilizada integer DEFAULT 0,
    promedio_aciertos double precision,
    calificacion_dificultad double precision,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    ultima_vez_utilizada timestamp with time zone,
    revisado_por character varying,
    fecha_revision timestamp with time zone,
    estado_revision character varying(50) DEFAULT 'pendiente'::character varying,
    comentarios_revision text
,
    PRIMARY KEY (pregunta_id)
);

-- Check Constraints de banco_preguntas
ALTER TABLE banco_preguntas ADD CONSTRAINT 39558_40811_16_not_null CHECK (creado_por IS NOT NULL);
ALTER TABLE banco_preguntas ADD CONSTRAINT 39558_40811_1_not_null CHECK (pregunta_id IS NOT NULL);
ALTER TABLE banco_preguntas ADD CONSTRAINT 39558_40811_2_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE banco_preguntas ADD CONSTRAINT 39558_40811_4_not_null CHECK (tipo_pregunta IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: configuracion_evaluaciones
-- =====================================================

CREATE TABLE IF NOT EXISTS configuracion_evaluaciones (
    config_id character varying NOT NULL,
    tiempo_gracia_segundos integer DEFAULT 300,
    maximo_intentos_globales integer DEFAULT 5,
    tiempo_minimo_entre_intentos integer DEFAULT 3600,
    max_cambios_pestana_permitidos integer DEFAULT 5,
    tiempo_max_inactividad_global integer DEFAULT 1800,
    habilitar_deteccion_copia_texto boolean DEFAULT true,
    habilitar_deteccion_pantalla_completa boolean DEFAULT true,
    algoritmo_calificacion_ensayos character varying(100) DEFAULT 'keyword_matching'::character varying,
    umbral_similitud_plagio double precision DEFAULT '0.8'::double precision,
    habilitar_feedback_automatico boolean DEFAULT true,
    notificar_intento_finalizado boolean DEFAULT true,
    notificar_resultado_disponible boolean DEFAULT true,
    notificar_tiempo_restante boolean DEFAULT true,
    tiempo_notificacion_previa_minutos integer DEFAULT 10,
    guardar_progreso_cada_segundos integer DEFAULT 30,
    habilitar_recuperacion_sesion boolean DEFAULT true,
    tiempo_expiracion_backup_horas integer DEFAULT 72,
    institucion_id character varying,
    aplicar_globalmente boolean DEFAULT true,
    creado_por character varying NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone
,
    PRIMARY KEY (config_id)
);

-- Check Constraints de configuracion_evaluaciones
ALTER TABLE configuracion_evaluaciones ADD CONSTRAINT 39558_40867_1_not_null CHECK (config_id IS NOT NULL);
ALTER TABLE configuracion_evaluaciones ADD CONSTRAINT 39558_40867_21_not_null CHECK (creado_por IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: entregas_tareas
-- =====================================================

CREATE TABLE IF NOT EXISTS entregas_tareas (
    entrega_id character varying NOT NULL,
    tarea_id character varying NOT NULL,
    estudiante_id uuid NOT NULL,
    titulo_entrega character varying(200),
    descripcion_entrega text,
    comentarios_estudiante text,
    archivo_url character varying(500),
    archivos_adicionales json,
    contenido_texto text,
    enlaces_externos json,
    fecha_entrega timestamp with time zone,
    fecha_limite_original timestamp with time zone,
    numero_intento integer,
    es_entrega_tardia boolean,
    calificacion double precision,
    calificacion_letras character varying(5),
    comentarios_docente text,
    rubrica_calificacion json,
    estado character varying(50),
    es_final boolean,
    requiere_revision boolean,
    tiempo_empleado integer,
    dificultad_percibida integer,
    satisfaccion_estudiante integer,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    calificado_por uuid,
    fecha_calificacion timestamp with time zone
,
    PRIMARY KEY (entrega_id)
);

-- Foreign Keys de entregas_tareas
ALTER TABLE entregas_tareas ADD CONSTRAINT entregas_tareas_calificado_por_fkey FOREIGN KEY (calificado_por) REFERENCES Usuario(usuario_id);
ALTER TABLE entregas_tareas ADD CONSTRAINT entregas_tareas_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES Usuario(usuario_id);
ALTER TABLE entregas_tareas ADD CONSTRAINT entregas_tareas_tarea_id_fkey FOREIGN KEY (tarea_id) REFERENCES tareas(tarea_id);

-- Check Constraints de entregas_tareas
ALTER TABLE entregas_tareas ADD CONSTRAINT 39558_40582_1_not_null CHECK (entrega_id IS NOT NULL);
ALTER TABLE entregas_tareas ADD CONSTRAINT 39558_40582_2_not_null CHECK (tarea_id IS NOT NULL);
ALTER TABLE entregas_tareas ADD CONSTRAINT 39558_40582_3_not_null CHECK (estudiante_id IS NOT NULL);

-- Índices de entregas_tareas
CREATE INDEX idx_entregas_tarea_id ON public.entregas_tareas USING btree (tarea_id);
CREATE INDEX idx_entregas_estudiante_id ON public.entregas_tareas USING btree (estudiante_id);
CREATE INDEX idx_entregas_estado ON public.entregas_tareas USING btree (estado);


============================================================

-- =====================================================
-- Tabla: estadisticas_examen
-- =====================================================

CREATE TABLE IF NOT EXISTS estadisticas_examen (
    estadistica_id character varying NOT NULL,
    examen_id character varying NOT NULL,
    total_estudiantes_asignados integer DEFAULT 0,
    total_intentos_realizados integer DEFAULT 0,
    total_intentos_finalizados integer DEFAULT 0,
    total_aprobados integer DEFAULT 0,
    total_reprobados integer DEFAULT 0,
    puntuacion_promedio double precision DEFAULT '0'::double precision,
    puntuacion_mediana double precision DEFAULT '0'::double precision,
    puntuacion_maxima_obtenida double precision DEFAULT '0'::double precision,
    puntuacion_minima_obtenida double precision DEFAULT '0'::double precision,
    desviacion_estandar double precision DEFAULT '0'::double precision,
    tiempo_promedio_minutos double precision DEFAULT '0'::double precision,
    tiempo_maximo_empleado integer DEFAULT 0,
    tiempo_minimo_empleado integer DEFAULT 0,
    estadisticas_preguntas json,
    preguntas_mas_dificiles json,
    preguntas_mas_faciles json,
    patrones_abandono json,
    tiempo_por_pregunta json,
    fecha_calculo timestamp with time zone DEFAULT now(),
    fecha_ultima_actualizacion timestamp with time zone,
    incluir_intentos_incompletos boolean DEFAULT false,
    periodo_calculo character varying(50) DEFAULT 'completo'::character varying
,
    PRIMARY KEY (estadistica_id)
);

-- Foreign Keys de estadisticas_examen
ALTER TABLE estadisticas_examen ADD CONSTRAINT estadisticas_examen_examen_id_fkey FOREIGN KEY (examen_id) REFERENCES examenes(examen_id);

-- Check Constraints de estadisticas_examen
ALTER TABLE estadisticas_examen ADD CONSTRAINT 39558_40893_1_not_null CHECK (estadistica_id IS NOT NULL);
ALTER TABLE estadisticas_examen ADD CONSTRAINT 39558_40893_2_not_null CHECK (examen_id IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: eventos_anti_trampa
-- =====================================================

CREATE TABLE IF NOT EXISTS eventos_anti_trampa (
    evento_id character varying NOT NULL,
    intento_id character varying NOT NULL,
    tipo_evento character varying(50) NOT NULL,
    descripcion text,
    datos_evento json,
    ip_address character varying(45),
    user_agent text,
    timestamp timestamp with time zone DEFAULT now(),
    es_sospechoso boolean DEFAULT false,
    nivel_riesgo character varying(20) DEFAULT 'bajo'::character varying,
    requiere_revision boolean DEFAULT false
,
    PRIMARY KEY (evento_id)
);

-- Foreign Keys de eventos_anti_trampa
ALTER TABLE eventos_anti_trampa ADD CONSTRAINT eventos_anti_trampa_intento_id_fkey FOREIGN KEY (intento_id) REFERENCES intentos_examen(intento_id);

-- Check Constraints de eventos_anti_trampa
ALTER TABLE eventos_anti_trampa ADD CONSTRAINT 39558_40921_1_not_null CHECK (evento_id IS NOT NULL);
ALTER TABLE eventos_anti_trampa ADD CONSTRAINT 39558_40921_2_not_null CHECK (intento_id IS NOT NULL);
ALTER TABLE eventos_anti_trampa ADD CONSTRAINT 39558_40921_3_not_null CHECK (tipo_evento IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: examenes
-- =====================================================

CREATE TABLE IF NOT EXISTS examenes (
    examen_id character varying NOT NULL,
    titulo character varying(200) NOT NULL,
    descripcion text,
    tipo_examen character varying(50) NOT NULL DEFAULT 'evaluacion'::character varying,
    estado_examen character varying(50) NOT NULL DEFAULT 'borrador'::character varying,
    tiempo_limite integer NOT NULL DEFAULT 60,
    fecha_inicio timestamp with time zone,
    fecha_limite timestamp with time zone,
    intentos_permitidos integer DEFAULT 1,
    requiere_contraseña boolean DEFAULT false,
    contraseña_acceso character varying(100),
    randomizar_preguntas boolean DEFAULT false,
    mostrar_resultados_inmediatos boolean DEFAULT true,
    permitir_revision boolean DEFAULT true,
    mostrar_respuestas_correctas boolean DEFAULT true,
    modo_pantalla_completa boolean DEFAULT false,
    bloquear_navegacion boolean DEFAULT false,
    detectar_cambio_pestana boolean DEFAULT false,
    tiempo_maximo_inactividad integer DEFAULT 300,
    puntuacion_total double precision NOT NULL DEFAULT '100'::double precision,
    puntuacion_minima_aprobacion double precision DEFAULT '60'::double precision,
    calificacion_automatica boolean DEFAULT true,
    curso_id character varying,
    grupo_id character varying,
    creado_por character varying NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    configuracion_avanzada json,
    instrucciones text,
    total_preguntas integer DEFAULT 0,
    total_intentos integer DEFAULT 0,
    promedio_calificacion double precision
,
    PRIMARY KEY (examen_id)
);

-- Check Constraints de examenes
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_1_not_null CHECK (examen_id IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_20_not_null CHECK (puntuacion_total IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_25_not_null CHECK (creado_por IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_2_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_4_not_null CHECK (tipo_examen IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_5_not_null CHECK (estado_examen IS NOT NULL);
ALTER TABLE examenes ADD CONSTRAINT 39558_40767_6_not_null CHECK (tiempo_limite IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: intentos_examen
-- =====================================================

CREATE TABLE IF NOT EXISTS intentos_examen (
    intento_id character varying NOT NULL,
    examen_id character varying NOT NULL,
    estudiante_id character varying NOT NULL,
    numero_intento integer NOT NULL,
    estado_intento character varying(50) NOT NULL DEFAULT 'en_progreso'::character varying,
    fecha_inicio timestamp with time zone DEFAULT now(),
    fecha_fin timestamp with time zone,
    tiempo_total_segundos integer,
    tiempo_limite_vencido boolean DEFAULT false,
    puntuacion_obtenida double precision DEFAULT '0'::double precision,
    puntuacion_maxima double precision NOT NULL,
    porcentaje double precision,
    aprobado boolean,
    preguntas_respondidas integer DEFAULT 0,
    total_preguntas integer NOT NULL,
    pregunta_actual integer DEFAULT 1,
    cambios_pestana_detectados integer DEFAULT 0,
    tiempo_inactividad_total integer DEFAULT 0,
    ip_address character varying(45),
    user_agent text,
    eventos_sospechosos json,
    orden_preguntas json,
    configuracion_intento json,
    finalizado_por character varying(50) DEFAULT 'estudiante'::character varying,
    comentarios_finalizacion text,
    fecha_revision timestamp with time zone,
    revisado_por character varying,
    comentarios_profesor text
,
    PRIMARY KEY (intento_id)
);

-- Foreign Keys de intentos_examen
ALTER TABLE intentos_examen ADD CONSTRAINT intentos_examen_examen_id_fkey FOREIGN KEY (examen_id) REFERENCES examenes(examen_id);

-- Check Constraints de intentos_examen
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_11_not_null CHECK (puntuacion_maxima IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_15_not_null CHECK (total_preguntas IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_1_not_null CHECK (intento_id IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_2_not_null CHECK (examen_id IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_3_not_null CHECK (estudiante_id IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_4_not_null CHECK (numero_intento IS NOT NULL);
ALTER TABLE intentos_examen ADD CONSTRAINT 39558_40824_5_not_null CHECK (estado_intento IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: mensajes
-- =====================================================

CREATE TABLE IF NOT EXISTS mensajes (
    id uuid NOT NULL,
    sala_id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    contenido text,
    contenido_html text,
    tipo_mensaje character varying(50),
    archivos_urls json,
    metadatos_archivos json,
    mensaje_padre_id uuid,
    tiene_respuestas boolean,
    numero_respuestas integer,
    menciones_usuarios json,
    menciones_ia boolean,
    menciones_todos boolean,
    estado character varying(50),
    fecha_creacion timestamp without time zone DEFAULT now(),
    fecha_actualizacion timestamp without time zone,
    fecha_eliminacion timestamp without time zone,
    reacciones json,
    es_importante boolean,
    es_anuncio boolean
,
    PRIMARY KEY (id)
);

-- Foreign Keys de mensajes
ALTER TABLE mensajes ADD CONSTRAINT mensajes_sala_id_fkey FOREIGN KEY (sala_id) REFERENCES salas_chat(id);
ALTER TABLE mensajes ADD CONSTRAINT mensajes_mensaje_padre_id_fkey FOREIGN KEY (mensaje_padre_id) REFERENCES mensajes(id);

-- Check Constraints de mensajes
ALTER TABLE mensajes ADD CONSTRAINT 39558_40661_1_not_null CHECK (id IS NOT NULL);
ALTER TABLE mensajes ADD CONSTRAINT 39558_40661_2_not_null CHECK (sala_id IS NOT NULL);
ALTER TABLE mensajes ADD CONSTRAINT 39558_40661_3_not_null CHECK (usuario_id IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: notificaciones
-- =====================================================

CREATE TABLE IF NOT EXISTS notificaciones (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    titulo character varying(255) NOT NULL,
    mensaje text,
    tipo_notificacion character varying(50),
    sala_id uuid,
    mensaje_id uuid,
    tarea_id uuid,
    curso_id uuid,
    leida boolean,
    enviada_email boolean,
    enviada_push boolean,
    fecha_creacion timestamp without time zone DEFAULT now(),
    fecha_lectura timestamp without time zone,
    fecha_envio_email timestamp without time zone,
    datos_adicionales json,
    url_accion character varying(500),
    icono character varying(100),
    color character varying(7)
,
    PRIMARY KEY (id)
);

-- Foreign Keys de notificaciones
ALTER TABLE notificaciones ADD CONSTRAINT notificaciones_sala_id_fkey FOREIGN KEY (sala_id) REFERENCES salas_chat(id);
ALTER TABLE notificaciones ADD CONSTRAINT notificaciones_mensaje_id_fkey FOREIGN KEY (mensaje_id) REFERENCES mensajes(id);

-- Check Constraints de notificaciones
ALTER TABLE notificaciones ADD CONSTRAINT 39558_40679_1_not_null CHECK (id IS NOT NULL);
ALTER TABLE notificaciones ADD CONSTRAINT 39558_40679_2_not_null CHECK (usuario_id IS NOT NULL);
ALTER TABLE notificaciones ADD CONSTRAINT 39558_40679_3_not_null CHECK (titulo IS NOT NULL);

-- Índices de notificaciones
CREATE INDEX idx_notificaciones_usuario_id ON public.notificaciones USING btree (usuario_id);
CREATE INDEX idx_notificaciones_leida ON public.notificaciones USING btree (leida);
CREATE INDEX idx_notificaciones_usuario_leida_fecha ON public.notificaciones USING btree (usuario_id, leida, fecha_creacion DESC);
CREATE INDEX idx_notificaciones_tipo ON public.notificaciones USING btree (tipo_notificacion) WHERE (tipo_notificacion IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: preguntas_examen
-- =====================================================

CREATE TABLE IF NOT EXISTS preguntas_examen (
    pregunta_id character varying NOT NULL,
    examen_id character varying NOT NULL,
    titulo text NOT NULL,
    descripcion text,
    tipo_pregunta character varying(50) NOT NULL,
    orden integer NOT NULL,
    puntuacion double precision NOT NULL DEFAULT '1'::double precision,
    es_obligatoria boolean DEFAULT true,
    tiempo_limite_segundos integer,
    opciones_respuesta json,
    respuesta_correcta json,
    explicacion text,
    puntos_respuesta_parcial boolean DEFAULT false,
    dificultad character varying(50) DEFAULT 'medio'::character varying,
    imagen_url character varying(500),
    audio_url character varying(500),
    video_url character varying(500),
    archivos_adjuntos json,
    banco_pregunta_id character varying,
    tags json,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    veces_utilizada integer DEFAULT 0,
    promedio_aciertos double precision,
    tiempo_promedio_respuesta double precision
,
    PRIMARY KEY (pregunta_id)
);

-- Foreign Keys de preguntas_examen
ALTER TABLE preguntas_examen ADD CONSTRAINT preguntas_examen_examen_id_fkey FOREIGN KEY (examen_id) REFERENCES examenes(examen_id);
ALTER TABLE preguntas_examen ADD CONSTRAINT fk_preguntas_examen_banco_pregunta_id FOREIGN KEY (banco_pregunta_id) REFERENCES banco_preguntas(pregunta_id);

-- Check Constraints de preguntas_examen
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_1_not_null CHECK (pregunta_id IS NOT NULL);
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_2_not_null CHECK (examen_id IS NOT NULL);
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_3_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_5_not_null CHECK (tipo_pregunta IS NOT NULL);
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_6_not_null CHECK (orden IS NOT NULL);
ALTER TABLE preguntas_examen ADD CONSTRAINT 39558_40793_7_not_null CHECK (puntuacion IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: respuestas_estudiante
-- =====================================================

CREATE TABLE IF NOT EXISTS respuestas_estudiante (
    respuesta_id character varying NOT NULL,
    intento_id character varying NOT NULL,
    pregunta_id character varying NOT NULL,
    respuesta_estudiante json,
    texto_respuesta text,
    puntuacion_obtenida double precision DEFAULT '0'::double precision,
    puntuacion_maxima double precision NOT NULL,
    es_correcta boolean,
    calificada_automaticamente boolean DEFAULT false,
    fecha_respuesta timestamp with time zone DEFAULT now(),
    tiempo_empleado_segundos integer,
    fecha_ultima_modificacion timestamp with time zone,
    historial_respuestas json,
    numero_modificaciones integer DEFAULT 0,
    feedback_automatico text,
    feedback_profesor text,
    mostrar_respuesta_correcta boolean DEFAULT false,
    palabras_clave_encontradas json,
    similitud_respuesta_correcta double precision,
    version_pregunta character varying(50),
    metadata_respuesta json
,
    PRIMARY KEY (respuesta_id)
);

-- Foreign Keys de respuestas_estudiante
ALTER TABLE respuestas_estudiante ADD CONSTRAINT respuestas_estudiante_intento_id_fkey FOREIGN KEY (intento_id) REFERENCES intentos_examen(intento_id);
ALTER TABLE respuestas_estudiante ADD CONSTRAINT respuestas_estudiante_pregunta_id_fkey FOREIGN KEY (pregunta_id) REFERENCES preguntas_examen(pregunta_id);

-- Check Constraints de respuestas_estudiante
ALTER TABLE respuestas_estudiante ADD CONSTRAINT 39558_40845_1_not_null CHECK (respuesta_id IS NOT NULL);
ALTER TABLE respuestas_estudiante ADD CONSTRAINT 39558_40845_2_not_null CHECK (intento_id IS NOT NULL);
ALTER TABLE respuestas_estudiante ADD CONSTRAINT 39558_40845_3_not_null CHECK (pregunta_id IS NOT NULL);
ALTER TABLE respuestas_estudiante ADD CONSTRAINT 39558_40845_7_not_null CHECK (puntuacion_maxima IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: rubricas
-- =====================================================

CREATE TABLE IF NOT EXISTS rubricas (
    rubrica_id character varying NOT NULL,
    nombre character varying(200) NOT NULL,
    descripcion text,
    criterios json NOT NULL,
    puntuacion_total double precision NOT NULL,
    es_publica boolean,
    es_plantilla boolean,
    activa boolean,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    creado_por character varying NOT NULL
,
    PRIMARY KEY (rubrica_id)
);

-- Check Constraints de rubricas
ALTER TABLE rubricas ADD CONSTRAINT 39558_40537_11_not_null CHECK (creado_por IS NOT NULL);
ALTER TABLE rubricas ADD CONSTRAINT 39558_40537_1_not_null CHECK (rubrica_id IS NOT NULL);
ALTER TABLE rubricas ADD CONSTRAINT 39558_40537_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE rubricas ADD CONSTRAINT 39558_40537_4_not_null CHECK (criterios IS NOT NULL);
ALTER TABLE rubricas ADD CONSTRAINT 39558_40537_5_not_null CHECK (puntuacion_total IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: salas_chat
-- =====================================================

CREATE TABLE IF NOT EXISTS salas_chat (
    id uuid NOT NULL,
    nombre character varying(255) NOT NULL,
    descripcion text,
    tipo_sala character varying(50) NOT NULL,
    curso_id uuid,
    grupo_id uuid,
    tarea_id uuid,
    es_publica boolean,
    permite_archivos boolean,
    permite_menciones boolean,
    permite_hilos boolean,
    moderacion_activa boolean,
    creador_id uuid NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now(),
    fecha_actualizacion timestamp without time zone,
    ultimo_mensaje_fecha timestamp without time zone,
    configuracion_json json,
    tags character varying(500)
,
    PRIMARY KEY (id)
);

-- Check Constraints de salas_chat
ALTER TABLE salas_chat ADD CONSTRAINT 39558_40653_13_not_null CHECK (creador_id IS NOT NULL);
ALTER TABLE salas_chat ADD CONSTRAINT 39558_40653_1_not_null CHECK (id IS NOT NULL);
ALTER TABLE salas_chat ADD CONSTRAINT 39558_40653_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE salas_chat ADD CONSTRAINT 39558_40653_4_not_null CHECK (tipo_sala IS NOT NULL);


============================================================

-- =====================================================
-- Tabla: tareas
-- =====================================================

CREATE TABLE IF NOT EXISTS tareas (
    tarea_id character varying NOT NULL,
    docente_id uuid NOT NULL,
    titulo character varying(200) NOT NULL,
    descripcion text,
    instrucciones text,
    objetivos text,
    tipo_tarea USER-DEFINED NOT NULL DEFAULT 'ensayo'::tipo_tarea,
    prioridad USER-DEFINED NOT NULL DEFAULT 'media'::prioridad_tarea,
    grupo_id uuid NOT NULL,
    tags character varying(500),
    fecha_asignacion timestamp with time zone DEFAULT now(),
    fecha_limite timestamp with time zone NOT NULL,
    fecha_inicio_disponible timestamp with time zone,
    tiempo_estimado integer,
    permite_entrega_tardia boolean,
    penalizacion_tardia double precision,
    intentos_maximos integer,
    formato_entrega character varying(200),
    tamano_maximo_mb double precision,
    puntuacion_maxima double precision NOT NULL,
    peso_evaluacion double precision,
    rubrica_id character varying,
    estado USER-DEFINED NOT NULL DEFAULT 'asignada'::estado_tarea,
    es_grupal boolean,
    es_publica boolean,
    requiere_aprobacion boolean,
    configuracion_json json,
    recursos_necesarios text,
    criterios_evaluacion text,
    activa boolean,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    creado_por uuid,
    actualizado_por uuid
,
    PRIMARY KEY (tarea_id)
);

-- Foreign Keys de tareas
ALTER TABLE tareas ADD CONSTRAINT tareas_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES Usuario(usuario_id);
ALTER TABLE tareas ADD CONSTRAINT tareas_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES Usuario(usuario_id);
ALTER TABLE tareas ADD CONSTRAINT tareas_docente_id_fkey FOREIGN KEY (docente_id) REFERENCES Usuario(usuario_id);
ALTER TABLE tareas ADD CONSTRAINT tareas_grupo_id_fkey FOREIGN KEY (grupo_id) REFERENCES Grupo(grupo_id);
ALTER TABLE tareas ADD CONSTRAINT tareas_rubrica_id_fkey FOREIGN KEY (rubrica_id) REFERENCES rubricas(rubrica_id);

-- Check Constraints de tareas
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_12_not_null CHECK (fecha_limite IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_1_not_null CHECK (tarea_id IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_20_not_null CHECK (puntuacion_maxima IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_23_not_null CHECK (estado IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_2_not_null CHECK (docente_id IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_3_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_7_not_null CHECK (tipo_tarea IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_8_not_null CHECK (prioridad IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_9_not_null CHECK (grupo_id IS NOT NULL);

-- Índices de tareas
CREATE INDEX idx_tareas_grupo_id ON public.tareas USING btree (grupo_id);
CREATE INDEX idx_tareas_docente_id ON public.tareas USING btree (docente_id);
CREATE INDEX idx_tareas_fecha_limite ON public.tareas USING btree (fecha_limite);
CREATE INDEX idx_tareas_estado ON public.tareas USING btree (estado);


============================================================

-- =====================================================
-- Tabla: user_avatar
-- =====================================================

CREATE TABLE IF NOT EXISTS user_avatar (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    layers json NOT NULL,
    image_url character varying(500) NOT NULL,
    layers_hash character varying(64) NOT NULL,
    is_active boolean NOT NULL DEFAULT false,
    is_public boolean NOT NULL DEFAULT true,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    base_gender character varying(20) NOT NULL DEFAULT 'male'::character varying
,
    PRIMARY KEY (id)
);

-- Foreign Keys de user_avatar
ALTER TABLE user_avatar ADD CONSTRAINT user_avatar_user_id_fkey FOREIGN KEY (user_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de user_avatar
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_10_not_null CHECK (updated_at IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_11_not_null CHECK (base_gender IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_1_not_null CHECK (id IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_2_not_null CHECK (user_id IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_3_not_null CHECK (name IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_4_not_null CHECK (layers IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_5_not_null CHECK (image_url IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_6_not_null CHECK (layers_hash IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_7_not_null CHECK (is_active IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_8_not_null CHECK (is_public IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_9_not_null CHECK (created_at IS NOT NULL);

-- Índices de user_avatar
CREATE INDEX ix_user_avatar_id ON public.user_avatar USING btree (id);
CREATE INDEX ix_user_avatar_user_id ON public.user_avatar USING btree (user_id);
CREATE INDEX ix_user_avatar_layers_hash ON public.user_avatar USING btree (layers_hash);


============================================================
