"""
Seed completo de la tienda con 55+ items coherentes
Usa SQL directo para evitar problemas con modelos SQLAlchemy
Distribuye items en categorías: banners, marcos, funcionales, accesorios avatar, etiquetas
"""
import asyncio
import asyncpg
from src.core.config import settings


# Definición completa de items organizados por categoría
BANNERS = [
    # Comunes (50-100 pts)
    {"nombre": "Cielo Estrellado", "descripcion": "Un hermoso cielo nocturno lleno de estrellas brillantes", "rareza": "comun", "precio": 80, "url": "/assets/banners/cielo_estrellado.jpg"},
    {"nombre": "Bosque Tranquilo", "descripcion": "Un bosque verde y pacífico al amanecer", "rareza": "comun", "precio": 80, "url": "/assets/banners/bosque_tranquilo.jpg"},
    {"nombre": "Playa Tropical", "descripcion": "Una playa paradisíaca con aguas cristalinas", "rareza": "comun", "precio": 90, "url": "/assets/banners/playa_tropical.jpg"},
    
    # Raros (150-250 pts)
    {"nombre": "Aurora Boreal", "descripcion": "Luces mágicas bailando en el cielo ártico", "rareza": "raro", "precio": 200, "url": "/assets/banners/aurora_boreal.jpg"},
    {"nombre": "Ciudad Cyberpunk", "descripcion": "Una metrópolis futurista llena de neones", "rareza": "raro", "precio": 220, "url": "/assets/banners/ciudad_cyber.jpg"},
    {"nombre": "Montañas Nevadas", "descripcion": "Majestuosas montañas cubiertas de nieve", "rareza": "raro", "precio": 180, "url": "/assets/banners/montanas_nevadas.jpg"},
    
    # Épicos (400-600 pts)
    {"nombre": "Nebulosa de Fuego", "descripcion": "Una nebulosa ardiente en el espacio profundo", "rareza": "epico", "precio": 500, "url": "/assets/banners/nebulosa_fuego.jpg"},
    {"nombre": "Templo Antiguo", "descripcion": "Ruinas místicas de una civilización perdida", "rareza": "epico", "precio": 450, "url": "/assets/banners/templo_antiguo.jpg"},
    
    # Legendarios (800-1200 pts)
    {"nombre": "Portal Dimensional", "descripcion": "Un portal que conecta múltiples realidades", "rareza": "legendario", "precio": 1000, "url": "/assets/banners/portal_dimensional.jpg"},
    {"nombre": "Dragón Cósmico", "descripcion": "Un majestuoso dragón surcando las estrellas", "rareza": "legendario", "precio": 1200, "url": "/assets/banners/dragon_cosmico.jpg"},
]

MARCOS = [
    # Comunes (50-100 pts)
    {"nombre": "Marco Básico", "descripcion": "Un marco simple y elegante", "rareza": "comun", "precio": 50, "url": "/assets/frames/basico.png"},
    {"nombre": "Marco de Madera", "descripcion": "Marco rústico de madera tallada", "rareza": "comun", "precio": 70, "url": "/assets/frames/madera.png"},
    {"nombre": "Marco Plateado", "descripcion": "Elegante marco con brillo plateado", "rareza": "comun", "precio": 90, "url": "/assets/frames/plateado.png"},
    
    # Raros (150-250 pts)
    {"nombre": "Marco Dorado", "descripcion": "Lujoso marco con detalles dorados", "rareza": "raro", "precio": 200, "url": "/assets/frames/dorado.png"},
    {"nombre": "Marco de Flores", "descripcion": "Marco decorado con flores exóticas", "rareza": "raro", "precio": 180, "url": "/assets/frames/flores.png"},
    {"nombre": "Marco Tech", "descripcion": "Marco futurista con circuitos luminosos", "rareza": "raro", "precio": 220, "url": "/assets/frames/tech.png"},
    
    # Épicos (400-600 pts)
    {"nombre": "Marco de Dragón", "descripcion": "Marco con un dragón tallado en 3D", "rareza": "epico", "precio": 500, "url": "/assets/frames/dragon.png"},
    {"nombre": "Marco Estelar", "descripcion": "Marco que brilla como las estrellas", "rareza": "epico", "precio": 450, "url": "/assets/frames/estelar.png"},
    
    # Legendarios (800-1200 pts)
    {"nombre": "Marco Infinity", "descripcion": "Marco que se expande infinitamente", "rareza": "legendario", "precio": 1000, "url": "/assets/frames/infinity.png"},
    {"nombre": "Marco Real", "descripcion": "El marco de los campeones supremos", "rareza": "legendario", "precio": 1200, "url": "/assets/frames/real.png"},
]

FUNCIONALES = [
    # Items consumibles y permanentes
    {"nombre": "Congelador 1 Día", "descripcion": "Congela tu racha por 1 día", "rareza": "comun", "precio": 50, "duracion": 1, "efecto": '{"tipo": "congelar_racha", "duracion_dias": 1}'},
    {"nombre": "Congelador 3 Días", "descripcion": "Congela tu racha por 3 días", "rareza": "raro", "precio": 120, "duracion": 3, "efecto": '{"tipo": "congelar_racha", "duracion_dias": 3}'},
    {"nombre": "Congelador 7 Días", "descripcion": "Congela tu racha por 1 semana", "rareza": "epico", "precio": 250, "duracion": 7, "efecto": '{"tipo": "congelar_racha", "duracion_dias": 7}'},
    {"nombre": "Recuperador de Racha", "descripcion": "Recupera una racha perdida", "rareza": "raro", "precio": 200, "duracion": None, "efecto": '{"tipo": "recuperar_racha"}'},
    {"nombre": "Multiplicador x2", "descripcion": "Duplica tus puntos por 24 horas", "rareza": "epico", "precio": 400, "duracion": 1, "efecto": '{"tipo": "multiplicador_puntos", "multiplicador": 2, "duracion_horas": 24}'},
    {"nombre": "Multiplicador x3", "descripcion": "Triplica tus puntos por 12 horas", "rareza": "legendario", "precio": 800, "duracion": None, "efecto": '{"tipo": "multiplicador_puntos", "multiplicador": 3, "duracion_horas": 12}'},
    {"nombre": "Boost XP +50%", "descripcion": "Aumenta tu experiencia 50% por 3 días", "rareza": "raro", "precio": 180, "duracion": 3, "efecto": '{"tipo": "boost_xp", "porcentaje": 50, "duracion_dias": 3}'},
]

ACCESORIOS_CABELLO = [
    {"nombre": "Cabello Corto Clásico", "descripcion": "Estilo corto y profesional", "rareza": "comun", "precio": 60},
    {"nombre": "Cabello Largo Liso", "descripcion": "Cabello largo y liso elegante", "rareza": "comun", "precio": 70},
    {"nombre": "Cabello Rizado", "descripcion": "Rizos naturales y voluminosos", "rareza": "raro", "precio": 150},
    {"nombre": "Mohawk Punk", "descripcion": "Estilo punk rebelde", "rareza": "raro", "precio": 180},
    {"nombre": "Trenzas Vikingas", "descripcion": "Trenzas al estilo nórdico", "rareza": "epico", "precio": 400},
    {"nombre": "Cabello de Fuego", "descripcion": "Cabello que parece arder", "rareza": "legendario", "precio": 900},
]

ACCESORIOS_OJOS = [
    {"nombre": "Ojos Marrones", "descripcion": "Ojos cálidos color marrón", "rareza": "comun", "precio": 40},
    {"nombre": "Ojos Azules", "descripcion": "Ojos azul cielo profundo", "rareza": "comun", "precio": 40},
    {"nombre": "Ojos Verdes", "descripcion": "Ojos verde esmeralda", "rareza": "raro", "precio": 120},
    {"nombre": "Ojos Heterocromía", "descripcion": "Cada ojo de diferente color", "rareza": "epico", "precio": 350},
    {"nombre": "Ojos Galácticos", "descripcion": "Ojos que reflejan el universo", "rareza": "legendario", "precio": 850},
]

ACCESORIOS_ROPA = [
    {"nombre": "Camisa Casual", "descripcion": "Camisa cómoda para el día a día", "rareza": "comun", "precio": 50},
    {"nombre": "Camisa Formal", "descripcion": "Camisa elegante para ocasiones especiales", "rareza": "raro", "precio": 150},
    {"nombre": "Hoodie Gamer", "descripcion": "Hoodie perfecta para gaming", "rareza": "raro", "precio": 180},
    {"nombre": "Chaqueta de Cuero", "descripcion": "Chaqueta de cuero auténtico", "rareza": "epico", "precio": 400},
    {"nombre": "Armadura Cyber", "descripcion": "Armadura tecnológica futurista", "rareza": "legendario", "precio": 950},
]

ETIQUETAS = [
    # Etiquetas de logros y estatus
    {"nombre": "Estudiante Dedicado", "descripcion": "Para quienes estudian con constancia", "rareza": "comun", "precio": 100},
    {"nombre": "Maestro del Código", "descripcion": "Experto en programación", "rareza": "raro", "precio": 250},
    {"nombre": "Científico Brillante", "descripcion": "Mente científica excepcional", "rareza": "raro", "precio": 250},
    {"nombre": "Líder Natural", "descripcion": "Cualidades de liderazgo sobresalientes", "rareza": "epico", "precio": 500},
    {"nombre": "Innovador", "descripcion": "Siempre pensando fuera de la caja", "rareza": "epico", "precio": 500},
    {"nombre": "Perfeccionista", "descripcion": "La excelencia es tu estándar", "rareza": "epico", "precio": 550},
    {"nombre": "Leyenda Viviente", "descripcion": "Has alcanzado el estatus legendario", "rareza": "legendario", "precio": 1000},
    {"nombre": "Gran Maestro", "descripcion": "Maestría absoluta en tu campo", "rareza": "legendario", "precio": 1100},
    {"nombre": "Fundador", "descripcion": "Uno de los primeros usuarios", "rareza": "legendario", "precio": 1500},
    {"nombre": "Campeón Supremo", "descripcion": "El mejor de los mejores", "rareza": "legendario", "precio": 2000},
]


async def insertar_items(conn, items, categoria, tipo):
    """Inserta un lote de items en la base de datos"""
    count = 0
    for item in items:
        try:
            await conn.execute("""
                INSERT INTO tienda_item (
                    nombre, descripcion, categoria, tipo, rareza,
                    precio_puntos, imagen_preview_url, es_disponible,
                    duracion_dias, efecto_json
                ) VALUES ($1, $2, $3::categoria_item_enum, $4, $5::rareza_enum, 
                          $6, $7, $8, $9, $10)
                ON CONFLICT (nombre) DO NOTHING
            """, 
                item['nombre'],
                item['descripcion'],
                categoria,
                tipo,
                item['rareza'],
                item['precio'],
                item.get('url'),
                True,
                item.get('duracion'),
                item.get('efecto')
            )
            count += 1
        except Exception as e:
            print(f"  ⚠️  Error en '{item['nombre']}': {e}")
    
    return count


async def main():
    print("\n" + "="*60)
    print("🎮 SEED COMPLETO DE TIENDA - ACADIFY")
    print("="*60 + "\n")
    
    # Conectar a la base de datos
    db_url = settings.get_database_url(async_driver=False)
    conn = await asyncpg.connect(db_url)
    
    try:
        # Limpiar datos anteriores (opcional)
        print("🧹 Limpiando datos anteriores...")
        await conn.execute("DELETE FROM inventario_usuario")
        await conn.execute("DELETE FROM transaccion_tienda")
        await conn.execute("DELETE FROM tienda_item")
        print("   ✓ Tablas limpiadas\n")
        
        total_insertados = 0
        
        # 1. Banners (foto_portada)
        print("📸 Insertando BANNERS (10 items)...")
        count = await insertar_items(conn, BANNERS, 'foto_portada', 'cosmetic')
        total_insertados += count
        print(f"   ✓ {count} banners insertados\n")
        
        # 2. Marcos (marco_perfil)
        print("🖼️  Insertando MARCOS (10 items)...")
        count = await insertar_items(conn, MARCOS, 'marco_perfil', 'cosmetic')
        total_insertados += count
        print(f"   ✓ {count} marcos insertados\n")
        
        # 3. Items funcionales
        print("⚙️  Insertando ITEMS FUNCIONALES (7 items)...")
        count = await insertar_items(conn, FUNCIONALES, 'proteccion_racha', 'consumible')
        total_insertados += count
        print(f"   ✓ {count} items funcionales insertados\n")
        
        # 4. Accesorios de cabello
        print("💇 Insertando ACCESORIOS CABELLO (6 items)...")
        count = await insertar_items(conn, ACCESORIOS_CABELLO, 'avatar_cabeza', 'avatar')
        total_insertados += count
        print(f"   ✓ {count} estilos de cabello insertados\n")
        
        # 5. Accesorios de ojos
        print("👁️  Insertando ACCESORIOS OJOS (5 items)...")
        count = await insertar_items(conn, ACCESORIOS_OJOS, 'avatar_cabeza', 'avatar')
        total_insertados += count
        print(f"   ✓ {count} estilos de ojos insertados\n")
        
        # 6. Accesorios de ropa
        print("👕 Insertando ACCESORIOS ROPA (5 items)...")
        count = await insertar_items(conn, ACCESORIOS_ROPA, 'avatar_torso', 'avatar')
        total_insertados += count
        print(f"   ✓ {count} prendas insertadas\n")
        
        # 7. Etiquetas
        print("🏷️  Insertando ETIQUETAS (10 items)...")
        count = await insertar_items(conn, ETIQUETAS, 'emoji_personalizado', 'permanente')
        total_insertados += count
        print(f"   ✓ {count} etiquetas insertadas\n")
        
        # Resumen final
        total_db = await conn.fetchval("SELECT COUNT(*) FROM tienda_item")
        
        print("="*60)
        print("✅ SEED COMPLETADO EXITOSAMENTE")
        print("="*60)
        print(f"📊 Total items procesados: {total_insertados}")
        print(f"📊 Total items en BD: {total_db}")
        print("\n🎯 Distribución por rareza:")
        
        # Mostrar distribución
        rarezas = await conn.fetch("""
            SELECT rareza, COUNT(*) as cantidad, 
                   SUM(precio_puntos) as valor_total,
                   AVG(precio_puntos)::INTEGER as precio_promedio
            FROM tienda_item 
            GROUP BY rareza 
            ORDER BY 
                CASE rareza
                    WHEN 'comun' THEN 1
                    WHEN 'raro' THEN 2
                    WHEN 'epico' THEN 3
                    WHEN 'legendario' THEN 4
                END
        """)
        
        for row in rarezas:
            emoji = {"comun": "⚪", "raro": "🔵", "epico": "🟣", "legendario": "🟡"}
            print(f"   {emoji.get(row['rareza'], '⚫')} {row['rareza'].upper():12} - "
                  f"{row['cantidad']:2} items | "
                  f"Promedio: {row['precio_promedio']:4} pts | "
                  f"Total: {row['valor_total']:5} pts")
        
        print("\n🎯 Distribución por categoría:")
        categorias = await conn.fetch("""
            SELECT categoria, COUNT(*) as cantidad
            FROM tienda_item 
            GROUP BY categoria 
            ORDER BY cantidad DESC
        """)
        
        for row in categorias:
            print(f"   📦 {row['categoria']:20} - {row['cantidad']:2} items")
        
        print("\n" + "="*60)
        print("🎉 ¡Tienda lista para usar!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
