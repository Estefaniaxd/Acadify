"""Validador de entregas de tareas - Validaciones de negocio.

Módulo que implementa todas las validaciones de lógica de negocio
para entregas de tareas siguiendo SOLID principles.

Validaciones:
- Inscripción en grupo
- Intentos máximos
- Fechas de disponibilidad y límite
- Estado de la tarea

Author: Acadify Team
Version: 1.0.0
"""

import logging
from typing import Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import func

logger = logging.getLogger(__name__)


class EstadoValidacionEntrega(str, Enum):
    """Estados posibles de validación de entrega."""
    VALIDA = "valida"
    ESTUDIANTE_NO_INSCRITO = "estudiante_no_inscrito"
    TAREA_NO_DISPONIBLE = "tarea_no_disponible"
    TAREA_VENCIDA = "tarea_vencida"
    TAREA_DESACTIVADA = "tarea_desactivada"
    LIMITE_INTENTOS_EXCEDIDO = "limite_intentos_excedido"
    ENTREGA_TARDIA_NO_PERMITIDA = "entrega_tardia_no_permitida"
    ERROR_VALIDACION = "error_validacion"


@dataclass
class ResultadoValidacionEntrega:
    """Resultado de validación de entrega."""
    es_valida: bool
    estado: EstadoValidacionEntrega
    mensaje: str
    intentos_restantes: Optional[int] = None
    tiempo_restante_segundos: Optional[int] = None
    detalles: Optional[dict] = None


class ValidadorEntregaTarea:
    """Validador de entregas siguiendo SOLID.
    
    Responsabilidades:
    - Verificar inscripción de estudiante
    - Verificar intentos máximos
    - Verificar disponibilidad de tarea
    - Verificar fechas
    
    Cada validación es un método independiente.
    Fácil de testear y extender.
    """
    
    def __init__(self, session: Session):
        """Inicializa validador.
        
        Args:
            session: Sesión de SQLAlchemy
        """
        self.session = session
    
    def verificar_inscripcion_estudiante(
        self,
        estudiante_id: str,
        grupo_id: str
    ) -> tuple[bool, str]:
        """Verifica que estudiante está inscrito en el grupo.
        
        Args:
            estudiante_id: ID del estudiante
            grupo_id: ID del grupo de la tarea
            
        Returns:
            Tupla (está_inscrito, mensaje)
        """
        try:
            # Importar aquí para evitar circular imports
            from src.models.academic.grupos import EstudianteGrupo
            
            inscripcion = self.session.query(EstudianteGrupo).filter(
                EstudianteGrupo.estudiante_id == estudiante_id,
                EstudianteGrupo.grupo_id == grupo_id,
                EstudianteGrupo.activa == True  # Solo inscripciones activas
            ).first()
            
            if not inscripcion:
                logger.warning(
                    f"Estudiante {estudiante_id} no inscrito en grupo {grupo_id}"
                )
                return False, (
                    f"No estás inscrito en el grupo de esta tarea. "
                    f"Contacta al docente."
                )
            
            logger.info(f"✅ Inscripción verificada: {estudiante_id} en {grupo_id}")
            return True, ""
        
        except Exception as e:
            logger.error(f"Error verificando inscripción: {e}", exc_info=True)
            return False, "Error al verificar inscripción"
    
    def contar_entregas_previas(
        self,
        tarea_id: str,
        estudiante_id: str
    ) -> int:
        """Cuenta entregas previas del estudiante.
        
        Args:
            tarea_id: ID de la tarea
            estudiante_id: ID del estudiante
            
        Returns:
            Número de entregas previas
        """
        try:
            from src.models.academic.entregas import EntregaTarea
            
            cantidad = self.session.query(func.count(EntregaTarea.entrega_id)).filter(
                EntregaTarea.tarea_id == tarea_id,
                EntregaTarea.estudiante_id == estudiante_id
            ).scalar()
            
            return cantidad or 0
        
        except Exception as e:
            logger.error(f"Error contando entregas: {e}", exc_info=True)
            return 0
    
    def verificar_intentos_maximos(
        self,
        tarea_id: str,
        estudiante_id: str,
        intentos_maximos: Optional[int]
    ) -> tuple[bool, str, int]:
        """Verifica si estudiante puede hacer otro intento.
        
        Args:
            tarea_id: ID de la tarea
            estudiante_id: ID del estudiante
            intentos_maximos: Número máximo de intentos (None = ilimitados)
            
        Returns:
            Tupla (puede_entregar, mensaje, intentos_restantes)
        """
        try:
            # Si no hay límite de intentos, permitir
            if intentos_maximos is None or intentos_maximos <= 0:
                return True, "", float('inf')
            
            # Contar entregas
            entregas_realizadas = self.contar_entregas_previas(
                tarea_id,
                estudiante_id
            )
            
            intentos_restantes = intentos_maximos - entregas_realizadas
            
            if intentos_restantes <= 0:
                logger.warning(
                    f"Estudiante {estudiante_id} excedió intentos en tarea {tarea_id}. "
                    f"Intentos: {entregas_realizadas}/{intentos_maximos}"
                )
                return False, (
                    f"Has alcanzado el límite de intentos ({intentos_maximos}). "
                    f"Contacta al docente si necesitas enviar de nuevo."
                ), 0
            
            logger.debug(
                f"Intentos restantes: {estudiante_id} - {intentos_restantes}/{intentos_maximos}"
            )
            return True, "", intentos_restantes
        
        except Exception as e:
            logger.error(f"Error verificando intentos: {e}", exc_info=True)
            return False, "Error al verificar intentos", 0
    
    def verificar_disponibilidad_tarea(
        self,
        tarea,  # Objeto Tarea
        incluir_tardias: bool = True
    ) -> tuple[bool, str, Optional[datetime]]:
        """Verifica si tarea está disponible para entregar.
        
        Comprobaciones:
        - Tarea está activa
        - Hoy es >= fecha_inicio_disponible
        - Hoy es <= fecha_limite (o permitida si es tardía)
        - No está en estado vencido o cerrado
        
        Args:
            tarea: Objeto Tarea
            incluir_tardias: Si True, permite entregas tardías si está configurado
            
        Returns:
            Tupla (está_disponible, mensaje, fecha_limite)
        """
        try:
            ahora = datetime.utcnow()
            
            # 1. ¿Tarea está activa?
            if not tarea.activa:
                logger.warning(f"Tarea {tarea.tarea_id} no está activa")
                return False, "Esta tarea no está disponible", None
            
            # 2. ¿Hoy es >= fecha_inicio?
            if tarea.fecha_inicio_disponible and ahora < tarea.fecha_inicio_disponible:
                tiempo_espera = (tarea.fecha_inicio_disponible - ahora).total_seconds()
                return False, (
                    f"Esta tarea aún no está disponible. "
                    f"Estará disponible en {tarea.fecha_inicio_disponible.strftime('%d/%m/%Y %H:%M')}"
                ), tarea.fecha_limite
            
            # 3. ¿Hoy es <= fecha_limite?
            es_tardia = ahora > tarea.fecha_limite
            
            if es_tardia:
                # Es tardía - ¿se permite?
                if not tarea.permite_entrega_tardia and not tarea.permite_entregas_tardias:
                    logger.warning(
                        f"Entrega tardía no permitida para tarea {tarea.tarea_id}"
                    )
                    return False, (
                        f"El plazo para esta tarea venció el "
                        f"{tarea.fecha_limite.strftime('%d/%m/%Y %H:%M')}. "
                        f"No se aceptan entregas tardías."
                    ), tarea.fecha_limite
                
                # Es tardía pero se permite
                if incluir_tardias:
                    logger.info(f"Entrega tardía permitida para {tarea.tarea_id}")
                    return True, (
                        "Envío tardío (se aplicará penalización del "
                        f"{tarea.penalizacion_tardia}%)"
                    ), tarea.fecha_limite
            
            logger.info(f"✅ Tarea disponible: {tarea.tarea_id}")
            return True, "", tarea.fecha_limite
        
        except Exception as e:
            logger.error(f"Error verificando disponibilidad: {e}", exc_info=True)
            return False, "Error al verificar disponibilidad", None
    
    def calcular_tiempo_restante(
        self,
        fecha_limite: datetime
    ) -> int:
        """Calcula tiempo restante en segundos.
        
        Args:
            fecha_limite: Fecha límite
            
        Returns:
            Segundos restantes (puede ser negativo si está vencida)
        """
        ahora = datetime.utcnow()
        diferencia = fecha_limite - ahora
        return int(diferencia.total_seconds())
    
    def validar_entrega_completa(
        self,
        tarea,
        estudiante_id: str,
        grupo_id: str
    ) -> ResultadoValidacionEntrega:
        """Realiza TODAS las validaciones.
        
        Orden lógico:
        1. ¿Estudiante está inscrito?
        2. ¿Tarea está disponible?
        3. ¿Puede hacer más intentos?
        
        Args:
            tarea: Objeto Tarea
            estudiante_id: ID del estudiante
            grupo_id: ID del grupo
            
        Returns:
            ResultadoValidacionEntrega con todo detallado
        """
        try:
            # 1. Verificar inscripción
            inscrito, msg_inscripcion = self.verificar_inscripcion_estudiante(
                estudiante_id,
                grupo_id
            )
            if not inscrito:
                return ResultadoValidacionEntrega(
                    es_valida=False,
                    estado=EstadoValidacionEntrega.ESTUDIANTE_NO_INSCRITO,
                    mensaje=msg_inscripcion,
                    detalles={"inscripcion_verificada": False}
                )
            
            # 2. Verificar disponibilidad
            disponible, msg_disponibilidad, fecha_limite = (
                self.verificar_disponibilidad_tarea(tarea)
            )
            if not disponible:
                return ResultadoValidacionEntrega(
                    es_valida=False,
                    estado=(
                        EstadoValidacionEntrega.TAREA_VENCIDA
                        if "plazo" in msg_disponibilidad
                        else EstadoValidacionEntrega.TAREA_NO_DISPONIBLE
                    ),
                    mensaje=msg_disponibilidad,
                    tiempo_restante_segundos=self.calcular_tiempo_restante(
                        fecha_limite
                    ) if fecha_limite else None,
                    detalles={"disponibilidad_verificada": False}
                )
            
            # 3. Verificar intentos
            puede_intentar, msg_intentos, intentos_restantes = (
                self.verificar_intentos_maximos(
                    tarea.tarea_id,
                    estudiante_id,
                    tarea.intentos_maximos
                )
            )
            if not puede_intentar:
                return ResultadoValidacionEntrega(
                    es_valida=False,
                    estado=EstadoValidacionEntrega.LIMITE_INTENTOS_EXCEDIDO,
                    mensaje=msg_intentos,
                    intentos_restantes=0,
                    detalles={"intentos_verificados": False}
                )
            
            # ✅ TODO VÁLIDO
            tiempo_restante = self.calcular_tiempo_restante(
                fecha_limite
            ) if fecha_limite else None
            
            return ResultadoValidacionEntrega(
                es_valida=True,
                estado=EstadoValidacionEntrega.VALIDA,
                mensaje=(
                    msg_disponibilidad or
                    f"✅ Puedes enviar. Intentos restantes: {intentos_restantes}"
                ),
                intentos_restantes=int(intentos_restantes)
                    if intentos_restantes != float('inf')
                    else None,
                tiempo_restante_segundos=tiempo_restante,
                detalles={
                    "inscripcion": True,
                    "disponibilidad": True,
                    "intentos": True,
                    "es_tardio": tiempo_restante is not None and tiempo_restante < 0
                }
            )
        
        except Exception as e:
            logger.error(f"Error en validación completa: {e}", exc_info=True)
            return ResultadoValidacionEntrega(
                es_valida=False,
                estado=EstadoValidacionEntrega.ERROR_VALIDACION,
                mensaje=f"Error al validar: {str(e)}",
                detalles={"error": str(e)}
            )
