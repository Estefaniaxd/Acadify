# backend/app/schemas/class_schema.py
from typing import Optional, List
from pydantic import BaseModel, validator
from uuid import UUID
from datetime import datetime, timedelta
from app.models.class_model import AttendanceStatus

# -------------------- HELPERS --------------------
def strip_str(value: Optional[str]) -> Optional[str]:
    return value.strip() if value else None

def validate_future_datetime(value: datetime) -> datetime:
    if value < datetime.utcnow():
        raise ValueError("La fecha debe ser futura")
    return value

# -------------------- CLASSES --------------------
class ClassBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    duration: timedelta
    video_call_link: str
    platform_id: Optional[UUID] = None

    @validator("title")
    def validate_title(cls, v):
        v = strip_str(v)
        if not v or len(v) < 3:
            raise ValueError("El título debe tener al menos 3 caracteres")
        if len(v) > 200:
            raise ValueError("El título no puede tener más de 200 caracteres")
        return v

    @validator("description")
    def validate_description(cls, v):
        v = strip_str(v)
        if v and len(v) > 1000:
            raise ValueError("La descripción no puede superar 1000 caracteres")
        return v

    @validator("start_time")
    def validate_start_time(cls, v):
        return validate_future_datetime(v)

    @validator("duration")
    def validate_duration(cls, v):
        if v.total_seconds() < 900:
            raise ValueError("Duración mínima: 15 minutos")
        if v.total_seconds() > 14400:
            raise ValueError("Duración máxima: 4 horas")
        return v

    @validator("video_call_link")
    def validate_video_call_link(cls, v):
        v = strip_str(v)
        if not v or len(v) < 10:
            raise ValueError("Debe proporcionar un enlace válido de videollamada")
        return v

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    duration: Optional[timedelta] = None
    video_call_link: Optional[str] = None
    platform_id: Optional[UUID] = None

    @validator("title")
    def validate_title(cls, v):
        v = strip_str(v)
        if v is not None and len(v) < 3:
            raise ValueError("El título debe tener al menos 3 caracteres")
        return v

    @validator("start_time")
    def validate_start_time(cls, v):
        if v is not None:
            return validate_future_datetime(v)
        return v

    @validator("duration")
    def validate_duration(cls, v):
        if v is not None:
            if v.total_seconds() < 900:
                raise ValueError("Duración mínima: 15 minutos")
            if v.total_seconds() > 14400:
                raise ValueError("Duración máxima: 4 horas")
        return v

    @validator("description")
    def validate_description(cls, v):
        return strip_str(v)

    @validator("video_call_link")
    def validate_video_call_link(cls, v):
        v = strip_str(v)
        if v and len(v) < 10:
            raise ValueError("El enlace de videollamada debe ser válido")
        return v

# -------------------- DB & RESPONSE --------------------
class ClassInDB(ClassBase):
    id: UUID
    group_course_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ClassResponse(ClassInDB):
    pass

class ClassWithDetails(ClassResponse):
    course_name: str
    group_name: str
    teacher_name: str
    teacher_email: str
    platform_name: Optional[str] = None
    total_students: int = 0
    present_students: int = 0
    attendance_percentage: float = 0.0
    materials_count: int = 0
    assignments_count: int = 0

class ClassListResponse(BaseModel):
    classes: List[ClassResponse]
    total: int
    skip: int
    limit: int

# -------------------- ATTENDANCE --------------------
class AttendanceBase(BaseModel):
    class_id: UUID
    student_id: UUID
    status: AttendanceStatus

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: AttendanceStatus

class AttendanceResponse(BaseModel):
    id: UUID
    class_id: UUID
    student_id: UUID
    status: AttendanceStatus
    created_at: datetime
    student_first_names: str
    student_last_names: str
    student_email: str
    student_document_number: str

    class Config:
        from_attributes = True

class ClassAttendanceResponse(BaseModel):
    class_id: UUID
    class_title: str
    start_time: datetime
    attendances: List[AttendanceResponse]
    attendance_summary: dict

class BulkAttendanceUpdate(BaseModel):
    attendance_data: List[AttendanceUpdate]

    @validator("attendance_data")
    def validate_attendance_data(cls, v):
        if not v:
            raise ValueError("Debe proporcionar al menos un registro de asistencia")
        return v

# -------------------- SEARCH & STATISTICS --------------------
class ClassSearchParams(BaseModel):
    query: Optional[str] = None
    group_course_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    student_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    upcoming_only: bool = False
    skip: int = 0
    limit: int = 100

class ClassStatistics(BaseModel):
    class_id: UUID
    title: str
    start_time: datetime
    total_students: int
    present_students: int
    justified_students: int
    absent_students: int
    attendance_percentage: float
    materials_count: int
    assignments_count: int
    teacher_name: str
    course_name: str
    group_name: str

# -------------------- REPROGRAM & CANCEL --------------------
class ClassReschedule(BaseModel):
    new_start_time: datetime
    new_duration: Optional[timedelta] = None
    reason: Optional[str] = None

    @validator("new_start_time")
    def validate_new_start_time(cls, v):
        return validate_future_datetime(v)

class ClassCancellation(BaseModel):
    reason: Optional[str] = None

    @validator("reason")
    def validate_reason(cls, v):
        v = strip_str(v)
        if v and len(v) > 500:
            raise ValueError("La razón no puede superar 500 caracteres")
        return v

# -------------------- CALENDAR --------------------
class ClassCalendarEvent(BaseModel):
    id: UUID
    title: str
    start_time: datetime
    duration: timedelta
    course_name: str
    group_name: str
    teacher_name: str
    video_call_link: str

    class Config:
        from_attributes = True

class ClassCalendarResponse(BaseModel):
    events: List[ClassCalendarEvent]
    start_date: datetime
    end_date: datetime
