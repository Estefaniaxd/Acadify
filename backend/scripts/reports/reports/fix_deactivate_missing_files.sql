-- SQL para desactivar archivos que no existen en disco
BEGIN;

UPDATE avatar_asset SET is_active='N' WHERE id='2e4fa84a-7382-43bd-bea5-b50022a2c67b'; -- accessories/unisex/manilla_2.png

COMMIT;
