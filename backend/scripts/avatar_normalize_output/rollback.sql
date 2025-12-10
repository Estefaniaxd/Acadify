BEGIN;
UPDATE avatar_asset SET filename = 'unisex/pantaloneta_morada.png' WHERE id = 32db60b9-d020-4d0b-bfb8-39e9cd71b5d6;
-- Verify: SELECT id, filename FROM avatar_asset WHERE id = 32db60b9-d020-4d0b-bfb8-39e9cd71b5d6;
COMMIT;

BEGIN;
UPDATE avatar_asset SET filename = 'unisex/medias_negras.png' WHERE id = da060d63-de3f-4a56-b85d-653a1f689134;
-- Verify: SELECT id, filename FROM avatar_asset WHERE id = da060d63-de3f-4a56-b85d-653a1f689134;
COMMIT;

BEGIN;
UPDATE avatar_asset SET filename = 'unisex/chaqueta_y2k.png' WHERE id = d8a9f44f-ef0f-4e39-b483-5604b970f254;
-- Verify: SELECT id, filename FROM avatar_asset WHERE id = d8a9f44f-ef0f-4e39-b483-5604b970f254;
COMMIT;

BEGIN;
UPDATE avatar_asset SET filename = 'unisex/zapatos.png' WHERE id = 6ecb8dc1-4180-437a-b430-777ccd36116e;
-- Verify: SELECT id, filename FROM avatar_asset WHERE id = 6ecb8dc1-4180-437a-b430-777ccd36116e;
COMMIT;

BEGIN;
UPDATE avatar_asset SET filename = 'unisex/Smoking_fuck_news.png' WHERE id = 3309957c-247c-4d1f-ac13-97dff8d1c4f1;
-- Verify: SELECT id, filename FROM avatar_asset WHERE id = 3309957c-247c-4d1f-ac13-97dff8d1c4f1;
COMMIT;

BEGIN;
UPDATE avatar_asset SET filename = 'unisex/Fuck_news_pantalon.png' WHERE id = 542e90af-065b-42de-84f8-d8421b037d13;
-- Verify: SELECT id, filename FROM avatar_asset WHERE id = 542e90af-065b-42de-84f8-d8421b037d13;
COMMIT;

BEGIN;
UPDATE avatar_asset SET filename = 'unisex/camisa_verde_juan.png' WHERE id = 33ddea78-4068-49c9-bdf2-f9893cdcc588;
-- Verify: SELECT id, filename FROM avatar_asset WHERE id = 33ddea78-4068-49c9-bdf2-f9893cdcc588;
COMMIT;

BEGIN;
UPDATE avatar_asset SET filename = 'unisex/pantalon.png' WHERE id = c52c5655-86a3-4c48-a72c-7db84a39a193;
-- Verify: SELECT id, filename FROM avatar_asset WHERE id = c52c5655-86a3-4c48-a72c-7db84a39a193;
COMMIT;

BEGIN;
UPDATE avatar_asset SET filename = 'unisex/Saco_tortuga.png' WHERE id = aeb45b9b-77f6-4b4d-a645-b0265258e7c1;
-- Verify: SELECT id, filename FROM avatar_asset WHERE id = aeb45b9b-77f6-4b4d-a645-b0265258e7c1;
COMMIT;

BEGIN;
UPDATE user_avatar SET layers = '[{"category": "base", "file": "base/base-man/167 sin t\u00edtulo_20250923002615.png"}, {"category": "shoes", "file": "clothes/zapatos_rosados.png"}, {"category": "socks", "file": "clothes/medias_negras.png"}, {"category": "eyes", "file": "eyes/ojos_1.png"}, {"category": "jacket", "file": "clothes/Saco_tortuga.png"}, {"category": "accessories", "file": "accessories/manilla_2.png"}, {"category": "makeup", "file": "makeup/rubor.png"}, {"category": "shirt", "file": "clothes/esqueleto_azul.png"}, {"category": "hair", "file": "hair/hair_6.png"}, {"category": "pants", "file": "clothes/pantalon_rojo.png"}]'::jsonb WHERE id = 196f2a87-cdc7-4c06-9ea7-b87ad6db985a;
-- Verify: SELECT id FROM user_avatar WHERE id = 196f2a87-cdc7-4c06-9ea7-b87ad6db985a;
COMMIT;

BEGIN;
UPDATE user_avatar SET layers = '[{"category": "base", "file": "base/base-man/167 sin t\u00edtulo_20250923002615.png"}, {"category": "shoes", "file": "clothes/zapatos_rosados.png"}, {"category": "socks", "file": "clothes/medias_negras.png"}, {"category": "eyes", "file": "eyes/ojos_1.png"}, {"category": "accessories", "file": "accessories/manilla_2.png"}, {"category": "makeup", "file": "makeup/rubor.png"}, {"category": "shirt", "file": "clothes/camisa_colombia.png"}, {"category": "hair", "file": "hair/hair_6.png"}, {"category": "pants", "file": "clothes/pantalon_rojo.png"}]'::jsonb WHERE id = 03693192-0d2f-4bea-99ef-c910adf85e52;
-- Verify: SELECT id FROM user_avatar WHERE id = 03693192-0d2f-4bea-99ef-c910adf85e52;
COMMIT;

BEGIN;
UPDATE user_avatar SET layers = '[{"category": "base", "file": "base/base-man/167 sin t\u00edtulo_20250923002615.png"}, {"category": "shoes", "file": "clothes/zapatos.png"}, {"category": "eyes", "file": "eyes/ojos_1.png"}, {"category": "accessories", "file": "accessories/manilla_2.png"}, {"category": "makeup", "file": "makeup/rubor.png"}, {"category": "shirt", "file": "clothes/esqueleto_blanco_mujer.png"}, {"category": "hair", "file": "hair/hair_2.png"}, {"category": "pants", "file": "clothes/pantalon_blanco.png"}]'::jsonb WHERE id = 00c51bec-7a75-4c5f-a4a8-b584cea9f9ca;
-- Verify: SELECT id FROM user_avatar WHERE id = 00c51bec-7a75-4c5f-a4a8-b584cea9f9ca;
COMMIT;

