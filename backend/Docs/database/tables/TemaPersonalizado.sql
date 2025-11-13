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
