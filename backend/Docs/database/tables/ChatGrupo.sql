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
