from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# -------------------------------
# Enums
# -------------------------------

class DocumentTypeEnum(str, Enum):
    """Tipos de documento"""
    TI = "ti"
    CC = "cc"
    CE = "ce"


class UserRoleEnum(str, Enum):
    """Roles de usuario"""
    ADMINISTRATOR = "administrator"
    COORDINATOR = "coordinator"
    TEACHER = "teacher"
    STUDENT = "student"


class AccountStatusEnum(str, Enum):
    """Estados de cuenta"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


# -------------------------------
# Base Schemas
# -------------------------------

class UserBase(BaseModel):
    """Schema base para usuario"""
    institutional_email: EmailStr
    first_names: str = Field(..., min_length=2, max_length=100)
    last_names: str = Field(..., min_length=2, max_length=100)
    document_type: DocumentTypeEnum
    document_number: str = Field(..., min_length=5, max_length=20)
    role: UserRoleEnum
    phone: Optional[str] = Field(None, max_length=20)
    biography: Optional[str] = None


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=8, max_length=100)

    @validator('password')
    def validate_password(cls, v: str) -> str:
        """Valida que la contraseña tenga al menos una mayúscula, minúscula y número"""
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    first_names: Optional[str] = Field(None, min_length=2, max_length=100)
    last_names: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    biography: Optional[str] = None
    profile_image_url: Optional[str] = None
    cover_image_url: Optional[str] = None


# -------------------------------
# Response / Output Schemas
# -------------------------------

class UserResponse(UserBase):
    """Schema para respuesta de usuario"""
    id: str
    account_status: AccountStatusEnum
    created_at: datetime
    last_access: Optional[datetime]
    profile_image_url: Optional[str]
    cover_image_url: Optional[str]

    class Config:
        from_attributes = True


class UserOut(UserResponse):
    """Schema para salida de usuario (UserOut)"""
    class Config:
        from_attributes = True


class UserList(BaseModel):
    """Schema para lista de usuarios"""
    users: List[UserResponse]
    total: int
    page: int
    size: int

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """Estadísticas de usuario"""
    total_courses: int
    completed_courses: int
    pending_tasks: int
    attendance_percentage: float

    class Config:
        from_attributes = True


# -------------------------------
# Password Change
# -------------------------------

class PasswordChangeRequest(BaseModel):
    """Schema para cambio de contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def validate_new_password(cls, v: str) -> str:
        """Valida la nueva contraseña"""
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v
