"""
Tests para API de Puntos.

Cubre:
- GET /api/gamification/puntos/me
- GET /api/gamification/puntos/ranking
- GET /api/gamification/puntos/ranking/me
- POST /api/gamification/puntos/otorgar (admin)
- GET /api/gamification/puntos/historial
- GET /api/gamification/puntos/nivel/info

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
Version: 1.0.0
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4


class TestPuntosMe:
    """Tests para GET /api/gamification/puntos/me"""
    
    async def test_obtener_puntos_exitoso(self, client, estudiante_headers, usuario_puntos):
        """Debe retornar puntos del usuario."""
        response = await client.get(
            "/api/gamification/puntos/me",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "puntos_acumulados" in data
        assert data["puntos_acumulados"] == 1000
    
    async def test_obtener_puntos_sin_auth(self, client):
        """Debe fallar sin autenticación."""
        response = await client.get("/api/gamification/puntos/me")
        
        assert response.status_code == 401
    
    async def test_obtener_puntos_incluye_historial(self, client, estudiante_headers, usuario_puntos, historial_puntos):
        """Debe incluir historial reciente."""
        response = await client.get(
            "/api/gamification/puntos/me",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "historial_reciente" in data
        assert isinstance(data["historial_reciente"], list)
        assert len(data["historial_reciente"]) <= 10
    
    async def test_obtener_puntos_incluye_insignias(self, client, estudiante_headers, usuario_puntos):
        """Debe incluir lista de insignias."""
        response = await client.get(
            "/api/gamification/puntos/me",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "insignias" in data
        assert isinstance(data["insignias"], list)


class TestPuntosRanking:
    """Tests para GET /api/gamification/puntos/ranking"""
    
    async def test_obtener_ranking_exitoso(self, client, estudiante_headers, multiple_users):
        """Debe retornar ranking paginado."""
        response = await client.get(
            "/api/gamification/puntos/ranking",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["data"], list)
    
    async def test_ranking_paginacion(self, client, estudiante_headers):
        """Debe respetar parámetros de paginación."""
        response = await client.get(
            "/api/gamification/puntos/ranking?limit=5&offset=0",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 5
        assert data["offset"] == 0
        assert len(data["data"]) <= 5
    
    async def test_ranking_validacion_limit(self, client, estudiante_headers):
        """Debe validar límite máximo."""
        response = await client.get(
            "/api/gamification/puntos/ranking?limit=300",
            headers=estudiante_headers
        )
        
        # Debe fallar o ajustar a máximo permitido (200)
        assert response.status_code in [200, 422]
    
    async def test_ranking_ordenado_descendente(self, client, estudiante_headers, multiple_users, db_session):
        """Debe ordenar por puntos descendente."""
        # Asignar puntos diferentes a usuarios
        from src.models.gamification import UsuarioPuntos
        for i, user in enumerate(multiple_users[:3]):
            puntos = UsuarioPuntos(
                usuario_id=user.usuario_id,
                puntos_acumulados=1000 * (3 - i)  # 3000, 2000, 1000
            )
            db_session.add(puntos)
        db_session.commit()
        
        response = await client.get(
            "/api/gamification/puntos/ranking?limit=3",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        ranking = data["data"]
        
        # Verificar orden descendente
        for i in range(len(ranking) - 1):
            assert ranking[i]["puntos"] >= ranking[i + 1]["puntos"]


class TestPuntosRankingMe:
    """Tests para GET /api/gamification/puntos/ranking/me"""
    
    async def test_obtener_mi_posicion_exitoso(self, client, estudiante_headers, usuario_puntos):
        """Debe retornar posición del usuario."""
        response = await client.get(
            "/api/gamification/puntos/ranking/me",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "posicion" in data or "posicion" is None  # Puede no tener posición si no hay puntos
        assert "puntos" in data
        assert "nivel" in data
        assert "total_usuarios" in data
    
    async def test_posicion_con_contexto(self, client, estudiante_headers, usuario_puntos):
        """Debe incluir contexto de posiciones cercanas."""
        response = await client.get(
            "/api/gamification/puntos/ranking/me",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        if data.get("posicion"):
            assert "puntos_hasta_anterior" in data
            assert "puntos_hasta_siguiente" in data


class TestOtorgarPuntos:
    """Tests para POST /api/gamification/puntos/otorgar"""
    
    async def test_otorgar_puntos_como_admin(self, client, auth_headers, estudiante_user, usuario_puntos):
        """Admin debe poder otorgar puntos."""
        payload = {
            "usuario_id": str(estudiante_user.usuario_id),
            "puntos": 500,
            "motivo": "Excelente participación en clase"
        }
        
        response = await client.post(
            "/api/gamification/puntos/otorgar",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["puntos_otorgados"] == 500
        assert "puntos_anteriores" in data
        assert "puntos_acumulados" in data
    
    async def test_otorgar_puntos_negativos(self, client, auth_headers, estudiante_user, usuario_puntos):
        """Admin debe poder quitar puntos."""
        payload = {
            "usuario_id": str(estudiante_user.usuario_id),
            "puntos": -200,
            "motivo": "Corrección de puntos"
        }
        
        response = await client.post(
            "/api/gamification/puntos/otorgar",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["puntos_otorgados"] == -200
    
    async def test_otorgar_puntos_como_estudiante(self, client, estudiante_headers, estudiante_user):
        """Estudiante no debe poder otorgar puntos."""
        payload = {
            "usuario_id": str(estudiante_user.usuario_id),
            "puntos": 500,
            "motivo": "Intento no autorizado"
        }
        
        response = await client.post(
            "/api/gamification/puntos/otorgar",
            json=payload,
            headers=estudiante_headers
        )
        
        assert response.status_code == 403  # Forbidden
    
    async def test_otorgar_puntos_validacion_cero(self, client, auth_headers, estudiante_user):
        """No debe permitir otorgar 0 puntos."""
        payload = {
            "usuario_id": str(estudiante_user.usuario_id),
            "puntos": 0,
            "motivo": "Test cero puntos"
        }
        
        response = await client.post(
            "/api/gamification/puntos/otorgar",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    async def test_otorgar_puntos_motivo_corto(self, client, auth_headers, estudiante_user):
        """Motivo debe tener mínimo 5 caracteres."""
        payload = {
            "usuario_id": str(estudiante_user.usuario_id),
            "puntos": 100,
            "motivo": "abc"
        }
        
        response = await client.post(
            "/api/gamification/puntos/otorgar",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    async def test_otorgar_puntos_usuario_inexistente(self, client, auth_headers):
        """Debe fallar con usuario inexistente."""
        payload = {
            "usuario_id": str(uuid4()),
            "puntos": 100,
            "motivo": "Usuario no existe"
        }
        
        response = await client.post(
            "/api/gamification/puntos/otorgar",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestHistorialPuntos:
    """Tests para GET /api/gamification/puntos/historial"""
    
    async def test_obtener_historial_exitoso(self, client, estudiante_headers, historial_puntos):
        """Debe retornar historial paginado."""
        response = await client.get(
            "/api/gamification/puntos/historial",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "historial" in data
        assert "total" in data
        assert isinstance(data["historial"], list)
    
    async def test_historial_paginacion(self, client, estudiante_headers, historial_puntos):
        """Debe respetar paginación."""
        response = await client.get(
            "/api/gamification/puntos/historial?limit=2&offset=0",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 2
        assert len(data["historial"]) <= 2
    
    async def test_historial_orden_cronologico(self, client, estudiante_headers, historial_puntos):
        """Debe ordenar por fecha descendente."""
        response = await client.get(
            "/api/gamification/puntos/historial",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        historial = data["historial"]
        
        if len(historial) > 1:
            # Verificar que está ordenado por fecha desc
            fechas = [item["fecha"] for item in historial]
            assert fechas == sorted(fechas, reverse=True)


class TestNivelInfo:
    """Tests para GET /api/gamification/puntos/nivel/info"""
    
    async def test_obtener_info_niveles(self, client, estudiante_headers):
        """Debe retornar información de niveles."""
        response = await client.get(
            "/api/gamification/puntos/nivel/info",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "niveles" in data
        assert isinstance(data["niveles"], list)
    
    async def test_niveles_incluyen_umbrales(self, client, estudiante_headers):
        """Cada nivel debe tener su umbral de puntos."""
        response = await client.get(
            "/api/gamification/puntos/nivel/info",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        niveles = data["niveles"]
        
        for nivel in niveles:
            assert "nombre" in nivel or "nivel" in nivel
            assert "puntos_requeridos" in nivel or "puntos_minimos" in nivel


# =============================================================================
# TESTS DE INTEGRACIÓN
# =============================================================================

class TestPuntosIntegracion:
    """Tests de integración del flujo completo de puntos."""
    
    async def test_flujo_completo_otorgar_y_verificar(
        self,
        client,
        auth_headers,
        estudiante_headers,
        admin_user,
        estudiante_user,
        db_session
    ):
        """Test flujo: Otorgar puntos → Verificar puntos → Ver historial → Ver ranking."""
        # 1. Crear registro de puntos inicial
        from src.models.gamification import UsuarioPuntos
        from datetime import datetime, timezone
        puntos = UsuarioPuntos(
            usuario_id=estudiante_user.usuario_id,
            puntos_acumulados=500,
            cambio=500,
            motivo="Puntos iniciales",
            fecha=datetime.now(timezone.utc)
        )
        db_session.add(puntos)
        await db_session.commit()
        
        # 2. Admin otorga puntos
        response = await client.post(
            "/api/gamification/puntos/otorgar",
            json={
                "usuario_id": str(estudiante_user.usuario_id),
                "puntos": 300,
                "motivo": "Test integración"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["puntos_acumulados"] == 800
        
        # 3. Usuario verifica sus puntos
        response = await client.get(
            "/api/gamification/puntos/me",
            headers=estudiante_headers
        )
        assert response.status_code == 200
        assert response.json()["puntos_acumulados"] == 800
        
        # 4. Usuario revisa historial
        response = await client.get(
            "/api/gamification/puntos/historial",
            headers=estudiante_headers
        )
        assert response.status_code == 200
        assert len(response.json()["historial"]) > 0
        
        # 5. Usuario verifica su posición en ranking
        response = await client.get(
            "/api/gamification/puntos/ranking/me",
            headers=estudiante_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["puntos"] == 800


# =============================================================================
# TESTS DE PERFORMANCE
# =============================================================================

@pytest.mark.slow
class TestPuntosPerformance:
    """Tests de rendimiento para endpoints de puntos."""
    
    async def test_ranking_con_muchos_usuarios(self, client, estudiante_headers, db_session):
        """Ranking debe ser eficiente con muchos usuarios."""
        from src.models.users.usuario import Usuario
        from src.models.gamification import UsuarioPuntos
        from src.enums.users.usuario_enums import RolUsuario, EstadoCuentaUsuario
        
        # Crear 100 usuarios con puntos
        for i in range(100):
            user = Usuario(
                correo_institucional=f"perf{i}@test.com",
                nombres=f"User{i}",
                apellidos="Perf",
                rol=RolUsuario.estudiante,
                estado_cuenta=EstadoCuentaUsuario.activo,
                password_hash="hash",
                email_verified=True
            )
            db_session.add(user)
            await db_session.flush()
            
            from datetime import datetime, timezone
            puntos = UsuarioPuntos(
                usuario_id=user.usuario_id,
                puntos_acumulados=1000 + (i * 10),
                cambio=1000 + (i * 10),
                motivo=f"Puntos iniciales usuario {i}",
                fecha=datetime.now(timezone.utc)
            )
            db_session.add(puntos)
        
        await db_session.commit()
        
        # Medir tiempo de respuesta
        import time
        start = time.time()
        
        response = await client.get(
            "/api/gamification/puntos/ranking?limit=50",
            headers=estudiante_headers
        )
        
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0  # Debe responder en menos de 2 segundos
        assert len(response.json()["data"]) == 50
