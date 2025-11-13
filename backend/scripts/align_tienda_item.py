"""
Script para alinear el modelo TiendaItem con la tabla SQL real
Agrega/modifica campos para que coincidan con la estructura de 004_gamification_sql
"""
import asyncio
import asyncpg
from src.core.config import settings


async def main():
    print("\n" + "="*70)
    print("🔧 ALINEANDO MODELO TIENDA_ITEM CON BD")
    print("="*70 + "\n")
    
    conn = await asyncpg.connect(settings.get_database_url(async_driver=False))
    
    try:
        # 1. Verificar columnas actuales
        print("📋 Verificando columnas actuales...")
        columnas = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tienda_item'
            ORDER BY ordinal_position
        """)
        
        columnas_existentes = {col['column_name'] for col in columnas}
        print(f"   ✓ {len(columnas_existentes)} columnas encontradas\n")
        
        # Campos del modelo Python que NO están en BD
        campos_modelo_faltantes = {
            'preview_url': 'imagen_preview_url',  # En BD se llama diferente
            'nivel_minimo_requerido': 'nivel_minimo',  # En BD se llama diferente
            'es_activo': 'es_disponible',  # En BD se llama diferente
            'stock_disponible': 'stock_actual',  # En BD se llama diferente
            'disponible_desde': 'fecha_inicio',  # En BD se llama diferente
            'disponible_hasta': 'fecha_fin',  # En BD se llama diferente
            'orden_visualizacion': 'orden',  # En BD se llama diferente
        }
        
        # Campos que existen en BD pero NO en modelo
        campos_bd_extra = [
            'tipo',  # tipo_item_enum
            'imagen_url',
            'icono_url',
            'color_hex',
            'precio_original',
            'descuento_porcentaje',
            'stock_limitado',
            'max_por_usuario',
            'veces_comprado',
            'popularidad',
            'es_destacado',
            'es_nuevo',
            'avatar_asset_id',
            'recompensa_id',
            'duracion_dias',
            'requisito_logro'
        ]
        
        print("⚠️  DISCREPANCIAS DETECTADAS:")
        print("\n1️⃣  Campos con nombres diferentes:")
        for campo_modelo, campo_bd in campos_modelo_faltantes.items():
            existe = campo_bd in columnas_existentes
            status = "✓" if existe else "✗"
            print(f"   {status} Modelo: '{campo_modelo}' → BD: '{campo_bd}'")
        
        print("\n2️⃣  Campos solo en BD (22 campos):")
        for campo in campos_bd_extra[:5]:
            print(f"   • {campo}")
        print(f"   ... y {len(campos_bd_extra) - 5} más")
        
        print("\n" + "="*70)
        print("📝 RECOMENDACIONES:")
        print("="*70)
        print("""
1. OPCIÓN A - Modificar modelo Python para usar nombres de BD:
   - Renombrar campos en el modelo
   - Agregar campos faltantes (tipo, imagen_url, etc.)
   - Más trabajo pero mejor sincronización
   
2. OPCIÓN B - Crear alias/properties en el modelo:
   - Mantener nombres actuales como properties
   - Agregar columnas reales con nombres de BD
   - Menos cambios en código existente
   
3. OPCIÓN C - Migración BD para renombrar columnas:
   - Cambiar nombres en BD para coincidir con modelo
   - Más arriesgado (puede romper datos existentes)
   - No recomendado para esta etapa
        """)
        
        print("\n✅ Verificación completa")
        print("="*70 + "\n")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
