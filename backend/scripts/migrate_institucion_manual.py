"""
Script manual para agregar los campos nuevos a la tabla Institucion.
Se ejecuta directamente con SQL para evitar conflictos con Alembic.
"""

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/acadify")

def ejecutar_migracion():
    """Ejecuta la migración manual de la tabla Institucion"""
    
    conn = None
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("🔄 Iniciando migración manual de Institucion...")
        
        # PASO 1: Crear nuevos ENUMs si no existen
        print("\n1️⃣ Creando nuevos ENUMs...")
        
        enum_queries = [
            """
            DO $$ BEGIN
                CREATE TYPE modalidad_ensenanza AS ENUM ('presencial', 'virtual', 'hibrida', 'dual');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """,
            """
            DO $$ BEGIN
                CREATE TYPE tipo_calendario AS ENUM ('semestral', 'trimestral', 'bimestral', 'cuatrimestral', 'anual', 'modular');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """,
        ]
        
        for query in enum_queries:
            cur.execute(query)
        
        conn.commit()
        print("   ✅ ENUMs creados/verificados")
        
        # PASO 2: Actualizar tipo_institucion con nuevos valores
        print("\n2️⃣ Actualizando ENUM tipo_institucion...")
        cur.execute("""
            ALTER TYPE tipo_institucion ADD VALUE IF NOT EXISTS 'centro_idiomas';
            ALTER TYPE tipo_institucion ADD VALUE IF NOT EXISTS 'centro_deportivo';
            ALTER TYPE tipo_institucion ADD VALUE IF NOT EXISTS 'seminario';
            ALTER TYPE tipo_institucion ADD VALUE IF NOT EXISTS 'conservatorio';
            ALTER TYPE tipo_institucion ADD VALUE IF NOT EXISTS 'escuela_militar';
            ALTER TYPE tipo_institucion ADD VALUE IF NOT EXISTS 'otro';
        """)
        conn.commit()
        print("   ✅ tipo_institucion actualizado")
        
        # PASO 3: Agregar nuevas columnas a Institucion
        print("\n3️⃣ Agregando nuevas columnas a Institucion...")
        
        columnas = [
            # Identidad visual
            ("logo_url", "VARCHAR(500)", "NOT NULL DEFAULT 'https://via.placeholder.com/150'", "URL del logo institucional (OBLIGATORIO)"),
            ("color_primario", "VARCHAR(7)", "NULL", "Color primario en formato hexadecimal #RRGGBB"),
            ("color_secundario", "VARCHAR(7)", "NULL", "Color secundario en formato hexadecimal #RRGGBB"),
            
            # Modalidad y calendario
            ("modalidad_ensenanza", "modalidad_ensenanza", "NOT NULL DEFAULT 'presencial'", "Modalidad: presencial, virtual, híbrida o dual"),
            ("tipo_calendario", "tipo_calendario", "NULL", "Tipo de calendario académico"),
            ("jornadas", "TEXT[]", "NULL", "Array de jornadas disponibles"),
            
            # Dominios
            ("dominio_principal", "VARCHAR(100)", "NULL", "Dominio principal sin @ (ej: arp.edu.co) - para registro automático"),
            ("dominios_adicionales", "TEXT[]", "NULL", "Dominios secundarios para registro automático"),
            
            # Presencia digital
            ("website", "VARCHAR(255)", "NULL", "Sitio web oficial de la institución"),
            ("redes_sociales", "JSONB", "NULL", "JSON con links a redes sociales"),
            
            # Acreditación
            ("acreditacion_nacional", "VARCHAR(150)", "NULL", "Entidad acreditadora nacional"),
            ("acreditacion_internacional", "VARCHAR(150)", "NULL", "Certificaciones internacionales"),
            ("fecha_acreditacion", "TIMESTAMP WITH TIME ZONE", "NULL", "Fecha de obtención de la acreditación principal"),
            
            # Capacidad y estadísticas
            ("capacidad_estudiantes", "INTEGER", "NULL", "Capacidad máxima de estudiantes"),
            ("numero_estudiantes_actual", "INTEGER", "DEFAULT 0", "Número actual de estudiantes matriculados"),
            ("numero_docentes", "INTEGER", "DEFAULT 0", "Número actual de docentes activos"),
            ("numero_programas_activos", "INTEGER", "DEFAULT 0", "Número de programas académicos activos"),
            
            # Configuración regional
            ("configuracion_regional", "JSONB", "NULL", "Configuración regional"),
            
            # Campos personalizados
            ("campos_personalizados", "JSONB", "NULL", "Campos personalizados específicos"),
        ]
        
        for nombre_columna, tipo_dato, constraints, comentario in columnas:
            try:
                # Verificar si la columna ya existe
                cur.execute(f"""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name='Institucion' AND column_name='{nombre_columna}';
                """)
                if cur.fetchone():
                    print(f"   ⚠️  Columna '{nombre_columna}' ya existe, saltando...")
                    continue
                
                # Agregar la columna
                query = f'ALTER TABLE "Institucion" ADD COLUMN {nombre_columna} {tipo_dato} {constraints};'
                cur.execute(query)
                
                # Agregar comentario
                cur.execute(f"""
                    COMMENT ON COLUMN "Institucion".{nombre_columna} IS '{comentario}';
                """)
                
                print(f"   ✅ Agregada: {nombre_columna}")
            except Exception as e:
                print(f"   ❌ Error en {nombre_columna}: {str(e)}")
                conn.rollback()
                continue
        
        conn.commit()
        
        # PASO 4: Agregar comentarios a columnas existentes
        print("\n4️⃣ Agregando comentarios a columnas existentes...")
        cur.execute("""
            COMMENT ON COLUMN "Institucion".usa_programas IS 'TRUE: Universidad/Instituto con programas. FALSE: Colegio sin programas';
            COMMENT ON COLUMN "Institucion".correo_institucional IS 'Correo principal para contacto y envío de invitaciones';
            COMMENT ON COLUMN "Institucion".estado IS 'Estado del ciclo de vida: pendiente → activa → suspendida/inactiva';
            COMMENT ON COLUMN "Institucion".fecha_creacion IS 'Fecha de creación de la institución en el sistema';
            COMMENT ON COLUMN "Institucion".fecha_activacion IS 'Fecha en que el primer coordinador aceptó la invitación';
        """)
        conn.commit()
        print("   ✅ Comentarios agregados")
        
        # PASO 5: Actualizar registros existentes con logo por defecto
        print("\n5️⃣ Actualizando registros existentes...")
        cur.execute("""
            UPDATE "Institucion" 
            SET logo_url = 'https://via.placeholder.com/150'
            WHERE logo_url IS NULL OR logo_url = '';
        """)
        conn.commit()
        print(f"   ✅ {cur.rowcount} instituciones actualizadas con logo por defecto")
        
        # PASO 6: Eliminar la columna 'dominio' antigua si existe
        print("\n6️⃣ Limpiando columna antigua 'dominio'...")
        try:
            cur.execute("""
                ALTER TABLE "Institucion" DROP COLUMN IF EXISTS dominio;
            """)
            conn.commit()
            print("   ✅ Columna 'dominio' eliminada")
        except Exception as e:
            print(f"   ⚠️  No se pudo eliminar 'dominio': {str(e)}")
            conn.rollback()
        
        print("\n✅ ¡Migración completada exitosamente!\n")
        
        # Mostrar estructura actualizada
        print("📊 Columnas de la tabla Institucion:")
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'Institucion'
            ORDER BY ordinal_position;
        """)
        for row in cur.fetchall():
            print(f"   - {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
        
        cur.close()
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN MANUAL: Institucion - Campos Extendidos")
    print("=" * 60)
    ejecutar_migracion()
