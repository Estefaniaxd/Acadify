from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.crud.base import CRUDBase
from app.models.institution import Institution
from app.models.user import SystemAdministrator, Coordinator
from app.schemas.institution import InstitutionCreate, InstitutionUpdate
from app.models.institution import InstitutionType
import uuid

class CRUDInstitution(CRUDBase[Institution, InstitutionCreate, InstitutionUpdate]):
    """CRUD para gestión de instituciones educativas"""
    
    def create_with_admin(
        self, db: Session, *, obj_in: InstitutionCreate, admin_id: uuid.UUID
    ) -> Institution:
        admin = db.query(SystemAdministrator).filter(SystemAdministrator.id == admin_id).first()
        if not admin:
            raise ValueError("Administrador no encontrado")
        
        obj_data = obj_in.dict()
        obj_data["administrator_id"] = admin_id
        db_obj = Institution(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Institution]:
        return db.query(Institution).filter(Institution.name == name).first()
    
    def get_by_acronym(self, db: Session, *, acronym: str) -> Optional[Institution]:
        return db.query(Institution).filter(Institution.acronym == acronym).first()
    
    def get_by_admin(self, db: Session, *, admin_id: uuid.UUID) -> List[Institution]:
        return db.query(Institution).filter(Institution.administrator_id == admin_id).all()
    
    def get_by_country(self, db: Session, *, country: str, skip: int = 0, limit: int = 100) -> List[Institution]:
        return db.query(Institution).filter(Institution.country.ilike(f"%{country}%")).offset(skip).limit(limit).all()
    
    def get_by_city(self, db: Session, *, city: str, skip: int = 0, limit: int = 100) -> List[Institution]:
        return db.query(Institution).filter(Institution.city.ilike(f"%{city}%")).offset(skip).limit(limit).all()
    
    def get_by_type(self, db: Session, *, institution_type: InstitutionType, skip: int = 0, limit: int = 100) -> List[Institution]:
        return db.query(Institution).filter(Institution.institution_type == institution_type).offset(skip).limit(limit).all()
    
    def search_institutions(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Institution]:
        search_filter = or_(
            Institution.name.ilike(f"%{query}%"),
            Institution.acronym.ilike(f"%{query}%"),
            Institution.city.ilike(f"%{query}%")
        )
        return db.query(Institution).filter(search_filter).offset(skip).limit(limit).all()
    
    def add_coordinator(self, db: Session, *, institution_id: uuid.UUID, coordinator_id: uuid.UUID) -> bool:
        institution = self.get(db, id=institution_id)
        if not institution:
            raise ValueError("Institución no encontrada")
        
        coordinator = db.query(Coordinator).filter(Coordinator.id == coordinator_id).first()
        if not coordinator:
            raise ValueError("Coordinador no encontrado")
        
        coordinator.institution_id = institution_id
        db.commit()
        return True
    
    def remove_coordinator(self, db: Session, *, institution_id: uuid.UUID, coordinator_id: uuid.UUID) -> bool:
        coordinator = db.query(Coordinator).filter(
            and_(Coordinator.id == coordinator_id, Coordinator.institution_id == institution_id)
        ).first()
        if not coordinator:
            raise ValueError("Coordinador no encontrado en esta institución")
        
        coordinator.institution_id = None
        db.commit()
        return True
    
    def get_coordinators(self, db: Session, *, institution_id: uuid.UUID) -> List[Coordinator]:
        return db.query(Coordinator).filter(Coordinator.institution_id == institution_id).all()
    
    def get_students_count(self, db: Session, *, institution_id: uuid.UUID) -> int:
        from app.models.user import Student
        from app.models.program import Program
        
        return db.query(Student).join(Program).filter(Program.institution_id == institution_id).count()
    
    def get_teachers_count(self, db: Session, *, institution_id: uuid.UUID) -> int:
        from app.models.group import GroupCourse
        from app.models.course import Course
        from app.models.user import Teacher
        
        return db.query(Teacher).join(GroupCourse).join(Course).filter(Course.institution_id == institution_id).distinct().count()
    
    def transfer_ownership(
        self, db: Session, *, institution_id: uuid.UUID, new_admin_id: uuid.UUID, current_admin_id: uuid.UUID
    ) -> Institution:
        institution = db.query(Institution).filter(
            and_(Institution.id == institution_id, Institution.administrator_id == current_admin_id)
        ).first()
        if not institution:
            raise ValueError("Institución no encontrada o no autorizado")
        
        new_admin = db.query(SystemAdministrator).filter(SystemAdministrator.id == new_admin_id).first()
        if not new_admin:
            raise ValueError("Nuevo administrador no encontrado")
        
        institution.administrator_id = new_admin_id
        db.commit()
        db.refresh(institution)
        return institution

# Instancia global
institution = CRUDInstitution(Institution)
