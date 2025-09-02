# backend/tests/test_auth.py
"""
Tests para el módulo de autenticación
Prueba login, registro, cambio de contraseñas y manejo de tokens
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_token
from app.crud.user import user_crud
from app.models.user import User

class TestAuthentication:
    """Suite de tests para autenticación"""
    
    def test_login_success(self, client: TestClient, created_user: User):
        """Test de login exitoso"""
        login_data = {
            "username": created_user.institutional_email,
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/auth/login/oauth", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["token"]["token_type"] == "bearer"
        assert data["user"]["institutional_email"] == created_user.institutional_email
        assert "access_token" in data["token"]
        assert "refresh_token" in data["token"]
    
    def test_login_invalid_email(self, client: TestClient):
        """Test de login con email inválido"""
        login_data = {
            "username": "invalid@email.com",
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/auth/login/oauth", data=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Email o contraseña incorrectos" in data["detail"]
    
    def test_login_invalid_password(self, client: TestClient, created_user: User):
        """Test de login con contraseña inválida"""
        login_data = {
            "username": created_user.institutional_email,
            "password": "WrongPassword123!"
        }
        
        response = client.post("/api/v1/auth/login/oauth", data=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Email o contraseña incorrectos" in data["detail"]
    
    def test_login_inactive_user(self, client: TestClient, created_user: User, db: Session):
        """Test de login con usuario inactivo"""
        # Desactivar usuario
        from app.models.user import AccountStatus
        user_crud.change_account_status(db, user=created_user, new_status=AccountStatus.INACTIVE)
        
        login_data = {
            "username": created_user.institutional_email,
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/auth/login/oauth", data=login_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "inactiva" in data["detail"]
    
    def test_register_success(self, client: TestClient):
        """Test de registro exitoso"""
        register_data = {
            "institutional_email": "newuser@university.edu.co",
            "first_names": "Nuevo",
            "last_names": "Usuario",
            "document_type": "cc",
            "document_number": "99887766",
            "role": "student",
            "password": "NewPassword123!"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["institutional_email"] == register_data["institutional_email"]
        assert data["role"] == register_data["role"]
        assert "password" not in data
    
    def test_register_duplicate_email(self, client: TestClient, created_user: User):
        """Test de registro con email duplicado"""
        register_data = {
            "institutional_email": created_user.institutional_email,
            "first_names": "Otro",
            "last_names": "Usuario",
            "document_type": "cc",
            "document_number": "55443322",
            "role": "student",
            "password": "AnotherPassword123!"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "ya está registrado" in data["detail"]
    
    def test_refresh_token_success(self, client: TestClient, created_user: User):
        """Test de refresh token exitoso"""
        # Primero hacer login para obtener tokens
        login_data = {
            "username": created_user.institutional_email,
            "password": "TestPassword123!"
        }
        
        login_response = client.post("/api/v1/auth/login/oauth", data=login_data)
        login_data_response = login_response.json()
        refresh_token = login_data_response["token"]["refresh_token"]
        
        # Usar refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client: TestClient):
        """Test de refresh token inválido"""
        refresh_data = {"refresh_token": "invalid_token"}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "inválido" in data["detail"]
    
    def test_change_password_success(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test de cambio de contraseña exitoso"""
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "NewTestPassword123!"
        }
        
        response = client.post(
            "/api/v1/auth/change-password", 
            json=password_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "actualizada correctamente" in data["message"]
    
    def test_change_password_wrong_current(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test de cambio de contraseña con contraseña actual incorrecta"""
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewTestPassword123!"
        }
        
        response = client.post(
            "/api/v1/auth/change-password", 
            json=password_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "incorrecta" in data["detail"]
    
    def test_get_current_user(self, client: TestClient, auth_headers: Dict[str, str], created_user: User):
        """Test de obtener información del usuario actual"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["institutional_email"] == created_user.institutional_email
        assert data["id"] == str(created_user.id)
    
    def test_logout(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test de logout"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "exitoso" in data["message"]