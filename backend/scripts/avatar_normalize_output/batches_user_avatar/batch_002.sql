BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'ahumado_negro.png' THEN jsonb_set(elem, '{file}', to_jsonb('makeup/female/ahumado_negro.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'ahumado_negro.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'ahumado_negro.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'remolino_rubor.png' THEN jsonb_set(elem, '{file}', to_jsonb('makeup/female/remolino_rubor.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'remolino_rubor.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'remolino_rubor.png');
COMMIT;

BEGIN;
UPDATE user_avatar
SET layers = (
  SELECT jsonb_agg(
    CASE WHEN elem->>'file' = 'boca_3.png' THEN jsonb_set(elem, '{file}', to_jsonb('mouth/female/boca_3.png'::text)) ELSE elem END
  )
  FROM jsonb_array_elements(layers::jsonb) elem
)
WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'boca_3.png');
-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'boca_3.png');
COMMIT;
