"""
CRUD operations para el modelo Examen
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta

from src.crud.base import CRUDBase
from src.models.evaluaciones import Examen, EstadoExamen, TipoExamen
from src.schemas.evaluaciones import ExamenCreate, ExamenUpdate, FiltrosBancoPreguntas


class CRUDExamen(CRUDBase[Examen, ExamenCreate, ExamenUpdate]):
    
    def get_examenes_por_profesor(
        self, 
        db: Session, 
        profesor_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Examen]:
        """Obtener exámenes creados por un profesor específico"""
        return db.query(Examen).filter(
            Examen.creado_por == profesor_id
        ).order_by(desc(Examen.fecha_creacion)).offset(skip).limit(limit).all()
    
    def get_examenes_por_curso(
        self, 
        db: Session, 
        curso_id: str, 
        estado: Optional[EstadoExamen] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Examen]:
        """Obtener exámenes de un curso específico"""
        query = db.query(Examen).filter(Examen.curso_id == curso_id)
        
        if estado:
            query = query.filter(Examen.estado == estado)
            
        return query.order_by(desc(Examen.fecha_creacion)).offset(skip).limit(limit).all()
    
    def get_examenes_disponibles_para_estudiante(
        self, 
        db: Session, 
        estudiante_id: str, 
        curso_ids: Optional[List[str]] = None
    ) -> List[Examen]:
        """Obtener exámenes disponibles para un estudiante"""
        now = datetime.utcnow()
        
        query = db.query(Examen).filter(
            and_(
                Examen.estado == EstadoExamen.ACTIVO,
                or_(
                    Examen.fecha_inicio.is_(None),
                    Examen.fecha_inicio <= now
                ),
                or_(
                    Examen.fecha_fin.is_(None),
                    Examen.fecha_fin >= now
                )
            )
        )
        
        if curso_ids:
            query = query.filter(Examen.curso_id.in_(curso_ids))
            
        return query.order_by(asc(Examen.fecha_inicio)).all()
    
    def get_examenes_proximos(
        self, 
        db: Session, 
        profesor_id: str, 
        dias_adelante: int = 7
    ) -> List[Examen]:
        """Obtener exámenes próximos en los próximos X días"""
        now = datetime.utcnow()
        fecha_limite = now + timedelta(days=dias_adelante)
        
        return db.query(Examen).filter(
            and_(
                Examen.creado_por == profesor_id,
                Examen.estado.in_([EstadoExamen.PUBLICADO, EstadoExamen.ACTIVO]),
                Examen.fecha_inicio >= now,
                Examen.fecha_inicio <= fecha_limite
            )
        ).order_by(asc(Examen.fecha_inicio)).all()
    
    def publicar_examen(self, db: Session, examen_id: str) -> Optional[Examen]:
        """Publicar un examen (cambiar de borrador a publicado)"""
        examen = self.get(db=db, id=examen_id)
        if not examen or examen.estado != EstadoExamen.BORRADOR:
            return None
            
        # Validar que tiene al menos una pregunta
        if examen.total_preguntas == 0:
            raise ValueError("No se puede publicar un examen sin preguntas")
            
        examen.estado = EstadoExamen.PUBLICADO
        examen.fecha_actualizacion = datetime.utcnow()
        db.commit()
        db.refresh(examen)
        return examen
    
    def activar_examen(self, db: Session, examen_id: str) -> Optional[Examen]:
        """Activar un examen (permitir que los estudiantes lo tomen)"""
        examen = self.get(db=db, id=examen_id)
        if not examen or examen.estado != EstadoExamen.PUBLICADO:
            return None
            
        examen.estado = EstadoExamen.ACTIVO
        examen.fecha_actualizacion = datetime.utcnow()
        db.commit()
        db.refresh(examen)
        return examen
    
    def finalizar_examen(self, db: Session, examen_id: str) -> Optional[Examen]:
        """Finalizar un examen (no permitir más intentos)"""
        examen = self.get(db=db, id=examen_id)
        if not examen or examen.estado != EstadoExamen.ACTIVO:
            return None
            
        examen.estado = EstadoExamen.FINALIZADO
        examen.fecha_actualizacion = datetime.utcnow()
        db.commit()
        db.refresh(examen)
        return examen
    
    def archivar_examen(self, db: Session, examen_id: str) -> Optional[Examen]:
        """Archivar un examen"""
        examen = self.get(db=db, id=examen_id)
        if not examen:
            return None
            
        examen.estado = EstadoExamen.ARCHIVADO
        examen.fecha_actualizacion = datetime.utcnow()
        db.commit()
        db.refresh(examen)
        return examen
    
    def duplicar_examen(
        self, 
        db: Session, 
        examen_id: str, 
        nuevo_titulo: str,
        profesor_id: str
    ) -> Optional[Examen]:
        """Duplicar un examen existente"""
        examen_original = self.get(db=db, id=examen_id)
        if not examen_original:
            return None
            
        # Crear nuevo examen basado en el original
        nuevo_examen_data = ExamenCreate(
            titulo=nuevo_titulo,
            descripcion=f"Copia de: {examen_original.titulo}",
            tipo_examen=examen_original.tipo_examen,
            duracion_minutos=examen_original.duracion_minutos,
            intentos_permitidos=examen_original.intentos_permitidos,
            requiere_contraseña=examen_original.requiere_contraseña,
            contraseña_acceso=examen_original.contraseña_acceso,
            randomizar_preguntas=examen_original.randomizar_preguntas,
            mostrar_resultados_inmediatos=examen_original.mostrar_resultados_inmediatos,
            permitir_revision=examen_original.permitir_revision,
            mostrar_respuestas_correctas=examen_original.mostrar_respuestas_correctas,
            modo_pantalla_completa=examen_original.modo_pantalla_completa,
            bloquear_navegacion=examen_original.bloquear_navegacion,
            detectar_cambio_pestana=examen_original.detectar_cambio_pestana,
            tiempo_maximo_inactividad=examen_original.tiempo_maximo_inactividad,
            puntuacion_total=examen_original.puntuacion_total,
            puntuacion_minima_aprobacion=examen_original.puntuacion_minima_aprobacion,
            calificacion_automatica=examen_original.calificacion_automatica,
            curso_id=examen_original.curso_id,
            grupo_id=examen_original.grupo_id,
            configuracion_avanzada=examen_original.configuracion_avanzada,
            instrucciones=examen_original.instrucciones,
            creado_por=profesor_id
        )
        
        return self.create(db=db, obj_in=nuevo_examen_data)
    
    def buscar_examenes(
        self, 
        db: Session,
        filtros: Dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[Examen]:
        """Buscar exámenes con filtros avanzados"""
        query = db.query(Examen)
        
        # Filtro por texto en título o descripción
        if "busqueda" in filtros and filtros["busqueda"]:
            texto_busqueda = f"%{filtros['busqueda']}%"
            query = query.filter(
                or_(
                    Examen.titulo.ilike(texto_busqueda),
                    Examen.descripcion.ilike(texto_busqueda)
                )
            )
        
        # Filtro por profesor
        if "profesor_id" in filtros and filtros["profesor_id"]:
            query = query.filter(Examen.creado_por == filtros["profesor_id"])
        
        # Filtro por curso
        if "curso_id" in filtros and filtros["curso_id"]:
            query = query.filter(Examen.curso_id == filtros["curso_id"])
        
        # Filtro por estado
        if "estado" in filtros and filtros["estado"]:
            if isinstance(filtros["estado"], list):
                query = query.filter(Examen.estado.in_(filtros["estado"]))
            else:
                query = query.filter(Examen.estado == filtros["estado"])
        
        # Filtro por tipo de examen
        if "tipo_examen" in filtros and filtros["tipo_examen"]:
            if isinstance(filtros["tipo_examen"], list):
                query = query.filter(Examen.tipo_examen.in_(filtros["tipo_examen"]))
            else:
                query = query.filter(Examen.tipo_examen == filtros["tipo_examen"])
        
        # Filtro por fechas
        if "fecha_desde" in filtros and filtros["fecha_desde"]:
            query = query.filter(Examen.fecha_creacion >= filtros["fecha_desde"])
        
        if "fecha_hasta" in filtros and filtros["fecha_hasta"]:
            query = query.filter(Examen.fecha_creacion <= filtros["fecha_hasta"])
        
        # Ordenamiento
        orden = filtros.get("orden", "fecha_creacion_desc")
        if orden == "fecha_creacion_desc":
            query = query.order_by(desc(Examen.fecha_creacion))
        elif orden == "fecha_creacion_asc":
            query = query.order_by(asc(Examen.fecha_creacion))
        elif orden == "titulo_asc":
            query = query.order_by(asc(Examen.titulo))
        elif orden == "titulo_desc":
            query = query.order_by(desc(Examen.titulo))
        
        return query.offset(skip).limit(limit).all()
    
    def get_estadisticas_profesor(self, db: Session, profesor_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de exámenes de un profesor"""
        total_examenes = db.query(func.count(Examen.examen_id)).filter(
            Examen.creado_por == profesor_id
        ).scalar()
        
        examenes_por_estado = db.query(
            Examen.estado, 
            func.count(Examen.examen_id)
        ).filter(
            Examen.creado_por == profesor_id
        ).group_by(Examen.estado).all()
        
        examenes_por_tipo = db.query(
            Examen.tipo_examen, 
            func.count(Examen.examen_id)
        ).filter(
            Examen.creado_por == profesor_id
        ).group_by(Examen.tipo_examen).all()
        
        # Promedio de calificaciones de todos los exámenes del profesor
        promedio_general = db.query(
            func.avg(Examen.promedio_calificacion)
        ).filter(
            and_(
                Examen.creado_por == profesor_id,
                Examen.promedio_calificacion.is_not(None)
            )
        ).scalar()
        
        return {
            "total_examenes": total_examenes,
            "examenes_por_estado": dict(examenes_por_estado),
            "examenes_por_tipo": dict(examenes_por_tipo),
            "promedio_general_calificaciones": round(promedio_general or 0, 2),
            "total_intentos": sum([e.total_intentos for e in 
                                db.query(Examen).filter(
                                    Examen.creado_por == profesor_id
                                ).all()]) or 0
        }
    
    def actualizar_estadisticas_examen(self, db: Session, examen_id: str):
        """Actualizar estadísticas calculadas del examen"""
        examen = self.get(db=db, id=examen_id)
        if not examen:
            return None
        
        # Contar preguntas
        from src.models.evaluaciones import PreguntaExamen
        total_preguntas = db.query(func.count(PreguntaExamen.pregunta_id)).filter(
            PreguntaExamen.examen_id == examen_id
        ).scalar()
        
        # Contar intentos finalizados
        from src.models.evaluaciones import IntentoExamen, EstadoIntento
        total_intentos = db.query(func.count(IntentoExamen.intento_id)).filter(
            and_(
                IntentoExamen.examen_id == examen_id,
                IntentoExamen.estado == EstadoIntento.FINALIZADO
            )
        ).scalar()
        
        # Calcular promedio de calificaciones
        promedio_calificacion = db.query(
            func.avg(IntentoExamen.porcentaje)
        ).filter(
            and_(
                IntentoExamen.examen_id == examen_id,
                IntentoExamen.estado == EstadoIntento.FINALIZADO,
                IntentoExamen.porcentaje.is_not(None)
            )
        ).scalar()
        
        # Actualizar examen
        examen.total_preguntas = total_preguntas or 0
        examen.total_intentos = total_intentos or 0
        examen.promedio_calificacion = round(promedio_calificacion or 0, 2) if promedio_calificacion else None
        examen.fecha_actualizacion = datetime.utcnow()
        
        db.commit()
        db.refresh(examen)
        return examen
    
    def verificar_acceso_estudiante(
        self, 
        db: Session, 
        examen_id: str, 
        estudiante_id: str
    ) -> Dict[str, Any]:
        """Verificar si un estudiante puede acceder a un examen"""
        examen = self.get(db=db, id=examen_id)
        if not examen:
            return {"puede_acceder": False, "mensaje": "Examen no encontrado"}
        
        now = datetime.utcnow()
        
        # Verificar estado del examen
        if examen.estado != EstadoExamen.ACTIVO:
            return {"puede_acceder": False, "mensaje": "El examen no está disponible"}
        
        # Verificar fechas
        if examen.fecha_inicio and now < examen.fecha_inicio:
            return {"puede_acceder": False, "mensaje": "El examen aún no ha comenzado"}
        
        if examen.fecha_fin and now > examen.fecha_fin:
            return {"puede_acceder": False, "mensaje": "El examen ha finalizado"}
        
        # Verificar intentos
        from src.models.evaluaciones import IntentoExamen
        intentos_realizados = db.query(func.count(IntentoExamen.intento_id)).filter(
            and_(
                IntentoExamen.examen_id == examen_id,
                IntentoExamen.estudiante_id == estudiante_id
            )
        ).scalar()
        
        if intentos_realizados >= examen.intentos_permitidos:
            return {"puede_acceder": False, "mensaje": "Has agotado tus intentos permitidos"}
        
        return {
            "puede_acceder": True,
            "intentos_restantes": examen.intentos_permitidos - (intentos_realizados or 0),
            "requiere_contraseña": examen.requiere_contraseña,
            "configuracion_antitrampa": {
                "modo_pantalla_completa": examen.modo_pantalla_completa,
                "bloquear_navegacion": examen.bloquear_navegacion,
                "detectar_cambio_pestana": examen.detectar_cambio_pestana,
                "tiempo_maximo_inactividad": examen.tiempo_maximo_inactividad
            }
        }


# Instancia del CRUD
examen = CRUDExamen(Examen)