from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from app.crud.base import CRUDBase
from app.models.course import Course
from app.models.user import Coordinator
from app.models.program import Program
from app.models.group import GroupCourse, StudentGroup
from app.models.materials import CourseMaterial
from app.schemas.course import CourseCreate, CourseUpdate
import uuid

class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    """CRUD para gestión de cursos"""

    # ----------------------
    # CREACIÓN Y ASIGNACIÓN
    # ----------------------
    def create_with_coordinator(
        self, db: Session, *, obj_in: CourseCreate, coordinator_id: uuid.UUID
    ) -> Course:
        """Crea un curso y lo asigna a un coordinador"""
        coordinator = db.query(Coordinator).filter(Coordinator.id == coordinator_id).first()
        if not coordinator:
            raise ValueError("Coordinador no encontrado")

        program = db.query(Program).filter(Program.id == obj_in.program_id).first()
        if not program:
            raise ValueError("Programa no encontrado")

        if program.institution_id != coordinator.institution_id:
            raise ValueError("El programa debe pertenecer a la misma institución del coordinador")

        obj_data = obj_in.dict()
        obj_data["coordinator_id"] = coordinator_id
        obj_data["institution_id"] = coordinator.institution_id

        db_obj = Course(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def assign_to_coordinator(self, db: Session, *, course_id: uuid.UUID, coordinator_id: uuid.UUID) -> Course:
        """Asigna un curso a un coordinador diferente"""
        course = self.get(db, id=course_id)
        if not course:
            raise ValueError("Curso no encontrado")

        coordinator = db.query(Coordinator).filter(Coordinator.id == coordinator_id).first()
        if not coordinator:
            raise ValueError("Coordinador no encontrado")

        if coordinator.institution_id != course.institution_id:
            raise ValueError("El coordinador debe pertenecer a la misma institución del curso")

        course.coordinator_id = coordinator_id
        db.commit()
        db.refresh(course)
        return course

    # ----------------------
    # OBTENER CURSOS
    # ----------------------
    def get_by_institution(self, db: Session, *, institution_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Course]:
        """Obtiene todos los cursos de una institución"""
        return db.query(Course).filter(Course.institution_id == institution_id).offset(skip).limit(limit).all()

    def get_by_coordinator(self, db: Session, *, coordinator_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Course]:
        """Obtiene todos los cursos de un coordinador"""
        return db.query(Course).filter(Course.coordinator_id == coordinator_id).offset(skip).limit(limit).all()

    def get_by_program(self, db: Session, *, program_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Course]:
        """Obtiene todos los cursos de un programa"""
        return db.query(Course).filter(Course.program_id == program_id).offset(skip).limit(limit).all()

    def get_by_name_in_institution(self, db: Session, *, name: str, institution_id: uuid.UUID) -> Optional[Course]:
        """Obtiene un curso por nombre dentro de una institución específica"""
        return db.query(Course).filter(and_(Course.name == name, Course.institution_id == institution_id)).first()

    def search_courses(self, db: Session, *, query: str, institution_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 100) -> List[Course]:
        """Busca cursos por nombre o descripción, opcionalmente filtrados por institución"""
        search_filter = or_(Course.name.ilike(f"%{query}%"), Course.description.ilike(f"%{query}%"))
        if institution_id:
            search_filter = and_(search_filter, Course.institution_id == institution_id)
        return db.query(Course).filter(search_filter).offset(skip).limit(limit).all()

    def get_active_courses(self, db: Session, *, institution_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 100) -> List[Course]:
        """Obtiene cursos activos (en progreso o próximos a iniciar)"""
        current_date = datetime.utcnow()
        query_filter = or_(Course.end_date >= current_date, Course.end_date.is_(None))
        if institution_id:
            query_filter = and_(query_filter, Course.institution_id == institution_id)
        return db.query(Course).filter(query_filter).offset(skip).limit(limit).all()

    def get_courses_by_modality(self, db: Session, *, modality: str, institution_id: Optional[uuid.UUID] = None, skip: int = 0, limit: int = 100) -> List[Course]:
        """Obtiene cursos por modalidad"""
        query_filter = Course.modality == modality
        if institution_id:
            query_filter = and_(query_filter, Course.institution_id == institution_id)
        return db.query(Course).filter(query_filter).offset(skip).limit(limit).all()

    # ----------------------
    # ESTADÍSTICAS Y UTILIDADES
    # ----------------------
    def get_course_statistics(self, db: Session, *, course_id: uuid.UUID) -> dict:
        """Obtiene estadísticas de un curso"""
        course = self.get(db, id=course_id)
        if not course:
            raise ValueError("Curso no encontrado")

        groups_count = db.query(GroupCourse).filter(GroupCourse.course_id == course_id).count()
        students_count = db.query(StudentGroup).join(GroupCourse).filter(GroupCourse.course_id == course_id).distinct(StudentGroup.student_id).count()
        materials_count = db.query(CourseMaterial).filter(CourseMaterial.course_id == course_id).count()

        return {
            "groups_count": groups_count,
            "students_count": students_count,
            "materials_count": materials_count,
            "coordinator_name": f"{course.coordinator.user.first_names} {course.coordinator.user.last_names}" if course.coordinator else None,
            "institution_name": course.institution.name,
            "program_name": course.program.name
        }

    def validate_course_dates(self, start_date, end_date) -> bool:
        """Valida coherencia de fechas del curso"""
        if start_date and end_date:
            return start_date < end_date
        return True

    def count_by_institution(self, db: Session, *, institution_id: uuid.UUID) -> int:
        """Cuenta los cursos de una institución"""
        return db.query(Course).filter(Course.institution_id == institution_id).count()

# Instancia del CRUD
course = CRUDCourse(Course)
