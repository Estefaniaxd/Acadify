BEGIN;
UPDATE avatar_asset SET filename = 'hair/female/hair_2.png' WHERE filename = 'hair_2.png' AND filename NOT LIKE '%/%';
-- Verify the update: SELECT * FROM avatar_asset WHERE filename = 'hair/female/hair_2.png';
COMMIT;

BEGIN;
UPDATE avatar_asset SET filename = 'hair/female/hair_1.png' WHERE filename = 'hair_1.png' AND filename NOT LIKE '%/%';
-- Verify the update: SELECT * FROM avatar_asset WHERE filename = 'hair/female/hair_1.png';
COMMIT;
