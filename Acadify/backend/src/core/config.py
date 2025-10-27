# src/core/config.py
import secrets
from typing import Optional, List, Any, Union
from pydantic import AnyHttpUrl, EmailStr, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Permitir que DATABASE_URL se lea directamente del .env si está presente
    DATABASE_URL: Optional[str] = None
    """
    Application configuration settings.
    
    All settings can be overridden with environment variables.
    """
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    # ===============================
    # API Configuration
    # ===============================
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Acadify API"
    PROJECT_DESCRIPTION: str = "Sistema de gestión académica"
    PROJECT_VERSION: str = "1.0.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # ===============================
    # Security Configuration
    # ===============================
    
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    
    # JWT Token Settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30    # 30 days
    
    # Password Reset Settings
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    
    # Login Security
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    LOGIN_ATTEMPT_WINDOW_MINUTES: int = 15
    
    # ===============================
    # Database Configuration
    # ===============================
    
    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "acadify_user"
    POSTGRES_PASSWORD: str = "acadify_password"
    POSTGRES_DB: str = "acadify_db"
    
    # Database URL (constructed from components)
    @property
    def database_url(self) -> str:
        # Prioridad: variable directa del .env, si no, construirla
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # ===============================
    # Redis Configuration
    # ===============================
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Redis URL (constructed from components)
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ===============================
    # Email Configuration (SMTP)
    # ===============================
    
    # SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_TLS: bool = True
    EMAIL_FROM: EmailStr = "noreply@acadify.com"
    
    # Email Templates
    EMAIL_TEMPLATES_DIR: str = "src/templates/emails"
    
    # Email Rate Limiting
    EMAIL_RATE_LIMIT_PER_HOUR: int = 10
    
    @field_validator("SMTP_USER")
    @classmethod
    def validate_smtp_user(cls, v: str) -> str:
        # Allow empty SMTP_USER in development/testing
        return v
    
    @field_validator("SMTP_PASS")
    @classmethod
    def validate_smtp_pass(cls, v: str) -> str:
        # Allow empty SMTP_PASS in development/testing
        return v
    
    # ===============================
    # Application Environment
    # ===============================
    
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    @field_validator("DEBUG", mode="before")
    @classmethod
    def set_debug_from_env(cls, v: Any) -> bool:
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # ===============================
    # File Upload Configuration
    # ===============================
    
    # Upload paths
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_FILE_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".pdf", 
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"
    ]
    
    # Profile images
    PROFILE_IMAGE_DIR: str = "uploads/profiles"
    MAX_PROFILE_IMAGE_SIZE: int = 2 * 1024 * 1024  # 2 MB
    
    # ===============================
    # Avatar Configuration
    # ===============================
    
    # Avatar Storage
    AVATAR_STORAGE_TYPE: str = "local"  # local or s3
    AVATAR_STORAGE_PATH: str = "static"
    AVATAR_ASSETS_PATH: str = "static/assets"
    AVATAR_ASSETS_BASE_URL: str = "/static/assets"
    
    # Avatar Processing
    AVATAR_MAX_FILE_SIZE: int = 1024 * 1024 * 1.5  # 1.5 MB
    AVATAR_STANDARD_RESOLUTION: List[int] = [512, 512]
    AVATAR_ALLOWED_FORMATS: List[str] = ["PNG"]
    
    # Avatar Cache (Redis)
    AVATAR_PREVIEW_CACHE_TTL: int = 3600  # 1 hour
    AVATAR_COMPOSITION_CACHE_TTL: int = 7 * 24 * 3600  # 7 days
    AVATAR_MANIFEST_CACHE_TTL: int = 24 * 3600  # 24 hours
    
    # AWS S3 (for future use)
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # ===============================
    # Third-party Service Configuration
    # ===============================
    
    # OAuth Settings (Google, Microsoft, etc.)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    
    # reCAPTCHA (optional)
    RECAPTCHA_SITE_KEY: Optional[str] = None
    RECAPTCHA_SECRET_KEY: Optional[str] = None
    
    # ===============================
    # Feature Flags
    # ===============================
    
    # Authentication features
    ENABLE_2FA: bool = True
    ENABLE_EMAIL_2FA: bool = True
    ENABLE_TOTP_2FA: bool = True
    ENABLE_OAUTH: bool = False
    
    # Registration features
    ENABLE_REGISTRATION: bool = True
    REQUIRE_EMAIL_VERIFICATION: bool = True
    
    # Security features
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_ACCOUNT_LOCKOUT: bool = True
    
    # ===============================
    # Monitoring and Health Checks
    # ===============================
    
    # Health check endpoints
    ENABLE_HEALTH_CHECKS: bool = True
    
    # Metrics collection
    ENABLE_METRICS: bool = False
    METRICS_ENDPOINT: str = "/metrics"
    
    # ===============================
    # Development Settings
    # ===============================
    
    # Development tools
    ENABLE_SWAGGER_UI: bool = True
    ENABLE_REDOC: bool = True
    
    # Testing
    TESTING: bool = False
    TEST_DATABASE_URL: Optional[str] = None
    
    # ===============================
    # Timezone and Localization
    # ===============================
    
    TIMEZONE: str = "America/Bogota"
    DEFAULT_LOCALE: str = "es_CO"
    SUPPORTED_LOCALES: List[str] = ["es_CO", "en_US"]
    
    # ===============================
    # Performance Settings
    # ===============================
    
    # Database connection pool
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    
    # Request timeout
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    # Cache settings
    CACHE_TTL_SECONDS: int = 300  # 5 minutes default
    
    # ===============================
    # Business Logic Configuration
    # ===============================
    
    # Institution settings
    MAX_USERS_PER_INSTITUTION: int = 10000
    MAX_PROGRAMS_PER_INSTITUTION: int = 100
    MAX_COURSES_PER_PROGRAM: int = 200
    
    # File storage limits per institution
    MAX_STORAGE_GB_PER_INSTITUTION: int = 10
    
    # Chat and communication
    MAX_MESSAGE_LENGTH: int = 2000
    MAX_CHAT_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    
    # Gamification
    ENABLE_GAMIFICATION: bool = True
    DEFAULT_POINTS_PER_ACTIVITY: int = 10
    
    # ===============================
    # Security Headers and CORS
    # ===============================
    
    # Security headers
    ENABLE_SECURITY_HEADERS: bool = True
    
    # CORS configuration
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = [
        "Authorization", "Content-Type", "X-Requested-With", 
        "X-Refresh-Token", "X-CSRF-Token"
    ]
    
    # ===============================
    # Validation Methods
    # ===============================
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.TESTING
    
    def get_database_url(self, async_driver: bool = False) -> str:
        """Get database URL with optional async driver"""
        if self.TESTING and self.TEST_DATABASE_URL:
            return self.TEST_DATABASE_URL
        
        if async_driver:
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DATABASE_URL
    
    # ===============================
    # Email Configuration Validation
    # ===============================
    
    def validate_email_config(self) -> bool:
        """Validate email configuration is complete"""
        required_fields = [
            self.SMTP_HOST,
            self.SMTP_USER,
            self.SMTP_PASS,
            self.EMAIL_FROM
        ]
        return all(required_fields)
    
    def validate_redis_config(self) -> bool:
        """Validate Redis configuration is complete"""
        return bool(self.REDIS_HOST and self.REDIS_PORT)
    
    # ===============================
    # Default Admin User (for initial setup)
    # ===============================
    
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "AdminPassword123!"
    
    # Only create default admin in development
    CREATE_DEFAULT_ADMIN: bool = True
    
    @field_validator("CREATE_DEFAULT_ADMIN", mode="before")
    @classmethod
    def validate_default_admin_creation(cls, v: Any, info) -> bool:
        # Only allow in development environment
        env = info.data.get("ENVIRONMENT", "development").lower()
        return bool(v) and env == "development"


# ===============================
# Settings Instance and Factory
# ===============================

_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """
    Get application settings singleton.
    
    Creates settings instance on first call and reuses it.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def reload_settings() -> Settings:
    """
    Force reload of settings (useful for testing).
    """
    global _settings
    _settings = Settings()
    return _settings

# ===============================
# Environment-specific Settings
# ===============================

class DevelopmentSettings(Settings):
    """Development environment settings"""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    CREATE_DEFAULT_ADMIN: bool = True
    ENABLE_SWAGGER_UI: bool = True
    ENABLE_REDOC: bool = True

class ProductionSettings(Settings):
    """Production environment settings"""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    CREATE_DEFAULT_ADMIN: bool = False
    ENABLE_SWAGGER_UI: bool = False
    ENABLE_REDOC: bool = False
    
    # More restrictive settings for production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    MAX_LOGIN_ATTEMPTS: int = 3
    LOCKOUT_DURATION_MINUTES: int = 30

class TestingSettings(Settings):
    """Testing environment settings"""
    ENVIRONMENT: str = "testing"
    TESTING: bool = True
    DEBUG: bool = True
    
    # Use in-memory databases for testing
    TEST_DATABASE_URL: str = "sqlite:///:memory:"
    
    # Disable external services in tests
    ENABLE_2FA: bool = False
    ENABLE_RATE_LIMITING: bool = False

def get_settings_for_environment(env: str) -> Settings:
    """Get settings instance for specific environment"""
    env = env.lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# ===============================
# Configuration Validation
# ===============================

def validate_configuration(settings: Settings) -> List[str]:
    """
    Validate configuration and return list of errors/warnings.
    """
    errors = []
    warnings = []
    
    # Required settings validation
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key":
        errors.append("SECRET_KEY must be set to a secure random value")
    
    if not settings.validate_email_config() and settings.ENVIRONMENT != "testing":
        warnings.append("Email configuration incomplete - email features will not work")
    
    if not settings.validate_redis_config():
        errors.append("Redis configuration is required")
    
    # Production-specific validations
    if settings.is_production():
        if settings.DEBUG:
            warnings.append("DEBUG should be False in production")
        if settings.CREATE_DEFAULT_ADMIN:
            errors.append("CREATE_DEFAULT_ADMIN should be False in production")
        if settings.ACCESS_TOKEN_EXPIRE_MINUTES > 60:
            warnings.append("Consider shorter token expiration in production")
    
    # Development warnings
    if settings.is_development() and not settings.DEBUG:
        warnings.append("Consider enabling DEBUG in development")
    
    # Combine errors and warnings
    all_issues = [f"ERROR: {error}" for error in errors]
    all_issues.extend([f"WARNING: {warning}" for warning in warnings])
    
    return all_issues


# ===============================
# Export commonly used settings
# ===============================

# Convenience exports
settings = get_settings()

# Database URL
DATABASE_URL = settings.DATABASE_URL

# Redis URL  
REDIS_URL = settings.REDIS_URL

# JWT Settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
