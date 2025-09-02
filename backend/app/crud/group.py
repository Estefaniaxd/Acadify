from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.sql import func
from uuid import UUID

from app.crud.base import CRUDBase
from app.models.group import Group, StudentGroup, GroupCourse, StudentGroupStatus
from app.models.user import Student, Teacher
from app.models.program import Program
from app.schemas.group import GroupCreate, GroupUpdate

class CRUDGroup(CRUDBase[Group, GroupCreate, GroupUpdate]):
    """CRUD para gestión de grupos académicos"""
    
    # -------------------------------
    # Creación de grupo
    # -------------------------------
    def create_with_program(
        self, 
        db: Session, 
        *, 
        obj_in: GroupCreate, 
        program_id: UUID
    ) -> Group:
        """Crea un nuevo grupo y lo asigna a un programa"""
        program = db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise ValueError("Programa no encontrado")
        
        if self.get_by_name_in_program(db, name=obj_in.name, program_id=program_id):
            raise ValueError("Ya existe un grupo con este nombre en el programa")
        
        db_obj = Group(**obj_in.dict(), program_id=program_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    # -------------------------------
    # Consultas
    # -------------------------------
    def get_by_program(self, db: Session, *, program_id: UUID, skip: int = 0, limit: int = 100) -> List[Group]:
        return db.query(Group).filter(Group.program_id == program_id).offset(skip).limit(limit).all()
    
    def get_by_name_in_program(self, db: Session, *, name: str, program_id: UUID) -> Optional[Group]:
        return db.query(Group).filter(and_(Group.name == name, Group.program_id == program_id)).first()
    
    def get_by_tutor(self, db: Session, *, teacher_id: UUID, skip: int = 0, limit: int = 100) -> List[Group]:
        return db.query(Group).filter(Group.tutor_teacher_id == teacher_id).offset(skip).limit(limit).all()
    
    # -------------------------------
    # Gestión de tutor
    # -------------------------------
    def assign_tutor_teacher(self, db: Session, *, group_id: UUID, teacher_id: UUID) -> Group:
        group = self.get(db, id=group_id)
        if not group:
            raise ValueError("Grupo no encontrado")
        
        teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            raise ValueError("Docente no encontrado")
        
        group.tutor_teacher_id = teacher_id
        db.commit()
        db.refresh(group)
        return group
    
    def remove_tutor_teacher(self, db: Session, *, group_id: UUID) -> Group:
        group = self.get(db, id=group_id)
        if not group:
            raise ValueError("Grupo no encontrado")
        
        group.tutor_teacher_id = None
        db.commit()
        db.refresh(group)
        return group
    
    # -------------------------------
    # Gestión de estudiantes
    # -------------------------------
    def add_student_to_group(self, db: Session, *, group_id: UUID, student_id: UUID) -> StudentGroup:
        group = self.get(db, id=group_id)
        if not group:
            raise ValueError("Grupo no encontrado")
        
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError("Estudiante no encontrado")
        
        if student.program_id != group.program_id:
            raise ValueError("El estudiante debe pertenecer al mismo programa del grupo")
        
        existing = db.query(StudentGroup).filter(
            and_(StudentGroup.group_id == group_id, StudentGroup.student_id == student_id, StudentGroup.status == StudentGroupStatus.ACTIVE)
        ).first()
        if existing:
            raise ValueError("El estudiante ya está en este grupo")
        
        student_group = StudentGroup(
            group_id=group_id,
            student_id=student_id,
            enrollment_date=func.now(),
            status=StudentGroupStatus.ACTIVE
        )
        db.add(student_group)
        db.commit()
        db.refresh(student_group)
        return student_group
    
    def remove_student_from_group(self, db: Session, *, group_id: UUID, student_id: UUID) -> bool:
        student_group = db.query(StudentGroup).filter(
            and_(StudentGroup.group_id == group_id, StudentGroup.student_id == student_id, StudentGroup.status == StudentGroupStatus.ACTIVE)
        ).first()
        
        if not student_group:
            raise ValueError("El estudiante no está en este grupo o ya fue removido")
        
        student_group.status = StudentGroupStatus.WITHDRAWN
        db.commit()
        return True
    
    def get_group_students(self, db: Session, *, group_id: UUID, active_only: bool = True) -> List[StudentGroup]:
        query = db.query(StudentGroup).filter(StudentGroup.group_id == group_id)
        if active_only:
            query = query.filter(StudentGroup.status == StudentGroupStatus.ACTIVE)
        return query.all()
    
    def get_student_groups(self, db: Session, *, student_id: UUID, active_only: bool = True) -> List[StudentGroup]:
        query = db.query(StudentGroup).filter(StudentGroup.student_id == student_id)
        if active_only:
            query = query.filter(StudentGroup.status == StudentGroupStatus.ACTIVE)
        return query.all()
    
    # -------------------------------
    # Búsqueda de grupos
    # -------------------------------
    def search_groups(self, db: Session, *, query: str, program_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[Group]:
        filter_expr = Group.name.ilike(f"%{query}%")
        if program_id:
            filter_expr = and_(filter_expr, Group.program_id == program_id)
        return db.query(Group).filter(filter_expr).offset(skip).limit(limit).all()
    
    # -------------------------------
    # Estadísticas
    # -------------------------------
    def get_group_statistics(self, db: Session, *, group_id: UUID) -> dict:
        group = self.get(db, id=group_id)
        if not group:
            raise ValueError("Grupo no encontrado")
        
        active_students = db.query(StudentGroup).filter(and_(StudentGroup.group_id == group_id, StudentGroup.status == StudentGroupStatus.ACTIVE)).count()
        assigned_courses = db.query(GroupCourse).filter(GroupCourse.group_id == group_id).count()
        tutor_name = f"{group.tutor_teacher.user.first_names} {group.tutor_teacher.user.last_names}" if group.tutor_teacher else None
        
        return {
            "active_students_count": active_students,
            "assigned_courses_count": assigned_courses,
            "tutor_teacher_name": tutor_name,
            "program_name": group.program.name,
            "institution_name": group.program.institution.name
        }
    
    # -------------------------------
    # Gestión de cursos
    # -------------------------------
    def assign_course_to_group(self, db: Session, *, group_id: UUID, course_id: UUID, teacher_id: UUID) -> GroupCourse:
        group = self.get(db, id=group_id)
        if not group:
            raise ValueError("Grupo no encontrado")
        
        from app.crud.course import course as crud_course
        course = crud_course.get(db, id=course_id)
        if not course:
            raise ValueError("Curso no encontrado")
        
        if course.institution_id != group.program.institution_id:
            raise ValueError("El curso debe pertenecer a la misma institución del grupo")
        
        teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            raise ValueError("Docente no encontrado")
        
        existing = db.query(GroupCourse).filter(and_(GroupCourse.group_id == group_id, GroupCourse.course_id == course_id)).first()
        if existing:
            raise ValueError("El curso ya está asignado a este grupo")
        
        group_course = GroupCourse(group_id=group_id, course_id=course_id, teacher_id=teacher_id, assignment_date=func.now())
        db.add(group_course)
        db.commit()
        db.refresh(group_course)
        return group_course
    
    def remove_course_from_group(self, db: Session, *, group_id: UUID, course_id: UUID) -> bool:
        group_course = db.query(GroupCourse).filter(and_(GroupCourse.group_id == group_id, GroupCourse.course_id == course_id)).first()
        if not group_course:
            raise ValueError("El curso no está asignado a este grupo")
        db.delete(group_course)
        db.commit()
        return True

# Instancia del CRUD
group = CRUDGroup(Group)
