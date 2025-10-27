#!/usr/bin/env python3

import re

def fix_curso_file():
    """
    Arregla la función get_mis_cursos en el archivo curso.py
    """
    file_path = "/home/esteban/Acadify/backend/src/api/routes/academic/curso.py"
    
    # Leer el archivo completo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar el inicio y final de la función problemática
    start_pattern = r'@router\.get\("/mis-cursos", response_model=CourseResponse\)'
    next_function_pattern = r'@router\.get\("/disponibles"\)'
    
    start_match = re.search(start_pattern, content)
    next_match = re.search(next_function_pattern, content)
    
    if not start_match or not next_match:
        print("No se pudieron encontrar los patrones de búsqueda")
        return False
    
    # Extraer las partes del archivo
    before_function = content[:start_match.start()]
    after_function = content[next_match.start():]
    
    # La función limpia
    clean_function = '''@router.get("/mis-cursos", response_model=CourseResponse)
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
        
        except Exception as e:
            logger.error(f"Error en consulta de cursos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al obtener cursos: {str(e)}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error general en get_mis_cursos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


'''
    
    # Reconstruir el archivo
    new_content = before_function + clean_function + after_function
    
    # Escribir el archivo arreglado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Archivo arreglado exitosamente")
    return True

if __name__ == "__main__":
    fix_curso_file()