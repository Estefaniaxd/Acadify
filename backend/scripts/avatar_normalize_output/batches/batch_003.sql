BEGIN;
UPDATE avatar_asset SET filename = 'hair/female/hair_3.png' WHERE filename = 'hair_3.png' AND filename NOT LIKE '%/%';
-- Verify the update: SELECT * FROM avatar_asset WHERE filename = 'hair/female/hair_3.png';
COMMIT;
