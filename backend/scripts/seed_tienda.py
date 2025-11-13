"""
Script para poblar la tienda con items iniciales.

Este script crea items de diferentes categorías:
- Banners/Fondos de perfil (10)
- Marcos de avatar (10)
- Accesorios para avatar (20)
- Items funcionales (5)
- Etiquetas especiales (10)

Cada item tiene:
- Nombre y descripción
- Categoría y rareza
- Precio según rareza
- Assets (cuando aplique)
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.models.gamification.tienda_item import TiendaItem
from src.enums.gamification.tienda_enums import CategoriaItem, RarezaItem
from datetime import datetime, timezone


# Configuración de precios por rareza
PRECIOS_POR_RAREZA = {
    RarezaItem.COMUN: (50, 150),
    RarezaItem.RARO: (150, 400),
    RarezaItem.EPICO: (500, 1000),
    RarezaItem.LEGENDARIO: (1000, 2500)
}


async def crear_items_tienda(session: AsyncSession):
    """Crea todos los items iniciales de la tienda."""
    items_creados = 0
    
    print("🏪 Iniciando creación de items para la tienda...")
    
    # ========== BANNERS / FONDOS DE PERFIL (10) ==========
    print("\n📸 Creando banners/fondos de perfil...")
    
    banners = [
        # Comunes
        {
            "nombre": "Cielo Estrellado",
            "descripcion": "Un hermoso cielo nocturno lleno de estrellas brillantes",
            "rareza": RarezaItem.COMUN,
            "precio": 100,
            "imagen_preview": "/assets/banners/cielo_estrellado.jpg"
        },
        {
            "nombre": "Bosque Tranquilo",
            "descripcion": "Un bosque verde y pacífico perfecto para relajarse",
            "rareza": RarezaItem.COMUN,
            "precio": 80,
            "imagen_preview": "/assets/banners/bosque_tranquilo.jpg"
        },
        {
            "nombre": "Atardecer Dorado",
            "descripcion": "Un atardecer cálido y dorado sobre el horizonte",
            "rareza": RarezaItem.COMUN,
            "precio": 120,
            "imagen_preview": "/assets/banners/atardecer_dorado.jpg"
        },
        # Raros
        {
            "nombre": "Galaxia Espiral",
            "descripcion": "Una impresionante galaxia espiral en el espacio profundo",
            "rareza": RarezaItem.RARO,
            "precio": 250,
            "imagen_preview": "/assets/banners/galaxia_espiral.jpg"
        },
        {
            "nombre": "Aurora Boreal",
            "descripcion": "Luces verdes y azules danzando en el cielo ártico",
            "rareza": RarezaItem.RARO,
            "precio": 300,
            "imagen_preview": "/assets/banners/aurora_boreal.jpg"
        },
        {
            "nombre": "Ciudad Cyber",
            "descripcion": "Una ciudad futurista con neones brillantes",
            "rareza": RarezaItem.RARO,
            "precio": 280,
            "imagen_preview": "/assets/banners/ciudad_cyber.jpg"
        },
        # Épicos
        {
            "nombre": "Nebulosa de Fuego",
            "descripcion": "Una nebulosa ardiente con tonos rojos y naranjas",
            "rareza": RarezaItem.EPICO,
            "precio": 700,
            "imagen_preview": "/assets/banners/nebulosa_fuego.jpg"
        },
        {
            "nombre": "Templo Antiguo",
            "descripcion": "Ruinas místicas de una civilización perdida",
            "rareza": RarezaItem.EPICO,
            "precio": 650,
            "imagen_preview": "/assets/banners/templo_antiguo.jpg"
        },
        # Legendarios
        {
            "nombre": "Portal Dimensional",
            "descripcion": "Un portal místico que conecta diferentes realidades",
            "rareza": RarezaItem.LEGENDARIO,
            "precio": 1500,
            "imagen_preview": "/assets/banners/portal_dimensional.jpg"
        },
        {
            "nombre": "Dragón Cósmico",
            "descripcion": "Un majestuoso dragón volando entre las estrellas",
            "rareza": RarezaItem.LEGENDARIO,
            "precio": 2000,
            "imagen_preview": "/assets/banners/dragon_cosmico.jpg"
        },
    ]
    
    for banner_data in banners:
        banner = TiendaItem(
            nombre=banner_data["nombre"],
            descripcion=banner_data["descripcion"],
            categoria=CategoriaItem.FONDO_PERFIL,
            rareza=banner_data["rareza"],
            precio_puntos=banner_data["precio"],
            imagen_preview=banner_data["imagen_preview"],
            es_limitado=False,
            es_activo=True
        )
        session.add(banner)
        items_creados += 1
    
    print(f"   ✅ {len(banners)} banners creados")
    
    # ========== MARCOS DE AVATAR (10) ==========
    print("\n🖼️ Creando marcos de avatar...")
    
    marcos = [
        # Comunes
        {
            "nombre": "Marco Básico",
            "descripcion": "Un marco simple y elegante",
            "rareza": RarezaItem.COMUN,
            "precio": 60
        },
        {
            "nombre": "Marco de Madera",
            "descripcion": "Marco rústico de madera tallada",
            "rareza": RarezaItem.COMUN,
            "precio": 80
        },
        {
            "nombre": "Marco Plateado",
            "descripcion": "Marco metálico con acabado plateado",
            "rareza": RarezaItem.COMUN,
            "precio": 100
        },
        # Raros
        {
            "nombre": "Marco Dorado",
            "descripcion": "Marco lujoso con detalles dorados",
            "rareza": RarezaItem.RARO,
            "precio": 200
        },
        {
            "nombre": "Marco de Flores",
            "descripcion": "Marco decorado con flores coloridas",
            "rareza": RarezaItem.RARO,
            "precio": 250
        },
        {
            "nombre": "Marco Tech",
            "descripcion": "Marco futurista con circuitos luminosos",
            "rareza": RarezaItem.RARO,
            "precio": 280
        },
        # Épicos
        {
            "nombre": "Marco de Dragón",
            "descripcion": "Marco con tallas de dragones míticos",
            "rareza": RarezaItem.EPICO,
            "precio": 600
        },
        {
            "nombre": "Marco Estelar",
            "descripcion": "Marco que brilla con estrellas animadas",
            "rareza": RarezaItem.EPICO,
            "precio": 750
        },
        # Legendarios
        {
            "nombre": "Marco Infinity",
            "descripcion": "Marco místico con el símbolo del infinito",
            "rareza": RarezaItem.LEGENDARIO,
            "precio": 1800
        },
        {
            "nombre": "Marco Real",
            "descripcion": "Marco digno de la realeza con gemas incrustadas",
            "rareza": RarezaItem.LEGENDARIO,
            "precio": 2200
        },
    ]
    
    for marco_data in marcos:
        marco = TiendaItem(
            nombre=marco_data["nombre"],
            descripcion=marco_data["descripcion"],
            categoria=CategoriaItem.MARCO_AVATAR,
            rareza=marco_data["rareza"],
            precio_puntos=marco_data["precio"],
            imagen_preview=f"/assets/marcos/{marco_data['nombre'].lower().replace(' ', '_')}.png",
            es_limitado=False,
            es_activo=True
        )
        session.add(marco)
        items_creados += 1
    
    print(f"   ✅ {len(marcos)} marcos creados")
    
    # ========== ITEMS FUNCIONALES (5) ==========
    print("\n⚙️ Creando items funcionales...")
    
    funcionales = [
        {
            "nombre": "Congelador de Racha 1 Día",
            "descripcion": "Congela tu racha por 1 día para no perderla",
            "rareza": RarezaItem.RARO,
            "precio": 200,
            "efecto": {"tipo": "congelar_racha", "dias": 1}
        },
        {
            "nombre": "Congelador de Racha 3 Días",
            "descripcion": "Congela tu racha por 3 días consecutivos",
            "rareza": RarezaItem.EPICO,
            "precio": 500,
            "efecto": {"tipo": "congelar_racha", "dias": 3}
        },
        {
            "nombre": "Recuperador de Racha",
            "descripcion": "Recupera tu racha perdida si actualizas hoy",
            "rareza": RarezaItem.EPICO,
            "precio": 400,
            "efecto": {"tipo": "recuperar_racha"}
        },
        {
            "nombre": "Multiplicador de Puntos x2",
            "descripcion": "Duplica los puntos obtenidos durante 24 horas",
            "rareza": RarezaItem.LEGENDARIO,
            "precio": 1000,
            "efecto": {"tipo": "multiplicador_puntos", "factor": 2, "duracion_horas": 24}
        },
        {
            "nombre": "Boost de XP +50%",
            "descripcion": "Aumenta la experiencia ganada en un 50% por 24 horas",
            "rareza": RarezaItem.LEGENDARIO,
            "precio": 800,
            "efecto": {"tipo": "boost_xp", "porcentaje": 50, "duracion_horas": 24}
        },
    ]
    
    for func_data in funcionales:
        funcional = TiendaItem(
            nombre=func_data["nombre"],
            descripcion=func_data["descripcion"],
            categoria=CategoriaItem.FUNCIONAL,
            rareza=func_data["rareza"],
            precio_puntos=func_data["precio"],
            imagen_preview=f"/assets/funcionales/{func_data['nombre'].lower().replace(' ', '_')}.png",
            es_funcional=True,
            efecto_json=func_data["efecto"],
            es_limitado=False,
            es_activo=True
        )
        session.add(funcional)
        items_creados += 1
    
    print(f"   ✅ {len(funcionales)} items funcionales creados")
    
    # ========== ACCESORIOS PARA AVATAR (20) ==========
    print("\n👔 Creando accesorios para avatar...")
    
    categorias_accesorios = [
        (CategoriaItem.CABELLO, "Cabello", 8),
        (CategoriaItem.OJOS, "Ojos", 6),
        (CategoriaItem.ROPA_SUPERIOR, "Ropa Superior", 6),
    ]
    
    contador_accesorios = 0
    for categoria, nombre_cat, cantidad in categorias_accesorios:
        for i in range(1, cantidad + 1):
            # Distribuir rareza
            if i <= cantidad // 2:
                rareza = RarezaItem.COMUN
                precio = 50 + (i * 10)
            elif i <= (cantidad * 3 // 4):
                rareza = RarezaItem.RARO
                precio = 200 + (i * 20)
            else:
                rareza = RarezaItem.EPICO
                precio = 600 + (i * 50)
            
            accesorio = TiendaItem(
                nombre=f"{nombre_cat} Estilo {i}",
                descripcion=f"Un estilo único de {nombre_cat.lower()} para tu avatar",
                categoria=categoria,
                rareza=rareza,
                precio_puntos=precio,
                imagen_preview=f"/assets/avatar/{categoria.value}/style_{i}.png",
                es_limitado=False,
                es_activo=True
            )
            session.add(accesorio)
            contador_accesorios += 1
            items_creados += 1
    
    print(f"   ✅ {contador_accesorios} accesorios creados")
    
    # ========== ETIQUETAS ESPECIALES (10) ==========
    print("\n🏷️  Creando etiquetas especiales...")
    
    etiquetas = [
        {
            "nombre": "Estudiante Dedicado",
            "descripcion": "Para estudiantes que nunca se rinden",
            "rareza": RarezaItem.COMUN,
            "precio": 100
        },
        {
            "nombre": "Maestro del Código",
            "descripcion": "Para programadores excepcionales",
            "rareza": RarezaItem.RARO,
            "precio": 300
        },
        {
            "nombre": "Científico Brillante",
            "descripcion": "Para mentes científicas destacadas",
            "rareza": RarezaItem.RARO,
            "precio": 300
        },
        {
            "nombre": "Líder Natural",
            "descripcion": "Para aquellos que inspiran a otros",
            "rareza": RarezaItem.EPICO,
            "precio": 700
        },
        {
            "nombre": "Innovador",
            "descripcion": "Para los que piensan diferente",
            "rareza": RarezaItem.EPICO,
            "precio": 750
        },
        {
            "nombre": "Perfeccionista",
            "descripcion": "Para los que buscan la excelencia",
            "rareza": RarezaItem.EPICO,
            "precio": 800
        },
        {
            "nombre": "Leyenda Viviente",
            "descripcion": "Etiqueta reservada para los mejores de los mejores",
            "rareza": RarezaItem.LEGENDARIO,
            "precio": 2000
        },
        {
            "nombre": "Gran Maestro",
            "descripcion": "El título más alto de conocimiento",
            "rareza": RarezaItem.LEGENDARIO,
            "precio": 2500
        },
        {
            "nombre": "Fundador",
            "descripcion": "Etiqueta especial para miembros fundadores",
            "rareza": RarezaItem.LEGENDARIO,
            "precio": 3000
        },
        {
            "nombre": "Campeón Absoluto",
            "descripcion": "Para los campeones de todas las competencias",
            "rareza": RarezaItem.LEGENDARIO,
            "precio": 2800
        },
    ]
    
    for etiqueta_data in etiquetas:
        etiqueta = TiendaItem(
            nombre=etiqueta_data["nombre"],
            descripcion=etiqueta_data["descripcion"],
            categoria=CategoriaItem.ETIQUETA,
            rareza=etiqueta_data["rareza"],
            precio_puntos=etiqueta_data["precio"],
            imagen_preview=f"/assets/etiquetas/{etiqueta_data['nombre'].lower().replace(' ', '_')}.png",
            es_limitado=False,
            es_activo=True
        )
        session.add(etiqueta)
        items_creados += 1
    
    print(f"   ✅ {len(etiquetas)} etiquetas creadas")
    
    # Guardar todo
    await session.commit()
    
    print(f"\n✨ ¡Seed completado exitosamente!")
    print(f"📊 Total de items creados: {items_creados}")
    print(f"   - Banners: 10")
    print(f"   - Marcos: 10")
    print(f"   - Items funcionales: 5")
    print(f"   - Accesorios: 20")
    print(f"   - Etiquetas: 10")
    print(f"   ----------------------")
    print(f"   TOTAL: {items_creados} items")


async def main():
    """Función principal."""
    print("🎮 SEED DE TIENDA - SISTEMA DE GAMIFICACIÓN")
    print("=" * 60)
    
    # Crear engine y sesión
    engine = create_async_engine(
        settings.get_database_url(async_driver=True),
        echo=False
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            await crear_items_tienda(session)
        except Exception as e:
            print(f"\n❌ Error durante el seed: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
        finally:
            await engine.dispose()
    
    print("\n✅ Proceso finalizado")


if __name__ == "__main__":
    asyncio.run(main())
