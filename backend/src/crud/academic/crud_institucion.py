from uuid import UUID

from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.models.academic.institucion import Institucion
from src.schemas.academic.institucion import InstitucionCreate, InstitucionUpdate


class CRUDInstitucion(CRUDBase[Institucion, InstitucionCreate, InstitucionUpdate]):
    def get(self, db: Session, institucion_id: UUID):
        return (
            db.query(Institucion)
            .filter(Institucion.institucion_id == institucion_id)
            .first()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Institucion).offset(skip).limit(limit).all()

    def get_by_dominio(self, db: Session, dominio: str) -> Institucion | None:
        """Busca una institución por su dominio de correo.
        Verifica tanto dominio_principal como dominios_adicionales.

        Args:
            db: Sesión de base de datos
            dominio: Dominio a buscar (ej: 'arp.edu.co')

        Returns:
            Institución que coincida con el dominio o None
        """
        dominio_lower = dominio.lower()

        # Buscar por dominio principal
        institucion = (
            db.query(Institucion)
            .filter(Institucion.dominio_principal == dominio_lower)
            .first()
        )

        if institucion:
            return institucion

        # Buscar en dominios adicionales
        # Nota: usa ANY para buscar en array PostgreSQL
        from sqlalchemy import func

        return (
            db.query(Institucion)
            .filter(
                func.lower(func.any_(Institucion.dominios_adicionales)) == dominio_lower
            )
            .first()
        )

    def get_by_nombre(self, db: Session, nombre: str) -> Institucion | None:
        """Busca una institución por nombre exacto."""
        return db.query(Institucion).filter(Institucion.nombre == nombre).first()

    def get_instituciones_activas(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> list[Institucion]:
        """Obtiene solo instituciones activas."""
        return (
            db.query(Institucion)
            .filter(Institucion.estado == "activa")
            .offset(skip)
            .limit(limit)
            .all()
        )

    def cambiar_estado(
        self, db: Session, institucion_id: UUID, nuevo_estado: str
    ) -> Institucion | None:
        """Cambia el estado de una institución.
        Estados válidos: 'pendiente', 'activa', 'suspendida', 'inactiva'.
        """
        institucion = self.get(db, institucion_id)
        if not institucion:
            return None

        institucion.estado = nuevo_estado

        # Si se activa, guardar fecha de activación
        if nuevo_estado == "activa" and not institucion.fecha_activacion:
            from datetime import UTC, datetime

            institucion.fecha_activacion = datetime.now(UTC)

        db.add(institucion)
        db.commit()
        db.refresh(institucion)
        return institucion

    def get_by_filtros(
        self,
        db: Session,
        tipo_institucion: str | None = None,
        nivel_educativo: str | None = None,
        modalidad_ensenanza: str | None = None,
        sector: str | None = None,
        estado: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Institucion]:
        """Busca instituciones aplicando múltiples filtros.

        Args:
            db: Sesión de base de datos
            tipo_institucion: Filtrar por tipo (universidad, colegio, etc.)
            nivel_educativo: Filtrar por nivel (basica, media, superior, etc.)
            modalidad_ensenanza: Filtrar por modalidad (presencial, virtual, hibrida)
            sector: Filtrar por sector (publico, privado)
            estado: Filtrar por estado (pendiente, activa, etc.)
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar

        Returns:
            Lista de instituciones que coincidan con los filtros
        """
        query = db.query(Institucion)

        if tipo_institucion:
            query = query.filter(Institucion.tipo_institucion == tipo_institucion)
        if nivel_educativo:
            query = query.filter(Institucion.nivel_educativo == nivel_educativo)
        if modalidad_ensenanza:
            query = query.filter(Institucion.modalidad_ensenanza == modalidad_ensenanza)
        if sector:
            query = query.filter(Institucion.sector == sector)
        if estado:
            query = query.filter(Institucion.estado == estado)

        return query.offset(skip).limit(limit).all()

    def get_estadisticas_institucion(self, db: Session, institucion_id: UUID) -> dict:
        """Obtiene estadísticas completas de una institución (actualizado con nuevos campos)."""
        from src.models.academic.curso import Curso
        from src.models.academic.programa import Programa
        from src.models.users.institucion_coordinador import InstitucionCoordinador

        institucion = self.get(db, institucion_id)
        if not institucion:
            return {}

        # Contar programas
        total_programas = (
            db.query(Programa).filter(Programa.institucion_id == institucion_id).count()
        )

        # Contar cursos
        total_cursos = (
            db.query(Curso).filter(Curso.institucion_id == institucion_id).count()
        )

        cursos_activos = (
            db.query(Curso)
            .filter(Curso.institucion_id == institucion_id, Curso.activo)
            .count()
        )

        # Contar coordinadores
        total_coordinadores = (
            db.query(InstitucionCoordinador)
            .filter(
                InstitucionCoordinador.institucion_id == institucion_id,
                InstitucionCoordinador.estado == "activo",
            )
            .count()
        )

        return {
            "institucion_id": institucion_id,
            "nombre": institucion.nombre,
            "sigla": institucion.sigla,
            "logo_url": institucion.logo_url,
            "estado": institucion.estado,
            "tipo_institucion": (
                institucion.tipo_institucion.value
                if institucion.tipo_institucion
                else None
            ),
            "nivel_educativo": (
                institucion.nivel_educativo.value
                if institucion.nivel_educativo
                else None
            ),
            "modalidad_ensenanza": (
                institucion.modalidad_ensenanza.value
                if institucion.modalidad_ensenanza
                else None
            ),
            "dominio_principal": institucion.dominio_principal,
            "dominios_adicionales": institucion.dominios_adicionales,
            "total_programas": total_programas,
            "total_cursos": total_cursos,
            "cursos_activos": cursos_activos,
            "cursos_inactivos": total_cursos - cursos_activos,
            "total_coordinadores": total_coordinadores,
            "numero_estudiantes_actual": institucion.numero_estudiantes_actual or 0,
            "numero_docentes": institucion.numero_docentes or 0,
            "capacidad_estudiantes": institucion.capacidad_estudiantes,
            "fecha_creacion": institucion.fecha_creacion,
            "fecha_activacion": institucion.fecha_activacion,
        }

    def create(self, db: Session, obj_in: InstitucionCreate):
        db_obj = Institucion(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Institucion, obj_in: InstitucionUpdate):
        """Actualiza una institución validando unicidad de campos."""
        from fastapi import HTTPException
        
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Validar unicidad de correo_institucional si se está actualizando
        if 'correo_institucional' in update_data and update_data['correo_institucional']:
            correo_existente = (
                db.query(Institucion)
                .filter(
                    Institucion.correo_institucional == update_data['correo_institucional'],
                    Institucion.institucion_id != db_obj.institucion_id
                )
                .first()
            )
            if correo_existente:
                raise HTTPException(
                    status_code=400,
                    detail=f"El correo institucional {update_data['correo_institucional']} ya está en uso por otra institución"
                )
        
        # Validar unicidad de dominio_principal si se está actualizando
        if 'dominio_principal' in update_data and update_data['dominio_principal']:
            dominio_existente = (
                db.query(Institucion)
                .filter(
                    Institucion.dominio_principal == update_data['dominio_principal'],
                    Institucion.institucion_id != db_obj.institucion_id
                )
                .first()
            )
            if dominio_existente:
                raise HTTPException(
                    status_code=400,
                    detail=f"El dominio {update_data['dominio_principal']} ya está en uso por otra institución"
                )
        
        # Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, institucion_id: UUID):
        obj = db.query(Institucion).get(institucion_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


institucion_crud = CRUDInstitucion(Institucion, id_field="institucion_id")
