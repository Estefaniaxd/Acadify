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
        tipo: Optional[str] = "ejercicios",
        prioridad: Optional[str] = "media",
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
                    tarea_id, docente_id, titulo, descripcion, fecha_limite,
                    puntuacion_maxima, tipo, prioridad, grupo_id,
                    creado_por, fecha_creacion
                )
                VALUES (
                    gen_random_uuid()::text, :docente_id, :titulo, :descripcion, :fecha_limite,
                    :puntuacion_maxima, CAST(:tipo AS tipo_tarea), CAST(:prioridad AS prioridad_tarea), :grupo_id,
                    :creado_por, :fecha_creacion
                )
                RETURNING tarea_id
            """)
            
            # Obtener el grupo_id correspondiente al curso_id
            grupo_query = text("""
                SELECT grupo_id FROM "GrupoCurso" 
                WHERE curso_id = :curso_id AND docente_id = :docente_id
                LIMIT 1
            """)
            
            grupo_result = db.execute(grupo_query, {
                "curso_id": curso_id,
                "docente_id": usuario.usuario_id
            }).fetchone()
            
            if not grupo_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontró un grupo asignado para este curso"
                )
            
            grupo_id = grupo_result[0]
            
            result = db.execute(query, {
                "docente_id": usuario.usuario_id,
                "titulo": titulo,
                "descripcion": descripcion,
                "fecha_limite": fecha_limite,
                "puntuacion_maxima": puntos_max,
                "tipo": tipo or "ejercicios",
                "prioridad": prioridad or "media",
                "grupo_id": grupo_id,  # Usar el grupo_id obtenido
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
            
            # Obtener el grupo_id correspondiente al curso_id
            grupo_query = text("""
                SELECT grupo_id FROM "GrupoCurso" 
                WHERE curso_id = :curso_id AND docente_id = :docente_id
                LIMIT 1
            """)
            
            grupo_result = db.execute(grupo_query, {
                "curso_id": curso_id,
                "docente_id": usuario.usuario_id
            }).fetchone()
            
            if not grupo_result:
                # Si no es docente del curso, intentar como estudiante
                grupo_query_estudiante = text("""
                    SELECT gc.grupo_id FROM "GrupoCurso" gc
                    JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id
                    WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
                    LIMIT 1
                """)
                
                grupo_result = db.execute(grupo_query_estudiante, {
                    "curso_id": curso_id,
                    "usuario_id": usuario.usuario_id
                }).fetchone()
                
                if not grupo_result:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes acceso a este curso"
                    )
            
            grupo_id = grupo_result[0]
            
            # Query optimizada con información de entrega
            fecha_actual = datetime.now(timezone.utc)
            
            query = text("""
                SELECT 
                    t.tarea_id,
                    t.titulo,
                    t.descripcion,
                    t.fecha_limite,
                    t.puntuacion_maxima as puntos_base,
                    t.tipo as tipo,
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
                LEFT JOIN LATERAL (
                    SELECT entrega_id, estado, calificacion
                    FROM entregas_tareas
                    WHERE tarea_id = t.tarea_id 
                      AND estudiante_id = :usuario_id
                    ORDER BY fecha_entrega DESC
                    LIMIT 1
                ) mi_entrega ON true
                WHERE t.grupo_id = :grupo_id
                    AND (:incluir_vencidas OR t.fecha_limite >= :fecha_actual)
                GROUP BY t.tarea_id, u.usuario_id, mi_entrega.entrega_id, 
                         mi_entrega.estado, mi_entrega.calificacion
                ORDER BY t.fecha_limite ASC
                LIMIT :limit OFFSET :offset
            """)
            
            result = db.execute(query, {
                "grupo_id": grupo_id,
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
                WHERE grupo_id = :grupo_id
                    AND (:incluir_vencidas OR fecha_limite >= :fecha_actual)
            """)
            
            total = db.execute(count_query, {
                "grupo_id": grupo_id,
                "fecha_actual": fecha_actual,
                "incluir_vencidas": incluir_vencidas
            }).scalar()
            
            tareas = [dict(row._mapping) for row in result]
            
            logger.info(f"📊 TAREAS ENCONTRADAS: {len(tareas)} tareas para grupo_id={grupo_id}, curso_id={curso_id}")
            logger.info(f"   Tareas: {[t['titulo'] for t in tareas]}")
            
            # Enriquecer con información adicional
            for tarea in tareas:
                tarea['dias_restantes'] = TareaService._calcular_dias_restantes(
                    tarea['fecha_limite']
                )
                tarea['puede_entregar'] = TareaService._puede_entregar(
                    tarea['estado_tiempo'],
                    tarea.get('mi_estado_entrega')
                )
            
            logger.info(f"✅ Devolviendo {len(tareas)} tareas al frontend")
            
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
    def obtener_tarea(
        db: Session,
        tarea_id: str,
        usuario: Usuario
    ) -> Dict[str, Any]:
        """
        Obtiene los detalles de una tarea específica
        
        Args:
            db: Sesión de base de datos
            tarea_id: ID de la tarea
            usuario: Usuario que consulta
            
        Returns:
            Dict con los detalles de la tarea
        """
        try:
            # 1. Obtener información básica de la tarea y verificar existencia
            query_info = text("""
                SELECT t.grupo_id, t.fecha_limite
                FROM tareas t
                WHERE t.tarea_id = :tarea_id
            """)
            
            result_info = db.execute(query_info, {"tarea_id": tarea_id}).fetchone()
            
            if not result_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tarea no encontrada"
                )
                
            grupo_id = result_info[0]
            
            # 2. Validar acceso al curso/grupo
            # Si es estudiante, debe estar inscrito en el grupo
            # Si es docente, debe ser docente del curso asociado al grupo
            
            if usuario.rol == "estudiante":
                query_acceso = text("""
                    SELECT 1 FROM "EstudianteGrupo"
                    WHERE grupo_id = :grupo_id AND estudiante_id = :usuario_id
                """)
                if not db.execute(query_acceso, {"grupo_id": grupo_id, "usuario_id": usuario.usuario_id}).fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes acceso a esta tarea"
                    )
            else:
                # Docente/Coordinador
                query_acceso = text("""
                    SELECT 1 FROM "GrupoCurso" gc
                    WHERE gc.grupo_id = :grupo_id AND (gc.docente_id = :usuario_id OR :rol = 'coordinador')
                """)
                if not db.execute(query_acceso, {
                    "grupo_id": grupo_id, 
                    "usuario_id": usuario.usuario_id,
                    "rol": usuario.rol
                }).fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes acceso a esta tarea"
                    )

            # 3. Obtener detalles completos
            fecha_actual = datetime.now(timezone.utc)
            
            query = text("""
                SELECT 
                    t.tarea_id,
                    t.titulo,
                    t.descripcion,
                    t.fecha_limite,
                    t.puntuacion_maxima as puntos_base,
                    t.tipo as tipo,
                    t.fecha_creacion,
                    t.grupo_id,
                    t.prioridad,
                    u.nombres || ' ' || u.apellidos as creador_nombre,
                    CASE 
                        WHEN t.fecha_limite < :fecha_actual THEN 'vencida'
                        WHEN t.fecha_limite < :fecha_actual + INTERVAL '24 hours' THEN 'proxima'
                        ELSE 'activa'
                    END as estado_tiempo,
                    COALESCE(mi_entrega.entrega_id, NULL) as mi_entrega_id,
                    COALESCE(mi_entrega.estado, NULL) as mi_estado_entrega,
                    COALESCE(mi_entrega.calificacion, NULL) as mi_calificacion,
                    COALESCE(mi_entrega.retroalimentacion_docente, NULL) as mi_retroalimentacion
                FROM tareas t
                JOIN "Usuario" u ON t.creado_por = u.usuario_id
                LEFT JOIN LATERAL (
                    SELECT entrega_id, estado, calificacion, retroalimentacion_docente
                    FROM entregas_tareas
                    WHERE tarea_id = t.tarea_id 
                      AND estudiante_id = :usuario_id
                    ORDER BY fecha_entrega DESC
                    LIMIT 1
                ) mi_entrega ON true
                WHERE t.tarea_id = :tarea_id
            """)
            
            result = db.execute(query, {
                "tarea_id": tarea_id,
                "usuario_id": usuario.usuario_id,
                "fecha_actual": fecha_actual
            }).fetchone()
            
            tarea = dict(result._mapping)
            
            # Enriquecer con información adicional
            tarea['dias_restantes'] = TareaService._calcular_dias_restantes(tarea['fecha_limite'])
            tarea['puede_entregar'] = TareaService._puede_entregar(
                tarea['estado_tiempo'],
                tarea.get('mi_estado_entrega')
            )
            
            return tarea
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo tarea {tarea_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener tarea: {str(e)}"
            )

    @staticmethod
    def entregar_tarea(
        db: Session,
        tarea_id: str,
        usuario: Usuario,
        contenido: str,
        archivo_url: Optional[str] = None,
        archivo_urls: Optional[list] = None,
        archivos_metadata: Optional[list] = None,
        enlaces_externos: Optional[list] = None  # ← Enlaces externos
    ) -> Dict[str, Any]:
        """
        Registra la entrega de una tarea por un estudiante
        
        Args:
            db: Sesión de base de datos
            tarea_id: ID de la tarea
            usuario: Estudiante que entrega
            contenido: Contenido de la entrega
            archivo_url: URL del archivo adjunto principal
            archivo_urls: Lista de todas las URLs de archivos
            archivos_metadata: Lista con metadata (url, nombre_original, nombre_almacenado)
            enlaces_externos: Lista de enlaces externos [{url, titulo}]
            
        Returns:
            Dict con la entrega registrada
        """
        try:
            import json
            
            # Permitir entregas vacías para poder actualizar solo archivos o comentarios
            # No validar contenido obligatorio
            
            # Validaciones
            TareaService._validar_puede_entregar(db, tarea_id, usuario)
            
            # Verificar si ya entregó
            entrega_existente = TareaService._obtener_mi_entrega(db, tarea_id, usuario.usuario_id)
            
            # Preparar JSON con archivos adicionales (con metadata)
            archivos_json = None
            if archivos_metadata is not None:
                # Si se pasa una lista (vacía o no), usarla. Esto permite borrar archivos enviando lista vacía.
                archivos_json = json.dumps({"archivos": archivos_metadata})
                if len(archivos_metadata) > 0:
                    logger.info(f"   ✅ archivos_json creado con {len(archivos_metadata)} archivos:")
                    logger.info(f"      {archivos_json[:300]}")
                else:
                    logger.info(f"   ⚠️ Lista de archivos vacía (se eliminarán los archivos existentes)")
            elif archivo_urls and len(archivo_urls) > 0:
                # Fallback: si no hay metadata, usar solo URLs
                archivos_json = json.dumps({
                    "archivos": [{"url": url, "nombre": url.split("/")[-1]} for url in archivo_urls]
                })
                logger.info(f"   ⚠️ Usando fallback URL con {len(archivo_urls)} archivos")
            else:
                # ✅ FIX #4: Si no hay archivos nuevos, reusar de entrega cancelada anterior
                logger.info(f"   ⚠️ Sin archivos nuevos")
                
            # Si no hay archivos nuevos pero hay una entrega cancelada, reusar archivos
            if not archivos_json and entrega_existente and entrega_existente.get('estado') == 'cancelada':
                if entrega_existente.get('archivos_adicionales'):
                    # ✅ CRÍTICO: Verificar si ya es string o dict
                    archivos_anteriores = entrega_existente['archivos_adicionales']
                    
                    if isinstance(archivos_anteriores, str):
                        # Ya es JSON string, usar directamente
                        archivos_json = archivos_anteriores
                        logger.info(f"   ♻️ Reusando archivos (ya en formato JSON string)")
                    elif isinstance(archivos_anteriores, dict):
                        # Es dict, convertir a JSON string
                        try:
                            archivos_json = json.dumps(archivos_anteriores)
                            archivos_data = archivos_anteriores
                            archivos_count = len(archivos_data.get('archivos', [])) if isinstance(archivos_data, dict) else 0
                            logger.info(f"   ♻️ REUSANDO {archivos_count} archivos de entrega cancelada {entrega_existente['entrega_id']}")
                        except Exception as e:
                            logger.error(f"   ❌ Error convirtiendo archivos anteriores a JSON: {e}")
                            archivos_json = None
                    else:
                        logger.warning(f"   ⚠️ Tipo inesperado para archivos_adicionales: {type(archivos_anteriores)}")
                        archivos_json = None
                else:
                    logger.info(f"   ⚠️ Entrega cancelada no tiene archivos para reusar")
            
            
            # Preparar enlaces externos como JSON (ANTES de la lógica de actualizar/crear)
            enlaces_json = None
            if enlaces_externos is not None:
                # Si se pasa una lista (vacía o no), usarla. Esto permite borrar enlaces enviando lista vacía.
                enlaces_json = json.dumps(enlaces_externos)
                logger.info(f"   🔗 Enlaces externos a guardar: {len(enlaces_externos)}")
            
            # ✅ FIX CRÍTICO: Actualizar entrega existente (incluso si está cancelada)
            # En vez de crear múltiples entregas, reutilizar la cancelada
            if entrega_existente:
                logger.info(f"   🔄 Actualizando entrega existente: {entrega_existente['entrega_id']} (estado: {entrega_existente.get('estado')})")
                return TareaService._actualizar_entrega(
                    db, entrega_existente['entrega_id'], contenido, archivo_url, archivos_json, enlaces_json
                )
            
            # Crear nueva entrega
            query = text("""
                INSERT INTO entregas_tareas (
                    entrega_id, tarea_id, estudiante_id, contenido_texto, archivo_url,
                    archivos_adicionales, enlaces_externos, fecha_entrega, estado
                )
                VALUES (
                    gen_random_uuid()::text, :tarea_id, :estudiante_id, :contenido, :archivo_url,
                    :archivos_adicionales::json, :enlaces_externos::json, :fecha_entrega, 'entregada'
                )
                RETURNING entrega_id
            """)
            
            result = db.execute(query, {
                "tarea_id": tarea_id,
                "estudiante_id": usuario.usuario_id,
                "contenido": contenido,
                "archivo_url": archivo_url,
                "archivos_adicionales": archivos_json,
                "enlaces_externos": enlaces_json,
                "fecha_entrega": datetime.now(timezone.utc)
            })
            
            entrega_id = result.fetchone()[0]
            db.commit()
            
            logger.info(f"Tarea entregada: {tarea_id} por {usuario.usuario_id} - {len(archivo_urls or [])} archivos, {len(enlaces_externos or [])} enlaces")
            
            # ✅ FIX: Devolver archivos reales (incluyendo reutilizados de entrega cancelada)
            archivos_response = archivos_metadata or []
            if not archivos_response and archivos_json:
                # Si no hay archivos_metadata pero sí archivos_json (reutilizados), parsear
                try:
                    archivos_data = json.loads(archivos_json) if isinstance(archivos_json, str) else archivos_json
                    archivos_response = archivos_data.get('archivos', []) if isinstance(archivos_data, dict) else []
                except:
                    archivos_response = []
            
            # ✅ FIX: Devolver enlaces también
            enlaces_response = enlaces_externos or []
            
            return {
                "success": True,
                "message": "Tarea entregada exitosamente",
                "data": {
                    "entrega_id": str(entrega_id),
                    "fecha_entrega": datetime.now(timezone.utc).isoformat(),
                    "estado": "entregada",
                    "archivos": archivos_response,
                    "enlaces": enlaces_response
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
    def obtener_entrega(
        db: Session,
        entrega_id: str,
        usuario: Usuario
    ) -> Dict[str, Any]:
        """
        Obtiene los detalles de una entrega específica
        """
        try:
            import json
            
            # Consulta con nombres de columnas exactos según esquema de BD
            query = text("""
                SELECT 
                    et.entrega_id,
                    et.tarea_id,
                    et.estudiante_id,
                    et.titulo_entrega,
                    et.descripcion_entrega,
                    et.comentarios_estudiante,
                    et.archivo_url,
                    et.archivos_adicionales,
                    et.contenido_texto,
                    et.enlaces_externos,
                    et.fecha_entrega,
                    et.fecha_limite_original,
                    et.numero_intento,
                    et.es_entrega_tardia,
                    et.calificacion,
                    et.calificacion_letras,
                    et.comentarios_docente,
                    et.rubrica_calificacion,
                    et.estado,
                    et.es_final,
                    et.requiere_revision,
                    et.tiempo_empleado,
                    et.dificultad_percibida,
                    et.satisfaccion_estudiante,
                    et.fecha_creacion,
                    et.fecha_actualizacion,
                    et.calificado_por,
                    et.fecha_calificacion
                FROM entregas_tareas et
                WHERE et.entrega_id = :entrega_id
            """)

            result = db.execute(query, {"entrega_id": entrega_id}).fetchone()

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Entrega no encontrada"
                )
            
            # Convertir resultado a diccionario
            entrega = dict(result._mapping)
            
            # Convertir UUIDs a strings para que sean serializables a JSON
            # PostgreSQL retorna UUIDs como objetos uuid.UUID que no son serializables
            for key in ['entrega_id', 'tarea_id', 'estudiante_id', 'calificado_por']:
                if key in entrega and entrega[key] is not None:
                    entrega[key] = str(entrega[key])
            
            # Convertir timestamps a ISO format strings para serialización JSON
            for key in ['fecha_entrega', 'fecha_limite_original', 'fecha_creacion', 'fecha_actualizacion', 'fecha_calificacion']:
                if key in entrega and entrega[key] is not None:
                    entrega[key] = entrega[key].isoformat() if hasattr(entrega[key], 'isoformat') else str(entrega[key])
            
            # Convertir campos de string para asegurar que sean strings (no objetos especiales)
            for key in ['titulo_entrega', 'descripcion_entrega', 'comentarios_estudiante', 'archivo_url', 'contenido_texto', 'calificacion_letras', 'comentarios_docente', 'estado']:
                if key in entrega and entrega[key] is not None and not isinstance(entrega[key], str):
                    entrega[key] = str(entrega[key])
            
            # Convertir campos numéricos a int o float según corresponda
            if 'numero_intento' in entrega and entrega['numero_intento'] is not None:
                entrega['numero_intento'] = int(entrega['numero_intento'])
            if 'calificacion' in entrega and entrega['calificacion'] is not None:
                entrega['calificacion'] = float(entrega['calificacion'])
            if 'tiempo_empleado' in entrega and entrega['tiempo_empleado'] is not None:
                entrega['tiempo_empleado'] = int(entrega['tiempo_empleado'])
            if 'dificultad_percibida' in entrega and entrega['dificultad_percibida'] is not None:
                entrega['dificultad_percibida'] = int(entrega['dificultad_percibida'])
            if 'satisfaccion_estudiante' in entrega and entrega['satisfaccion_estudiante'] is not None:
                entrega['satisfaccion_estudiante'] = int(entrega['satisfaccion_estudiante'])
            
            # Convertir booleanos
            for key in ['es_entrega_tardia', 'es_final', 'requiere_revision']:
                if key in entrega and entrega[key] is not None:
                    entrega[key] = bool(entrega[key])
            
            # Parsear archivos_adicionales JSON y preparar lista completa de archivos
            # IMPORTANTE: SIEMPRE usar archivos_adicionales como fuente de verdad (nunca archivo_url)
            # archivo_url es un campo legado que solo contiene el PRIMER archivo
            archivos_lista = []
            
            # ✅ FIX #4: LOGGING DETALLADO + DEFENSIVE CHECKS para diagnóstico
            logger.info(f"🔍 PARSEANDO ARCHIVOS para entrega {entrega_id}:")
            logger.info(f"   - archivos_adicionales type: {type(entrega.get('archivos_adicionales'))}")
            logger.info(f"   - archivos_adicionales existe: {bool(entrega.get('archivos_adicionales'))}")
            
            # Defensive check: asegurar que archivos_adicionales existe y no es None
            if entrega.get('archivos_adicionales') is not None and entrega.get('archivos_adicionales') != '':
                # Log del JSON raw
                raw_json = entrega['archivos_adicionales']
                logger.info(f"   - Raw JSON (primeros 500 chars): {raw_json[:500] if isinstance(raw_json, str) else str(raw_json)[:500]}")
                
                try:
                    # Defensive: si ya es dict, no parsear
                    if isinstance(raw_json, dict):
                        archivos_data = raw_json
                        logger.info(f"   ✅ Ya es dict, no requiere parseo")
                    else:
                        archivos_data = json.loads(entrega['archivos_adicionales'])
                        logger.info(f"   ✅ JSON parseado correctamente")
                    
                    logger.info(f"   - Tipo de datos parseados: {type(archivos_data)}")
                    logger.info(f"   - Tiene key 'archivos': {isinstance(archivos_data, dict) and 'archivos' in archivos_data}")
                    
                    # Defensive: verificar estructura esperada
                    if isinstance(archivos_data, dict) and 'archivos' in archivos_data:
                        archivos_array = archivos_data['archivos']
                        
                        # Defensive: asegurar que es lista
                        if not isinstance(archivos_array, list):
                            logger.warning(f"   ⚠️ archivos_array NO es lista: {type(archivos_array)}")
                            archivos_array = []
                        
                        logger.info(f"   - Total archivos en array: {len(archivos_array)}")
                        
                        # Iterar sobre TODOS los archivos en metadata
                        for idx, archivo in enumerate(archivos_array, 1):
                            logger.info(f"      📄 Archivo {idx}:")
                            logger.info(f"         - Type: {type(archivo)}")
                            
                            # Defensive: manejar diferentes formatos
                            if isinstance(archivo, dict) and 'url' in archivo:
                                logger.info(f"         - Keys disponibles: {archivo.keys()}")
                                logger.info(f"         - url: {archivo['url']}")
                                logger.info(f"         - nombre_original: {archivo.get('nombre_original')}")
                                logger.info(f"         - nombre: {archivo.get('nombre')}")
                                
                                # ✅ FIX #2 y #3: GARANTIZAR que nombre_original esté disponible
                                nombre_original = archivo.get('nombre_original')
                                nombre = archivo.get('nombre')
                                url_filename = archivo['url'].split("/")[-1] if archivo.get('url') else f"archivo_{idx}"
                                
                                # Priorizar nombre_original, luego nombre, luego extraer de URL
                                nombre_final = nombre_original or nombre or url_filename
                                
                                logger.info(f"         ➡️ Nombre final elegido: {nombre_final}")
                                
                                archivos_lista.append({
                                    "url": archivo['url'],
                                    "nombre": nombre_final,
                                    "nombre_original": nombre_original or nombre or url_filename,
                                    "nombre_almacenado": archivo.get('nombre_almacenado', url_filename)
                                })
                            elif isinstance(archivo, str):
                                # Formato legacy: solo URL como string
                                logger.info(f"         - Es string (URL): {archivo}")
                                archivos_lista.append({
                                    "url": archivo,
                                    "nombre": archivo.split("/")[-1],
                                    "nombre_original": archivo.split("/")[-1]
                                })
                            else:
                                logger.warning(f"         ⚠️ Formato inesperado de archivo: {archivo}")
                        
                        logger.info(f"   ✅ Total archivos procesados: {len(archivos_lista)}")
                    else:
                        logger.warning(f"   ⚠️ JSON no tiene estructura esperada {{archivos: [...]}}")
                        logger.warning(f"   ⚠️ Estructura recibida: {archivos_data}")
                        
                except (json.JSONDecodeError, TypeError) as e:
                    logger.error(f"   ❌ Error parseando JSON: {type(e).__name__}: {str(e)}")
                    # Fallback a archivo_url si existe
                    if entrega.get('archivo_url'):
                        logger.info(f"   ➡️ Fallback a archivo_url: {entrega['archivo_url']}")
                        archivos_lista.append({
                            "url": entrega['archivo_url'],
                            "nombre": entrega['archivo_url'].split("/")[-1],
                            "nombre_original": entrega['archivo_url'].split("/")[-1]
                        })
            elif entrega.get('archivo_url'):
                # Fallback: si no hay archivos_adicionales, usar archivo_url (legado)
                logger.info(f"   ⚠️ No hay archivos_adicionales, usando archivo_url...")
                archivos_lista.append({
                    "url": entrega['archivo_url'],
                    "nombre": entrega['archivo_url'].split("/")[-1],
                    "nombre_original": entrega['archivo_url'].split("/")[-1]
                })
            else:
                logger.info(f"   ⚠️ No hay archivos en esta entrega")
            
            # Agregar lista completa de archivos a la respuesta
            entrega['archivos'] = archivos_lista
            logger.info(f"🔍 RESULTADO FINAL: {len(archivos_lista)} archivos en entrega['archivos']")

            
            # 2. Validar permisos
            # Estudiante: Solo su propia entrega
            # Docente: Debe ser docente del curso
            
            if usuario.rol == "estudiante":
                # Los UUIDs ya se convirtieron a strings arriba
                if entrega['estudiante_id'] != str(usuario.usuario_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No tienes permiso para ver esta entrega"
                    )
            else:
                # Para docentes, obtener grupo_id de la tarea
                query_grupo = text("SELECT grupo_id FROM tareas WHERE tarea_id = :tarea_id")
                grupo_result = db.execute(query_grupo, {"tarea_id": entrega['tarea_id']}).fetchone()
                
                if grupo_result:
                    grupo_id = grupo_result[0]
                    # Verificar si es docente del curso
                    query_acceso = text("""
                        SELECT 1 FROM "GrupoCurso" gc
                        WHERE gc.grupo_id = :grupo_id AND (gc.docente_id = :usuario_id OR :rol = 'coordinador')
                    """)
                    if not db.execute(query_acceso, {
                        "grupo_id": grupo_id, 
                        "usuario_id": usuario.usuario_id,
                        "rol": usuario.rol
                    }).fetchone():
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes acceso a esta entrega"
                        )
            
            # PASO CRÍTICO: Convertir archivos_adicionales de JSON string a dict
            if isinstance(entrega.get('archivos_adicionales'), str):
                try:
                    entrega['archivos_adicionales'] = json.loads(entrega['archivos_adicionales'])
                except (json.JSONDecodeError, TypeError):
                    entrega['archivos_adicionales'] = None
            
            # PASO CRÍTICO: Convertir enlaces_externos de JSON string a list si es necesario
            logger.info(f"🔗 DEBUG enlaces_externos RAW: {entrega.get('enlaces_externos')} (type: {type(entrega.get('enlaces_externos'))})")
            enlaces_raw = entrega.get('enlaces_externos')
            
            if enlaces_raw is None:
                logger.info(f"🔗 DEBUG enlaces_externos es NULL en BD")
                entrega['enlaces_externos'] = None
            elif isinstance(enlaces_raw, list):
                # Ya es lista, no parsear
                logger.info(f"🔗 DEBUG enlaces_externos ya es lista: {enlaces_raw}")
                entrega['enlaces_externos'] = enlaces_raw
            elif isinstance(enlaces_raw, str):
                # Es string, parsear a JSON
                try:
                    entrega['enlaces_externos'] = json.loads(enlaces_raw)
                    logger.info(f"🔗 DEBUG enlaces_externos PARSED: {entrega['enlaces_externos']}")
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"🔗 DEBUG enlaces_externos PARSE ERROR: {e}")
                    entrega['enlaces_externos'] = None
            else:
                logger.warning(f"🔗 DEBUG enlaces_externos tipo inesperado: {type(enlaces_raw)}")
                entrega['enlaces_externos'] = None
            
            # PASO CRÍTICO: Convertir rubrica_calificacion de JSON string a dict si es necesario
            if isinstance(entrega.get('rubrica_calificacion'), str):
                try:
                    entrega['rubrica_calificacion'] = json.loads(entrega['rubrica_calificacion'])
                except (json.JSONDecodeError, TypeError):
                    entrega['rubrica_calificacion'] = None
            
            # LOG FINAL: Verificar tipos antes de retornar
            logger.info(f"🔍 TIPOS FINALES antes de retornar entrega {entrega_id}:")
            for key, value in entrega.items():
                tipo = type(value).__name__
                logger.info(f"   {key}: {tipo}")
            
            return entrega
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo entrega {entrega_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener entrega: {str(e)}"
            )

    @staticmethod
    def cancelar_entrega(
        db: Session,
        entrega_id: str,
        usuario: Usuario
    ) -> Dict[str, Any]:
        """
        Cancela/elimina una entrega de tarea.
        
        Validaciones:
        - Solo el estudiante propietario puede cancelar
        - No se puede cancelar si ya está calificada
        - Solo estudiantes pueden cancelar (no profesores)
        """
        try:
            # 1. Obtener la entrega
            query = text("""
                SELECT entrega_id, estudiante_id, estado, calificacion
                FROM entregas_tareas
                WHERE entrega_id = :entrega_id
            """)
            
            result = db.execute(query, {"entrega_id": entrega_id}).fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Entrega no encontrada"
                )
            
            entrega = dict(result._mapping)
            
            # 2. Validar que es el estudiante propietario
            if str(entrega['estudiante_id']) != str(usuario.usuario_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Solo puedes cancelar tus propias entregas"
                )
            
            # 3. Validar que no esté calificada
            if entrega['calificacion'] is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No puedes cancelar una entrega que ya ha sido calificada"
                )
            
            # 4. Cambiar estado a 'cancelada' PRESERVANDO archivos_adicionales
            # Así el estudiante puede ver sus archivos anteriores como referencia
            update_query = text("""
                UPDATE entregas_tareas
                SET estado = 'cancelada'
                WHERE entrega_id = :entrega_id
            """)
            
            db.execute(update_query, {"entrega_id": entrega_id})
            db.commit()
            
            logger.info(f"Entrega cancelada: {entrega_id} por {usuario.usuario_id} - Archivos preservados para referencia")
            
            return {
                "success": True,
                "message": "Entrega cancelada exitosamente. Ahora puedes volver a entregar la tarea.",
                "data": {
                    "entrega_id": entrega_id,
                    "cancelada": True
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error cancelando entrega {entrega_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al cancelar entrega: {str(e)}"
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
                    u.nombres as estudiante_nombre,
                    u.apellidos as estudiante_apellido,
                    u.correo_institucional as estudiante_email,
                    et.fecha_entrega as fecha_envio,
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
                JOIN "Usuario" u ON CAST(et.estudiante_id AS UUID) = u.usuario_id
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
        """Valida que el usuario sea docente del curso a través de GrupoCurso"""
        if usuario.rol != "docente" and usuario.rol != "coordinador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo docentes pueden crear tareas"
            )
        
        # Verificar que existe un grupo para este curso y que el docente está asignado
        query = text("""
            SELECT gc.grupo_id
            FROM "GrupoCurso" gc
            WHERE gc.curso_id = :curso_id AND gc.docente_id = :docente_id
            LIMIT 1
        """)
        
        result = db.execute(query, {
            "curso_id": curso_id,
            "docente_id": usuario.usuario_id
        }).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No eres docente de este curso o el curso no tiene un grupo asignado"
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

        # Defensive: fecha_limite puede ser NULL en BD -> prevenir TypeError
        fecha_limite = result[0]
        logger.debug(f"Validando fecha_limite para tarea {tarea_id}: {fecha_limite!r}")

        if fecha_limite is None:
            logger.error(f"La tarea {tarea_id} no tiene 'fecha_limite' configurada")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Tarea inválida: fecha límite no configurada"
            )

        # Note: We allow late submissions but mark them as late in the database
        # The frontend can show a warning, but we don't block the submission
    
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
        """Obtiene la entrega MÁS RECIENTE del estudiante para una tarea"""
        query = text("""
            SELECT entrega_id, estado, fecha_entrega
            FROM entregas_tareas
            WHERE tarea_id = :tarea_id 
              AND estudiante_id = :estudiante_id
            ORDER BY fecha_entrega DESC
            LIMIT 1
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
        archivo_url: Optional[str],
        archivos_json: Optional[str] = None,
        enlaces_json: Optional[str] = None
    ) -> Dict[str, Any]:
        """Actualiza una entrega existente"""
        
        # ✅ LÓGICA CORRECTA: REEMPLAZAR archivos/enlaces, NO merge
        # Si el usuario envía nuevos archivos/enlaces → REEMPLAZAR los anteriores
        # Si NO envía nada → MANTENER los anteriores (solo si archivos_json/enlaces_json son None)
        
        # Solo preservar si explícitamente NO se enviaron nuevos (None, no vacío)
        if archivos_json is None:
            # Usuario no envió archivos nuevos → mantener anteriores
            query_prev = text("SELECT archivos_adicionales FROM entregas_tareas WHERE entrega_id = :entrega_id")
            prev_data = db.execute(query_prev, {"entrega_id": entrega_id}).fetchone()
            if prev_data and prev_data[0]:
                archivos_prev = prev_data[0]
                archivos_json = json.dumps(archivos_prev) if isinstance(archivos_prev, dict) else archivos_prev
                logger.info(f"   ♻️ Preservando archivos anteriores (usuario no envió nuevos)")
        else:
            logger.info(f"   🔄 REEMPLAZANDO archivos anteriores con nuevos")
        
        if enlaces_json is None:
            # Usuario no envió enlaces nuevos → mantener anteriores
            query_prev_enlaces = text("SELECT enlaces_externos FROM entregas_tareas WHERE entrega_id = :entrega_id")
            prev_enlaces = db.execute(query_prev_enlaces, {"entrega_id": entrega_id}).fetchone()
            if prev_enlaces and prev_enlaces[0]:
                enlaces_prev = prev_enlaces[0]
                enlaces_json = json.dumps(enlaces_prev) if isinstance(enlaces_prev, list) else enlaces_prev
                logger.info(f"   ♻️ Preservando enlaces anteriores (usuario no envió nuevos)")
        else:
            logger.info(f"   🔄 REEMPLAZANDO enlaces anteriores con nuevos")
        
        query = text("""
            UPDATE entregas_tareas
            SET contenido_texto = :contenido,
                archivo_url = :archivo_url,
                archivos_adicionales = :archivos_adicionales,
                enlaces_externos = :enlaces_externos,
                fecha_entrega = :fecha_entrega,
                estado = 'entregada'
            WHERE entrega_id = :entrega_id
        """)

    
        db.execute(query, {
            "entrega_id": entrega_id,
            "contenido": contenido,
            "archivo_url": archivo_url,
            "archivos_adicionales": archivos_json,
            "enlaces_externos": enlaces_json,
            "fecha_entrega": datetime.now(timezone.utc)
        })

        db.commit()

        # Parse response data
        archivos_response = []
        if archivos_json:
            try:
                archivos_data = json.loads(archivos_json) if isinstance(archivos_json, str) else archivos_json
                archivos_response = archivos_data.get('archivos', []) if isinstance(archivos_data, dict) else []
            except:
                archivos_response = []
        
        enlaces_response = []
        if enlaces_json:
            try:
                enlaces_response = json.loads(enlaces_json) if isinstance(enlaces_json, str) else enlaces_json
            except:
                enlaces_response = []

        return {
            "success": True,
            "message": "Entrega actualizada exitosamente",
            "data": {
                "entrega_id": str(entrega_id),
                "actualizado": True,
                "archivos": archivos_response,
                "enlaces": enlaces_response
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
                        entrega_id, tarea_id, estudiante_id, contenido_texto,
                        archivo_metadata, fecha_entrega, es_tardia,
                        intentos, estado
                    )
                    VALUES (
                        gen_random_uuid()::text, :tarea_id, :estudiante_id, :contenido_texto,
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
