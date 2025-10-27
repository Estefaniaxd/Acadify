"""
Servicio anti-trampa para el sistema de evaluaciones
Incluye detección de comportamientos sospechosos y monitoreo de actividad
"""

from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import ipaddress

from src.models.evaluaciones import (
    IntentoExamen, EventoAntiTrampa, TipoEvento,
    Examen, ConfiguracionEvaluaciones
)
from src.models.users import User


class DetectorAntiTrampa:
    """Servicio para detección y prevención de trampas en exámenes"""
    
    def __init__(self):
        self.eventos_sospechosos = {
            TipoEvento.CAMBIO_PESTANA: {"peso": 3, "limite_critico": 5},
            TipoEvento.CAMBIO_APLICACION: {"peso": 4, "limite_critico": 3},
            TipoEvento.CLIC_FUERA_VENTANA: {"peso": 2, "limite_critico": 10},
            TipoEvento.TIEMPO_INACTIVO: {"peso": 2, "limite_critico": 8},
            TipoEvento.PANTALLA_COMPLETA_SALIDA: {"peso": 5, "limite_critico": 2},
            TipoEvento.TECLAS_SOSPECHOSAS: {"peso": 4, "limite_critico": 5},
            TipoEvento.MULTIPLE_SESION_IP: {"peso": 6, "limite_critico": 1},
            TipoEvento.PATRON_RESPUESTA_SOSPECHOSO: {"peso": 5, "limite_critico": 3},
            TipoEvento.VELOCIDAD_RESPUESTA_ANOMALA: {"peso": 3, "limite_critico": 5}
        }
        
        self.umbrales_riesgo = {
            "bajo": 15,      # 0-15 puntos
            "medio": 35,     # 16-35 puntos
            "alto": 60,      # 36-60 puntos
            "critico": 100   # 61+ puntos
        }
    
    def registrar_evento(
        self,
        db: Session,
        intento_id: int,
        tipo_evento: TipoEvento,
        datos_evento: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> EventoAntiTrampa:
        """Registrar un evento anti-trampa"""
        evento = EventoAntiTrampa(
            intento_id=intento_id,
            tipo_evento=tipo_evento,
            descripcion=self._generar_descripcion_evento(tipo_evento, datos_evento),
            datos_evento=datos_evento,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        
        db.add(evento)
        db.commit()
        db.refresh(evento)
        
        # Verificar si este evento desencadena alertas
        self._verificar_alertas_tiempo_real(db, evento)
        
        return evento
    
    def analizar_patron_actividad(
        self,
        db: Session,
        intento_id: int,
        ventana_tiempo: int = 300  # 5 minutos
    ) -> Dict[str, Any]:
        """Analizar patrones de actividad sospechosa"""
        timestamp_limite = datetime.utcnow() - timedelta(seconds=ventana_tiempo)
        
        # Obtener eventos recientes
        eventos = db.query(EventoAntiTrampa).filter(
            and_(
                EventoAntiTrampa.intento_id == intento_id,
                EventoAntiTrampa.timestamp >= timestamp_limite
            )
        ).order_by(EventoAntiTrampa.timestamp).all()
        
        analisis = {
            "intento_id": intento_id,
            "ventana_analisis_segundos": ventana_tiempo,
            "total_eventos": len(eventos),
            "eventos_por_tipo": {},
            "puntuacion_riesgo": 0,
            "nivel_riesgo": "bajo",
            "alertas_activas": [],
            "recomendaciones": [],
            "patron_temporal": self._analizar_patron_temporal(eventos),
            "cambios_contexto": self._analizar_cambios_contexto(eventos)
        }
        
        # Contar eventos por tipo y calcular puntuación
        for evento in eventos:
            tipo = evento.tipo_evento
            if tipo not in analisis["eventos_por_tipo"]:
                analisis["eventos_por_tipo"][tipo.value] = 0
            analisis["eventos_por_tipo"][tipo.value] += 1
            
            # Agregar puntuación de riesgo
            if tipo in self.eventos_sospechosos:
                analisis["puntuacion_riesgo"] += self.eventos_sospechosos[tipo]["peso"]
        
        # Determinar nivel de riesgo
        analisis["nivel_riesgo"] = self._calcular_nivel_riesgo(analisis["puntuacion_riesgo"])
        
        # Generar alertas y recomendaciones
        analisis["alertas_activas"] = self._generar_alertas(analisis["eventos_por_tipo"])
        analisis["recomendaciones"] = self._generar_recomendaciones(analisis)
        
        return analisis
    
    def detectar_sesiones_multiples(
        self,
        db: Session,
        usuario_id: int,
        examen_id: int,
        ventana_tiempo: int = 3600  # 1 hora
    ) -> Dict[str, Any]:
        """Detectar múltiples sesiones activas del mismo usuario"""
        timestamp_limite = datetime.utcnow() - timedelta(seconds=ventana_tiempo)
        
        # Buscar intentos activos recientes del usuario para este examen
        intentos = db.query(IntentoExamen).filter(
            and_(
                IntentoExamen.usuario_id == usuario_id,
                IntentoExamen.examen_id == examen_id,
                IntentoExamen.fecha_inicio >= timestamp_limite,
                IntentoExamen.fecha_finalizacion.is_(None)  # Intentos sin finalizar
            )
        ).all()
        
        # Analizar IPs únicas
        ips_unicas = set()
        user_agents_unicos = set()
        sesiones_detalles = []
        
        for intento in intentos:
            # Obtener eventos recientes para obtener IPs
            eventos = db.query(EventoAntiTrampa).filter(
                and_(
                    EventoAntiTrampa.intento_id == intento.intento_id,
                    EventoAntiTrampa.ip_address.isnot(None)
                )
            ).order_by(EventoAntiTrampa.timestamp.desc()).limit(10).all()
            
            for evento in eventos:
                if evento.ip_address:
                    ips_unicas.add(evento.ip_address)
                if evento.user_agent:
                    user_agents_unicos.add(evento.user_agent)
            
            sesiones_detalles.append({
                "intento_id": intento.intento_id,
                "fecha_inicio": intento.fecha_inicio.isoformat(),
                "tiempo_transcurrido": (datetime.utcnow() - intento.fecha_inicio).seconds,
                "progreso": intento.progreso_actual
            })
        
        resultado = {
            "usuario_id": usuario_id,
            "examen_id": examen_id,
            "intentos_activos": len(intentos),
            "ips_unicas": len(ips_unicas),
            "user_agents_unicos": len(user_agents_unicos),
            "sesiones_detalles": sesiones_detalles,
            "sospechoso": len(intentos) > 1 or len(ips_unicas) > 1,
            "nivel_sospecha": "alto" if len(intentos) > 1 and len(ips_unicas) > 1 else "medio" if len(intentos) > 1 else "bajo"
        }
        
        # Registrar evento si es sospechoso
        if resultado["sospechoso"] and intentos:
            self.registrar_evento(
                db=db,
                intento_id=intentos[0].intento_id,
                tipo_evento=TipoEvento.MULTIPLE_SESION_IP,
                datos_evento={
                    "intentos_simultaneos": len(intentos),
                    "ips_detectadas": list(ips_unicas),
                    "user_agents": list(user_agents_unicos)[:3]  # Limitar para no sobrecargar
                }
            )
        
        return resultado
    
    def analizar_patron_respuestas(
        self,
        db: Session,
        intento_id: int,
        respuestas_recientes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analizar patrones sospechosos en las respuestas"""
        if not respuestas_recientes:
            return {"sospechoso": False, "razon": "No hay respuestas para analizar"}
        
        analisis = {
            "intento_id": intento_id,
            "total_respuestas": len(respuestas_recientes),
            "patrones_detectados": [],
            "puntuacion_sospecha": 0,
            "sospechoso": False,
            "detalles": {}
        }
        
        # Analizar velocidades de respuesta
        velocidades = []
        for i, respuesta in enumerate(respuestas_recientes):
            tiempo_respuesta = respuesta.get("tiempo_respuesta", 0)
            if tiempo_respuesta > 0:
                velocidades.append(tiempo_respuesta)
        
        if velocidades:
            velocidad_promedio = sum(velocidades) / len(velocidades)
            velocidad_min = min(velocidades)
            velocidad_max = max(velocidades)
            
            # Detectar respuestas anómalamente rápidas
            respuestas_muy_rapidas = [v for v in velocidades if v < 5]  # Menos de 5 segundos
            if len(respuestas_muy_rapidas) > len(velocidades) * 0.3:  # Más del 30% muy rápidas
                analisis["patrones_detectados"].append("respuestas_muy_rapidas")
                analisis["puntuacion_sospecha"] += 4
            
            # Detectar patrón uniforme sospechoso
            if len(set(velocidades)) == 1:  # Todas las respuestas con el mismo tiempo
                analisis["patrones_detectados"].append("tiempo_uniforme_sospechoso")
                analisis["puntuacion_sospecha"] += 5
            
            analisis["detalles"]["velocidades"] = {
                "promedio": round(velocidad_promedio, 2),
                "minima": velocidad_min,
                "maxima": velocidad_max,
                "respuestas_rapidas": len(respuestas_muy_rapidas)
            }
        
        # Analizar secuencia de respuestas correctas
        respuestas_correctas_consecutivas = 0
        max_consecutivas = 0
        
        for respuesta in respuestas_recientes:
            if respuesta.get("es_correcta", False):
                respuestas_correctas_consecutivas += 1
                max_consecutivas = max(max_consecutivas, respuestas_correctas_consecutivas)
            else:
                respuestas_correctas_consecutivas = 0
        
        # Sospechoso si tiene muchas respuestas correctas consecutivas con tiempos muy bajos
        if max_consecutivas > 5 and velocidad_promedio < 10:
            analisis["patrones_detectados"].append("precision_velocidad_anomala")
            analisis["puntuacion_sospecha"] += 6
        
        analisis["detalles"]["respuestas_correctas_max_consecutivas"] = max_consecutivas
        
        # Analizar patrón de opciones seleccionadas (para preguntas de opción múltiple)
        opciones_seleccionadas = []
        for respuesta in respuestas_recientes:
            opcion = respuesta.get("opcion_seleccionada")
            if opcion:
                opciones_seleccionadas.append(opcion)
        
        if opciones_seleccionadas:
            # Detectar patrón repetitivo (ej: A, B, C, A, B, C...)
            patron_detectado = self._detectar_patron_repetitivo(opciones_seleccionadas)
            if patron_detectado:
                analisis["patrones_detectados"].append(f"patron_repetitivo_{patron_detectado}")
                analisis["puntuacion_sospecha"] += 3
            
            analisis["detalles"]["opciones_seleccionadas"] = opciones_seleccionadas
        
        # Determinar si es sospechoso
        analisis["sospechoso"] = analisis["puntuacion_sospecha"] >= 5
        
        # Registrar evento si es sospechoso
        if analisis["sospechoso"]:
            self.registrar_evento(
                db=db,
                intento_id=intento_id,
                tipo_evento=TipoEvento.PATRON_RESPUESTA_SOSPECHOSO,
                datos_evento={
                    "patrones": analisis["patrones_detectados"],
                    "puntuacion_sospecha": analisis["puntuacion_sospecha"],
                    "detalles": analisis["detalles"]
                }
            )
        
        return analisis
    
    def generar_reporte_integridad(
        self,
        db: Session,
        intento_id: int
    ) -> Dict[str, Any]:
        """Generar reporte completo de integridad del intento"""
        # Obtener intento y examen
        intento = db.query(IntentoExamen).filter(
            IntentoExamen.intento_id == intento_id
        ).first()
        
        if not intento:
            return {"error": "Intento no encontrado"}
        
        # Obtener todos los eventos del intento
        eventos = db.query(EventoAntiTrampa).filter(
            EventoAntiTrampa.intento_id == intento_id
        ).order_by(EventoAntiTrampa.timestamp).all()
        
        # Análisis de patrones completo
        analisis_actividad = self.analizar_patron_actividad(db, intento_id, ventana_tiempo=999999)  # Todo el tiempo
        
        # Análisis de sesiones múltiples
        sesiones_multiples = self.detectar_sesiones_multiples(
            db, intento.usuario_id, intento.examen_id
        )
        
        # Calcular métricas de integridad
        total_eventos = len(eventos)
        eventos_criticos = len([e for e in eventos if e.tipo_evento in [
            TipoEvento.CAMBIO_APLICACION,
            TipoEvento.PANTALLA_COMPLETA_SALIDA,
            TipoEvento.MULTIPLE_SESION_IP
        ]])
        
        # Calcular puntuación de integridad (0-100, donde 100 es máxima integridad)
        puntuacion_integridad = max(0, 100 - analisis_actividad["puntuacion_riesgo"])
        
        # Determinar resultado final
        if puntuacion_integridad >= 80:
            resultado_integridad = "ALTA"
            recomendacion_accion = "Aprobar - Intento limpio"
        elif puntuacion_integridad >= 60:
            resultado_integridad = "MEDIA"
            recomendacion_accion = "Revisar manualmente - Posibles irregularidades menores"
        elif puntuacion_integridad >= 40:
            resultado_integridad = "BAJA"
            recomendacion_accion = "Investigar - Múltiples eventos sospechosos"
        else:
            resultado_integridad = "MUY_BAJA"
            recomendacion_accion = "Invalidar - Alto riesgo de trampa"
        
        reporte = {
            "intento_id": intento_id,
            "usuario_id": intento.usuario_id,
            "examen_id": intento.examen_id,
            "fecha_analisis": datetime.utcnow().isoformat(),
            
            # Métricas generales
            "metricas_generales": {
                "duracion_intento_minutos": (
                    (intento.fecha_finalizacion or datetime.utcnow()) - intento.fecha_inicio
                ).seconds // 60,
                "total_eventos_registrados": total_eventos,
                "eventos_criticos": eventos_criticos,
                "puntuacion_integridad": puntuacion_integridad,
                "puntuacion_riesgo": analisis_actividad["puntuacion_riesgo"]
            },
            
            # Resultado de integridad
            "resultado_integridad": resultado_integridad,
            "recomendacion_accion": recomendacion_accion,
            
            # Análisis detallados
            "analisis_actividad": analisis_actividad,
            "analisis_sesiones_multiples": sesiones_multiples,
            
            # Cronología de eventos
            "cronologia_eventos": [
                {
                    "timestamp": evento.timestamp.isoformat(),
                    "tipo": evento.tipo_evento.value,
                    "descripcion": evento.descripcion,
                    "datos": evento.datos_evento
                }
                for evento in eventos[-20:]  # Últimos 20 eventos para no sobrecargar
            ],
            
            # Resumen ejecutivo
            "resumen_ejecutivo": {
                "flags_rojas": self._generar_flags_rojas(eventos, analisis_actividad),
                "aspectos_positivos": self._generar_aspectos_positivos(analisis_actividad),
                "recomendaciones_detalladas": self._generar_recomendaciones_detalladas(
                    analisis_actividad, sesiones_multiples, puntuacion_integridad
                )
            }
        }
        
        return reporte
    
    def configurar_monitoreo_tiempo_real(
        self,
        db: Session,
        examen_id: int,
        configuracion: Dict[str, Any]
    ) -> bool:
        """Configurar parámetros de monitoreo en tiempo real para un examen"""
        try:
            # Actualizar configuración del examen
            examen = db.query(Examen).filter(Examen.examen_id == examen_id).first()
            if not examen:
                return False
            
            if not examen.configuracion_anti_trampa:
                examen.configuracion_anti_trampa = {}
            
            examen.configuracion_anti_trampa.update({
                "monitoreo_tiempo_real": configuracion.get("habilitado", True),
                "alertas_inmediatas": configuracion.get("alertas_inmediatas", True),
                "umbral_eventos_criticos": configuracion.get("umbral_eventos_criticos", 3),
                "tiempo_inactividad_max": configuracion.get("tiempo_inactividad_max", 300),
                "permitir_salida_pantalla_completa": configuracion.get("permitir_salida_pantalla_completa", False),
                "max_cambios_pestana": configuracion.get("max_cambios_pestana", 5),
                "max_cambios_aplicacion": configuracion.get("max_cambios_aplicacion", 2),
                "bloquear_clic_derecho": configuracion.get("bloquear_clic_derecho", True),
                "bloquear_teclas_especiales": configuracion.get("bloquear_teclas_especiales", True),
                "grabar_actividad": configuracion.get("grabar_actividad", False)
            })
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            return False
    
    # Métodos auxiliares privados
    
    def _generar_descripcion_evento(self, tipo_evento: TipoEvento, datos_evento: Dict[str, Any]) -> str:
        """Generar descripción legible del evento"""
        descripciones = {
            TipoEvento.CAMBIO_PESTANA: "Cambió de pestaña del navegador",
            TipoEvento.CAMBIO_APLICACION: "Cambió a otra aplicación",
            TipoEvento.CLIC_FUERA_VENTANA: "Hizo clic fuera de la ventana del examen",
            TipoEvento.TIEMPO_INACTIVO: f"Inactivo por {datos_evento.get('duracion', 0)} segundos",
            TipoEvento.PANTALLA_COMPLETA_SALIDA: "Salió del modo pantalla completa",
            TipoEvento.TECLAS_SOSPECHOSAS: f"Presionó teclas sospechosas: {datos_evento.get('teclas', 'N/A')}",
            TipoEvento.MULTIPLE_SESION_IP: f"Múltiples sesiones detectadas desde {datos_evento.get('ips_detectadas', [])}",
            TipoEvento.PATRON_RESPUESTA_SOSPECHOSO: "Patrón de respuestas sospechoso detectado",
            TipoEvento.VELOCIDAD_RESPUESTA_ANOMALA: f"Velocidad de respuesta anómala: {datos_evento.get('velocidad', 0)}s"
        }
        
        return descripciones.get(tipo_evento, f"Evento {tipo_evento.value}")
    
    def _verificar_alertas_tiempo_real(self, db: Session, evento: EventoAntiTrampa):
        """Verificar si el evento requiere alertas inmediatas"""
        # Obtener configuración del examen
        intento = db.query(IntentoExamen).filter(
            IntentoExamen.intento_id == evento.intento_id
        ).first()
        
        if not intento:
            return
        
        examen = db.query(Examen).filter(Examen.examen_id == intento.examen_id).first()
        if not examen or not examen.configuracion_anti_trampa:
            return
        
        config = examen.configuracion_anti_trampa
        
        # Verificar umbrales críticos
        if config.get("alertas_inmediatas", False):
            if evento.tipo_evento in self.eventos_sospechosos:
                limite_critico = self.eventos_sospechosos[evento.tipo_evento]["limite_critico"]
                
                # Contar eventos del mismo tipo en los últimos 10 minutos
                timestamp_limite = datetime.utcnow() - timedelta(minutes=10)
                eventos_similares = db.query(EventoAntiTrampa).filter(
                    and_(
                        EventoAntiTrampa.intento_id == evento.intento_id,
                        EventoAntiTrampa.tipo_evento == evento.tipo_evento,
                        EventoAntiTrampa.timestamp >= timestamp_limite
                    )
                ).count()
                
                if eventos_similares >= limite_critico:
                    # TODO: Implementar sistema de notificaciones en tiempo real
                    # Por ahora, marcar el intento como sospechoso
                    intento.datos_adicionales = intento.datos_adicionales or {}
                    intento.datos_adicionales["alerta_critica"] = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "tipo_evento": evento.tipo_evento.value,
                        "eventos_acumulados": eventos_similares
                    }
                    db.commit()
    
    def _analizar_patron_temporal(self, eventos: List[EventoAntiTrampa]) -> Dict[str, Any]:
        """Analizar patrones temporales en los eventos"""
        if len(eventos) < 2:
            return {"suficientes_datos": False}
        
        # Calcular intervalos entre eventos
        intervalos = []
        for i in range(1, len(eventos)):
            intervalo = (eventos[i].timestamp - eventos[i-1].timestamp).seconds
            intervalos.append(intervalo)
        
        if not intervalos:
            return {"suficientes_datos": False}
        
        intervalo_promedio = sum(intervalos) / len(intervalos)
        
        # Detectar ráfagas de eventos (muchos eventos en poco tiempo)
        eventos_en_rafaga = 0
        for intervalo in intervalos:
            if intervalo < 5:  # Eventos con menos de 5 segundos de diferencia
                eventos_en_rafaga += 1
        
        return {
            "suficientes_datos": True,
            "intervalo_promedio_segundos": round(intervalo_promedio, 2),
            "total_intervalos": len(intervalos),
            "eventos_en_rafaga": eventos_en_rafaga,
            "porcentaje_rafaga": round((eventos_en_rafaga / len(intervalos)) * 100, 2) if intervalos else 0
        }
    
    def _analizar_cambios_contexto(self, eventos: List[EventoAntiTrampa]) -> Dict[str, Any]:
        """Analizar cambios de contexto (IPs, user agents)"""
        ips_unicas = set()
        user_agents_unicos = set()
        
        for evento in eventos:
            if evento.ip_address:
                ips_unicas.add(evento.ip_address)
            if evento.user_agent:
                user_agents_unicos.add(evento.user_agent)
        
        return {
            "ips_unicas": len(ips_unicas),
            "user_agents_unicos": len(user_agents_unicos),
            "cambio_contexto_sospechoso": len(ips_unicas) > 1 or len(user_agents_unicos) > 2
        }
    
    def _calcular_nivel_riesgo(self, puntuacion: int) -> str:
        """Calcular nivel de riesgo basado en puntuación"""
        for nivel, umbral in self.umbrales_riesgo.items():
            if puntuacion <= umbral:
                return nivel
        return "critico"
    
    def _generar_alertas(self, eventos_por_tipo: Dict[str, int]) -> List[str]:
        """Generar alertas basadas en eventos por tipo"""
        alertas = []
        
        for tipo_str, cantidad in eventos_por_tipo.items():
            try:
                tipo_evento = TipoEvento(tipo_str)
                if tipo_evento in self.eventos_sospechosos:
                    limite = self.eventos_sospechosos[tipo_evento]["limite_critico"]
                    if cantidad >= limite:
                        alertas.append(f"CRÍTICO: {cantidad} eventos de tipo {tipo_str} (límite: {limite})")
                    elif cantidad >= limite * 0.7:
                        alertas.append(f"ADVERTENCIA: {cantidad} eventos de tipo {tipo_str} aproximándose al límite")
            except ValueError:
                continue
        
        return alertas
    
    def _generar_recomendaciones(self, analisis: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones basadas en el análisis"""
        recomendaciones = []
        
        if analisis["nivel_riesgo"] == "critico":
            recomendaciones.append("ACCIÓN INMEDIATA: Considerar suspender el intento y contactar al estudiante")
            recomendaciones.append("Revisar manualmente todas las respuestas")
        
        elif analisis["nivel_riesgo"] == "alto":
            recomendaciones.append("Revisión manual recomendada")
            recomendaciones.append("Considerar entrevista con el estudiante")
        
        elif analisis["nivel_riesgo"] == "medio":
            recomendaciones.append("Monitoreo adicional recomendado")
            recomendaciones.append("Revisar respuestas con mayor detalle")
        
        # Recomendaciones específicas
        eventos_cambio_app = analisis["eventos_por_tipo"].get("cambio_aplicacion", 0)
        if eventos_cambio_app > 2:
            recomendaciones.append(f"Investigar {eventos_cambio_app} cambios de aplicación")
        
        eventos_pantalla_completa = analisis["eventos_por_tipo"].get("pantalla_completa_salida", 0)
        if eventos_pantalla_completa > 0:
            recomendaciones.append("Verificar razones para salir de pantalla completa")
        
        return recomendaciones
    
    def _detectar_patron_repetitivo(self, secuencia: List[Any]) -> Optional[str]:
        """Detectar patrones repetitivos en una secuencia"""
        if len(secuencia) < 4:
            return None
        
        # Buscar patrones de longitud 2, 3 y 4
        for longitud_patron in range(2, min(5, len(secuencia) // 2 + 1)):
            for inicio in range(len(secuencia) - longitud_patron * 2 + 1):
                patron = secuencia[inicio:inicio + longitud_patron]
                
                # Verificar si el patrón se repite al menos 2 veces
                repeticiones = 0
                pos = inicio
                while pos + longitud_patron <= len(secuencia):
                    if secuencia[pos:pos + longitud_patron] == patron:
                        repeticiones += 1
                        pos += longitud_patron
                    else:
                        break
                
                if repeticiones >= 2:
                    return f"longitud_{longitud_patron}_repeticiones_{repeticiones}"
        
        return None
    
    def _generar_flags_rojas(self, eventos: List[EventoAntiTrampa], analisis: Dict[str, Any]) -> List[str]:
        """Generar lista de flags rojas (señales de alerta críticas)"""
        flags = []
        
        # Flags basados en eventos críticos
        eventos_criticos = [e for e in eventos if e.tipo_evento in [
            TipoEvento.CAMBIO_APLICACION,
            TipoEvento.PANTALLA_COMPLETA_SALIDA,
            TipoEvento.MULTIPLE_SESION_IP
        ]]
        
        if eventos_criticos:
            flags.append(f"{len(eventos_criticos)} eventos críticos detectados")
        
        # Flags basados en análisis de actividad
        if analisis["puntuacion_riesgo"] > 50:
            flags.append(f"Puntuación de riesgo muy alta: {analisis['puntuacion_riesgo']}")
        
        if analisis["nivel_riesgo"] in ["alto", "critico"]:
            flags.append(f"Nivel de riesgo: {analisis['nivel_riesgo'].upper()}")
        
        return flags
    
    def _generar_aspectos_positivos(self, analisis: Dict[str, Any]) -> List[str]:
        """Generar lista de aspectos positivos del intento"""
        aspectos = []
        
        if analisis["puntuacion_riesgo"] < 10:
            aspectos.append("Muy pocos eventos sospechosos")
        
        if analisis["nivel_riesgo"] == "bajo":
            aspectos.append("Comportamiento consistente con un intento legítimo")
        
        eventos_menores = analisis["eventos_por_tipo"].get("clic_fuera_ventana", 0)
        if eventos_menores < 3:
            aspectos.append("Pocos clics fuera de la ventana")
        
        return aspectos
    
    def _generar_recomendaciones_detalladas(
        self, 
        analisis_actividad: Dict[str, Any], 
        sesiones_multiples: Dict[str, Any], 
        puntuacion_integridad: float
    ) -> List[str]:
        """Generar recomendaciones detalladas para el profesor"""
        recomendaciones = []
        
        if puntuacion_integridad >= 80:
            recomendaciones.append("✅ Intento con alta integridad - Se puede calificar normalmente")
        
        elif puntuacion_integridad >= 60:
            recomendaciones.append("⚠️ Revisar respuestas manualmente por precaución")
            recomendaciones.append("💬 Considerar conversación con el estudiante sobre las irregularidades menores")
        
        elif puntuacion_integridad >= 40:
            recomendaciones.append("🔍 Investigación requerida - Múltiples eventos sospechosos")
            recomendaciones.append("📞 Entrevista con el estudiante altamente recomendada")
            recomendaciones.append("📝 Documentar el proceso de investigación")
        
        else:
            recomendaciones.append("❌ Considerar invalidar el intento")
            recomendaciones.append("🚨 Investigación formal necesaria")
            recomendaciones.append("📋 Ofrecer al estudiante la oportunidad de repetir bajo supervisión")
        
        # Recomendaciones específicas por tipo de evento
        if sesiones_multiples.get("sospechoso", False):
            recomendaciones.append("🔐 Verificar que el estudiante no compartió credenciales")
        
        cambios_app = analisis_actividad["eventos_por_tipo"].get("cambio_aplicacion", 0)
        if cambios_app > 0:
            recomendaciones.append(f"💻 Investigar los {cambios_app} cambios de aplicación detectados")
        
        return recomendaciones


# Instancia global del servicio
detector_anti_trampa = DetectorAntiTrampa()