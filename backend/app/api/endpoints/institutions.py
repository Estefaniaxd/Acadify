from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import deps
from app.crud import institution as crud_institution
from app.schemas.institution import (
    InstitutionCreate,
    InstitutionUpdate,
    InstitutionResponse,
    InstitutionWithStats,
    InstitutionListResponse,
    InstitutionTransferOwnership,
    CoordinatorAssignment,
    InstitutionCoordinators
)
from app.models.user import User, UserRole
from app.core.security import get_current_active_user
from app.utils.logger import log_user_action, log_security_event

router = APIRouter()

# -------------------------------
# Crear institución
# -------------------------------
@router.post("/", response_model=InstitutionResponse, status_code=status.HTTP_201_CREATED)
def create_institution(
    *,
    db: Session = Depends(deps.get_db),
    institution_in: InstitutionCreate,
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los administradores pueden crear instituciones")

    if crud_institution.institution.get_by_name(db, name=institution_in.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ya existe una institución con este nombre")

    if institution_in.acronym and crud_institution.institution.get_by_acronym(db, acronym=institution_in.acronym):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ya existe una institución con este acrónimo")

    try:
        institution = crud_institution.institution.create_with_admin(
            db=db,
            obj_in=institution_in,
            admin_id=current_user.system_admin.id
        )
        return institution
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# -------------------------------
# Listar instituciones
# -------------------------------
@router.get("/", response_model=InstitutionListResponse)
def read_institutions(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role == UserRole.ADMINISTRATOR:
        institutions = crud_institution.institution.get_multi(db, skip=skip, limit=limit)
        total = crud_institution.institution.count(db)
    elif current_user.role == UserRole.COORDINATOR:
        institutions = [current_user.coordinator.institution] if current_user.coordinator.institution else []
        total = 1 if institutions else 0
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para ver las instituciones")

    return InstitutionListResponse(institutions=institutions, total=total, skip=skip, limit=limit)

# -------------------------------
# Buscar instituciones
# -------------------------------
@router.get("/search", response_model=InstitutionListResponse)
def search_institutions(
    *,
    db: Session = Depends(deps.get_db),
    query: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los administradores pueden buscar instituciones")

    institutions = crud_institution.institution.search_institutions(
        db, query=query, skip=skip, limit=limit
    )

    return InstitutionListResponse(
        institutions=institutions,
        total=len(institutions),
        skip=skip,
        limit=limit
    )

# -------------------------------
# Obtener institución por país
# -------------------------------
@router.get("/by-country/{country}", response_model=InstitutionListResponse)
def get_institutions_by_country(
    *,
    db: Session = Depends(deps.get_db),
    country: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los administradores pueden filtrar por país")

    institutions = crud_institution.institution.get_by_country(
        db, country=country, skip=skip, limit=limit
    )

    return InstitutionListResponse(
        institutions=institutions,
        total=len(institutions),
        skip=skip,
        limit=limit
    )

# -------------------------------
# Obtener institución por ID con stats
# -------------------------------
@router.get("/{institution_id}", response_model=InstitutionWithStats)
def read_institution(
    *,
    db: Session = Depends(deps.get_db),
    institution_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    institution = crud_institution.institution.get(db, id=institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institución no encontrada")

    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator or current_user.coordinator.institution_id != institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="No tienes permisos para ver esta institución")
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para ver instituciones")

    students_count = crud_institution.institution.get_students_count(db, institution_id=institution_id)
    teachers_count = crud_institution.institution.get_teachers_count(db, institution_id=institution_id)
    coordinators_count = len(crud_institution.institution.get_coordinators(db, institution_id=institution_id))
    courses_count = len(getattr(institution, "courses", []))
    programs_count = len(getattr(institution, "programs", []))

    return InstitutionWithStats(
        **vars(institution),
        students_count=students_count,
        teachers_count=teachers_count,
        coordinators_count=coordinators_count,
        courses_count=courses_count,
        programs_count=programs_count
    )

# -------------------------------
# Actualizar institución
# -------------------------------
@router.put("/{institution_id}", response_model=InstitutionResponse)
def update_institution(
    *,
    db: Session = Depends(deps.get_db),
    institution_id: UUID,
    institution_in: InstitutionUpdate,
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los administradores pueden actualizar instituciones")

    institution = crud_institution.institution.get(db, id=institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institución no encontrada")

    if institution_in.name:
        existing_name = crud_institution.institution.get_by_name(db, name=institution_in.name)
        if existing_name and existing_name.id != institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Ya existe otra institución con este nombre")

    if institution_in.acronym:
        existing_acronym = crud_institution.institution.get_by_acronym(db, acronym=institution_in.acronym)
        if existing_acronym and existing_acronym.id != institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Ya existe otra institución con este acrónimo")

    institution = crud_institution.institution.update(db, db_obj=institution, obj_in=institution_in)
    return institution

# -------------------------------
# Eliminar institución
# -------------------------------
@router.delete("/{institution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_institution(
    *,
    db: Session = Depends(deps.get_db),
    institution_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los administradores pueden eliminar instituciones")

    institution = crud_institution.institution.get(db, id=institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institución no encontrada")

    if institution.administrator_id != current_user.system_admin.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo puedes eliminar instituciones que administras")

    crud_institution.institution.remove(db, id=institution_id)
    return

# -------------------------------
# Coordinadores
# -------------------------------
@router.post("/{institution_id}/coordinators", response_model=dict)
def assign_coordinator(
    *,
    db: Session = Depends(deps.get_db),
    institution_id: UUID,
    coordinator_assignment: CoordinatorAssignment,
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los administradores pueden asignar coordinadores")
    try:
        crud_institution.institution.add_coordinator(
            db, institution_id=institution_id, coordinator_id=coordinator_assignment.coordinator_id
        )
        return {"message": "Coordinador asignado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{institution_id}/coordinators/{coordinator_id}", response_model=dict)
def remove_coordinator(
    *,
    db: Session = Depends(deps.get_db),
    institution_id: UUID,
    coordinator_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMINISTRATOR:
        log_security_event("REMOVE_COORDINATOR_FORBIDDEN", {
            "user_id": str(current_user.id),
            "institution_id": str(institution_id),
            "coordinator_id": str(coordinator_id)
        })
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los administradores pueden remover coordinadores")
    try:
        crud_institution.institution.remove_coordinator(
            db, institution_id=institution_id, coordinator_id=coordinator_id
        )
        log_user_action(str(current_user.id), "REMOVE_COORDINATOR", {
            "institution_id": str(institution_id),
            "coordinator_id": str(coordinator_id)
        })
        return {"message": "Coordinador removido exitosamente"}
    except ValueError as e:
        log_security_event("REMOVE_COORDINATOR_ERROR", {
            "user_id": str(current_user.id),
            "institution_id": str(institution_id),
            "coordinator_id": str(coordinator_id),
            "error": str(e)
        })
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{institution_id}/coordinators", response_model=InstitutionCoordinators)
def get_institution_coordinators(
    *,
    db: Session = Depends(deps.get_db),
    institution_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    institution = crud_institution.institution.get(db, id=institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institución no encontrada")

    if current_user.role == UserRole.COORDINATOR:
        if not current_user.coordinator or current_user.coordinator.institution_id != institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="No tienes permisos para ver los coordinadores de esta institución")
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para ver coordinadores")

    coordinators = crud_institution.institution.get_coordinators(db, institution_id=institution_id)
    coordinators_data = [{
        "id": coord.id,
        "user_id": coord.user_id,
        "office_hours": coord.office_hours,
        "career_start_date": coord.career_start_date,
        "first_names": coord.user.first_names,
        "last_names": coord.user.last_names,
        "institutional_email": coord.user.institutional_email
    } for coord in coordinators]

    return InstitutionCoordinators(institution_id=institution_id, coordinators=coordinators_data)

# -------------------------------
# Transferir propiedad
# -------------------------------
@router.post("/{institution_id}/transfer-ownership", response_model=InstitutionResponse)
def transfer_institution_ownership(
    *,
    db: Session = Depends(deps.get_db),
    institution_id: UUID,
    transfer_data: InstitutionTransferOwnership,
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los administradores pueden transferir instituciones")
    try:
        institution = crud_institution.institution.transfer_ownership(
            db,
            institution_id=institution_id,
            new_admin_id=transfer_data.new_admin_id,
            current_admin_id=current_user.system_admin.id
        )
        return institution
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# -------------------------------
# Mis instituciones
# -------------------------------
@router.get("/my-institutions", response_model=InstitutionListResponse)
def get_my_institutions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role == UserRole.ADMINISTRATOR:
        institutions = crud_institution.institution.get_by_admin(db, admin_id=current_user.system_admin.id)
    elif current_user.role == UserRole.COORDINATOR:
        institutions = [current_user.coordinator.institution] if current_user.coordinator.institution else []
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="No tienes permisos para ver instituciones")

    return InstitutionListResponse(institutions=institutions, total=len(institutions), skip=0, limit=len(institutions))
