from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.crud import group as crud_group
from app.schemas.group import (
    GroupCreate, GroupUpdate, GroupResponse, GroupWithDetails, GroupListResponse
)
from app.models.user import User, UserRole
from app.core.security import get_current_active_user

router = APIRouter()

# ------------------- Helper -------------------
def check_permissions(user: User, group, required_roles: list):
    if user.role not in required_roles:
        raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")
    if user.role == UserRole.COORDINATOR:
        if not user.coordinator or user.coordinator.institution_id != group.program.institution_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")

# ------------------- GRUPOS -------------------

@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    *,
    db: Session = Depends(deps.get_db),
    group_in: GroupCreate,
    program_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.COORDINATOR or not current_user.coordinator:
        raise HTTPException(status_code=403, detail="Solo coordinadores pueden crear grupos")
    return crud_group.group.create_with_program(db=db, obj_in=group_in, program_id=program_id)

@router.get("/", response_model=GroupListResponse)
def read_groups(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    program_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    from app.models.program import Program
    groups = []

    if current_user.role == UserRole.ADMINISTRATOR:
        groups = crud_group.group.get_by_program(db, program_id, skip, limit) if program_id else crud_group.group.get_multi(db, skip, limit)
    elif current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator:
            raise HTTPException(status_code=400, detail="Usuario no tiene perfil de coordinador")
        programs = db.query(Program).filter(Program.institution_id == current_user.coordinator.institution_id).all()
        for program in programs:
            groups.extend(crud_group.group.get_by_program(db, program.id, 0, 1000))
        groups = groups[skip:skip+limit]
    else:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver grupos")

    return GroupListResponse(groups=groups, total=len(groups), skip=skip, limit=limit)

@router.get("/search", response_model=GroupListResponse)
def search_groups(
    *,
    db: Session = Depends(deps.get_db),
    query: str = Query(..., min_length=2),
    program_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    groups = crud_group.group.search_groups(db, query, program_id, skip, limit)
    if current_user.role == UserRole.COORDINATOR:
        groups = [g for g in groups if g.program.institution_id == current_user.coordinator.institution_id]
    elif current_user.role not in [UserRole.ADMINISTRATOR]:
        raise HTTPException(status_code=403, detail="No tienes permisos para buscar grupos")
    return GroupListResponse(groups=groups, total=len(groups), skip=skip, limit=limit)

@router.get("/{group_id}", response_model=GroupWithDetails)
def read_group(
    *,
    db: Session = Depends(deps.get_db),
    group_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    group = crud_group.group.get(db, id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    check_permissions(current_user, group, [UserRole.ADMINISTRATOR, UserRole.COORDINATOR, UserRole.TEACHER])
    stats = crud_group.group.get_group_statistics(db, group_id)
    return GroupWithDetails(
        **group.__dict__,
        program_name=stats["program_name"],
        program_level=group.program.level.value,
        institution_name=stats["institution_name"],
        tutor_teacher_name=stats.get("tutor_teacher_name"),
        tutor_teacher_email=group.tutor_teacher.user.institutional_email if group.tutor_teacher else None,
        active_students_count=stats["active_students_count"],
        assigned_courses_count=stats["assigned_courses_count"]
    )

@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    *,
    db: Session = Depends(deps.get_db),
    group_id: UUID,
    group_in: GroupUpdate,
    current_user: User = Depends(get_current_active_user)
):
    group = crud_group.group.get(db, id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    check_permissions(current_user, group, [UserRole.ADMINISTRATOR, UserRole.COORDINATOR])
    if group_in.name:
        existing = crud_group.group.get_by_name_in_program(db, group_in.name, group.program_id)
        if existing and existing.id != group_id:
            raise HTTPException(status_code=400, detail="Ya existe otro grupo con este nombre en el programa")
    return crud_group.group.update(db, db_obj=group, obj_in=group_in)

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    *,
    db: Session = Depends(deps.get_db),
    group_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    group = crud_group.group.get(db, id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    check_permissions(current_user, group, [UserRole.ADMINISTRATOR, UserRole.COORDINATOR])
    crud_group.group.remove(db, group_id)
