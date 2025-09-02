from pydantic_settings import BaseSettings
from typing import Dict, List, Optional, Set
import secrets


class Settings(BaseSettings):
    """Configuraciones de la aplicación"""

    # Configuración de la aplicación
    PROJECT_NAME: str = "Acadify"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Plataforma educativa con gamificación y IA"
    DEBUG: bool = False

    # Configuración de base de datos
    DATABASE_URL = "postgresql://postgre:243019@localhost:5432/acadify_new"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgre"
    DATABASE_PASSWORD: str = "243019"
    DATABASE_NAME: str = "acadify"

    # Configuración de seguridad
    SECRET_KEY: str = secrets.token_urlsafe(32)  # para producción, usar .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Configuración de CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Configuración de archivos
    UPLOAD_FOLDER: str = "uploads"
    MAX_UPLOAD_SIZE: int = 52_428_800  # 50MB
    ALLOWED_EXTENSIONS: Set[str] = {
        "txt", "pdf", "png", "jpg", "jpeg", "gif", "mp4", "mp3",
        "doc", "docx", "xls", "xlsx", "ppt", "pptx"
    }

    # Configuración de email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/acadify.log"

    # Configuración de Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Configuración de API externa (IA)
    OPENAI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-3.5-turbo"

    # Configuración OAuth2
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None

    # URL del frontend para redirecciones
    FRONTEND_URL: str = "http://localhost:3000"

    # URLs de callback OAuth2 (construcción dinámica)
    @property
    def OAUTH_CALLBACK_URLS(self) -> Dict[str, str]:
        return {
            "google": f"{self.FRONTEND_URL}/auth/google/callback",
            "github": f"{self.FRONTEND_URL}/auth/github/callback",
            "microsoft": f"{self.FRONTEND_URL}/auth/microsoft/callback",
        }

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global
settings = Settings()
