"""
Tests para API de Rachas (Streaks).

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
"""

import pytest
from datetime import date, timedelta


class TestObtenerRacha:
    """Tests para GET /api/gamification/rachas/me"""
    
    async def test_obtener_racha_exitoso(self, client, estudiante_headers, racha_usuario):
        """Debe retornar racha actual."""
        response = await client.get(
            "/api/gamification/rachas/me",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "racha" in data
        assert "mensaje_motivacional" in data
        racha = data["racha"]
        assert "dias_actuales" in racha
        assert "dias_maximos" in racha
        assert "estado" in racha


class TestVerificarRacha:
    """Tests para POST /api/gamification/rachas/verificar"""
    
    async def test_verificar_racha_exitoso(self, client, estudiante_headers, racha_usuario, db_session):
        """Debe verificar actividad diaria."""
        # Ajustar última actividad para permitir verificación
        racha_usuario.ultima_actividad = date.today() - timedelta(days=1)
        db_session.commit()
        
        payload = {
            "actividad_completada": "Completé 3 tareas y 1 examen",
            "puntos_ganados": 350
        }
        
        response = await client.post(
            "/api/gamification/rachas/verificar",
            json=payload,
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "racha_actual" in data
        assert "mensaje_motivacional" in data
    
    async def test_verificar_racha_ya_verificada(self, client, estudiante_headers, racha_usuario):
        """Debe fallar si ya se verificó hoy."""
        payload = {
            "actividad_completada": "Intento duplicado",
            "puntos_ganados": 100
        }
        
        response = await client.post(
            "/api/gamification/rachas/verificar",
            json=payload,
            headers=estudiante_headers
        )
        
        assert response.status_code == 400
    
    async def test_verificar_racha_validacion_actividad(self, client, estudiante_headers):
        """Debe validar actividad mínima."""
        payload = {
            "actividad_completada": "abc",  # Muy corta
            "puntos_ganados": 100
        }
        
        response = await client.post(
            "/api/gamification/rachas/verificar",
            json=payload,
            headers=estudiante_headers
        )
        
        assert response.status_code == 422


class TestCongelarRacha:
    """Tests para POST /api/gamification/rachas/congelar"""
    
    async def test_congelar_racha_exitoso(self, client, estudiante_headers, racha_usuario):
        """Debe congelar racha."""
        payload = {
            "dias_proteccion": 3,
            "usar_item": False
        }
        
        response = await client.post(
            "/api/gamification/rachas/congelar",
            json=payload,
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["dias_protegidos"] == 3
    
    async def test_congelar_racha_validacion_dias(self, client, estudiante_headers):
        """Debe validar rango de días."""
        payload = {
            "dias_proteccion": 10,  # Máximo es 7
            "usar_item": False
        }
        
        response = await client.post(
            "/api/gamification/rachas/congelar",
            json=payload,
            headers=estudiante_headers
        )
        
        assert response.status_code == 422


class TestRecuperarRacha:
    """Tests para POST /api/gamification/rachas/recuperar"""
    
    async def test_recuperar_racha_sin_condiciones(self, client, estudiante_headers, racha_usuario):
        """Debe fallar si no hay racha rota."""
        response = await client.post(
            "/api/gamification/rachas/recuperar",
            headers=estudiante_headers
        )
        
        assert response.status_code == 400


class TestMilestones:
    """Tests para GET /api/gamification/rachas/milestones"""
    
    async def test_obtener_milestones(self, client, estudiante_headers, milestones_racha):
        """Debe retornar milestones."""
        response = await client.get(
            "/api/gamification/rachas/milestones",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "milestones" in data
        assert "total_alcanzados" in data
        assert len(data["milestones"]) > 0


class TestRankingRachas:
    """Tests para GET /api/gamification/rachas/ranking"""
    
    async def test_obtener_ranking_rachas(self, client, estudiante_headers):
        """Debe retornar ranking de rachas."""
        response = await client.get(
            "/api/gamification/rachas/ranking",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "ranking" in data
        assert "total" in data


class TestEstadisticasRacha:
    """Tests para GET /api/gamification/rachas/estadisticas"""
    
    async def test_obtener_estadisticas(self, client, estudiante_headers, racha_usuario):
        """Debe retornar estadísticas de racha."""
        response = await client.get(
            "/api/gamification/rachas/estadisticas",
            headers=estudiante_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "racha_actual" in data
        assert "racha_maxima" in data
        assert "total_dias_activos" in data


# Integración
class TestRachasIntegracion:
    """Tests de flujo completo de rachas."""
    
    async def test_flujo_verificar_milestone_estadisticas(
        self,
        client,
        estudiante_headers,
        racha_usuario,
        milestones_racha,
        db_session
    ):
        """Test: Verificar día → Alcanzar milestone → Ver estadísticas."""
        # 1. Ajustar racha cercana a milestone
        racha_usuario.dias_actuales = 2
        racha_usuario.ultima_actividad = date.today() - timedelta(days=1)
        db_session.commit()
        
        # 2. Verificar actividad
        response = await client.post(
            "/api/gamification/rachas/verificar",
            json={
                "actividad_completada": "Test milestone",
                "puntos_ganados": 100
            },
            headers=estudiante_headers
        )
        assert response.status_code == 200
        assert response.json()["racha_actual"] == 3
        
        # 3. Ver milestones
        response = await client.get(
            "/api/gamification/rachas/milestones",
            headers=estudiante_headers
        )
        assert response.status_code == 200
        
        # 4. Ver estadísticas
        response = await client.get(
            "/api/gamification/rachas/estadisticas",
            headers=estudiante_headers
        )
        assert response.status_code == 200
