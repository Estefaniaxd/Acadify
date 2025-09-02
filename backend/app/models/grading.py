from sqlalchemy import Column, String, ForeignKey, Numeric, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import enum

class GradingType(enum.Enum):
    """Tipos de escalafón de calificación"""
    NUMERIC = "numeric"
    LETTERS = "letters"
    QUALITATIVE = "qualitative"

class GradingScale(BaseModel):
    """Modelo de escala de calificación"""
    __tablename__ = "grading_scales"
    
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    grading_type = Column(SQLEnum(GradingType), nullable=False)
    min_value = Column(Numeric(5,2))
    max_value = Column(Numeric(5,2))
    
    # Relaciones
    institution = relationship("Institution", back_populates="grading_scales")
    grade_values = relationship("GradeValue", back_populates="grading_scale")

class GradeValue(BaseModel):
    """Modelo de valor de calificación"""
    __tablename__ = "grade_values"
    
    grading_scale_id = Column(UUID(as_uuid=True), ForeignKey("grading_scales.id", ondelete="CASCADE"), nullable=False)
    value = Column(String(10), nullable=False)
    description = Column(String(100))
    order = Column(Integer)
    
    # Relaciones
    grading_scale = relationship("GradingScale", back_populates="grade_values")
    assignment_submissions = relationship("AssignmentSubmission", back_populates="grade_value")