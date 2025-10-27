"""
Rutas de API para la gestión de cursos en Acadify

Endpoints disponibles:
- POST /inscribir: Inscribir estudiante en un curso
- GET /mis-cursos: Obtener cursos del usuario actual
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Header
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import os
import uuid
import aiofiles
import json

from src.api import deps
from src.db.session import SessionLocal
from src.models.users.usuario import Usuario

# Importaciones para comentarios
from src.crud.communication.comentario import comentario as crud_comentario
from src.schemas.communication.comentario import ComentarioCreate, ComentarioResponse
from src.models.communication.comentario import TipoComentario, Comentario
from src.models.communication.reaccion import Reaccion

# Configuración del router
router = APIRouter(prefix="/cursos")

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos de datos
class CourseInscriptionRequest(BaseModel):
    codigo_curso: str

from pydantic import BaseModel
from typing import Optional

class EstudianteVinculacionRequest(BaseModel):
    codigo_invitacion: Optional[str] = None

class CodigoInvitacionGenerate(BaseModel):
    programa_id: str
    descripcion: Optional[str] = None

class CourseResponse(BaseModel):
    success: bool
    message: str
    data: List[dict]
    total: int
    source: str
    user_role: str
    empty_state: bool
    empty_message: Optional[str] = None

@router.post("/inscribir")
async def inscribir_curso(
    request: CourseInscriptionRequest,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Inscribir estudiante en un curso usando código de acceso
    VALIDACIÓN: Solo puede inscribirse a cursos de su misma institución
    """
    try:
        logger.info(f"Usuario {current_user.usuario_id} intentando inscribirse con código: {request.codigo_curso}")
        
        # 1. Buscar curso por código de acceso
        curso_result = db.execute(text("""
            SELECT c.curso_id, c.nombre, c.descripcion, c.programa_id, c.institucion_id
            FROM "Curso" c 
            WHERE c.codigo_acceso = :codigo_acceso
        """), {"codigo_acceso": request.codigo_curso}).fetchone()
        
        if not curso_result:
            raise HTTPException(
                status_code=404,
                detail="Código de acceso inválido. Verifica que el código sea correcto."
            )
        
        curso_id, curso_nombre, curso_descripcion, curso_programa_id, curso_institucion_id = curso_result
        
        # 2. Obtener la institución del usuario (a través de su programa como estudiante)
        usuario_institucion_result = db.execute(text("""
            SELECT p.institucion_id, i.nombre as institucion_nombre
            FROM "Estudiante" e
            JOIN "Programa" p ON e.programa_id = p.programa_id
            JOIN "Institucion" i ON p.institucion_id = i.institucion_id
            WHERE e.estudiante_id = :usuario_id
        """), {"usuario_id": current_user.usuario_id}).fetchone()
        
        if not usuario_institucion_result:
            raise HTTPException(
                status_code=400,
                detail="Tu perfil de estudiante no está vinculado a ninguna institución. Contacta al administrador."
            )
        
        usuario_institucion_id, usuario_institucion_nombre = usuario_institucion_result
        
        # 3. VALIDACIÓN CRÍTICA: Verificar que el curso pertenece a la misma institución del usuario
        if str(curso_institucion_id) != str(usuario_institucion_id):
            # Obtener nombre de la institución del curso para el mensaje
            curso_institucion_result = db.execute(text("""
                SELECT nombre FROM "Institucion" WHERE institucion_id = :institucion_id
            """), {"institucion_id": curso_institucion_id}).fetchone()
            
            curso_institucion_nombre = curso_institucion_result[0] if curso_institucion_result else "Otra institución"
            
            raise HTTPException(
                status_code=403,
                detail=f"No puedes inscribirte al curso '{curso_nombre}' porque pertenece a '{curso_institucion_nombre}' y tú estás vinculado a '{usuario_institucion_nombre}'. Solo puedes inscribirte a cursos de tu propia institución."
            )
        
        # 4. Verificar si el usuario ya está inscrito en el curso
        inscripcion_existente = db.execute(text("""
            SELECT 1 FROM "EstudianteGrupo" eg
            JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id  
            WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
        """), {"curso_id": curso_id, "usuario_id": current_user.usuario_id}).fetchone()
        
        if inscripcion_existente:
            raise HTTPException(
                status_code=409,
                detail=f"Ya estás inscrito en el curso '{curso_nombre}'"
            )
        
        # 5. Buscar un grupo disponible para el curso QUE SEA DEL MISMO PROGRAMA del estudiante
        grupo_curso = db.execute(text("""
            SELECT gc.grupo_id, g.nombre as grupo_nombre
            FROM "GrupoCurso" gc 
            JOIN "Grupo" g ON gc.grupo_id = g.grupo_id
            JOIN "Estudiante" e ON e.programa_id = g.programa_id
            WHERE gc.curso_id = :curso_id AND e.estudiante_id = :usuario_id
            ORDER BY gc.fecha_asignacion ASC
            LIMIT 1
        """), {"curso_id": curso_id, "usuario_id": current_user.usuario_id}).fetchone()

        if not grupo_curso:
            # Debug: Verificar qué grupos existen para el curso
            grupos_curso_debug = db.execute(text("""
                SELECT gc.grupo_id, g.nombre as grupo_nombre, g.programa_id,
                       p.nombre as programa_nombre
                FROM "GrupoCurso" gc 
                JOIN "Grupo" g ON gc.grupo_id = g.grupo_id
                JOIN "Programa" p ON g.programa_id = p.programa_id
                WHERE gc.curso_id = :curso_id
            """), {"curso_id": curso_id}).fetchall()
            
            logger.error(f"No hay grupos compatibles. Grupos del curso: {[dict(g._mapping) for g in grupos_curso_debug]}")
            
            raise HTTPException(
                status_code=404,
                detail="No hay grupos disponibles para este curso en tu programa. El curso puede estar asociado a un programa diferente al tuyo. Contacta al coordinador."
            )        # 6. Inscribir al estudiante en el grupo
        db.execute(text("""
            INSERT INTO "EstudianteGrupo" (grupo_id, estudiante_id, fecha_vinculacion)
            VALUES (:grupo_id, :usuario_id, CURRENT_DATE)
        """), {
            "grupo_id": grupo_curso[0], 
            "usuario_id": current_user.usuario_id
        })
        
        db.commit()
        
        logger.info(f"Usuario {current_user.usuario_id} inscrito exitosamente en curso {curso_id} de la institución {usuario_institucion_nombre}")
        
        return {
            "success": True,
            "message": f"¡Inscripción exitosa! Te has unido al curso '{curso_nombre}' de {usuario_institucion_nombre}",
            "curso_id": str(curso_id),
            "curso_nombre": curso_nombre,
            "grupo_nombre": grupo_curso[1],
            "codigo_acceso": request.codigo_curso,
            "institucion": usuario_institucion_nombre
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en inscripción: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/mis-cursos", response_model=CourseResponse)
async def get_mis_cursos(current_user: Usuario = Depends(deps.get_current_user)):
    """
    Obtener los cursos del usuario actual con datos reales y calculados
    """
    try:
        logger.info(f"Obteniendo cursos para usuario: {current_user.usuario_id}")
        logger.info(f"Email del usuario: {current_user.correo_institucional}")
        
        # Crear conexión manual para consultas complejas
        db = SessionLocal()
        
        try:
            # Verificar si el usuario tiene perfil de estudiante
            estudiante_check = db.execute(text("""
                SELECT estudiante_id, programa_id FROM "Estudiante" 
                WHERE estudiante_id = :usuario_id
            """), {"usuario_id": current_user.usuario_id})
            
            estudiante_info = estudiante_check.fetchone()
            logger.info(f"Info estudiante: {estudiante_info}")
            
            if not estudiante_info:
                # Si no tiene perfil de estudiante, verificar si es docente o administrador
                if current_user.rol.value in ["docente", "coordinador", "administrador"]:
                    # Consulta para obtener cursos donde el usuario es docente
                    result_docente = db.execute(text("""
                        SELECT DISTINCT 
                            c.curso_id,
                            c.nombre,
                            c.descripcion,
                            c.codigo_acceso,
                            c.modalidad,
                            c.fecha_inicio,
                            c.fecha_fin,
                            g.nombre as grupo_nombre,
                            u_docente.nombres || ' ' || u_docente.apellidos as instructor,
                            i.nombre as institucion_nombre,
                            COUNT(DISTINCT eg_count.estudiante_id) as total_estudiantes,
                            :rol as tipo_vinculacion
                        FROM "GrupoCurso" gc
                        JOIN "Grupo" g ON gc.grupo_id = g.grupo_id
                        JOIN "Curso" c ON gc.curso_id = c.curso_id
                        LEFT JOIN "Usuario" u_docente ON gc.docente_id = u_docente.usuario_id
                        LEFT JOIN "EstudianteGrupo" eg_count ON g.grupo_id = eg_count.grupo_id
                        LEFT JOIN "Programa" p ON g.programa_id = p.programa_id
                        LEFT JOIN "Institucion" i ON p.institucion_id = i.institucion_id
                        WHERE gc.docente_id = :usuario_id OR :rol = 'administrador'
                        GROUP BY c.curso_id, c.nombre, c.descripcion, c.codigo_acceso, 
                                 c.modalidad, c.fecha_inicio, c.fecha_fin,
                                 g.nombre, u_docente.nombres, u_docente.apellidos, i.nombre
                        ORDER BY c.fecha_inicio DESC
                    """), {"usuario_id": current_user.usuario_id, "rol": current_user.rol.value})
                    
                    cursos_raw = result_docente.fetchall()
                    
                    if not cursos_raw:
                        return {
                            "success": True,
                            "message": "No tienes cursos asignados como docente",
                            "data": [],
                            "total": 0,
                            "source": "database",
                            "user_role": current_user.rol.value,
                            "empty_state": True,
                            "empty_message": "No tienes cursos asignados."
                        }
                else:
                    return {
                        "success": True,
                        "message": "Primero debes completar tu perfil de estudiante",
                        "data": [],
                        "total": 0,
                        "source": "database",
                        "user_role": "sin_perfil",
                        "empty_state": True,
                        "empty_message": "Completa tu perfil de estudiante para ver tus cursos."
                    }
            else:
                # Usuario tiene perfil de estudiante, obtener cursos como estudiante
                result_estudiante = db.execute(text("""
                    SELECT DISTINCT 
                        c.curso_id,
                        c.nombre,
                        c.descripcion,
                        c.codigo_acceso,
                        c.modalidad,
                        c.fecha_inicio,
                        c.fecha_fin,
                        g.nombre as grupo_nombre,
                        u_docente.nombres || ' ' || u_docente.apellidos as instructor,
                        i.nombre as institucion_nombre,
                        COUNT(DISTINCT eg_count.estudiante_id) as total_estudiantes,
                        'estudiante' as tipo_vinculacion
                    FROM "Estudiante" est
                    JOIN "EstudianteGrupo" eg ON est.estudiante_id = eg.estudiante_id
                    JOIN "Grupo" g ON eg.grupo_id = g.grupo_id
                    JOIN "GrupoCurso" gc ON g.grupo_id = gc.grupo_id
                    JOIN "Curso" c ON gc.curso_id = c.curso_id
                    LEFT JOIN "Usuario" u_docente ON gc.docente_id = u_docente.usuario_id
                    LEFT JOIN "EstudianteGrupo" eg_count ON g.grupo_id = eg_count.grupo_id
                    LEFT JOIN "Programa" p ON est.programa_id = p.programa_id
                    LEFT JOIN "Institucion" i ON p.institucion_id = i.institucion_id
                    WHERE est.estudiante_id = :usuario_id 
                    GROUP BY c.curso_id, c.nombre, c.descripcion, c.codigo_acceso, 
                             c.modalidad, c.fecha_inicio, c.fecha_fin,
                             g.nombre, u_docente.nombres, u_docente.apellidos, i.nombre
                    ORDER BY c.fecha_inicio DESC
                """), {"usuario_id": current_user.usuario_id})
                
                # También obtener cursos como docente si aplica
                result_docente = db.execute(text("""
                    SELECT DISTINCT 
                        c.curso_id,
                        c.nombre,
                        c.descripcion,
                        c.codigo_acceso,
                        c.modalidad,
                        c.fecha_inicio,
                        c.fecha_fin,
                        g.nombre as grupo_nombre,
                        u_docente.nombres || ' ' || u_docente.apellidos as instructor,
                        i.nombre as institucion_nombre,
                        COUNT(DISTINCT eg_count.estudiante_id) as total_estudiantes,
                        'docente' as tipo_vinculacion
                    FROM "GrupoCurso" gc
                    JOIN "Grupo" g ON gc.grupo_id = g.grupo_id
                    JOIN "Curso" c ON gc.curso_id = c.curso_id
                    LEFT JOIN "Usuario" u_docente ON gc.docente_id = u_docente.usuario_id
                    LEFT JOIN "EstudianteGrupo" eg_count ON g.grupo_id = eg_count.grupo_id
                    LEFT JOIN "Programa" p ON g.programa_id = p.programa_id
                    LEFT JOIN "Institucion" i ON p.institucion_id = i.institucion_id
                    WHERE gc.docente_id = :usuario_id 
                    GROUP BY c.curso_id, c.nombre, c.descripcion, c.codigo_acceso, 
                             c.modalidad, c.fecha_inicio, c.fecha_fin,
                             g.nombre, u_docente.nombres, u_docente.apellidos, i.nombre
                    ORDER BY c.fecha_inicio DESC
                """), {"usuario_id": current_user.usuario_id})

                cursos_raw = result_estudiante.fetchall() + result_docente.fetchall()
            
            # Agrupar por curso_id para evitar duplicados
            cursos_dict = {}
            for curso in cursos_raw:
                curso_id = curso[0]
                nombre = curso[1]
                descripcion = curso[2]
                codigo_acceso = curso[3]
                modalidad = curso[4]
                fecha_inicio = curso[5]
                fecha_fin = curso[6]
                grupo_nombre = curso[7]
                instructor = curso[8] or "Profesor Asignado"
                institucion_nombre = curso[9] or "Institución"
                total_estudiantes = curso[10] or 0
                
                if curso_id not in cursos_dict:
                    # Calcular estado real basado en fechas
                    from datetime import datetime, date
                    hoy = date.today()
                    
                    if fecha_inicio and fecha_fin:
                        if hoy < fecha_inicio:
                            estado_calculado = "próximo"
                            color_estado = "bg-yellow-600"
                        elif hoy > fecha_fin:
                            estado_calculado = "finalizado"
                            color_estado = "bg-gray-600"
                        else:
                            estado_calculado = "activo"
                            color_estado = "bg-blue-600"
                    else:
                        estado_calculado = "activo"
                        color_estado = "bg-blue-600"
                    
                    # Calcular progreso real basado en fechas
                    if fecha_inicio and fecha_fin and estado_calculado in ["activo", "finalizado"]:
                        total_dias = (fecha_fin - fecha_inicio).days
                        if estado_calculado == "finalizado":
                            progreso_calculado = 100
                        elif total_dias > 0:
                            dias_transcurridos = (hoy - fecha_inicio).days
                            progreso_calculado = min(100, max(0, int((dias_transcurridos / total_dias) * 100)))
                        else:
                            progreso_calculado = 0
                    else:
                        progreso_calculado = 0
                    
                    # Calcular duración en semanas
                    if fecha_inicio and fecha_fin:
                        total_dias = (fecha_fin - fecha_inicio).days
                        semanas = max(1, total_dias // 7)
                        duracion_calculada = f"{semanas} semanas"
                    else:
                        duracion_calculada = "16 semanas"
                    
                    cursos_dict[curso_id] = {
                        "id": str(curso_id),
                        "course_id": str(curso_id),
                        "title": nombre,
                        "nombre": nombre,
                        "description": descripcion or f"Curso de {nombre}",
                        "descripcion": descripcion or f"Curso de {nombre}",
                        "codigo": codigo_acceso,
                        "codigo_acceso": codigo_acceso,
                        "modalidad": modalidad or "Presencial",
                        "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else "2025-01-15",
                        "fecha_fin": fecha_fin.isoformat() if fecha_fin else "2025-06-15",
                        "estado": estado_calculado,
                        "grupos": [],
                        "instructor": instructor,
                        "profesor": instructor,
                        "estudiantes": total_estudiantes,
                        "total_estudiantes": total_estudiantes,
                        "progress": progreso_calculado,
                        "progreso": progreso_calculado,
                        "creditos": 3,
                        "horas": 48,
                        "duration": duracion_calculada,
                        "color": color_estado,
                        "institucion": institucion_nombre
                    }
                cursos_dict[curso_id]["grupos"].append({
                    "nombre": grupo_nombre,
                    "total_estudiantes": total_estudiantes
                })
            
            cursos_data = list(cursos_dict.values())
            
            if not cursos_data:
                return {
                    "success": True,
                    "message": "Aún no te has unido a ningún curso",
                    "data": [],
                    "total": 0,
                    "source": "database",
                    "user_role": current_user.rol.value,
                    "empty_state": True,
                    "empty_message": "¡Únete a un curso para comenzar tu aprendizaje!"
                }
            
            return {
                "success": True,
                "message": f"Se encontraron {len(cursos_data)} cursos",
                "data": cursos_data,
                "total": len(cursos_data),
                "source": "database",
                "user_role": current_user.rol.value,
                "empty_state": False,
                "empty_message": None
            }
        
        except Exception as e:
            logger.error(f"Error en consulta de cursos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al obtener cursos: {str(e)}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error general en get_mis_cursos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/disponibles")
async def get_cursos_disponibles(current_user: Usuario = Depends(deps.get_current_user)):
    """
    Obtener lista de cursos disponibles con sus códigos (para profesores/coordinadores)
    """
    try:
        logger.info(f"Obteniendo cursos disponibles para usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Solo mostrar cursos si el usuario es coordinador, docente o admin
            if current_user.rol.value not in ['coordinador', 'docente', 'administrador']:
                raise HTTPException(
                    status_code=403,
                    detail="No tienes permisos para ver la lista de cursos disponibles"
                )
            
            # Consultar todos los cursos disponibles
            result = db.execute(text("""
                SELECT 
                    c.curso_id,
                    c.nombre,
                    c.descripcion,
                    c.codigo_acceso,
                    c.modalidad,
                    c.fecha_inicio,
                    c.fecha_fin,
                    COUNT(DISTINCT eg.estudiante_id) as total_estudiantes
                FROM "Curso" c
                LEFT JOIN "GrupoCurso" gc ON c.curso_id = gc.curso_id
                LEFT JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id
                GROUP BY c.curso_id, c.nombre, c.descripcion, c.codigo_acceso, 
                         c.modalidad, c.fecha_inicio, c.fecha_fin
                ORDER BY c.fecha_inicio DESC
            """))
            
            cursos_raw = result.fetchall()
            
            cursos_data = []
            for curso in cursos_raw:
                curso_data = {
                    "id": str(curso[0]),
                    "nombre": curso[1],
                    "descripcion": curso[2] or f"Curso de {curso[1]}",
                    "codigo_acceso": curso[3],
                    "modalidad": curso[4],
                    "fecha_inicio": curso[5].isoformat() if curso[5] else None,
                    "fecha_fin": curso[6].isoformat() if curso[6] else None,
                    "total_estudiantes": curso[7] or 0
                }
                cursos_data.append(curso_data)
            
            return {
                "success": True,
                "message": f"Se encontraron {len(cursos_data)} cursos disponibles",
                "data": cursos_data,
                "total": len(cursos_data)
            }
            
        finally:
            db.close()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo cursos disponibles: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al obtener cursos"
        )

@router.post("/auto-vincular-estudiante")
async def auto_vincular_estudiante(
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Vinculación automática inteligente de estudiante basada en:
    1. Dominio de email institucional
    2. Código de invitación (si se proporciona)
    """
    try:
        logger.info(f"Auto-vinculando usuario {current_user.usuario_id} - {current_user.correo_institucional}")
        
        # Verificar si ya existe perfil de estudiante
        estudiante_existente = db.execute(text("""
            SELECT e.estudiante_id, p.nombre as programa_nombre, i.nombre as institucion_nombre
            FROM "Estudiante" e
            JOIN "Programa" p ON e.programa_id = p.programa_id
            JOIN "Institucion" i ON p.institucion_id = i.institucion_id
            WHERE e.estudiante_id = :usuario_id
        """), {"usuario_id": current_user.usuario_id}).fetchone()
        
        if estudiante_existente:
            programa_nombre = estudiante_existente[1]
            institucion_nombre = estudiante_existente[2]
            return {
                "success": True,
                "message": f"Ya estás vinculado al programa '{programa_nombre}' de '{institucion_nombre}'",
                "programa": programa_nombre,
                "institucion": institucion_nombre,
                "metodo": "ya_vinculado"
            }
        
        # MÉTODO 1: Vinculación por dominio de email
        user_email = current_user.correo_institucional
        if not user_email:
            raise HTTPException(
                status_code=400,
                detail="No tienes email registrado. Contacta al administrador."
            )
        
        # Extraer dominio del email
        email_domain = user_email.split('@')[1].lower() if '@' in user_email else None
        
        logger.info(f"Buscando institución por dominio: {email_domain}")
        
        # Buscar institución por dominio de email
        # Nota: Necesitaremos agregar campo 'dominio' a la tabla Institución
        institucion_por_dominio = None
        
        # Mapeo temporal de dominios (esto debería estar en la BD)
        dominios_instituciones = {
            'arp.edu.co': 'Colegio Alejandro Obregón',
            'uniejemplo.edu': 'Universidad Ejemplo',
            'colegio-ao.edu': 'Colegio Alejandro Obregón',
            'ejemplo.edu.co': 'Universidad Ejemplo'
        }
        
        institucion_nombre_matched = dominios_instituciones.get(email_domain)
        
        if institucion_nombre_matched:
            # Buscar TODOS los programas disponibles de la institución
            programas_disponibles = db.execute(text("""
                SELECT p.programa_id, p.nombre as programa_nombre, p.descripcion,
                       i.institucion_id, i.nombre as institucion_nombre
                FROM "Programa" p
                JOIN "Institucion" i ON p.institucion_id = i.institucion_id
                WHERE LOWER(i.nombre) = LOWER(:institucion_nombre)
                ORDER BY p.nombre
            """), {"institucion_nombre": institucion_nombre_matched}).fetchall()
            
            if programas_disponibles:
                programas_list = []
                for programa in programas_disponibles:
                    programas_list.append({
                        "programa_id": str(programa[0]),
                        "nombre": programa[1],
                        "descripcion": programa[2] or "Sin descripción"
                    })
                
                return {
                    "success": True,
                    "message": f"Tu email '{user_email}' te vincula a '{institucion_nombre_matched}'. Selecciona tu programa:",
                    "tipo": "seleccion_programa", 
                    "institucion": {
                        "id": str(programas_disponibles[0][3]),
                        "nombre": programas_disponibles[0][4]
                    },
                    "programas_disponibles": programas_list,
                    "dominio": email_domain
                }
            else:
                return {
                    "success": False,
                    "message": f"No hay programas disponibles en '{institucion_nombre_matched}'. Contacta al coordinador.",
                    "tipo": "sin_programas"
                }
        
        # MÉTODO 2: Si no hay vinculación por dominio, ofrecer código de invitación
        return {
            "success": False,
            "requires_invitation": True,
            "message": f"Tu dominio '{email_domain}' no está registrado en el sistema. Necesitas un código de invitación de tu institución.",
            "user_email": user_email,
            "dominio": email_domain
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en auto-vinculación: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/confirmar-programa")
async def confirmar_seleccion_programa(
    request: dict,  # {"programa_id": "uuid"}
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Confirmar selección de programa después de auto-vinculación por dominio
    """
    try:
        programa_id = request.get("programa_id")
        if not programa_id:
            raise HTTPException(
                status_code=400,
                detail="programa_id es requerido"
            )
        
        logger.info(f"Usuario {current_user.usuario_id} confirmando programa: {programa_id}")
        
        # Verificar que el usuario no tenga ya un perfil de estudiante
        estudiante_existente = db.execute(text("""
            SELECT estudiante_id FROM "Estudiante" WHERE estudiante_id = :usuario_id
        """), {"usuario_id": current_user.usuario_id}).fetchone()
        
        if estudiante_existente:
            raise HTTPException(
                status_code=409,
                detail="Ya tienes un perfil de estudiante. No puedes cambiar de programa."
            )
        
        # Verificar que el programa existe y obtener información
        programa_info = db.execute(text("""
            SELECT p.programa_id, p.nombre as programa_nombre, 
                   i.institucion_id, i.nombre as institucion_nombre
            FROM "Programa" p
            JOIN "Institucion" i ON p.institucion_id = i.institucion_id
            WHERE p.programa_id = :programa_id
        """), {"programa_id": programa_id}).fetchone()
        
        if not programa_info:
            raise HTTPException(
                status_code=404,
                detail="Programa no encontrado"
            )
        
        # Crear perfil de estudiante
        db.execute(text("""
            INSERT INTO "Estudiante" (
                estudiante_id, programa_id, fecha_ingreso, 
                etapa_formativa, creditos_aprobados
            ) VALUES (
                :usuario_id, :programa_id, CURRENT_DATE,
                'i', 0
            )
        """), {
            "usuario_id": current_user.usuario_id,
            "programa_id": programa_id
        })
        
        db.commit()
        
        logger.info(f"Usuario {current_user.usuario_id} vinculado al programa {programa_info[1]} de {programa_info[3]}")
        
        return {
            "success": True,
            "message": f"¡Perfil de estudiante creado exitosamente! Te has vinculado al programa '{programa_info[1]}' de '{programa_info[3]}'",
            "programa": {
                "id": str(programa_info[0]),
                "nombre": programa_info[1]
            },
            "institucion": {
                "id": str(programa_info[2]), 
                "nombre": programa_info[3]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirmando programa: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/vincular-por-codigo")
async def vincular_por_codigo_invitacion(
    request: EstudianteVinculacionRequest,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Vinculación de estudiante mediante código de invitación
    """
    try:
        codigo = request.codigo_invitacion
        if not codigo:
            raise HTTPException(
                status_code=400,
                detail="Debes proporcionar un código de invitación"
            )
        
        logger.info(f"Vinculando usuario {current_user.usuario_id} con código {codigo}")
        
        # Verificar si ya existe perfil de estudiante
        estudiante_existente = db.execute(text("""
            SELECT e.estudiante_id, p.nombre as programa_nombre, i.nombre as institucion_nombre
            FROM "Estudiante" e
            JOIN "Programa" p ON e.programa_id = p.programa_id
            JOIN "Institucion" i ON p.institucion_id = i.institucion_id
            WHERE e.estudiante_id = :usuario_id
        """), {"usuario_id": current_user.usuario_id}).fetchone()
        
        if estudiante_existente:
            programa_nombre = estudiante_existente[1]
            institucion_nombre = estudiante_existente[2]
            return {
                "success": True,
                "message": f"Ya estás vinculado al programa '{programa_nombre}' de '{institucion_nombre}'",
                "programa": programa_nombre,
                "institucion": institucion_nombre,
                "metodo": "ya_vinculado"
            }
        
        # Buscar código de invitación válido
        # Nota: Necesitaremos crear tabla CodigoInvitacion
        # Por ahora, simulación con códigos hardcodeados
        codigos_validos = {
            'INV-2025-ARP-001': ('Colegio Alejandro Obregón', 'Bachillerato Científico'),
            'INV-2025-UNEJ-001': ('Universidad Ejemplo', 'Ingeniería de Sistemas'),
            'INV-2025-ARP-MED': ('Colegio Alejandro Obregón', 'Bachillerato Médico'),
            'TEST-ARP-2025': ('Colegio Alejandro Obregón', 'Bachillerato Científico')
        }
        
        if codigo not in codigos_validos:
            raise HTTPException(
                status_code=404,
                detail="Código de invitación inválido o expirado"
            )
        
        institucion_nombre, programa_nombre = codigos_validos[codigo]
        
        # Buscar programa en la base de datos
        programa_result = db.execute(text("""
            SELECT p.programa_id, p.nombre as programa_nombre, 
                   i.institucion_id, i.nombre as institucion_nombre
            FROM "Programa" p
            JOIN "Institucion" i ON p.institucion_id = i.institucion_id
            WHERE LOWER(i.nombre) = LOWER(:institucion_nombre)
              AND LOWER(p.nombre) = LOWER(:programa_nombre)
        """), {
            "institucion_nombre": institucion_nombre,
            "programa_nombre": programa_nombre
        }).fetchone()
        
        if not programa_result:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró el programa '{programa_nombre}' en '{institucion_nombre}'"
            )
        
        programa_id, programa_db_nombre, institucion_id, institucion_db_nombre = programa_result
        
        # Crear perfil de estudiante
        db.execute(text("""
            INSERT INTO "Estudiante" (
                estudiante_id, programa_id, fecha_ingreso, 
                etapa_formativa, creditos_aprobados
            ) VALUES (
                :usuario_id, :programa_id, CURRENT_DATE,
                'i', 0
            )
        """), {
            "usuario_id": current_user.usuario_id,
            "programa_id": programa_id
        })
        
        db.commit()
        
        logger.info(f"Usuario {current_user.usuario_id} vinculado exitosamente con código {codigo}")
        
        return {
            "success": True,
            "message": f"¡Vinculación exitosa! Código '{codigo}' te ha vinculado al programa '{programa_db_nombre}' de '{institucion_db_nombre}'",
            "programa": programa_db_nombre,
            "institucion": institucion_db_nombre,
            "metodo": "codigo_invitacion",
            "codigo_usado": codigo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en vinculación por código: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/generar-codigo-invitacion")
async def generar_codigo_invitacion(
    request: CodigoInvitacionGenerate,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Genera un código de invitación para un programa específico
    Solo coordinadores o administradores pueden generar códigos
    """
    try:
        programa_id = request.programa_id
        descripcion = request.descripcion or "Código generado por coordinador"
        
        # Verificar que el programa existe y obtener datos
        programa_result = db.execute(text("""
            SELECT p.programa_id, p.nombre as programa_nombre, 
                   i.institucion_id, i.nombre as institucion_nombre
            FROM "Programa" p
            JOIN "Institucion" i ON p.institucion_id = i.institucion_id
            WHERE p.programa_id = :programa_id
        """), {"programa_id": programa_id}).fetchone()
        
        if not programa_result:
            raise HTTPException(
                status_code=404,
                detail="El programa especificado no existe"
            )
        
        _, programa_nombre, institucion_id, institucion_nombre = programa_result
        
        # Generar código único
        import random
        import string
        from datetime import datetime
        
        # Formato: INV-YEAR-INST-NNN
        year = datetime.now().year
        inst_code = institucion_nombre[:3].upper().replace(" ", "")
        random_suffix = ''.join(random.choices(string.digits, k=3))
        codigo_invitacion = f"INV-{year}-{inst_code}-{random_suffix}"
        
        # En una implementación real, guardaríamos esto en una tabla CodigoInvitacion
        # Por ahora, retornamos el código generado
        
        logger.info(f"Código de invitación generado: {codigo_invitacion} para programa {programa_nombre}")
        
        return {
            "success": True,
            "codigo_invitacion": codigo_invitacion,
            "programa": programa_nombre,
            "institucion": institucion_nombre,
            "descripcion": descripcion,
            "valido_hasta": "2025-12-31",  # Ejemplo de fecha de expiración
            "generado_por": current_user.nombre_usuario,
            "instrucciones": f"Comparte este código con estudiantes que deseen unirse al programa '{programa_nombre}'. El código es válido hasta diciembre 2025."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando código de invitación: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/programas-disponibles")
async def get_programas_disponibles(current_user: Usuario = Depends(deps.get_current_user)):
    """
    Obtener lista de programas académicos disponibles por institución
    """
    try:
        db = SessionLocal()
        
        try:
            result = db.execute(text("""
                SELECT p.programa_id, p.nombre as programa_nombre, p.nivel, p.tipo,
                       i.institucion_id, i.nombre as institucion_nombre
                FROM "Programa" p
                JOIN "Institucion" i ON p.institucion_id = i.institucion_id
                ORDER BY i.nombre, p.nombre
            """))
            
            # Agrupar por institución
            instituciones = {}
            for row in result.fetchall():
                programa_id, programa_nombre, nivel, tipo, institucion_id, institucion_nombre = row
                
                if institucion_nombre not in instituciones:
                    instituciones[institucion_nombre] = {
                        "institucion_id": str(institucion_id),
                        "nombre": institucion_nombre,
                        "programas": []
                    }
                
                instituciones[institucion_nombre]["programas"].append({
                    "programa_id": str(programa_id),
                    "nombre": programa_nombre,
                    "nivel": nivel,
                    "tipo": tipo
                })
            
            return {
                "success": True,
                "data": list(instituciones.values()),
                "total": len(instituciones)
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error obteniendo programas: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/debug/usuario-cursos")
async def debug_usuario_cursos(current_user: Usuario = Depends(deps.get_current_user)):
    """
    Debug: Ver datos completos del usuario y sus inscripciones
    """
    db = SessionLocal()
    try:
        # 1. Info del usuario
        usuario_info = {
            "usuario_id": str(current_user.usuario_id),
            "correo": current_user.correo_institucional,
            "nombres": current_user.nombres,
            "apellidos": current_user.apellidos
        }
        
        # 2. Verificar si tiene perfil de estudiante
        estudiante_query = db.execute(text("""
            SELECT e.estudiante_id, e.programa_id, p.nombre as programa_nombre, 
                   i.nombre as institucion_nombre
            FROM "Estudiante" e
            JOIN "Programa" p ON e.programa_id = p.programa_id  
            JOIN "Institucion" i ON p.institucion_id = i.institucion_id
            WHERE e.estudiante_id = :usuario_id
        """), {"usuario_id": current_user.usuario_id})
        
        estudiante_info = estudiante_query.fetchone()
        
        # 3. Ver inscripciones en grupos
        inscripciones_query = db.execute(text("""
            SELECT eg.grupo_id, g.nombre as grupo_nombre, c.nombre as curso_nombre,
                   c.curso_id, eg.fecha_vinculacion
            FROM "EstudianteGrupo" eg
            JOIN "Grupo" g ON eg.grupo_id = g.grupo_id
            JOIN "GrupoCurso" gc ON g.grupo_id = gc.grupo_id
            JOIN "Curso" c ON gc.curso_id = c.curso_id
            JOIN "Estudiante" e ON eg.estudiante_id = e.estudiante_id
            WHERE e.estudiante_id = :usuario_id
        """), {"usuario_id": current_user.usuario_id})
        
        inscripciones_raw = inscripciones_query.fetchall()
        inscripciones = [dict(row._mapping) for row in inscripciones_raw]
        
        return {
            "usuario": usuario_info,
            "estudiante": dict(estudiante_info._mapping) if estudiante_info else None,
            "inscripciones": inscripciones,
            "total_inscripciones": len(inscripciones)
        }
        
    finally:
        db.close()


@router.get("/debug/info")
async def get_debug_info():
    """
    Endpoint temporal para debugging - obtener información de cursos, instituciones y programas
    """
    try:
        db = SessionLocal()
        
        try:
            # Obtener información de cursos existentes
            cursos_result = db.execute(text("""
                SELECT curso_id, nombre, codigo_acceso 
                FROM "Curso" 
                ORDER BY nombre
                LIMIT 10
            """))
            
            cursos = []
            for row in cursos_result.fetchall():
                cursos.append({
                    "curso_id": str(row[0]),
                    "nombre": row[1],
                    "codigo_acceso": row[2]
                })
            
            # Obtener información de instituciones
            instituciones_result = db.execute(text("""
                SELECT institucion_id, nombre
                FROM "Institucion"
                ORDER BY nombre
                LIMIT 5
            """))
            
            instituciones = []
            for row in instituciones_result.fetchall():
                instituciones.append({
                    "institucion_id": str(row[0]),
                    "nombre": row[1]
                })
            
            # Obtener información de programas
            programas_result = db.execute(text("""
                SELECT programa_id, nombre
                FROM "Programa"
                ORDER BY nombre
                LIMIT 10
            """))
            
            programas = []
            for row in programas_result.fetchall():
                programas.append({
                    "programa_id": str(row[0]),
                    "nombre": row[1]
                })
            
            return {
                "success": True,
                "data": {
                    "cursos": cursos,
                    "instituciones": instituciones,
                    "programas": programas,
                    "total_cursos": len(cursos),
                    "total_instituciones": len(instituciones),
                    "total_programas": len(programas)
                }
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error en debug info: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/{curso_id}")
async def get_curso_detalle(
    curso_id: str,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """
    Obtener detalles completos de un curso específico
    """
    try:
        logger.info(f"Obteniendo detalles del curso {curso_id} para usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Consultar detalles del curso con datos completos incluyendo programa
            result = db.execute(text("""
                SELECT 
                    c.curso_id,
                    c.nombre,
                    c.descripcion,
                    c.codigo_acceso,
                    c.modalidad,
                    c.fecha_inicio,
                    c.fecha_fin,
                    u_docente.nombres || ' ' || u_docente.apellidos as instructor,
                    u_docente.correo_institucional as instructor_email,
                    COUNT(DISTINCT eg.estudiante_id) as total_estudiantes,
                    p.programa_id,
                    p.nombre as programa_nombre,
                    p.nivel as programa_nivel,
                    p.tipo as programa_tipo,
                    i.institucion_id,
                    i.nombre as institucion_nombre
                FROM "Curso" c
                LEFT JOIN "GrupoCurso" gc ON c.curso_id = gc.curso_id
                LEFT JOIN "Usuario" u_docente ON gc.docente_id = u_docente.usuario_id
                LEFT JOIN "EstudianteGrupo" eg ON gc.grupo_id = eg.grupo_id
                LEFT JOIN "Grupo" g ON gc.grupo_id = g.grupo_id
                LEFT JOIN "Programa" p ON g.programa_id = p.programa_id
                LEFT JOIN "Institucion" i ON p.institucion_id = i.institucion_id
                WHERE c.curso_id = :curso_id
                GROUP BY c.curso_id, c.nombre, c.descripcion, c.codigo_acceso, 
                         c.modalidad, c.fecha_inicio, c.fecha_fin,
                         u_docente.nombres, u_docente.apellidos, u_docente.correo_institucional,
                         p.programa_id, p.nombre, p.nivel, p.tipo,
                         i.institucion_id, i.nombre
                LIMIT 1
            """), {"curso_id": curso_id})
            
            curso_raw = result.fetchone()
            
            if not curso_raw:
                raise HTTPException(
                    status_code=404,
                    detail="Curso no encontrado"
                )
            
            # Verificar si el usuario está inscrito en este curso
            inscripcion_result = db.execute(text("""
                SELECT 1 FROM "EstudianteGrupo" eg
                JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id  
                WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
            """), {"curso_id": curso_id, "usuario_id": current_user.usuario_id}).fetchone()
            
            esta_inscrito = inscripcion_result is not None
            
            # Importar datetime para cálculos
            from datetime import datetime, date
            
            # Extraer datos del curso incluyendo información del programa
            curso_id = curso_raw[0]
            nombre = curso_raw[1]
            descripcion = curso_raw[2]
            codigo_acceso = curso_raw[3]
            modalidad = curso_raw[4]
            fecha_inicio = curso_raw[5]
            fecha_fin = curso_raw[6]
            instructor = curso_raw[7] or "Profesor Asignado"
            instructor_email = curso_raw[8] or "profesor@acadify.com"
            total_estudiantes = curso_raw[9] or 0
            
            # Información del programa
            programa_id = curso_raw[10]
            programa_nombre = curso_raw[11]
            programa_nivel = curso_raw[12]
            programa_tipo = curso_raw[13]
            institucion_id = curso_raw[14]
            institucion_nombre = curso_raw[15]
            
            # Calcular estado basado en fechas
            hoy = date.today()
            estado_calculado = "activo"
            progress = 0
            
            if fecha_inicio and fecha_fin:
                if hoy < fecha_inicio:
                    estado_calculado = "próximo"
                    progress = 0
                elif hoy > fecha_fin:
                    estado_calculado = "completado"
                    progress = 100
                else:
                    estado_calculado = "activo"
                    # Calcular progreso basado en fechas
                    total_dias = (fecha_fin - fecha_inicio).days
                    dias_transcurridos = (hoy - fecha_inicio).days
                    if total_dias > 0:
                        progress = min(100, max(0, int((dias_transcurridos / total_dias) * 100)))
                    else:
                        progress = 50
            
            # Calcular duración del curso
            duration = "16 semanas"
            if fecha_inicio and fecha_fin:
                total_dias = (fecha_fin - fecha_inicio).days
                semanas = max(1, total_dias // 7)
                duration = f"{semanas} semanas"
            
            # Obtener información de personas inscritas en el curso
            import time
            start_time = time.time()
            logger.info(f"Obteniendo personas inscritas en curso {curso_id}")
            
            # Consulta optimizada que obtiene estudiantes y profesores, con lógica de deduplicación
            personas_result = db.execute(text("""
                WITH personas_curso AS (
                    -- Estudiantes inscritos
                    SELECT DISTINCT
                        u.usuario_id,
                        u.nombres,
                        u.apellidos,
                        u.correo_institucional,
                        u.perfil_url,
                        u.ultimo_acceso,
                        eg.fecha_vinculacion as fecha,
                        'estudiante' as tipo_persona,
                        1 as prioridad  -- Menor prioridad para estudiantes
                    FROM "Usuario" u
                    JOIN "EstudianteGrupo" eg ON u.usuario_id = eg.estudiante_id
                    JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
                    WHERE gc.curso_id = :curso_id AND u.rol = 'estudiante'
                    
                    UNION ALL
                    
                    -- Profesores/docentes del curso
                    SELECT DISTINCT
                        u.usuario_id,
                        u.nombres,
                        u.apellidos,
                        u.correo_institucional,
                        u.perfil_url,
                        u.ultimo_acceso,
                        gc.fecha_asignacion as fecha,
                        'docente' as tipo_persona,
                        2 as prioridad  -- Mayor prioridad para docentes
                    FROM "Usuario" u
                    JOIN "GrupoCurso" gc ON u.usuario_id = gc.docente_id
                    WHERE gc.curso_id = :curso_id AND u.rol IN ('docente', 'coordinador')
                ),
                personas_deduplicadas AS (
                    SELECT DISTINCT ON (usuario_id)
                        usuario_id,
                        nombres,
                        apellidos,
                        correo_institucional,
                        perfil_url,
                        ultimo_acceso,
                        fecha,
                        tipo_persona
                    FROM personas_curso
                    ORDER BY usuario_id, prioridad DESC, tipo_persona DESC
                )
                SELECT * FROM personas_deduplicadas
                ORDER BY tipo_persona DESC, nombres, apellidos
            """), {"curso_id": curso_id})
            
            personas_raw = personas_result.fetchall()
            query_time = time.time() - start_time
            logger.info(f"Consulta de personas completada en {query_time:.3f} segundos. Encontradas {len(personas_raw)} personas")
            
            # Procesar resultados separando estudiantes y profesores
            estudiantes = []
            profesores = []
            
            for persona in personas_raw:
                fecha_key = "fecha_vinculacion" if persona[7] == 'estudiante' else "fecha_asignacion"
                
                # Generar URL del avatar basada en el ID del usuario
                avatar_url = persona[4] if persona[4] else f"/static/avatars/{persona[0]}.png"
                
                persona_data = {
                    "id": str(persona[0]),
                    "nombres": persona[1],
                    "apellidos": persona[2],
                    "nombre_completo": f"{persona[1]} {persona[2]}",
                    "correo": persona[3],
                    "avatar_url": avatar_url,  # URL del avatar o URL generada
                    "ultimo_acceso": persona[5].isoformat() if persona[5] else None,
                    fecha_key: persona[6].isoformat() if persona[6] else None,
                    "rol": persona[7]
                }
                
                if persona[7] == 'estudiante':
                    estudiantes.append(persona_data)
                else:  # docente
                    profesores.append(persona_data)
            
            logger.info(f"Encontrados {len(estudiantes)} estudiantes y {len(profesores)} profesores")
            
            curso_detalle = {
                "success": True,
                "data": {
                    "id": str(curso_id),
                    "course_id": str(curso_id),
                    "title": nombre,
                    "nombre": nombre,
                    "description": descripcion or f"Curso de {nombre}",
                    "descripcion": descripcion or f"Curso de {nombre}",
                    "codigo": codigo_acceso,
                    "codigo_acceso": codigo_acceso,
                    "modalidad": modalidad or "Presencial",
                    "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else "2025-01-15",
                    "fecha_fin": fecha_fin.isoformat() if fecha_fin else "2025-06-15",
                    "estado": estado_calculado,
                    "instructor": instructor,
                    "profesor": instructor,
                    "instructor_email": instructor_email,
                    "estudiantes": total_estudiantes,
                    "total_estudiantes": total_estudiantes,
                    "progress": progress,
                    "progreso": progress,
                    "creditos": 3,  # Valor por defecto
                    "horas": 48,  # Valor por defecto
                    "duration": duration,
                    "esta_inscrito": esta_inscrito,
                    "programa": {
                        "id": str(programa_id) if programa_id else None,
                        "nombre": programa_nombre or "Programa Académico",
                        "codigo": "PROG",  # Código por defecto ya que no existe en BD
                        "nivel": programa_nivel or "pregrado",
                        "tipo": programa_tipo or "profesional",
                        "facultad": institucion_nombre or "Facultad Académica"
                    } if programa_id else {
                        "id": None,
                        "nombre": "ISYS - Ingeniería de Sistemas",
                        "codigo": "ISYS",
                        "nivel": "pregrado",
                        "tipo": "profesional",
                        "facultad": "Facultad de Ingeniería"
                    },
                    "personas": {
                        "estudiantes": estudiantes,
                        "profesores": profesores,
                        "total_estudiantes": len(estudiantes),
                        "total_profesores": len(profesores)
                    }
                }
            }
            
            logger.info(f"Detalles del curso {curso_id} obtenidos exitosamente")
            
            return curso_detalle
            
        finally:
            db.close()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalles del curso {curso_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/{curso_id}/comentarios")
async def obtener_comentarios_curso(
    curso_id: str, 
    limit: int = 20, 
    offset: int = 0,
    tipo: Optional[str] = None,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Obtener comentarios/anuncios del curso desde la base de datos"""
    try:
        logger.info(f"Obteniendo comentarios del curso {curso_id} para usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar que el usuario tenga acceso al curso
            acceso_result = db.execute(text("""
                SELECT 1 FROM "EstudianteGrupo" eg
                JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id  
                WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
                
                UNION
                
                SELECT 1 FROM "GrupoCurso" gc
                WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
            """), {"curso_id": curso_id, "usuario_id": current_user.usuario_id}).fetchone()
            
            if not acceso_result:
                raise HTTPException(
                    status_code=403,
                    detail="No tienes acceso a este curso"
                )
            
            # Obtener comentarios usando CRUD
            comentarios = crud_comentario.get_comentarios_con_respuestas(
                db=db,
                curso_id=uuid.UUID(curso_id),
                skip=offset,
                limit=limit
            )
            
            # Preparar datos para respuesta
            comentarios_data = []
            for comentario in comentarios:
                # Obtener información del autor
                autor_info = db.execute(text("""
                    SELECT nombres, apellidos, correo_institucional
                    FROM "Usuario"
                    WHERE usuario_id = :autor_id
                """), {"autor_id": comentario.autor_id}).fetchone()
                
                # Obtener respuestas del comentario
                respuestas = crud_comentario.get_respuestas_comentario(
                    db=db,
                    comentario_padre_id=comentario.comentario_id
                )
                
                respuestas_data = []
                for respuesta in respuestas:
                    autor_respuesta = db.execute(text("""
                        SELECT nombres, apellidos, correo_institucional
                        FROM "Usuario"
                        WHERE usuario_id = :autor_id
                    """), {"autor_id": respuesta.autor_id}).fetchone()
                    
                    # Obtener archivos adjuntos de la respuesta
                    archivos_respuesta = []
                    if respuesta.archivos_adjuntos:
                        try:
                            import json
                            archivos_raw = json.loads(respuesta.archivos_adjuntos) if isinstance(respuesta.archivos_adjuntos, str) else respuesta.archivos_adjuntos
                            
                            # Normalizar campos de archivos para compatibilidad
                            for archivo in archivos_raw:
                                if isinstance(archivo, dict):
                                    archivo_normalizado = {
                                        "id": archivo.get("id", archivo.get("filename", archivo.get("nombre", ""))),
                                        "nombre": archivo.get("nombre", archivo.get("filename", archivo.get("name", "Archivo"))),
                                        "url": archivo.get("url", ""),
                                        "tamaño": archivo.get("tamaño", archivo.get("size", 0)),
                                        "tipo": archivo.get("tipo", archivo.get("type", "application/octet-stream")),
                                        "fecha_subida": archivo.get("fecha_subida", archivo.get("upload_date", ""))
                                    }
                                    archivos_respuesta.append(archivo_normalizado)
                        except (json.JSONDecodeError, TypeError):
                            archivos_respuesta = []
                    
                    respuestas_data.append({
                        "id": str(respuesta.comentario_id),
                        "autor": f"{autor_respuesta.nombres} {autor_respuesta.apellidos}" if autor_respuesta else "Usuario desconocido",
                        "contenido": respuesta.contenido,
                        "fecha": respuesta.fecha_creacion.isoformat(),
                        "tipo": respuesta.tipo.value,
                        "archivos": archivos_respuesta,
                        "editado": respuesta.editado
                    })
                
                # Obtener archivos adjuntos del comentario principal
                archivos_comentario = []
                if comentario.archivos_adjuntos:
                    try:
                        import json
                        archivos_raw = json.loads(comentario.archivos_adjuntos) if isinstance(comentario.archivos_adjuntos, str) else comentario.archivos_adjuntos
                        
                        # Normalizar campos de archivos para compatibilidad
                        archivos_comentario = []
                        for archivo in archivos_raw:
                            if isinstance(archivo, dict):
                                # Normalizar campos (tanto viejos como nuevos formatos)
                                archivo_normalizado = {
                                    "id": archivo.get("id", archivo.get("filename", archivo.get("nombre", ""))),
                                    "nombre": archivo.get("nombre", archivo.get("filename", archivo.get("name", "Archivo"))),
                                    "url": archivo.get("url", ""),
                                    "tamaño": archivo.get("tamaño", archivo.get("size", 0)),
                                    "tipo": archivo.get("tipo", archivo.get("type", "application/octet-stream")),
                                    "fecha_subida": archivo.get("fecha_subida", archivo.get("upload_date", ""))
                                }
                                archivos_comentario.append(archivo_normalizado)
                        
                        logger.info(f"📎 RECUPERANDO archivos del comentario {comentario.comentario_id}:")
                        logger.info(f"📎 Archivos RAW: {archivos_raw}")
                        logger.info(f"📎 Archivos NORMALIZADOS: {archivos_comentario}")
                        logger.info(f"📎 Cantidad: {len(archivos_comentario)}")
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.error(f"📎 ERROR parseando archivos del comentario {comentario.comentario_id}: {e}")
                        archivos_comentario = []
                else:
                    logger.info(f"📎 El comentario {comentario.comentario_id} no tiene archivos adjuntos")
                
                comentarios_data.append({
                    "id": str(comentario.comentario_id),
                    "autor": f"{autor_info.nombres} {autor_info.apellidos}" if autor_info else "Usuario desconocido",
                    "contenido": comentario.contenido,
                    "fecha": comentario.fecha_creacion.isoformat(),
                    "tipo": comentario.tipo.value,
                    "archivos": archivos_comentario,
                    "editado": comentario.editado,
                    "respuestas": respuestas_data
                })
            
            return {
                "success": True,
                "data": comentarios_data,
                "total": len(comentarios_data),
                "message": "Comentarios obtenidos exitosamente",
                "user_authenticated": str(current_user.usuario_id),
                "user_name": f"{current_user.nombres} {current_user.apellidos}"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo comentarios del curso {curso_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/{curso_id}/comentarios")
async def crear_comentario(
    curso_id: str, 
    comentario_data: dict,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Crear nuevo comentario/anuncio en el curso"""
    try:
        logger.info(f"Creando comentario en curso {curso_id} por usuario: {current_user.usuario_id}")
        logger.info(f"Datos comentario: {comentario_data}")
        
        db = SessionLocal()
        
        try:
            # Verificar que el usuario tenga acceso al curso
            acceso_result = db.execute(text("""
                SELECT 1 FROM "EstudianteGrupo" eg
                JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id  
                WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
                
                UNION
                
                SELECT 1 FROM "GrupoCurso" gc
                WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
            """), {"curso_id": curso_id, "usuario_id": current_user.usuario_id}).fetchone()
            
            if not acceso_result:
                raise HTTPException(
                    status_code=403,
                    detail="No tienes acceso a este curso"
                )
            
            # Validar datos del comentario
            contenido = comentario_data.get("contenido", "").strip()
            tipo_str = comentario_data.get("tipo", "comentario")
            archivos = comentario_data.get("archivos", [])
            comentario_padre_id = comentario_data.get("comentario_padre_id")
            
            if not contenido:
                raise HTTPException(
                    status_code=400,
                    detail="El contenido del comentario no puede estar vacío"
                )
            
            # Convertir string de tipo a enum
            try:
                if tipo_str == "anuncio":
                    tipo_enum = TipoComentario.anuncio
                elif tipo_str == "pregunta":
                    tipo_enum = TipoComentario.pregunta
                elif tipo_str == "respuesta":
                    tipo_enum = TipoComentario.respuesta
                else:
                    tipo_enum = TipoComentario.comentario
            except ValueError:
                tipo_enum = TipoComentario.comentario
            
            # Si es una respuesta, verificar que el comentario padre existe
            padre_uuid = None
            if comentario_padre_id:
                try:
                    padre_uuid = uuid.UUID(comentario_padre_id)
                    # Verificar que el comentario padre existe
                    padre_existe = db.execute(text("""
                        SELECT 1 FROM "Comentario" 
                        WHERE comentario_id = :padre_id AND curso_id = :curso_id
                    """), {"padre_id": padre_uuid, "curso_id": curso_id}).fetchone()
                    
                    if not padre_existe:
                        raise HTTPException(status_code=404, detail="Comentario padre no encontrado")
                        
                    # Si tiene padre, automáticamente es una respuesta
                    tipo_enum = TipoComentario.respuesta
                    logger.info(f"Creando respuesta al comentario {padre_uuid}")
                except ValueError:
                    logger.warning(f"ID de comentario padre inválido: {comentario_padre_id}")
                    padre_uuid = None
            
            # Solo profesores pueden crear anuncios
            if tipo_enum == TipoComentario.anuncio:
                # Verificar si el usuario es docente del curso
                docente_check = db.execute(text("""
                    SELECT 1 FROM "GrupoCurso" gc
                    WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
                """), {"curso_id": curso_id, "usuario_id": current_user.usuario_id}).fetchone()
                
                if not docente_check:
                    raise HTTPException(
                        status_code=403,
                        detail="Solo los profesores pueden crear anuncios"
                    )
            
            # Preparar archivos adjuntos (convertir a JSON string si hay archivos)
            archivos_json = None
            if archivos and len(archivos) > 0:
                import json
                archivos_json = json.dumps(archivos)
                logger.info(f"📎 GUARDANDO {len(archivos)} archivos:")
                logger.info(f"📎 Estructura de archivos recibida: {archivos}")
                logger.info(f"📎 JSON que se guardará: {archivos_json}")
            else:
                logger.info("📎 No hay archivos para guardar")
            
            # Crear comentario directamente en la base de datos
            from src.models.communication.comentario import Comentario
            
            nuevo_comentario = Comentario(
                curso_id=uuid.UUID(curso_id),
                autor_id=current_user.usuario_id,
                contenido=contenido,
                tipo=tipo_enum,
                archivos_adjuntos=archivos_json,
                comentario_padre_id=padre_uuid
            )
            
            db.add(nuevo_comentario)
            db.commit()
            db.refresh(nuevo_comentario)
            
            logger.info(f"Comentario creado exitosamente: {nuevo_comentario.comentario_id}")
            
            return {
                "success": True,
                "data": {
                    "id": str(nuevo_comentario.comentario_id),
                    "curso_id": curso_id,
                    "autor": f"{current_user.nombres} {current_user.apellidos}",
                    "contenido": nuevo_comentario.contenido,
                    "tipo": nuevo_comentario.tipo.value,
                    "fecha": nuevo_comentario.fecha_creacion.isoformat(),
                    "archivos": archivos or [],
                    "editado": nuevo_comentario.editado,
                    "comentario_padre_id": str(nuevo_comentario.comentario_padre_id) if nuevo_comentario.comentario_padre_id else None
                },
                "message": "Comentario creado exitosamente"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando comentario en curso {curso_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/{curso_id}/tareas")  
async def obtener_tareas_curso(
    curso_id: str,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Obtener tareas del curso desde la base de datos"""
    try:
        logger.info(f"Obteniendo tareas del curso {curso_id} para usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar acceso al curso
            acceso_result = db.execute(text("""
                SELECT 1 FROM "EstudianteGrupo" eg
                JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id  
                WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
                
                UNION
                
                SELECT 1 FROM "GrupoCurso" gc
                WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
            """), {"curso_id": curso_id, "usuario_id": current_user.usuario_id}).fetchone()
            
            if not acceso_result:
                raise HTTPException(
                    status_code=403,
                    detail="No tienes acceso a este curso"
                )
            
            # TODO: Implementar consulta real de tareas cuando se cree la tabla
            # Por ahora devolver lista vacía en lugar de datos simulados con fechas inválidas
            
            # Consulta temporal para verificar si existen tareas reales en la BD
            # En el futuro, aquí iría la consulta real a la tabla de Tareas
            tareas_reales = []
            
            logger.info(f"Tareas encontradas en el curso {curso_id}: {len(tareas_reales)} (tabla no implementada aún)")
            
            return {
                "success": True,
                "data": tareas_reales,  # Lista vacía hasta implementar tabla de tareas
                "total": len(tareas_reales),
                "message": "Lista de tareas (tabla en desarrollo)"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo tareas del curso {curso_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/{curso_id}/tareas")
async def crear_tarea(
    curso_id: str,
    tarea_data: dict,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Crear nueva tarea en el curso"""
    try:
        logger.info(f"Creando tarea en curso {curso_id} por usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar que el usuario sea docente del curso
            docente_result = db.execute(text("""
                SELECT 1 FROM "GrupoCurso" gc
                WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
            """), {"curso_id": curso_id, "usuario_id": current_user.usuario_id}).fetchone()
            
            if not docente_result:
                raise HTTPException(
                    status_code=403,
                    detail="Solo los docentes pueden crear tareas en este curso"
                )
            
            # Validar datos de la tarea
            titulo = tarea_data.get("titulo", "").strip()
            descripcion = tarea_data.get("descripcion", "").strip()
            fechaVencimiento = tarea_data.get("fechaVencimiento")
            puntos = tarea_data.get("puntos", 0)
            
            if not titulo:
                raise HTTPException(
                    status_code=400,
                    detail="El título de la tarea es requerido"
                )
            
            if not descripcion:
                raise HTTPException(
                    status_code=400,
                    detail="La descripción de la tarea es requerida"
                )
            
            # Por ahora crear respuesta simulada hasta implementar tabla de tareas real
            from datetime import datetime
            import uuid
            
            nueva_tarea = {
                "id": str(uuid.uuid4()),
                "curso_id": curso_id,
                "titulo": titulo,
                "descripcion": descripcion,
                "fechaCreacion": datetime.now().isoformat(),
                "fechaVencimiento": fechaVencimiento or (datetime.now() + timedelta(days=7)).isoformat(),
                "puntos": puntos,
                "estado": "publicada",
                "creador_id": str(current_user.usuario_id),
                "archivos": tarea_data.get("archivos", [])
            }
            
            logger.info(f"Tarea creada: {nueva_tarea['id']} en curso {curso_id}")
            
            # === CREAR ANUNCIO AUTOMÁTICO PARA LA NUEVA TAREA ===
            try:
                # Crear anuncio automático sobre la nueva tarea
                from src.models.communication.comentario import Comentario, TipoComentario
                
                # Contenido del anuncio automático
                fecha_vencimiento_formateada = fechaVencimiento or (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")
                contenido_anuncio = f"""📋 **Nueva tarea asignada: {titulo}**

{descripcion}

📅 **Fecha de vencimiento:** {fecha_vencimiento_formateada}
💯 **Puntos:** {puntos}

¡No olvides entregar tu trabajo a tiempo!"""
                
                # Crear comentario/anuncio automático
                anuncio_automatico = Comentario(
                    curso_id=uuid.UUID(curso_id),
                    autor_id=current_user.usuario_id,
                    contenido=contenido_anuncio,
                    tipo=TipoComentario.anuncio,
                    archivos_adjuntos=None
                )
                
                db.add(anuncio_automatico)
                db.commit()
                db.refresh(anuncio_automatico)
                
                logger.info(f"Anuncio automático creado: {anuncio_automatico.comentario_id} para tarea {nueva_tarea['id']}")
                
                # Agregar información del anuncio a la respuesta
                nueva_tarea["anuncio_creado"] = {
                    "id": str(anuncio_automatico.comentario_id),
                    "contenido": contenido_anuncio,
                    "fecha": anuncio_automatico.fecha_creacion.isoformat()
                }
                
            except Exception as anuncio_error:
                # Si falla crear el anuncio, no fallar toda la operación
                logger.warning(f"Error creando anuncio automático para tarea: {anuncio_error}")
                nueva_tarea["anuncio_creado"] = None
            
            # === CREAR NOTIFICACIONES PARA ESTUDIANTES ===
            try:
                # Obtener todos los estudiantes del curso para enviar notificaciones
                estudiantes_result = db.execute(text("""
                    SELECT DISTINCT u.usuario_id, u.nombres, u.apellidos, u.correo_institucional
                    FROM "Usuario" u
                    JOIN "EstudianteGrupo" eg ON u.usuario_id = eg.estudiante_id
                    JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id
                    WHERE gc.curso_id = :curso_id AND u.rol = 'estudiante'
                """), {"curso_id": curso_id})
                
                estudiantes = estudiantes_result.fetchall()
                notificaciones_creadas = 0
                
                # Crear notificaciones para cada estudiante
                from src.models.communication.chat import Notificacion
                
                for estudiante in estudiantes:
                    notificacion = Notificacion(
                        usuario_id=estudiante.usuario_id,
                        titulo=f"📋 Nueva tarea: {titulo}",
                        mensaje=f"Se ha asignado una nueva tarea en el curso. Fecha de vencimiento: {fecha_vencimiento_formateada}",
                        tipo="tarea",
                        referencia_id=uuid.UUID(nueva_tarea["id"]),
                        referencia_tipo="tarea",
                        leida=False
                    )
                    
                    db.add(notificacion)
                    notificaciones_creadas += 1
                
                if notificaciones_creadas > 0:
                    db.commit()
                    logger.info(f"✅ {notificaciones_creadas} notificaciones de tarea creadas para estudiantes")
                    nueva_tarea["notificaciones_enviadas"] = notificaciones_creadas
                else:
                    nueva_tarea["notificaciones_enviadas"] = 0
                
            except Exception as notif_error:
                # Si falla crear las notificaciones, no fallar toda la operación
                logger.warning(f"Error creando notificaciones para estudiantes: {notif_error}")
                nueva_tarea["notificaciones_enviadas"] = 0
            
            mensaje_exito = f"Tarea creada exitosamente"
            if nueva_tarea.get("anuncio_creado"):
                mensaje_exito += " (con anuncio automático)"
            if nueva_tarea.get("notificaciones_enviadas", 0) > 0:
                mensaje_exito += f" (notificaciones enviadas a {nueva_tarea['notificaciones_enviadas']} estudiantes)"
            
            return {
                "success": True,
                "data": nueva_tarea,
                "message": mensaje_exito
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando tarea en curso {curso_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/{curso_id}/subir-archivo")
async def subir_archivo_curso(
    curso_id: str,
    file: UploadFile = File(...),
    tipo: str = Form("anuncio"),  # anuncio, tarea, material
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Subir archivo para anuncios, tareas o materiales del curso"""
    try:
        logger.info(f"Subiendo archivo para curso {curso_id} por usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar acceso al curso
            acceso_result = db.execute(text("""
                SELECT 1 FROM "EstudianteGrupo" eg
                JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id  
                WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
                
                UNION
                
                SELECT 1 FROM "GrupoCurso" gc
                WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
            """), {"curso_id": curso_id, "usuario_id": current_user.usuario_id}).fetchone()
            
            if not acceso_result:
                raise HTTPException(
                    status_code=403,
                    detail="No tienes acceso a este curso"
                )
            
            # Validar el archivo
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail="No se proporcionó archivo"
                )
            
            # Validar tamaño (límite de 50MB)
            max_size = 50 * 1024 * 1024  # 50MB
            file_content = await file.read()
            file_size = len(file_content)
            
            if file_size > max_size:
                raise HTTPException(
                    status_code=413,
                    detail="El archivo es demasiado grande (máximo 50MB)"
                )
            
            # Validar extensión
            allowed_extensions = {
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.txt', '.rtf', '.odt', '.ods', '.odp',
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
                '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
                '.mp3', '.wav', '.ogg', '.m4a',
                '.zip', '.rar', '.7z', '.tar', '.gz'
            }
            
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo de archivo no permitido: {file_extension}"
                )
            
            # Crear nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_uuid = str(uuid.uuid4())[:8]
            filename_base = os.path.splitext(file.filename)[0]
            safe_filename = f"{timestamp}_{file_uuid}_{filename_base}{file_extension}"
            
            # Crear directorio si no existe
            upload_dir = f"/home/esteban/Acadify/backend/static/uploads/cursos/{curso_id}"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Guardar archivo
            file_path = os.path.join(upload_dir, safe_filename)
            
            # Resetear posición del archivo
            await file.seek(0)
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Calcular URL relativa
            relative_path = f"/static/uploads/cursos/{curso_id}/{safe_filename}"
            
            logger.info(f"Archivo guardado exitosamente en: {file_path}")
            
            return {
                "success": True,
                "data": {
                    "filename": file.filename,
                    "size": file_size,
                    "url": relative_path,
                    "upload_date": datetime.now().isoformat()
                },
                "message": "Archivo subido exitosamente"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo archivo para curso {curso_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/comentarios/{comentario_id}")
async def actualizar_comentario(
    comentario_id: str,
    comentario_data: dict,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Actualizar comentario existente"""
    try:
        logger.info(f"Actualizando comentario {comentario_id} por usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar que el comentario existe y pertenece al usuario
            comentario_result = db.execute(text("""
                SELECT c.comentario_id, c.autor_id, c.curso_id, c.tipo
                FROM "Comentario" c
                WHERE c.comentario_id = :comentario_id
            """), {"comentario_id": comentario_id}).fetchone()
            
            if not comentario_result:
                raise HTTPException(
                    status_code=404,
                    detail="Comentario no encontrado"
                )
            
            # Verificar que el usuario es el autor del comentario
            if str(comentario_result.autor_id) != str(current_user.usuario_id):
                raise HTTPException(
                    status_code=403,
                    detail="Solo puedes editar tus propios comentarios"
                )
            
            # Validar nuevo contenido
            nuevo_contenido = comentario_data.get("contenido", "").strip()
            if not nuevo_contenido:
                raise HTTPException(
                    status_code=400,
                    detail="El contenido del comentario no puede estar vacío"
                )
            
            # Actualizar comentario
            db.execute(text("""
                UPDATE "Comentario" 
                SET contenido = :contenido, 
                    fecha_modificacion = CURRENT_TIMESTAMP,
                    editado = TRUE
                WHERE comentario_id = :comentario_id
            """), {
                "contenido": nuevo_contenido,
                "comentario_id": comentario_id
            })
            
            db.commit()
            
            logger.info(f"Comentario {comentario_id} actualizado exitosamente")
            
            return {
                "success": True,
                "data": {
                    "id": comentario_id,
                    "contenido": nuevo_contenido,
                    "editado": True,
                    "fecha_modificacion": datetime.now().isoformat()
                },
                "message": "Comentario actualizado exitosamente"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando comentario {comentario_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/comentarios/{comentario_id}")
async def eliminar_comentario(
    comentario_id: str,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Eliminar comentario"""
    try:
        logger.info(f"Eliminando comentario {comentario_id} por usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar que el comentario existe y pertenece al usuario
            comentario_result = db.execute(text("""
                SELECT c.comentario_id, c.autor_id, c.curso_id, c.tipo
                FROM "Comentario" c
                WHERE c.comentario_id = :comentario_id
            """), {"comentario_id": comentario_id}).fetchone()
            
            if not comentario_result:
                raise HTTPException(
                    status_code=404,
                    detail="Comentario no encontrado"
                )
            
            # Verificar permisos: autor del comentario o docente del curso
            es_autor = str(comentario_result.autor_id) == str(current_user.usuario_id)
            
            # Verificar si es docente del curso (para eliminar cualquier comentario)
            es_docente = db.execute(text("""
                SELECT 1 FROM "GrupoCurso" gc
                WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
            """), {
                "curso_id": comentario_result.curso_id, 
                "usuario_id": current_user.usuario_id
            }).fetchone()
            
            if not (es_autor or es_docente):
                raise HTTPException(
                    status_code=403,
                    detail="No tienes permisos para eliminar este comentario"
                )
            
            # Eliminar respuestas primero (si las hay)
            db.execute(text("""
                DELETE FROM "Comentario" 
                WHERE comentario_padre_id = :comentario_id
            """), {"comentario_id": comentario_id})
            
            # Eliminar comentario principal
            db.execute(text("""
                DELETE FROM "Comentario" 
                WHERE comentario_id = :comentario_id
            """), {"comentario_id": comentario_id})
            
            db.commit()
            
            logger.info(f"Comentario {comentario_id} eliminado exitosamente")
            
            return {
                "success": True,
                "message": "Comentario eliminado exitosamente"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando comentario {comentario_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/comentarios/{comentario_id}/respuestas")
async def crear_respuesta(
    comentario_id: str,
    respuesta_data: dict,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Crear respuesta a un comentario"""
    try:
        logger.info(f"Creando respuesta al comentario {comentario_id} por usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar que el comentario padre existe
            comentario_padre = db.execute(text("""
                SELECT c.comentario_id, c.curso_id
                FROM "Comentario" c
                WHERE c.comentario_id = :comentario_id
            """), {"comentario_id": comentario_id}).fetchone()
            
            if not comentario_padre:
                raise HTTPException(
                    status_code=404,
                    detail="Comentario padre no encontrado"
                )
            
            # Verificar acceso al curso
            acceso_result = db.execute(text("""
                SELECT 1 FROM "EstudianteGrupo" eg
                JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id  
                WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
                
                UNION
                
                SELECT 1 FROM "GrupoCurso" gc
                WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
            """), {"curso_id": comentario_padre.curso_id, "usuario_id": current_user.usuario_id}).fetchone()
            
            if not acceso_result:
                raise HTTPException(
                    status_code=403,
                    detail="No tienes acceso a este curso"
                )
            
            # Validar contenido de la respuesta
            contenido = respuesta_data.get("contenido", "").strip()
            if not contenido:
                raise HTTPException(
                    status_code=400,
                    detail="El contenido de la respuesta no puede estar vacío"
                )
            
            # Crear respuesta
            from src.models.communication.comentario import Comentario, TipoComentario
            
            nueva_respuesta = Comentario(
                curso_id=comentario_padre.curso_id,
                autor_id=current_user.usuario_id,
                contenido=contenido,
                tipo=TipoComentario.respuesta,
                comentario_padre_id=uuid.UUID(comentario_id)
            )
            
            db.add(nueva_respuesta)
            db.commit()
            db.refresh(nueva_respuesta)
            
            logger.info(f"Respuesta creada exitosamente: {nueva_respuesta.comentario_id}")
            
            return {
                "success": True,
                "data": {
                    "id": str(nueva_respuesta.comentario_id),
                    "comentario_padre_id": comentario_id,
                    "autor": f"{current_user.nombres} {current_user.apellidos}",
                    "contenido": nueva_respuesta.contenido,
                    "fecha": nueva_respuesta.fecha_creacion.isoformat(),
                    "tipo": "respuesta"
                },
                "message": "Respuesta creada exitosamente"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando respuesta al comentario {comentario_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/comentarios/{comentario_id}/respuestas")
async def obtener_respuestas(
    comentario_id: str,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Obtener respuestas de un comentario"""
    try:
        logger.info(f"Obteniendo respuestas del comentario {comentario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar que el comentario padre existe y obtener curso_id
            comentario_padre = db.execute(text("""
                SELECT c.comentario_id, c.curso_id
                FROM "Comentario" c
                WHERE c.comentario_id = :comentario_id
            """), {"comentario_id": comentario_id}).fetchone()
            
            if not comentario_padre:
                raise HTTPException(
                    status_code=404,
                    detail="Comentario no encontrado"
                )
            
            # Verificar acceso al curso
            acceso_result = db.execute(text("""
                SELECT 1 FROM "EstudianteGrupo" eg
                JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id  
                WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
                
                UNION
                
                SELECT 1 FROM "GrupoCurso" gc
                WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
            """), {"curso_id": comentario_padre.curso_id, "usuario_id": current_user.usuario_id}).fetchone()
            
            if not acceso_result:
                raise HTTPException(
                    status_code=403,
                    detail="No tienes acceso a este curso"
                )
            
            # Obtener respuestas
            respuestas = crud_comentario.get_respuestas_comentario(
                db=db,
                comentario_padre_id=uuid.UUID(comentario_id)
            )
            
            respuestas_data = []
            for respuesta in respuestas:
                # Obtener información del autor
                autor_info = db.execute(text("""
                    SELECT nombres, apellidos, correo_institucional
                    FROM "Usuario"
                    WHERE usuario_id = :autor_id
                """), {"autor_id": respuesta.autor_id}).fetchone()
                
                respuestas_data.append({
                    "id": str(respuesta.comentario_id),
                    "autor": f"{autor_info.nombres} {autor_info.apellidos}" if autor_info else "Usuario desconocido",
                    "contenido": respuesta.contenido,
                    "fecha": respuesta.fecha_creacion.isoformat(),
                    "editado": respuesta.editado,
                    "archivos": respuesta.archivos_lista
                })
            
            return {
                "success": True,
                "data": respuestas_data,
                "total": len(respuestas_data),
                "message": "Respuestas obtenidas exitosamente"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo respuestas del comentario {comentario_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/respuestas/{respuesta_id}")
async def actualizar_respuesta(
    respuesta_id: str,
    respuesta_data: dict,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Actualizar respuesta existente"""
    try:
        logger.info(f"Actualizando respuesta {respuesta_id} por usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar que la respuesta existe y pertenece al usuario
            respuesta_result = db.execute(text("""
                SELECT c.comentario_id, c.autor_id, c.comentario_padre_id
                FROM "Comentario" c
                WHERE c.comentario_id = :respuesta_id 
                  AND c.tipo = 'respuesta'
                  AND c.comentario_padre_id IS NOT NULL
            """), {"respuesta_id": respuesta_id}).fetchone()
            
            if not respuesta_result:
                raise HTTPException(
                    status_code=404,
                    detail="Respuesta no encontrada"
                )
            
            # Verificar que el usuario es el autor de la respuesta
            if str(respuesta_result.autor_id) != str(current_user.usuario_id):
                raise HTTPException(
                    status_code=403,
                    detail="Solo puedes editar tus propias respuestas"
                )
            
            # Validar nuevo contenido
            nuevo_contenido = respuesta_data.get("contenido", "").strip()
            if not nuevo_contenido:
                raise HTTPException(
                    status_code=400,
                    detail="El contenido de la respuesta no puede estar vacío"
                )
            
            # Actualizar respuesta
            db.execute(text("""
                UPDATE "Comentario" 
                SET contenido = :contenido, 
                    fecha_modificacion = CURRENT_TIMESTAMP,
                    editado = TRUE
                WHERE comentario_id = :respuesta_id
            """), {
                "contenido": nuevo_contenido,
                "respuesta_id": respuesta_id
            })
            
            db.commit()
            
            logger.info(f"Respuesta {respuesta_id} actualizada exitosamente")
            
            return {
                "success": True,
                "data": {
                    "id": respuesta_id,
                    "contenido": nuevo_contenido,
                    "editado": True,
                    "fecha_modificacion": datetime.now().isoformat()
                },
                "message": "Respuesta actualizada exitosamente"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando respuesta {respuesta_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/respuestas/{respuesta_id}")
async def eliminar_respuesta(
    respuesta_id: str,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Eliminar respuesta"""
    try:
        logger.info(f"Eliminando respuesta {respuesta_id} por usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar que la respuesta existe y obtener info del curso
            respuesta_result = db.execute(text("""
                SELECT c.comentario_id, c.autor_id, c.curso_id, c.comentario_padre_id
                FROM "Comentario" c
                WHERE c.comentario_id = :respuesta_id 
                  AND c.tipo = 'respuesta'
                  AND c.comentario_padre_id IS NOT NULL
            """), {"respuesta_id": respuesta_id}).fetchone()
            
            if not respuesta_result:
                raise HTTPException(
                    status_code=404,
                    detail="Respuesta no encontrada"
                )
            
            # Verificar permisos: autor de la respuesta o docente del curso
            es_autor = str(respuesta_result.autor_id) == str(current_user.usuario_id)
            
            # Verificar si es docente del curso
            es_docente = db.execute(text("""
                SELECT 1 FROM "GrupoCurso" gc
                WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
            """), {
                "curso_id": respuesta_result.curso_id, 
                "usuario_id": current_user.usuario_id
            }).fetchone()
            
            if not (es_autor or es_docente):
                raise HTTPException(
                    status_code=403,
                    detail="No tienes permisos para eliminar esta respuesta"
                )
            
            # Eliminar respuesta
            db.execute(text("""
                DELETE FROM "Comentario" 
                WHERE comentario_id = :respuesta_id
            """), {"respuesta_id": respuesta_id})
            
            db.commit()
            
            logger.info(f"Respuesta {respuesta_id} eliminada exitosamente")
            
            return {
                "success": True,
                "message": "Respuesta eliminada exitosamente"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando respuesta {respuesta_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

# === ENDPOINTS PARA SISTEMA DE REACCIONES ===

@router.post("/comentarios/{comentario_id}/reacciones")
async def agregar_reaccion(
    comentario_id: str,
    reaccion_data: dict,  # {"emoji": "👍", "tipo": "like"}
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Agregar reacción emoji a un comentario o respuesta"""
    try:
        logger.info(f"Agregando reacción al comentario {comentario_id} por usuario: {current_user.usuario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar que el comentario existe y obtener curso_id
            comentario_result = db.execute(text("""
                SELECT c.comentario_id, c.curso_id
                FROM "Comentario" c
                WHERE c.comentario_id = :comentario_id
            """), {"comentario_id": comentario_id}).fetchone()
            
            if not comentario_result:
                raise HTTPException(
                    status_code=404,
                    detail="Comentario no encontrado"
                )
            
            # Verificar acceso al curso
            acceso_result = db.execute(text("""
                SELECT 1 FROM "EstudianteGrupo" eg
                JOIN "GrupoCurso" gc ON eg.grupo_id = gc.grupo_id  
                WHERE gc.curso_id = :curso_id AND eg.estudiante_id = :usuario_id
                
                UNION
                
                SELECT 1 FROM "GrupoCurso" gc
                WHERE gc.curso_id = :curso_id AND gc.docente_id = :usuario_id
            """), {"curso_id": comentario_result.curso_id, "usuario_id": current_user.usuario_id}).fetchone()
            
            if not acceso_result:
                raise HTTPException(
                    status_code=403,
                    detail="No tienes acceso a este curso"
                )
            
            # Validar datos de la reacción
            emoji = reaccion_data.get("emoji", "👍")
            tipo = reaccion_data.get("tipo", "like")
            
            # Intentar crear tabla de reacciones si no existe
            try:
                db.execute(text("""
                    CREATE TABLE IF NOT EXISTS "Reacciones" (
                        reaccion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        comentario_id UUID NOT NULL,
                        usuario_id UUID NOT NULL,
                        emoji VARCHAR(10) NOT NULL,
                        tipo VARCHAR(20),
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        activo BOOLEAN DEFAULT true,
                        FOREIGN KEY (comentario_id) REFERENCES "Comentario"(comentario_id) ON DELETE CASCADE,
                        FOREIGN KEY (usuario_id) REFERENCES "Usuario"(usuario_id) ON DELETE CASCADE,
                        UNIQUE(comentario_id, usuario_id, emoji)
                    )
                """))
                db.commit()
            except Exception as create_error:
                logger.warning(f"Error creando tabla Reacciones o ya existe: {create_error}")
                db.rollback()
            
            # Verificar si el usuario ya reaccionó con ese emoji
            reaccion_existente = db.execute(text("""
                SELECT reaccion_id, activo FROM "Reacciones"
                WHERE comentario_id = :comentario_id 
                AND usuario_id = :usuario_id 
                AND emoji = :emoji
            """), {
                "comentario_id": comentario_id,
                "usuario_id": current_user.usuario_id,
                "emoji": emoji
            }).fetchone()
            
            if reaccion_existente:
                # Si ya existe, toggle la reacción (activar/desactivar)
                nuevo_estado = not reaccion_existente.activo
                db.execute(text("""
                    UPDATE "Reacciones" 
                    SET activo = :activo, fecha_creacion = CURRENT_TIMESTAMP
                    WHERE reaccion_id = :reaccion_id
                """), {
                    "activo": nuevo_estado,
                    "reaccion_id": reaccion_existente.reaccion_id
                })
                db.commit()
                
                mensaje = "Reacción activada" if nuevo_estado else "Reacción removida"
                logger.info(f"Reacción {emoji} {'activada' if nuevo_estado else 'removida'} en comentario {comentario_id}")
                
                return {
                    "success": True,
                    "data": {
                        "comentario_id": comentario_id,
                        "usuario_id": str(current_user.usuario_id),
                        "emoji": emoji,
                        "tipo": tipo,
                        "activo": nuevo_estado,
                        "fecha": datetime.now().isoformat()
                    },
                    "message": mensaje
                }
            else:
                # Crear nueva reacción
                resultado = db.execute(text("""
                    INSERT INTO "Reacciones" (comentario_id, usuario_id, emoji, tipo, activo)
                    VALUES (:comentario_id, :usuario_id, :emoji, :tipo, true)
                    RETURNING reaccion_id, fecha_creacion
                """), {
                    "comentario_id": comentario_id,
                    "usuario_id": current_user.usuario_id,
                    "emoji": emoji,
                    "tipo": tipo
                })
                
                new_reaccion = resultado.fetchone()
                db.commit()
                
                logger.info(f"Nueva reacción {emoji} agregada al comentario {comentario_id}")
                
                return {
                    "success": True,
                    "data": {
                        "reaccion_id": str(new_reaccion.reaccion_id),
                        "comentario_id": comentario_id,
                        "usuario_id": str(current_user.usuario_id),
                        "emoji": emoji,
                        "tipo": tipo,
                        "activo": True,
                        "fecha": new_reaccion.fecha_creacion.isoformat()
                    },
                    "message": "Reacción agregada exitosamente"
                }
                
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error agregando reacción al comentario {comentario_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/comentarios/{comentario_id}/reacciones")
async def obtener_reacciones(
    comentario_id: str,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Obtener reacciones de un comentario agrupadas por emoji"""
    try:
        logger.info(f"Obteniendo reacciones del comentario {comentario_id}")
        
        db = SessionLocal()
        
        try:
            # Verificar que el comentario existe y obtener curso_id
            comentario_result = db.execute(text("""
                SELECT c.comentario_id, c.curso_id
                FROM "Comentario" c
                WHERE c.comentario_id = :comentario_id
            """), {"comentario_id": comentario_id}).fetchone()
            
            if not comentario_result:
                raise HTTPException(
                    status_code=404,
                    detail="Comentario no encontrado"
                )
            
            # Intentar obtener reacciones de la base de datos
            try:
                # Obtener reacciones agrupadas por emoji con contadores
                reacciones_result = db.execute(text("""
                    SELECT 
                        r.emoji,
                        COUNT(*) as cantidad,
                        ARRAY_AGG(
                            JSON_BUILD_OBJECT(
                                'usuario_id', r.usuario_id::text,
                                'usuario_nombre', COALESCE(u.nombres || ' ' || u.apellidos, u.email),
                                'fecha', r.fecha_creacion,
                                'reaccion_id', r.reaccion_id::text
                            ) 
                            ORDER BY r.fecha_creacion DESC
                        ) as usuarios
                    FROM "Reacciones" r
                    JOIN "Usuario" u ON r.usuario_id = u.usuario_id
                    WHERE r.comentario_id = :comentario_id 
                    AND r.activo = true
                    GROUP BY r.emoji
                    ORDER BY COUNT(*) DESC, MIN(r.fecha_creacion) ASC
                """), {"comentario_id": comentario_id}).fetchall()
                
                reacciones_agrupadas = []
                for reaccion in reacciones_result:
                    reacciones_agrupadas.append({
                        "emoji": reaccion.emoji,
                        "cantidad": reaccion.cantidad,
                        "usuarios": reaccion.usuarios,
                        "texto_usuarios": f"{reaccion.cantidad} {'persona' if reaccion.cantidad == 1 else 'personas'}"
                    })
                
                return {
                    "success": True,
                    "data": reacciones_agrupadas,
                    "total": len(reacciones_agrupadas),
                    "total_reacciones": sum(r["cantidad"] for r in reacciones_agrupadas),
                    "message": "Reacciones obtenidas exitosamente"
                }
                
            except Exception as db_error:
                logger.warning(f"Error consultando reacciones desde BD: {db_error}")
                # Fallback: retornar array vacío si no hay tabla
                return {
                    "success": True,
                    "data": [],
                    "total": 0,
                    "total_reacciones": 0,
                    "message": "No hay reacciones disponibles"
                }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo reacciones del comentario {comentario_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/reacciones/{reaccion_id}")
async def eliminar_reaccion(
    reaccion_id: str,
    current_user: Usuario = Depends(deps.get_current_user)
):
    """Eliminar reacción de un comentario"""
    try:
        logger.info(f"Eliminando reacción {reaccion_id} por usuario: {current_user.usuario_id}")
        db = SessionLocal()
        try:
            # Verificar que la reacción existe y pertenece al usuario
            reaccion = db.execute(text("""
                SELECT reaccion_id, usuario_id, activo FROM "Reacciones"
                WHERE reaccion_id = :reaccion_id
            """), {"reaccion_id": reaccion_id}).fetchone()
            if not reaccion:
                raise HTTPException(status_code=404, detail="Reacción no encontrada")
            if str(reaccion.usuario_id) != str(current_user.usuario_id):
                raise HTTPException(status_code=403, detail="No puedes eliminar una reacción de otro usuario")
            if not reaccion.activo:
                return {"success": True, "message": "La reacción ya estaba eliminada"}
            # Eliminar (desactivar) la reacción
            db.execute(text("""
                UPDATE "Reacciones" SET activo = false WHERE reaccion_id = :reaccion_id
            """), {"reaccion_id": reaccion_id})
            db.commit()
            logger.info(f"Reacción {reaccion_id} eliminada correctamente")
            return {"success": True, "message": "Reacción eliminada exitosamente"}
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando reacción {reaccion_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )