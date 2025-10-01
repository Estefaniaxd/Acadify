"""
Servicio de estadísticas y análisis para el sistema de evaluaciones
Genera métricas, reportes y análisis de rendimiento
"""

from typing import Dict, List, Any, Optional, Tuple
import statistics
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case, desc, asc
import json

from src.models.evaluaciones import (
    Examen, PreguntaExamen, IntentoExamen, RespuestaEstudiante,
    EstadisticaExamen, TipoExamen, EstadoExamen, TipoPregunta,
    DificultadPregunta, EstadoIntento
)
from src.models.users import User
from src.models.classes import Clase


class ServicioEstadisticas:
    """Servicio para generar estadísticas y análisis del sistema de evaluaciones"""
    
    def __init__(self):
        self.metricas_basicas = [
            "promedio_calificaciones",
            "mediana_calificaciones", 
            "desviacion_estandar",
            "tasa_aprobacion",
            "tiempo_promedio_resolucion"
        ]
        
        self.dificultades_orden = {
            DificultadPregunta.MUY_FACIL: 1,
            DificultadPregunta.FACIL: 2,
            DificultadPregunta.MEDIO: 3,
            DificultadPregunta.DIFICIL: 4,
            DificultadPregunta.MUY_DIFICIL: 5
        }
    
    def generar_estadisticas_examen(
        self,
        db: Session,
        examen_id: int,
        incluir_intentos_incompletos: bool = False
    ) -> Dict[str, Any]:
        """Generar estadísticas completas para un examen específico"""
        examen = db.query(Examen).filter(Examen.examen_id == examen_id).first()
        if not examen:
            return {"error": "Examen no encontrado"}
        
        # Filtro de intentos
        query_intentos = db.query(IntentoExamen).filter(
            IntentoExamen.examen_id == examen_id
        )
        
        if not incluir_intentos_incompletos:
            query_intentos = query_intentos.filter(
                IntentoExamen.estado_intento == EstadoIntento.FINALIZADO
            )
        
        intentos = query_intentos.all()
        
        if not intentos:
            return {
                "examen_id": examen_id,
                "titulo_examen": examen.titulo,
                "total_intentos": 0,
                "mensaje": "No hay intentos completados para analizar"
            }
        
        # Obtener preguntas del examen
        preguntas = db.query(PreguntaExamen).filter(
            PreguntaExamen.examen_id == examen_id
        ).all()
        
        # Calcular estadísticas básicas
        estadisticas = {
            "examen_info": {
                "examen_id": examen_id,
                "titulo": examen.titulo,
                "descripcion": examen.descripcion,
                "tipo_examen": examen.tipo_examen.value,
                "puntuacion_maxima": examen.puntuacion_total,
                "tiempo_limite_minutos": examen.tiempo_limite,
                "fecha_creacion": examen.fecha_creacion.isoformat()
            },
            
            "metricas_generales": self._calcular_metricas_generales(intentos, examen.puntuacion_total),
            "distribucion_calificaciones": self._calcular_distribucion_calificaciones(intentos, examen.puntuacion_total),
            "analisis_temporal": self._analizar_tiempos_resolucion(intentos),
            "analisis_preguntas": self._analizar_preguntas_detalle(db, preguntas, examen_id),
            "rendimiento_por_estudiante": self._analizar_rendimiento_estudiantes(db, intentos),
            "comparacion_grupos": self._comparar_grupos_rendimiento(db, intentos),
            
            # Metadatos del análisis
            "metadata": {
                "fecha_analisis": datetime.utcnow().isoformat(),
                "total_intentos_analizados": len(intentos),
                "incluye_intentos_incompletos": incluir_intentos_incompletos
            }
        }
        
        # Guardar estadísticas en la base de datos
        self._guardar_estadisticas_examen(db, examen_id, estadisticas)
        
        return estadisticas
    
    def generar_reporte_clase(
        self,
        db: Session,
        clase_id: int,
        periodo_inicio: Optional[datetime] = None,
        periodo_fin: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generar reporte de rendimiento para una clase completa"""
        clase = db.query(Clase).filter(Clase.clase_id == clase_id).first()
        if not clase:
            return {"error": "Clase no encontrada"}
        
        # Configurar período de análisis
        if not periodo_inicio:
            periodo_inicio = datetime.utcnow() - timedelta(days=90)  # Últimos 3 meses
        if not periodo_fin:
            periodo_fin = datetime.utcnow()
        
        # Obtener exámenes de la clase en el período
        examenes_query = db.query(Examen).filter(
            and_(
                Examen.clase_id == clase_id,
                Examen.fecha_creacion >= periodo_inicio,
                Examen.fecha_creacion <= periodo_fin
            )
        )
        examenes = examenes_query.all()
        
        if not examenes:
            return {
                "clase_id": clase_id,
                "nombre_clase": clase.nombre,
                "mensaje": "No hay exámenes en el período especificado"
            }
        
        # Análisis por examen
        analisis_examenes = []
        for examen in examenes:
            stats_examen = self.generar_estadisticas_examen(db, examen.examen_id, incluir_intentos_incompletos=False)
            if "error" not in stats_examen:
                analisis_examenes.append({
                    "examen_id": examen.examen_id,
                    "titulo": examen.titulo,
                    "fecha": examen.fecha_creacion.isoformat(),
                    "promedio_clase": stats_examen["metricas_generales"]["promedio_calificaciones"],
                    "tasa_aprobacion": stats_examen["metricas_generales"]["tasa_aprobacion"],
                    "total_intentos": stats_examen["metadata"]["total_intentos_analizados"]
                })
        
        # Obtener todos los intentos de la clase en el período
        intentos_clase = db.query(IntentoExamen).join(Examen).filter(
            and_(
                Examen.clase_id == clase_id,
                Examen.fecha_creacion >= periodo_inicio,
                Examen.fecha_creacion <= periodo_fin,
                IntentoExamen.estado_intento == EstadoIntento.FINALIZADO
            )
        ).all()
        
        reporte = {
            "clase_info": {
                "clase_id": clase_id,
                "nombre_clase": clase.nombre,
                "codigo_clase": clase.codigo,
                "periodo_analisis": {
                    "inicio": periodo_inicio.isoformat(),
                    "fin": periodo_fin.isoformat()
                }
            },
            
            "resumen_ejecutivo": self._generar_resumen_ejecutivo_clase(examenes, intentos_clase),
            "tendencias_rendimiento": self._analizar_tendencias_clase(analisis_examenes),
            "estudiantes_destacados": self._identificar_estudiantes_destacados(db, intentos_clase),
            "estudiantes_en_riesgo": self._identificar_estudiantes_riesgo(db, intentos_clase),
            "analisis_por_examen": analisis_examenes,
            "recomendaciones": self._generar_recomendaciones_clase(intentos_clase, analisis_examenes),
            
            "metadata": {
                "fecha_reporte": datetime.utcnow().isoformat(),
                "total_examenes": len(examenes),
                "total_intentos": len(intentos_clase)
            }
        }
        
        return reporte
    
    def analizar_pregunta_detallada(
        self,
        db: Session,
        pregunta_id: int
    ) -> Dict[str, Any]:
        """Análisis detallado de una pregunta específica"""
        pregunta = db.query(PreguntaExamen).filter(
            PreguntaExamen.pregunta_id == pregunta_id
        ).first()
        
        if not pregunta:
            return {"error": "Pregunta no encontrada"}
        
        # Obtener todas las respuestas a esta pregunta
        respuestas = db.query(RespuestaEstudiante).filter(
            RespuestaEstudiante.pregunta_id == pregunta_id
        ).all()
        
        if not respuestas:
            return {
                "pregunta_id": pregunta_id,
                "mensaje": "No hay respuestas para analizar"
            }
        
        analisis = {
            "pregunta_info": {
                "pregunta_id": pregunta_id,
                "texto_pregunta": pregunta.texto_pregunta,
                "tipo_pregunta": pregunta.tipo_pregunta.value,
                "dificultad": pregunta.dificultad.value,
                "puntuacion_maxima": pregunta.puntuacion,
                "orden_presentacion": pregunta.orden
            },
            
            "estadisticas_respuestas": self._analizar_respuestas_pregunta(respuestas, pregunta),
            "analisis_dificultad": self._evaluar_dificultad_real(respuestas, pregunta),
            "patrones_respuestas_incorrectas": self._analizar_errores_comunes(respuestas, pregunta),
            "discriminacion": self._calcular_discriminacion_pregunta(db, pregunta, respuestas),
            "recomendaciones_mejora": self._generar_recomendaciones_pregunta(respuestas, pregunta)
        }
        
        return analisis
    
    def generar_dashboard_profesor(
        self,
        db: Session,
        profesor_id: int,
        periodo_dias: int = 30
    ) -> Dict[str, Any]:
        """Generar dashboard con métricas para el profesor"""
        fecha_inicio = datetime.utcnow() - timedelta(days=periodo_dias)
        
        # Obtener exámenes del profesor
        examenes_profesor = db.query(Examen).filter(
            and_(
                Examen.creado_por == profesor_id,
                Examen.fecha_creacion >= fecha_inicio
            )
        ).all()
        
        if not examenes_profesor:
            return {
                "mensaje": "No hay exámenes en el período especificado",
                "periodo_dias": periodo_dias
            }
        
        # Calcular métricas del dashboard
        total_intentos = 0
        calificaciones_todas = []
        examenes_activos = 0
        
        for examen in examenes_profesor:
            if examen.estado_examen == EstadoExamen.ACTIVO:
                examenes_activos += 1
            
            intentos = db.query(IntentoExamen).filter(
                and_(
                    IntentoExamen.examen_id == examen.examen_id,
                    IntentoExamen.estado_intento == EstadoIntento.FINALIZADO
                )
            ).all()
            
            total_intentos += len(intentos)
            calificaciones_todas.extend([i.puntuacion_obtenida for i in intentos if i.puntuacion_obtenida is not None])
        
        dashboard = {
            "resumen_periodo": {
                "periodo_dias": periodo_dias,
                "fecha_inicio": fecha_inicio.isoformat(),
                "total_examenes": len(examenes_profesor),
                "examenes_activos": examenes_activos,
                "total_intentos": total_intentos,
                "promedio_general": round(statistics.mean(calificaciones_todas), 2) if calificaciones_todas else 0
            },
            
            "examenes_recientes": [
                {
                    "examen_id": e.examen_id,
                    "titulo": e.titulo,
                    "fecha_creacion": e.fecha_creacion.isoformat(),
                    "estado": e.estado_examen.value,
                    "tipo": e.tipo_examen.value,
                    "intentos_completados": db.query(IntentoExamen).filter(
                        and_(
                            IntentoExamen.examen_id == e.examen_id,
                            IntentoExamen.estado_intento == EstadoIntento.FINALIZADO
                        )
                    ).count()
                }
                for e in sorted(examenes_profesor, key=lambda x: x.fecha_creacion, reverse=True)[:5]
            ],
            
            "alertas_atencion": self._generar_alertas_profesor(db, examenes_profesor),
            "metricas_rapidas": self._calcular_metricas_rapidas_profesor(db, examenes_profesor)
        }
        
        return dashboard
    
    def exportar_estadisticas(
        self,
        db: Session,
        examen_id: int,
        formato: str = "json"
    ) -> Dict[str, Any]:
        """Exportar estadísticas en diferentes formatos"""
        estadisticas = self.generar_estadisticas_examen(db, examen_id)
        
        if formato.lower() == "csv":
            return self._convertir_a_csv(estadisticas)
        elif formato.lower() == "excel":
            return self._preparar_excel(estadisticas)
        else:
            return estadisticas
    
    # Métodos auxiliares privados
    
    def _calcular_metricas_generales(self, intentos: List[IntentoExamen], puntuacion_maxima: float) -> Dict[str, Any]:
        """Calcular métricas estadísticas básicas"""
        calificaciones = [i.puntuacion_obtenida for i in intentos if i.puntuacion_obtenida is not None]
        tiempos = [
            (i.fecha_finalizacion - i.fecha_inicio).seconds // 60 
            for i in intentos 
            if i.fecha_finalizacion
        ]
        
        if not calificaciones:
            return {"error": "No hay calificaciones para calcular"}
        
        umbral_aprobacion = puntuacion_maxima * 0.6  # 60% para aprobar
        aprobados = len([c for c in calificaciones if c >= umbral_aprobacion])
        
        return {
            "total_intentos": len(intentos),
            "promedio_calificaciones": round(statistics.mean(calificaciones), 2),
            "mediana_calificaciones": round(statistics.median(calificaciones), 2),
            "desviacion_estandar": round(statistics.stdev(calificaciones) if len(calificaciones) > 1 else 0, 2),
            "calificacion_minima": min(calificaciones),
            "calificacion_maxima": max(calificaciones),
            "tasa_aprobacion": round((aprobados / len(calificaciones)) * 100, 2),
            "tiempo_promedio_minutos": round(statistics.mean(tiempos), 2) if tiempos else 0,
            "tiempo_mediano_minutos": round(statistics.median(tiempos), 2) if tiempos else 0
        }
    
    def _calcular_distribucion_calificaciones(self, intentos: List[IntentoExamen], puntuacion_maxima: float) -> Dict[str, Any]:
        """Calcular distribución de calificaciones por rangos"""
        calificaciones = [i.puntuacion_obtenida for i in intentos if i.puntuacion_obtenida is not None]
        
        if not calificaciones:
            return {}
        
        # Definir rangos de calificaciones
        rangos = {
            "0-20%": 0,
            "21-40%": 0,
            "41-60%": 0,
            "61-80%": 0,
            "81-100%": 0
        }
        
        for calificacion in calificaciones:
            porcentaje = (calificacion / puntuacion_maxima) * 100
            
            if porcentaje <= 20:
                rangos["0-20%"] += 1
            elif porcentaje <= 40:
                rangos["21-40%"] += 1
            elif porcentaje <= 60:
                rangos["41-60%"] += 1
            elif porcentaje <= 80:
                rangos["61-80%"] += 1
            else:
                rangos["81-100%"] += 1
        
        return {
            "rangos_absolutos": rangos,
            "rangos_porcentuales": {
                rango: round((cantidad / len(calificaciones)) * 100, 2)
                for rango, cantidad in rangos.items()
            },
            "total_calificaciones": len(calificaciones)
        }
    
    def _analizar_tiempos_resolucion(self, intentos: List[IntentoExamen]) -> Dict[str, Any]:
        """Analizar patrones temporales de resolución"""
        tiempos_minutos = []
        patrones_abandono = []
        
        for intento in intentos:
            if intento.fecha_finalizacion and intento.fecha_inicio:
                tiempo = (intento.fecha_finalizacion - intento.fecha_inicio).seconds // 60
                tiempos_minutos.append(tiempo)
            elif not intento.fecha_finalizacion:
                # Intento abandonado
                tiempo_transcurrido = (datetime.utcnow() - intento.fecha_inicio).seconds // 60
                patrones_abandono.append({
                    "tiempo_antes_abandono": tiempo_transcurrido,
                    "progreso_alcanzado": intento.progreso_actual
                })
        
        if not tiempos_minutos:
            return {"mensaje": "No hay datos de tiempo para analizar"}
        
        return {
            "tiempo_promedio": round(statistics.mean(tiempos_minutos), 2),
            "tiempo_mediano": round(statistics.median(tiempos_minutos), 2),
            "tiempo_minimo": min(tiempos_minutos),
            "tiempo_maximo": max(tiempos_minutos),
            "desviacion_tiempo": round(statistics.stdev(tiempos_minutos) if len(tiempos_minutos) > 1 else 0, 2),
            "abandonos": len(patrones_abandono),
            "tasa_abandono": round((len(patrones_abandono) / len(intentos)) * 100, 2) if intentos else 0
        }
    
    def _analizar_preguntas_detalle(self, db: Session, preguntas: List[PreguntaExamen], examen_id: int) -> List[Dict[str, Any]]:
        """Analizar cada pregunta del examen en detalle"""
        analisis_preguntas = []
        
        for pregunta in preguntas:
            respuestas = db.query(RespuestaEstudiante).filter(
                RespuestaEstudiante.pregunta_id == pregunta.pregunta_id
            ).all()
            
            if not respuestas:
                continue
            
            total_respuestas = len(respuestas)
            respuestas_correctas = len([r for r in respuestas if r.es_correcta])
            puntuaciones = [r.puntuacion_obtenida for r in respuestas if r.puntuacion_obtenida is not None]
            
            analisis_pregunta = {
                "pregunta_id": pregunta.pregunta_id,
                "orden": pregunta.orden,
                "tipo": pregunta.tipo_pregunta.value,
                "dificultad_configurada": pregunta.dificultad.value,
                "puntuacion_maxima": pregunta.puntuacion,
                
                "estadisticas": {
                    "total_respuestas": total_respuestas,
                    "respuestas_correctas": respuestas_correctas,
                    "tasa_acierto": round((respuestas_correctas / total_respuestas) * 100, 2),
                    "promedio_puntuacion": round(statistics.mean(puntuaciones), 2) if puntuaciones else 0,
                    "dificultad_real": self._calcular_dificultad_real(respuestas_correctas, total_respuestas)
                },
                
                "tiempo_promedio": round(statistics.mean([
                    r.tiempo_respuesta for r in respuestas if r.tiempo_respuesta
                ]), 2) if any(r.tiempo_respuesta for r in respuestas) else 0
            }
            
            # Análisis específico por tipo de pregunta
            if pregunta.tipo_pregunta == TipoPregunta.OPCION_MULTIPLE:
                analisis_pregunta["distribucion_opciones"] = self._analizar_opciones_multiple(respuestas)
            
            analisis_preguntas.append(analisis_pregunta)
        
        return sorted(analisis_preguntas, key=lambda x: x["orden"])
    
    def _analizar_rendimiento_estudiantes(self, db: Session, intentos: List[IntentoExamen]) -> List[Dict[str, Any]]:
        """Analizar rendimiento individual de estudiantes"""
        estudiantes_rendimiento = {}
        
        for intento in intentos:
            usuario_id = intento.usuario_id
            if usuario_id not in estudiantes_rendimiento:
                # Obtener información del estudiante
                usuario = db.query(User).filter(User.user_id == usuario_id).first()
                estudiantes_rendimiento[usuario_id] = {
                    "usuario_id": usuario_id,
                    "nombre": f"{usuario.first_name} {usuario.last_name}" if usuario else "Usuario desconocido",
                    "intentos": [],
                    "mejor_puntuacion": 0,
                    "promedio": 0,
                    "total_intentos": 0
                }
            
            if intento.puntuacion_obtenida is not None:
                estudiantes_rendimiento[usuario_id]["intentos"].append({
                    "intento_id": intento.intento_id,
                    "puntuacion": intento.puntuacion_obtenida,
                    "fecha": intento.fecha_inicio.isoformat(),
                    "tiempo_minutos": (
                        (intento.fecha_finalizacion - intento.fecha_inicio).seconds // 60
                        if intento.fecha_finalizacion else 0
                    )
                })
        
        # Calcular estadísticas por estudiante
        for usuario_id, datos in estudiantes_rendimiento.items():
            puntuaciones = [i["puntuacion"] for i in datos["intentos"]]
            if puntuaciones:
                datos["mejor_puntuacion"] = max(puntuaciones)
                datos["promedio"] = round(statistics.mean(puntuaciones), 2)
                datos["total_intentos"] = len(puntuaciones)
        
        return list(estudiantes_rendimiento.values())
    
    def _comparar_grupos_rendimiento(self, db: Session, intentos: List[IntentoExamen]) -> Dict[str, Any]:
        """Comparar rendimiento entre diferentes grupos"""
        # Para simplificar, comparamos por cuartiles de rendimiento
        calificaciones = [i.puntuacion_obtenida for i in intentos if i.puntuacion_obtenida is not None]
        
        if not calificaciones:
            return {}
        
        # Calcular cuartiles
        calificaciones_ordenadas = sorted(calificaciones)
        n = len(calificaciones_ordenadas)
        
        q1_index = n // 4
        q2_index = n // 2
        q3_index = (3 * n) // 4
        
        grupos = {
            "cuartil_inferior": calificaciones_ordenadas[:q1_index],
            "cuartil_medio_bajo": calificaciones_ordenadas[q1_index:q2_index],
            "cuartil_medio_alto": calificaciones_ordenadas[q2_index:q3_index],
            "cuartil_superior": calificaciones_ordenadas[q3_index:]
        }
        
        comparacion = {}
        for nombre_grupo, califs in grupos.items():
            if califs:
                comparacion[nombre_grupo] = {
                    "cantidad": len(califs),
                    "promedio": round(statistics.mean(califs), 2),
                    "rango_min": min(califs),
                    "rango_max": max(califs)
                }
        
        return comparacion
    
    def _analizar_respuestas_pregunta(self, respuestas: List[RespuestaEstudiante], pregunta: PreguntaExamen) -> Dict[str, Any]:
        """Analizar estadísticas de respuestas para una pregunta"""
        total = len(respuestas)
        correctas = len([r for r in respuestas if r.es_correcta])
        
        estadisticas = {
            "total_respuestas": total,
            "respuestas_correctas": correctas,
            "respuestas_incorrectas": total - correctas,
            "tasa_acierto": round((correctas / total) * 100, 2),
            "tasa_error": round(((total - correctas) / total) * 100, 2)
        }
        
        # Análisis de puntuaciones
        puntuaciones = [r.puntuacion_obtenida for r in respuestas if r.puntuacion_obtenida is not None]
        if puntuaciones:
            estadisticas.update({
                "promedio_puntuacion": round(statistics.mean(puntuaciones), 2),
                "mediana_puntuacion": round(statistics.median(puntuaciones), 2),
                "puntuacion_maxima_obtenida": max(puntuaciones),
                "puntuacion_minima_obtenida": min(puntuaciones)
            })
        
        # Análisis de tiempos
        tiempos = [r.tiempo_respuesta for r in respuestas if r.tiempo_respuesta]
        if tiempos:
            estadisticas.update({
                "tiempo_promedio_segundos": round(statistics.mean(tiempos), 2),
                "tiempo_mediano_segundos": round(statistics.median(tiempos), 2),
                "tiempo_minimo_segundos": min(tiempos),
                "tiempo_maximo_segundos": max(tiempos)
            })
        
        return estadisticas
    
    def _evaluar_dificultad_real(self, respuestas: List[RespuestaEstudiante], pregunta: PreguntaExamen) -> Dict[str, Any]:
        """Evaluar la dificultad real basada en el rendimiento"""
        total = len(respuestas)
        correctas = len([r for r in respuestas if r.es_correcta])
        
        if total == 0:
            return {}
        
        tasa_acierto = correctas / total
        
        # Clasificar dificultad real
        if tasa_acierto >= 0.8:
            dificultad_real = "MUY_FACIL"
        elif tasa_acierto >= 0.6:
            dificultad_real = "FACIL"
        elif tasa_acierto >= 0.4:
            dificultad_real = "MEDIO"
        elif tasa_acierto >= 0.2:
            dificultad_real = "DIFICIL"
        else:
            dificultad_real = "MUY_DIFICIL"
        
        return {
            "dificultad_configurada": pregunta.dificultad.value,
            "dificultad_real": dificultad_real,
            "tasa_acierto": round(tasa_acierto * 100, 2),
            "coincide_configuracion": pregunta.dificultad.value == dificultad_real,
            "recomendacion": self._recomendar_ajuste_dificultad(pregunta.dificultad.value, dificultad_real)
        }
    
    def _analizar_errores_comunes(self, respuestas: List[RespuestaEstudiante], pregunta: PreguntaExamen) -> Dict[str, Any]:
        """Analizar patrones en respuestas incorrectas"""
        respuestas_incorrectas = [r for r in respuestas if not r.es_correcta]
        
        if not respuestas_incorrectas:
            return {"mensaje": "No hay respuestas incorrectas para analizar"}
        
        # Para preguntas de opción múltiple, analizar opciones incorrectas más frecuentes
        if pregunta.tipo_pregunta == TipoPregunta.OPCION_MULTIPLE:
            opciones_incorrectas = {}
            for respuesta in respuestas_incorrectas:
                if respuesta.respuesta_estudiante and "opcion_seleccionada" in respuesta.respuesta_estudiante:
                    opcion = respuesta.respuesta_estudiante["opcion_seleccionada"]
                    opciones_incorrectas[opcion] = opciones_incorrectas.get(opcion, 0) + 1
            
            return {
                "total_incorrectas": len(respuestas_incorrectas),
                "opciones_incorrectas_frecuentes": dict(sorted(
                    opciones_incorrectas.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )),
                "patron_principal": max(opciones_incorrectas, key=opciones_incorrectas.get) if opciones_incorrectas else None
            }
        
        # Para preguntas de texto, analizar palabras comunes en respuestas incorrectas
        elif pregunta.tipo_pregunta in [TipoPregunta.ENSAYO, TipoPregunta.RESPUESTA_CORTA]:
            palabras_frecuentes = {}
            for respuesta in respuestas_incorrectas:
                if respuesta.texto_respuesta:
                    palabras = respuesta.texto_respuesta.lower().split()
                    for palabra in palabras:
                        if len(palabra) > 3:  # Ignorar palabras muy cortas
                            palabras_frecuentes[palabra] = palabras_frecuentes.get(palabra, 0) + 1
            
            return {
                "total_incorrectas": len(respuestas_incorrectas),
                "palabras_frecuentes_incorrectas": dict(sorted(
                    palabras_frecuentes.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10])  # Top 10
            }
        
        return {
            "total_incorrectas": len(respuestas_incorrectas),
            "tipo_pregunta": pregunta.tipo_pregunta.value
        }
    
    def _calcular_discriminacion_pregunta(
        self, 
        db: Session, 
        pregunta: PreguntaExamen, 
        respuestas: List[RespuestaEstudiante]
    ) -> Dict[str, Any]:
        """Calcular índice de discriminación de la pregunta"""
        # Obtener puntuaciones totales de los intentos
        intentos_puntuaciones = {}
        for respuesta in respuestas:
            intento = db.query(IntentoExamen).filter(
                IntentoExamen.intento_id == respuesta.intento_id
            ).first()
            if intento and intento.puntuacion_obtenida is not None:
                intentos_puntuaciones[respuesta.intento_id] = intento.puntuacion_obtenida
        
        if len(intentos_puntuaciones) < 10:  # Necesitamos suficientes datos
            return {"mensaje": "Datos insuficientes para calcular discriminación"}
        
        # Dividir en grupo alto y bajo (27% superior e inferior)
        puntuaciones_ordenadas = sorted(intentos_puntuaciones.items(), key=lambda x: x[1], reverse=True)
        n_grupo = max(1, len(puntuaciones_ordenadas) // 4)  # 25% aproximadamente
        
        grupo_alto_ids = set([item[0] for item in puntuaciones_ordenadas[:n_grupo]])
        grupo_bajo_ids = set([item[0] for item in puntuaciones_ordenadas[-n_grupo:]])
        
        # Calcular aciertos en cada grupo
        aciertos_alto = len([r for r in respuestas if r.intento_id in grupo_alto_ids and r.es_correcta])
        aciertos_bajo = len([r for r in respuestas if r.intento_id in grupo_bajo_ids and r.es_correcta])
        
        # Índice de discriminación
        discriminacion = (aciertos_alto - aciertos_bajo) / n_grupo
        
        # Interpretación
        if discriminacion >= 0.4:
            interpretacion = "Excelente discriminación"
        elif discriminacion >= 0.3:
            interpretacion = "Buena discriminación"
        elif discriminacion >= 0.2:
            interpretacion = "Discriminación aceptable"
        elif discriminacion >= 0.0:
            interpretacion = "Baja discriminación"
        else:
            interpretacion = "Discriminación negativa (revisar pregunta)"
        
        return {
            "indice_discriminacion": round(discriminacion, 3),
            "interpretacion": interpretacion,
            "grupo_alto_aciertos": aciertos_alto,
            "grupo_bajo_aciertos": aciertos_bajo,
            "tamano_grupos": n_grupo
        }
    
    def _generar_recomendaciones_pregunta(
        self, 
        respuestas: List[RespuestaEstudiante], 
        pregunta: PreguntaExamen
    ) -> List[str]:
        """Generar recomendaciones para mejorar la pregunta"""
        recomendaciones = []
        
        total = len(respuestas)
        correctas = len([r for r in respuestas if r.es_correcta])
        tasa_acierto = correctas / total if total > 0 else 0
        
        # Recomendaciones basadas en tasa de acierto
        if tasa_acierto < 0.2:
            recomendaciones.append("🔴 Pregunta muy difícil - considerar revisar la redacción o reducir la dificultad")
            recomendaciones.append("📝 Verificar que la respuesta correcta esté claramente definida")
        
        elif tasa_acierto > 0.9:
            recomendaciones.append("🟢 Pregunta muy fácil - considerar aumentar la complejidad")
            recomendaciones.append("🎯 Agregar distractores más plausibles en opciones múltiples")
        
        # Recomendaciones por tipo de pregunta
        if pregunta.tipo_pregunta == TipoPregunta.OPCION_MULTIPLE:
            if tasa_acierto > 0.8:
                recomendaciones.append("⚡ Mejorar los distractores para aumentar el desafío")
        
        elif pregunta.tipo_pregunta in [TipoPregunta.ENSAYO, TipoPregunta.RESPUESTA_CORTA]:
            if tasa_acierto < 0.4:
                recomendaciones.append("📋 Considerar proporcionar más criterios de evaluación claros")
                recomendaciones.append("🔧 Revisar palabras clave y conceptos esperados")
        
        # Recomendaciones basadas en tiempo de respuesta
        tiempos = [r.tiempo_respuesta for r in respuestas if r.tiempo_respuesta]
        if tiempos:
            tiempo_promedio = statistics.mean(tiempos)
            if tiempo_promedio < 10:  # Menos de 10 segundos
                recomendaciones.append("⏱️ Respuestas muy rápidas - podría ser demasiado fácil")
            elif tiempo_promedio > 300:  # Más de 5 minutos
                recomendaciones.append("⏳ Respuestas muy lentas - considerar clarificar la pregunta")
        
        if not recomendaciones:
            recomendaciones.append("✅ Pregunta funcionando correctamente - sin ajustes necesarios")
        
        return recomendaciones
    
    def _guardar_estadisticas_examen(self, db: Session, examen_id: int, estadisticas: Dict[str, Any]):
        """Guardar estadísticas en la base de datos"""
        try:
            # Buscar registro existente
            estadistica_existente = db.query(EstadisticaExamen).filter(
                EstadisticaExamen.examen_id == examen_id
            ).first()
            
            if estadistica_existente:
                # Actualizar existente
                estadistica_existente.datos_estadisticas = estadisticas
                estadistica_existente.fecha_actualizacion = datetime.utcnow()
            else:
                # Crear nuevo registro
                nueva_estadistica = EstadisticaExamen(
                    examen_id=examen_id,
                    datos_estadisticas=estadisticas,
                    fecha_generacion=datetime.utcnow(),
                    fecha_actualizacion=datetime.utcnow()
                )
                db.add(nueva_estadistica)
            
            db.commit()
        
        except Exception as e:
            db.rollback()
            # Log del error pero no interrumpir el proceso
            print(f"Error guardando estadísticas: {e}")
    
    def _calcular_dificultad_real(self, correctas: int, total: int) -> str:
        """Calcular dificultad real basada en tasa de acierto"""
        if total == 0:
            return "INDETERMINADA"
        
        tasa = correctas / total
        
        if tasa >= 0.8:
            return "MUY_FACIL"
        elif tasa >= 0.6:
            return "FACIL"
        elif tasa >= 0.4:
            return "MEDIO"
        elif tasa >= 0.2:
            return "DIFICIL"
        else:
            return "MUY_DIFICIL"
    
    def _analizar_opciones_multiple(self, respuestas: List[RespuestaEstudiante]) -> Dict[str, Any]:
        """Analizar distribución de opciones en preguntas de opción múltiple"""
        distribucion = {}
        
        for respuesta in respuestas:
            if respuesta.respuesta_estudiante and "opcion_seleccionada" in respuesta.respuesta_estudiante:
                opcion = respuesta.respuesta_estudiante["opcion_seleccionada"]
                if opcion not in distribucion:
                    distribucion[opcion] = {"total": 0, "correctas": 0}
                
                distribucion[opcion]["total"] += 1
                if respuesta.es_correcta:
                    distribucion[opcion]["correctas"] += 1
        
        # Calcular porcentajes
        total_respuestas = sum(datos["total"] for datos in distribucion.values())
        
        for opcion, datos in distribucion.items():
            datos["porcentaje_seleccion"] = round((datos["total"] / total_respuestas) * 100, 2)
            datos["es_correcta"] = datos["correctas"] > 0
        
        return distribucion
    
    def _recomendar_ajuste_dificultad(self, dificultad_config: str, dificultad_real: str) -> str:
        """Recomendar ajustes basados en diferencia entre dificultad configurada y real"""
        config_orden = self.dificultades_orden.get(DificultadPregunta(dificultad_config), 3)
        
        real_mapping = {
            "MUY_FACIL": 1,
            "FACIL": 2, 
            "MEDIO": 3,
            "DIFICIL": 4,
            "MUY_DIFICIL": 5
        }
        real_orden = real_mapping.get(dificultad_real, 3)
        
        diferencia = real_orden - config_orden
        
        if diferencia >= 2:
            return "Considerar aumentar la dificultad configurada"
        elif diferencia <= -2:
            return "Considerar reducir la dificultad configurada"
        else:
            return "La dificultad configurada es apropiada"
    
    def _generar_resumen_ejecutivo_clase(self, examenes: List[Examen], intentos: List[IntentoExamen]) -> Dict[str, Any]:
        """Generar resumen ejecutivo para la clase"""
        if not intentos:
            return {"mensaje": "No hay datos para generar resumen"}
        
        calificaciones = [i.puntuacion_obtenida for i in intentos if i.puntuacion_obtenida is not None]
        
        return {
            "total_examenes": len(examenes),
            "total_intentos": len(intentos),
            "promedio_clase": round(statistics.mean(calificaciones), 2) if calificaciones else 0,
            "estudiantes_unicos": len(set(i.usuario_id for i in intentos)),
            "tasa_participacion": round((len(intentos) / len(examenes)) * 100, 2) if examenes else 0,
            "ultimo_examen": max([e.fecha_creacion for e in examenes]) if examenes else None
        }
    
    def _analizar_tendencias_clase(self, analisis_examenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizar tendencias de rendimiento en la clase"""
        if len(analisis_examenes) < 2:
            return {"mensaje": "Necesarios al menos 2 exámenes para analizar tendencias"}
        
        # Ordenar por fecha
        examenes_ordenados = sorted(analisis_examenes, key=lambda x: x["fecha"])
        
        promedios = [e["promedio_clase"] for e in examenes_ordenados]
        tasas_aprobacion = [e["tasa_aprobacion"] for e in examenes_ordenados]
        
        # Calcular tendencias
        mejora_promedio = promedios[-1] - promedios[0]
        mejora_aprobacion = tasas_aprobacion[-1] - tasas_aprobacion[0]
        
        return {
            "tendencia_promedio": {
                "direccion": "mejorando" if mejora_promedio > 0 else "empeorando" if mejora_promedio < 0 else "estable",
                "cambio": round(mejora_promedio, 2)
            },
            "tendencia_aprobacion": {
                "direccion": "mejorando" if mejora_aprobacion > 0 else "empeorando" if mejora_aprobacion < 0 else "estable",
                "cambio": round(mejora_aprobacion, 2)
            },
            "consistencia": round(statistics.stdev(promedios), 2) if len(promedios) > 1 else 0
        }
    
    def _identificar_estudiantes_destacados(self, db: Session, intentos: List[IntentoExamen]) -> List[Dict[str, Any]]:
        """Identificar estudiantes con rendimiento destacado"""
        rendimiento_estudiantes = {}
        
        for intento in intentos:
            if intento.puntuacion_obtenida is not None:
                usuario_id = intento.usuario_id
                if usuario_id not in rendimiento_estudiantes:
                    rendimiento_estudiantes[usuario_id] = []
                rendimiento_estudiantes[usuario_id].append(intento.puntuacion_obtenida)
        
        destacados = []
        for usuario_id, puntuaciones in rendimiento_estudiantes.items():
            if len(puntuaciones) >= 2:  # Al menos 2 exámenes
                promedio = statistics.mean(puntuaciones)
                if promedio >= 85:  # 85% o más
                    usuario = db.query(User).filter(User.user_id == usuario_id).first()
                    destacados.append({
                        "usuario_id": usuario_id,
                        "nombre": f"{usuario.first_name} {usuario.last_name}" if usuario else "Usuario desconocido",
                        "promedio": round(promedio, 2),
                        "total_examenes": len(puntuaciones),
                        "mejor_puntuacion": max(puntuaciones)
                    })
        
        return sorted(destacados, key=lambda x: x["promedio"], reverse=True)[:5]  # Top 5
    
    def _identificar_estudiantes_riesgo(self, db: Session, intentos: List[IntentoExamen]) -> List[Dict[str, Any]]:
        """Identificar estudiantes en riesgo académico"""
        rendimiento_estudiantes = {}
        
        for intento in intentos:
            if intento.puntuacion_obtenida is not None:
                usuario_id = intento.usuario_id
                if usuario_id not in rendimiento_estudiantes:
                    rendimiento_estudiantes[usuario_id] = []
                rendimiento_estudiantes[usuario_id].append(intento.puntuacion_obtenida)
        
        en_riesgo = []
        for usuario_id, puntuaciones in rendimiento_estudiantes.items():
            if len(puntuaciones) >= 2:  # Al menos 2 exámenes
                promedio = statistics.mean(puntuaciones)
                if promedio < 60:  # Menos del 60%
                    usuario = db.query(User).filter(User.user_id == usuario_id).first()
                    en_riesgo.append({
                        "usuario_id": usuario_id,
                        "nombre": f"{usuario.first_name} {usuario.last_name}" if usuario else "Usuario desconocido",
                        "promedio": round(promedio, 2),
                        "total_examenes": len(puntuaciones),
                        "peor_puntuacion": min(puntuaciones),
                        "nivel_riesgo": "alto" if promedio < 40 else "medio"
                    })
        
        return sorted(en_riesgo, key=lambda x: x["promedio"])  # Ordenar por promedio ascendente
    
    def _generar_recomendaciones_clase(self, intentos: List[IntentoExamen], analisis_examenes: List[Dict[str, Any]]) -> List[str]:
        """Generar recomendaciones para mejorar el rendimiento de la clase"""
        recomendaciones = []
        
        if not intentos or not analisis_examenes:
            return ["No hay suficientes datos para generar recomendaciones"]
        
        # Análisis general
        calificaciones = [i.puntuacion_obtenida for i in intentos if i.puntuacion_obtenida is not None]
        if calificaciones:
            promedio_general = statistics.mean(calificaciones)
            
            if promedio_general < 60:
                recomendaciones.append("🚨 Promedio de clase bajo - considerar revisar metodología de enseñanza")
                recomendaciones.append("📚 Proporcionar material de estudio adicional")
            
            elif promedio_general > 85:
                recomendaciones.append("🎯 Clase con alto rendimiento - considerar aumentar el nivel de desafío")
        
        # Análisis de participación
        if len(analisis_examenes) > 0:
            participacion_promedio = statistics.mean([e["total_intentos"] for e in analisis_examenes])
            if participacion_promedio < 50:  # Menos del 50% de participación esperada
                recomendaciones.append("📢 Baja participación - considerar estrategias para motivar a los estudiantes")
        
        # Recomendaciones específicas
        recomendaciones.extend([
            "📊 Revisar estadísticas individuales de preguntas para identificar temas problemáticos",
            "💬 Considerar feedback individual para estudiantes en riesgo",
            "🔄 Implementar sesiones de repaso para temas con bajo rendimiento"
        ])
        
        return recomendaciones
    
    def _generar_alertas_profesor(self, db: Session, examenes: List[Examen]) -> List[Dict[str, Any]]:
        """Generar alertas importantes para el profesor"""
        alertas = []
        
        for examen in examenes:
            # Verificar exámenes con pocos intentos
            intentos_count = db.query(IntentoExamen).filter(
                and_(
                    IntentoExamen.examen_id == examen.examen_id,
                    IntentoExamen.estado_intento == EstadoIntento.FINALIZADO
                )
            ).count()
            
            if intentos_count < 5 and examen.estado_examen == EstadoExamen.ACTIVO:
                alertas.append({
                    "tipo": "baja_participacion",
                    "examen_id": examen.examen_id,
                    "titulo": examen.titulo,
                    "mensaje": f"Solo {intentos_count} estudiantes han completado este examen",
                    "prioridad": "media"
                })
            
            # Verificar exámenes próximos a vencer
            if examen.fecha_limite and examen.fecha_limite <= datetime.utcnow() + timedelta(days=2):
                alertas.append({
                    "tipo": "proximo_vencimiento",
                    "examen_id": examen.examen_id,
                    "titulo": examen.titulo,
                    "mensaje": f"El examen vence el {examen.fecha_limite.strftime('%Y-%m-%d %H:%M')}",
                    "prioridad": "alta"
                })
        
        return sorted(alertas, key=lambda x: {"alta": 3, "media": 2, "baja": 1}[x["prioridad"]], reverse=True)
    
    def _calcular_metricas_rapidas_profesor(self, db: Session, examenes: List[Examen]) -> Dict[str, Any]:
        """Calcular métricas rápidas para el dashboard del profesor"""
        total_intentos = 0
        total_estudiantes = set()
        examenes_activos = 0
        
        for examen in examenes:
            if examen.estado_examen == EstadoExamen.ACTIVO:
                examenes_activos += 1
            
            intentos = db.query(IntentoExamen).filter(
                IntentoExamen.examen_id == examen.examen_id
            ).all()
            
            total_intentos += len(intentos)
            total_estudiantes.update(i.usuario_id for i in intentos)
        
        return {
            "examenes_activos": examenes_activos,
            "total_intentos_periodo": total_intentos,
            "estudiantes_activos": len(total_estudiantes),
            "promedio_intentos_por_examen": round(total_intentos / len(examenes), 1) if examenes else 0
        }
    
    def _convertir_a_csv(self, estadisticas: Dict[str, Any]) -> Dict[str, Any]:
        """Convertir estadísticas a formato preparado para CSV"""
        # Simplificado - en una implementación real se generaría CSV
        return {
            "formato": "csv",
            "datos": estadisticas,
            "mensaje": "Conversión a CSV pendiente de implementar"
        }
    
    def _preparar_excel(self, estadisticas: Dict[str, Any]) -> Dict[str, Any]:
        """Preparar estadísticas para Excel"""
        # Simplificado - en una implementación real se generaría Excel
        return {
            "formato": "excel",
            "datos": estadisticas,
            "mensaje": "Exportación a Excel pendiente de implementar"
        }


# Instancia global del servicio
servicio_estadisticas = ServicioEstadisticas()