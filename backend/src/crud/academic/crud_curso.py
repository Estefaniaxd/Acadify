import random
import string
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, selectinload

from src.crud.base import CRUDBase
from src.enums.academic.curso_enums import ModalidadCurso
from src.models.academic.curso import Curso
from src.schemas.academic.curso import CursoCreate, CursoUpdate


class CRUDCurso(CRUDBase[Curso, CursoCreate, CursoUpdate]):

    def get(self, db: Session, curso_id: UUID) -> Curso | None:
        """Obtiene un curso por ID con relaciones cargadas."""
        return (
            db.query(Curso)
            .options(
                selectinload(Curso.institucion),
                selectinload(Curso.coordinador),
                selectinload(Curso.programa),
                selectinload(Curso.curso_docentes),
                selectinload(Curso.grupo_cursos),
            )
            .filter(Curso.curso_id == curso_id)
            .first()
        )

    def get_by_codigo_acceso(self, db: Session, codigo: str) -> Curso | None:
        """Busca un curso por su código de acceso."""
        return db.query(Curso).filter(Curso.codigo_acceso == codigo).first()

    def generar_codigo_acceso_unico(self, db: Session, longitud: int = 6) -> str:
        """Genera un código de acceso único para un curso.
        Por defecto 6 caracteres alfanuméricos (mayúsculas y números).
        """
        max_intentos = 100
        caracteres = string.ascii_uppercase + string.digits

        for _ in range(max_intentos):
            codigo = "".join(random.choices(caracteres, k=longitud))

            # Verificar que no exista
            existe = db.query(Curso).filter(Curso.codigo_acceso == codigo).first()

            if not existe:
                return codigo

        # Si llegamos aquí, intentamos con longitud mayor
        return self.generar_codigo_acceso_unico(db, longitud + 1)

    def verificar_disponibilidad(
        self, db: Session, curso_id: UUID, estudiante_id: UUID | None = None
    ) -> dict:
        """Verifica si un curso está disponible para inscripción.
        Retorna un dict con disponible (bool) y razon (str).
        """
        curso = self.get(db, curso_id)
        if not curso:
            return {"disponible": False, "razon": "Curso no encontrado"}

        if not curso.activo:
            return {"disponible": False, "razon": "Curso inactivo"}

        if not curso.permite_inscripcion:
            return {"disponible": False, "razon": "Inscripciones cerradas"}

        # Verificar límite de estudiantes
        if curso.maximo_estudiantes:
            total_estudiantes = curso.total_estudiantes
            if total_estudiantes >= curso.maximo_estudiantes:
                return {"disponible": False, "razon": "Curso lleno"}

        # Verificar fecha de inicio (no se puede inscribir si ya empezó)
        from datetime import date

        if curso.fecha_inicio and curso.fecha_inicio < date.today():
            return {"disponible": False, "razon": "Curso ya iniciado"}

        # Si se proporciona estudiante_id, verificar que no esté ya inscrito
        if estudiante_id:
            from src.models.academic.estudiante_grupo import EstudianteGrupo
            from src.models.academic.grupo_curso import GrupoCurso

            # Buscar si el estudiante ya está en algún grupo del curso
            inscrito = (
                db.query(EstudianteGrupo)
                .join(GrupoCurso, EstudianteGrupo.grupo_id == GrupoCurso.grupo_id)
                .filter(
                    GrupoCurso.curso_id == curso_id,
                    EstudianteGrupo.estudiante_id == estudiante_id,
                )
                .first()
            )

            if inscrito:
                return {"disponible": False, "razon": "Ya inscrito en este curso"}

        return {"disponible": True, "razon": "Disponible para inscripción"}

    def get_multi_by_institucion(
        self,
        db: Session,
        institucion_id: UUID,
        skip: int = 0,
        limit: int = 100,
        activo_solo: bool = True,
    ) -> list[Curso]:
        """Obtiene cursos de una institución."""
        query = db.query(Curso).filter(Curso.institucion_id == institucion_id)

        if activo_solo:
            query = query.filter(Curso.activo)

        return query.offset(skip).limit(limit).all()

    def get_multi_by_coordinador(
        self, db: Session, coordinador_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Curso]:
        """Obtiene cursos de un coordinador."""
        return (
            db.query(Curso)
            .filter(Curso.coordinador_id == coordinador_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_programa(
        self, db: Session, programa_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Curso]:
        """Obtiene cursos de un programa."""
        return (
            db.query(Curso)
            .filter(Curso.programa_id == programa_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, obj_in: CursoCreate) -> Curso:
        """Crea un nuevo curso."""
        curso_data = obj_in.dict()

        # Generar código de acceso si no se proporcionó
        if not curso_data.get("codigo_acceso"):
            curso_data["codigo_acceso"] = self.generar_codigo_acceso_unico(db)

        db_obj = Curso(**curso_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Curso, obj_in: CursoUpdate) -> Curso:
        """Actualiza un curso existente."""
        update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, curso_id: UUID) -> Curso | None:
        """Elimina un curso."""
        obj = db.query(Curso).get(curso_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def activar_desactivar(self, db: Session, curso_id: UUID, activo: bool) -> bool:
        """Activa o desactiva un curso."""
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
        institucion_id: UUID | None = None,
        modalidad: ModalidadCurso | None = None,
        activo_solo: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Curso]:
        """Busca cursos por término de búsqueda."""
        query = db.query(Curso)

        # Filtro de búsqueda
        query = query.filter(
            or_(
                Curso.nombre.ilike(f"%{termino_busqueda}%"),
                Curso.descripcion.ilike(f"%{termino_busqueda}%"),
                Curso.codigo_curso.ilike(f"%{termino_busqueda}%"),
            )
        )

        # Filtros adicionales
        if institucion_id:
            query = query.filter(Curso.institucion_id == institucion_id)
        if modalidad:
            query = query.filter(Curso.modalidad == modalidad)
        if activo_solo:
            query = query.filter(Curso.activo)

        return query.offset(skip).limit(limit).all()

    def get_estadisticas_curso(self, db: Session, curso_id: UUID) -> dict:
        """Obtiene estadísticas detalladas de un curso."""
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
        total_material = (
            len(curso.material_cursos) if hasattr(curso, "material_cursos") else 0
        )

        # Contar clases
        total_clases = 0
        for grupo_curso in curso.grupo_cursos:
            if hasattr(grupo_curso.grupo, "clases"):
                total_clases += len(grupo_curso.grupo.clases)

        return {
            "curso_id": curso_id,
            "nombre": curso.nombre,
            "total_estudiantes": total_estudiantes,
            "total_docentes": total_docentes,
            "total_grupos": total_grupos,
            "total_material": total_material,
            "total_clases": total_clases,
            "activo": curso.activo,
            "permite_inscripcion": curso.permite_inscripcion,
            "codigo_acceso": curso.codigo_acceso,
            "maximo_estudiantes": curso.maximo_estudiantes,
            "espacios_disponibles": (
                (curso.maximo_estudiantes - total_estudiantes)
                if curso.maximo_estudiantes
                else None
            ),
        }

    def get_cursos_con_inscripciones_abiertas(
        self, db: Session, programa_id: UUID | None = None
    ) -> list[Curso]:
        """Obtiene cursos que permiten inscripciones."""
        query = db.query(Curso).filter(and_(Curso.activo, Curso.permite_inscripcion))

        if programa_id:
            query = query.filter(Curso.programa_id == programa_id)

        return query.all()

    def get_cursos_por_periodo(
        self,
        db: Session,
        fecha_inicio: str | None = None,
        fecha_fin: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Curso]:
        """Obtiene cursos por período de fechas."""
        from datetime import datetime

        query = db.query(Curso)

        if fecha_inicio:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            query = query.filter(Curso.fecha_inicio >= fecha_inicio_dt)

        if fecha_fin:
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            query = query.filter(Curso.fecha_fin <= fecha_fin_dt)

        return query.offset(skip).limit(limit).all()


curso_crud = CRUDCurso(Curso)
