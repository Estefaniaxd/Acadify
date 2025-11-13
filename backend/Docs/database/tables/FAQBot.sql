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
