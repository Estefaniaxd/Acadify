from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from uuid import UUID
from datetime import datetime
from app.models.institution import InstitutionType, EducationalLevel, InstitutionSector

# ---------- BASE SCHEMA ----------
class InstitutionBase(BaseModel):
    name: str
    acronym: Optional[str] = None
    motto: Optional[str] = None
    institution_type: InstitutionType
    uses_programs: bool = True
    educational_level: EducationalLevel
    sector: InstitutionSector
    address: Optional[str] = None
    city: Optional[str] = None
    country: str
    institutional_email: EmailStr
    phone: str
    tax_id: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('El nombre debe tener al menos 3 caracteres')
        if len(v) > 100:
            raise ValueError('El nombre no puede tener más de 100 caracteres')
        return v.strip()
    
    @validator('acronym')
    def validate_acronym(cls, v):
        if v and len(v) > 10:
            raise ValueError('El acrónimo no puede tener más de 10 caracteres')
        return v.upper() if v else None
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v:
            raise ValueError('El teléfono es requerido')
        clean_phone = ''.join(filter(str.isdigit, v))
        if len(clean_phone) < 7 or len(clean_phone) > 15:
            raise ValueError('El teléfono debe tener entre 7 y 15 dígitos')
        return clean_phone  # Guardamos limpio para consistencia
    
    @validator('tax_id')
    def validate_tax_id(cls, v):
        if v and len(v.strip()) < 5:
            raise ValueError('El NIT debe tener al menos 5 caracteres')
        return v.strip() if v else None

# ---------- CREATE / UPDATE SCHEMAS ----------
class InstitutionCreate(InstitutionBase):
    pass

class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    acronym: Optional[str] = None
    motto: Optional[str] = None
    institution_type: Optional[InstitutionType] = None
    uses_programs: Optional[bool] = None
    educational_level: Optional[EducationalLevel] = None
    sector: Optional[InstitutionSector] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    institutional_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None and (len(v.strip()) < 3):
            raise ValueError('El nombre debe tener al menos 3 caracteres')
        return v.strip() if v else None

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            clean_phone = ''.join(filter(str.isdigit, v))
            if len(clean_phone) < 7 or len(clean_phone) > 15:
                raise ValueError('El teléfono debe tener entre 7 y 15 dígitos')
            return clean_phone
        return v

# ---------- DB SCHEMA ----------
class InstitutionInDB(InstitutionBase):
    id: UUID
    administrator_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# ---------- RESPONSE SCHEMAS ----------
class InstitutionResponse(InstitutionInDB):
    pass

class InstitutionWithStats(InstitutionResponse):
    students_count: int = 0
    teachers_count: int = 0
    coordinators_count: int = 0
    courses_count: int = 0
    programs_count: int = 0

class InstitutionListResponse(BaseModel):
    institutions: List[InstitutionResponse]
    total: int
    skip: int
    limit: int

# ---------- COORDINATOR SCHEMAS ----------
class CoordinatorAssignment(BaseModel):
    coordinator_id: UUID
    institution_id: UUID

class CoordinatorInInstitution(BaseModel):
    id: UUID
    user_id: UUID
    office_hours: Optional[str] = None
    career_start_date: datetime
    first_names: str
    last_names: str
    institutional_email: str

    class Config:
        orm_mode = True

class InstitutionCoordinators(BaseModel):
    institution_id: UUID
    coordinators: List[CoordinatorInInstitution]

# ---------- SEARCH & TRANSFER SCHEMAS ----------
class InstitutionSearchParams(BaseModel):
    query: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    institution_type: Optional[InstitutionType] = None
    educational_level: Optional[EducationalLevel] = None
    sector: Optional[InstitutionSector] = None
    skip: int = 0
    limit: int = 100

class InstitutionTransferOwnership(BaseModel):
    new_admin_id: UUID

    @validator('new_admin_id')
    def validate_new_admin_id(cls, v):
        if not v:
            raise ValueError('El ID del nuevo administrador es requerido')
        return v
