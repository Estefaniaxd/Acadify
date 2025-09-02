# backend/tests/test_institutions.py
"""
Tests para el módulo de instituciones
Prueba operaciones CRUD y funcionalidades específicas de instituciones
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models.user import User
from app.models.institution import Institution

class TestInstitutions:
    """Suite de tests para instituciones"""
    
    def test_get_institutions_list(self, client: TestClient, admin_auth_headers: Dict[str, str], created_institution: Institution):
        """Test de obtener lista de instituciones"""
        response = client.get("/api/v1/institutions/", headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "institutions" in data
        assert len(data["institutions"]) >= 1
    
    def test_get_institution_by_id(self, client: TestClient, admin_auth_headers: Dict[str, str], created_institution: Institution):
        """Test de obtener institución por ID"""
        response = client.get(f"/api/v1/institutions/{created_institution.id}", headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(created_institution.id)
        assert data["name"] == created_institution.name
    
    def test_create_institution(self, client: TestClient, admin_auth_headers: Dict[str, str], created_admin: User):
        """Test de crear institución"""
        institution_data = {
            "name": "Nueva Universidad de Prueba",
            "acronym": "NUP",
            "institution_type": "university",
            "educational_level": "higher",
            "sector": "private",
            "country": "Colombia",
            "institutional_email": "info@nup.edu.co",
            "phone": "+571987654321",
            "uses_programs": True,
            "administrator_id": str(created_admin.id)
        }
        
        response = client.post("/api/v1/institutions/", json=institution_data, headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == institution_data["name"]
        assert data["acronym"] == institution_data["acronym"]
    
    def test_update_institution(self, client: TestClient, admin_auth_headers: Dict[str, str], created_institution: Institution):
        """Test de actualizar institución"""
        update_data = {
            "motto": "Nuevo lema institucional",
            "city": "Medellín"
        }
        
        response = client.put(
            f"/api/v1/institutions/{created_institution.id}", 
            json=update_data, 
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["motto"] == update_data["motto"]
        assert data["city"] == update_data["city"]
    
    def test_delete_institution(self, client: TestClient, admin_auth_headers: Dict[str, str], created_institution: Institution):
        """Test de eliminar institución"""
        response = client.delete(f"/api/v1/institutions/{created_institution.id}", headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "eliminada correctamente" in data["message"]