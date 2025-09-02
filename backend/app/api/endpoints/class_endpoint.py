# backend/app/endpoints/class_endpoint.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import uuid

from app.crud.class_crud import class_crud
from app.schemas.class_schema import (
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    ClassWithDetails,
    ClassListResponse,
    BulkAttendanceUpdate,
    ClassReschedule,
    ClassCancellation,
)
from app.api.deps import get_db  # tu dependencia de sesión de DB

router = APIRouter(prefix="/classes", tags=["Classes"])

# -------------------------
# CREAR CLASE
# -------------------------
@router.post("/", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(class_in: ClassCreate, db: Session = Depends(get_db)):
    try:
        db_class = class_crud.create_with_group_course(
            db, obj_in=class_in, group_course_id=class_in.group_course_id
        )
        return db_class
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -------------------------
# OBTENER CLASE POR ID
# -------------------------
@router.get("/{class_id}", response_model=ClassWithDetails)
def get_class(class_id: uuid.UUID, db: Session = Depends(get_db)):
    db_class = class_crud.get(db, id=class_id)
    if not db_class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clase no encontrada")
    stats = class_crud.get_class_statistics(db, class_id=class_id)
    # Combinar datos de clase con estadísticas
    return ClassWithDetails(
        id=db_class.id,
        group_course_id=db_class.group_course_id,
        title=db_class.title,
        description=db_class.description,
        start_time=db_class.start_time,
        duration=db_class.duration,
        video_call_link=db_class.video_call_link,
        platform_id=db_class.platform_id,
        created_at=db_class.created_at,
        updated_at=db_class.updated_at,
        course_name=stats["course_name"],
        group_name=stats["group_name"],
        teacher_name=stats["teacher_name"],
        teacher_email=db_class.group_course.teacher.user.email,
        platform_name=db_class.platform.name if db_class.platform else None,
        total_students=stats["total_students"],
        present_students=stats["present_students"],
        attendance_percentage=stats["attendance_percentage"],
        materials_count=stats["materials_count"],
        assignments_count=stats["assignments_count"]
    )


# -------------------------
# LISTAR CLASES
# -------------------------
@router.get("/", response_model=ClassListResponse)
def list_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    group_course_id: Optional[uuid.UUID] = None,
    teacher_id: Optional[uuid.UUID] = None,
    student_id: Optional[uuid.UUID] = None,
    upcoming_only: bool = False,
    days_ahead: int = 7,
    db: Session = Depends(get_db)
):
    if upcoming_only:
        classes = class_crud.get_upcoming_classes(
            db, teacher_id=teacher_id, student_id=student_id, days_ahead=days_ahead, skip=skip, limit=limit
        )
        total = len(classes)
    elif group_course_id:
        classes = class_crud.get_by_group_course(db, group_course_id=group_course_id, skip=skip, limit=limit)
        total = len(classes)
    elif teacher_id:
        classes = class_crud.get_by_teacher(db, teacher_id=teacher_id, skip=skip, limit=limit)
        total = len(classes)
    else:
        classes = db.query(class_crud.model).offset(skip).limit(limit).all()
        total = db.query(class_crud.model).count()

    return ClassListResponse(classes=classes, total=total, skip=skip, limit=limit)


# -------------------------
# ACTUALIZAR CLASE
# -------------------------
@router.put("/{class_id}", response_model=ClassResponse)
def update_class(class_id: uuid.UUID, class_in: ClassUpdate, db: Session = Depends(get_db)):
    db_class = class_crud.get(db, id=class_id)
    if not db_class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clase no encontrada")
    updated_class = class_crud.update(db, db_obj=db_class, obj_in=class_in)
    return updated_class


# -------------------------
# CANCELAR CLASE
# -------------------------
@router.patch("/{class_id}/cancel", response_model=ClassResponse)
def cancel_class(class_id: uuid.UUID, cancellation: ClassCancellation, db: Session = Depends(get_db)):
    db_class = class_crud.cancel_class(db, class_id=class_id, reason=cancellation.reason)
    return db_class


# -------------------------
# REPROGRAMAR CLASE
# -------------------------
@router.patch("/{class_id}/reschedule", response_model=ClassResponse)
def reschedule_class(class_id: uuid.UUID, reschedule: ClassReschedule, db: Session = Depends(get_db)):
    db_class = class_crud.reschedule_class(
        db, class_id=class_id, new_start_time=reschedule.new_start_time, new_duration=reschedule.new_duration
    )
    return db_class


# -------------------------
# MARCAR ASISTENCIA INDIVIDUAL
# -------------------------
@router.post("/{class_id}/attendance/{student_id}", response_model=dict)
def mark_attendance(class_id: uuid.UUID, student_id: uuid.UUID, status: str, db: Session = Depends(get_db)):
    try:
        attendance_status = class_crud.model.attendances.property.mapper.class_.status.enum_class(status)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado de asistencia inválido")
    attendance = class_crud.mark_attendance(db, class_id=class_id, student_id=student_id, status=attendance_status)
    return {"student_id": student_id, "status": attendance.status.value}


# -------------------------
# MARCAR ASISTENCIA MASIVA
# -------------------------
@router.post("/{class_id}/attendance/bulk", response_model=List[dict])
def bulk_mark_attendance(class_id: uuid.UUID, bulk_data: BulkAttendanceUpdate, db: Session = Depends(get_db)):
    updated = class_crud.bulk_mark_attendance(db, class_id=class_id, attendance_data=bulk_data.attendance_data)
    return [{"student_id": att.student_id, "status": att.status.value} for att in updated]
