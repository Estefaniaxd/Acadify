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
