"""
Script simple para poblar la tienda - sin imports de modelos problemáticos.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.models.gamification.tienda_item import TiendaItem
from src.enums.gamification.tienda_enums import CategoriaItem, RarezaItem


async def crear_items_tienda(session: AsyncSession):
    """Crea todos los items iniciales."""
    items_creados = 0
    
    print("🏪 Iniciando creación de items...")
    
    # Banners
    banners_data = [
        ("Cielo Estrellado", "Un hermoso cielo nocturno", RarezaItem.COMUN, 100),
        ("Bosque Tranquilo", "Un bosque verde pacífico", RarezaItem.COMUN, 80),
        ("Galaxia Espiral", "Galaxia impresionante", RarezaItem.RARO, 250),
        ("Portal Dimensional", "Portal místico", RarezaItem.LEGENDARIO, 1500),
    ]
    
    for nombre, desc, rareza, precio in banners_data:
        item = TiendaItem(
            nombre=nombre,
            descripcion=desc,
            categoria=CategoriaItem.FONDO_PERFIL,
            rareza=rareza,
            precio_puntos=precio,
            preview_url=f"/assets/banners/{nombre.lower().replace(' ', '_')}.jpg",
            es_activo=True
        )
        session.add(item)
        items_creados += 1
    
    print(f"✅ {items_creados} items creados")
    await session.commit()
    

async def main():
    print("🎮 SEED DE TIENDA")
    print("=" * 50)
    
    engine = create_async_engine(settings.get_database_url(async_driver=True), echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            await crear_items_tienda(session)
            print("✅ Seed completado")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
