# backend/tests/test_performance.py
"""
Tests de rendimiento y carga
Prueba el comportamiento del sistema bajo diferentes cargas
"""
import pytest
import time
from fastapi.testclient import TestClient
from typing import Dict

class TestPerformance:
    """Suite de tests de rendimiento"""
    
    def test_login_performance(self, client: TestClient, created_user):
        """Test de rendimiento del endpoint de login"""
        login_data = {
            "username": created_user.institutional_email,
            "password": "TestPassword123!"
        }
        
        start_time = time.time()
        response = client.post("/api/v1/auth/login/oauth", data=login_data)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Login debe tomar menos de 1 segundo
    
    def test_user_list_pagination_performance(self, client: TestClient, admin_auth_headers: Dict[str, str]):
        """Test de rendimiento de paginación de usuarios"""
        
        # Crear múltiples usuarios para el test
        for i in range(50):
            user_data = {
                "institutional_email": f"perftest{i}@university.edu.co",
                "first_names": f"User{i}",
                "last_names": "Test",
                "document_type": "cc",
                "document_number": f"perftest{i:06d}",
                "role": "student",
                "password": "TestPassword123!"
            }
            client.post("/api/v1/users/", json=user_data, headers=admin_auth_headers)
        
        # Probar paginación
        start_time = time.time()
        response = client.get("/api/v1/users/?page=1&size=20", headers=admin_auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Paginación debe ser rápida
        
        data = response.json()
        assert len(data["users"]) <= 20
    
    def test_search_performance(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test de rendimiento de búsqueda de usuarios"""
        
        start_time = time.time()
        response = client.get("/api/v1/users/search/?q=Test", headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.5  # Búsqueda debe ser rápida