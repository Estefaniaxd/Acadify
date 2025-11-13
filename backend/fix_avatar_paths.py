"""Script para corregir las rutas duplicadas de assets en la base de datos.""""""Script para corregir los paths duplicados en avatar_asset."""



from src.db.session import SessionLocalfrom src.db.session import SessionLocal

from sqlalchemy import textfrom sqlalchemy import text



db = SessionLocal()def fix_avatar_paths():

try:    db = SessionLocal()

    # Actualizar filenames que empiezan con "assets/"    try:

    result = db.execute(text(        # Actualizar los filenames para quitar el prefijo "assets/"

        "UPDATE avatar_asset SET filename = REPLACE(filename, 'assets/', '') WHERE filename LIKE 'assets/%'"        result = db.execute(

    ))            text("UPDATE avatar_asset SET filename = REPLACE(filename, 'assets/', '') WHERE filename LIKE 'assets/%'")

    db.commit()        )

    print(f"✅ {result.rowcount} registros actualizados")        db.commit()



    # Verificar algunos ejemplos        print(f"✅ {result.rowcount} registros actualizados")

    check = db.execute(text("SELECT filename FROM avatar_asset LIMIT 5"))

    print("\n📋 Ejemplos de filenames actualizados:")        # Verificar algunos ejemplos

    for row in check:        examples = db.execute(text("SELECT filename FROM avatar_asset LIMIT 5")).fetchall()

        print(f"  - {row[0]}")        print("\n📋 Ejemplos de filenames actualizados:")

                for row in examples:

except Exception as e:            print(f"  - {row[0]}")

    print(f"❌ Error: {e}")

    db.rollback()    except Exception as e:

finally:        print(f"❌ Error: {e}")

    db.close()        db.rollback()

    finally:
        db.close()

if __name__ == "__main__":
    fix_avatar_paths()
