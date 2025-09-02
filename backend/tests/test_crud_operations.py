# backend/tests/test_crud_operations.py
"""
Tests para operaciones CRUD de diferentes entidades
Prueba la lógica de persistencia y consultas
"""
import pytest
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.crud.user import user_crud
from app.crud.institution import institution_crud
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.institution import InstitutionCreate, InstitutionUpdate
from app.models.user import User, UserRole

class TestUserCRUD:
    """Tests para CRUD de usuarios"""
    
    def test_create_user(self, db: Session, test_user_data: Dict[str, Any]):
        """Test de creación de usuario"""
        from app.schemas.user import UserCreate
        
        user_create = UserCreate(**test_user_data)
        user = user_crud.create(db, obj_in=user_create)
        
        assert user.institutional_email == test_user_data["institutional_email"]
        assert user.first_names == test_user_data["first_names"]
        assert user.role == UserRole.STUDENT
        assert user.password_hash != test_user_data["password"]  # Debe estar hasheada
    
    def test_get_user_by_email(self, db: Session, created_user: User):
        """Test de obtener usuario por email"""
        user = user_crud.get_by_email(db, email=created_user.institutional_email)
        
        assert user is not None
        assert user.id == created_user.id
        assert user.institutional_email == created_user.institutional_email
    
    def test_get_user_by_document(self, db: Session, created_user: User):
        """Test de obtener usuario por documento"""
        user = user_crud.get_by_document(db, document_number=created_user.document_number)
        
        assert user is not None
        assert user.id == created_user.id
        assert user.document_number == created_user.document_number
    
    def test_authenticate_user(self, db: Session, test_user_data: Dict[str, Any]):
        """Test de autenticación de usuario"""
        from app.schemas.user import UserCreate
        
        # Crear usuario
        user_create = UserCreate(**test_user_data)
        created_user = user_crud.create(db, obj_in=user_create)
        
        # Autenticar
        authenticated_user = user_crud.authenticate(
            db, 
            email=test_user_data["institutional_email"],
            password=test_user_data["password"]
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
    
    def test_authenticate_user_wrong_password(self, db: Session, created_user: User):
        """Test de autenticación con contraseña incorrecta"""
        authenticated_user = user_crud.authenticate(
            db,
            email=created_user.institutional_email,
            password="WrongPassword123!"
        )
        
        assert authenticated_user is None
    
    def test_update_user(self, db: Session, created_user: User):
        """Test de actualización de usuario"""
        update_data = UserUpdate(
            first_names="Nombre Actualizado",
            biography="Nueva biografía"
        )
        
        updated_user = user_crud.update(db, db_obj=created_user, obj_in=update_data)
        
        assert updated_user.first_names == "Nombre Actualizado"
        assert updated_user.biography == "Nueva biografía"
        assert updated_user.id == created_user.id
    
    def test_search_users(self, db: Session, created_user: User):
        """Test de búsqueda de usuarios"""
        users = user_crud.search_users(db, query=created_user.first_names)
        
        assert len(users) >= 1
        assert any(user.id == created_user.id for user in users)
    
    def test_get_users_by_role(self, db: Session, created_user: User):
        """Test de obtener usuarios por rol"""
        users = user_crud.get_by_role(db, role=UserRole.STUDENT)
        
        assert len(users) >= 1
        assert all(user.role == UserRole.STUDENT for user in users)

class TestInstitutionCRUD:
    """Tests para CRUD de instituciones"""
    
    def test_create_institution(self, db: Session, test_institution_data: Dict[str, Any], created_admin: User):
        """Test de creación de institución"""
        from app.schemas.institution import InstitutionCreate
        
        institution_data = test_institution_data.copy()
        institution_data["administrator_id"] = str(created_admin.id)
        
        institution_create = InstitutionCreate(**institution_data)
        institution = institution_crud.create(db, obj_in=institution_create)
        
        assert institution.name == test_institution_data["name"]
        assert institution.acronym == test_institution_data["acronym"]
        assert str(institution.administrator_id) == str(created_admin.id)
    
    def test_get_institution_by_name(self, db: Session, created_institution: Institution):
        """Test de obtener institución por nombre"""
        institution = institution_crud.get_by_name(db, name=created_institution.name)
        
        assert institution is not None
        assert institution.id == created_institution.id
    
    def test_update_institution(self, db: Session, created_institution: Institution):
        """Test de actualización de institución"""
        from app.schemas.institution import InstitutionUpdate
        
        update_data = InstitutionUpdate(
            motto="Nuevo lema actualizado",
            city="Nueva Ciudad"
        )
        
        updated_institution = institution_crud.update(db, db_obj=created_institution, obj_in=update_data)
        
        assert updated_institution.motto == "Nuevo lema actualizado"
        assert updated_institution.city == "Nueva Ciudad"