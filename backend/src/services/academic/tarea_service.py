"""
Service para gestión de tareas en cursos

Principios SOLID aplicados:
- SRP: Responsabilidad única - gestión de tareas
- OCP: Abierto para extensión, cerrado para modificación
- LSP: Interfaces consistentes
- ISP: Métodos cohesivos y específicos
- DIP: Depende de abstracciones

Clean Code:
- Nombres descriptivos y auto-documentados
- Funciones pequeñas (una responsabilidad por función)
- DRY: Don't Repeat Yourself
- Manejo explícito de errores
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID
import json

from src.models.users.usuario import Usuario

logger = logging.getLogger(__name__)


class TareaService:
    """
    Service para gestión de tareas
    
    Responsabilidades:
    - CRUD de tareas
    - Gestión de entregas
    - Calificaciones
    - Validación de permisos
    - Notificaciones (futuro)
    """
    
    # Constantes (Clean Code: Evitar magic numbers)
    MAX_TITULO_LENGTH = 200
    MAX_DESCRIPCION_LENGTH = 5000
    DEFAULT_PAGE_SIZE = 20
    MAX_CALIFICACION = 100
    MIN_CALIFICACION = 0
    
    @staticmethod
    def crear_tarea(
        db: Session,
        curso_id: str,
        titulo: str,
        descripcion: str,
        fecha_limite: datetime,
        puntos_max: float,
        usuario: Usuario,
        tipo: Optional[str] = "individual",
        archivo_adjunto: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crea una nueva tarea en un curso
        
        Args:
            db: Sesión de base de datos
            curso_id: ID del curso
            titulo: Título de la tarea
            descripcion: Descripción detallada
            fecha_limite: Fecha límite de entrega
            puntos_max: Puntuación máxima
            usuario: Usuario que crea (debe ser docente)
            tipo: Tipo de tarea (individual/grupal)
            archivo_adjunto: URL del archivo adjunto
            
        Returns:
            Dict con la tarea creada
            
        Raises:
            HTTPException: Si hay errores de validación
        """
        try:
            # Validaciones (Clean Code: Fail fast)
            TareaService._validar_datos_tarea(titulo, descripcion, puntos_max, fecha_limite)
            TareaService._validar_permisos_docente(db, curso_id, usuario)
            
            # Crear tarea usando SQL directo (por ahora)
            query = text("""
                INSERT INTO tareas (
                    curso_id, titulo, descripcion, fecha_limite,
                    puntos_max, tipo, archivo_adjunto, creado_por,
                    fecha_creacion
                )
                VALUES (
                    :curso_id, :titulo, :descripcion, :fecha_limite,
                    :puntos_max, :tipo, :archivo_adjunto, :creado_por,
                    :fecha_creacion
                )
                RETURNING tarea_id
            """)
            
            result = db.execute(query, {
                "curso_id": curso_id,
                "titulo": titulo,
                "descripcion": descripcion,
                "fecha_limite": fecha_limite,
                "puntos_max": puntos_max,
                "tipo": tipo,
                "archivo_adjunto": archivo_adjunto,
                "creado_por": usuario.usuario_id,
                "fecha_creacion": datetime.now(timezone.utc)
            })
            
            tarea_id = result.fetchone()[0]
            db.commit()
            
            logger.info(f"Tarea creada: {tarea_id} en curso {curso_id}")
            
            return {
                "success": True,
                "message": "Tarea creada exitosamente",
                "data": {
                    "tarea_id": str(tarea_id),
                    "titulo": titulo,
                    "fecha_limite": fecha_limite.isoformat()
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creando tarea: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear tarea: {str(e)}"
            )
    
    @staticmethod
    def obtener_tareas_curso(
        db: Session,
        curso_id: str,
        usuario: Usuario,
        limit: int = DEFAULT_PAGE_SIZE,
        offset: int = 0,
        incluir_vencidas: bool = False
    ) -> Dict[str, Any]:
        """
        Obtiene tareas de un curso con información de entrega
        
        Args:
            db: Sesión de base de datos
            curso_id: ID del curso
            usuario: Usuario que consulta
            limit: Límite de resultados
            offset: Offset para paginación
            incluir_vencidas: Si incluir tareas vencidas
            
        Returns:
            Dict con tareas y metadata
        """
        try:
            # Validar acceso al curso
            TareaService._validar_acceso_curso(db, curso_id, usuario)
            
            # Query optimizada con información de entrega
            fecha_actual = datetime.now(timezone.utc)
            
            query = text("""
                SELECT 
                    t.tarea_id,
                    t.titulo,
                    t.descripcion,
                    t.fecha_limite,
                    t.puntos_max,
                    t.tipo,
                    t.archivo_adjunto,
                    t.fecha_creacion,
                    u.nombres || ' ' || u.apellidos as creador_nombre,
                    CASE 
                        WHEN t.fecha_limite < :fecha_actual THEN 'vencida'
                        WHEN t.fecha_limite < :fecha_actual + INTERVAL '24 hours' THEN 'proxima'
                        ELSE 'activa'
                    END as estado_tiempo,
                    COUNT(DISTINCT et.entrega_id) as total_entregas,
                    COALESCE(mi_entrega.entrega_id, NULL) as mi_entrega_id,
                    COALESCE(mi_entrega.estado, NULL) as mi_estado_entrega,
                    COALESCE(mi_entrega.calificacion, NULL) as mi_calificacion
                FROM tareas t
                JOIN "Usuario" u ON t.creado_por = u.usuario_id
                LEFT JOIN entregas_tareas et ON t.tarea_id = et.tarea_id
                LEFT JOIN entregas_tareas mi_entrega 
                    ON t.tarea_id = mi_entrega.tarea_id 
                    AND mi_entrega.estudiante_id = :usuario_id
                WHERE t.curso_id = :curso_id
                    AND (:incluir_vencidas OR t.fecha_limite >= :fecha_actual)
                GROUP BY t.tarea_id, u.usuario_id, mi_entrega.entrega_id, 
                         mi_entrega.estado, mi_entrega.calificacion
                ORDER BY t.fecha_limite ASC
                LIMIT :limit OFFSET :offset
            """)
            
            result = db.execute(query, {
                "curso_id": curso_id,
                "usuario_id": usuario.usuario_id,
                "fecha_actual": fecha_actual,
                "incluir_vencidas": incluir_vencidas,
                "limit": limit,
                "offset": offset
            }).fetchall()
            
            # Contar total
            count_query = text("""
                SELECT COUNT(*) 
                FROM tareas 
                WHERE curso_id = :curso_id
                    AND (:incluir_vencidas OR fecha_limite >= :fecha_actual)
            """)
            
            total = db.execute(count_query, {
                "curso_id": curso_id,
                "fecha_actual": fecha_actual,
                "incluir_vencidas": incluir_vencidas
            }).scalar()
            
            tareas = [dict(row._mapping) for row in result]
            
            # Enriquecer con información adicional
            for tarea in tareas:
                tarea['dias_restantes'] = TareaService._calcular_dias_restantes(
                    tarea['fecha_limite']
                )
                tarea['puede_entregar'] = TareaService._puede_entregar(
                    tarea['estado_tiempo'],
                    tarea.get('mi_estado_entrega')
                )
            
            return {
                "success": True,
                "data": tareas,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total
                },
                "summary": TareaService._generar_resumen_tareas(tareas)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo tareas: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener tareas: {str(e)}"
            )
    
    @staticmethod
    def entregar_tarea(
        db: Session,
        tarea_id: str,
        usuario: Usuario,
        contenido: str,
        archivo_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra la entrega de una tarea por un estudiante
        
        Args:
            db: Sesión de base de datos
            tarea_id: ID de la tarea
            usuario: Estudiante que entrega
            contenido: Contenido de la entrega
            archivo_url: URL del archivo adjunto
            
        Returns:
            Dict con la entrega registrada
        """
        try:
            # Validar contenido no vacío
            if not contenido or not contenido.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El contenido de la entrega no puede estar vacío"
                )
            
            # Validaciones
            TareaService._validar_puede_entregar(db, tarea_id, usuario)
            
            # Verificar si ya entregó
            entrega_existente = TareaService._obtener_mi_entrega(db, tarea_id, usuario.usuario_id)
            
            if entrega_existente:
                # Actualizar entrega existente
                return TareaService._actualizar_entrega(
                    db, entrega_existente['entrega_id'], contenido, archivo_url
                )
            
            # Crear nueva entrega
            query = text("""
                INSERT INTO entregas_tareas (
                    tarea_id, estudiante_id, contenido, archivo_url,
                    fecha_entrega, estado
                )
                VALUES (
                    :tarea_id, :estudiante_id, :contenido, :archivo_url,
                    :fecha_entrega, 'entregada'
                )
                RETURNING entrega_id
            """)
            
            result = db.execute(query, {
                "tarea_id": tarea_id,
                "estudiante_id": usuario.usuario_id,
                "contenido": contenido,
                "archivo_url": archivo_url,
                "fecha_entrega": datetime.now(timezone.utc)
            })
            
            entrega_id = result.fetchone()[0]
            db.commit()
            
            logger.info(f"Tarea entregada: {tarea_id} por {usuario.usuario_id}")
            
            return {
                "success": True,
                "message": "Tarea entregada exitosamente",
                "data": {
                    "entrega_id": str(entrega_id),
                    "fecha_entrega": datetime.now(timezone.utc).isoformat(),
                    "estado": "entregada"
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error entregando tarea: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al entregar tarea: {str(e)}"
            )
    
    @staticmethod
    async def calificar_entrega(
        db: Session,
        entrega_id: str,
        calificacion: float,
        retroalimentacion: Optional[str],
        usuario: Usuario
    ) -> Dict[str, Any]:
        """
        Califica una entrega de tarea CON GAMIFICACIÓN INTEGRADA.
        
        Flujo completo:
        1. Valida calificación y permisos
        2. Actualiza calificación en BD
        3. Calcula puntos (base + bonos por calidad, rapidez, racha)
        4. Otorga puntos con PuntosService
        5. Verifica racha diaria con RachaService
        6. Actualiza progreso de badges
        
        Args:
            db: Sesión de base de datos
            entrega_id: ID de la entrega
            calificacion: Calificación numérica (0-100)
            retroalimentacion: Comentarios del docente
            usuario: Docente que califica
            
        Returns:
            Dict con:
            - calificacion registrada
            - puntos otorgados (con desglose de bonos)
            - racha actualizada
            - badges progresados
        """
        try:
            # ========== 1. VALIDACIONES ==========
            TareaService._validar_calificacion(calificacion)
            TareaService._validar_permisos_calificar(db, entrega_id, usuario)
            
            # ========== 2. OBTENER INFO DE ENTREGA Y TAREA ==========
            query_info = text("""
                SELECT 
                    et.entrega_id,
                    et.tarea_id,
                    et.estudiante_id,
                    et.fecha_envio,
                    et.es_tardia,
                    et.intentos,
                    t.titulo as tarea_titulo,
                    t.puntos_base,
                    t.puntos_bonificacion,
                    t.fecha_limite,
                    t.fecha_asignacion,
                    t.tipo as tipo_tarea
                FROM entregas_tareas et
                JOIN tareas t ON et.tarea_id = t.tarea_id
                WHERE et.entrega_id = :entrega_id
            """)
            
            info_row = db.execute(query_info, {"entrega_id": entrega_id}).fetchone()
            
            if not info_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Entrega no encontrada"
                )
            
            info = dict(info_row._mapping)
            
            # ========== 3. CONVERTIR CALIFICACIÓN 0-100 A 0-5 ==========
            # Sistema usa 0-5 para calificación académica
            calificacion_5 = (calificacion / 100) * 5
            
            # ========== 4. CALCULAR PUNTOS GAMIFICACIÓN ==========
            
            # Puntos base de la tarea (default 50 si no está configurado)
            puntos_base = info['puntos_base'] or 50
            puntos_bonificacion_config = info['puntos_bonificacion'] or 20
            
            # Puntos según calificación (proporcional)
            # >= 90 (4.5/5): puntos_base + bonificación completa
            # >= 80 (4.0/5): puntos_base + 50% bonificación
            # >= 70 (3.5/5): puntos_base
            # < 70: puntos_base * porcentaje
            
            if calificacion >= 90:  # Excelente
                puntos_calidad = puntos_base + puntos_bonificacion_config
                multiplicador_calidad = 1.0
                nivel_calidad = "Excelente"
            elif calificacion >= 80:  # Bueno
                puntos_calidad = puntos_base + (puntos_bonificacion_config // 2)
                multiplicador_calidad = 1.0
                nivel_calidad = "Bueno"
            elif calificacion >= 70:  # Aceptable
                puntos_calidad = puntos_base
                multiplicador_calidad = 1.0
                nivel_calidad = "Aceptable"
            else:  # Bajo (proporcional)
                multiplicador_calidad = calificacion / 70  # 0.0 - 1.0
                puntos_calidad = int(puntos_base * multiplicador_calidad)
                nivel_calidad = "En desarrollo"
            
            # Bono por rapidez (si entregó en la primera mitad del plazo)
            puntos_rapidez = 0
            dias_disponibles = (info['fecha_limite'] - info['fecha_asignacion']).days
            dias_usado = (info['fecha_envio'] - info['fecha_asignacion']).days
            
            if not info['es_tardia'] and dias_disponibles > 0:
                porcentaje_tiempo_usado = dias_usado / dias_disponibles
                
                if porcentaje_tiempo_usado <= 0.3:  # Entregó en primer 30%
                    puntos_rapidez = 15
                    nivel_rapidez = "Ultra-rápido"
                elif porcentaje_tiempo_usado <= 0.5:  # Entregó en primer 50%
                    puntos_rapidez = 10
                    nivel_rapidez = "Rápido"
                elif porcentaje_tiempo_usado <= 0.75:  # Entregó en primer 75%
                    puntos_rapidez = 5
                    nivel_rapidez = "A tiempo"
                else:
                    nivel_rapidez = "Justo a tiempo"
            else:
                nivel_rapidez = "Tardía" if info['es_tardia'] else "Sin bono"
            
            # Penalización por entrega tardía
            penalizacion_tardia = 0
            if info['es_tardia']:
                penalizacion_tardia = -10
            
            # Penalización por múltiples intentos (si reenvió)
            penalizacion_intentos = 0
            if info['intentos'] > 1:
                penalizacion_intentos = -(info['intentos'] - 1) * 5
            
            # TOTAL DE PUNTOS
            puntos_totales = max(0, puntos_calidad + puntos_rapidez + penalizacion_tardia + penalizacion_intentos)
            
            logger.info(
                f"Puntos calculados para entrega {entrega_id}: "
                f"Base+Calidad={puntos_calidad}, Rapidez={puntos_rapidez}, "
                f"Tardía={penalizacion_tardia}, Intentos={penalizacion_intentos}, "
                f"TOTAL={puntos_totales}"
            )
            
            # ========== 5. ACTUALIZAR CALIFICACIÓN EN BD ==========
            query = text("""
                UPDATE entregas_tareas
                SET calificacion = :calificacion,
                    retroalimentacion_docente = :retroalimentacion,
                    fecha_revision = :fecha_revision,
                    estado = :estado,
                    puntos_otorgados = :puntos_otorgados
                WHERE entrega_id = :entrega_id
                RETURNING tarea_id, estudiante_id
            """)
            
            result = db.execute(query, {
                "entrega_id": entrega_id,
                "calificacion": calificacion_5,  # Guardar en escala 0-5
                "retroalimentacion": retroalimentacion,
                "fecha_revision": datetime.now(timezone.utc),
                "estado": "calificada",
                "puntos_otorgados": puntos_totales
            })
            
            row = result.fetchone()
            db.commit()
            
            logger.info(f"Entrega calificada: {entrega_id} con {calificacion}/100 ({calificacion_5}/5)")
            
            # ========== 6. OTORGAR PUNTOS CON GAMIFICACIÓN ==========
            
            from src.services.gamification.puntos_service import PuntosService
            
            puntos_service = PuntosService(db)
            
            resultado_puntos = await puntos_service.agregar_puntos(
                usuario_id=info['estudiante_id'],
                cantidad=puntos_totales,
                razon=f"Tarea calificada: {info['tarea_titulo']}",
                tipo_evento="tarea_calificada",
                referencia_id=entrega_id,
                metadata={
                    "tarea_id": str(info['tarea_id']),
                    "calificacion": calificacion,
                    "calificacion_5": calificacion_5,
                    "nivel_calidad": nivel_calidad,
                    "nivel_rapidez": nivel_rapidez,
                    "puntos_base": puntos_calidad,
                    "puntos_rapidez": puntos_rapidez,
                    "penalizacion_tardia": penalizacion_tardia,
                    "penalizacion_intentos": penalizacion_intentos,
                    "es_tardia": info['es_tardia'],
                    "intentos": info['intentos']
                }
            )
            
            logger.info(
                f"Puntos otorgados a usuario {info['estudiante_id']}: "
                f"{puntos_totales} pts (Total acumulado: {resultado_puntos.get('puntos_totales', 0)} pts)"
            )
            
            # ========== 7. VERIFICAR RACHA DIARIA ==========
            
            from src.services.gamification.racha_service import RachaService
            
            racha_service = RachaService(db)
            
            resultado_racha = await racha_service.verificar_racha_diaria(
                usuario_id=info['estudiante_id'],
                tipo_actividad="TAREA_COMPLETADA",
                actividad_id=entrega_id
            )
            
            logger.info(
                f"Racha verificada: {resultado_racha.get('racha_actual', 0)} días. "
                f"Puntos racha: {resultado_racha.get('puntos_dia', 0)} pts"
            )
            
            # ========== 8. VERIFICAR PROGRESO DE BADGES ==========
            
            # TODO: Implementar verificación de badges
            # Por ejemplo: "10 tareas completadas en Matemáticas" -> Badge Matemático
            # Por ahora solo registramos que se completó una tarea
            
            badges_progresados = []  # Futuro
            
            # ========== 9. PREPARAR RESPUESTA COMPLETA ==========
            
            return {
                "success": True,
                "message": "Entrega calificada exitosamente con gamificación completa",
                "data": {
                    "entrega": {
                        "entrega_id": str(entrega_id),
                        "calificacion": calificacion,
                        "calificacion_5": round(calificacion_5, 1),
                        "fecha_calificacion": datetime.now(timezone.utc).isoformat(),
                        "estado": "calificada"
                    },
                    "puntos": {
                        "puntos_totales": puntos_totales,
                        "desglose": {
                            "puntos_calidad": puntos_calidad,
                            "nivel_calidad": nivel_calidad,
                            "puntos_rapidez": puntos_rapidez,
                            "nivel_rapidez": nivel_rapidez,
                            "penalizacion_tardia": penalizacion_tardia,
                            "penalizacion_intentos": penalizacion_intentos
                        },
                        "puntos_acumulados": resultado_puntos.get('puntos_totales', 0),
                        "nivel_usuario": resultado_puntos.get('nivel', 'Novato')
                    },
                    "racha": {
                        "racha_actual": resultado_racha.get('racha_actual', 0),
                        "mejor_racha": resultado_racha.get('mejor_racha', 0),
                        "puntos_racha_hoy": resultado_racha.get('puntos_dia', 0),
                        "milestone_alcanzado": resultado_racha.get('milestone_alcanzado'),
                        "mensaje": resultado_racha.get('mensaje', '')
                    },
                    "badges": {
                        "progresados": badges_progresados,
                        "nuevos": []  # Futuro
                    }
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error calificando entrega con gamificación: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al calificar entrega: {str(e)}"
            )
    
    # ========== MÉTODOS PRIVADOS (Helper functions) ==========
    
    @staticmethod
    def _validar_datos_tarea(
        titulo: str,
        descripcion: str,
        puntos_max: float,
        fecha_limite: datetime
    ) -> None:
        """Valida los datos de una tarea"""
        if not titulo or not titulo.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El título es requerido"
            )
        
        if len(titulo) > TareaService.MAX_TITULO_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El título no puede exceder {TareaService.MAX_TITULO_LENGTH} caracteres"
            )
        
        if len(descripcion) > TareaService.MAX_DESCRIPCION_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La descripción no puede exceder {TareaService.MAX_DESCRIPCION_LENGTH} caracteres"
            )
        
        if puntos_max <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los puntos máximos deben ser mayores a 0"
            )
        
        if fecha_limite <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha límite debe ser en el futuro"
            )
    
    @staticmethod
    def _validar_permisos_docente(db: Session, curso_id: str, usuario: Usuario) -> None:
        """Valida que el usuario sea docente del curso"""
        if usuario.rol != "docente" and usuario.rol != "coordinador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo docentes pueden crear tareas"
            )
        
        # Verificar que es docente del curso
        query = text("""
            SELECT EXISTS(
                SELECT 1 FROM "CursoDocente"
                WHERE curso_id = :curso_id AND docente_id = :docente_id
            )
        """)
        
        es_docente = db.execute(query, {
            "curso_id": curso_id,
            "docente_id": usuario.usuario_id
        }).scalar()
        
        if not es_docente and usuario.rol != "coordinador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No eres docente de este curso"
            )
    
    @staticmethod
    def _validar_acceso_curso(db: Session, curso_id: str, usuario: Usuario) -> None:
        """Valida que el usuario tenga acceso al curso"""
        from src.services.academic.curso_service import CursoService
        
        if not CursoService._usuario_tiene_acceso(db, curso_id, usuario):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este curso"
            )
    
    @staticmethod
    def _validar_puede_entregar(db: Session, tarea_id: str, usuario: Usuario) -> None:
        """Valida que el estudiante puede entregar la tarea"""
        if usuario.rol != "estudiante":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo estudiantes pueden entregar tareas"
            )
        
        # Verificar fecha límite
        query = text("""
            SELECT fecha_limite, titulo
            FROM tareas
            WHERE tarea_id = :tarea_id
        """)
        
        result = db.execute(query, {"tarea_id": tarea_id}).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        
        if result[0] < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha límite de esta tarea ya pasó"
            )
    
    @staticmethod
    def _validar_calificacion(calificacion: float) -> None:
        """Valida que la calificación esté en rango válido"""
        if calificacion < TareaService.MIN_CALIFICACION or calificacion > TareaService.MAX_CALIFICACION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La calificación debe estar entre {TareaService.MIN_CALIFICACION} y {TareaService.MAX_CALIFICACION}"
            )
    
    @staticmethod
    def _validar_permisos_calificar(db: Session, entrega_id: str, usuario: Usuario) -> None:
        """Valida que el usuario pueda calificar la entrega"""
        if usuario.rol != "docente" and usuario.rol != "coordinador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo docentes pueden calificar entregas"
            )
    
    @staticmethod
    def _obtener_mi_entrega(db: Session, tarea_id: str, estudiante_id: UUID) -> Optional[Dict]:
        """Obtiene la entrega del estudiante para una tarea"""
        query = text("""
            SELECT entrega_id, estado, fecha_entrega
            FROM entregas_tareas
            WHERE tarea_id = :tarea_id AND estudiante_id = :estudiante_id
        """)
        
        result = db.execute(query, {
            "tarea_id": tarea_id,
            "estudiante_id": estudiante_id
        }).fetchone()
        
        return dict(result._mapping) if result else None
    
    @staticmethod
    def _actualizar_entrega(
        db: Session,
        entrega_id: str,
        contenido: str,
        archivo_url: Optional[str]
    ) -> Dict[str, Any]:
        """Actualiza una entrega existente"""
        query = text("""
            UPDATE entregas_tareas
            SET contenido = :contenido,
                archivo_url = :archivo_url,
                fecha_entrega = :fecha_entrega,
                estado = 'entregada'
            WHERE entrega_id = :entrega_id
        """)
        
        db.execute(query, {
            "entrega_id": entrega_id,
            "contenido": contenido,
            "archivo_url": archivo_url,
            "fecha_entrega": datetime.now(timezone.utc)
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Entrega actualizada exitosamente",
            "data": {
                "entrega_id": str(entrega_id),
                "actualizado": True
            }
        }
    
    @staticmethod
    def _calcular_dias_restantes(fecha_limite: datetime) -> int:
        """Calcula días restantes hasta la fecha límite"""
        delta = fecha_limite - datetime.now(timezone.utc)
        return max(0, delta.days)
    
    @staticmethod
    def _puede_entregar(estado_tiempo: str, estado_entrega: Optional[str]) -> bool:
        """Determina si el estudiante puede entregar la tarea"""
        if estado_tiempo == 'vencida':
            return False
        if estado_entrega == 'calificada':
            return False
        return True
    
    @staticmethod
    def _generar_resumen_tareas(tareas: List[Dict]) -> Dict[str, int]:
        """Genera un resumen estadístico de las tareas"""
        return {
            "total": len(tareas),
            "activas": sum(1 for t in tareas if t['estado_tiempo'] == 'activa'),
            "proximas": sum(1 for t in tareas if t['estado_tiempo'] == 'proxima'),
            "vencidas": sum(1 for t in tareas if t['estado_tiempo'] == 'vencida'),
            "entregadas": sum(1 for t in tareas if t.get('mi_entrega_id')),
            "calificadas": sum(1 for t in tareas if t.get('mi_calificacion') is not None)
        }
    
    # ========== MÉTODOS DE INTEGRACIÓN CON IA Y GAMIFICACIÓN ==========
    
    @staticmethod
    async def procesar_entrega_con_ia(
        db: Session,
        tarea_id: str,
        estudiante_id: UUID,
        contenido_texto: Optional[str] = None,
        archivo_binario: Optional[Any] = None,
        archivo_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa una entrega con análisis de IA completo.
        
        Este método orquesta todo el flujo:
        1. Valida y guarda la entrega
        2. Analiza con GeminiService
        3. Calcula puntos con PuntosService
        4. Actualiza BD con retroalimentación y puntos
        5. Verifica y otorga insignias
        
        Args:
            db: Sesión de base de datos
            tarea_id: ID de la tarea
            estudiante_id: ID del estudiante
            contenido_texto: Texto de la entrega (opcional si hay archivo)
            archivo_binario: Stream del archivo (opcional)
            archivo_metadata: Metadata del archivo (nombre, mime_type, tamaño)
        
        Returns:
            Dict con:
            {
                "entrega_id": str,
                "retroalimentacion_ia": {...},
                "calificacion_sugerida": float,
                "puntos_calculados": {...},
                "puntos_otorgados": int,
                "nuevas_insignias": [...],
                "nivel_actual": str
            }
        
        Raises:
            HTTPException: Si hay errores de validación o procesamiento
        """
        
        from src.services.ai import GeminiService
        from src.services.gamification import PuntosService
        from src.models.classes.tarea import Tarea
        from src.models.classes.entregar_tarea import EntregarTarea
        
        try:
            logger.info(f"Iniciando procesamiento con IA para tarea {tarea_id}, estudiante {estudiante_id}")
            
            # ========== 1. VALIDACIONES ==========
            
            if not contenido_texto and not archivo_binario:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debe proporcionar contenido texto o archivo"
                )
            
            # Obtener tarea con configuración de IA
            tarea_query = text("""
                SELECT 
                    tarea_id, titulo, descripcion, fecha_limite,
                    puntos_base, puntos_bonificacion, peso_calificacion,
                    rubrica, restricciones_archivo,
                    habilitar_retroalimentacion_ia, prompt_ia_personalizado,
                    tipo
                FROM tareas
                WHERE tarea_id = :tarea_id
            """)
            
            tarea_row = db.execute(tarea_query, {"tarea_id": tarea_id}).fetchone()
            
            if not tarea_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tarea no encontrada"
                )
            
            tarea_dict = dict(tarea_row._mapping)
            
            # Verificar si IA está habilitada
            if not tarea_dict.get('habilitar_retroalimentacion_ia', False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Esta tarea no tiene habilitada la retroalimentación con IA"
                )
            
            # Verificar fecha límite
            if tarea_dict['fecha_limite'] < datetime.now(timezone.utc):
                es_tardia = True
                logger.warning(f"Entrega tardía detectada para tarea {tarea_id}")
            else:
                es_tardia = False
            
            # ========== 2. CREAR/ACTUALIZAR ENTREGA ==========
            
            # Verificar si ya existe entrega
            entrega_existente_query = text("""
                SELECT entrega_id, intentos, estado
                FROM entregas_tareas
                WHERE tarea_id = :tarea_id AND estudiante_id = :estudiante_id
            """)
            
            entrega_existente = db.execute(entrega_existente_query, {
                "tarea_id": tarea_id,
                "estudiante_id": estudiante_id
            }).fetchone()
            
            if entrega_existente:
                # Actualizar entrega existente
                intentos = entrega_existente[1] + 1
                
                update_query = text("""
                    UPDATE entregas_tareas
                    SET contenido_texto = :contenido_texto,
                        archivo_metadata = :archivo_metadata,
                        fecha_entrega = :fecha_entrega,
                        es_tardia = :es_tardia,
                        intentos = :intentos,
                        estado = 'entregada'
                    WHERE entrega_id = :entrega_id
                    RETURNING entrega_id
                """)
                
                result = db.execute(update_query, {
                    "entrega_id": entrega_existente[0],
                    "contenido_texto": contenido_texto,
                    "archivo_metadata": archivo_metadata,
                    "fecha_entrega": datetime.now(timezone.utc),
                    "es_tardia": es_tardia,
                    "intentos": intentos
                })
                
                entrega_id = entrega_existente[0]
                
            else:
                # Crear nueva entrega
                intentos = 1
                
                insert_query = text("""
                    INSERT INTO entregas_tareas (
                        tarea_id, estudiante_id, contenido_texto,
                        archivo_metadata, fecha_entrega, es_tardia,
                        intentos, estado
                    )
                    VALUES (
                        :tarea_id, :estudiante_id, :contenido_texto,
                        :archivo_metadata, :fecha_entrega, :es_tardia,
                        :intentos, 'entregada'
                    )
                    RETURNING entrega_id
                """)
                
                result = db.execute(insert_query, {
                    "tarea_id": tarea_id,
                    "estudiante_id": estudiante_id,
                    "contenido_texto": contenido_texto,
                    "archivo_metadata": archivo_metadata,
                    "fecha_entrega": datetime.now(timezone.utc),
                    "es_tardia": es_tardia,
                    "intentos": intentos
                })
                
                entrega_id = result.fetchone()[0]
            
            db.commit()
            
            logger.info(f"Entrega guardada: {entrega_id} (intento #{intentos})")
            
            # ========== 3. ANÁLISIS CON IA ==========
            
            logger.info("Iniciando análisis con GeminiService...")
            
            gemini_service = GeminiService()
            await gemini_service.inicializar()
            
            # Preparar contenido para análisis
            if archivo_binario:
                # Extraer contenido del archivo
                from src.services.ai.helpers import FileProcessor
                file_processor = FileProcessor()
                
                archivo_data = file_processor.extraer_contenido(
                    archivo=archivo_binario,
                    nombre_archivo=archivo_metadata.get('nombre', 'archivo') if archivo_metadata else 'archivo',
                    mime_type=archivo_metadata.get('mime_type') if archivo_metadata else None
                )
                
                contenido_analisis = archivo_data
            else:
                contenido_analisis = contenido_texto
            
            # Construir prompt con información de la tarea
            prompt_custom = tarea_dict.get('prompt_ia_personalizado', '')
            
            # Analizar con IA
            retroalimentacion_ia = await gemini_service.analizar_texto(
                texto=contenido_analisis,
                tipo_analisis="tarea_academica",
                rubrica=tarea_dict.get('rubrica'),
                prompt_adicional=prompt_custom,
                contexto={
                    "titulo_tarea": tarea_dict['titulo'],
                    "descripcion": tarea_dict['descripcion'],
                    "tipo_tarea": tarea_dict.get('tipo', 'individual')
                }
            )
            
            calificacion_ia = retroalimentacion_ia.get('calificacion', 0.0)
            
            logger.info(f"Análisis IA completado. Calificación: {calificacion_ia}/5.0")
            
            # ========== 4. CALCULAR PUNTOS ==========
            
            logger.info("Calculando puntos con PuntosService...")
            
            puntos_service = PuntosService(db)
            
            # Crear objeto Tarea mock para el cálculo
            class TareaMock:
                def __init__(self, data):
                    self.tarea_id = data['tarea_id']
                    self.puntos_base = data.get('puntos_base', 50)
                    self.puntos_bonificacion = data.get('puntos_bonificacion', 20)
            
            tarea_mock = TareaMock(tarea_dict)
            
            puntos_info = await puntos_service.calcular_puntos_tarea(
                tarea=tarea_mock,
                calificacion=calificacion_ia,
                es_tardia=es_tardia,
                intentos=intentos
            )
            
            logger.info(f"Puntos calculados: {puntos_info['puntos_totales']} ({puntos_info['desglose']})")
            
            # ========== 5. ACTUALIZAR BD CON RESULTADOS ==========
            
            update_ia_query = text("""
                UPDATE entregas_tareas
                SET calificacion_preliminar_ia = :calificacion_ia,
                    retroalimentacion_ia = :retroalimentacion_ia,
                    puntos_otorgados = :puntos_otorgados
                WHERE entrega_id = :entrega_id
            """)
            
            db.execute(update_ia_query, {
                "entrega_id": entrega_id,
                "calificacion_ia": calificacion_ia,
                "retroalimentacion_ia": retroalimentacion_ia,
                "puntos_otorgados": puntos_info['puntos_totales']
            })
            
            db.commit()
            
            logger.info("Resultados IA guardados en BD")
            
            # ========== 6. OTORGAR PUNTOS AL USUARIO ==========
            
            logger.info("Otorgando puntos al usuario...")
            
            resultado_puntos = await puntos_service.otorgar_puntos(
                usuario_id=estudiante_id,
                puntos=puntos_info['puntos_totales'],
                motivo=f"Tarea: {tarea_dict['titulo']}",
                entrega_id=entrega_id,
                tarea_id=tarea_id
            )
            
            logger.info(
                f"Puntos otorgados: {resultado_puntos['puntos_otorgados']} pts. "
                f"Total acumulado: {resultado_puntos['puntos_acumulados']} pts. "
                f"Nivel: {resultado_puntos['nivel_actual']}"
            )
            
            # ========== 7. RETORNAR RESULTADO COMPLETO ==========
            
            return {
                "success": True,
                "message": "Entrega procesada exitosamente con IA",
                "data": {
                    "entrega_id": str(entrega_id),
                    "intentos": intentos,
                    "es_tardia": es_tardia,
                    "retroalimentacion_ia": {
                        "analisis_general": retroalimentacion_ia.get('analisis_general', ''),
                        "fortalezas": retroalimentacion_ia.get('fortalezas', []),
                        "areas_mejora": retroalimentacion_ia.get('areas_mejora', []),
                        "sugerencias_especificas": retroalimentacion_ia.get('sugerencias_especificas', []),
                        "nivel_cumplimiento": retroalimentacion_ia.get('nivel_cumplimiento', '0%'),
                        "calificacion": calificacion_ia
                    },
                    "puntos": {
                        "puntos_base": puntos_info['puntos_base'],
                        "puntos_bonificacion": puntos_info['puntos_bonificacion'],
                        "penalizacion_tardia": puntos_info['penalizacion_tardia'],
                        "penalizacion_intentos": puntos_info['penalizacion_intentos'],
                        "puntos_totales": puntos_info['puntos_totales'],
                        "desglose": puntos_info['desglose']
                    },
                    "gamificacion": {
                        "puntos_otorgados": resultado_puntos['puntos_otorgados'],
                        "puntos_acumulados": resultado_puntos['puntos_acumulados'],
                        "nivel_actual": resultado_puntos['nivel_actual'],
                        "nuevas_insignias": resultado_puntos['nuevas_insignias']
                    }
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error procesando entrega con IA: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al procesar entrega con IA: {str(e)}"
            )
    
    @staticmethod
    async def obtener_retroalimentacion_ia(
        db: Session,
        entrega_id: str,
        usuario: Usuario
    ) -> Dict[str, Any]:
        """
        Obtiene la retroalimentación de IA para una entrega.
        
        Args:
            db: Sesión de base de datos
            entrega_id: ID de la entrega
            usuario: Usuario que consulta
        
        Returns:
            Dict con retroalimentación completa
        """
        
        try:
            # Obtener entrega con retroalimentación
            query = text("""
                SELECT 
                    et.entrega_id,
                    et.estudiante_id,
                    et.calificacion_preliminar_ia,
                    et.retroalimentacion_ia,
                    et.puntos_otorgados,
                    et.intentos,
                    et.es_tardia,
                    et.fecha_entrega,
                    t.titulo as tarea_titulo,
                    t.tarea_id
                FROM entregas_tareas et
                JOIN tareas t ON et.tarea_id = t.tarea_id
                WHERE et.entrega_id = :entrega_id
            """)
            
            result = db.execute(query, {"entrega_id": entrega_id}).fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Entrega no encontrada"
                )
            
            entrega_data = dict(result._mapping)
            
            # Validar permisos
            if (usuario.rol == "estudiante" and 
                str(entrega_data['estudiante_id']) != str(usuario.usuario_id)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permiso para ver esta retroalimentación"
                )
            
            return {
                "success": True,
                "data": {
                    "entrega_id": str(entrega_data['entrega_id']),
                    "tarea_titulo": entrega_data['tarea_titulo'],
                    "calificacion_ia": entrega_data['calificacion_preliminar_ia'],
                    "retroalimentacion": entrega_data['retroalimentacion_ia'],
                    "puntos_otorgados": entrega_data['puntos_otorgados'],
                    "intentos": entrega_data['intentos'],
                    "es_tardia": entrega_data['es_tardia'],
                    "fecha_entrega": entrega_data['fecha_entrega'].isoformat() if entrega_data['fecha_entrega'] else None
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo retroalimentación IA: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener retroalimentación: {str(e)}"
            )
    
    async def obtener_estadisticas_ia_tarea(
        db: Session,
        tarea_id: str,
        docente_id: UUID
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas agregadas de IA para todas las entregas de una tarea.
        
        Solo para docentes del curso.
        
        Args:
            db: Sesión de base de datos
            tarea_id: ID de la tarea
            docente_id: ID del docente que consulta
        
        Returns:
            Dict con estadísticas de calificaciones, fortalezas, áreas de mejora
        """
        
        try:
            # Validar que el docente tiene permisos sobre esta tarea
            query_tarea = text("""
                SELECT t.tarea_id, t.titulo, c.docente_id
                FROM tareas t
                JOIN cursos c ON t.curso_id = c.curso_id
                WHERE t.tarea_id = :tarea_id
            """)
            
            tarea_result = db.execute(query_tarea, {"tarea_id": tarea_id}).fetchone()
            
            if not tarea_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tarea no encontrada"
                )
            
            tarea_data = dict(tarea_result._mapping)
            
            if str(tarea_data['docente_id']) != str(docente_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permisos para ver estas estadísticas"
                )
            
            # Obtener todas las entregas con retroalimentación de IA
            query_entregas = text("""
                SELECT 
                    et.entrega_id,
                    et.calificacion_preliminar_ia,
                    et.retroalimentacion_ia,
                    et.puntos_otorgados,
                    et.es_tardia
                FROM entregas_tareas et
                WHERE et.tarea_id = :tarea_id
                  AND et.retroalimentacion_ia IS NOT NULL
            """)
            
            entregas = db.execute(query_entregas, {"tarea_id": tarea_id}).fetchall()
            
            if not entregas:
                return {
                    "tarea_id": tarea_id,
                    "tarea_titulo": tarea_data['titulo'],
                    "total_entregas": 0,
                    "estadisticas": {
                        "calificacion_promedio": None,
                        "calificacion_maxima": None,
                        "calificacion_minima": None,
                        "puntos_promedio": None,
                        "entregas_tardias": 0,
                        "fortalezas_comunes": [],
                        "areas_mejora_comunes": []
                    }
                }
            
            # Procesar estadísticas
            calificaciones = []
            puntos = []
            tardias = 0
            fortalezas_todas = []
            areas_mejora_todas = []
            
            for entrega in entregas:
                entrega_data = dict(entrega._mapping)
                
                if entrega_data['calificacion_preliminar_ia']:
                    calificaciones.append(float(entrega_data['calificacion_preliminar_ia']))
                
                if entrega_data['puntos_otorgados']:
                    puntos.append(int(entrega_data['puntos_otorgados']))
                
                if entrega_data['es_tardia']:
                    tardias += 1
                
                # Extraer fortalezas y áreas de mejora del JSON
                if entrega_data['retroalimentacion_ia']:
                    import json
                    try:
                        retro = json.loads(entrega_data['retroalimentacion_ia'])
                        if isinstance(retro, dict):
                            fortalezas_todas.extend(retro.get('fortalezas', []))
                            areas_mejora_todas.extend(retro.get('areas_mejora', []))
                    except:
                        pass
            
            # Calcular estadísticas
            from collections import Counter
            
            estadisticas = {
                "calificacion_promedio": round(sum(calificaciones) / len(calificaciones), 2) if calificaciones else None,
                "calificacion_maxima": max(calificaciones) if calificaciones else None,
                "calificacion_minima": min(calificaciones) if calificaciones else None,
                "puntos_promedio": round(sum(puntos) / len(puntos), 1) if puntos else None,
                "puntos_maximos": max(puntos) if puntos else None,
                "puntos_minimos": min(puntos) if puntos else None,
                "entregas_tardias": tardias,
                "porcentaje_tardias": round((tardias / len(entregas)) * 100, 1) if entregas else 0,
                "fortalezas_comunes": [
                    {"texto": item, "frecuencia": count}
                    for item, count in Counter(fortalezas_todas).most_common(5)
                ],
                "areas_mejora_comunes": [
                    {"texto": item, "frecuencia": count}
                    for item, count in Counter(areas_mejora_todas).most_common(5)
                ]
            }
            
            return {
                "tarea_id": tarea_id,
                "tarea_titulo": tarea_data['titulo'],
                "total_entregas": len(entregas),
                "estadisticas": estadisticas
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de IA: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener estadísticas: {str(e)}"
            )


# Instancia global del servicio
tarea_service = TareaService()
