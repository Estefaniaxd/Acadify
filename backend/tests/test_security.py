# backend/tests/test_security.py
"""
Tests específicos para funcionalidades de seguridad
Prueba validaciones, tokens, permisos y protecciones
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.security import create_access_token, verify_token, get_password_hash, verify_password
from app.utils.validators import (
    validate_institutional_email,
    validate_document_number,
    validate_phone_number,
    validate_password_strength
)

class TestSecurity:
    """Suite de tests para seguridad"""
    
    def test_password_hashing(self):
        """Test de hashing y verificación de contraseñas"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_token_creation_and_verification(self):
        """Test de creación y verificación de tokens JWT"""
        user_id = "test-user-id"
        token = create_access_token(data={"sub": user_id})
        
        assert token is not None
        
        payload = verify_token(token, "access")
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
    
    def test_expired_token(self):
        """Test de token expirado"""
        # Crear token que expira inmediatamente
        user_id = "test-user-id"
        expires_delta = timedelta(seconds=-1)  # Ya expirado
        token = create_access_token(data={"sub": user_id}, expires_delta=expires_delta)
        
        payload = verify_token(token, "access")
        assert payload is None  # Token expirado debe retornar None
    
    def test_invalid_token(self):
        """Test de token inválido"""
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token, "access")
        assert payload is None
    
    def test_institutional_email_validation(self):
        """Test de validación de emails institucionales"""
        # Emails válidos
        assert validate_institutional_email("test@university.edu.co") is True
        assert validate_institutional_email("student@college.edu") is True
        assert validate_institutional_email("prof@instituto.ac.cr") is True
        
        # Emails inválidos
        assert validate_institutional_email("test@gmail.com") is False
        assert validate_institutional_email("invalid-email") is False
        assert validate_institutional_email("test@company.com") is False
    
    def test_document_number_validation(self):
        """Test de validación de números de documento"""
        # Cédulas válidas
        assert validate_document_number("cc", "12345678") is True
        assert validate_document_number("cc", "1234567890") is True
        
        # Tarjetas de identidad válidas
        assert validate_document_number("ti", "12345678") is True
        
        # Documentos inválidos
        assert validate_document_number("cc", "123") is False  # Muy corto
        assert validate_document_number("ti", "123456789012345") is False  # Muy largo
    
    def test_phone_validation(self):
        """Test de validación de números telefónicos"""
        # Teléfonos válidos
        assert validate_phone_number("+573001234567") is True
        assert validate_phone_number("3001234567") is True
        assert validate_phone_number("+1234567890") is True
        
        # Teléfonos inválidos
        assert validate_phone_number("123") is False  # Muy corto
        assert validate_phone_number("invalid-phone") is False
        assert validate_phone_number("") is False
    
    def test_password_strength_validation(self):
        """Test de validación de fortaleza de contraseñas"""
        # Contraseñas válidas
        valid, msg = validate_password_strength("Password123!")
        assert valid is True
        assert msg is None
        
        # Contraseñas inválidas
        invalid_cases = [
            ("weak", "debe tener al menos 8 caracteres"),
            ("password123!", "debe contener al menos una mayúscula"),
            ("PASSWORD123!", "debe contener al menos una minúscula"),
            ("Password!", "debe contener al menos un número"),
            ("Password123", "debe contener al menos un carácter especial")
        ]
        
        for password, expected_error in invalid_cases:
            valid, msg = validate_password_strength(password)
            assert valid is False
            assert expected_error in msg.lower()