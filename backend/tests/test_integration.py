# backend/tests/test_integration.py
"""
Tests de integración entre módulos
Prueba flujos completos y interacciones entre diferentes componentes
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict, Any

class TestIntegration:
    """Suite de tests de integración"""
    
    def test_complete_user_workflow(self, client: TestClient, admin_auth_headers: Dict[str, str]):
        """Test de flujo completo: crear usuario -> login -> actualizar -> eliminar"""
        
        # 1. Crear usuario
        user_data = {
            "institutional_email": "workflow@university.edu.co",
            "first_names": "Test",
            "last_names": "Workflow",
            "document_type": "cc",
            "document_number": "workflow123",
            "role": "student",
            "password": "WorkflowPassword123!"
        }
        
        create_response = client.post("/api/v1/users/", json=user_data, headers=admin_auth_headers)
        assert create_response.status_code == 200
        created_user = create_response.json()
        user_id = created_user["id"]
        
        # 2. Login con el nuevo usuario
        login_data = {
            "username": user_data["institutional_email"],
            "password": user_data["password"]
        }
        
        login_response = client.post("/api/v1/auth/login/oauth", data=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        
        user_headers = {"Authorization": f"Bearer {token_data['token']['access_token']}"}
        
        # 3. Obtener perfil propio
        profile_response = client.get(f"/api/v1/users/{user_id}", headers=user_headers)
        assert profile_response.status_code == 200
        
        # 4. Actualizar perfil propio
        update_data = {"biography": "Biografía de prueba de workflow"}
        update_response = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=user_headers)
        assert update_response.status_code == 200
        
        # 5. Cambiar contraseña
        password_change = {
            "current_password": user_data["password"],
            "new_password": "NewWorkflowPassword123!"
        }
        password_response = client.post("/api/v1/auth/change-password", json=password_change, headers=user_headers)
        assert password_response.status_code == 200
        
        # 6. Eliminar usuario (como admin)
        delete_response = client.delete(f"/api/v1/users/{user_id}", headers=admin_auth_headers)
        assert delete_response.status_code == 200
    
    def test_institution_and_programs_workflow(self, client: TestClient, admin_auth_headers: Dict[str, str], created_admin: User):
        """Test de flujo institución -> programas -> cursos"""
        
        # 1. Crear institución
        institution_data = {
            "name": "Universidad de Integración",
            "acronym": "UDI",
            "institution_type": "university",
            "educational_level": "higher",
            "sector": "public",
            "country": "Colombia",
            "institutional_email": "info@udi.edu.co",
            "phone": "+571111111111",
            "uses_programs": True,
            "administrator_id": str(created_admin.id)
        }
        
        inst_response = client.post("/api/v1/institutions/", json=institution_data, headers=admin_auth_headers)
        assert inst_response.status_code == 200
        institution = inst_response.json()
        
        # 2. Crear programa
        program_data = {
            "name": "Ingeniería de Sistemas",
            "description": "Programa de ingeniería de sistemas",
            "level": "professional",
            "program_type": "in_person",
            "institution_id": institution["id"]
        }
        
        prog_response = client.post("/api/v1/programs/", json=program_data, headers=admin_auth_headers)
        assert prog_response.status_code == 200
        program = prog_response.json()
        
        # 3. Crear curso
        course_data = {
            "name": "Programación I",
            "description": "Curso introductorio de programación",
            "modality": "semester",
            "institution_id": institution["id"],
            "program_id": program["id"]
        }
        
        course_response = client.post("/api/v1/courses/", json=course_data, headers=admin_auth_headers)
        assert course_response.status_code == 200
        course = course_response.json()
        
        # Verificar relaciones
        assert course["institution_id"] == institution["id"]
        assert course["program_id"] == program["id"]
    
    def test_unauthorized_access_patterns(self, client: TestClient, auth_headers: Dict[str, str]):
        """Test de patrones de acceso no autorizado"""
        
        # Intentar acceder a endpoints de admin sin permisos
        admin_endpoints = [
            "/api/v1/users/",
            "/api/v1/institutions/",
            "/api/v1/users/by-role/student"
        ]
        
        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code == 403
    
    def test_invalid_uuid_handling(self, client: TestClient, admin_auth_headers: Dict[str, str]):
        """Test de manejo de UUIDs inválidos"""
        invalid_uuids = ["invalid-uuid", "123", "", "not-a-uuid-at-all"]
        
        for invalid_uuid in invalid_uuids:
            response = client.get(f"/api/v1/users/{invalid_uuid}", headers=admin_auth_headers)
            assert response.status_code == 400
            data = response.json()
            assert "inválido" in data["detail"].lower()