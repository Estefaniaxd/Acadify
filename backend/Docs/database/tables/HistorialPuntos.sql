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
