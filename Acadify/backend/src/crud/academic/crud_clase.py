from sqlalchemy.orm import Session, selectinload
from ..base import CRUDBase
from ...models.academic.clase import Clase, HistorialAccesoClase
from ...schemas.academic.clase import ClaseCreate, ClaseUpdate, HistorialAccesoCreate
from ...enums.academic.clase_enums import EstadoClase, EstadoCodigoAcceso
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func
from typing import List, Optional
import secrets
import string


class CRUDClase(CRUDBase[Clase, ClaseCreate, ClaseUpdate]):
    
    def get(self, db: Session, clase_id: UUID) -> Optional[Clase]:
        """Obtiene una clase por ID con relaciones cargadas"""
        return db.query(Clase).options(
            selectinload(Clase.grupo),
            selectinload(Clase.docente),
            selectinload(Clase.material_clases)
        ).filter(Clase.clase_id == clase_id).first()

    def get_multi_by_grupo(
        self, 
        db: Session, 
        grupo_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        estado: Optional[EstadoClase] = None
    ) -> List[Clase]:
        """Obtiene clases de un grupo específico"""
        query = db.query(Clase).filter(Clase.grupo_id == grupo_id)
        
        if estado:
            query = query.filter(Clase.estado == estado)
            
        return query.offset(skip).limit(limit).all()

    def get_multi_by_docente(
        self, 
        db: Session, 
        docente_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None
    ) -> List[Clase]:
        """Obtiene clases de un docente específico"""
        query = db.query(Clase).filter(Clase.docente_id == docente_id)
        
        if fecha_desde:
            query = query.filter(Clase.fecha_inicio >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Clase.fecha_inicio <= fecha_hasta)
            
        return query.order_by(Clase.fecha_inicio.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: ClaseCreate) -> Clase:
        """Crea una nueva clase con código único"""
        # Generar código único
        codigo = self._generar_codigo_unico(db)
        
        db_obj = Clase(
            **obj_in.dict(),
            codigo_acceso=codigo,
            estado_codigo=EstadoCodigoAcceso.activo
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, 
        db: Session, 
        db_obj: Clase, 
        obj_in: ClaseUpdate
    ) -> Clase:
        """Actualiza una clase existente"""
        update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db_obj.fecha_actualizacion = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def regenerar_codigo_acceso(self, db: Session, clase_id: UUID) -> str:
        """Regenera el código de acceso de una clase"""
        db_obj = self.get(db, clase_id)
        if not db_obj:
            raise ValueError("Clase no encontrada")
            
        nuevo_codigo = self._generar_codigo_unico(db)
        db_obj.codigo_acceso = nuevo_codigo
        db_obj.estado_codigo = EstadoCodigoAcceso.activo
        db_obj.fecha_actualizacion = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return nuevo_codigo

    def deshabilitar_codigo(self, db: Session, clase_id: UUID) -> bool:
        """Deshabilita el código de acceso de una clase"""
        db_obj = self.get(db, clase_id)
        if not db_obj:
            return False
            
        db_obj.estado_codigo = EstadoCodigoAcceso.deshabilitado
        db_obj.fecha_actualizacion = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        return True

    def get_by_codigo_acceso(self, db: Session, codigo: str) -> Optional[Clase]:
        """Obtiene una clase por su código de acceso si está activa"""
        return db.query(Clase).filter(
            and_(
                Clase.codigo_acceso == codigo,
                Clase.estado_codigo == EstadoCodigoAcceso.activo,
                or_(
                    Clase.fecha_vencimiento_codigo.is_(None),
                    Clase.fecha_vencimiento_codigo > datetime.utcnow()
                )
            )
        ).first()

    def unirse_a_clase(
        self, 
        db: Session, 
        codigo: str, 
        estudiante_id: UUID,
        ip_acceso: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> tuple[bool, str, Optional[Clase]]:
        """Permite a un estudiante unirse a una clase usando el código"""
        
        # Buscar clase por código
        clase = self.get_by_codigo_acceso(db, codigo)
        if not clase:
            return False, "Código inválido o expirado", None
            
        # Verificar si ya está unido
        acceso_existente = db.query(HistorialAccesoClase).filter(
            and_(
                HistorialAccesoClase.clase_id == clase.clase_id,
                HistorialAccesoClase.estudiante_id == estudiante_id
            )
        ).first()
        
        if acceso_existente:
            return False, "Ya estás unido a esta clase", clase
            
        # Verificar límite de estudiantes
        if clase.max_estudiantes:
            total_unidos = db.query(HistorialAccesoClase).filter(
                HistorialAccesoClase.clase_id == clase.clase_id
            ).count()
            
            if total_unidos >= clase.max_estudiantes:
                return False, "La clase ha alcanzado el límite máximo de estudiantes", clase
        
        # Crear registro de acceso
        nuevo_acceso = HistorialAccesoClase(
            clase_id=clase.clase_id,
            estudiante_id=estudiante_id,
            codigo_usado=codigo,
            ip_acceso=ip_acceso,
            user_agent=user_agent
        )
        
        db.add(nuevo_acceso)
        db.commit()
        
        return True, "Te has unido exitosamente a la clase", clase

    def get_historial_accesos(
        self, 
        db: Session, 
        clase_id: UUID
    ) -> List[HistorialAccesoClase]:
        """Obtiene el historial de accesos de una clase"""
        return db.query(HistorialAccesoClase).options(
            selectinload(HistorialAccesoClase.estudiante)
        ).filter(
            HistorialAccesoClase.clase_id == clase_id
        ).order_by(HistorialAccesoClase.fecha_acceso.desc()).all()

    def get_estadisticas_clase(self, db: Session, clase_id: UUID) -> dict:
        """Obtiene estadísticas de una clase"""
        clase = self.get(db, clase_id)
        if not clase:
            return {}
            
        total_accesos = db.query(HistorialAccesoClase).filter(
            HistorialAccesoClase.clase_id == clase_id
        ).count()
        
        total_material = len(clase.material_clases) if clase.material_clases else 0
        
        return {
            "clase_id": clase_id,
            "total_estudiantes_unidos": total_accesos,
            "total_material_subido": total_material,
            "codigo_activo": clase.estado_codigo == EstadoCodigoAcceso.activo,
            "fecha_ultima_union": db.query(func.max(HistorialAccesoClase.fecha_acceso)).filter(
                HistorialAccesoClase.clase_id == clase_id
            ).scalar()
        }

    def _generar_codigo_unico(self, db: Session) -> str:
        """Genera un código único para una clase"""
        max_intentos = 10
        for _ in range(max_intentos):
            # Formato: 4 letras + 4 números (ej: MATH2025)
            letras = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(4))
            numeros = ''.join(secrets.choice(string.digits) for _ in range(4))
            codigo = f"{letras}{numeros}"
            
            # Verificar que no exista
            if not db.query(Clase).filter(Clase.codigo_acceso == codigo).first():
                return codigo
                
        raise ValueError("No se pudo generar un código único después de varios intentos")

    def obtener_clases_proximas(
        self, 
        db: Session, 
        docente_id: Optional[UUID] = None,
        limite_horas: int = 24
    ) -> List[Clase]:
        """Obtiene clases programadas en las próximas horas"""
        fecha_limite = datetime.utcnow() + timedelta(hours=limite_horas)
        
        query = db.query(Clase).filter(
            and_(
                Clase.fecha_inicio >= datetime.utcnow(),
                Clase.fecha_inicio <= fecha_limite,
                Clase.estado == EstadoClase.programada
            )
        )
        
        if docente_id:
            query = query.filter(Clase.docente_id == docente_id)
            
        return query.order_by(Clase.fecha_inicio).all()


clase = CRUDClase(Clase)