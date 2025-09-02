from sqlalchemy import Column, String, ForeignKey, DateTime, Enum as SQLEnum, UniqueConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import enum

# -------------------------------
# Enums
# -------------------------------
class GroupShift(enum.Enum):
    """Jornadas de grupo"""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"

class StudentGroupStatus(enum.Enum):
    """Estados del estudiante en el grupo"""
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"
    FINISHED = "finished"

# -------------------------------
# Modelo de Grupo
# -------------------------------
class Group(BaseModel):
    """Modelo de grupo académico"""
    __tablename__ = "groups"
    
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    tutor_teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="SET NULL"))
    name = Column(String(50), nullable=False)
    shift = Column(SQLEnum(GroupShift, name="group_shift"), default=GroupShift.MORNING, nullable=False)
    
    # Relaciones
    program = relationship("Program", back_populates="groups")
    tutor_teacher = relationship("Teacher", back_populates="tutored_groups")
    student_groups = relationship("StudentGroup", back_populates="group", cascade="all, delete-orphan")
    group_courses = relationship("GroupCourse", back_populates="group", cascade="all, delete-orphan")
    group_chat = relationship("GroupChat", back_populates="group", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('program_id', 'name', name='uq_program_group_name'),
    )

# -------------------------------
# Relación Estudiante-Grupo
# -------------------------------
class StudentGroup(BaseModel):
    """Modelo de relación estudiante-grupo"""
    __tablename__ = "student_groups"
    
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(SQLEnum(StudentGroupStatus, name="student_group_status"), default=StudentGroupStatus.ACTIVE, nullable=False)
    
    # Relaciones
    group = relationship("Group", back_populates="student_groups")
    student = relationship("Student", back_populates="student_groups")

    __table_args__ = (
        UniqueConstraint('group_id', 'student_id', name='uq_student_group'),
    )

# -------------------------------
# Relación Grupo-Curso
# -------------------------------
class GroupCourse(BaseModel):
    """Modelo de relación grupo-curso"""
    __tablename__ = "group_courses"
    
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    assignment_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    group = relationship("Group", back_populates="group_courses")
    course = relationship("Course", back_populates="group_courses")
    teacher = relationship("Teacher", back_populates="group_courses")
    classes = relationship("Class", back_populates="group_course", cascade="all, delete-orphan")
    
    # Constraint único
    __table_args__ = (
        UniqueConstraint('course_id', 'group_id', name='uq_group_course'),
    )
