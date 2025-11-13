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
