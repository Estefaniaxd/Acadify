"""
CRUD operations para el modelo RespuestaEstudiante
"""

from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime
import json
import re

from src.crud.base import CRUDBase
from src.models.evaluaciones import (
    RespuestaEstudiante, PreguntaExamen, TipoPregunta, IntentoExamen
)
from src.schemas.evaluaciones import RespuestaEstudianteCreate, RespuestaEstudianteUpdate


class CRUDRespuestaEstudiante(CRUDBase[RespuestaEstudiante, RespuestaEstudianteCreate, RespuestaEstudianteUpdate]):
    
    def crear_o_actualizar_respuesta(
        self, 
        db: Session, 
        intento_id: str,
        pregunta_id: str,
        respuesta_datos: Dict[str, Any],
        tiempo_empleado: Optional[int] = None
    ) -> Optional[RespuestaEstudiante]:
        """Crear o actualizar una respuesta del estudiante"""
        
        # Verificar que el intento existe y está activo
        intento = db.query(IntentoExamen).filter(
            IntentoExamen.intento_id == intento_id
        ).first()
        if not intento or intento.estado.value != "en_progreso":
            return None
        
        # Obtener información de la pregunta
        pregunta = db.query(PreguntaExamen).filter(
            PreguntaExamen.pregunta_id == pregunta_id
        ).first()
        if not pregunta:
            return None
        
        # Buscar respuesta existente
        respuesta_existente = db.query(RespuestaEstudiante).filter(
            and_(
                RespuestaEstudiante.intento_id == intento_id,
                RespuestaEstudiante.pregunta_id == pregunta_id
            )
        ).first()
        
        if respuesta_existente:
            # Actualizar respuesta existente
            return self._actualizar_respuesta_existente(
                db, respuesta_existente, respuesta_datos, pregunta, tiempo_empleado
            )
        else:
            # Crear nueva respuesta
            return self._crear_nueva_respuesta(
                db, intento_id, pregunta_id, respuesta_datos, pregunta, tiempo_empleado
            )
    
    def _crear_nueva_respuesta(
        self, 
        db: Session, 
        intento_id: str,
        pregunta_id: str,
        respuesta_datos: Dict[str, Any],
        pregunta: PreguntaExamen,
        tiempo_empleado: Optional[int]
    ) -> RespuestaEstudiante:
        """Crear una nueva respuesta"""
        
        # Procesar la respuesta según el tipo de pregunta
        respuesta_procesada = self._procesar_respuesta_por_tipo(
            respuesta_datos, pregunta.tipo_pregunta
        )
        
        # Crear objeto de respuesta
        db_obj = RespuestaEstudiante(
            intento_id=intento_id,
            pregunta_id=pregunta_id,
            respuesta_estudiante=respuesta_procesada["respuesta_estudiante"],
            texto_respuesta=respuesta_procesada.get("texto_respuesta"),
            puntuacion_maxima=pregunta.puntuacion,
            tiempo_empleado_segundos=tiempo_empleado,
            fecha_respuesta=datetime.utcnow(),
            numero_modificaciones=0
        )
        
        # Calificar automáticamente si es posible
        if pregunta.tipo_pregunta in [TipoPregunta.OPCION_MULTIPLE, TipoPregunta.VERDADERO_FALSO]:
            self._calificar_automaticamente(db_obj, pregunta)
        else:
            # Para preguntas que requieren calificación manual
            db_obj.puntuacion_obtenida = 0.0
            db_obj.es_correcta = None
            db_obj.calificada_automaticamente = False
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def _actualizar_respuesta_existente(
        self, 
        db: Session, 
        respuesta: RespuestaEstudiante,
        respuesta_datos: Dict[str, Any],
        pregunta: PreguntaExamen,
        tiempo_empleado: Optional[int]
    ) -> RespuestaEstudiante:
        """Actualizar una respuesta existente"""
        
        # Guardar en historial si es necesario
        if respuesta.respuesta_estudiante != respuesta_datos:
            historial = respuesta.historial_respuestas or []
            historial.append({
                "timestamp": datetime.utcnow().isoformat(),
                "respuesta_anterior": respuesta.respuesta_estudiante,
                "texto_anterior": respuesta.texto_respuesta
            })
            respuesta.historial_respuestas = historial
            respuesta.numero_modificaciones = (respuesta.numero_modificaciones or 0) + 1
        
        # Procesar nueva respuesta
        respuesta_procesada = self._procesar_respuesta_por_tipo(
            respuesta_datos, pregunta.tipo_pregunta
        )
        
        # Actualizar campos
        respuesta.respuesta_estudiante = respuesta_procesada["respuesta_estudiante"]
        respuesta.texto_respuesta = respuesta_procesada.get("texto_respuesta")
        respuesta.fecha_ultima_modificacion = datetime.utcnow()
        
        if tiempo_empleado is not None:
            respuesta.tiempo_empleado_segundos = tiempo_empleado
        
        # Re-calificar si es necesario
        if pregunta.tipo_pregunta in [TipoPregunta.OPCION_MULTIPLE, TipoPregunta.VERDADERO_FALSO]:
            self._calificar_automaticamente(respuesta, pregunta)
        
        db.commit()
        db.refresh(respuesta)
        return respuesta
    
    def _procesar_respuesta_por_tipo(
        self, 
        respuesta_datos: Dict[str, Any], 
        tipo_pregunta: TipoPregunta
    ) -> Dict[str, Any]:
        """Procesar respuesta según el tipo de pregunta"""
        
        resultado = {}
        
        if tipo_pregunta == TipoPregunta.OPCION_MULTIPLE:
            resultado["respuesta_estudiante"] = {
                "opcion_seleccionada": respuesta_datos.get("opcion_seleccionada"),
                "opciones_multiples": respuesta_datos.get("opciones_multiples", []) if respuesta_datos.get("permite_multiple") else None
            }
        
        elif tipo_pregunta == TipoPregunta.VERDADERO_FALSO:
            resultado["respuesta_estudiante"] = {
                "respuesta": respuesta_datos.get("respuesta")  # True/False
            }
        
        elif tipo_pregunta in [TipoPregunta.ENSAYO, TipoPregunta.RESPUESTA_CORTA]:
            resultado["texto_respuesta"] = respuesta_datos.get("texto_respuesta", "").strip()
            resultado["respuesta_estudiante"] = {
                "texto": resultado["texto_respuesta"]
            }
        
        elif tipo_pregunta == TipoPregunta.COMPLETAR:
            resultado["respuesta_estudiante"] = {
                "respuestas": respuesta_datos.get("respuestas", {})  # {"hueco_1": "respuesta", ...}
            }
        
        elif tipo_pregunta == TipoPregunta.EMPAREJAMIENTO:
            resultado["respuesta_estudiante"] = {
                "emparejamientos": respuesta_datos.get("emparejamientos", {})  # {"item_1": "match_a", ...}
            }
        
        elif tipo_pregunta == TipoPregunta.ORDENAMIENTO:
            resultado["respuesta_estudiante"] = {
                "orden": respuesta_datos.get("orden", [])  # ["item_3", "item_1", "item_2", ...]
            }
        
        else:
            # Tipo no reconocido, guardar tal como viene
            resultado["respuesta_estudiante"] = respuesta_datos
            if "texto_respuesta" in respuesta_datos:
                resultado["texto_respuesta"] = respuesta_datos["texto_respuesta"]
        
        return resultado
    
    def _calificar_automaticamente(
        self, 
        respuesta: RespuestaEstudiante, 
        pregunta: PreguntaExamen
    ):
        """Calificar automáticamente una respuesta"""
        
        respuesta.calificada_automaticamente = True
        
        if pregunta.tipo_pregunta == TipoPregunta.OPCION_MULTIPLE:
            self._calificar_opcion_multiple(respuesta, pregunta)
        
        elif pregunta.tipo_pregunta == TipoPregunta.VERDADERO_FALSO:
            self._calificar_verdadero_falso(respuesta, pregunta)
        
        elif pregunta.tipo_pregunta == TipoPregunta.COMPLETAR:
            self._calificar_completar(respuesta, pregunta)
        
        elif pregunta.tipo_pregunta == TipoPregunta.EMPAREJAMIENTO:
            self._calificar_emparejamiento(respuesta, pregunta)
        
        elif pregunta.tipo_pregunta == TipoPregunta.ORDENAMIENTO:
            self._calificar_ordenamiento(respuesta, pregunta)
        
        # Generar feedback automático
        self._generar_feedback_automatico(respuesta, pregunta)
    
    def _calificar_opcion_multiple(self, respuesta: RespuestaEstudiante, pregunta: PreguntaExamen):
        """Calificar pregunta de opción múltiple"""
        if not pregunta.respuesta_correcta or not respuesta.respuesta_estudiante:
            respuesta.puntuacion_obtenida = 0.0
            respuesta.es_correcta = False
            return
        
        respuesta_correcta = pregunta.respuesta_correcta
        respuesta_estudiante = respuesta.respuesta_estudiante
        
        # Verificar si es opción múltiple con varias respuestas correctas
        if isinstance(respuesta_correcta.get("respuestas_correctas"), list):
            # Múltiples respuestas correctas
            correctas = set(respuesta_correcta["respuestas_correctas"])
            seleccionadas = set(respuesta_estudiante.get("opciones_multiples", []))
            
            if correctas == seleccionadas:
                respuesta.puntuacion_obtenida = pregunta.puntuacion
                respuesta.es_correcta = True
            elif pregunta.puntos_respuesta_parcial:
                # Puntuación parcial
                interseccion = correctas.intersection(seleccionadas)
                puntos_por_correcta = pregunta.puntuacion / len(correctas)
                puntos_por_incorrecta = puntos_por_correcta * 0.5  # Penalización por incorrectas
                
                puntos = (len(interseccion) * puntos_por_correcta) - (len(seleccionadas - correctas) * puntos_por_incorrecta)
                respuesta.puntuacion_obtenida = max(0, puntos)
                respuesta.es_correcta = len(interseccion) == len(correctas) and len(seleccionadas) == len(correctas)
            else:
                respuesta.puntuacion_obtenida = 0.0
                respuesta.es_correcta = False
        else:
            # Una sola respuesta correcta
            opcion_correcta = respuesta_correcta.get("opcion_correcta")
            opcion_seleccionada = respuesta_estudiante.get("opcion_seleccionada")
            
            if opcion_correcta == opcion_seleccionada:
                respuesta.puntuacion_obtenida = pregunta.puntuacion
                respuesta.es_correcta = True
            else:
                respuesta.puntuacion_obtenida = 0.0
                respuesta.es_correcta = False
    
    def _calificar_verdadero_falso(self, respuesta: RespuestaEstudiante, pregunta: PreguntaExamen):
        """Calificar pregunta de verdadero/falso"""
        if not pregunta.respuesta_correcta or not respuesta.respuesta_estudiante:
            respuesta.puntuacion_obtenida = 0.0
            respuesta.es_correcta = False
            return
        
        respuesta_correcta = pregunta.respuesta_correcta.get("respuesta")
        respuesta_estudiante = respuesta.respuesta_estudiante.get("respuesta")
        
        if respuesta_correcta == respuesta_estudiante:
            respuesta.puntuacion_obtenida = pregunta.puntuacion
            respuesta.es_correcta = True
        else:
            respuesta.puntuacion_obtenida = 0.0
            respuesta.es_correcta = False
    
    def _calificar_completar(self, respuesta: RespuestaEstudiante, pregunta: PreguntaExamen):
        """Calificar pregunta de completar espacios"""
        if not pregunta.respuesta_correcta or not respuesta.respuesta_estudiante:
            respuesta.puntuacion_obtenida = 0.0
            respuesta.es_correcta = False
            return
        
        respuestas_correctas = pregunta.respuesta_correcta.get("respuestas", {})
        respuestas_estudiante = respuesta.respuesta_estudiante.get("respuestas", {})
        
        total_huecos = len(respuestas_correctas)
        huecos_correctos = 0
        
        for hueco, respuesta_correcta in respuestas_correctas.items():
            respuesta_est = respuestas_estudiante.get(hueco, "").strip().lower()
            
            # Permitir múltiples respuestas correctas separadas por |
            opciones_correctas = [opt.strip().lower() for opt in str(respuesta_correcta).split("|")]
            
            if respuesta_est in opciones_correctas:
                huecos_correctos += 1
        
        if pregunta.puntos_respuesta_parcial and total_huecos > 0:
            proporcion = huecos_correctos / total_huecos
            respuesta.puntuacion_obtenida = pregunta.puntuacion * proporcion
            respuesta.es_correcta = huecos_correctos == total_huecos
        else:
            if huecos_correctos == total_huecos:
                respuesta.puntuacion_obtenida = pregunta.puntuacion
                respuesta.es_correcta = True
            else:
                respuesta.puntuacion_obtenida = 0.0
                respuesta.es_correcta = False
    
    def _calificar_emparejamiento(self, respuesta: RespuestaEstudiante, pregunta: PreguntaExamen):
        """Calificar pregunta de emparejamiento"""
        if not pregunta.respuesta_correcta or not respuesta.respuesta_estudiante:
            respuesta.puntuacion_obtenida = 0.0
            respuesta.es_correcta = False
            return
        
        emparejamientos_correctos = pregunta.respuesta_correcta.get("emparejamientos", {})
        emparejamientos_estudiante = respuesta.respuesta_estudiante.get("emparejamientos", {})
        
        total_emparejamientos = len(emparejamientos_correctos)
        emparejamientos_correctos_count = 0
        
        for item, match_correcto in emparejamientos_correctos.items():
            match_estudiante = emparejamientos_estudiante.get(item)
            if match_correcto == match_estudiante:
                emparejamientos_correctos_count += 1
        
        if pregunta.puntos_respuesta_parcial and total_emparejamientos > 0:
            proporcion = emparejamientos_correctos_count / total_emparejamientos
            respuesta.puntuacion_obtenida = pregunta.puntuacion * proporcion
            respuesta.es_correcta = emparejamientos_correctos_count == total_emparejamientos
        else:
            if emparejamientos_correctos_count == total_emparejamientos:
                respuesta.puntuacion_obtenida = pregunta.puntuacion
                respuesta.es_correcta = True
            else:
                respuesta.puntuacion_obtenida = 0.0
                respuesta.es_correcta = False
    
    def _calificar_ordenamiento(self, respuesta: RespuestaEstudiante, pregunta: PreguntaExamen):
        """Calificar pregunta de ordenamiento"""
        if not pregunta.respuesta_correcta or not respuesta.respuesta_estudiante:
            respuesta.puntuacion_obtenida = 0.0
            respuesta.es_correcta = False
            return
        
        orden_correcto = pregunta.respuesta_correcta.get("orden", [])
        orden_estudiante = respuesta.respuesta_estudiante.get("orden", [])
        
        if orden_correcto == orden_estudiante:
            respuesta.puntuacion_obtenida = pregunta.puntuacion
            respuesta.es_correcta = True
        elif pregunta.puntos_respuesta_parcial:
            # Calcular puntuación basada en posiciones correctas
            posiciones_correctas = 0
            total_items = len(orden_correcto)
            
            for i, item in enumerate(orden_correcto):
                if i < len(orden_estudiante) and orden_estudiante[i] == item:
                    posiciones_correctas += 1
            
            if total_items > 0:
                proporcion = posiciones_correctas / total_items
                respuesta.puntuacion_obtenida = pregunta.puntuacion * proporcion
                respuesta.es_correcta = posiciones_correctas == total_items
            else:
                respuesta.puntuacion_obtenida = 0.0
                respuesta.es_correcta = False
        else:
            respuesta.puntuacion_obtenida = 0.0
            respuesta.es_correcta = False
    
    def _generar_feedback_automatico(self, respuesta: RespuestaEstudiante, pregunta: PreguntaExamen):
        """Generar feedback automático basado en la respuesta"""
        feedback = []
        
        if respuesta.es_correcta:
            feedback.append("¡Correcto! ")
            if pregunta.explicacion:
                feedback.append(f"Explicación: {pregunta.explicacion}")
        else:
            feedback.append("Incorrecto. ")
            if pregunta.explicacion:
                feedback.append(f"Explicación: {pregunta.explicacion}")
        
        # Feedback específico por tipo de pregunta
        if pregunta.tipo_pregunta == TipoPregunta.OPCION_MULTIPLE and pregunta.respuesta_correcta:
            if not respuesta.es_correcta:
                respuesta_correcta = pregunta.respuesta_correcta.get("opcion_correcta")
                if respuesta_correcta:
                    feedback.append(f"La respuesta correcta era: {respuesta_correcta}")
        
        respuesta.feedback_automatico = " ".join(feedback) if feedback else None
    
    def calificar_manualmente(
        self, 
        db: Session, 
        respuesta_id: str,
        puntuacion: float,
        feedback_profesor: Optional[str] = None,
        profesor_id: str = None
    ) -> Optional[RespuestaEstudiante]:
        """Calificar manualmente una respuesta (para ensayos, etc.)"""
        respuesta = self.get(db=db, id=respuesta_id)
        if not respuesta:
            return None
        
        # Obtener la pregunta para verificar puntuación máxima
        pregunta = db.query(PreguntaExamen).filter(
            PreguntaExamen.pregunta_id == respuesta.pregunta_id
        ).first()
        
        if not pregunta:
            return None
        
        # Validar puntuación
        if puntuacion < 0 or puntuacion > pregunta.puntuacion:
            raise ValueError(f"La puntuación debe estar entre 0 y {pregunta.puntuacion}")
        
        # Actualizar respuesta
        respuesta.puntuacion_obtenida = puntuacion
        respuesta.es_correcta = puntuacion >= (pregunta.puntuacion * 0.6)  # 60% como mínimo para considerar correcta
        respuesta.calificada_automaticamente = False
        respuesta.feedback_profesor = feedback_profesor
        respuesta.fecha_ultima_modificacion = datetime.utcnow()
        
        db.commit()
        db.refresh(respuesta)
        
        # Recalcular calificación del intento
        self._recalcular_calificacion_intento(db, respuesta.intento_id)
        
        return respuesta
    
    def calificar_ensayo_automatico(
        self, 
        db: Session, 
        respuesta_id: str,
        palabras_clave: List[str],
        peso_palabras_clave: float = 0.7
    ) -> Optional[RespuestaEstudiante]:
        """Calificación automática básica para ensayos basada en palabras clave"""
        respuesta = self.get(db=db, id=respuesta_id)
        if not respuesta or not respuesta.texto_respuesta:
            return None
        
        pregunta = db.query(PreguntaExamen).filter(
            PreguntaExamen.pregunta_id == respuesta.pregunta_id
        ).first()
        
        if not pregunta:
            return None
        
        texto = respuesta.texto_respuesta.lower()
        palabras_encontradas = []
        
        for palabra in palabras_clave:
            if palabra.lower() in texto:
                palabras_encontradas.append(palabra)
        
        # Calcular puntuación basada en palabras clave encontradas
        if palabras_clave:
            proporcion_palabras = len(palabras_encontradas) / len(palabras_clave)
        else:
            proporcion_palabras = 0
        
        # Calcular longitud del texto (factor adicional)
        longitud_minima = 50  # caracteres mínimos esperados
        longitud_texto = len(respuesta.texto_respuesta)
        factor_longitud = min(longitud_texto / longitud_minima, 1.0) if longitud_minima > 0 else 1.0
        
        # Puntuación final
        puntuacion_final = pregunta.puntuacion * (
            (proporcion_palabras * peso_palabras_clave) + 
            (factor_longitud * (1 - peso_palabras_clave))
        )
        
        respuesta.puntuacion_obtenida = round(puntuacion_final, 2)
        respuesta.es_correcta = respuesta.puntuacion_obtenida >= (pregunta.puntuacion * 0.6)
        respuesta.calificada_automaticamente = True
        respuesta.palabras_clave_encontradas = palabras_encontradas
        respuesta.feedback_automatico = f"Se encontraron {len(palabras_encontradas)} de {len(palabras_clave)} palabras clave esperadas."
        
        db.commit()
        db.refresh(respuesta)
        
        return respuesta
    
    def get_respuestas_por_intento(
        self, 
        db: Session, 
        intento_id: str,
        incluir_pregunta: bool = False
    ) -> List[RespuestaEstudiante]:
        """Obtener todas las respuestas de un intento"""
        query = db.query(RespuestaEstudiante).filter(
            RespuestaEstudiante.intento_id == intento_id
        )
        
        if incluir_pregunta:
            query = query.options(joinedload(RespuestaEstudiante.pregunta))
        
        return query.order_by(RespuestaEstudiante.fecha_respuesta).all()
    
    def get_respuestas_por_pregunta(
        self, 
        db: Session, 
        pregunta_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[RespuestaEstudiante]:
        """Obtener todas las respuestas a una pregunta específica"""
        return db.query(RespuestaEstudiante).filter(
            RespuestaEstudiante.pregunta_id == pregunta_id
        ).order_by(desc(RespuestaEstudiante.fecha_respuesta)).offset(skip).limit(limit).all()
    
    def get_respuestas_pendientes_calificacion(
        self, 
        db: Session, 
        profesor_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[RespuestaEstudiante]:
        """Obtener respuestas pendientes de calificación manual"""
        # Obtener respuestas de preguntas tipo ensayo o respuesta corta
        return db.query(RespuestaEstudiante).join(
            PreguntaExamen, RespuestaEstudiante.pregunta_id == PreguntaExamen.pregunta_id
        ).join(
            IntentoExamen, RespuestaEstudiante.intento_id == IntentoExamen.intento_id
        ).filter(
            and_(
                PreguntaExamen.tipo_pregunta.in_([TipoPregunta.ENSAYO, TipoPregunta.RESPUESTA_CORTA]),
                RespuestaEstudiante.calificada_automaticamente == False,
                RespuestaEstudiante.feedback_profesor.is_(None),
                IntentoExamen.estado.in_(["finalizado", "tiempo_agotado"])
            )
        ).order_by(asc(RespuestaEstudiante.fecha_respuesta)).offset(skip).limit(limit).all()
    
    def _recalcular_calificacion_intento(self, db: Session, intento_id: str):
        """Recalcular la calificación total del intento después de calificar manualmente"""
        from src.crud.evaluaciones.crud_intento import intento_examen
        
        intento = db.query(IntentoExamen).filter(
            IntentoExamen.intento_id == intento_id
        ).first()
        
        if not intento:
            return
        
        # Recalcular puntuación total
        respuestas = self.get_respuestas_por_intento(db, intento_id)
        puntuacion_total = sum(r.puntuacion_obtenida for r in respuestas)
        
        intento.puntuacion_obtenida = puntuacion_total
        
        if intento.puntuacion_maxima > 0:
            intento.porcentaje = round((puntuacion_total / intento.puntuacion_maxima) * 100, 2)
        
        # Verificar aprobación
        examen = db.query(PreguntaExamen).filter(
            PreguntaExamen.pregunta_id == respuestas[0].pregunta_id if respuestas else None
        ).first()
        
        if examen:
            from src.models.evaluaciones import Examen
            examen_obj = db.query(Examen).filter(Examen.examen_id == intento.examen_id).first()
            if examen_obj:
                intento.aprobado = intento.porcentaje >= examen_obj.puntuacion_minima_aprobacion
        
        db.commit()
        db.refresh(intento)


# Instancia del CRUD
respuesta_estudiante = CRUDRespuestaEstudiante(RespuestaEstudiante)