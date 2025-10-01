"""
CRUD operations para el modelo PreguntaExamen
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime

from src.crud.base import CRUDBase
from src.models.evaluaciones import PreguntaExamen, TipoPregunta, DificultadPregunta
from src.schemas.evaluaciones import PreguntaExamenCreate, PreguntaExamenUpdate


class CRUDPreguntaExamen(CRUDBase[PreguntaExamen, PreguntaExamenCreate, PreguntaExamenUpdate]):
    
    def get_preguntas_por_examen(
        self, 
        db: Session, 
        examen_id: str,
        orden: bool = True
    ) -> List[PreguntaExamen]:
        """Obtener todas las preguntas de un examen ordenadas"""
        query = db.query(PreguntaExamen).filter(PreguntaExamen.examen_id == examen_id)
        
        if orden:
            query = query.order_by(asc(PreguntaExamen.orden))
        
        return query.all()
    
    def get_pregunta_por_orden(
        self, 
        db: Session, 
        examen_id: str, 
        orden: int
    ) -> Optional[PreguntaExamen]:
        """Obtener una pregunta específica por su orden en el examen"""
        return db.query(PreguntaExamen).filter(
            and_(
                PreguntaExamen.examen_id == examen_id,
                PreguntaExamen.orden == orden
            )
        ).first()
    
    def create_pregunta_con_orden(
        self, 
        db: Session, 
        obj_in: PreguntaExamenCreate
    ) -> PreguntaExamen:
        """Crear una pregunta asignando automáticamente el siguiente número de orden"""
        # Obtener el último orden para este examen
        ultimo_orden = db.query(func.max(PreguntaExamen.orden)).filter(
            PreguntaExamen.examen_id == obj_in.examen_id
        ).scalar()
        
        # Si no hay preguntas, empezar en 1, sino siguiente número
        nuevo_orden = (ultimo_orden or 0) + 1
        
        # Crear la pregunta con el nuevo orden
        obj_in.orden = nuevo_orden
        return self.create(db=db, obj_in=obj_in)
    
    def reordenar_preguntas(
        self, 
        db: Session, 
        examen_id: str, 
        nuevos_ordenes: List[Dict[str, int]]
    ) -> List[PreguntaExamen]:
        """Reordenar preguntas según nuevos órdenes
        
        Args:
            nuevos_ordenes: Lista de {"pregunta_id": "id", "nuevo_orden": 1}
        """
        preguntas_actualizadas = []
        
        for item in nuevos_ordenes:
            pregunta = db.query(PreguntaExamen).filter(
                and_(
                    PreguntaExamen.pregunta_id == item["pregunta_id"],
                    PreguntaExamen.examen_id == examen_id
                )
            ).first()
            
            if pregunta:
                pregunta.orden = item["nuevo_orden"]
                pregunta.fecha_actualizacion = datetime.utcnow()
                preguntas_actualizadas.append(pregunta)
        
        db.commit()
        
        # Refrescar todas las preguntas actualizadas
        for pregunta in preguntas_actualizadas:
            db.refresh(pregunta)
        
        return preguntas_actualizadas
    
    def importar_desde_banco(
        self, 
        db: Session, 
        examen_id: str, 
        banco_pregunta_id: str,
        puntuacion_personalizada: Optional[float] = None,
        orden_personalizado: Optional[int] = None
    ) -> Optional[PreguntaExamen]:
        """Importar una pregunta del banco de preguntas a un examen"""
        from src.models.evaluaciones import BancoPregunta
        
        banco_pregunta = db.query(BancoPregunta).filter(
            BancoPregunta.pregunta_id == banco_pregunta_id
        ).first()
        
        if not banco_pregunta:
            return None
        
        # Determinar el orden
        if orden_personalizado:
            orden = orden_personalizado
        else:
            ultimo_orden = db.query(func.max(PreguntaExamen.orden)).filter(
                PreguntaExamen.examen_id == examen_id
            ).scalar()
            orden = (ultimo_orden or 0) + 1
        
        # Crear pregunta basada en el banco
        pregunta_data = PreguntaExamenCreate(
            examen_id=examen_id,
            banco_pregunta_id=banco_pregunta_id,
            titulo=banco_pregunta.titulo,
            descripcion=banco_pregunta.descripcion,
            tipo_pregunta=banco_pregunta.tipo_pregunta,
            orden=orden,
            puntuacion=puntuacion_personalizada or banco_pregunta.puntuacion_sugerida,
            opciones_respuesta=banco_pregunta.opciones_respuesta,
            respuesta_correcta=banco_pregunta.respuesta_correcta,
            explicacion=banco_pregunta.explicacion,
            dificultad=banco_pregunta.dificultad,
            imagen_url=banco_pregunta.imagen_url,
            audio_url=banco_pregunta.audio_url,
            video_url=banco_pregunta.video_url,
            archivos_adjuntos=banco_pregunta.archivos_adjuntos,
            tags=banco_pregunta.tags,
            tiempo_limite_segundos=banco_pregunta.tiempo_estimado_segundos
        )
        
        pregunta_creada = self.create(db=db, obj_in=pregunta_data)
        
        # Actualizar estadísticas del banco
        banco_pregunta.veces_utilizada = (banco_pregunta.veces_utilizada or 0) + 1
        banco_pregunta.ultima_vez_utilizada = datetime.utcnow()
        
        db.commit()
        db.refresh(pregunta_creada)
        return pregunta_creada
    
    def duplicar_pregunta(
        self, 
        db: Session, 
        pregunta_id: str, 
        nuevo_examen_id: Optional[str] = None
    ) -> Optional[PreguntaExamen]:
        """Duplicar una pregunta, opcionalmente a otro examen"""
        pregunta_original = self.get(db=db, id=pregunta_id)
        if not pregunta_original:
            return None
        
        examen_destino = nuevo_examen_id or pregunta_original.examen_id
        
        # Obtener siguiente orden para el examen destino
        ultimo_orden = db.query(func.max(PreguntaExamen.orden)).filter(
            PreguntaExamen.examen_id == examen_destino
        ).scalar()
        nuevo_orden = (ultimo_orden or 0) + 1
        
        # Crear pregunta duplicada
        pregunta_data = PreguntaExamenCreate(
            examen_id=examen_destino,
            titulo=f"Copia de: {pregunta_original.titulo}",
            descripcion=pregunta_original.descripcion,
            tipo_pregunta=pregunta_original.tipo_pregunta,
            orden=nuevo_orden,
            puntuacion=pregunta_original.puntuacion,
            es_obligatoria=pregunta_original.es_obligatoria,
            tiempo_limite_segundos=pregunta_original.tiempo_limite_segundos,
            opciones_respuesta=pregunta_original.opciones_respuesta,
            respuesta_correcta=pregunta_original.respuesta_correcta,
            explicacion=pregunta_original.explicacion,
            puntos_respuesta_parcial=pregunta_original.puntos_respuesta_parcial,
            dificultad=pregunta_original.dificultad,
            imagen_url=pregunta_original.imagen_url,
            audio_url=pregunta_original.audio_url,
            video_url=pregunta_original.video_url,
            archivos_adjuntos=pregunta_original.archivos_adjuntos,
            tags=pregunta_original.tags
        )
        
        return self.create(db=db, obj_in=pregunta_data)
    
    def eliminar_con_reordenamiento(
        self, 
        db: Session, 
        pregunta_id: str
    ) -> bool:
        """Eliminar una pregunta y reordenar las siguientes"""
        pregunta = self.get(db=db, id=pregunta_id)
        if not pregunta:
            return False
        
        examen_id = pregunta.examen_id
        orden_eliminado = pregunta.orden
        
        # Eliminar la pregunta
        db.delete(pregunta)
        
        # Reordenar las preguntas posteriores
        preguntas_posteriores = db.query(PreguntaExamen).filter(
            and_(
                PreguntaExamen.examen_id == examen_id,
                PreguntaExamen.orden > orden_eliminado
            )
        ).all()
        
        for pregunta_posterior in preguntas_posteriores:
            pregunta_posterior.orden -= 1
            pregunta_posterior.fecha_actualizacion = datetime.utcnow()
        
        db.commit()
        return True
    
    def buscar_preguntas(
        self, 
        db: Session,
        filtros: Dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[PreguntaExamen]:
        """Buscar preguntas con filtros avanzados"""
        query = db.query(PreguntaExamen)
        
        # Filtro por examen
        if "examen_id" in filtros and filtros["examen_id"]:
            query = query.filter(PreguntaExamen.examen_id == filtros["examen_id"])
        
        # Filtro por tipo de pregunta
        if "tipo_pregunta" in filtros and filtros["tipo_pregunta"]:
            if isinstance(filtros["tipo_pregunta"], list):
                query = query.filter(PreguntaExamen.tipo_pregunta.in_(filtros["tipo_pregunta"]))
            else:
                query = query.filter(PreguntaExamen.tipo_pregunta == filtros["tipo_pregunta"])
        
        # Filtro por dificultad
        if "dificultad" in filtros and filtros["dificultad"]:
            if isinstance(filtros["dificultad"], list):
                query = query.filter(PreguntaExamen.dificultad.in_(filtros["dificultad"]))
            else:
                query = query.filter(PreguntaExamen.dificultad == filtros["dificultad"])
        
        # Filtro por texto en título
        if "busqueda" in filtros and filtros["busqueda"]:
            texto_busqueda = f"%{filtros['busqueda']}%"
            query = query.filter(PreguntaExamen.titulo.ilike(texto_busqueda))
        
        # Filtro por puntuación mínima/máxima
        if "puntuacion_min" in filtros and filtros["puntuacion_min"]:
            query = query.filter(PreguntaExamen.puntuacion >= filtros["puntuacion_min"])
        
        if "puntuacion_max" in filtros and filtros["puntuacion_max"]:
            query = query.filter(PreguntaExamen.puntuacion <= filtros["puntuacion_max"])
        
        # Filtro por tags
        if "tags" in filtros and filtros["tags"]:
            for tag in filtros["tags"]:
                query = query.filter(PreguntaExamen.tags.contains([tag]))
        
        # Ordenamiento
        orden = filtros.get("orden", "orden_asc")
        if orden == "orden_asc":
            query = query.order_by(asc(PreguntaExamen.orden))
        elif orden == "orden_desc":
            query = query.order_by(desc(PreguntaExamen.orden))
        elif orden == "puntuacion_asc":
            query = query.order_by(asc(PreguntaExamen.puntuacion))
        elif orden == "puntuacion_desc":
            query = query.order_by(desc(PreguntaExamen.puntuacion))
        elif orden == "dificultad":
            # Ordenar por dificultad: FACIL, MEDIO, DIFICIL
            query = query.order_by(PreguntaExamen.dificultad)
        
        return query.offset(skip).limit(limit).all()
    
    def get_estadisticas_pregunta(
        self, 
        db: Session, 
        pregunta_id: str
    ) -> Dict[str, Any]:
        """Obtener estadísticas detalladas de una pregunta"""
        pregunta = self.get(db=db, id=pregunta_id)
        if not pregunta:
            return {}
        
        from src.models.evaluaciones import RespuestaEstudiante, IntentoExamen, EstadoIntento
        
        # Total de respuestas
        total_respuestas = db.query(func.count(RespuestaEstudiante.respuesta_id)).filter(
            RespuestaEstudiante.pregunta_id == pregunta_id
        ).scalar()
        
        # Respuestas correctas
        respuestas_correctas = db.query(func.count(RespuestaEstudiante.respuesta_id)).filter(
            and_(
                RespuestaEstudiante.pregunta_id == pregunta_id,
                RespuestaEstudiante.es_correcta == True
            )
        ).scalar()
        
        # Tiempo promedio de respuesta
        tiempo_promedio = db.query(
            func.avg(RespuestaEstudiante.tiempo_empleado_segundos)
        ).filter(
            and_(
                RespuestaEstudiante.pregunta_id == pregunta_id,
                RespuestaEstudiante.tiempo_empleado_segundos.is_not(None)
            )
        ).scalar()
        
        # Puntuación promedio
        puntuacion_promedio = db.query(
            func.avg(RespuestaEstudiante.puntuacion_obtenida)
        ).filter(
            RespuestaEstudiante.pregunta_id == pregunta_id
        ).scalar()
        
        # Distribución de respuestas (para opción múltiple)
        distribucion_respuestas = {}
        if pregunta.tipo_pregunta == TipoPregunta.OPCION_MULTIPLE:
            respuestas_estudiantes = db.query(
                RespuestaEstudiante.respuesta_estudiante
            ).filter(
                RespuestaEstudiante.pregunta_id == pregunta_id
            ).all()
            
            for resp in respuestas_estudiantes:
                if resp.respuesta_estudiante and isinstance(resp.respuesta_estudiante, dict):
                    opcion = resp.respuesta_estudiante.get('opcion_seleccionada', 'sin_respuesta')
                    distribucion_respuestas[opcion] = distribucion_respuestas.get(opcion, 0) + 1
        
        # Calcular porcentaje de aciertos
        porcentaje_aciertos = 0
        if total_respuestas > 0:
            porcentaje_aciertos = round((respuestas_correctas / total_respuestas) * 100, 2)
        
        # Actualizar estadísticas en la pregunta
        pregunta.veces_utilizada = total_respuestas or 0
        pregunta.promedio_aciertos = porcentaje_aciertos
        pregunta.tiempo_promedio_respuesta = round(tiempo_promedio or 0, 2) if tiempo_promedio else None
        
        db.commit()
        db.refresh(pregunta)
        
        return {
            "pregunta_id": pregunta_id,
            "total_respuestas": total_respuestas or 0,
            "respuestas_correctas": respuestas_correctas or 0,
            "porcentaje_aciertos": porcentaje_aciertos,
            "tiempo_promedio_segundos": round(tiempo_promedio or 0, 2) if tiempo_promedio else None,
            "puntuacion_promedio": round(puntuacion_promedio or 0, 2) if puntuacion_promedio else None,
            "distribucion_respuestas": distribucion_respuestas,
            "dificultad_calculada": self._calcular_dificultad_real(porcentaje_aciertos),
            "tipo_pregunta": pregunta.tipo_pregunta.value,
            "dificultad_asignada": pregunta.dificultad.value
        }
    
    def _calcular_dificultad_real(self, porcentaje_aciertos: float) -> str:
        """Calcular la dificultad real basada en el porcentaje de aciertos"""
        if porcentaje_aciertos >= 80:
            return "muy_facil"
        elif porcentaje_aciertos >= 60:
            return "facil"
        elif porcentaje_aciertos >= 40:
            return "medio"
        elif porcentaje_aciertos >= 20:
            return "dificil"
        else:
            return "muy_dificil"
    
    def validar_pregunta(self, db: Session, pregunta_id: str) -> Dict[str, Any]:
        """Validar que una pregunta esté bien configurada"""
        pregunta = self.get(db=db, id=pregunta_id)
        if not pregunta:
            return {"valida": False, "errores": ["Pregunta no encontrada"]}
        
        errores = []
        advertencias = []
        
        # Validaciones básicas
        if not pregunta.titulo or len(pregunta.titulo.strip()) < 5:
            errores.append("El título de la pregunta debe tener al menos 5 caracteres")
        
        if pregunta.puntuacion <= 0:
            errores.append("La puntuación debe ser mayor a 0")
        
        # Validaciones por tipo de pregunta
        if pregunta.tipo_pregunta == TipoPregunta.OPCION_MULTIPLE:
            if not pregunta.opciones_respuesta or "opciones" not in pregunta.opciones_respuesta:
                errores.append("Las preguntas de opción múltiple deben tener opciones definidas")
            elif len(pregunta.opciones_respuesta["opciones"]) < 2:
                errores.append("Debe haber al menos 2 opciones")
            
            if not pregunta.respuesta_correcta:
                errores.append("Debe especificar la respuesta correcta")
        
        elif pregunta.tipo_pregunta == TipoPregunta.VERDADERO_FALSO:
            if not pregunta.respuesta_correcta:
                errores.append("Debe especificar si la respuesta es verdadero o falso")
        
        elif pregunta.tipo_pregunta == TipoPregunta.ENSAYO:
            if not pregunta.explicacion:
                advertencias.append("Se recomienda proporcionar criterios de evaluación para preguntas de ensayo")
        
        # Validaciones de recursos
        if pregunta.tiempo_limite_segundos and pregunta.tiempo_limite_segundos < 10:
            advertencias.append("Un tiempo límite muy corto puede ser insuficiente")
        
        return {
            "valida": len(errores) == 0,
            "errores": errores,
            "advertencias": advertencias,
            "puede_usar_calificacion_automatica": pregunta.tipo_pregunta in [
                TipoPregunta.OPCION_MULTIPLE, 
                TipoPregunta.VERDADERO_FALSO
            ]
        }


# Instancia del CRUD
pregunta_examen = CRUDPreguntaExamen(PreguntaExamen)