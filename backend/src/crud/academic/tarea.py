from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func, case
from datetime import datetime, timedelta

from ...models.academic.tarea import Tarea, EntregaTarea, Rubrica
from ...models.users.usuario import Usuario
from ...models.academic.grupo import Grupo
from ...schemas.academic.tarea_schemas import (
    TareaCreate, TareaUpdate, FiltrosTarea,
    EntregaTareaCreate, EntregaTareaUpdate, CalificarEntrega, FiltrosEntrega,
    RubricaCreate, RubricaUpdate
)
from ...enums.academic.tareas import EstadoTarea, EstadoEntrega
from ..base import CRUDBase

class CRUDTarea(CRUDBase[Tarea, TareaCreate, TareaUpdate]):
    
    def crear_tarea(
        self, 
        db: Session, 
        *, 
        tarea_data: TareaCreate,
        creado_por: str
    ) -> Tarea:
        """Crear una nueva tarea"""
        tarea_dict = tarea_data.dict()
        tarea_dict["creado_por"] = creado_por
        
        tarea = Tarea(**tarea_dict)
        db.add(tarea)
        db.commit()
        db.refresh(tarea)
        return tarea
    
    def obtener_tareas_por_grupo(
        self,
        db: Session,
        *,
        grupo_id: str,
        filtros: Optional[FiltrosTarea] = None,
        usuario_id: Optional[str] = None
    ) -> List[Tarea]:
        """Obtener todas las tareas de un grupo con filtros opcionales"""
        query = db.query(Tarea).filter(Tarea.grupo_id == grupo_id)
        
        if filtros:
            if filtros.solo_activas:
                query = query.filter(Tarea.activa == True)
            
            if filtros.estado:
                query = query.filter(Tarea.estado == filtros.estado)
            
            if filtros.tipo_tarea:
                query = query.filter(Tarea.tipo_tarea == filtros.tipo_tarea)
            
            if filtros.prioridad:
                query = query.filter(Tarea.prioridad == filtros.prioridad)
            
            if filtros.es_grupal is not None:
                query = query.filter(Tarea.es_grupal == filtros.es_grupal)
            
            if filtros.docente_id:
                query = query.filter(Tarea.docente_id == filtros.docente_id)
            
            if filtros.fecha_desde:
                query = query.filter(Tarea.fecha_limite >= filtros.fecha_desde)
            
            if filtros.fecha_hasta:
                query = query.filter(Tarea.fecha_limite <= filtros.fecha_hasta)
            
            if filtros.busqueda:
                search_term = f"%{filtros.busqueda}%"
                query = query.filter(
                    or_(
                        Tarea.titulo.ilike(search_term),
                        Tarea.descripcion.ilike(search_term),
                        Tarea.categoria.ilike(search_term),
                        Tarea.tags.ilike(search_term)
                    )
                )
            
            # Ordenamiento
            if filtros.ordenar_por == "fecha_limite":
                order_field = Tarea.fecha_limite
            elif filtros.ordenar_por == "fecha_creacion":
                order_field = Tarea.fecha_creacion
            elif filtros.ordenar_por == "titulo":
                order_field = Tarea.titulo
            elif filtros.ordenar_por == "prioridad":
                # Ordenar por prioridad: urgente -> alta -> media -> baja
                order_field = case(
                    (Tarea.prioridad == "urgente", 1),
                    (Tarea.prioridad == "alta", 2),
                    (Tarea.prioridad == "media", 3),
                    (Tarea.prioridad == "baja", 4),
                    else_=5
                )
            else:
                order_field = Tarea.fecha_creacion
            
            if filtros.orden_desc:
                query = query.order_by(desc(order_field))
            else:
                query = query.order_by(asc(order_field))
            
            # Paginación
            offset = (filtros.pagina - 1) * filtros.tamaño_pagina
            query = query.offset(offset).limit(filtros.tamaño_pagina)
        
        return query.all()
    
    def obtener_tareas_por_docente(
        self,
        db: Session,
        *,
        docente_id: str,
        filtros: Optional[FiltrosTarea] = None
    ) -> List[Tarea]:
        """Obtener todas las tareas creadas por un docente"""
        query = db.query(Tarea).filter(Tarea.docente_id == docente_id)
        
        if filtros and filtros.solo_activas:
            query = query.filter(Tarea.activa == True)
        
        return query.all()
    
    def obtener_tarea_detallada(self, db: Session, tarea_id: str) -> Optional[Tarea]:
        """Obtener una tarea con toda su información relacionada"""
        return db.query(Tarea).options(
            joinedload(Tarea.docente),
            joinedload(Tarea.grupo),
            joinedload(Tarea.rubrica),
            joinedload(Tarea.entregas)
        ).filter(Tarea.tarea_id == tarea_id).first()
    
    def actualizar_estado_tarea(
        self, 
        db: Session, 
        *, 
        tarea_id: str, 
        nuevo_estado: EstadoTarea,
        actualizado_por: str
    ) -> Optional[Tarea]:
        """Actualizar solo el estado de una tarea"""
        tarea = self.get(db, id=tarea_id)
        if tarea:
            tarea.estado = nuevo_estado
            tarea.actualizado_por = actualizado_por
            tarea.fecha_actualizacion = datetime.utcnow()
            db.commit()
            db.refresh(tarea)
        return tarea
    
    def marcar_tareas_vencidas(self, db: Session) -> int:
        """Marcar automáticamente las tareas vencidas"""
        ahora = datetime.utcnow()
        tareas_vencidas = db.query(Tarea).filter(
            and_(
                Tarea.fecha_limite < ahora,
                Tarea.estado.in_([EstadoTarea.ASIGNADA, EstadoTarea.EN_PROGRESO]),
                Tarea.activa == True
            )
        ).update({
            "estado": EstadoTarea.VENCIDA,
            "fecha_actualizacion": ahora
        })
        
        db.commit()
        return tareas_vencidas
    
    def obtener_estadisticas_tarea(self, db: Session, tarea_id: str) -> Dict[str, Any]:
        """Obtener estadísticas detalladas de una tarea"""
        tarea = self.get(db, id=tarea_id)
        if not tarea:
            return {}
        
        entregas = db.query(EntregaTarea).filter(EntregaTarea.tarea_id == tarea_id).all()
        
        total_entregas = len([e for e in entregas if e.estado != EstadoEntrega.BORRADOR])
        entregas_calificadas = len([e for e in entregas if e.calificacion is not None])
        entregas_tardias = len([e for e in entregas if e.es_entrega_tardia])
        
        calificaciones = [e.calificacion for e in entregas if e.calificacion is not None]
        promedio_calificaciones = sum(calificaciones) / len(calificaciones) if calificaciones else 0
        
        return {
            "tarea_id": tarea_id,
            "titulo": tarea.titulo,
            "total_entregas": total_entregas,
            "entregas_calificadas": entregas_calificadas,
            "entregas_pendientes": total_entregas - entregas_calificadas,
            "entregas_tardias": entregas_tardias,
            "promedio_calificaciones": promedio_calificaciones,
            "porcentaje_completitud": (entregas_calificadas / total_entregas * 100) if total_entregas > 0 else 0,
            "esta_vencida": tarea.esta_vencida
        }


class CRUDEntregaTarea(CRUDBase[EntregaTarea, EntregaTareaCreate, EntregaTareaUpdate]):
    
    def crear_entrega(
        self,
        db: Session,
        *,
        entrega_data: EntregaTareaCreate
    ) -> EntregaTarea:
        """Crear una nueva entrega de tarea"""
        # Verificar si ya existe una entrega para esta tarea y estudiante
        entrega_existente = db.query(EntregaTarea).filter(
            and_(
                EntregaTarea.tarea_id == entrega_data.tarea_id,
                EntregaTarea.estudiante_id == entrega_data.estudiante_id
            )
        ).first()
        
        if entrega_existente:
            # Si existe, incrementar el número de intento
            numero_intento = entrega_existente.numero_intento + 1
        else:
            numero_intento = 1
        
        # Verificar si la entrega es tardía
        tarea = db.query(Tarea).filter(Tarea.tarea_id == entrega_data.tarea_id).first()
        es_tardia = datetime.utcnow() > tarea.fecha_limite if tarea else False
        
        entrega_dict = entrega_data.dict()
        entrega_dict.update({
            "numero_intento": numero_intento,
            "es_entrega_tardia": es_tardia,
            "fecha_limite_original": tarea.fecha_limite if tarea else None
        })
        
        entrega = EntregaTarea(**entrega_dict)
        db.add(entrega)
        db.commit()
        db.refresh(entrega)
        
        return entrega
    
    def entregar_tarea(
        self,
        db: Session,
        *,
        entrega_id: str
    ) -> Optional[EntregaTarea]:
        """Marcar una entrega como entregada (cambiar de borrador a entregada)"""
        entrega = self.get(db, id=entrega_id)
        if entrega and entrega.estado == EstadoEntrega.BORRADOR:
            entrega.estado = EstadoEntrega.ENTREGADA
            entrega.fecha_entrega = datetime.utcnow()
            entrega.es_final = True
            
            db.commit()
            db.refresh(entrega)
        
        return entrega
    
    def calificar_entrega(
        self,
        db: Session,
        *,
        entrega_id: str,
        calificacion_data: CalificarEntrega,
        calificado_por: str
    ) -> Optional[EntregaTarea]:
        """Calificar una entrega"""
        entrega = self.get(db, id=entrega_id)
        if not entrega:
            return None
        
        # Validar que la calificación no exceda el máximo de la tarea
        tarea = db.query(Tarea).filter(Tarea.tarea_id == entrega.tarea_id).first()
        if tarea and calificacion_data.calificacion > tarea.puntuacion_maxima:
            raise ValueError(f"La calificación no puede exceder {tarea.puntuacion_maxima} puntos")
        
        entrega.calificacion = calificacion_data.calificacion
        entrega.calificacion_letras = calificacion_data.calificacion_letras
        entrega.comentarios_docente = calificacion_data.comentarios_docente
        entrega.rubrica_calificacion = calificacion_data.rubrica_calificacion
        entrega.requiere_revision = calificacion_data.requiere_revision
        entrega.estado = EstadoEntrega.DEVUELTA if calificacion_data.requiere_revision else EstadoEntrega.CALIFICADA
        entrega.calificado_por = calificado_por
        entrega.fecha_calificacion = datetime.utcnow()
        
        db.commit()
        db.refresh(entrega)
        
        return entrega
    
    def obtener_entregas_por_tarea(
        self,
        db: Session,
        *,
        tarea_id: str,
        filtros: Optional[FiltrosEntrega] = None
    ) -> List[EntregaTarea]:
        """Obtener todas las entregas de una tarea"""
        query = db.query(EntregaTarea).filter(EntregaTarea.tarea_id == tarea_id)
        
        if filtros:
            if filtros.estado:
                query = query.filter(EntregaTarea.estado == filtros.estado)
            
            if filtros.estudiante_id:
                query = query.filter(EntregaTarea.estudiante_id == filtros.estudiante_id)
            
            if filtros.solo_calificadas:
                query = query.filter(EntregaTarea.calificacion.isnot(None))
            
            if filtros.solo_pendientes:
                query = query.filter(
                    and_(
                        EntregaTarea.estado == EstadoEntrega.ENTREGADA,
                        EntregaTarea.calificacion.is_(None)
                    )
                )
            
            if filtros.fecha_desde:
                query = query.filter(EntregaTarea.fecha_entrega >= filtros.fecha_desde)
            
            if filtros.fecha_hasta:
                query = query.filter(EntregaTarea.fecha_entrega <= filtros.fecha_hasta)
            
            # Ordenamiento
            if filtros.ordenar_por == "fecha_entrega":
                order_field = EntregaTarea.fecha_entrega
            elif filtros.ordenar_por == "calificacion":
                order_field = EntregaTarea.calificacion
            elif filtros.ordenar_por == "fecha_creacion":
                order_field = EntregaTarea.fecha_creacion
            else:
                order_field = EntregaTarea.fecha_entrega
            
            if filtros.orden_desc:
                query = query.order_by(desc(order_field))
            else:
                query = query.order_by(asc(order_field))
            
            # Paginación
            if filtros.pagina and filtros.tamaño_pagina:
                offset = (filtros.pagina - 1) * filtros.tamaño_pagina
                query = query.offset(offset).limit(filtros.tamaño_pagina)
        
        return query.all()
    
    def obtener_entregas_por_estudiante(
        self,
        db: Session,
        *,
        estudiante_id: str,
        grupo_id: Optional[str] = None
    ) -> List[EntregaTarea]:
        """Obtener todas las entregas de un estudiante"""
        query = db.query(EntregaTarea).filter(EntregaTarea.estudiante_id == estudiante_id)
        
        if grupo_id:
            query = query.join(Tarea).filter(Tarea.grupo_id == grupo_id)
        
        return query.all()
    
    def obtener_entrega_detallada(self, db: Session, entrega_id: str) -> Optional[EntregaTarea]:
        """Obtener una entrega con toda su información relacionada"""
        return db.query(EntregaTarea).options(
            joinedload(EntregaTarea.tarea),
            joinedload(EntregaTarea.estudiante),
            joinedload(EntregaTarea.calificador)
        ).filter(EntregaTarea.entrega_id == entrega_id).first()


class CRUDRubrica(CRUDBase[Rubrica, RubricaCreate, RubricaUpdate]):
    
    def obtener_rubricas_por_docente(
        self,
        db: Session,
        *,
        docente_id: str,
        incluir_publicas: bool = True
    ) -> List[Rubrica]:
        """Obtener todas las rúbricas de un docente"""
        query = db.query(Rubrica)
        
        if incluir_publicas:
            query = query.filter(
                or_(
                    Rubrica.creado_por == docente_id,
                    Rubrica.es_publica == True
                )
            )
        else:
            query = query.filter(Rubrica.creado_por == docente_id)
        
        return query.filter(Rubrica.activa == True).all()
    
    def obtener_rubricas_publicas(self, db: Session) -> List[Rubrica]:
        """Obtener todas las rúbricas públicas"""
        return db.query(Rubrica).filter(
            and_(
                Rubrica.es_publica == True,
                Rubrica.activa == True
            )
        ).all()
    
    def obtener_plantillas_rubrica(self, db: Session) -> List[Rubrica]:
        """Obtener todas las plantillas de rúbricas"""
        return db.query(Rubrica).filter(
            and_(
                Rubrica.es_plantilla == True,
                Rubrica.activa == True
            )
        ).all()
    
    def duplicar_rubrica(
        self,
        db: Session,
        *,
        rubrica_id: str,
        nuevo_nombre: str,
        creado_por: str
    ) -> Optional[Rubrica]:
        """Duplicar una rúbrica existente"""
        rubrica_original = self.get(db, id=rubrica_id)
        if not rubrica_original:
            return None
        
        nueva_rubrica = Rubrica(
            nombre=nuevo_nombre,
            descripcion=rubrica_original.descripcion,
            criterios=rubrica_original.criterios,
            puntuacion_total=rubrica_original.puntuacion_total,
            es_publica=False,  # Por defecto, las copias son privadas
            es_plantilla=False,
            creado_por=creado_por
        )
        
        db.add(nueva_rubrica)
        db.commit()
        db.refresh(nueva_rubrica)
        
        return nueva_rubrica


# Instancias de los CRUDs
crud_tarea = CRUDTarea(Tarea)
crud_entrega_tarea = CRUDEntregaTarea(EntregaTarea)
crud_rubrica = CRUDRubrica(Rubrica)