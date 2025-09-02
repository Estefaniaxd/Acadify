from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import enum

class MaterialType(enum.Enum):
    """Tipos de material educativo"""
    PDF = "pdf"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    PRESENTATION = "presentation"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    LINK = "link"
    INTERACTIVE = "interactive"
    SOURCE_CODE = "source_code"
    OTHER = "other"

class EducationalMaterial(BaseModel):
    """Modelo de material educativo"""
    __tablename__ = "educational_materials"
    
    title = Column(String(100), nullable=False)
    description = Column(Text)
    material_type = Column(SQLEnum(MaterialType), nullable=False)
    file_url = Column(String(255), nullable=False)
    file_format = Column(String(10), nullable=False)
    
    # Relaciones
    class_materials = relationship("ClassMaterial", back_populates="material")
    course_materials = relationship("CourseMaterial", back_populates="material")
    bot_messages = relationship("BotMessage", back_populates="referenced_material")

class ClassMaterial(BaseModel):
    """Modelo de material de clase"""
    __tablename__ = "class_materials"
    
    material_id = Column(UUID(as_uuid=True), ForeignKey("educational_materials.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id", ondelete="SET NULL"))
    
    # Relaciones
    material = relationship("EducationalMaterial", back_populates="class_materials")
    class_session = relationship("Class", back_populates="class_materials")

class CourseMaterial(BaseModel):
    """Modelo de material de curso"""
    __tablename__ = "course_materials"
    
    material_id = Column(UUID(as_uuid=True), ForeignKey("educational_materials.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="SET NULL"))
    
    # Relaciones
    material = relationship("EducationalMaterial", back_populates="course_materials")
    course = relationship("Course", back_populates="course_materials")