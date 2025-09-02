# backend/app/utils/validators.py
import re

# -------------------------------
# Validación de emails
# -------------------------------
def validate_email(email: str, institutional: bool = False) -> bool:
    """
    Valida un email general o institucional.
    
    Args:
        email (str): Email a validar.
        institutional (bool): Si True, valida formato institucional (.edu, .ac.co).
    
    Returns:
        bool: True si es válido, False si no.
    """
    if not email:
        return False
    
    if institutional:
        # Ajusta el patrón según tu dominio real
        pattern = r'^[\w\.-]+@([\w-]+\.)+(edu|ac\.co)$'
    else:
        # Email general válido
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    
    return re.match(pattern, email) is not None


# -------------------------------
# Validación de documentos
# -------------------------------
DOCUMENT_RULES = {
    "CC": {"digits": True, "min": 6, "max": 10},
    "TI": {"digits": True, "min": 6, "max": 10},
    "CE": {"digits": True, "min": 6, "max": 12},
    "PASSPORT": {"regex": r'^[A-Z0-9]{5,20}$'}
}

def validate_document(document_type: str, document_number: str) -> bool:
    """
    Valida un documento según su tipo.
    
    Args:
        document_type (str): Tipo de documento (CC, TI, CE, PASSPORT)
        document_number (str): Número de documento
    
    Returns:
        bool: True si es válido, False si no.
    """
    if not document_number or not document_type:
        return False
    
    doc_type = document_type.upper()
    rules = DOCUMENT_RULES.get(doc_type)
    if not rules:
        return False
    
    if "digits" in rules and rules["digits"]:
        return document_number.isdigit() and rules["min"] <= len(document_number) <= rules["max"]
    if "regex" in rules:
        return re.match(rules["regex"], document_number) is not None
    
    return False


# -------------------------------
# Validación de teléfonos
# -------------------------------
def validate_phone(phone: str) -> bool:
    """
    Valida números de teléfono internacionales y locales.
    
    Formatos válidos: +573001234567, 3001234567
    """
    if not phone:
        return False
    pattern = r'^(\+\d{1,3})?(\d{7,12})$'
    return re.match(pattern, phone) is not None


# -------------------------------
# Sanitización de strings
# -------------------------------
def sanitize_input(value: str, max_length: int = 255) -> str:
    """
    Sanitiza cadenas eliminando caracteres peligrosos y recortando longitud.
    
    Args:
        value (str): Cadena a sanitizar.
        max_length (int): Longitud máxima permitida.
    
    Returns:
        str: Cadena sanitizada.
    """
    if not value:
        return ""
    sanitized = re.sub(r'[<>;"\'%]', '', value)
    return sanitized[:max_length]


# -------------------------------
# Validación de contraseñas
# -------------------------------
def validate_password(password: str, min_length: int = 8, require_numbers: bool = True, require_letters: bool = True) -> bool:
    """
    Valida contraseña según reglas de longitud y complejidad.
    
    Args:
        password (str): Contraseña a validar.
        min_length (int): Longitud mínima.
        require_numbers (bool): Requerir al menos un número.
        require_letters (bool): Requerir al menos una letra.
    
    Returns:
        bool: True si cumple las reglas.
    """
    if not password or len(password) < min_length:
        return False
    if require_letters and not re.search(r'[A-Za-z]', password):
        return False
    if require_numbers and not re.search(r'\d', password):
        return False
    return True
