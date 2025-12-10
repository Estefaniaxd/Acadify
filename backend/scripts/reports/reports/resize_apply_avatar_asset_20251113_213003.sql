-- Generated apply SQL to update avatar_asset after resizing assets
-- Snapshot command (run in psql) to capture existing rows before applying:
-- \copy (SELECT id, filename, width, height, file_size, sha256 FROM avatar_asset WHERE filename IN ('accessories/unisex/collar_1.png','accessories/unisex/gafas_2.png','accessories/unisex/moño.png','accessories/unisex/orejas_gato.png','clothes/unisex/Corset_rojo.png','clothes/unisex/Medias_maya.png','clothes/unisex/calentadoras.png','clothes/unisex/camisa_cafe.png','clothes/unisex/camisa_miku.png','clothes/unisex/esqueleto_azul.png','clothes/unisex/falda_2.png','clothes/unisex/falda_blanca.png','clothes/unisex/falda_miku.png','clothes/unisex/vestido.png','clothes/unisex/zapatos_beige.png','clothes/unisex/zapatos_rosados.png','eyes/unisex/ojos_4.png','eyes/unisex/ojos_5.png','eyes/unisex/ojos_6.png','hair/unisex/hair_1.png','hair/unisex/hair_2.png','hair/unisex/hair_3.png','hair/unisex/hair_4.png','makeup/unisex/ahumado_morado.png','makeup/unisex/ahumado_negro.png','makeup/unisex/remolino_rubor.png','makeup/unisex/rubor.png','mouth/unisex/boca_3.png')) TO '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/scripts/reports/reports/preapply_resize_avatar_asset_snapshot_20251113_213003.csv' CSV HEADER;

BEGIN;

-- Update for file: accessories/unisex/collar_1.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 2151, sha256 = 'c0ab1a74636dec5466d849dd6c0ab8d4e315c1e9f1884a7aa628ee4a43f04a7f' WHERE filename = 'accessories/unisex/collar_1.png';

-- Update for file: accessories/unisex/gafas_2.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 4751, sha256 = 'bfbfe73f81260789b37e1a15180530c46abe3fab224c45666f790c8fc16711d9' WHERE filename = 'accessories/unisex/gafas_2.png';

-- Update for file: accessories/unisex/moño.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 5167, sha256 = '3c390fc6ed33b27d3231e58d145f0d31b7665952de9067cb039d7bd9edf94d1d' WHERE filename = 'accessories/unisex/moño.png';

-- Update for file: accessories/unisex/orejas_gato.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 2783, sha256 = 'c437c6f309a55dab4648db3a6c788c331063bb8298e5abec935b85458b454361' WHERE filename = 'accessories/unisex/orejas_gato.png';

-- Update for file: clothes/unisex/Corset_rojo.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 10035, sha256 = 'a3aec9c5c201b5f7685ffdaddd25747e44594eceafa60f784509f57758fbcbfc' WHERE filename = 'clothes/unisex/Corset_rojo.png';

-- Update for file: clothes/unisex/Medias_maya.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 11469, sha256 = '2853aa080503e4ce2932426c783673fed2ffb9d92e1df30a34081264cee2257f' WHERE filename = 'clothes/unisex/Medias_maya.png';

-- Update for file: clothes/unisex/calentadoras.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 8925, sha256 = '41bf503b4664239527f6913c97dd41251d9f89cbaa5a68e9bbd178c03395fad4' WHERE filename = 'clothes/unisex/calentadoras.png';

-- Update for file: clothes/unisex/camisa_cafe.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 9402, sha256 = 'c9323506bf985393fdb192424ebb7a1082898be44f4a4bfacb8f0fe7d1e23133' WHERE filename = 'clothes/unisex/camisa_cafe.png';

-- Update for file: clothes/unisex/camisa_miku.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 10969, sha256 = '04ea8593a336b1a16e6658e4d26ed69b8ebd151a4aea09141fad1df33e97d10b' WHERE filename = 'clothes/unisex/camisa_miku.png';

-- Update for file: clothes/unisex/esqueleto_azul.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 7626, sha256 = '4887e077e3750a4337a2a4d45e7706fe6c3d7760db2af55110e66d274aa5feed' WHERE filename = 'clothes/unisex/esqueleto_azul.png';

-- Update for file: clothes/unisex/falda_2.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 12331, sha256 = '384e6bffa48e36e08ed3d30a221ed1153f6d98b684720e601b1f41e6a104fe9b' WHERE filename = 'clothes/unisex/falda_2.png';

-- Update for file: clothes/unisex/falda_blanca.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 9423, sha256 = '3372c9c9d539c7e85777bfb3a220fdd970d2e226833e50fb9c9124f8a0f6997a' WHERE filename = 'clothes/unisex/falda_blanca.png';

-- Update for file: clothes/unisex/falda_miku.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 7382, sha256 = '8d24c3f94731d2d44cb38967fc25f1d5ec68442816421b67a576afc160554a33' WHERE filename = 'clothes/unisex/falda_miku.png';

-- Update for file: clothes/unisex/vestido.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 6430, sha256 = 'ea5d92ca1fbc574084b65b144d2dfcf80e75c6131f92dbf1ffbd9ee0897352d8' WHERE filename = 'clothes/unisex/vestido.png';

-- Update for file: clothes/unisex/zapatos_beige.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 9742, sha256 = '6a93e5306670684d231554077605591665f9af9ba4e4b0a76a61c0aada2b0e9b' WHERE filename = 'clothes/unisex/zapatos_beige.png';

-- Update for file: clothes/unisex/zapatos_rosados.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 8142, sha256 = 'c88230ba374d521ab66636838ada9f6005ee24f9071cbcae1e9f2401598f7dd9' WHERE filename = 'clothes/unisex/zapatos_rosados.png';

-- Update for file: eyes/unisex/ojos_4.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 4267, sha256 = '8121a11b46e934a466cb7bd08437552b26c8d25b248f2ecc442583be02124d73' WHERE filename = 'eyes/unisex/ojos_4.png';

-- Update for file: eyes/unisex/ojos_5.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 5885, sha256 = '8041dd9f051088e9519d3333cc20f463f0060c029e65e5c5711d588c6747ec55' WHERE filename = 'eyes/unisex/ojos_5.png';

-- Update for file: eyes/unisex/ojos_6.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 5954, sha256 = 'd453e47e85cc57d2d122ff3077d65a9043959b7bd49c11e3837512e077bde411' WHERE filename = 'eyes/unisex/ojos_6.png';

-- Update for file: hair/unisex/hair_1.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 21279, sha256 = '753a406ccc40ea16429e678dae7f7fb4576a67e87ceeecdf962372b0bca27472' WHERE filename = 'hair/unisex/hair_1.png';

-- Update for file: hair/unisex/hair_2.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 27071, sha256 = 'a7d7e34173d4b6f38967c93cff3f64ca24552a71a3fb904e3f3cba4f97279fe3' WHERE filename = 'hair/unisex/hair_2.png';

-- Update for file: hair/unisex/hair_3.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 22417, sha256 = 'bf6871a47e2fa9837dd560fcf4d189ddd5f7a225b4a8ddeb7ac4f24c122b7069' WHERE filename = 'hair/unisex/hair_3.png';

-- Update for file: hair/unisex/hair_4.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 12662, sha256 = 'edfefa561221008fcad0f3c25b02318a94d63b0ca21af66aa2197f4b00009804' WHERE filename = 'hair/unisex/hair_4.png';

-- Update for file: makeup/unisex/ahumado_morado.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 4924, sha256 = '647445cadd7f099c4d01ebf6e14cfacb8c072a4b09377eaaa2eb48198ad6fafa' WHERE filename = 'makeup/unisex/ahumado_morado.png';

-- Update for file: makeup/unisex/ahumado_negro.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 3241, sha256 = 'b3a0808a117287d8cfed3ebed4844ed6def7642c8ea2822c81c3bded012ee810' WHERE filename = 'makeup/unisex/ahumado_negro.png';

-- Update for file: makeup/unisex/remolino_rubor.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 3171, sha256 = 'e6d940968373c31c4081e40e28b9a3aacb546f091ecced66e43c7f62a500afd0' WHERE filename = 'makeup/unisex/remolino_rubor.png';

-- Update for file: makeup/unisex/rubor.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 5442, sha256 = 'b8da8e79d7e641c639d64d7d86fc6e4748b96f38738182aa7ef339c97aeb14c9' WHERE filename = 'makeup/unisex/rubor.png';

-- Update for file: mouth/unisex/boca_3.png
UPDATE avatar_asset SET width = 512, height = 512, file_size = 1649, sha256 = '1b6ddd84355be97d89223712f44dba624abfac53b37c7f114026d7d637c25be3' WHERE filename = 'mouth/unisex/boca_3.png';

COMMIT;
