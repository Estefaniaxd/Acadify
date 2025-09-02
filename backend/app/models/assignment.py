# backend/app/models/assignment.py
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import enum
from datetime import datetime

# -----------------------
# Enum de estados de entrega
# -----------------------
class SubmissionStatus(enum.Enum):
    """Estados posibles para la entrega de una tarea"""
    SUBMITTED = "submitted"
    NOT_SUBMITTED = "not_submitted"
    REVIEWED = "reviewed"


# -----------------------
# Modelo de tarea/actividad
# -----------------------
class Assignment(BaseModel):
    """Modelo que representa una tarea o actividad académica"""
    __tablename__ = "assignments"
    
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    assignment_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    due_date = Column(DateTime(timezone=True), nullable=True)
    attachment_file = Column(Text, nullable=True)
    allows_late_submissions = Column(Boolean, nullable=False, default=False)
    
    # Relaciones
    teacher = relationship(
        "Teacher", 
        back_populates="assignments",
        lazy="selectin"
    )
    class_session = relationship(
        "Class", 
        back_populates="assignments",
        lazy="selectin"
    )
    submissions = relationship(
        "AssignmentSubmission", 
        back_populates="assignment",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


# -----------------------
# Modelo de entrega de tarea
# -----------------------
class AssignmentSubmission(BaseModel):
    """Modelo que representa la entrega de una tarea por un estudiante"""
    __tablename__ = "assignment_submissions"
    
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    grade_value_id = Column(UUID(as_uuid=True), ForeignKey("grade_values.id", ondelete="SET NULL"), nullable=True)
    
    file_url = Column(Text, nullable=False)
    submission_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    status = Column(SQLEnum(SubmissionStatus), nullable=False, default=SubmissionStatus.SUBMITTED)
    text_feedback = Column(Text, nullable=True)
    audio_feedback = Column(Text, nullable=True)
    
    # Relaciones
    assignment = relationship(
        "Assignment",
        back_populates="submissions",
        lazy="selectin"
    )
    student = relationship(
        "Student",
        back_populates="assignment_submissions",
        lazy="selectin"
    )
    grade_value = relationship(
        "GradeValue",
        back_populates="assignment_submissions",
        lazy="selectin"
    )
