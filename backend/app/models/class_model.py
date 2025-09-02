from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel


class Class(BaseModel):
    """Modelo para las clases/sesiones educativas"""
    __tablename__ = "classes"
    
    # Información básica de la clase
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Relaciones principales
    group_course_id = Column(UUID(as_uuid=True), ForeignKey("group_courses.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Si necesitas plataforma, asegúrate de que exista la tabla platforms
    # platform_id = Column(UUID(as_uuid=True), ForeignKey("platforms.id"))  # Descomentar cuando exista
    
    # Horarios
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    # Estado de la clase
    is_active = Column(Boolean, default=True)
    is_virtual = Column(Boolean, default=False)
    
    # Información adicional
    location = Column(String(255))  # Aula física o URL de reunión virtual
    max_participants = Column(Integer)
    
    def __repr__(self):
        return f"<Class(id={self.id}, title={self.title})>"


class Attendance(BaseModel):
    """Modelo para el registro de asistencia"""
    __tablename__ = "attendance"
    
    # Relaciones
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    
    # Estado de asistencia
    present = Column(Boolean, default=False)
    attendance_time = Column(DateTime)
    
    # Información adicional
    late_minutes = Column(Integer, default=0)
    early_departure = Column(Boolean, default=False)
    notes = Column(Text)
    
    def __repr__(self):
        return f"<Attendance(student_id={self.student_id}, class_id={self.class_id}, present={self.present})>"
