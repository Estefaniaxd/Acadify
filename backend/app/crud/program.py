# backend/app/crud/program.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.crud.base import CRUDBase
from app.models.program import Program
from app.models.institution import Institution
from app.schemas.program import ProgramCreate, ProgramUpdate
import uuid

class CRUDProgram(CRUDBase[Program, ProgramCreate, ProgramUpdate]):
    """CRUD para gestión de programas académicos"""
    
    def create_with_institution(
        self, 
        db: Session, 
        *, 
        obj_in: ProgramCreate, 
        institution_id: uuid.UUID
    ) -> Program:
        """
        Crea un nuevo programa y lo asigna a una institución
        """
        # Verificar que la institución existe
        institution = db.query(Institution).filter(
            Institution.id == institution_id
        ).first()
        if not institution:
            raise ValueError("Institución no encontrada")
        
        # Verificar que la institución usa programas
        if not institution.uses_programs:
            raise ValueError("Esta institución no maneja programas académicos")
        
        # Verificar que no exista un programa con el mismo nombre en la institución
        existing_program = self.get_by_name_in_institution(
            db, name=obj_in.name, institution_id=institution_id
        )
        if existing_program:
            raise ValueError("Ya existe un programa con este nombre en la institución")
        
        # Crear el programa
        obj_data = obj_in.dict()
        obj_data["institution_id"] = institution_id
        
        db_obj = Program(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_institution(
        self, 
        db: Session, 
        *, 
        institution_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Program]:
        """Obtiene todos los programas de una institución"""
        return db.query(Program).filter(
            Program.institution_id == institution_id
        ).offset(skip).limit(limit).all()
    
    def get_by_name_in_institution(
        self, 
        db: Session, 
        *, 
        name: str, 
        institution_id: uuid.UUID
    ) -> Optional[Program]:
        """Obtiene un programa por nombre dentro de una institución específica"""
        return db.query(Program).filter(
            and_(
                Program.name == name,
                Program.institution_id == institution_id
            )
        ).first()
    
    def get_by_level(
        self, 
        db: Session, 
        *, 
        level: str, 
        institution_id: Optional[uuid.UUID] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Program]:
        """Obtiene programas por nivel educativo"""
        query_filter = Program.level == level
        
        if institution_id:
            query_filter = and_(query_filter, Program.institution_id == institution_id)
        
        return db.query(Program).filter(query_filter).offset(skip).limit(limit).all()
    
    def get_by_type(
        self, 
        db: Session, 
        *, 
        program_type: str, 
        institution_id: Optional[uuid.UUID] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Program]:
        """Obtiene programas por tipo"""
        query_filter = Program.program_type == program_type
        
        if institution_id:
            query_filter = and_(query_filter, Program.institution_id == institution_id)
        
        return db.query(Program).filter(query_filter).offset(skip).limit(limit).all()
    
    def search_programs(
        self, 
        db: Session, 
        *, 
        query: str,
        institution_id: Optional[uuid.UUID] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Program]:
        """
        Busca programas por nombre o descripción
        """
        search_filter = or_(
            Program.name.ilike(f"%{query}%"),
            Program.description.ilike(f"%{query}%")
        )
        
        if institution_id:
            search_filter = and_(search_filter, Program.institution_id == institution_id)
        
        return db.query(Program).filter(search_filter).offset(skip).limit(limit).all()
    
    def get_program_statistics(self, db: Session, *, program_id: uuid.UUID) -> dict:
        """
        Obtiene estadísticas de un programa (estudiantes, grupos, cursos)
        """
        program = self.get(db, id=program_id)
        if not program:
            raise ValueError("Programa no encontrado")
        
        # Contar estudiantes activos en el programa
        from app.models.user import Student
        students_count = db.query(Student).filter(
            Student.program_id == program_id
        ).count()
        
        # Contar grupos del programa
        from app.models.group import Group
        groups_count = db.query(Group).filter(
            Group.program_id == program_id
        ).count()
        
        # Contar cursos del programa
        from app.models.course import Course
        courses_count = db.query(Course).filter(
            Course.program_id == program_id
        ).count()
        
        return {
            "students_count": students_count,
            "groups_count": groups_count,
            "courses_count": courses_count,
            "institution_name": program.institution.name,
            "level": program.level.value,
            "program_type": program.program_type.value
        }
    
    def get_programs_with_available_spots(
        self, 
        db: Session, 
        *, 
        institution_id: uuid.UUID,
        max_students_per_program: int = 100
    ) -> List[Program]:
        """
        Obtiene programas que tienen cupos disponibles para nuevos estudiantes
        """
        from app.models.user import Student
        
        # Subconsulta para contar estudiantes por programa
        student_counts = db.query(
            Student.program_id,
            db.func.count(Student.id).label('student_count')
        ).group_by(Student.program_id).subquery()
        
        # Programas con menos estudiantes que el máximo permitido
        return db.query(Program).outerjoin(
            student_counts, Program.id == student_counts.c.program_id
        ).filter(
            and_(
                Program.institution_id == institution_id,
                or_(
                    student_counts.c.student_count < max_students_per_program,
                    student_counts.c.student_count.is_(None)
                )
            )
        ).all()
    
    def count_by_institution(self, db: Session, *, institution_id: uuid.UUID) -> int:
        """Cuenta los programas de una institución"""
        return db.query(Program).filter(
            Program.institution_id == institution_id
        ).count()
    
    def get_popular_programs(
        self, 
        db: Session, 
        *, 
        institution_id: Optional[uuid.UUID] = None,
        limit: int = 10
    ) -> List[dict]:
        """
        Obtiene los programas más populares por número de estudiantes
        """
        from app.models.user import Student
        
        query = db.query(
            Program,
            db.func.count(Student.id).label('student_count')
        ).outerjoin(Student, Program.id == Student.program_id)
        
        if institution_id:
            query = query.filter(Program.institution_id == institution_id)
        
        results = query.group_by(Program.id).order_by(
            db.func.count(Student.id).desc()
        ).limit(limit).all()
        
        return [
            {
                "program": result[0],
                "student_count": result[1]
            }
            for result in results
        ]
    
    def validate_program_constraints(
        self, 
        db: Session, 
        *, 
        program: Program
    ) -> dict:
        """
        Valida las restricciones y requisitos de un programa
        """
        errors = []
        warnings = []
        
        # Verificar que tiene al menos un grupo
        groups_count = len(program.groups)
        if groups_count == 0:
            warnings.append("El programa no tiene grupos asignados")
        
        # Verificar que tiene cursos
        courses_count = len(program.courses)
        if courses_count == 0:
            warnings.append("El programa no tiene cursos asignados")
        
        # Verificar coherencia entre nivel educativo del programa y la institución
        if program.institution.educational_level == "basic" and program.level in ["masters", "doctorate"]:
            errors.append("Una institución de educación básica no puede ofrecer programas de posgrado")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "statistics": {
                "groups_count": groups_count,
                "courses_count": courses_count,
                "students_count": len(program.students)
            }
        }

# Instancia del CRUD
program = CRUDProgram(Program)