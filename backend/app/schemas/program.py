from typing import Optional, List, Dict
from pydantic import BaseModel, validator
from uuid import UUID
from datetime import datetime
from app.models.program import ProgramLevel, ProgramType

# -------------------------------
# Base
# -------------------------------
class ProgramBase(BaseModel):
    name: str
    description: Optional[str] = None
    level: ProgramLevel
    program_type: ProgramType

    @validator('name')
    def validate_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError('El nombre del programa debe tener al menos 3 caracteres')
        if len(v.strip()) > 100:
            raise ValueError('El nombre del programa no puede tener más de 100 caracteres')
        return v.strip()

    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v.strip()) > 2000:
            raise ValueError('La descripción no puede tener más de 2000 caracteres')
        return v.strip() if v else None

# -------------------------------
# Creación y actualización
# -------------------------------
class ProgramCreate(ProgramBase):
    pass

class ProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[ProgramLevel] = None
    program_type: Optional[ProgramType] = None

    @validator('name')
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 3:
            raise ValueError('El nombre del programa debe tener al menos 3 caracteres')
        return v.strip() if v else None

    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) > 2000:
            raise ValueError('La descripción no puede tener más de 2000 caracteres')
        return v.strip() if v else None

# -------------------------------
# DB y respuesta
# -------------------------------
class ProgramInDB(ProgramBase):
    id: UUID
    institution_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProgramResponse(ProgramInDB):
    pass

class ProgramWithDetails(ProgramResponse):
    institution_name: str
    institution_type: str
    students_count: int = 0
    groups_count: int = 0
    courses_count: int = 0

class ProgramListResponse(BaseModel):
    programs: List[ProgramResponse]
    total: int
    skip: int
    limit: int

class ProgramSearchParams(BaseModel):
    query: Optional[str] = None
    level: Optional[ProgramLevel] = None
    program_type: Optional[ProgramType] = None
    institution_id: Optional[UUID] = None
    skip: int = 0
    limit: int = 100

class ProgramStatistics(BaseModel):
    program_id: UUID
    program_name: str
    students_count: int
    groups_count: int
    courses_count: int
    institution_name: str
    level: str
    program_type: str
    enrollment_capacity: Optional[int] = None
    completion_rate: Optional[float] = None

class PopularProgram(BaseModel):
    program: ProgramResponse
    student_count: int = 0

class PopularProgramsResponse(BaseModel):
    programs: List[PopularProgram]
    institution_id: Optional[UUID] = None

class ProgramValidation(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    statistics: Dict = {}

# -------------------------------
# Estudiantes en programas
# -------------------------------
class ProgramStudentInfo(BaseModel):
    student_id: UUID
    first_names: str
    last_names: str
    institutional_email: str
    document_number: str
    enrollment_date: datetime
    educational_stage: str
    cumulative_average: Optional[str] = None

    class Config:
        from_attributes = True

class ProgramStudents(BaseModel):
    program_id: UUID
    program_name: str
    students: List[ProgramStudentInfo]
    total_students: int

# -------------------------------
# Grupos en programas
# -------------------------------
class ProgramGroupInfo(BaseModel):
    group_id: UUID
    group_name: str
    shift: str
    tutor_teacher_name: Optional[str] = None
    active_students_count: int = 0

    class Config:
        from_attributes = True

class ProgramGroups(BaseModel):
    program_id: UUID
    program_name: str
    groups: List[ProgramGroupInfo]
    total_groups: int
