from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME:str = "Acadify"
    PROJECT_VERSION:str = "0.0.1"
    # JWT Configuration
    JWT_SECRET: str = Field(..., description="Secret key for JWT tokens")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=10, description="Access token lifespan")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, description="Refresh token lifespan")

    # Redis Configuration  
    REDIS_URL: str = Field(..., description="Redis connection URL")

    # Security
    BCRYPT_ROUNDS: int = Field(default=12, description="Bcrypt hashing rounds")
    MAX_LOGIN_ATTEMPTS: int = Field(default=5, description="Max failed login attempts")
    LOCKOUT_DURATION_MINUTES: int = Field(default=15, description="Account lockout duration")

    # OAuth2 Google
    GOOGLE_CLIENT_ID: str = Field(..., description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., description="Google OAuth client secret")
    GOOGLE_REDIRECT_URI: str = Field(..., description="OAuth callback URI")

    # Email Configuration (opcional)
    SMTP_HOST: str = Field(default="", description="SMTP server host")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USER: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password")
    EMAIL_FROM: str = Field(default="noreply@acadify.com", description="From email address")

    # Frontend URL
    FRONTEND_URL: str = Field(..., description="Frontend application URL")

    # Security headers
    SECURE_COOKIES: bool = Field(default=True, description="Use secure cookies in production")
    DATABASE_URL:str 

    class Config:
        env_file = "../.env"

settings = Settings()