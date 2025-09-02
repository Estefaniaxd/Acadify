from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import enum

class CourseModality(enum.Enum):
    """Modalidades de curso"""
    ANNUAL = "annual"
    SEMESTER = "semester"
    TRIMESTER = "trimester"
    QUARTER = "quarter"
    BIMONTHLY = "bimonthly"
    MONTHLY = "monthly"
    MODULAR = "modular"
    FLEXIBLE = "flexible"
    OTHER = "other"

class Course(BaseModel):
    """Modelo de curso"""
    __tablename__ = "courses"
    
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    coordinator_id = Column(UUID(as_uuid=True), ForeignKey("coordinators.id", ondelete="SET NULL"))
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    modality = Column(SQLEnum(CourseModality), nullable=False)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    # Relaciones
    institution = relationship("Institution", back_populates="courses")
    coordinator = relationship("Coordinator", back_populates="courses")
    program = relationship("Program", back_populates="courses")
    group_courses = relationship("GroupCourse", back_populates="course")
    course_materials = relationship("CourseMaterial", back_populates="course")
    
    # Constraint único por institución
    __table_args__ = (UniqueConstraint('institution_id', 'name', name='uq_course_name_per_institution'),)
