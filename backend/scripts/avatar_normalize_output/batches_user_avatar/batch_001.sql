-- user_avatar updates generated from mapping CSV
-- These updates rebuild the `layers` JSON replacing basenames with canonical paths.
-- Review and test in staging before applying to production.

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = '167 sin título_20250922233558.png' THEN jsonb_set(elem, '{file}', to_jsonb('base/167 sin título_20250922233558.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = '167 sin título_20250922233558.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = '167 sin título_20250922233558.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = '167 sin título_20250923002534.png' THEN jsonb_set(elem, '{file}', to_jsonb('base/167 sin título_20250923002534.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = '167 sin título_20250923002534.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = '167 sin título_20250923002534.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = '167 sin título_20250923002615.png' THEN jsonb_set(elem, '{file}', to_jsonb('base/167 sin título_20250923002615.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = '167 sin título_20250923002615.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = '167 sin título_20250923002615.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = '167 sin título_20250922233650.png' THEN jsonb_set(elem, '{file}', to_jsonb('base/167 sin título_20250922233650.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = '167 sin título_20250922233650.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = '167 sin título_20250922233650.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'bg_002.png' THEN jsonb_set(elem, '{file}', to_jsonb('backgrounds/unisex/bg_002.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'bg_002.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'bg_002.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'ojos_6.png' THEN jsonb_set(elem, '{file}', to_jsonb('eyes/female/ojos_6.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'ojos_6.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'ojos_6.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'ojos_5.png' THEN jsonb_set(elem, '{file}', to_jsonb('eyes/female/ojos_5.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'ojos_5.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'ojos_5.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'ojos_4.png' THEN jsonb_set(elem, '{file}', to_jsonb('eyes/female/ojos_4.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'ojos_4.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'ojos_4.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'camisa_cafe_mujer.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/unisex/camisa_cafe_mujer.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'camisa_cafe_mujer.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'camisa_cafe_mujer.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'Medias_maya.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/Medias_maya.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Medias_maya.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Medias_maya.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'camisa_miku.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/camisa_miku.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'camisa_miku.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'camisa_miku.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'vestido.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/vestido.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'vestido.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'vestido.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'Camisa_morada_mujer.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/Camisa_morada_mujer.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Camisa_morada_mujer.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Camisa_morada_mujer.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'zapatos_beige.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/zapatos_beige.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'zapatos_beige.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'zapatos_beige.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'Camisa_verde_mujer.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/Camisa_verde_mujer.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Camisa_verde_mujer.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Camisa_verde_mujer.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'Corset_rojo.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/Corset_rojo.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Corset_rojo.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Corset_rojo.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'esqueleto_azul.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/esqueleto_azul.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'esqueleto_azul.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'esqueleto_azul.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'falda_miku.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/falda_miku.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'falda_miku.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'falda_miku.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'falda_2.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/falda_2.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'falda_2.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'falda_2.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'camisa_cafe.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/camisa_cafe.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'camisa_cafe.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'camisa_cafe.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'esqueleto_blanco_mujer.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/esqueleto_blanco_mujer.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'esqueleto_blanco_mujer.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'esqueleto_blanco_mujer.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'zapatos_rosados.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/zapatos_rosados.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'zapatos_rosados.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'zapatos_rosados.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'calentadoras.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/calentadoras.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'calentadoras.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'calentadoras.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'Camisa_roja_mujer.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/Camisa_roja_mujer.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Camisa_roja_mujer.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Camisa_roja_mujer.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'Camisa_negra_mujer.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/Camisa_negra_mujer.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Camisa_negra_mujer.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'Camisa_negra_mujer.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'camisa_elegante_mujer.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/camisa_elegante_mujer.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'camisa_elegante_mujer.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'camisa_elegante_mujer.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'falda_blanca.png' THEN jsonb_set(elem, '{file}', to_jsonb('clothes/female/falda_blanca.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'falda_blanca.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'falda_blanca.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'hair_4.png' THEN jsonb_set(elem, '{file}', to_jsonb('hair/female/hair_4.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'hair_4.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'hair_4.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'hair_2.png' THEN jsonb_set(elem, '{file}', to_jsonb('hair/female/hair_2.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'hair_2.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'hair_2.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'hair_1.png' THEN jsonb_set(elem, '{file}', to_jsonb('hair/female/hair_1.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'hair_1.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'hair_1.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'hair_3.png' THEN jsonb_set(elem, '{file}', to_jsonb('hair/female/hair_3.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'hair_3.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'hair_3.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'manilla_1.png' THEN jsonb_set(elem, '{file}', to_jsonb('accessories/unisex/manilla_1.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'manilla_1.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'manilla_1.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'collar_1.png' THEN jsonb_set(elem, '{file}', to_jsonb('accessories/female/collar_1.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'collar_1.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'collar_1.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'manilla_2.png' THEN jsonb_set(elem, '{file}', to_jsonb('accessories/female/manilla_2.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'manilla_2.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'manilla_2.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'moño.png' THEN jsonb_set(elem, '{file}', to_jsonb('accessories/female/moño.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'moño.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'moño.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'gafas_2.png' THEN jsonb_set(elem, '{file}', to_jsonb('accessories/female/gafas_2.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'gafas_2.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'gafas_2.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'orejas_gato.png' THEN jsonb_set(elem, '{file}', to_jsonb('accessories/female/orejas_gato.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'orejas_gato.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'orejas_gato.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'rubor.png' THEN jsonb_set(elem, '{file}', to_jsonb('makeup/female/rubor.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'rubor.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'rubor.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'ahumado_morado.png' THEN jsonb_set(elem, '{file}', to_jsonb('makeup/female/ahumado_morado.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'ahumado_morado.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'ahumado_morado.png');
COMMIT;
