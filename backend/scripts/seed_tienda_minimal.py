"""
Script minimalista para insertar items en la tienda usando SQL directo
Usa solo las columnas que existen en la tabla SQL
"""
import asyncio
import asyncpg
from src.core.config import settings


async def main():
    print("🎮 SEED TIENDA MINIMAL")
    print("=" * 50)
    
    # Conectar directamente con asyncpg
    conn = await asyncpg.connect(settings.get_database_url(async_driver=False))
    
    try:
        # Definir items básicos con solo las columnas que existen
        items = [
            {
                'nombre': 'Cielo Estrellado',
                'descripcion': 'Un hermoso cielo nocturno lleno de estrellas',
                'categoria': 'foto_portada',
                'tipo': 'cosmetic',
                'rareza': 'comun',
                'precio_puntos': 100,
                'imagen_preview_url': '/assets/banners/cielo_estrellado.jpg',
                'es_disponible': True,
            },
            {
                'nombre': 'Bosque Tranquilo',
                'descripcion': 'Un bosque verde y pacífico',
                'categoria': 'foto_portada',
                'tipo': 'cosmetic',
                'rareza': 'comun',
                'precio_puntos': 100,
                'imagen_preview_url': '/assets/banners/bosque.jpg',
                'es_disponible': True,
            },
            {
                'nombre': 'Marco Dorado',
                'descripcion': 'Un elegante marco dorado para tu perfil',
                'categoria': 'marco_perfil',
                'tipo': 'cosmetic',
                'rareza': 'raro',
                'precio_puntos': 250,
                'imagen_preview_url': '/assets/frames/marco_dorado.png',
                'es_disponible': True,
            },
            {
                'nombre': 'Congelador de Racha',
                'descripcion': 'Congela tu racha por 1 día',
                'categoria': 'proteccion_racha',
                'tipo': 'consumible',
                'rareza': 'comun',
                'precio_puntos': 50,
                'duracion_dias': 1,
                'efecto_json': '{"tipo": "congelar_racha", "duracion_dias": 1}',
                'es_disponible': True,
            },
        ]
        
        print(f"🏪 Insertando {len(items)} items...")
        
        for item in items:
            await conn.execute("""
                INSERT INTO tienda_item (
                    nombre, descripcion, categoria, tipo, rareza,
                    precio_puntos, imagen_preview_url, es_disponible, duracion_dias, efecto_json
                ) VALUES ($1, $2, $3::categoria_item_enum, $4::tipo_item_enum, $5::rareza_enum, $6, $7, $8, $9, $10)
                ON CONFLICT (nombre) DO NOTHING
            """, 
                item['nombre'],
                item['descripcion'],
                item['categoria'],
                item['tipo'],
                item['rareza'],
                item['precio_puntos'],
                item.get('imagen_preview_url'),
                item['es_disponible'],
                item.get('duracion_dias'),
                item.get('efecto_json')
            )
            print(f"  ✓ {item['nombre']}")
        
        # Verificar
        count = await conn.fetchval("SELECT COUNT(*) FROM tienda_item")
        print(f"\n✅ Total items en tienda: {count}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
