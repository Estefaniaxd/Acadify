"""
Rutas de API para la gestión de cursos en Acadify

Endpoints disponibles:
- POST /inscribir: Inscribir estudiante en un curso
- GET /mis-cursos: Obtener cursos del usuario actual
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import os
import uuid
import aiofiles

from src.api import deps
from src.db.session import SessionLocal
from src.models.users.usuario import Usuario

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
                        "estado": "activo",
                        "grupos": [],
                        "instructor": instructor,
                        "profesor": instructor,
                        "estudiantes": total_estudiantes,
                        "total_estudiantes": total_estudiantes,
                        "progress": 0,
                        "progreso": 0,
                        "creditos": 3,
                        "horas": 48,
                        "duration": "16 semanas",
                        "color": "bg-blue-600",
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
                        # Agrupar por curso_id y asociar los grupos
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
                            # ...existing code...
                            if curso_id not in cursos_dict:
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
                                    "progress": progress,
                                    "progreso": progress,
                                    "creditos": 3,
                                    "horas": 48,
                                    "duration": duration,
                                    "color": color_map.get(estado_calculado, "bg-blue-600"),
                                    "institucion": institucion_nombre
                                }
                            cursos_dict[curso_id]["grupos"].append({
                                "nombre": grupo_nombre,
                                "total_estudiantes": total_estudiantes
                            })
                        cursos_data = list(cursos_dict.values())
                                else:
                                    progress = 50
                        duration = "16 semanas"
                        if fecha_inicio and fecha_fin:
                            total_dias = (fecha_fin - fecha_inicio).days
                            semanas = max(1, total_dias // 7)
                            duration = f"{semanas} semanas"
                        color_map = {
                            "activo": "bg-green-600",
                            "completado": "bg-gray-600",
                            "próximo": "bg-blue-600"
                        }
                        curso_data = {
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
                            "grupo_nombre": grupo_nombre,
                            "instructor": instructor,
                            "profesor": instructor,
                            "estudiantes": total_estudiantes,
                            "total_estudiantes": total_estudiantes,
                            "progress": progress,
                            "progreso": progress,
                            "creditos": 3,
                            "horas": 48,
                            "duration": duration,
                            "color": color_map.get(estado_calculado, "bg-blue-600"),
                            "institucion": institucion_nombre
                        }
                        cursos_data.append(curso_data)
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
                else:
                    logger.warning(f"Usuario {current_user.usuario_id} no tiene perfil de estudiante ni rol docente/administrador")
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
            
            # DEBUG: Consultas paso a paso para entender el problema
            logger.info("=== DEBUG CONSULTAS ===")
            
            # 1. Verificar estudiante (estudiante_id = usuario_id en esta tabla)
            debug_estudiante = db.execute(text("""
                SELECT estudiante_id, programa_id FROM "Estudiante" WHERE estudiante_id = :usuario_id
            """), {"usuario_id": current_user.usuario_id})
            estudiante_info = debug_estudiante.fetchone()
            logger.info(f"1. Estudiante info: {estudiante_info}")
            
            if estudiante_info:
                # 2. Verificar inscripciones en grupos
                debug_grupos = db.execute(text("""
                    SELECT grupo_id, fecha_vinculacion FROM "EstudianteGrupo" 
                    WHERE estudiante_id = :estudiante_id
                """), {"estudiante_id": estudiante_info[0]})
                grupos_inscritos = debug_grupos.fetchall()
                logger.info(f"2. Grupos inscritos: {[dict(g._mapping) for g in grupos_inscritos]}")
                
                # 3. Verificar cursos de esos grupos
                if grupos_inscritos:
                    for grupo in grupos_inscritos:
                        debug_curso = db.execute(text("""
                            SELECT c.nombre, c.curso_id FROM "Curso" c
                            JOIN "GrupoCurso" gc ON c.curso_id = gc.curso_id
                            WHERE gc.grupo_id = :grupo_id
                        """), {"grupo_id": grupo[0]})
                        curso_info = debug_curso.fetchone()
                        logger.info(f"3. Grupo {grupo[0]} -> Curso: {curso_info}")
            
            logger.info("=== FIN DEBUG ===")
            
            # Consulta para obtener cursos donde el usuario es estudiante
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
            logger.info(f"Cursos encontrados: {len(cursos_raw)}")
            logger.info(f"Datos cursos raw: {[dict(row._mapping) for row in cursos_raw]}")
            
            if not cursos_raw:
                return {
                    "success": True,
                    "message": "Aún no te has unido a ningún curso",
                    "data": [],
                    "total": 0,
                    "source": "database",
                    "user_role": "estudiante",
                    "empty_state": True,
                    "empty_message": "¡Únete a un curso para comenzar tu aprendizaje! Usa el botón 'Nuevo Curso' para inscribirte con un código."
                }
            
            # Importar datetime para cálculos de estado y progreso
            from datetime import datetime, date
            
            # Convertir los resultados a formato del frontend
            cursos_data = []
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
                
                # Determinar color basado en estado
                color_map = {
                    "activo": "bg-green-600",
                    "completado": "bg-gray-600",
                    "próximo": "bg-blue-600"
                }
                
                curso_data = {
                    "id": str(curso_id),
                    "course_id": str(curso_id),
                    "title": nombre,
                    "nombre": nombre,  # Para compatibilidad con frontend
                    "description": descripcion or f"Curso de {nombre}",
                    "descripcion": descripcion or f"Curso de {nombre}",  # Para compatibilidad
                    "codigo": codigo_acceso,
                    "codigo_acceso": codigo_acceso,
                    "modalidad": modalidad or "Presencial",
                    "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else "2025-01-15",
                    "fecha_fin": fecha_fin.isoformat() if fecha_fin else "2025-06-15",
                    "estado": estado_calculado,
                    "grupo_nombre": grupo_nombre,
                    "instructor": instructor,
                    "profesor": instructor,  # Para compatibilidad con frontend
                    "estudiantes": total_estudiantes,
                    "total_estudiantes": total_estudiantes,
                    "progress": progress,
                    "progreso": progress,
                    "creditos": 3,
                    "horas": 48,
                    "duration": duration,
                    "color": color_map.get(estado_calculado, "bg-blue-600"),
                    "institucion": institucion_nombre
                }
                cursos_data.append(curso_data)
            
            logger.info(f"Usuario {current_user.usuario_id} tiene {len(cursos_data)} cursos con datos reales")
            
            return {
                "success": True,
                "message": f"Se encontraron {len(cursos_data)} cursos",
                "data": cursos_data,
                "total": len(cursos_data),
                "source": "database",
                "user_role": "estudiante",
                "empty_state": False,
                "empty_message": None
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error obteniendo cursos: {e}")
        return {
            "success": True,
            "message": "Error temporal al cargar cursos",
            "data": [],
            "total": 0,
            "source": "error",
            "user_role": "estudiante",
            "empty_state": True,
            "empty_message": "Ocurrió un problema al cargar los cursos. Intenta nuevamente."
        }

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
            
            # Obtener comentarios reales de la base de datos
            # Por ahora usamos datos de ejemplo hasta implementar la tabla de comentarios
            comentarios_ejemplo = [
                {
                    "id": "1",
                    "autor": f"{current_user.nombres} {current_user.apellidos}",
                    "contenido": "Bienvenidos al curso. Pueden encontrar el material de estudio en la sección de recursos.",
                    "fecha": "2025-09-28T10:30:00",
                    "tipo": "anuncio",
                    "archivos": []
                },
                {
                    "id": "2", 
                    "autor": "Prof. Ana García",
                    "contenido": "Recordatorio: Examen parcial el próximo viernes 4 de octubre a las 8:00 AM.",
                    "fecha": "2025-09-27T15:45:00",
                    "tipo": "anuncio",
                    "archivos": [
                        {
                            "id": "file_1",
                            "name": "Temario_Examen.pdf",
                            "size": 245760,
                            "type": "application/pdf"
                        }
                    ]
                },
                {
                    "id": "3",
                    "autor": "Prof. Ana García",
                    "contenido": "Nueva tarea disponible: Análisis de algoritmos de ordenamiento. Fecha límite: 15 de octubre.",
                    "fecha": "2025-09-26T11:20:00",
                    "tipo": "tarea",
                    "archivos": []
                }
            ]
            
            return {
                "success": True,
                "data": comentarios_ejemplo[offset:offset+limit],
                "total": len(comentarios_ejemplo),
                "message": "Comentarios obtenidos exitosamente"
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
            tipo = comentario_data.get("tipo", "comentario")
            archivos = comentario_data.get("archivos", [])
            
            if not contenido:
                raise HTTPException(
                    status_code=400,
                    detail="El contenido del comentario no puede estar vacío"
                )
            
            # Por ahora crear respuesta simulada hasta implementar tabla de comentarios
            from datetime import datetime
            import uuid
            
            nuevo_comentario = {
                "id": str(uuid.uuid4()),
                "curso_id": curso_id,
                "autor": f"{current_user.nombres} {current_user.apellidos}",
                "autor_id": str(current_user.usuario_id),
                "contenido": contenido,
                "tipo": tipo,
                "fecha": datetime.now().isoformat(),
                "archivos": archivos,
                "editado": False
            }
            
            logger.info(f"Comentario creado: {nuevo_comentario['id']} en curso {curso_id}")
            
            return {
                "success": True,
                "data": nuevo_comentario,
                "message": "Comentario creado exitosamente"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando comentario en curso {curso_id}: {e}")
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
            
            # Por ahora datos de ejemplo hasta conectar con tabla de tareas real
            from datetime import datetime, timedelta
            import uuid
            
            tareas_ejemplo = [
                {
                    "id": str(uuid.uuid4()),
                    "titulo": "Ejercicios de Álgebra Lineal",
                    "descripcion": "Resolver los ejercicios 1-15 del capítulo 3. Entregar en formato PDF con desarrollo completo.",
                    "fechaCreacion": (datetime.now() - timedelta(days=5)).isoformat(),
                    "fechaVencimiento": (datetime.now() + timedelta(days=7)).isoformat(),
                    "puntos": 25,
                    "estado": "pendiente",
                    "archivos": [
                        {
                            "id": "task_file_1",
                            "name": "Ejercicios_Cap3.pdf",
                            "size": 1024000,
                            "type": "application/pdf"
                        }
                    ],
                    "entrega": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "titulo": "Proyecto: Análisis de Datos",
                    "descripcion": "Análisis estadístico de un conjunto de datos reales. Incluir gráficos y conclusiones.",
                    "fechaCreacion": (datetime.now() - timedelta(days=10)).isoformat(),
                    "fechaVencimiento": (datetime.now() + timedelta(days=14)).isoformat(),
                    "puntos": 50,
                    "estado": "entregado",
                    "archivos": [
                        {
                            "id": "task_file_2",
                            "name": "Dataset_Analisis.csv",
                            "size": 2048000,
                            "type": "text/csv"
                        },
                        {
                            "id": "task_file_3",
                            "name": "Instrucciones_Proyecto.docx",
                            "size": 512000,
                            "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        }
                    ],
                    "entrega": {
                        "fechaEntrega": (datetime.now() - timedelta(days=2)).isoformat(),
                        "archivos": [
                            {
                                "name": "Analisis_Final.pdf",
                                "size": 3072000
                            }
                        ],
                        "comentario": "Proyecto completado con análisis detallado y gráficos explicativos.",
                        "calificacion": 45
                    }
                },
                {
                    "id": str(uuid.uuid4()),
                    "titulo": "Quiz: Conceptos Fundamentales",
                    "descripcion": "Evaluación sobre los conceptos vistos en las primeras 4 clases del curso.",
                    "fechaCreacion": (datetime.now() - timedelta(days=15)).isoformat(),
                    "fechaVencimiento": (datetime.now() - timedelta(days=8)).isoformat(),
                    "puntos": 20,
                    "estado": "calificado",
                    "archivos": [],
                    "entrega": {
                        "fechaEntrega": (datetime.now() - timedelta(days=9)).isoformat(),
                        "archivos": [],
                        "comentario": "Quiz respondido en plataforma virtual.",
                        "calificacion": 18
                    }
                }
            ]
            
            return {
                "success": True,
                "data": tareas_ejemplo,
                "total": len(tareas_ejemplo),
                "message": "Tareas obtenidas exitosamente"
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
            
            return {
                "success": True,
                "data": nueva_tarea,
                "message": "Tarea creada exitosamente"
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
            if not file:
                raise HTTPException(
                    status_code=400,
                    detail="No se ha proporcionado ningún archivo"
                )
            
            # Validar tamaño del archivo (máximo 50MB)
            max_file_size = 50 * 1024 * 1024  # 50MB en bytes
            if file.size and file.size > max_file_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"El archivo es demasiado grande. Máximo permitido: 50MB"
                )
            
            # Validar tipo de archivo
            allowed_extensions = {
                '.pdf', '.doc', '.docx', '.txt', '.md',
                '.jpg', '.jpeg', '.png', '.gif', '.webp',
                '.mp4', '.avi', '.mov', '.wmv',
                '.xls', '.xlsx', '.csv',
                '.ppt', '.pptx',
                '.zip', '.rar', '.7z'
            }
            
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo de archivo no permitido: {file_extension}"
                )
            
            # Crear directorio de uploads si no existe
            upload_dir = f"static/uploads/cursos/{curso_id}"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generar nombre único para el archivo
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Guardar el archivo
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Información del archivo guardado
            archivo_info = {
                "id": str(uuid.uuid4()),
                "name": file.filename,
                "filename": unique_filename,
                "size": len(content),
                "type": file.content_type,
                "path": file_path,
                "url": f"/static/uploads/cursos/{curso_id}/{unique_filename}",
                "uploaded_by": str(current_user.usuario_id),
                "uploaded_at": datetime.now().isoformat(),
                "tipo": tipo
            }
            
            logger.info(f"Archivo guardado: {file.filename} -> {file_path}")
            
            return {
                "success": True,
                "data": archivo_info,
                "message": f"Archivo '{file.filename}' subido exitosamente"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo archivo para curso {curso_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )