#!/usr/bin/env python3
"""Script para corregir los tamaños de archivos que están como NULL en la base de datos."""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.core.config import get_settings


async def corregir_tamanos_null() -> None:
    """Corrige los tamaños NULL en la base de datos calculando el tamaño real de los archivos."""
    settings = get_settings()

    # Crear engine de base de datos con driver async
    database_url = settings.get_database_url(async_driver=True)
    engine = create_async_engine(database_url, echo=False)

    async with AsyncSession(engine) as session:
        try:
            # Obtener todos los archivos con tamaño NULL
            query = text("""
                SELECT archivo_id, nombre_original, url
                FROM archivos_curso
                WHERE tamaño IS NULL
            """)
            result = await session.execute(query)
            archivos_null = result.fetchall()

            print(f"Encontrados {len(archivos_null)} archivos con tamaño NULL")

            actualizados = 0
            errores = 0

            for archivo in archivos_null:
                archivo_id = archivo[0]
                nombre_original = archivo[1]
                url = archivo[2]

                ruta_completa = Path(url.lstrip("/"))

                if ruta_completa.exists():
                    try:
                        tamaño_real = ruta_completa.stat().st_size

                        # Actualizar el registro
                        update_query = text("""
                            UPDATE archivos_curso
                            SET tamaño = :tamaño
                            WHERE archivo_id = :archivo_id
                        """)
                        await session.execute(update_query, {
                            "tamaño": tamaño_real,
                            "archivo_id": archivo_id
                        })

                        print(f"✅ Actualizado {nombre_original}: {tamaño_real} bytes")
                        actualizados += 1

                    except OSError as e:
                        print(f"❌ Error al calcular tamaño de {nombre_original}: {e}")
                        errores += 1
                else:
                    print(f"⚠️  Archivo no encontrado: {url}")
                    errores += 1

            await session.commit()
            print("\n📊 Resumen:")
            print(f"   ✅ Actualizados: {actualizados}")
            print(f"   ❌ Errores: {errores}")
            print(f"   📁 Total procesados: {len(archivos_null)}")

        except Exception as e:
            print(f"❌ Error general: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(corregir_tamanos_null())