from typing import Optional, List
from pydantic import BaseModel, validator
from uuid import UUID
from datetime import datetime
from app.models.course import CourseModality


class CourseBase(BaseModel):
    """Schema base para curso"""
    name: str
    description: Optional[str] = None
    modality: CourseModality
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator('name')
    def validate_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 2:
            raise ValueError('El nombre del curso debe tener al menos 2 caracteres')
        if len(v) > 50:
            raise ValueError('El nombre del curso no puede tener más de 50 caracteres')
        return v.strip()

    @validator('end_date')
    def validate_dates(cls, v: Optional[datetime], values) -> Optional[datetime]:
        start = values.get('start_date')
        if v and start and v <= start:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v.strip()) > 1000:
            raise ValueError('La descripción no puede tener más de 1000 caracteres')
        return v.strip() if v else None

    class Config:
        orm_mode = True


class CourseCreate(CourseBase):
    """Schema para creación de curso"""
    program_id: UUID

    @validator('program_id')
    def validate_program_id(cls, v: UUID) -> UUID:
        if not v:
            raise ValueError('El ID del programa es requerido')
        return v


class CourseUpdate(BaseModel):
    """Schema para actualización de curso"""
    name: Optional[str] = None
    description: Optional[str] = None
    modality: Optional[CourseModality] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    program_id: Optional[UUID] = None

    @validator('name')
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError('El nombre del curso debe tener al menos 2 caracteres')
            if len(v.strip()) > 50:
                raise ValueError('El nombre del curso no puede tener más de 50 caracteres')
            return v.strip()
        return v

    @validator('end_date')
    def validate_dates(cls, v: Optional[datetime], values) -> Optional[datetime]:
        start = values.get('start_date')
        if v and start and v <= start:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v.strip()) > 1000:
            raise ValueError('La descripción no puede tener más de 1000 caracteres')
        return v.strip() if v else None

    class Config:
        orm_mode = True


class CourseInDB(CourseBase):
    """Schema para curso en base de datos"""
    id: UUID
    institution_id: UUID
    coordinator_id: Optional[UUID] = None
    program_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class CourseResponse(CourseInDB):
    """Schema para respuesta de curso"""
    pass


class CourseWithDetails(CourseResponse):
    """Schema para curso con detalles completos"""
    coordinator_name: Optional[str] = None
    coordinator_email: Optional[str] = None
    institution_name: str
    program_name: str
    program_level: str
    groups_count: int = 0
    students_count: int = 0
    materials_count: int = 0
    classes_count: int = 0


class CourseListResponse(BaseModel):
    """Schema para respuesta de lista de cursos"""
    courses: List[CourseResponse]
    total: int
    skip: int
    limit: int

    class Config:
        orm_mode = True


class CourseSearchParams(BaseModel):
    """Schema para parámetros de búsqueda de cursos"""
    query: Optional[str] = None
    modality: Optional[CourseModality] = None
    program_id: Optional[UUID] = None
    institution_id: Optional[UUID] = None
    coordinator_id: Optional[UUID] = None
    active_only: bool = False
    skip: int = 0
    limit: int = 100


class CourseCoordinatorAssignment(BaseModel):
    """Schema para asignación de coordinador a curso"""
    coordinator_id: UUID

    @validator('coordinator_id')
    def validate_coordinator_id(cls, v: UUID) -> UUID:
        if not v:
            raise ValueError('El ID del coordinador es requerido')
        return v


class CourseStatistics(BaseModel):
    """Schema para estadísticas de curso"""
    course_id: UUID
    groups_count: int
    students_count: int
    materials_count: int
    classes_count: int
    assignments_count: int
    average_attendance: Optional[float] = None
    coordinator_name: Optional[str] = None
    institution_name: str
    program_name: str

    class Config:
        orm_mode = True


class CourseGroupInfo(BaseModel):
    """Schema para información de grupo en un curso"""
    group_id: UUID
    group_name: str
    teacher_name: Optional[str] = None
    assignment_date: Optional[datetime] = None
    students_count: int = 0

    class Config:
        orm_mode = True


class CourseGroups(BaseModel):
    """Schema para grupos de un curso"""
    course_id: UUID
    course_name: str
    groups: List[CourseGroupInfo]

    class Config:
        orm_mode = True
