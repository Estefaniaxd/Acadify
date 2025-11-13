"""
Análisis detallado de discrepancias en HistorialRacha
"""
import asyncio
import asyncpg
from src.core.config import settings
from sqlalchemy import inspect
from src.models.gamification.historial_racha import HistorialRacha


async def main():
    print("\n" + "="*70)
    print("🔍 ANÁLISIS: HistorialRacha - Modelo vs Base de Datos")
    print("="*70 + "\n")
    
    # Conectar a BD
    db_url = settings.get_database_url(async_driver=False)
    conn = await asyncpg.connect(db_url)
    
    try:
        # 1. Obtener columnas de la BD
        bd_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'historial_racha'
            ORDER BY ordinal_position
        """)
        
        print(f"📋 Verificando columnas actuales...")
        print(f"   ✓ {len(bd_columns)} columnas encontradas en BD\n")
        
        # 2. Obtener columnas del modelo
        mapper = inspect(HistorialRacha)
        model_columns = {col.key for col in mapper.columns}
        
        print(f"   ✓ {len(model_columns)} columnas en modelo\n")
        
        # 3. Comparar
        bd_column_names = {col['column_name'] for col in bd_columns}
        
        # Campos solo en BD
        solo_bd = bd_column_names - model_columns
        # Campos solo en modelo
        solo_modelo = model_columns - bd_column_names
        # Campos en ambos
        en_ambos = bd_column_names & model_columns
        
        print("="*70)
        print("1️⃣  CAMPOS SOLO EN BASE DE DATOS (faltan en modelo):")
        print("="*70)
        if solo_bd:
            for col_name in sorted(solo_bd):
                col_info = next(c for c in bd_columns if c['column_name'] == col_name)
                nullable = "NULL" if col_info['is_nullable'] == 'YES' else "NOT NULL"
                default = f", default={col_info['column_default']}" if col_info['column_default'] else ""
                print(f"   ❌ {col_name:30} ({col_info['data_type']:20} {nullable}{default})")
        else:
            print("   ✅ Ninguno - Modelo tiene todos los campos de BD")
        
        print("\n" + "="*70)
        print("2️⃣  CAMPOS SOLO EN MODELO (no existen en BD):")
        print("="*70)
        if solo_modelo:
            for col_name in sorted(solo_modelo):
                col = next(c for c in mapper.columns if c.key == col_name)
                print(f"   ⚠️  {col_name:30} ({col.type.__class__.__name__})")
        else:
            print("   ✅ Ninguno - Todos los campos del modelo existen en BD")
        
        print("\n" + "="*70)
        print("3️⃣  CAMPOS EN AMBOS (correctos):")
        print("="*70)
        for col_name in sorted(en_ambos):
            col_info = next(c for c in bd_columns if c['column_name'] == col_name)
            print(f"   ✅ {col_name:30} ({col_info['data_type']})")
        
        # 4. Recomendaciones
        print("\n" + "="*70)
        print("💡 RECOMENDACIONES:")
        print("="*70)
        
        if solo_bd:
            print("\n🔧 Agregar al modelo HistorialRacha:\n")
            for col_name in sorted(solo_bd):
                col_info = next(c for c in bd_columns if c['column_name'] == col_name)
                data_type = col_info['data_type']
                nullable = col_info['is_nullable'] == 'YES'
                
                # Mapear tipos SQL a SQLAlchemy
                type_map = {
                    'integer': 'Integer',
                    'bigint': 'BigInteger',
                    'character varying': 'String',
                    'text': 'Text',
                    'boolean': 'Boolean',
                    'timestamp with time zone': 'TIMESTAMP(timezone=True)',
                    'timestamp without time zone': 'TIMESTAMP',
                    'uuid': 'UUID(as_uuid=True)',
                    'json': 'JSON',
                    'jsonb': 'JSON',
                    'numeric': 'Numeric',
                    'USER-DEFINED': 'ENUM or Custom'
                }
                
                sa_type = type_map.get(data_type, data_type)
                null_str = f"nullable={nullable}"
                
                print(f"    {col_name} = Column({sa_type}, {null_str})")
        
        if solo_modelo:
            print("\n⚠️  Campos en modelo que NO existen en BD:")
            print("    Opciones:")
            print("    A) Eliminar del modelo (si no se usan)")
            print("    B) Crear migración para agregar a BD")
        
        if not solo_bd and not solo_modelo:
            print("\n   ✨ ¡MODELO PERFECTAMENTE ALINEADO CON BD! ✨")
        
        print("\n" + "="*70)
        print("📊 RESUMEN:")
        print("="*70)
        print(f"   📦 Campos en BD:        {len(bd_column_names)}")
        print(f"   📦 Campos en modelo:    {len(model_columns)}")
        print(f"   ✅ Campos correctos:    {len(en_ambos)}")
        print(f"   ❌ Faltan en modelo:    {len(solo_bd)}")
        print(f"   ⚠️  Sobran en modelo:   {len(solo_modelo)}")
        print("="*70 + "\n")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
