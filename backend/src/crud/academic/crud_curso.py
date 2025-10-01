from sqlalchemy.orm import Session, selectinload
from ..base import CRUDBase
from ...models.academic.curso import Curso
from ...schemas.academic.curso import CursoCreate, CursoUpdate
from ...enums.academic.curso_enums import ModalidadCurso
from uuid import UUID
from typing import List, Optional
from sqlalchemy import and_, or_, func


class CRUDCurso(CRUDBase[Curso, CursoCreate, CursoUpdate]):
    
    def get(self, db: Session, curso_id: UUID) -> Optional[Curso]:
        """Obtiene un curso por ID con relaciones cargadas"""
        return db.query(Curso).options(
            selectinload(Curso.institucion),
            selectinload(Curso.coordinador),
            selectinload(Curso.programa),
            selectinload(Curso.curso_docentes),
            selectinload(Curso.grupo_cursos)
        ).filter(Curso.curso_id == curso_id).first()

    def get_multi_by_institucion(
        self, 
        db: Session, 
        institucion_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        activo_solo: bool = True
    ) -> List[Curso]:
        """Obtiene cursos de una institución"""
        query = db.query(Curso).filter(Curso.institucion_id == institucion_id)
        
        if activo_solo:
            query = query.filter(Curso.activo == True)
            
        return query.offset(skip).limit(limit).all()

    def get_multi_by_coordinador(
        self, 
        db: Session, 
        coordinador_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Curso]:
        """Obtiene cursos de un coordinador"""
        return db.query(Curso).filter(
            Curso.coordinador_id == coordinador_id
        ).offset(skip).limit(limit).all()

    def get_multi_by_programa(
        self, 
        db: Session, 
        programa_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Curso]:
        """Obtiene cursos de un programa"""
        return db.query(Curso).filter(
            Curso.programa_id == programa_id
        ).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CursoCreate) -> Curso:
        """Crea un nuevo curso"""
        db_obj = Curso(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, 
        db: Session, 
        db_obj: Curso, 
        obj_in: CursoUpdate
    ) -> Curso:
        """Actualiza un curso existente"""
        update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, curso_id: UUID) -> Optional[Curso]:
        """Elimina un curso"""
        obj = db.query(Curso).get(curso_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def activar_desactivar(self, db: Session, curso_id: UUID, activo: bool) -> bool:
        """Activa o desactiva un curso"""
        db_obj = self.get(db, curso_id)
        if not db_obj:
            return False
            
        db_obj.activo = activo
        db.add(db_obj)
        db.commit()
        return True

    def buscar_cursos(
        self, 
        db: Session, 
        termino_busqueda: str,
        institucion_id: Optional[UUID] = None,
        modalidad: Optional[ModalidadCurso] = None,
        activo_solo: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[Curso]:
        """Busca cursos por término de búsqueda"""
        query = db.query(Curso)
        
        # Filtro de búsqueda
        query = query.filter(
            or_(
                Curso.nombre.ilike(f"%{termino_busqueda}%"),
                Curso.descripcion.ilike(f"%{termino_busqueda}%"),
                Curso.codigo_curso.ilike(f"%{termino_busqueda}%")
            )
        )
        
        # Filtros adicionales
        if institucion_id:
            query = query.filter(Curso.institucion_id == institucion_id)
        if modalidad:
            query = query.filter(Curso.modalidad == modalidad)
        if activo_solo:
            query = query.filter(Curso.activo == True)
            
        return query.offset(skip).limit(limit).all()

    def get_estadisticas_curso(self, db: Session, curso_id: UUID) -> dict:
        """Obtiene estadísticas detalladas de un curso"""
        curso = self.get(db, curso_id)
        if not curso:
            return {}
            
        # Calcular estadísticas
        total_estudiantes = 0
        for grupo_curso in curso.grupo_cursos:
            total_estudiantes += len(grupo_curso.grupo.estudiante_grupos)
            
        total_docentes = len(curso.curso_docentes)
        total_grupos = len(curso.grupo_cursos)
        
        # Contar material
        total_material = len(curso.material_cursos) if hasattr(curso, 'material_cursos') else 0
        
        # Contar clases
        total_clases = 0
        for grupo_curso in curso.grupo_cursos:
            if hasattr(grupo_curso.grupo, 'clases'):
                total_clases += len(grupo_curso.grupo.clases)
        
        return {
            "curso_id": curso_id,
            "nombre": curso.nombre,
            "total_estudiantes": total_estudiantes,
            "total_docentes": total_docentes,
            "total_grupos": total_grupos,
            "total_material": total_material,
            "total_clases": total_clases,
            "fecha_creacion": curso.fecha_creacion,
            "activo": curso.activo,
            "permite_inscripcion": curso.permite_inscripcion
        }

    def get_cursos_con_inscripciones_abiertas(
        self, 
        db: Session, 
        programa_id: Optional[UUID] = None
    ) -> List[Curso]:
        """Obtiene cursos que permiten inscripciones"""
        query = db.query(Curso).filter(
            and_(
                Curso.activo == True,
                Curso.permite_inscripcion == True
            )
        )
        
        if programa_id:
            query = query.filter(Curso.programa_id == programa_id)
            
        return query.all()


curso = CRUDCurso(Curso)
