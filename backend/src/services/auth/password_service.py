from src.core.config import settings
import re
from passlib.context import CryptContext


class PasswordService:
    """Servicio para hashing y validación de contraseñas"""

    def __init__(self):
        # Usar bcrypt con rounds configurables (por defecto 12)
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=getattr(settings, "BCRYPT_ROUNDS", 12),
        )

    def hash_password(self, password: str) -> str:
        """Hashear contraseña con bcrypt"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña contra hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def validate_password_policy(self, password: str) -> tuple[bool, list[str]]:
        """
        Validar que la contraseña cumple con las políticas de seguridad

        Returns:
            tuple: (is_valid, errors_list)
        """
        errors = []

        # Longitud mínima
        if len(password) < 10:
            errors.append("La contraseña debe tener al menos 10 caracteres")

        # Al menos una mayúscula
        if not re.search(r"[A-Z]", password):
            errors.append("La contraseña debe contener al menos una letra mayúscula")

        # Al menos una minúscula
        if not re.search(r"[a-z]", password):
            errors.append("La contraseña debe contener al menos una letra minúscula")

        # Al menos un dígito
        if not re.search(r"\d", password):
            errors.append("La contraseña debe contener al menos un número")

        # Al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("La contraseña debe contener al menos un carácter especial")

        # No debe contener secuencias obvias (opcional)
        forbidden_sequences = [
            "123456",
            "abcdef",
            "qwerty",
            "password",
            "admin",
            "acadify",
        ]

        password_lower = password.lower()
        for sequence in forbidden_sequences:
            if sequence in password_lower:
                errors.append(
                    f"La contraseña no debe contener secuencias obvias como '{sequence}'"
                )

        return len(errors) == 0, errors

    def generate_password_strength_score(self, password: str) -> int:
        """
        Generar score de fortaleza de contraseña (0-100)
        """
        score = 0

        # Longitud (máximo 25 puntos)
        length_score = min(25, len(password) * 2)
        score += length_score

        # Variedad de caracteres (máximo 40 puntos)
        if re.search(r"[a-z]", password):
            score += 10
        if re.search(r"[A-Z]", password):
            score += 10
        if re.search(r"\d", password):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10

        # Complejidad adicional (máximo 35 puntos)
        if len(set(password)) > len(password) * 0.7:  # Caracteres únicos
            score += 15

        if len(password) > 15:  # Longitud superior
            score += 10

        if re.search(r"[^\w\s]", password):  # Símbolos adicionales
            score += 10

        return min(100, score)

