BEGIN;
UPDATE avatar_asset SET filename = 'makeup/female/ahumado_negro.png' WHERE filename = 'ahumado_negro.png' AND filename NOT LIKE '%/%';
-- Verify the update: SELECT * FROM avatar_asset WHERE filename = 'makeup/female/ahumado_negro.png';
COMMIT;

BEGIN;
UPDATE avatar_asset SET filename = 'makeup/female/remolino_rubor.png' WHERE filename = 'remolino_rubor.png' AND filename NOT LIKE '%/%';
-- Verify the update: SELECT * FROM avatar_asset WHERE filename = 'makeup/female/remolino_rubor.png';
COMMIT;

BEGIN;
UPDATE avatar_asset SET filename = 'mouth/female/boca_3.png' WHERE filename = 'boca_3.png' AND filename NOT LIKE '%/%';
-- Verify the update: SELECT * FROM avatar_asset WHERE filename = 'mouth/female/boca_3.png';
COMMIT;
