"""
Tests para API de Tienda e Inventario.

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestTiendaCatalogo:
    """Tests para GET /api/gamification/tienda/catalogo"""
    
    async def test_obtener_catalogo_exitoso(self, client, estudiante_headers, items_catalogo):
        """Debe retornar catálogo de items."""
        response = await client.get(
            "/api/gamification/tienda/catalogo",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    async def test_catalogo_filtros_multiples(self, client, estudiante_headers, items_catalogo):
        """Debe aplicar múltiples filtros."""
        response = await client.get(
            "/api/gamification/tienda/catalogo?categoria=avatar_cabeza&rareza=comun",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200


class TestComprarItem:
    """Tests para POST /api/gamification/tienda/comprar"""
    
    async def test_comprar_item_exitoso(self, client, estudiante_headers, item_tienda_sample, usuario_puntos, db_session):
        """Debe comprar item con puntos suficientes."""
        usuario_puntos.puntos_acumulados = 1000
        db_session.commit()
        
        payload = {
            "item_id": str(item_tienda_sample.item_id),
            "cantidad": 1
        }
        
        response = await client.post(
            "/api/gamification/tienda/comprar",
            json=payload,
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "transaccion_id" in data
        assert "inventario_id" in data
    
    async def test_comprar_item_cantidad_multiple(self, client, estudiante_headers, item_tienda_sample, usuario_puntos, db_session):
        """Debe comprar múltiples unidades."""
        usuario_puntos.puntos_acumulados = 5000
        db_session.commit()
        
        payload = {
            "item_id": str(item_tienda_sample.item_id),
            "cantidad": 3
        }
        
        response = await client.post(
            "/api/gamification/tienda/comprar",
            json=payload,
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        assert response.json()["cantidad"] == 3


class TestInventario:
    """Tests para GET /api/gamification/tienda/inventario"""
    
    async def test_obtener_inventario(self, client, estudiante_headers, inventario_item):
        """Debe retornar inventario del usuario."""
        response = await client.get(
            "/api/gamification/tienda/inventario",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "equipados" in data


class TestEquiparItem:
    """Tests para POST /api/gamification/tienda/equipar/{id}"""
    
    async def test_equipar_item_exitoso(self, client, estudiante_headers, inventario_item):
        """Debe equipar item del inventario."""
        response = await client.post(
            f"/api/gamification/tienda/equipar/{inventario_item.inventario_id}",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "item_equipado" in data


class TestTransacciones:
    """Tests para GET /api/gamification/tienda/transacciones"""
    
    async def test_obtener_transacciones(self, client, estudiante_headers):
        """Debe retornar historial de transacciones."""
        response = await client.get(
            "/api/gamification/tienda/transacciones",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "transacciones" in data
        assert "total" in data


# Integración
class TestTiendaIntegracion:
    """Tests de flujo completo de tienda."""
    
    async def test_flujo_comprar_equipar_usar(
        self,
        client,
        estudiante_headers,
        item_tienda_sample,
        usuario_puntos,
        db_session
    ):
        """Test: Comprar → Ver inventario → Equipar → Ver estadísticas."""
        # 1. Asegurar puntos
        usuario_puntos.puntos_acumulados = 2000
        db_session.commit()
        
        # 2. Comprar
        response = await client.post(
            "/api/gamification/tienda/comprar",
            json={"item_id": str(item_tienda_sample.item_id), "cantidad": 1},
            headers=estudiante_headers
        )
        assert response.status_code == 200
        inventario_id = response.json()["inventario_id"]
        
        # 3. Ver inventario
        response = await client.get(
            "/api/gamification/tienda/inventario",
            headers=estudiante_headers
        )
        assert response.status_code == 200
        assert response.json()["total"] > 0
        
        # 4. Equipar
        response = await client.post(
            f"/api/gamification/tienda/equipar/{inventario_id}",
            headers=estudiante_headers
        )
        assert response.status_code == 200
