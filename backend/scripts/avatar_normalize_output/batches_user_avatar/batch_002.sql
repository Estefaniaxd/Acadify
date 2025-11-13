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
