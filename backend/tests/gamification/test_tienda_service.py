"""
Tests unitarios para TiendaService

Cubre:
- Compra de items (validaciones de puntos, stock, nivel)
- Equipamiento (validación única por categoría)
- Uso de consumibles (reducir cantidad)
- Inventario del usuario
- Transacciones
- Estadísticas
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from decimal import Decimal

from src.services.gamification.tienda_service import TiendaService
from src.services.gamification.puntos_service import PuntosService
from src.models.gamification.tienda_item import TiendaItem
from src.models.gamification.inventario_usuario import InventarioUsuario
from src.enums.gamification.tienda_enums import CategoriaItem, RarezaItem


# ============================================
# FIXTURES
# ============================================

@pytest.fixture(scope="module")
def db_engine():
    """Crear engine de test (usar BD de desarrollo)"""
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/acadify_db"
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Crear sesión por test con rollback automático"""
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def usuario_test(db_session):
    """Crear usuario de prueba con puntos"""
    usuario_id = uuid4()
    
    # Crear usuario en BD
    query = text("""
        INSERT INTO "Usuario" (usuario_id, nombres, apellidos, email, password_hash, rol)
        VALUES (:usuario_id, :nombres, :apellidos, :email, :password, :rol)
        ON CONFLICT (usuario_id) DO NOTHING
    """)
    
    db_session.execute(query, {
        "usuario_id": usuario_id,
        "nombres": "Test",
        "apellidos": "Usuario",
        "email": f"test_{usuario_id}@test.com",
        "password": "hash123",
        "rol": "estudiante"
    })
    
    # Dar puntos al usuario
    puntos_service = PuntosService(db_session)
    puntos_service.agregar_puntos_sync(
        usuario_id=usuario_id,
        cantidad=1000,
        razon="Puntos iniciales para tests",
        tipo_evento="test"
    )
    
    db_session.commit()
    
    yield usuario_id
    
    # Cleanup se hace con rollback automático


@pytest.fixture(scope="function")
def item_test(db_session):
    """Crear item de prueba en tienda"""
    item = TiendaItem(
        item_id=uuid4(),
        nombre="Avatar de Prueba",
        descripcion="Item para testing",
        categoria=CategoriaItem.CABELLO,
        rareza=RarezaItem.COMUN,
        precio_puntos=100,
        nivel_minimo_requerido=1,
        es_consumible=False,
        activo=True,
        disponible_desde=datetime.now(timezone.utc) - timedelta(days=1),
        disponible_hasta=datetime.now(timezone.utc) + timedelta(days=30)
    )
    
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    
    yield item


@pytest.fixture(scope="function")
def item_consumible_test(db_session):
    """Crear item consumible de prueba"""
    item = TiendaItem(
        item_id=uuid4(),
        nombre="Congelador de Racha",
        descripcion="Protege tu racha por 3 días",
        categoria=CategoriaItem.FUNCIONAL,
        rareza=RarezaItem.RARO,
        precio_puntos=200,
        nivel_minimo_requerido=1,
        es_consumible=True,
        usos_maximos=3,
        activo=True
    )
    
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    
    yield item


# ============================================
# TESTS: Compra de Items
# ============================================

@pytest.mark.asyncio
async def test_comprar_item_exitoso(db_session, usuario_test, item_test):
    """Test: Compra exitosa de item"""
    tienda_service = TiendaService(db_session)
    
    # Comprar item
    resultado = await tienda_service.comprar_item(
        usuario_id=usuario_test,
        item_id=item_test.item_id,
        cantidad=1
    )
    
    assert resultado is not None
    assert "inventario_id" in resultado
    assert resultado["item_id"] == item_test.item_id
    assert resultado["cantidad"] == 1
    
    # Verificar que se agregó al inventario
    inventario = db_session.query(InventarioUsuario).filter(
        InventarioUsuario.usuario_id == usuario_test,
        InventarioUsuario.item_id == item_test.item_id
    ).first()
    
    assert inventario is not None
    assert inventario.cantidad == 1


@pytest.mark.asyncio
async def test_comprar_item_sin_puntos(db_session, usuario_test, item_test):
    """Test: Error al comprar sin puntos suficientes"""
    tienda_service = TiendaService(db_session)
    
    # Gastar todos los puntos
    query = text("""
        INSERT INTO historial_puntos (usuario_id, cantidad, razon, tipo_evento)
        VALUES (:usuario_id, :cantidad, :razon, :tipo)
    """)
    
    db_session.execute(query, {
        "usuario_id": usuario_test,
        "cantidad": -1000,
        "razon": "Gastar puntos para test",
        "tipo": "test"
    })
    db_session.commit()
    
    # Intentar comprar
    with pytest.raises(Exception) as exc_info:
        await tienda_service.comprar_item(
            usuario_id=usuario_test,
            item_id=item_test.item_id,
            cantidad=1
        )
    
    assert "puntos insuficientes" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_comprar_item_sin_stock(db_session, usuario_test, item_test):
    """Test: Error al comprar item sin stock"""
    tienda_service = TiendaService(db_session)
    
    # Poner stock limitado
    item_test.stock_limitado = True
    item_test.stock_disponible = 0
    db_session.commit()
    
    # Intentar comprar
    with pytest.raises(Exception) as exc_info:
        await tienda_service.comprar_item(
            usuario_id=usuario_test,
            item_id=item_test.item_id,
            cantidad=1
        )
    
    assert "stock" in str(exc_info.value).lower() or "disponible" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_comprar_item_duplicado_no_consumible(db_session, usuario_test, item_test):
    """Test: No se puede comprar item no-consumible duplicado"""
    tienda_service = TiendaService(db_session)
    
    # Primera compra (exitosa)
    await tienda_service.comprar_item(
        usuario_id=usuario_test,
        item_id=item_test.item_id,
        cantidad=1
    )
    
    # Segunda compra (debe fallar)
    with pytest.raises(Exception) as exc_info:
        await tienda_service.comprar_item(
            usuario_id=usuario_test,
            item_id=item_test.item_id,
            cantidad=1
        )
    
    assert "ya posees" in str(exc_info.value).lower() or "duplicado" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_comprar_consumible_multiples_veces(db_session, usuario_test, item_consumible_test):
    """Test: Se puede comprar consumible múltiples veces (suma cantidad)"""
    tienda_service = TiendaService(db_session)
    
    # Dar puntos extra
    puntos_service = PuntosService(db_session)
    await puntos_service.agregar_puntos(
        usuario_id=usuario_test,
        cantidad=1000,
        razon="Puntos extra para test",
        tipo_evento="test"
    )
    
    # Primera compra
    resultado1 = await tienda_service.comprar_item(
        usuario_id=usuario_test,
        item_id=item_consumible_test.item_id,
        cantidad=2
    )
    
    assert resultado1["cantidad"] == 2
    
    # Segunda compra (debe sumar)
    resultado2 = await tienda_service.comprar_item(
        usuario_id=usuario_test,
        item_id=item_consumible_test.item_id,
        cantidad=3
    )
    
    # Debe tener total de 5
    inventario = db_session.query(InventarioUsuario).filter(
        InventarioUsuario.usuario_id == usuario_test,
        InventarioUsuario.item_id == item_consumible_test.item_id
    ).first()
    
    assert inventario.cantidad == 5


# ============================================
# TESTS: Equipamiento
# ============================================

@pytest.mark.asyncio
async def test_equipar_item(db_session, usuario_test, item_test):
    """Test: Equipar item exitosamente"""
    tienda_service = TiendaService(db_session)
    
    # Comprar item primero
    compra = await tienda_service.comprar_item(
        usuario_id=usuario_test,
        item_id=item_test.item_id,
        cantidad=1
    )
    
    inventario_id = compra["inventario_id"]
    
    # Equipar item
    resultado = await tienda_service.equipar_item(
        usuario_id=usuario_test,
        inventario_id=inventario_id
    )
    
    assert resultado["equipado"] is True
    
    # Verificar en BD
    inventario = db_session.query(InventarioUsuario).filter(
        InventarioUsuario.inventario_id == inventario_id
    ).first()
    
    assert inventario.equipado is True
    assert inventario.fecha_equipado is not None


@pytest.mark.asyncio
async def test_equipar_item_desequipa_anterior(db_session, usuario_test):
    """Test: Al equipar item de misma categoría, desequipa el anterior"""
    tienda_service = TiendaService(db_session)
    
    # Crear 2 items de la misma categoría
    item1 = TiendaItem(
        item_id=uuid4(),
        nombre="Cabello 1",
        categoria=CategoriaItem.CABELLO,
        rareza=RarezaItem.COMUN,
        precio_puntos=100,
        activo=True
    )
    
    item2 = TiendaItem(
        item_id=uuid4(),
        nombre="Cabello 2",
        categoria=CategoriaItem.CABELLO,
        rareza=RarezaItem.RARO,
        precio_puntos=200,
        activo=True
    )
    
    db_session.add_all([item1, item2])
    db_session.commit()
    
    # Comprar ambos
    compra1 = await tienda_service.comprar_item(usuario_test, item1.item_id, 1)
    compra2 = await tienda_service.comprar_item(usuario_test, item2.item_id, 1)
    
    # Equipar primer item
    await tienda_service.equipar_item(usuario_test, compra1["inventario_id"])
    
    # Verificar que está equipado
    inv1 = db_session.query(InventarioUsuario).filter(
        InventarioUsuario.inventario_id == compra1["inventario_id"]
    ).first()
    assert inv1.equipado is True
    
    # Equipar segundo item (debe desequipar el primero)
    await tienda_service.equipar_item(usuario_test, compra2["inventario_id"])
    
    # Refrescar y verificar
    db_session.refresh(inv1)
    inv2 = db_session.query(InventarioUsuario).filter(
        InventarioUsuario.inventario_id == compra2["inventario_id"]
    ).first()
    
    assert inv1.equipado is False  # Primer item desequipado
    assert inv2.equipado is True   # Segundo item equipado


# ============================================
# TESTS: Uso de Consumibles
# ============================================

@pytest.mark.asyncio
async def test_usar_consumible(db_session, usuario_test, item_consumible_test):
    """Test: Usar item consumible reduce cantidad"""
    tienda_service = TiendaService(db_session)
    
    # Comprar consumible
    compra = await tienda_service.comprar_item(
        usuario_id=usuario_test,
        item_id=item_consumible_test.item_id,
        cantidad=3
    )
    
    inventario_id = compra["inventario_id"]
    
    # Usar 1 unidad
    resultado = await tienda_service.usar_item_consumible(
        usuario_id=usuario_test,
        inventario_id=inventario_id,
        cantidad_usar=1
    )
    
    assert resultado["cantidad_restante"] == 2
    
    # Verificar en BD
    inventario = db_session.query(InventarioUsuario).filter(
        InventarioUsuario.inventario_id == inventario_id
    ).first()
    
    assert inventario.cantidad == 2


@pytest.mark.asyncio
async def test_usar_consumible_elimina_al_llegar_a_cero(db_session, usuario_test, item_consumible_test):
    """Test: Al usar última unidad, se elimina del inventario"""
    tienda_service = TiendaService(db_session)
    
    # Comprar 1 unidad
    compra = await tienda_service.comprar_item(
        usuario_id=usuario_test,
        item_id=item_consumible_test.item_id,
        cantidad=1
    )
    
    inventario_id = compra["inventario_id"]
    
    # Usar la única unidad
    resultado = await tienda_service.usar_item_consumible(
        usuario_id=usuario_test,
        inventario_id=inventario_id,
        cantidad_usar=1
    )
    
    assert resultado["cantidad_restante"] == 0
    assert resultado["item_eliminado"] is True
    
    # Verificar que ya no existe en BD
    inventario = db_session.query(InventarioUsuario).filter(
        InventarioUsuario.inventario_id == inventario_id
    ).first()
    
    assert inventario is None


@pytest.mark.asyncio
async def test_usar_item_no_consumible_error(db_session, usuario_test, item_test):
    """Test: Error al intentar usar item no consumible"""
    tienda_service = TiendaService(db_session)
    
    # Comprar item no consumible
    compra = await tienda_service.comprar_item(
        usuario_id=usuario_test,
        item_id=item_test.item_id,
        cantidad=1
    )
    
    # Intentar usar
    with pytest.raises(Exception) as exc_info:
        await tienda_service.usar_item_consumible(
            usuario_id=usuario_test,
            inventario_id=compra["inventario_id"],
            cantidad_usar=1
        )
    
    assert "no es consumible" in str(exc_info.value).lower()


# ============================================
# TESTS: Catálogo y Búsqueda
# ============================================

@pytest.mark.asyncio
async def test_obtener_catalogo_con_filtros(db_session, item_test):
    """Test: Obtener catálogo con filtros"""
    tienda_service = TiendaService(db_session)
    
    # Sin filtros
    catalogo = await tienda_service.get_catalogo_items(
        limit=100,
        offset=0
    )
    
    assert len(catalogo) > 0
    assert any(item["item_id"] == item_test.item_id for item in catalogo)
    
    # Con filtro de categoría
    catalogo_cabello = await tienda_service.get_catalogo_items(
        categoria=CategoriaItem.CABELLO,
        limit=100
    )
    
    assert all(item["categoria"] == "CABELLO" for item in catalogo_cabello)
    
    # Con filtro de rareza
    catalogo_comun = await tienda_service.get_catalogo_items(
        rareza=RarezaItem.COMUN,
        limit=100
    )
    
    assert all(item["rareza"] == "COMUN" for item in catalogo_comun)


@pytest.mark.asyncio
async def test_buscar_items_por_nombre(db_session, item_test):
    """Test: Buscar items por nombre"""
    tienda_service = TiendaService(db_session)
    
    # Buscar por término
    resultados = await tienda_service.get_catalogo_items(
        buscar="Avatar",
        limit=100
    )
    
    assert len(resultados) > 0
    assert any("avatar" in item["nombre"].lower() for item in resultados)


# ============================================
# TESTS: Inventario y Estadísticas
# ============================================

@pytest.mark.asyncio
async def test_obtener_inventario_usuario(db_session, usuario_test, item_test):
    """Test: Obtener inventario del usuario"""
    tienda_service = TiendaService(db_session)
    
    # Comprar varios items
    await tienda_service.comprar_item(usuario_test, item_test.item_id, 1)
    
    # Obtener inventario
    inventario = await tienda_service.get_inventario_usuario(
        usuario_id=usuario_test
    )
    
    assert len(inventario) > 0
    assert any(item["item_id"] == item_test.item_id for item in inventario)


@pytest.mark.asyncio
async def test_obtener_transacciones_usuario(db_session, usuario_test, item_test):
    """Test: Obtener historial de transacciones"""
    tienda_service = TiendaService(db_session)
    
    # Realizar compra
    await tienda_service.comprar_item(usuario_test, item_test.item_id, 1)
    
    # Obtener transacciones
    transacciones = await tienda_service.get_transacciones_usuario(
        usuario_id=usuario_test
    )
    
    assert len(transacciones) > 0
    assert transacciones[0]["item_id"] == item_test.item_id
    assert transacciones[0]["exitosa"] is True


@pytest.mark.asyncio
async def test_obtener_estadisticas_usuario(db_session, usuario_test, item_test):
    """Test: Obtener estadísticas de compras"""
    tienda_service = TiendaService(db_session)
    
    # Realizar compra
    await tienda_service.comprar_item(usuario_test, item_test.item_id, 1)
    
    # Obtener estadísticas
    stats = await tienda_service.get_estadisticas_usuario(
        usuario_id=usuario_test
    )
    
    assert stats["total_items_comprados"] >= 1
    assert stats["total_puntos_gastados"] >= 100
    assert stats["items_equipados"] >= 0


# ============================================
# TESTS: Validaciones
# ============================================

@pytest.mark.asyncio
async def test_validar_nivel_minimo(db_session, usuario_test):
    """Test: No se puede comprar item sin nivel mínimo"""
    tienda_service = TiendaService(db_session)
    
    # Crear item con nivel alto
    item = TiendaItem(
        item_id=uuid4(),
        nombre="Item Premium",
        categoria=CategoriaItem.ROPA,
        rareza=RarezaItem.LEGENDARIO,
        precio_puntos=5000,
        nivel_minimo_requerido=50,  # Nivel alto
        activo=True
    )
    
    db_session.add(item)
    db_session.commit()
    
    # Intentar comprar (usuario es nivel 1)
    with pytest.raises(Exception) as exc_info:
        await tienda_service.comprar_item(
            usuario_id=usuario_test,
            item_id=item.item_id,
            cantidad=1
        )
    
    assert "nivel" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_item_no_disponible_aun(db_session, usuario_test):
    """Test: No se puede comprar item que aún no está disponible"""
    tienda_service = TiendaService(db_session)
    
    # Crear item disponible en el futuro
    item = TiendaItem(
        item_id=uuid4(),
        nombre="Item Futuro",
        categoria=CategoriaItem.ROPA,
        rareza=RarezaItem.COMUN,
        precio_puntos=100,
        disponible_desde=datetime.now(timezone.utc) + timedelta(days=10),
        activo=True
    )
    
    db_session.add(item)
    db_session.commit()
    
    # Intentar comprar
    with pytest.raises(Exception) as exc_info:
        await tienda_service.comprar_item(
            usuario_id=usuario_test,
            item_id=item.item_id,
            cantidad=1
        )
    
    assert "disponible" in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
