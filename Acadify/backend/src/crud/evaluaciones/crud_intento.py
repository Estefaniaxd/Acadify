"""
CRUD operations para el modelo IntentoExamen
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
import random

from src.crud.base import CRUDBase
from src.models.evaluaciones import (
    IntentoExamen, EstadoIntento, Examen, PreguntaExamen, RespuestaEstudiante
)
from src.schemas.evaluaciones import IntentoExamenCreate, IntentoExamenUpdate


class CRUDIntentoExamen(CRUDBase[IntentoExamen, IntentoExamenCreate, IntentoExamenUpdate]):
    
    def crear_intento(
        self, 
        db: Session, 
        estudiante_id: str, 
        examen_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[IntentoExamen]:
        """Crear un nuevo intento de examen con todas las validaciones"""
        
        # Verificar que el examen existe y está disponible
        examen = db.query(Examen).filter(Examen.examen_id == examen_id).first()
        if not examen:
            return None
        
        # Contar intentos previos del estudiante
        intentos_previos = db.query(func.count(IntentoExamen.intento_id)).filter(
            and_(
                IntentoExamen.examen_id == examen_id,
                IntentoExamen.estudiante_id == estudiante_id
            )
        ).scalar()
        
        # Verificar límite de intentos
        if intentos_previos >= examen.intentos_permitidos:
            raise ValueError("Has excedido el número máximo de intentos permitidos")
        
        # Verificar si hay un intento en progreso
        intento_en_progreso = db.query(IntentoExamen).filter(
            and_(
                IntentoExamen.examen_id == examen_id,
                IntentoExamen.estudiante_id == estudiante_id,
                IntentoExamen.estado == EstadoIntento.EN_PROGRESO
            )
        ).first()
        
        if intento_en_progreso:
            return intento_en_progreso  # Retornar el intento existente
        
        # Obtener preguntas del examen
        preguntas = db.query(PreguntaExamen).filter(
            PreguntaExamen.examen_id == examen_id
        ).order_by(PreguntaExamen.orden).all()
        
        if not preguntas:
            raise ValueError("El examen no tiene preguntas configuradas")
        
        # Determinar orden de preguntas
        orden_preguntas = [p.pregunta_id for p in preguntas]
        if examen.randomizar_preguntas:
            random.shuffle(orden_preguntas)
        
        # Calcular puntuación máxima
        puntuacion_maxima = sum(p.puntuacion for p in preguntas)
        
        # Crear el intento
        intento_data = IntentoExamenCreate(
            examen_id=examen_id,
            estudiante_id=estudiante_id
        )
        
        # Crear objeto IntentoExamen directamente con todos los campos
        db_obj = IntentoExamen(
            examen_id=examen_id,
            estudiante_id=estudiante_id,
            numero_intento=(intentos_previos or 0) + 1,
            estado=EstadoIntento.EN_PROGRESO,
            puntuacion_maxima=puntuacion_maxima,
            total_preguntas=len(preguntas),
            pregunta_actual=1,
            orden_preguntas=orden_preguntas,
            ip_address=ip_address,
            user_agent=user_agent,
            fecha_inicio=datetime.utcnow()
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def get_intentos_por_estudiante(
        self, 
        db: Session, 
        estudiante_id: str, 
        examen_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[IntentoExamen]:
        """Obtener intentos de un estudiante"""
        query = db.query(IntentoExamen).filter(
            IntentoExamen.estudiante_id == estudiante_id
        )
        
        if examen_id:
            query = query.filter(IntentoExamen.examen_id == examen_id)
        
        return query.order_by(desc(IntentoExamen.fecha_inicio)).offset(skip).limit(limit).all()
    
    def get_intento_activo(
        self, 
        db: Session, 
        estudiante_id: str, 
        examen_id: str
    ) -> Optional[IntentoExamen]:
        """Obtener el intento activo de un estudiante para un examen"""
        return db.query(IntentoExamen).filter(
            and_(
                IntentoExamen.estudiante_id == estudiante_id,
                IntentoExamen.examen_id == examen_id,
                IntentoExamen.estado == EstadoIntento.EN_PROGRESO
            )
        ).first()
    
    def avanzar_pregunta(
        self, 
        db: Session, 
        intento_id: str, 
        nueva_pregunta: Optional[int] = None
    ) -> Optional[IntentoExamen]:
        """Avanzar a la siguiente pregunta o a una pregunta específica"""
        intento = self.get(db=db, id=intento_id)
        if not intento or intento.estado != EstadoIntento.EN_PROGRESO:
            return None
        
        if nueva_pregunta:
            if 1 <= nueva_pregunta <= intento.total_preguntas:
                intento.pregunta_actual = nueva_pregunta
        else:
            if intento.pregunta_actual < intento.total_preguntas:
                intento.pregunta_actual += 1
        
        db.commit()
        db.refresh(intento)
        return intento
    
    def registrar_evento_sospechoso(
        self, 
        db: Session, 
        intento_id: str, 
        tipo_evento: str,
        detalles: Dict[str, Any]
    ) -> Optional[IntentoExamen]:
        """Registrar un evento sospechoso durante el intento"""
        intento = self.get(db=db, id=intento_id)
        if not intento:
            return None
        
        eventos_actuales = intento.eventos_sospechosos or {}
        timestamp = datetime.utcnow().isoformat()
        
        if tipo_evento not in eventos_actuales:
            eventos_actuales[tipo_evento] = []
        
        eventos_actuales[tipo_evento].append({
            "timestamp": timestamp,
            "detalles": detalles
        })
        
        # Actualizar contadores específicos
        if tipo_evento == "cambio_pestana":
            intento.cambios_pestana_detectados = (intento.cambios_pestana_detectados or 0) + 1
        elif tipo_evento == "inactividad":
            tiempo_inactividad = detalles.get("duracion_segundos", 0)
            intento.tiempo_inactividad_total = (intento.tiempo_inactividad_total or 0) + tiempo_inactividad
        
        intento.eventos_sospechosos = eventos_actuales
        
        db.commit()
        db.refresh(intento)
        return intento
    
    def finalizar_intento(
        self, 
        db: Session, 
        intento_id: str, 
        motivo_finalizacion: str = "estudiante",
        forzar_finalizacion: bool = False
    ) -> Optional[IntentoExamen]:
        """Finalizar un intento de examen"""
        intento = self.get(db=db, id=intento_id)
        if not intento:
            return None
        
        if intento.estado != EstadoIntento.EN_PROGRESO and not forzar_finalizacion:
            return intento  # Ya está finalizado
        
        # Determinar el estado final
        if motivo_finalizacion == "tiempo_agotado":
            intento.estado = EstadoIntento.TIEMPO_AGOTADO
            intento.tiempo_limite_vencido = True
        elif motivo_finalizacion == "cancelado":
            intento.estado = EstadoIntento.CANCELADO
        else:
            intento.estado = EstadoIntento.FINALIZADO
        
        # Registrar tiempos
        intento.fecha_fin = datetime.utcnow()
        if intento.fecha_inicio:
            tiempo_total = intento.fecha_fin - intento.fecha_inicio
            intento.tiempo_total_segundos = int(tiempo_total.total_seconds())
        
        intento.finalizado_por = motivo_finalizacion
        
        # Calcular calificación final
        self._calcular_calificacion_final(db, intento)
        
        db.commit()
        db.refresh(intento)
        
        # Actualizar estadísticas del examen
        self._actualizar_estadisticas_examen(db, intento.examen_id)
        
        return intento
    
    def finalizar_por_tiempo(
        self, 
        db: Session, 
        duracion_maxima_minutos: int
    ) -> List[IntentoExamen]:
        """Finalizar intentos que han excedido el tiempo límite"""
        tiempo_limite = datetime.utcnow() - timedelta(minutes=duracion_maxima_minutos)
        
        intentos_vencidos = db.query(IntentoExamen).filter(
            and_(
                IntentoExamen.estado == EstadoIntento.EN_PROGRESO,
                IntentoExamen.fecha_inicio <= tiempo_limite
            )
        ).all()
        
        intentos_finalizados = []
        for intento in intentos_vencidos:
            intento_finalizado = self.finalizar_intento(
                db, intento.intento_id, "tiempo_agotado", forzar_finalizacion=True
            )
            if intento_finalizado:
                intentos_finalizados.append(intento_finalizado)
        
        return intentos_finalizados
    
    def recuperar_intento(
        self, 
        db: Session, 
        estudiante_id: str, 
        examen_id: str
    ) -> Optional[IntentoExamen]:
        """Recuperar un intento interrumpido si es posible"""
        # Buscar intento en progreso reciente (últimas 72 horas por defecto)
        tiempo_limite = datetime.utcnow() - timedelta(hours=72)
        
        intento = db.query(IntentoExamen).filter(
            and_(
                IntentoExamen.estudiante_id == estudiante_id,
                IntentoExamen.examen_id == examen_id,
                IntentoExamen.estado == EstadoIntento.EN_PROGRESO,
                IntentoExamen.fecha_inicio >= tiempo_limite
            )
        ).first()
        
        if not intento:
            return None
        
        # Verificar si el examen aún permite recuperación
        examen = db.query(Examen).filter(Examen.examen_id == examen_id).first()
        if not examen:
            return None
        
        # Verificar tiempo límite del examen
        if examen.duracion_minutos:
            tiempo_transcurrido = datetime.utcnow() - intento.fecha_inicio
            if tiempo_transcurrido.total_seconds() > (examen.duracion_minutos * 60):
                # Finalizar por tiempo agotado
                return self.finalizar_intento(db, intento.intento_id, "tiempo_agotado")
        
        return intento
    
    def get_intentos_por_examen(
        self, 
        db: Session, 
        examen_id: str,
        estado: Optional[EstadoIntento] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[IntentoExamen]:
        """Obtener intentos de un examen específico"""
        query = db.query(IntentoExamen).filter(
            IntentoExamen.examen_id == examen_id
        )
        
        if estado:
            query = query.filter(IntentoExamen.estado == estado)
        
        return query.order_by(desc(IntentoExamen.fecha_inicio)).offset(skip).limit(limit).all()
    
    def get_estadisticas_intento(
        self, 
        db: Session, 
        intento_id: str
    ) -> Dict[str, Any]:
        """Obtener estadísticas detalladas de un intento"""
        intento = self.get(db=db, id=intento_id)
        if not intento:
            return {}
        
        # Obtener respuestas del intento
        respuestas = db.query(RespuestaEstudiante).filter(
            RespuestaEstudiante.intento_id == intento_id
        ).all()
        
        # Calcular estadísticas
        total_respuestas = len(respuestas)
        respuestas_correctas = sum(1 for r in respuestas if r.es_correcta)
        respuestas_incorrectas = total_respuestas - respuestas_correctas
        
        # Tiempo promedio por pregunta
        tiempos_respuesta = [r.tiempo_empleado_segundos for r in respuestas if r.tiempo_empleado_segundos]
        tiempo_promedio_pregunta = sum(tiempos_respuesta) / len(tiempos_respuesta) if tiempos_respuesta else 0
        
        # Distribución por tipo de pregunta
        from src.models.evaluaciones import PreguntaExamen
        distribucion_tipos = {}
        for respuesta in respuestas:
            pregunta = db.query(PreguntaExamen).filter(
                PreguntaExamen.pregunta_id == respuesta.pregunta_id
            ).first()
            if pregunta:
                tipo = pregunta.tipo_pregunta.value
                if tipo not in distribucion_tipos:
                    distribucion_tipos[tipo] = {"total": 0, "correctas": 0}
                distribucion_tipos[tipo]["total"] += 1
                if respuesta.es_correcta:
                    distribucion_tipos[tipo]["correctas"] += 1
        
        return {
            "intento_id": intento_id,
            "estado": intento.estado.value,
            "numero_intento": intento.numero_intento,
            "puntuacion_obtenida": intento.puntuacion_obtenida,
            "puntuacion_maxima": intento.puntuacion_maxima,
            "porcentaje": intento.porcentaje,
            "aprobado": intento.aprobado,
            "tiempo_total_segundos": intento.tiempo_total_segundos,
            "total_respuestas": total_respuestas,
            "respuestas_correctas": respuestas_correctas,
            "respuestas_incorrectas": respuestas_incorrectas,
            "porcentaje_aciertos": round((respuestas_correctas / total_respuestas) * 100, 2) if total_respuestas > 0 else 0,
            "tiempo_promedio_por_pregunta": round(tiempo_promedio_pregunta, 2),
            "cambios_pestana_detectados": intento.cambios_pestana_detectados or 0,
            "tiempo_inactividad_total": intento.tiempo_inactividad_total or 0,
            "eventos_sospechosos": intento.eventos_sospechosos or {},
            "distribucion_por_tipo": distribucion_tipos,
            "progreso": {
                "preguntas_respondidas": intento.preguntas_respondidas,
                "total_preguntas": intento.total_preguntas,
                "progreso_porcentaje": round((intento.preguntas_respondidas / intento.total_preguntas) * 100, 2) if intento.total_preguntas > 0 else 0
            }
        }
    
    def _calcular_calificacion_final(self, db: Session, intento: IntentoExamen):
        """Calcular la calificación final del intento"""
        # Obtener todas las respuestas del intento
        respuestas = db.query(RespuestaEstudiante).filter(
            RespuestaEstudiante.intento_id == intento.intento_id
        ).all()
        
        # Calcular puntuación total obtenida
        puntuacion_obtenida = sum(r.puntuacion_obtenida for r in respuestas)
        intento.puntuacion_obtenida = puntuacion_obtenida
        
        # Calcular porcentaje
        if intento.puntuacion_maxima > 0:
            intento.porcentaje = round((puntuacion_obtenida / intento.puntuacion_maxima) * 100, 2)
        else:
            intento.porcentaje = 0
        
        # Determinar si aprobó
        examen = db.query(Examen).filter(Examen.examen_id == intento.examen_id).first()
        if examen:
            intento.aprobado = intento.porcentaje >= examen.puntuacion_minima_aprobacion
        
        # Actualizar contador de preguntas respondidas
        intento.preguntas_respondidas = len(respuestas)
    
    def _actualizar_estadisticas_examen(self, db: Session, examen_id: str):
        """Actualizar estadísticas del examen después de finalizar un intento"""
        from src.crud.evaluaciones.crud_examen import examen
        examen.actualizar_estadisticas_examen(db, examen_id)
    
    def get_ranking_intentos(
        self, 
        db: Session, 
        examen_id: str, 
        limite: int = 10
    ) -> List[Dict[str, Any]]:
        """Obtener ranking de mejores intentos de un examen"""
        intentos = db.query(IntentoExamen).filter(
            and_(
                IntentoExamen.examen_id == examen_id,
                IntentoExamen.estado == EstadoIntento.FINALIZADO,
                IntentoExamen.porcentaje.is_not(None)
            )
        ).order_by(
            desc(IntentoExamen.porcentaje),
            asc(IntentoExamen.tiempo_total_segundos)
        ).limit(limite).all()
        
        ranking = []
        for i, intento in enumerate(intentos, 1):
            ranking.append({
                "posicion": i,
                "intento_id": intento.intento_id,
                "estudiante_id": intento.estudiante_id,
                "puntuacion_obtenida": intento.puntuacion_obtenida,
                "puntuacion_maxima": intento.puntuacion_maxima,
                "porcentaje": intento.porcentaje,
                "tiempo_total_segundos": intento.tiempo_total_segundos,
                "fecha_fin": intento.fecha_fin,
                "numero_intento": intento.numero_intento
            })
        
        return ranking


# Instancia del CRUD
intento_examen = CRUDIntentoExamen(IntentoExamen)