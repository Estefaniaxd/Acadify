-- avatar_asset updates generated from mapping CSV
-- Review carefully and run in a transaction or in small batches.

BEGIN;
UPDATE avatar_asset SET filename = 'hair/female/hair_4.png' WHERE filename = 'hair_4.png' AND filename NOT LIKE '%/%';
-- Verify the update: SELECT * FROM avatar_asset WHERE filename = 'hair/female/hair_4.png';
COMMIT;
