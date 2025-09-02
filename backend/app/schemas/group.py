# backend/app/schemas/group.py
from typing import Optional, List
from pydantic import BaseModel, validator
from uuid import UUID
from datetime import datetime
from app.models.group import GroupShift, StudentGroupStatus

class GroupBase(BaseModel):
    """Schema base para grupo"""
    name: str
    shift: GroupShift = GroupShift.MORNING
    
    @validator('name')
    def validate_name(cls, v):
        """Valida que el nombre del grupo sea válido"""
        if not v or len(v.strip()) < 2:
            raise ValueError('El nombre del grupo debe tener al menos 2 caracteres')
        if len(v) > 50:
            raise ValueError('El nombre del grupo no puede tener más de 50 caracteres')
        return v.strip()

class GroupCreate(GroupBase):
    """Schema para creación de grupo"""
    tutor_teacher_id: Optional[UUID] = None

class GroupUpdate(BaseModel):
    """Schema para actualización de grupo"""
    name: Optional[str] = None
    shift: Optional[GroupShift] = None
    tutor_teacher_id: Optional[UUID] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Valida que el nombre del grupo sea válido si se proporciona"""
        if v is not None and (not v or len(v.strip()) < 2):
            raise ValueError('El nombre del grupo debe tener al menos 2 caracteres')
        return v.strip() if v else None

class GroupInDB(GroupBase):
    """Schema para grupo en base de datos"""
    id: UUID
    program_id: UUID
    tutor_teacher_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class GroupResponse(GroupInDB):
    """Schema para respuesta de grupo"""
    pass

class GroupWithDetails(GroupResponse):
    """Schema para grupo con detalles completos"""
    # Información del programa
    program_name: str
    program_level: str
    
    # Información de la institución
    institution_name: str
    
    # Información del tutor
    tutor_teacher_name: Optional[str] = None
    tutor_teacher_email: Optional[str] = None
    
    # Estadísticas
    active_students_count: int = 0
    assigned_courses_count: int = 0

class GroupListResponse(BaseModel):
    """Schema para respuesta de lista de grupos"""
    groups: List[GroupResponse]
    total: int
    skip: int
    limit: int

# Schemas para gestión de estudiantes en grupos
class StudentGroupBase(BaseModel):
    """Schema base para estudiante en grupo"""
    group_id: UUID
    student_id: UUID
    status: StudentGroupStatus = StudentGroupStatus.ACTIVE

class StudentGroupCreate(StudentGroupBase):
    """Schema para agregar estudiante a grupo"""
    pass

class StudentGroupResponse(BaseModel):
    """Schema para respuesta de estudiante en grupo"""
    id: UUID
    group_id: UUID
    student_id: UUID
    enrollment_date: datetime
    status: StudentGroupStatus
    
    # Información del estudiante
    student_first_names: str
    student_last_names: str
    student_email: str
    student_document_number: str
    
    class Config:
        from_attributes = True

class GroupStudentsResponse(BaseModel):
    """Schema para estudiantes de un grupo"""
    group_id: UUID
    group_name: str
    students: List[StudentGroupResponse]
    total_students: int

# Schemas para gestión de cursos en grupos
class GroupCourseAssignment(BaseModel):
    """Schema para asignación de curso a grupo"""
    course_id: UUID
    teacher_id: UUID
    
    @validator('course_id', 'teacher_id')
    def validate_ids(cls, v):
        """Valida que se proporcionen IDs válidos"""
        if not v:
            raise ValueError('Los IDs son requeridos')
        return v

class GroupCourseInfo(BaseModel):
    """Schema para información de curso en grupo"""
    id: UUID
    course_id: UUID
    course_name: str
    teacher_id: UUID
    teacher_name: str
    assignment_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class GroupCoursesResponse(BaseModel):
    """Schema para cursos de un grupo"""
    group_id: UUID
    group_name: str
    courses: List[GroupCourseInfo]
    total_courses: int

# Schemas para búsqueda y filtros
class GroupSearchParams(BaseModel):
    """Schema para parámetros de búsqueda de grupos"""
    query: Optional[str] = None
    program_id: Optional[UUID] = None
    shift: Optional[GroupShift] = None
    has_tutor: Optional[bool] = None
    skip: int = 0
    limit: int = 100

class TutorAssignment(BaseModel):
    """Schema para asignación de tutor a grupo"""
    teacher_id: UUID
    
    @validator('teacher_id')
    def validate_teacher_id(cls, v):
        """Valida que se proporcione un ID de docente válido"""
        if not v:
            raise ValueError('El ID del docente es requerido')
        return v

class GroupStatistics(BaseModel):
    """Schema para estadísticas de grupo"""
    group_id: UUID
    group_name: str
    active_students_count: int
    assigned_courses_count: int
    tutor_teacher_name: Optional[str] = None
    program_name: str
    institution_name: str
    enrollment_capacity: Optional[int] = None
    completion_rate: Optional[float] = None

# Schema para invitaciones a grupos
class GroupInvitation(BaseModel):
    """Schema para invitación a grupo"""
    student_email: str
    group_id: UUID
    message: Optional[str] = None
    
    @validator('student_email')
    def validate_email(cls, v):
        """Valida el formato del email"""
        if not v or '@' not in v:
            raise ValueError('Debe proporcionar un email válido')
        return v.lower().strip()

class BulkStudentAssignment(BaseModel):
    """Schema para asignación masiva de estudiantes"""
    student_ids: List[UUID]
    group_id: UUID
    
    @validator('student_ids')
    def validate_student_ids(cls, v):
        """Valida la lista de IDs de estudiantes"""
        if not v or len(v) == 0:
            raise ValueError('Debe proporcionar al menos un ID de estudiante')
        if len(v) > 50:
            raise ValueError('No se pueden asignar más de 50 estudiantes a la vez')
        return v