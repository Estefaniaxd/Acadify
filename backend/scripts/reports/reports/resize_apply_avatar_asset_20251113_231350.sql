-- Generated apply SQL to update avatar_asset after resizing assets
-- Snapshot command (run in psql) to capture existing rows before applying:
-- \copy (SELECT id, filename, width, height, file_size, sha256 FROM avatar_asset WHERE filename IN ('clothes/unisex/camisa_colombia.png','clothes/unisex/camisa_colombia_2.png','clothes/unisex/camisa_elegante_blanca.png','clothes/unisex/pantalon_azul.png','clothes/unisex/pantalon_blanco.png','clothes/unisex/pantalon_cafe.png','clothes/unisex/pantalon_rojo.png','clothes/unisex/real_madrid.png')) TO '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/scripts/reports/reports/preapply_resize_avatar_asset_snapshot_20251113_231350.csv' CSV HEADER;

BEGIN;

-- Update for file: clothes/unisex/camisa_colombia.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 21330, sha256 = '0108e5cd1b1f70acb81f6269d62cf0644b2833ed7a55a350c32f854cdcb44b06' WHERE filename = 'clothes/unisex/camisa_colombia.png';

-- Update for file: clothes/unisex/camisa_colombia_2.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 14517, sha256 = '53c27ef86a722e4030ea83a1bd977b0c1e4ffe8928e48b835630fa1d7291bf40' WHERE filename = 'clothes/unisex/camisa_colombia_2.png';

-- Update for file: clothes/unisex/camisa_elegante_blanca.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 15299, sha256 = '5d583f4e8d15262e7909dd7c5a7077e513756f6c5e8555e8002c1fd5e2aa88c4' WHERE filename = 'clothes/unisex/camisa_elegante_blanca.png';

-- Update for file: clothes/unisex/pantalon_azul.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 14556, sha256 = '505229d729e39c90e97b519f65b2374de7c67ed235a3cde0bc3ae76b8c260edc' WHERE filename = 'clothes/unisex/pantalon_azul.png';

-- Update for file: clothes/unisex/pantalon_blanco.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 11458, sha256 = '3e20839e383c2fda912dd0114057e10f879127f24726d3dd1891dee0ace8ab61' WHERE filename = 'clothes/unisex/pantalon_blanco.png';

-- Update for file: clothes/unisex/pantalon_cafe.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 9352, sha256 = 'd554e427bea998fbaae43d66247d2cd43cfbad0d711a06f5b847022265ab8683' WHERE filename = 'clothes/unisex/pantalon_cafe.png';

-- Update for file: clothes/unisex/pantalon_rojo.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 10607, sha256 = 'd6f61c306bcdceb183da18ad67170ef5317f6a2e716e876e5f1abc1006c3681b' WHERE filename = 'clothes/unisex/pantalon_rojo.png';

-- Update for file: clothes/unisex/real_madrid.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 14180, sha256 = 'c95e27dcf5030d032ad863fb7f173814c07589415e70d574c4aca8c55ab6589f' WHERE filename = 'clothes/unisex/real_madrid.png';

COMMIT;
