"""
Test rápido para verificar que el modelo TiendaItem refactorizado funciona correctamente
"""
import asyncio
import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect
from src.db.base_class import Base
from src.models.gamification.tienda_item import TiendaItem


def test_model_columns():
    """Verifica que todos los campos del modelo están definidos correctamente"""
    print("\n" + "="*70)
    print("🧪 TEST: Verificando modelo TiendaItem refactorizado")
    print("="*70 + "\n")
    
    # Obtener columnas del modelo usando SQLAlchemy inspect
    mapper = inspect(TiendaItem)
    columns = {col.key: col for col in mapper.columns}
    
    # Campos esperados según la BD
    campos_esperados = {
        # Campos básicos
        'item_id': 'UUID',
        'nombre': 'String',
        'descripcion': 'String',
        'categoria': 'Enum',
        'tipo': 'String',  # NUEVO - requerido
        'rareza': 'Enum',
        
        # Precios y descuentos
        'precio_puntos': 'Integer',
        'precio_original': 'Integer',  # NUEVO
        'descuento_porcentaje': 'Integer',  # NUEVO
        
        # Imágenes
        'imagen_url': 'String',  # NUEVO
        'imagen_preview_url': 'String',  # RENOMBRADO desde preview_url
        'icono_url': 'String',  # NUEVO
        'color_hex': 'String',  # NUEVO
        
        # Stock y disponibilidad
        'es_disponible': 'Boolean',  # RENOMBRADO desde es_activo
        'stock_limitado': 'Boolean',  # NUEVO
        'stock_actual': 'Integer',  # RENOMBRADO desde stock_disponible
        'max_por_usuario': 'Integer',  # NUEVO
        
        # Requisitos
        'nivel_minimo': 'Integer',  # RENOMBRADO desde nivel_minimo_requerido, cambiado de String
        'requisito_logro': 'JSON',  # NUEVO
        
        # Referencias
        'avatar_asset_id': 'UUID',  # RENOMBRADO desde asset_id
        'recompensa_id': 'UUID',  # NUEVO
        
        # Temporales
        'duracion_dias': 'Integer',
        'fecha_inicio': 'TIMESTAMP',  # RENOMBRADO desde disponible_desde
        'fecha_fin': 'TIMESTAMP',  # RENOMBRADO desde disponible_hasta
        
        # Estadísticas
        'veces_comprado': 'Integer',  # NUEVO
        'popularidad': 'Integer',  # NUEVO
        
        # Metadata
        'efecto_json': 'JSON',
        'orden': 'Integer',  # RENOMBRADO desde orden_visualizacion
        'es_destacado': 'Boolean',  # NUEVO
        'es_nuevo': 'Boolean',  # NUEVO
        
        # Auditoría
        'fecha_creacion': 'TIMESTAMP',
        'fecha_actualizacion': 'TIMESTAMP'
    }
    
    print("📋 Verificando campos del modelo:\n")
    
    # Verificar que todos los campos esperados existen
    errores = []
    exitos = []
    
    for campo, tipo_esperado in campos_esperados.items():
        if campo in columns:
            col = columns[campo]
            tipo_actual = col.type.__class__.__name__
            
            # Normalizar tipos para comparación
            if tipo_esperado == 'String' and 'String' in tipo_actual:
                exitos.append(f"   ✅ {campo:25} → {tipo_actual}")
            elif tipo_esperado == 'Integer' and tipo_actual == 'Integer':
                exitos.append(f"   ✅ {campo:25} → {tipo_actual}")
            elif tipo_esperado == 'Boolean' and tipo_actual == 'Boolean':
                exitos.append(f"   ✅ {campo:25} → {tipo_actual}")
            elif tipo_esperado == 'UUID' and tipo_actual == 'UUID':
                exitos.append(f"   ✅ {campo:25} → {tipo_actual}")
            elif tipo_esperado == 'Enum' and tipo_actual == 'Enum':
                exitos.append(f"   ✅ {campo:25} → {tipo_actual}")
            elif tipo_esperado == 'JSON' and tipo_actual == 'JSON':
                exitos.append(f"   ✅ {campo:25} → {tipo_actual}")
            elif tipo_esperado == 'TIMESTAMP' and 'TIMESTAMP' in tipo_actual:
                exitos.append(f"   ✅ {campo:25} → {tipo_actual}")
            else:
                errores.append(f"   ⚠️  {campo:25} → Esperado: {tipo_esperado}, Encontrado: {tipo_actual}")
        else:
            errores.append(f"   ❌ {campo:25} → FALTA EN EL MODELO")
    
    # Mostrar resultados
    for exito in exitos:
        print(exito)
    
    if errores:
        print("\n⚠️  PROBLEMAS ENCONTRADOS:\n")
        for error in errores:
            print(error)
    
    # Verificar campos obsoletos que NO deberían estar
    campos_obsoletos = [
        'preview_url',
        'nivel_minimo_requerido',
        'es_activo',
        'stock_disponible',
        'disponible_desde',
        'disponible_hasta',
        'orden_visualizacion',
        'asset_id',  # debe ser avatar_asset_id
        'subcategoria',
        'puntos_minimos_requeridos'
    ]
    
    print("\n🔍 Verificando que campos obsoletos fueron eliminados:\n")
    campos_obsoletos_encontrados = []
    
    for campo in campos_obsoletos:
        if campo in columns:
            campos_obsoletos_encontrados.append(f"   ⚠️  {campo} - DEBERÍA SER ELIMINADO")
        else:
            print(f"   ✅ {campo:25} → Correctamente eliminado")
    
    if campos_obsoletos_encontrados:
        print("\n⚠️  CAMPOS OBSOLETOS ENCONTRADOS:\n")
        for obs in campos_obsoletos_encontrados:
            print(obs)
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN:")
    print("="*70)
    print(f"   ✅ Campos correctos:     {len(exitos)}")
    print(f"   ⚠️  Problemas:           {len(errores)}")
    print(f"   ⚠️  Campos obsoletos:    {len(campos_obsoletos_encontrados)}")
    
    total_campos = len(columns)
    print(f"\n   📦 Total campos modelo:  {total_campos}")
    print(f"   📋 Campos esperados:     {len(campos_esperados)}")
    
    if len(errores) == 0 and len(campos_obsoletos_encontrados) == 0:
        print("\n   ✨ ¡MODELO REFACTORIZADO CORRECTAMENTE! ✨")
        return True
    else:
        print("\n   ⚠️  Hay problemas que necesitan corrección")
        return False


if __name__ == "__main__":
    try:
        success = test_model_columns()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
