"""
Tests para API de Etiquetas (Badges).

Cubre:
- GET /api/gamification/etiquetas/catalogo
- POST /api/gamification/etiquetas/comprar/{id}
- GET /api/gamification/etiquetas/me
- POST /api/gamification/etiquetas/equipar
- POST /api/gamification/etiquetas/desequipar/{id}
- GET /api/gamification/etiquetas/evolucion/{id}
- POST /api/gamification/etiquetas/evolucionar/{id}
- GET /api/gamification/etiquetas/estadisticas

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
Version: 1.0.0
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestEtiquetasCatalogo:
    """Tests para GET /api/gamification/etiquetas/catalogo"""
    
    async def test_obtener_catalogo_exitoso(self, client, estudiante_headers, etiquetas_catalogo):
        """Debe retornar catálogo de etiquetas."""
        response = await client.get(
            "/api/gamification/etiquetas/catalogo",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "etiquetas" in data
        assert "total" in data
        assert isinstance(data["etiquetas"], list)
    
    async def test_catalogo_filtro_categoria(self, client, estudiante_headers, etiquetas_catalogo):
        """Debe filtrar por categoría."""
        response = await client.get(
            "/api/gamification/etiquetas/catalogo?categoria=programacion",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "filtros_aplicados" in data
        if data["total"] > 0:
            assert all(e["categoria"] == "programacion" for e in data["etiquetas"])
    
    async def test_catalogo_filtro_rareza(self, client, estudiante_headers, etiquetas_catalogo):
        """Debe filtrar por rareza."""
        response = await client.get(
            "/api/gamification/etiquetas/catalogo?rareza=epico",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        if data["total"] > 0:
            assert all(e["rareza"] == "epico" for e in data["etiquetas"])
    
    async def test_catalogo_busqueda(self, client, estudiante_headers, etiquetas_catalogo):
        """Debe buscar por nombre."""
        response = await client.get(
            "/api/gamification/etiquetas/catalogo?buscar=Badge",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200


class TestComprarEtiqueta:
    """Tests para POST /api/gamification/etiquetas/comprar/{id}"""
    
    async def test_comprar_etiqueta_exitoso(self, client, estudiante_headers, etiqueta_sample, usuario_puntos, db_session):
        """Debe comprar etiqueta con puntos suficientes."""
        # Asegurar puntos suficientes
        usuario_puntos.puntos_acumulados = 1000
        db_session.commit()
        
        response = await client.post(
            f"/api/gamification/etiquetas/comprar/{etiqueta_sample.etiqueta_id}",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "etiqueta" in data
        assert "puntos_gastados" in data
        assert "puntos_restantes" in data
    
    async def test_comprar_etiqueta_puntos_insuficientes(self, client, estudiante_headers, etiqueta_sample, usuario_puntos, db_session):
        """Debe fallar con puntos insuficientes."""
        usuario_puntos.puntos_acumulados = 100
        db_session.commit()
        
        response = await client.post(
            f"/api/gamification/etiquetas/comprar/{etiqueta_sample.etiqueta_id}",
            headers=estudiante_headers
        )
        
        assert response.status_code == 400
    
    async def test_comprar_etiqueta_duplicada(self, client, estudiante_headers, etiqueta_sample, usuario_etiqueta, usuario_puntos):
        """Debe fallar si ya posee la etiqueta."""
        response = await client.post(
            f"/api/gamification/etiquetas/comprar/{etiqueta_sample.etiqueta_id}",
            headers=estudiante_headers
        )
        
        assert response.status_code == 409
    
    async def test_comprar_etiqueta_inexistente(self, client, estudiante_headers):
        """Debe fallar con ID inexistente."""
        response = await client.post(
            f"/api/gamification/etiquetas/comprar/{uuid4()}",
            headers=estudiante_headers
        )
        
        assert response.status_code == 404


class TestMisEtiquetas:
    """Tests para GET /api/gamification/etiquetas/me"""
    
    async def test_obtener_mis_etiquetas(self, client, estudiante_headers, usuario_etiqueta):
        """Debe retornar etiquetas del usuario."""
        response = await client.get(
            "/api/gamification/etiquetas/me",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "etiquetas" in data
        assert "total" in data
        assert "equipadas" in data
    
    async def test_filtro_equipadas_solo(self, client, estudiante_headers, usuario_etiqueta, db_session):
        """Debe filtrar solo equipadas."""
        usuario_etiqueta.esta_equipada = True
        db_session.commit()
        
        response = await client.get(
            "/api/gamification/etiquetas/me?equipadas_solo=true",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        if data["total"] > 0:
            assert all(e["esta_equipada"] for e in data["etiquetas"])


class TestEquiparEtiquetas:
    """Tests para POST /api/gamification/etiquetas/equipar"""
    
    async def test_equipar_etiquetas_exitoso(self, client, estudiante_headers, usuario_etiqueta):
        """Debe equipar etiquetas."""
        payload = {
            "etiquetas_ids": [str(usuario_etiqueta.usuario_etiqueta_id)]
        }
        
        response = await client.post(
            "/api/gamification/etiquetas/equipar",
            json=payload,
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["etiquetas_equipadas"] == 1
    
    async def test_equipar_maximo_5_etiquetas(self, client, estudiante_headers, db_session, estudiante_user, etiquetas_catalogo):
        """No debe permitir más de 5 etiquetas."""
        from src.models.gamification import UsuarioEtiqueta
        
        # Crear 6 etiquetas del usuario
        etiquetas_ids = []
        for i in range(6):
            ue = UsuarioEtiqueta(
                usuario_etiqueta_id=uuid4(),
                usuario_id=estudiante_user.usuario_id,
                etiqueta_id=etiquetas_catalogo[i % 3].etiqueta_id,
                fecha_obtencion=datetime.utcnow(),
                metodo_obtencion="test"
            )
            db_session.add(ue)
            etiquetas_ids.append(str(ue.usuario_etiqueta_id))
        db_session.commit()
        
        payload = {"etiquetas_ids": etiquetas_ids}
        
        response = await client.post(
            "/api/gamification/etiquetas/equipar",
            json=payload,
            headers=estudiante_headers
        )
        
        assert response.status_code == 422  # Validation error


class TestDesequiparEtiqueta:
    """Tests para POST /api/gamification/etiquetas/desequipar/{id}"""
    
    async def test_desequipar_etiqueta_exitoso(self, client, estudiante_headers, usuario_etiqueta, db_session):
        """Debe desequipar etiqueta."""
        # Asegurar que está equipada
        usuario_etiqueta.esta_equipada = True
        db_session.commit()
        
        response = await client.post(
            f"/api/gamification/etiquetas/desequipar/{usuario_etiqueta.usuario_etiqueta_id}",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "mensaje" in data
    
    async def test_desequipar_etiqueta_no_equipada(self, client, estudiante_headers, usuario_etiqueta, db_session):
        """Debe fallar si no está equipada."""
        usuario_etiqueta.esta_equipada = False
        db_session.commit()
        
        response = await client.post(
            f"/api/gamification/etiquetas/desequipar/{usuario_etiqueta.usuario_etiqueta_id}",
            headers=estudiante_headers
        )
        
        assert response.status_code == 400


class TestEvolucionEtiqueta:
    """Tests para GET /api/gamification/etiquetas/evolucion/{id}"""
    
    async def test_verificar_evolucion(self, client, estudiante_headers, usuario_etiqueta):
        """Debe verificar si puede evolucionar."""
        response = await client.get(
            f"/api/gamification/etiquetas/evolucion/{usuario_etiqueta.usuario_etiqueta_id}",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "puede_evolucionar" in data
        assert "requisitos" in data


class TestEvolucionarEtiqueta:
    """Tests para POST /api/gamification/etiquetas/evolucionar/{id}"""
    
    async def test_evolucionar_etiqueta_sin_evolucion(self, client, estudiante_headers, usuario_etiqueta, db_session):
        """Debe fallar si etiqueta no tiene evolución."""
        from src.models.gamification import EtiquetaPerfil
        
        etiqueta = db_session.get(EtiquetaPerfil, usuario_etiqueta.etiqueta_id)
        etiqueta.etiqueta_evolucion_id = None
        db_session.commit()
        
        response = await client.post(
            f"/api/gamification/etiquetas/evolucionar/{usuario_etiqueta.usuario_etiqueta_id}",
            headers=estudiante_headers
        )
        
        assert response.status_code == 400


class TestEstadisticasEtiquetas:
    """Tests para GET /api/gamification/etiquetas/estadisticas"""
    
    async def test_obtener_estadisticas(self, client, estudiante_headers, usuario_etiqueta):
        """Debe retornar estadísticas."""
        response = await client.get(
            "/api/gamification/etiquetas/estadisticas",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_etiquetas" in data
        assert "etiquetas_equipadas" in data
        assert "por_metodo" in data
        assert "por_rareza" in data
        assert "por_categoria" in data


# Tests de integración
class TestEtiquetasIntegracion:
    """Tests de flujo completo de etiquetas."""
    
    async def test_flujo_comprar_y_equipar(
        self,
        client,
        estudiante_headers,
        etiqueta_sample,
        usuario_puntos,
        db_session
    ):
        """Test: Comprar → Ver colección → Equipar → Ver estadísticas."""
        # 1. Asegurar puntos
        usuario_puntos.puntos_acumulados = 1000
        db_session.commit()
        
        # 2. Comprar etiqueta
        response = await client.post(
            f"/api/gamification/etiquetas/comprar/{etiqueta_sample.etiqueta_id}",
            headers=estudiante_headers
        )
        assert response.status_code == 200
        
        # 3. Ver colección
        response = await client.get(
            "/api/gamification/etiquetas/me",
            headers=estudiante_headers
        )
        assert response.status_code == 200
        assert response.json()["total"] > 0
        
        # 4. Equipar
        etiquetas = response.json()["etiquetas"]
        payload = {"etiquetas_ids": [etiquetas[0]["usuario_etiqueta_id"]]}
        
        response = await client.post(
            "/api/gamification/etiquetas/equipar",
            json=payload,
            headers=estudiante_headers
        )
        assert response.status_code == 200
        
        # 5. Ver estadísticas
        response = await client.get(
            "/api/gamification/etiquetas/estadisticas",
            headers=estudiante_headers
        )
        assert response.status_code == 200
        assert response.json()["etiquetas_equipadas"] == 1
