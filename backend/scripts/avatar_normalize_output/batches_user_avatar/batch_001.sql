-- user_avatar updates generated from mapping CSV
-- These updates rebuild the `layers` JSON replacing basenames with canonical paths.
-- Review and test in staging before applying to production.

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
