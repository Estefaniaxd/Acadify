# backend/app/api/endpoints/programs.py
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.crud import program as crud_program
from app.schemas.program import (
    ProgramCreate,
    ProgramUpdate,
    ProgramResponse,
    ProgramWithDetails,
    ProgramListResponse,
    ProgramSearchParams,
    ProgramStatistics,
    PopularProgramsResponse,
    ProgramValidation,
    ProgramStudents,
    ProgramGroups
)
from app.models.user import User, UserRole
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    *,
    db: Session = Depends(deps.get_db),
    program_in: ProgramCreate,
    institution_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Crea un nuevo programa académico.
    Solo coordinadores pueden crear programas en su institución.
    """
    # Verificar permisos de coordinador
    if current_user.role != UserRole.COORDINATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los coordinadores pueden crear programas"
        )
    
    if not current_user.coordinator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no tiene perfil de coordinador"
        )
    
    # Verificar que el coordinador pertenece a la institución
    if current_user.coordinator.institution_id != institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes crear programas en tu institución"
        )
    
    try:
        program = crud_program.program.create_with_institution(
            db=db, obj_in=program_in, institution_id=institution_id
        )
        return program
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=ProgramListResponse)
def read_programs(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    institution_id: Optional[UUID] = Query(None),
    level: Optional[str] = Query(None),
    program_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtiene la lista de programas.
    Los coordinadores ven solo los programas de su institución.
    """
    if current_user.role == UserRole.ADMINISTRATOR:
        if institution_id:
            programs = crud_program.program.get_by_institution(
                db, institution_id=institution_id, skip=skip, limit=limit
            )
        elif level:
            programs = crud_program.program.get_by_level(
                db, level=level, skip=skip, limit=limit
            )
        elif program_type:
            programs = crud_program.program.get_by_type(
                db, program_type=program_type, skip=skip, limit=limit
            )
        else:
            programs = crud_program.program.get_multi(db, skip=skip, limit=limit)
        total = len(programs)
        
    elif current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no tiene perfil de coordinador"
            )
        
        # Los coordinadores solo ven programas de su institución
        programs = crud_program.program.get_by_institution(
            db, institution_id=current_user.coordinator.institution_id, skip=skip, limit=limit
        )
        total = len(programs)
        
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver programas"
        )
    
    return ProgramListResponse(
        programs=programs,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/search", response_model=ProgramListResponse)
def search_programs(
    *,
    db: Session = Depends(deps.get_db),
    query: str = Query(..., min_length=2),
    institution_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Busca programas por nombre o descripción.
    """
    # Verificar permisos
    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no tiene perfil de coordinador"
            )
        # Los coordinadores solo pueden buscar en su institución
        institution_id = current_user.coordinator.institution_id
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para buscar programas"
        )
    
    programs = crud_program.program.search_programs(
        db, query=query, institution_id=institution_id, skip=skip, limit=limit
    )
    
    return ProgramListResponse(
        programs=programs,
        total=len(programs),
        skip=skip,
        limit=limit
    )

@router.get("/popular", response_model=PopularProgramsResponse)
def get_popular_programs(
    *,
    db: Session = Depends(deps.get_db),
    institution_id: Optional[UUID] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtiene los programas más populares por número de estudiantes.
    """
    # Verificar permisos
    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no tiene perfil de coordinador"
            )
        institution_id = current_user.coordinator.institution_id
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estadísticas de programas"
        )
    
    popular_programs_data = crud_program.program.get_popular_programs(
        db, institution_id=institution_id, limit=limit
    )
    
    popular_programs = [
        {
            "program": data["program"],
            "student_count": data["student_count"]
        }
        for data in popular_programs_data
    ]
    
    return PopularProgramsResponse(
        programs=popular_programs,
        institution_id=institution_id
    )

@router.get("/{program_id}", response_model=ProgramWithDetails)
def read_program(
    *,
    db: Session = Depends(deps.get_db),
    program_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtiene un programa por ID con detalles completos.
    """
    program = crud_program.program.get(db, id=program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator or current_user.coordinator.institution_id != program.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver este programa"
            )
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver programas"
        )
    
    # Obtener estadísticas del programa
    try:
        stats = crud_program.program.get_program_statistics(db, program_id=program_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return ProgramWithDetails(
        **program.__dict__,
        institution_name=stats["institution_name"],
        institution_type=program.institution.institution_type.value,
        students_count=stats["students_count"],
        groups_count=stats["groups_count"],
        courses_count=stats["courses_count"]
    )

@router.put("/{program_id}", response_model=ProgramResponse)
def update_program(
    *,
    db: Session = Depends(deps.get_db),
    program_id: UUID,
    program_in: ProgramUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Actualiza un programa existente.
    Solo coordinadores pueden actualizar programas de su institución.
    """
    program = crud_program.program.get(db, id=program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator or current_user.coordinator.institution_id != program.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para actualizar este programa"
            )
    elif current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar programas"
        )
    
    # Verificar conflicto de nombres si se actualiza el nombre
    if program_in.name:
        existing_program = crud_program.program.get_by_name_in_institution(
            db, name=program_in.name, institution_id=program.institution_id
        )
        if existing_program and existing_program.id != program_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro programa con este nombre en la institución"
            )
    
    program = crud_program.program.update(db, db_obj=program, obj_in=program_in)
    return program

@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    *,
    db: Session = Depends(deps.get_db),
    program_id: UUID,
    current_user: User = Depends(deps.get_current_active_user)
) -> None:
    """
    Elimina un programa.
    Solo coordinadores pueden eliminar programas de su institución.
    """
    # Obtener programa
    program = crud_program.program.get(db, id=program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado"
        )

    # Verificar permisos
    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator or current_user.coordinator.institution_id != program.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar este programa"
            )
    elif current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar programas"
        )

    # Eliminar programa
    crud_program.program.remove(db, id=program_id)

    # No se retorna nada, porque 204 No Content no permite response body
    return

@router.get("/{program_id}/statistics", response_model=ProgramStatistics)
def get_program_statistics(
    *,
    db: Session = Depends(deps.get_db),
    program_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtiene estadísticas detalladas de un programa.
    """
    program = crud_program.program.get(db, id=program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator or current_user.coordinator.institution_id != program.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver las estadísticas de este programa"
            )
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estadísticas de programas"
        )
    
    try:
        stats = crud_program.program.get_program_statistics(db, program_id=program_id)
        return ProgramStatistics(
            program_id=program_id,
            program_name=program.name,
            students_count=stats["students_count"],
            groups_count=stats["groups_count"],
            courses_count=stats["courses_count"],
            institution_name=stats["institution_name"],
            level=stats["level"],
            program_type=stats["program_type"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{program_id}/validate", response_model=ProgramValidation)
def validate_program(
    *,
    db: Session = Depends(deps.get_db),
    program_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Valida las restricciones y requisitos de un programa.
    """
    program = crud_program.program.get(db, id=program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator or current_user.coordinator.institution_id != program.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para validar este programa"
            )
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para validar programas"
        )
    
    validation_result = crud_program.program.validate_program_constraints(db, program=program)
    return ProgramValidation(**validation_result)

@router.get("/{program_id}/students", response_model=ProgramStudents)
def get_program_students(
    *,
    db: Session = Depends(deps.get_db),
    program_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtiene los estudiantes de un programa.
    """
    program = crud_program.program.get(db, id=program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator or current_user.coordinator.institution_id != program.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver los estudiantes de este programa"
            )
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estudiantes de programas"
        )
    
    # Formatear datos de estudiantes
    students_data = []
    for student in program.students:
        students_data.append({
            "student_id": student.id,
            "first_names": student.user.first_names,
            "last_names": student.user.last_names,
            "institutional_email": student.user.institutional_email,
            "document_number": student.user.document_number,
            "enrollment_date": student.enrollment_date,
            "educational_stage": student.educational_stage.value,
            "cumulative_average": student.cumulative_average
        })
    
    return ProgramStudents(
        program_id=program_id,
        program_name=program.name,
        students=students_data,
        total_students=len(students_data)
    )

@router.get("/{program_id}/groups", response_model=ProgramGroups)
def get_program_groups(
    *,
    db: Session = Depends(deps.get_db),
    program_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtiene los grupos de un programa.
    """
    program = crud_program.program.get(db, id=program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator or current_user.coordinator.institution_id != program.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver los grupos de este programa"
            )
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver grupos de programas"
        )
    
    # Formatear datos de grupos
    groups_data = []
    for group in program.groups:
        # Contar estudiantes activos en el grupo
        from app.models.group import StudentGroup, StudentGroupStatus
        active_students = db.query(StudentGroup).filter(
            and_(
                StudentGroup.group_id == group.id,
                StudentGroup.status == StudentGroupStatus.ACTIVE
            )
        ).count()
        
        groups_data.append({
            "group_id": group.id,
            "group_name": group.name,
            "shift": group.shift.value,
            "tutor_teacher_name": f"{group.tutor_teacher.user.first_names} {group.tutor_teacher.user.last_names}" if group.tutor_teacher else None,
            "active_students_count": active_students
        })
    
    return ProgramGroups(
        program_id=program_id,
        program_name=program.name,
        groups=groups_data,
        total_groups=len(groups_data)
    )