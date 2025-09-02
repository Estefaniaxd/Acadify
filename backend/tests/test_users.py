# backend/tests/test_users.py
"""
Tests para el módulo de usuarios
Prueba operaciones CRUD y funcionalidades específicas de usuarios
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models.user import User

class TestUsers:
    """Suite de tests para usuarios"""
    
    def test_get_users_list_as_admin(self, client: TestClient, admin_auth_headers: Dict[str, str], created_user: User):
        """Test de obtener lista de usuarios como administrador"""
        response = client.get("/api/v1/users/", headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["users"]) >= 1
    
    def test_get_users_list_as_non_admin(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test de obtener lista de usuarios como no-administrador (debe fallar)"""
        response = client.get("/api/v1/users/", headers=auth_headers)
        
        assert response.status_code == 403
        data = response.json()
        assert "permisos" in data["detail"]
    
    def test_get_user_by_id_own_profile(self, client: TestClient, auth_headers: Dict[str, str], created_user: User):
        """Test de obtener propio perfil"""
        response = client.get(f"/api/v1/users/{created_user.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(created_user.id)
        assert data["institutional_email"] == created_user.institutional_email
    
    def test_get_user_by_id_as_admin(self, client: TestClient, admin_auth_headers: Dict[str, str], created_user: User):
        """Test de obtener usuario como administrador"""
        response = client.get(f"/api/v1/users/{created_user.id}", headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(created_user.id)
    
    def test_get_user_unauthorized(self, client: TestClient, auth_headers: Dict[str, str], created_admin: User):
        """Test de obtener usuario sin permisos (debe fallar)"""
        response = client.get(f"/api/v1/users/{created_admin.id}", headers=auth_headers)
        
        assert response.status_code == 403
        data = response.json()
        assert "permisos" in data["detail"]
    
    def test_get_user_not_found(self, client: TestClient, admin_auth_headers: Dict[str, str]):
        """Test de obtener usuario inexistente"""
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = client.get(f"/api/v1/users/{fake_id}", headers=admin_auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "no encontrado" in data["detail"]
    
    def test_create_user_as_admin(self, client: TestClient, admin_auth_headers: Dict[str, str]):
        """Test de crear usuario como administrador"""
        user_data = {
            "institutional_email": "nuevo@university.edu.co",
            "first_names": "Usuario",
            "last_names": "Nuevo",
            "document_type": "cc",
            "document_number": "13579246",
            "role": "teacher",
            "password": "NewUserPassword123!",
            "phone": "+573001112233"
        }
        
        response = client.post("/api/v1/users/", json=user_data, headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["institutional_email"] == user_data["institutional_email"]
        assert data["role"] == user_data["role"]
        assert "password" not in data
    
    def test_create_user_as_non_admin(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test de crear usuario como no-administrador (debe fallar)"""
        user_data = {
            "institutional_email": "nuevo2@university.edu.co",
            "first_names": "Usuario",
            "last_names": "Nuevo",
            "document_type": "cc",
            "document_number": "24681357",
            "role": "student",
            "password": "NewUserPassword123!"
        }
        
        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_create_user_duplicate_email(self, client: TestClient, admin_auth_headers: Dict[str, str], created_user: User):
        """Test de crear usuario con email duplicado"""
        user_data = {
            "institutional_email": created_user.institutional_email,
            "first_names": "Otro",
            "last_names": "Usuario",
            "document_type": "cc",
            "document_number": "99999999",
            "role": "student",
            "password": "Password123!"
        }
        
        response = client.post("/api/v1/users/", json=user_data, headers=admin_auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "ya está registrado" in data["detail"]
    
    def test_update_own_profile(self, client: TestClient, auth_headers: Dict[str, str], created_user: User):
        """Test de actualizar propio perfil"""
        update_data = {
            "first_names": "Juan Carlos Actualizado",
            "biography": "Biografía actualizada"
        }
        
        response = client.put(
            f"/api/v1/users/{created_user.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_names"] == update_data["first_names"]
        assert data["biography"] == update_data["biography"]
    
    def test_update_user_as_admin(self, client: TestClient, admin_auth_headers: Dict[str, str], created_user: User):
        """Test de actualizar usuario como administrador"""
        update_data = {
            "first_names": "Nombre Actualizado Por Admin",
            "phone": "+573009999999"
        }
        
        response = client.put(
            f"/api/v1/users/{created_user.id}", 
            json=update_data, 
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_names"] == update_data["first_names"]
        assert data["phone"] == update_data["phone"]
    
    def test_update_user_unauthorized(self, client: TestClient, auth_headers: Dict[str, str], created_admin: User):
        """Test de actualizar usuario sin permisos"""
        update_data = {"first_names": "Intento de hack"}
        
        response = client.put(
            f"/api/v1/users/{created_admin.id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    def test_delete_user_as_admin(self, client: TestClient, admin_auth_headers: Dict[str, str], created_user: User):
        """Test de eliminar usuario como administrador"""
        response = client.delete(f"/api/v1/users/{created_user.id}", headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "eliminado correctamente" in data["message"]
    
    def test_delete_user_self_prevention(self, client: TestClient, admin_auth_headers: Dict[str, str], created_admin: User):
        """Test de prevención de auto-eliminación"""
        response = client.delete(f"/api/v1/users/{created_admin.id}", headers=admin_auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "tu propia cuenta" in data["detail"]
    
    def test_change_user_status(self, client: TestClient, admin_auth_headers: Dict[str, str], created_user: User):
        """Test de cambio de estado de usuario"""
        response = client.patch(
            f"/api/v1/users/{created_user.id}/status?new_status=suspended",
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["account_status"] == "suspended"
    
    def test_search_users(self, client: TestClient, auth_headers: Dict[str, str], created_user: User):
        """Test de búsqueda de usuarios"""
        response = client.get(
            f"/api/v1/users/search/?q={created_user.first_names}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) >= 1
        # Como no es admin, no debe ver email
        if data["users"]:
            assert data["users"][0]["institutional_email"] is None
    
    def test_get_users_by_role(self, client: TestClient, admin_auth_headers: Dict[str, str]):
        """Test de obtener usuarios por rol"""
        response = client.get("/api/v1/users/by-role/student", headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        # Todos los usuarios retornados deben tener rol student
        for user in data["users"]:
            assert user["role"] == "student"