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
