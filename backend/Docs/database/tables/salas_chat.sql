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
