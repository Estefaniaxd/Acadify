# backend/app/api/endpoints/courses.py
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.crud import course as crud_course
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse, CourseWithDetails,
    CourseListResponse, CourseCoordinatorAssignment, CourseStatistics
)
from app.models.user import User, UserRole
from app.core.security import get_current_active_user

router = APIRouter()

def _check_coordinator_permission(user: User, institution_id: UUID):
    if user.role != UserRole.COORDINATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo coordinadores pueden realizar esta acción")
    if not user.coordinator or user.coordinator.institution_id != institution_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos sobre esta institución")

# -------------------- CREATE --------------------
@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: CourseCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if current_user.role != UserRole.COORDINATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los coordinadores pueden crear cursos")
    
    if not current_user.coordinator:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Usuario no tiene perfil de coordinador")

    existing_course = crud_course.course.get_by_name_in_institution(
        db, name=course_in.name, institution_id=current_user.coordinator.institution_id
    )
    if existing_course:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ya existe un curso con este nombre en la institución")
    
    course = crud_course.course.create_with_coordinator(
        db=db, obj_in=course_in, coordinator_id=current_user.coordinator.id
    )
    return course

# -------------------- READ LIST --------------------
@router.get("/", response_model=CourseListResponse)
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    institution_id: Optional[UUID] = Query(None),
    active_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if current_user.role == UserRole.ADMINISTRATOR:
        if institution_id:
            courses = crud_course.course.get_by_institution(db, institution_id, skip=skip, limit=limit)
        elif active_only:
            courses = crud_course.course.get_active_courses(db, skip=skip, limit=limit)
        else:
            courses = crud_course.course.get_multi(db, skip=skip, limit=limit)
    elif current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Usuario no tiene perfil de coordinador")
        institution_id = current_user.coordinator.institution_id
        courses = (crud_course.course.get_active_courses(db, institution_id, skip=skip, limit=limit)
                   if active_only else crud_course.course.get_by_institution(db, institution_id, skip=skip, limit=limit))
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para ver cursos")
    
    return CourseListResponse(courses=courses, total=len(courses), skip=skip, limit=limit)

# -------------------- SEARCH --------------------
@router.get("/search", response_model=CourseListResponse)
def search_courses(
    *,
    db: Session = Depends(deps.get_db),
    query: str = Query(..., min_length=2),
    institution_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Usuario no tiene perfil de coordinador")
        institution_id = current_user.coordinator.institution_id
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para buscar cursos")
    
    courses = crud_course.course.search_courses(db, query=query, institution_id=institution_id, skip=skip, limit=limit)
    return CourseListResponse(courses=courses, total=len(courses), skip=skip, limit=limit)

# -------------------- READ SINGLE --------------------
@router.get("/{course_id}", response_model=CourseWithDetails)
def read_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    course = crud_course.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")
    
    if current_user.role == UserRole.COORDINATOR:
        _check_coordinator_permission(current_user, course.institution_id)
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para ver cursos")
    
    stats = crud_course.course.get_course_statistics(db, course_id=course_id)
    return CourseWithDetails(
        **course.__dict__,
        coordinator_name=stats.get("coordinator_name"),
        coordinator_email=course.coordinator.user.institutional_email if course.coordinator else None,
        institution_name=stats["institution_name"],
        program_name=stats["program_name"],
        groups_count=stats["groups_count"],
        students_count=stats["students_count"],
        materials_count=stats["materials_count"],
        classes_count=0
    )

# -------------------- UPDATE --------------------
@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    course_in: CourseUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    course = crud_course.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")
    
    if current_user.role == UserRole.COORDINATOR:
        _check_coordinator_permission(current_user, course.institution_id)
    elif current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para actualizar cursos")
    
    if course_in.name:
        existing_course = crud_course.course.get_by_name_in_institution(db, course_in.name, course.institution_id)
        if existing_course and existing_course.id != course_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Ya existe otro curso con este nombre en la institución")
    
    return crud_course.course.update(db, db_obj=course, obj_in=course_in)

# -------------------- DELETE --------------------
@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> None:
    course = crud_course.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")
    
    if current_user.role == UserRole.COORDINATOR:
        _check_coordinator_permission(current_user, course.institution_id)
    elif current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para eliminar cursos")
    
    crud_course.course.remove(db, id=course_id)

# -------------------- ASSIGN COORDINATOR --------------------
@router.post("/{course_id}/assign-coordinator", response_model=CourseResponse)
def assign_coordinator_to_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    assignment: CourseCoordinatorAssignment,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los administradores pueden asignar coordinadores")
    
    return crud_course.course.assign_to_coordinator(db, course_id=course_id, coordinator_id=assignment.coordinator_id)

# -------------------- STATISTICS --------------------
@router.get("/{course_id}/statistics", response_model=CourseStatistics)
def get_course_statistics(
    *,
    db: Session = Depends(deps.get_db),
    course_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    course = crud_course.course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")
    
    if current_user.role == UserRole.COORDINATOR:
        _check_coordinator_permission(current_user, course.institution_id)
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para ver estadísticas de cursos")
    
    stats = crud_course.course.get_course_statistics(db, course_id=course_id)
    return CourseStatistics(
        course_id=course_id,
        groups_count=stats["groups_count"],
        students_count=stats["students_count"],
        materials_count=stats["materials_count"],
        classes_count=0,
        assignments_count=0,
        coordinator_name=stats.get("coordinator_name"),
        institution_name=stats["institution_name"],
        program_name=stats["program_name"]
    )

# -------------------- MY COURSES --------------------
@router.get("/my-courses", response_model=CourseListResponse)
def get_my_courses(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if current_user.role != UserRole.COORDINATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los coordinadores pueden acceder a sus cursos")
    
    if not current_user.coordinator:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Usuario no tiene perfil de coordinador")
    
    courses = crud_course.course.get_by_coordinator(db, coordinator_id=current_user.coordinator.id, skip=skip, limit=limit)
    return CourseListResponse(courses=courses, total=len(courses), skip=skip, limit=limit)

# -------------------- COURSES BY PROGRAM --------------------
@router.get("/program/{program_id}", response_model=CourseListResponse)
def get_courses_by_program(
    *,
    db: Session = Depends(deps.get_db),
    program_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para ver cursos por programa")
    
    courses = crud_course.course.get_by_program(db, program_id, skip=skip, limit=limit)
    
    if current_user.role == UserRole.COORDINATOR and courses:
        _check_coordinator_permission(current_user, courses[0].institution_id)
    
    return CourseListResponse(courses=courses, total=len(courses), skip=skip, limit=limit)
