from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import enum

# ---------- ENUMS ----------
class InstitutionType(enum.Enum):
    SCHOOL = "school"
    COLLEGE = "college"
    INSTITUTE = "institute"
    UNIVERSITY = "university"
    POLYTECHNIC = "polytechnic"
    TRAINING_CENTER = "training_center"
    CORPORATION = "corporation"
    FOUNDATION = "foundation"
    ACADEMY = "academy"

class EducationalLevel(enum.Enum):
    BASIC = "basic"
    MIDDLE = "middle"
    TECHNICAL = "technical"
    TECHNOLOGICAL = "technological"
    HIGHER = "higher"

class InstitutionSector(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"

# ---------- MODELO ----------
class Institution(BaseModel):
    """Modelo de institución educativa"""
    __tablename__ = "institutions"
    
    administrator_id = Column(UUID(as_uuid=True), ForeignKey("system_administrators.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    acronym = Column(String(10), unique=True, index=True)
    motto = Column(String(255), nullable=True)
    institution_type = Column(SQLEnum(InstitutionType), nullable=False)
    uses_programs = Column(Boolean, nullable=False, default=True)
    educational_level = Column(SQLEnum(EducationalLevel), nullable=False)
    sector = Column(SQLEnum(InstitutionSector), nullable=False)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    institutional_email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20), nullable=False, unique=True)
    tax_id = Column(String(20), unique=True, nullable=True)  # NIT

    # ---------- RELACIONES ----------
    administrator = relationship("SystemAdministrator", back_populates="managed_institutions")
    programs = relationship("Program", back_populates="institution")
    coordinators = relationship("Coordinator", back_populates="institution")
    courses = relationship("Course", back_populates="institution")
    grading_scales = relationship("GradingScale", back_populates="institution")
