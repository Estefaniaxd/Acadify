from passlib.context import CryptContext

# Contexto de hashing seguro con Argon2 y fallback Bcrypt
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__memory_cost=65536,   # 64 MB
    argon2__time_cost=3,         # iteraciones
    argon2__parallelism=1
)

def get_password_hash(password: str) -> str:
    """
    Genera el hash seguro de una contraseña.

    Args:
        password (str): Contraseña en texto plano.

    Returns:
        str: Hash seguro de la contraseña.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash.

    Args:
        plain_password (str): Contraseña en texto plano.
        hashed_password (str): Hash previamente generado.

    Returns:
        bool: True si coinciden, False en caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)
