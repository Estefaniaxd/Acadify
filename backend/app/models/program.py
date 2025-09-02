from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import enum

class ProgramLevel(enum.Enum):
    """Niveles de programa académico"""
    BASIC = "basic"
    MIDDLE = "middle"
    TECHNICAL = "technical"
    TECHNOLOGICAL = "technological"
    PROFESSIONAL = "professional"
    SPECIALIZATION = "specialization"
    MASTERS = "masters"
    DOCTORATE = "doctorate"
    OTHER = "other"

class ProgramType(enum.Enum):
    """Tipos de programa académico"""
    IN_PERSON = "in_person"
    VIRTUAL = "virtual"
    MIXED = "mixed"
    DISTANCE = "distance"
    DUAL = "dual"
    BY_CYCLES = "by_cycles"
    CONTINUOUS = "continuous"
    OTHER = "other"

class Program(BaseModel):
    """Modelo de programa académico"""
    __tablename__ = "programs"
    
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    level = Column(SQLEnum(ProgramLevel), nullable=False)
    program_type = Column(SQLEnum(ProgramType), nullable=False)
    
    # Relaciones
    institution = relationship("Institution", back_populates="programs")
    students = relationship("Student", back_populates="program")
    groups = relationship("Group", back_populates="program")
    courses = relationship("Course", back_populates="program")
    
    # Constraint único por institución
    __table_args__ = (UniqueConstraint('institution_id', 'name', name='uq_program_name_per_institution'),)