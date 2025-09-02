# backend/app/schemas/assignment.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from ..models.assignment import SubmissionStatus

# -----------------------
# Esquemas base de Assignment
# -----------------------
class AssignmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    assignment_date: datetime
    due_date: Optional[datetime] = None
    attachment_file: Optional[str] = None
    allows_late_submissions: bool = False

    @validator('due_date')
    def validate_due_date(cls, v, values):
        """La fecha de entrega debe ser posterior a la fecha de asignación"""
        if v and 'assignment_date' in values and v <= values['assignment_date']:
            raise ValueError('Due date must be after assignment date')
        return v


class AssignmentCreate(AssignmentBase):
    teacher_id: Optional[UUID] = None
    class_id: UUID


class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    attachment_file: Optional[str] = None
    allows_late_submissions: Optional[bool] = None


class AssignmentInDB(AssignmentBase):
    id: UUID
    teacher_id: Optional[UUID]
    class_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Assignment(AssignmentInDB):
    pass


# -----------------------
# Esquemas de AssignmentSubmission
# -----------------------
class AssignmentSubmissionBase(BaseModel):
    file_url: str = Field(..., min_length=1)
    submission_date: datetime
    status: SubmissionStatus = SubmissionStatus.SUBMITTED
    text_feedback: Optional[str] = None
    audio_feedback: Optional[str] = None


class AssignmentSubmissionCreate(BaseModel):
    assignment_id: UUID
    file_url: str = Field(..., min_length=1)
    submission_date: datetime = Field(default_factory=datetime.utcnow)


class AssignmentSubmissionUpdate(BaseModel):
    file_url: Optional[str] = Field(None, min_length=1)
    status: Optional[SubmissionStatus] = None
    text_feedback: Optional[str] = None
    audio_feedback: Optional[str] = None
    grade_value_id: Optional[UUID] = None


class AssignmentSubmissionInDB(AssignmentSubmissionBase):
    id: UUID
    assignment_id: UUID
    student_id: UUID
    grade_value_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AssignmentSubmission(AssignmentSubmissionInDB):
    pass


# -----------------------
# Esquemas de respuestas con información relacionada
# -----------------------
class AssignmentWithTeacher(Assignment):
    teacher_name: Optional[str] = None


class AssignmentWithSubmissions(Assignment):
    submissions: List[AssignmentSubmission] = []
    total_submissions: int = 0


class StudentSubmissionDetail(AssignmentSubmission):
    assignment_title: str
    assignment_description: Optional[str]
    assignment_due_date: Optional[datetime]


class TeacherSubmissionView(AssignmentSubmission):
    student_name: str
    student_email: str


# -----------------------
# Esquemas para estadísticas
# -----------------------
class AssignmentStats(BaseModel):
    total_assignments: int
    assignments_with_submissions: int
    total_submissions: int
    on_time_submissions: int
    late_submissions: int
    pending_review: int


class SubmissionStats(BaseModel):
    submitted: int
    not_submitted: int
    reviewed: int
