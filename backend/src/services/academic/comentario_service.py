"""Service para gestión de comentarios en cursos.

Aplica principios SOLID:
- Single Responsibility: Solo gestiona comentarios
- Open/Closed: Extensible sin modificar código existente
- Liskov Substitution: Interfaces consistentes
- Interface Segregation: Métodos específicos y cohesivos
- Dependency Inversion: Depende de abstracciones (Session, models)

Clean Code:
- Nombres descriptivos
- Funciones pequeñas (< 50 líneas)
- Un solo nivel de abstracción por función
- Manejo de errores explícito
"""

from datetime import UTC, datetime
import logging
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.models.communication.comentario import Comentario, TipoComentario
from src.models.users.usuario import Usuario


logger = logging.getLogger(__name__)


class ComentarioService:
    """Service para gestión de comentarios.

    Responsabilidades:
    - CRUD de comentarios
    - Paginación de resultados
    """

    # Constantes (Clean Code: Magic numbers -> Named constants)
    MAX_COMENTARIO_LENGTH = 5000
    MAX_RESPUESTAS_PER_PAGE = 50
    DEFAULT_PAGE_SIZE = 20

    @staticmethod
    def crear_comentario(
        db: Session,
        curso_id: str,
        contenido: str,
        usuario: Usuario,
        tipo: TipoComentario = TipoComentario.comentario,
        comentario_padre_id: str | None = None,
        archivos_adjuntos: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Crea un nuevo comentario en un curso.

        Args:
            db: Sesión de base de datos
            curso_id: ID del curso
        contenido: Contenido del comentario
        """
        try:
            logger.info(f"🔄 Creando comentario - curso_id: {curso_id}, usuario: {usuario.usuario_id}, tipo: {tipo}, contenido_length: {len(contenido)}")
            logger.info(f"📎 Archivos adjuntos recibidos: {archivos_adjuntos}")
            logger.info(f"📎 Tipo de archivos_adjuntos: {type(archivos_adjuntos)}")

            # Validación de entrada (Clean Code: Fail fast)
            ComentarioService._validar_contenido(contenido)
            ComentarioService._validar_acceso_curso(db, curso_id, usuario)

            # Si es respuesta, validar comentario padre
            if comentario_padre_id:
                ComentarioService._validar_comentario_padre(
                    db, comentario_padre_id, curso_id
                )

            # Crear comentario (Single Responsibility)
            # comentario_padre_id puede venir como UUID (de Pydantic) o como string
            if comentario_padre_id:
                if isinstance(comentario_padre_id, UUID):
                    comentario_padre_uuid = comentario_padre_id
                else:
                    comentario_padre_uuid = UUID(str(comentario_padre_id))
            else:
                comentario_padre_uuid = None
            
            # DEBUG: Loggear si es respuesta
            if comentario_padre_uuid:
                logger.info(f"💬 Creando RESPUESTA a comentario padre {comentario_padre_uuid}")
            else:
                logger.info(f"💬 Creando comentario RAÍZ (sin padre)")
            
            comentario = Comentario(
                contenido=contenido,
                autor_id=usuario.usuario_id,
                tipo=tipo,
                curso_id=UUID(curso_id),
                comentario_padre_id=comentario_padre_uuid,
                fecha_creacion=datetime.now(UTC),
            )

            # Asignar archivos adjuntos si existen (validar que existan en archivos_curso)
            if archivos_adjuntos:
                logger.info(f"📎 Recibidos {len(archivos_adjuntos)} archivos adjuntos. Validando existencia en archivos_curso...")

                archivos_validos: list[dict] = []
                for a in archivos_adjuntos:
                    # Preferir archivo_id, si no usar id
                    archivo_id = None
                    try:
                        archivo_id = a.get('archivo_id') or a.get('id')
                    except Exception:
                        archivo_id = None

                    if archivo_id:
                        try:
                            q = text("SELECT archivo_id FROM archivos_curso WHERE archivo_id = :archivo_id")
                            res = db.execute(q, {"archivo_id": archivo_id}).fetchone()
                            if res:
                                archivos_validos.append({"archivo_id": str(res[0])})
                            else:
                                logger.warning(f"⚠️ Archivo no encontrado en archivos_curso, descartando referencia: {archivo_id}")
                        except Exception as e:
                            logger.exception(f"Error validando archivo {archivo_id}: {e}")
                    else:
                        logger.warning(f"⚠️ Referencia de archivo inválida o sin ID: {a}")

                # Guardar archivos válidos. Si ninguno se encontró, mantener
                # la referencia enviada por el frontend para evitar perder
                # archivos que quizás fueron subidos recientemente y aún
                # no están visibles por la transacción.
                if archivos_validos:
                    comentario.archivos_lista = archivos_validos
                    logger.info(f"📎 Archivos válidos asignados: {len(archivos_validos)}")
                else:
                    # Fallback: almacenar las referencias originales (normalizadas)
                    logger.warning("📎 Ningún archivo validado; persistiendo referencias originales para evitar pérdida")
                    normalized_originals = []
                    for a in archivos_adjuntos:
                        try:
                            archivo_id = a.get('archivo_id') or a.get('id')
                        except Exception:
                            archivo_id = None
                        if archivo_id:
                            normalized_originals.append({"archivo_id": str(archivo_id)})
                    comentario.archivos_lista = normalized_originals
                    logger.info(f"📎 Archivos normalizados (fallback) asignados: {len(normalized_originals)}")

                if len(archivos_validos) != len(archivos_adjuntos):
                    logger.info(f"📎 {len(archivos_adjuntos)-len(archivos_validos)} referencias procesadas/validadas")
            else:
                logger.info("📎 No hay archivos adjuntos")

            db.add(comentario)
            db.commit()
            db.refresh(comentario)

            logger.info(
                f"✅ Comentario creado: {comentario.comentario_id} por usuario {usuario.usuario_id}"
            )
            
            # DEBUG: Verificar que comentario_padre_id se guardó correctamente
            if comentario.comentario_padre_id:
                logger.info(f"✅ comentario_padre_id guardado en DB: {comentario.comentario_padre_id}")
            else:
                logger.info("✅ Comentario raíz guardado (sin padre)")
            # DEBUG: mostrar qué se guardó exactamente en archivos_adjuntos
            try:
                logger.info(f"📦 Guardado en DB - archivos_adjuntos(raw): {comentario.archivos_adjuntos}")
                logger.info(f"📦 Guardado en DB - archivos_lista(parsed): {comentario.archivos_lista}")
                logger.info(f"📦 Guardado en DB - comentario_id: {comentario.comentario_id}")
            except Exception:
                logger.debug("📦 Debug archivos: no fue posible imprimir metadata de archivos guardados")

            # Devolver el comentario creado en formato consistente (enriquecido)
            return {
                "success": True,
                "message": "Comentario creado exitosamente",
                "data": ComentarioService._comentario_to_dict_enriquecido(db, comentario),
                }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error creando comentario: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear comentario: {e!s}",
            ) from e
        
        
    @staticmethod
    def _enriquecer_archivos_adjuntos(db: Session, archivos_basicos: list[dict]) -> list[dict]:
        """Enriquece una lista de archivos adjuntos con metadatos completos desde la tabla archivos_curso."""
        archivos_enriquecidos = []
        if not archivos_basicos:
            return []
        for archivo_basico in archivos_basicos:
            # Aceptar tanto objetos como strings (legacy)
            archivo_id = None
            if isinstance(archivo_basico, str):
                archivo_id = archivo_basico
            elif isinstance(archivo_basico, dict):
                archivo_id = (
                    archivo_basico.get('archivo_id')
                    or archivo_basico.get('id')
                    or archivo_basico.get('file_id')
                    or archivo_basico.get('archivoId')
                )
            else:
                # Si el formato es inesperado, intentar convertir a str
                try:
                    archivo_id = str(archivo_basico)
                except Exception:
                    archivo_id = None
            if archivo_id:
                archivo_query = text(
                    """
                    SELECT 
                        archivo_id,
                        nombre_original,
                        url,
                        tipo,
                        tamaño,
                        fecha_subida
                    FROM archivos_curso 
                    WHERE archivo_id = :archivo_id
                    """
                )
                archivo_result = db.execute(archivo_query, {"archivo_id": archivo_id}).fetchone()
                if archivo_result:
                    archivo_completo = dict(archivo_result._mapping)
                    archivo_enriquecido = {
                        'id': str(archivo_completo['archivo_id']),
                        'archivo_id': str(archivo_completo['archivo_id']),
                        'nombre': archivo_completo['nombre_original'],
                        'url': archivo_completo['url'],
                        'tamaño': archivo_completo['tamaño'],
                        'tipo': archivo_completo['tipo'],
                        'fecha_subida': archivo_completo['fecha_subida'].isoformat() if archivo_completo['fecha_subida'] else None
                    }
                    archivos_enriquecidos.append(archivo_enriquecido)
                else:
                    # No se encontró metadata; devolver objeto mínimo con id
                    archivos_enriquecidos.append({
                        'id': str(archivo_id),
                        'archivo_id': str(archivo_id),
                    })
            else:
                # archivo_basico no tiene id, devolver tal cual (posible estructura desconocida)
                archivos_enriquecidos.append(archivo_basico)
        return archivos_enriquecidos

    @staticmethod
    def _comentario_to_dict_enriquecido(db: Session, comentario: Comentario) -> dict[str, Any]:
        """Serializa un comentario a dict, enriqueciendo archivos adjuntos con metadatos completos."""
        archivos_basicos = comentario.archivos_lista
        archivos_adjuntos = ComentarioService._enriquecer_archivos_adjuntos(db, archivos_basicos)
        return {
            "comentario_id": str(comentario.comentario_id),
            "contenido": comentario.contenido,
            "tipo": comentario.tipo.value if comentario.tipo else "general",
            "fecha_creacion": (
                comentario.fecha_creacion.isoformat()
                if comentario.fecha_creacion
                else None
            ),
            "fecha_actualizacion": (
                comentario.fecha_actualizacion.isoformat()
                if comentario.fecha_actualizacion
                else None
            ),
            "autor_id": str(comentario.autor_id),
            "curso_id": str(comentario.curso_id),
            "comentario_padre_id": (
                str(comentario.comentario_padre_id)
                if comentario.comentario_padre_id
                else None
            ),
            "archivos_adjuntos": archivos_adjuntos,
        }

        

    @staticmethod
    def obtener_comentarios_curso(
        db: Session,
        curso_id: str,
        usuario: Usuario,
        limit: int = DEFAULT_PAGE_SIZE,
        offset: int = 0,
        tipo: TipoComentario | None = None,
    ) -> dict[str, Any]:
        """Obtiene comentarios de un curso con paginación.

        Args:
            db: Sesión de base de datos
            curso_id: ID del curso
            usuario: Usuario que consulta
            limit: Límite de resultados
            offset: Offset para paginación
            tipo: Filtro opcional por tipo de comentario

        Returns:
            Dict con comentarios y metadata de paginación
        """
        try:
            # Validar acceso
            ComentarioService._validar_acceso_curso(db, curso_id, usuario)

            # Query optimizada con JOINs (Clean Code: Avoid N+1)
            query = text(
                """
                SELECT
                    c.comentario_id,
                    c.contenido,
                    c.tipo,
                    c.fecha_creacion,
                    c.fecha_actualizacion,
                    c.comentario_padre_id,
                    c.archivos_adjuntos,
                    u.usuario_id as autor_id,
                    u.nombres || ' ' || u.apellidos as autor_nombre,
                    u.perfil_url as autor_avatar,
                    COUNT(DISTINCT r.comentario_id) as total_respuestas,
                    COUNT(DISTINCT reac.reaccion_id) as total_reacciones
                FROM "Comentario" c
                JOIN "Usuario" u ON c.autor_id = u.usuario_id
                LEFT JOIN "Comentario" r ON r.comentario_padre_id = c.comentario_id
                LEFT JOIN "Reacciones" reac ON reac.comentario_id = c.comentario_id
                WHERE c.curso_id = :curso_id
                    AND c.comentario_padre_id IS NULL
                    AND (:tipo IS NULL OR c.tipo = :tipo)
                GROUP BY c.comentario_id, u.usuario_id
                ORDER BY c.fecha_creacion DESC
                LIMIT :limit OFFSET :offset
            """
            )

            result = db.execute(
                query,
                {
                    "curso_id": curso_id,
                    "tipo": tipo.value if tipo else None,
                    "limit": limit,
                    "offset": offset,
                },
            ).fetchall()

            # Contar total (para paginación)
            count_query = text(
                """
                SELECT COUNT(*)
                FROM "Comentario"
                WHERE curso_id = :curso_id
                    AND comentario_padre_id IS NULL
                    AND (:tipo IS NULL OR tipo = :tipo)
            """
            )

            total = db.execute(
                count_query,
                {"curso_id": curso_id, "tipo": tipo.value if tipo else None},
            ).scalar()

            comentarios = []
            import json
            # Collect raw rows and build the main comment dicts first
            raw_rows = [row for row in result]

            # Batch-load respuestas para evitar N+1: si hay comentarios, obtener respuestas en una sola query
            comentario_ids = [str(row._mapping['comentario_id']) for row in raw_rows if row._mapping.get('comentario_id')]
            logger.info(f"🔍 Batch-loading respuestas para {len(comentario_ids)} comentarios padre: {comentario_ids}")
            respuestas_by_parent: dict[str, list] = {}
            if comentario_ids:
                # Obtención masiva de respuestas (una sola query)
                # Crear placeholders dinámicos para CAST a UUID
                placeholders = [f"CAST(:parent_id_{i} AS UUID)" for i in range(len(comentario_ids))]
                placeholders_str = ", ".join(placeholders)
                
                respuestas_query = text(
                    f"""
                    SELECT
                        c.comentario_id,
                        c.contenido,
                        c.fecha_creacion,
                        c.fecha_actualizacion,
                        c.archivos_adjuntos,
                        c.comentario_padre_id,
                        u.usuario_id as autor_id,
                        u.nombres || ' ' || u.apellidos as autor_nombre,
                        u.perfil_url as autor_avatar
                    FROM "Comentario" c
                    JOIN "Usuario" u ON c.autor_id = u.usuario_id
                    WHERE c.comentario_padre_id IN ({placeholders_str})
                    ORDER BY c.fecha_creacion ASC
                """
                )

                # Crear parámetros con nombres dinámicos
                params = {f"parent_id_{i}": comentario_ids[i] for i in range(len(comentario_ids))}

                try:
                    res_rows = db.execute(respuestas_query, params).fetchall()
                    logger.info(f"✅ Carguadas {len(res_rows)} respuestas en batch")

                    # Procesar respuestas y agrupar por padre
                    for r in res_rows:
                        rdict = dict(r._mapping)
                        parent = str(rdict.get('comentario_padre_id'))
                        logger.info(f"📝 Procesando respuesta {rdict.get('comentario_id')} con padre {parent}")

                        # Enriquecer archivos_adjuntos para cada respuesta
                        archivos_basicos = []
                        if rdict.get('archivos_adjuntos'):
                            # archivos_adjuntos puede venir como string JSON o como objeto ya parseado
                            archivos_raw = rdict['archivos_adjuntos']
                            if isinstance(archivos_raw, str):
                                try:
                                    import json
                                    archivos_basicos = json.loads(archivos_raw)
                                except (json.JSONDecodeError, TypeError):
                                    archivos_basicos = []
                            elif isinstance(archivos_raw, list):
                                archivos_basicos = archivos_raw
                            else:
                                archivos_basicos = []
                        archivos_enriquecidos = ComentarioService._enriquecer_archivos_adjuntos(db, archivos_basicos)
                        rdict['archivos_adjuntos'] = archivos_enriquecidos

                        # Mapear campos para frontend
                        rdict['id'] = rdict['comentario_id']
                        rdict['autor'] = {
                            'nombre': rdict['autor_nombre'].split(' ')[0] if rdict['autor_nombre'] else 'Usuario',
                            'apellido': ' '.join(rdict['autor_nombre'].split(' ')[1:]) if rdict['autor_nombre'] and len(rdict['autor_nombre'].split(' ')) > 1 else '',
                            'email': rdict.get('autor_email', ''),
                            'avatar': rdict.get('autor_avatar', '')
                        }
                        rdict['fecha'] = rdict['fecha_creacion']
                        rdict['tipo'] = 'respuesta'
                        rdict['editado'] = rdict.get('fecha_actualizacion') is not None

                        respuestas_by_parent.setdefault(parent, []).append(rdict)

                    logger.info(f"✅ Respuestas agrupadas por padre: {list(respuestas_by_parent.keys())}")

                except Exception as e:
                    logger.exception(f"❌ Error en batch-load de respuestas: {e}")

            for row in raw_rows:
                comentario_dict = dict(row._mapping)
                logger.info(f"🔍 Procesando comentario {comentario_dict.get('comentario_id')} - padre: {comentario_dict.get('comentario_padre_id')}")
                # Procesar archivos_adjuntos enriquecidos
                archivos_basicos = []
                if comentario_dict.get('archivos_adjuntos'):
                    # archivos_adjuntos puede venir como string JSON (de raw SQL) o como objeto ya parseado (de SQLAlchemy)
                    archivos_raw = comentario_dict['archivos_adjuntos']
                    if isinstance(archivos_raw, str):
                        try:
                            archivos_basicos = json.loads(archivos_raw)
                            logger.info(f"📄 Archivos básicos parseados desde string: {archivos_basicos}")
                        except (json.JSONDecodeError, TypeError):
                            archivos_basicos = []
                            logger.warning(f"❌ Error parseando archivos_adjuntos como string para comentario {comentario_dict.get('comentario_id')}")
                    elif isinstance(archivos_raw, list):
                        archivos_basicos = archivos_raw
                        logger.info(f"📄 Archivos básicos ya parseados como lista: {archivos_basicos}")
                    else:
                        archivos_basicos = []
                        logger.warning(f"❌ Tipo inesperado de archivos_adjuntos para comentario {comentario_dict.get('comentario_id')}: {type(archivos_raw)}")
                archivos_enriquecidos = ComentarioService._enriquecer_archivos_adjuntos(db, archivos_basicos)
                # DEBUG: loggear archivos para inspección en caso de que no aparezcan en frontend
                try:
                    logger.info(f"🔍 Comentario {comentario_dict.get('comentario_id')} - archivos_enriquecidos: {archivos_enriquecidos}")
                except Exception:
                    logger.debug("🔍 No fue posible imprimir archivos_enriquecidos del comentario")
                comentario_dict['archivos_adjuntos'] = archivos_enriquecidos
                # Mapear campos para que coincidan con lo que espera el frontend
                comentario_dict['id'] = comentario_dict['comentario_id']
                comentario_dict['autor'] = {
                    'nombre': comentario_dict['autor_nombre'].split(' ')[0] if comentario_dict['autor_nombre'] else 'Usuario',
                    'apellido': ' '.join(comentario_dict['autor_nombre'].split(' ')[1:]) if comentario_dict['autor_nombre'] and len(comentario_dict['autor_nombre'].split(' ')) > 1 else '',
                    'email': comentario_dict.get('autor_email', ''),
                    'avatar': comentario_dict.get('autor_avatar', '')
                }
                comentario_dict['fecha'] = comentario_dict['fecha_creacion']
                comentario_dict['tipo'] = comentario_dict.get('tipo', 'comentario')
                comentario_dict['editado'] = comentario_dict.get('fecha_actualizacion') is not None

                # Usar respuestas del batch-load
                comentario_id = str(comentario_dict['comentario_id'])
                comentario_dict['respuestas'] = respuestas_by_parent.get(comentario_id, [])
                logger.info(f"📋 Comentario {comentario_id} final - respuestas: {len(comentario_dict['respuestas'])}")
                comentarios.append(comentario_dict)
            
            logger.info(f"📊 TOTAL: {len(comentarios)} comentarios procesados")
            return {
                "success": True,
                "data": comentarios,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo comentarios: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener comentarios: {e!s}",
            ) from e

    @staticmethod
    def actualizar_comentario(
        db: Session, comentario_id: str, nuevo_contenido: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Actualiza el contenido de un comentario.

        Args:
            db: Sesión de base de datos
            comentario_id: ID del comentario
            nuevo_contenido: Nuevo contenido
            usuario: Usuario que actualiza

        Returns:
            Dict con el comentario actualizado
        """
        try:
            # Validaciones
            ComentarioService._validar_contenido(nuevo_contenido)
            comentario = ComentarioService._obtener_comentario(db, comentario_id)
            ComentarioService._validar_permisos_edicion(comentario, usuario)

            # Actualizar
            comentario.contenido = nuevo_contenido
            comentario.fecha_actualizacion = datetime.now(UTC)

            db.commit()
            db.refresh(comentario)

            logger.info(f"Comentario actualizado: {comentario_id}")

            return {
                "success": True,
                "message": "Comentario actualizado exitosamente",
                "data": ComentarioService._comentario_to_dict(db, comentario),
            }

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error actualizando comentario: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar comentario: {e!s}",
            ) from e

    @staticmethod
    def eliminar_comentario(
        db: Session, comentario_id: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Elimina un comentario (soft delete).

        Args:
            db: Sesión de base de datos
            comentario_id: ID del comentario
            usuario: Usuario que elimina

        Returns:
            Dict con confirmación
        """
        try:
            comentario = ComentarioService._obtener_comentario(db, comentario_id)
            ComentarioService._validar_permisos_edicion(comentario, usuario)

            # Soft delete: marcar como eliminado en lugar de borrar
            comentario.contenido = "[Comentario eliminado]"
            comentario.fecha_actualizacion = datetime.now(UTC)

            db.commit()

            logger.info(f"Comentario eliminado: {comentario_id}")

            return {"success": True, "message": "Comentario eliminado exitosamente"}

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error eliminando comentario: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar comentario: {e!s}",
            ) from e

    @staticmethod
    def obtener_respuestas(
        db: Session,
        comentario_id: str,
        usuario: Usuario,
        limit: int = MAX_RESPUESTAS_PER_PAGE,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Obtiene respuestas de un comentario.

        Args:
            db: Sesión de base de datos
            comentario_id: ID del comentario padre
            usuario: Usuario que consulta
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Dict con respuestas y paginación
        """
        try:
            # DEBUG: Loggear parámetros de entrada
            logger.info(f"obtener_respuestas llamado con comentario_id={comentario_id} (tipo={type(comentario_id)})")
            
            # Validar que el comentario existe
            comentario_padre = ComentarioService._obtener_comentario(db, comentario_id)
            logger.info(f"Comentario padre encontrado: {comentario_padre.comentario_id}, curso={comentario_padre.curso_id}")
            
            ComentarioService._validar_acceso_curso(
                db, str(comentario_padre.curso_id), usuario
            )

            # Obtener respuestas - CAST explícito a UUID para evitar problemas de tipo
            query = text(
                """
                SELECT
                    c.comentario_id,
                    c.contenido,
                    c.fecha_creacion,
                    c.fecha_actualizacion,
                    c.archivos_adjuntos,
                    u.usuario_id as autor_id,
                    u.nombres || ' ' || u.apellidos as autor_nombre,
                    u.perfil_url as autor_avatar,
                    COUNT(DISTINCT reac.reaccion_id) as total_reacciones
                FROM "Comentario" c
                JOIN "Usuario" u ON c.autor_id = u.usuario_id
                LEFT JOIN "Reacciones" reac ON reac.comentario_id = c.comentario_id
                WHERE c.comentario_padre_id = CAST(:comentario_padre_id AS UUID)
                GROUP BY c.comentario_id, u.usuario_id
                ORDER BY c.fecha_creacion ASC
                LIMIT :limit OFFSET :offset
            """
            )

            result = db.execute(
                query,
                {
                    "comentario_padre_id": str(comentario_id),  # Forzar a string
                    "limit": limit,
                    "offset": offset,
                },
            ).fetchall()
            
            # DEBUG: Loggear cantidad de respuestas encontradas
            logger.info(f"Respuestas encontradas para comentario {comentario_id}: {len(result)}")

            # Contar total
            count_query = text(
                """
                SELECT COUNT(*)
                FROM "Comentario"
                WHERE comentario_padre_id = CAST(:comentario_padre_id AS UUID)
            """
            )

            total = db.execute(
                count_query, {"comentario_padre_id": str(comentario_id)}
            ).scalar()
            
            logger.info(f"Total de respuestas (incluyendo paginadas): {total}")

            respuestas = [dict(row._mapping) for row in result]

            # Procesar archivos_adjuntos para cada respuesta
            for respuesta in respuestas:
                if respuesta.get('archivos_adjuntos'):
                    # archivos_adjuntos puede venir como string JSON o como objeto ya parseado
                    archivos_raw = respuesta['archivos_adjuntos']
                    if isinstance(archivos_raw, str):
                        try:
                            import json
                            archivos_basicos = json.loads(archivos_raw)
                            respuesta['archivos_adjuntos'] = ComentarioService._enriquecer_archivos_adjuntos(db, archivos_basicos)
                        except (json.JSONDecodeError, TypeError) as e:
                            logger.warning(f"Error procesando archivos_adjuntos para respuesta {respuesta.get('comentario_id')}: {e}")
                            respuesta['archivos_adjuntos'] = []
                    elif isinstance(archivos_raw, list):
                        respuesta['archivos_adjuntos'] = ComentarioService._enriquecer_archivos_adjuntos(db, archivos_raw)
                    else:
                        respuesta['archivos_adjuntos'] = []
                else:
                    respuesta['archivos_adjuntos'] = []

                # Mapear campos para que coincidan con lo que espera el frontend
                respuesta['id'] = respuesta['comentario_id']
                respuesta['autor'] = {
                    'nombre': respuesta['autor_nombre'].split(' ')[0] if respuesta['autor_nombre'] else 'Usuario',
                    'apellido': ' '.join(respuesta['autor_nombre'].split(' ')[1:]) if respuesta['autor_nombre'] and len(respuesta['autor_nombre'].split(' ')) > 1 else '',
                    'email': respuesta.get('autor_email', ''),
                    'avatar': respuesta.get('autor_avatar', '')
                }
                respuesta['fecha'] = respuesta['fecha_creacion']
                respuesta['tipo'] = 'respuesta'
                respuesta['editado'] = respuesta.get('fecha_actualizacion') is not None

            return {
                "success": True,
                "data": respuestas,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo respuestas: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener respuestas: {e!s}",
            ) from e

    @staticmethod
    def obtener_comentario_por_id(
        db: Session,
        comentario_id: str,
        usuario: Usuario,
    ) -> dict[str, Any] | None:
        """Obtiene un comentario específico por ID.

        Args:
            db: Sesión de base de datos
            comentario_id: ID del comentario
            usuario: Usuario que consulta

        Returns:
            Dict con el comentario o None si no existe
        """
        try:
            # Obtener comentario
            comentario = ComentarioService._obtener_comentario(db, comentario_id)
            
            # Validar acceso al curso
            ComentarioService._validar_acceso_curso(
                db, str(comentario.curso_id), usuario
            )

            # Convertir a diccionario
            return {
                "comentario_id": str(comentario.comentario_id),
                "curso_id": str(comentario.curso_id),
                "contenido": comentario.contenido,
                "tipo": comentario.tipo.value if comentario.tipo else "comentario",
                "autor_id": str(comentario.autor_id),
                "comentario_padre_id": str(comentario.comentario_padre_id) if comentario.comentario_padre_id else None,
                "fecha_creacion": comentario.fecha_creacion.isoformat() if comentario.fecha_creacion else None,
                "archivos_adjuntos": comentario.archivos_lista if comentario.archivos_adjuntos else [],
            }

        except HTTPException:
            # Si no tiene acceso o no existe, devolver None
            return None
        except Exception as e:
            logger.exception("Error obteniendo comentario %s", comentario_id)
            return None

    # ========== MÉTODOS PRIVADOS (Helper functions) ==========

    @staticmethod
    def _validar_contenido(contenido: str) -> None:
        """Valida el contenido del comentario."""
        if not contenido or not contenido.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El contenido del comentario no puede estar vacío",
            )

        if len(contenido) > ComentarioService.MAX_COMENTARIO_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El comentario no puede exceder {ComentarioService.MAX_COMENTARIO_LENGTH} caracteres",
            )

    @staticmethod
    def _validar_acceso_curso(db: Session, curso_id: str, usuario: Usuario) -> None:
        """Valida que el usuario tenga acceso al curso."""
        logger.info("🔍 Validando acceso - curso_id: %s, usuario: %s (%s)", curso_id, usuario.usuario_id, usuario.rol)
        
        # Usar método público de curso_service
        from src.services.academic.curso_service import CursoService

        tiene_acceso = CursoService.validar_acceso_curso(db, curso_id, usuario)
        logger.info("🔍 Resultado validación acceso: %s", tiene_acceso)
        
        if not tiene_acceso:
            logger.warning("🚫 Acceso denegado - usuario %s no tiene acceso al curso %s", usuario.usuario_id, curso_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este curso",
            )

    @staticmethod
    def _validar_comentario_padre(
        db: Session, comentario_padre_id: str, curso_id: str
    ) -> None:
        """Valida que el comentario padre existe y pertenece al curso."""
        query = text(
            """
            SELECT comentario_id
            FROM "Comentario"
            WHERE comentario_id = :comentario_id
                AND curso_id = :curso_id
        """
        )

        result = db.execute(
            query, {"comentario_id": comentario_padre_id, "curso_id": curso_id}
        ).fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comentario padre no encontrado",
            )

    @staticmethod
    def _obtener_comentario(db: Session, comentario_id: str) -> Comentario:
        """Obtiene un comentario por ID."""
        # Convertir a string si es UUID
        if isinstance(comentario_id, UUID):
            comentario_id = str(comentario_id)

        comentario = (
            db.query(Comentario)
            .filter(Comentario.comentario_id == UUID(comentario_id))
            .first()
        )

        if not comentario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado"
            )

        return comentario

    @staticmethod
    def _validar_permisos_edicion(comentario: Comentario, usuario: Usuario) -> None:
        """Valida que el usuario puede editar/eliminar el comentario."""
        es_autor = str(comentario.autor_id) == str(usuario.usuario_id)
        es_coordinador = usuario.rol == "coordinador"
        es_docente = usuario.rol == "docente"

        if not (es_autor or es_coordinador or es_docente):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para modificar este comentario",
            )

    @staticmethod
    def _comentario_to_dict(db: Session, comentario: Comentario) -> dict[str, Any]:
        """Convierte un comentario a diccionario."""
        archivos_adjuntos = comentario.archivos_lista if comentario.archivos_adjuntos else []
        
        # Enriquecer archivos_adjuntos con información completa de archivos_curso
        if archivos_adjuntos:
            archivos_adjuntos = ComentarioService._enriquecer_archivos_adjuntos(db, archivos_adjuntos)
        
        return {
            "comentario_id": str(comentario.comentario_id),
            "contenido": comentario.contenido,
            "tipo": comentario.tipo.value if comentario.tipo else "general",
            "fecha_creacion": (
                comentario.fecha_creacion.isoformat()
                if comentario.fecha_creacion
                else None
            ),
            "fecha_actualizacion": (
                comentario.fecha_actualizacion.isoformat()
                if comentario.fecha_actualizacion
                else None
            ),
            "autor_id": str(comentario.autor_id),
            "curso_id": str(comentario.curso_id),
            "comentario_padre_id": (
                str(comentario.comentario_padre_id)
                if comentario.comentario_padre_id
                else None
            ),
            "archivos_adjuntos": archivos_adjuntos,
        }


# Instancia global del servicio
comentario_service = ComentarioService()
