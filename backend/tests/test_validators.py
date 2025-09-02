# backend/tests/test_validators.py
"""
Tests para validadores y utilidades
Prueba funciones de validación y helpers
"""
import pytest
from app.utils.validators import *
from app.utils.helpers import *

class TestValidators:
    """Suite de tests para validadores"""
    
    @pytest.mark.parametrize("email,expected", [
        ("test@university.edu.co", True),
        ("student@college.edu", True),
        ("prof@instituto.ac.cr", True),
        ("admin@escuela.edu.mx", True),
        ("test@gmail.com", False),
        ("user@company.com", False),
        ("invalid-email", False),
        ("", False)
    ])
    def test_institutional_email_validation(self, email, expected):
        """Test parametrizado para validación de emails institucionales"""
        assert validate_institutional_email(email) == expected
    
    @pytest.mark.parametrize("doc_type,doc_number,expected", [
        ("cc", "12345678", True),
        ("cc", "1234567890", True),
        ("ti", "12345678", True),
        ("ce", "123456789012", True),
        ("cc", "123", False),  # Muy corto
        ("ti", "123456789012345", False),  # Muy largo
        ("cc", "", False),  # Vacío
    ])
    def test_document_validation(self, doc_type, doc_number, expected):
        """Test parametrizado para validación de documentos"""
        assert validate_document_number(doc_type, doc_number) == expected
    
    @pytest.mark.parametrize("phone,expected", [
        ("+573001234567", True),
        ("3001234567", True),
        ("+1234567890", True),
        ("123", False),
        ("invalid-phone", False),
        ("", False)
    ])
    def test_phone_validation(self, phone, expected):
        """Test parametrizado para validación de teléfonos"""
        assert validate_phone_number(phone) == expected

class TestHelpers:
    """Suite de tests para funciones auxiliares"""
    
    def test_generate_random_string(self):
        """Test de generación de strings aleatorios"""
        string1 = generate_random_string(32)
        string2 = generate_random_string(32)
        
        assert len(string1) == 32
        assert len(string2) == 32
        assert string1 != string2  # Deben ser diferentes
    
    def test_generate_uuid(self):
        """Test de generación de UUIDs"""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        
        assert len(uuid1) == 36  # Formato estándar UUID
        assert uuid1 != uuid2
        assert "-" in uuid1  # Debe contener guiones
    
    def test_format_file_size(self):
        """Test de formateo de tamaños de archivo"""
        assert format_file_size(0) == "0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1048576) == "1.0 MB"
        assert format_file_size(1073741824) == "1.0 GB"
    
    def test_clean_filename(self):
        """Test de limpieza de nombres de archivo"""
        assert clean_filename("test file.pdf") == "test file.pdf"
        assert clean_filename("test/file\\with:bad*chars?.pdf") == "testfilewithabadchars.pdf"
        
        # Test de archivo muy largo
        long_name = "a" * 200 + ".pdf"
        cleaned = clean_filename(long_name)
        assert len(cleaned) <= 100
        assert cleaned.endswith(".pdf")
    
    def test_sanitize_input(self):
        """Test de sanitización de entrada"""
        assert sanitize_input("  Normal text  ") == "Normal text"
        assert sanitize_input("Text\x00with\x1fcontrol\x7fchars") == "Textwithcontrolchars"
        assert sanitize_input("Text   with    multiple   spaces") == "Text with multiple spaces"
        
        # Test de longitud máxima
        long_text = "a" * 200
        assert len(sanitize_input(long_text, 50)) == 50
    
    def test_paginate_response(self):
        """Test de respuesta paginada"""
        items = [f"item{i}" for i in range(25)]
        
        result = paginate_response(items[:10], 25, 1, 10)
        
        assert result["total"] == 25
        assert result["page"] == 1
        assert result["size"] == 10
        assert result["total_pages"] == 3
        assert result["has_next"] is True
        assert result["has_prev"] is False
        assert len(result["items"]) == 10