# backend/app/api/endpoints/classes.py
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy import and_
from app.api import deps
from app.crud import class_crud as crud_class
from app.schemas.class_schema import (
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    ClassWithDetails,
    ClassListResponse,
    AttendanceUpdate,
    AttendanceResponse,
    ClassAttendanceResponse,
    BulkAttendanceUpdate,
    ClassReschedule,
    ClassCancellation,
)
from app.models.user import User, UserRole
from app.models.class_model import AttendanceStatus
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    *,
    db: Session = Depends(deps.get_db),
    class_in: ClassCreate,
    group_course_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Crea una nueva clase.
    Solo docentes pueden crear clases en sus cursos asignados.
    """
    # Verificar permisos de docente
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden crear clases"
        )
    
    if not current_user.teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no tiene perfil de docente"
        )
    
    # Verificar que el docente está asignado al grupo-curso
    from app.models.group import GroupCourse
    group_course = db.query(GroupCourse).filter(
        and_(
            GroupCourse.id == group_course_id,
            GroupCourse.teacher_id == current_user.teacher.id
        )
    ).first()
    
    if not group_course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear clases en este curso"
        )
    
    try:
        class_obj = crud_class.class_crud.create_with_group_course(
            db=db, obj_in=class_in, group_course_id=group_course_id
        )
        return class_obj
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=ClassListResponse)
def read_classes(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    group_course_id: Optional[UUID] = Query(None),
    teacher_id: Optional[UUID] = Query(None),
    upcoming_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtiene la lista de clases.
    Los docentes ven sus clases, los estudiantes ven las de sus grupos.
    """
    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no tiene perfil de docente"
            )
        
        if upcoming_only:
            classes = crud_class.class_crud.get_upcoming_classes(
                db, teacher_id=current_user.teacher.id, skip=skip, limit=limit
            )
        else:
            classes = crud_class.class_crud.get_by_teacher(
                db, teacher_id=current_user.teacher.id, skip=skip, limit=limit
            )
        
    elif current_user.role == UserRole.STUDENT:
        if not current_user.student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no tiene perfil de estudiante"
            )
        
        if upcoming_only:
            classes = crud_class.class_crud.get_upcoming_classes(
                db, student_id=current_user.student.id, skip=skip, limit=limit
            )
        else:
            classes = crud_class.class_crud.get_classes_for_student(
                db, student_id=current_user.student.id, skip=skip, limit=limit
            )
        
    elif current_user.role in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        if group_course_id:
            classes = crud_class.class_crud.get_by_group_course(
                db, group_course_id=group_course_id, skip=skip, limit=limit
            )
        else:
            classes = crud_class.class_crud.get_multi(db, skip=skip, limit=limit)
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver clases"
        )
    
    return ClassListResponse(
        classes=classes,
        total=len(classes),
        skip=skip,
        limit=limit
    )

@router.get("/today", response_model=ClassListResponse)
def get_today_classes(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtiene las clases de hoy para el usuario actual.
    """
    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no tiene perfil de docente"
            )
        classes = crud_class.class_crud.get_today_classes(db, teacher_id=current_user.teacher.id)
        
    elif current_user.role == UserRole.STUDENT:
        if not current_user.student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no tiene perfil de estudiante"
            )
        classes = crud_class.class_crud.get_today_classes(db, student_id=current_user.student.id)
        
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo docentes y estudiantes pueden ver sus clases de hoy"
        )
    
    return ClassListResponse(
        classes=classes,
        total=len(classes),
        skip=0,
        limit=len(classes)
    )

@router.get("/{class_id}", response_model=ClassWithDetails)
def read_class(
    *,
    db: Session = Depends(deps.get_db),
    class_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtiene una clase por ID con detalles completos.
    """
    class_obj = crud_class.class_crud.get(db, id=class_id)
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada"
        )
    
    # Verificar permisos según el rol
    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher or class_obj.group_course.teacher_id != current_user.teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver esta clase"
            )
    elif current_user.role == UserRole.STUDENT:
        # Verificar que el estudiante pertenece al grupo de la clase
        from app.models.group import StudentGroup, StudentGroupStatus
        student_in_group = db.query(StudentGroup).filter(
            and_(
                StudentGroup.student_id == current_user.student.id,
                StudentGroup.group_id == class_obj.group_course.group_id,
                StudentGroup.status == StudentGroupStatus.ACTIVE
            )
        ).first()
        
        if not student_in_group:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver esta clase"
            )
    
    # Obtener estadísticas de la clase
    try:
        stats = crud_class.class_crud.get_class_statistics(db, class_id=class_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return ClassWithDetails(
        **class_obj.__dict__,
        course_name=stats["course_name"],
        group_name=stats["group_name"],
        teacher_name=stats["teacher_name"],
        teacher_email=class_obj.group_course.teacher.user.institutional_email,
        platform_name=class_obj.platform.name if class_obj.platform else None,
        total_students=stats["total_students"],
        present_students=stats["present_students"],
        attendance_percentage=stats["attendance_percentage"],
        materials_count=stats["materials_count"],
        assignments_count=stats["assignments_count"]
    )

@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    *,
    db: Session = Depends(deps.get_db),
    class_id: UUID,
    class_in: ClassUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Actualiza una clase existente.
    Solo el docente asignado puede actualizar la clase.
    """
    class_obj = crud_class.class_crud.get(db, id=class_id)
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher or class_obj.group_course.teacher_id != current_user.teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para actualizar esta clase"
            )
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar clases"
        )
    
    class_obj = crud_class.class_crud.update(db, db_obj=class_obj, obj_in=class_in)
    return class_obj


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    *,
    db: Session = Depends(deps.get_db),
    class_id: UUID,
    current_user: User = Depends(deps.get_current_active_user)
) -> None:
    """
    Elimina una clase.
    Solo el docente asignado puede eliminar la clase.
    """
    class_obj = crud_class.class_crud.get(db, id=class_id)
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher or class_obj.group_course.teacher_id != current_user.teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar esta clase"
            )
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar clases"
        )
    
    crud_class.class_crud.remove(db, id=class_id)
@router.get("/{class_id}/attendance", response_model=ClassAttendanceResponse)
def get_class_attendance(
    *,
    db: Session = Depends(deps.get_db),
    class_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtiene la asistencia de una clase.
    Solo docentes y coordinadores pueden ver la asistencia completa.
    """
    class_obj = crud_class.class_crud.get(db, id=class_id)
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher or class_obj.group_course.teacher_id != current_user.teacher.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver la asistencia de esta clase"
            )
    elif current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver asistencia"
        )
    
    attendances = crud_class.class_crud.get_class_attendance(db, class_id=class_id)
    
    # Formatear datos de asistencia
    attendance_data = []
    for att in attendances:
        attendance_data.append({
            "id": att.id,
            "class_id": att.class_id,
            "student_id": att.student_id,
            "status": att.status,
            "created_at": att.created_at,
            "student_first_names": att.student.user.first_names,
            "student_last_names": att.student.user.last_names,
            "student_email": att.student.user.institutional_email,
            "student_document_number": att.student.user.document_number
        })
    
    # Calcular resumen de asistencia
    total = len(attendance_data)
    present = sum(1 for att in attendances if att.status == AttendanceStatus.PRESENT)
    justified = sum(1 for att in attendances if att.status == AttendanceStatus.JUSTIFIED)
    absent = sum(1 for att in attendances if att.status == AttendanceStatus.ABSENT)
    
    attendance_summary = {
        "total_students": total,
        "present": present,
        "justified": justified,
        "absent": absent,
        "attendance_percentage": ((present + justified) / total * 100) if total > 0 else 0
    }
    
    return ClassAttendanceResponse(
        class_id=class_id,
        class_title=class_obj.title,
        start_time=class_obj.start_time,
        attendances=attendance_data,
        attendance_summary=attendance_summary
    )

@router.put("/{class_id}/attendance/{student_id}", response_model=AttendanceResponse)
def update_student_attendance(
    *,
    db: Session = Depends(deps.get_db),
    class_id: UUID,
    student_id: UUID,
    attendance_in: AttendanceUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Actualiza la asistencia de un estudiante en una clase.
    Solo docentes pueden marcar asistencia.
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden marcar asistencia"
        )
    
    try:
        attendance = crud_class.class_crud.mark_attendance(
            db,
            class_id=class_id,
            student_id=student_id,
            status=attendance_in.status
        )
        
        # Formatear respuesta
        response_data = {
            "id": attendance.id,
            "class_id": attendance.class_id,
            "student_id": attendance.student_id,
            "status": attendance.status,
            "created_at": attendance.created_at,
            "student_first_names": attendance.student.user.first_names,
            "student_last_names": attendance.student.user.last_names,
            "student_email": attendance.student.user.institutional_email,
            "student_document_number": attendance.student.user.document_number
        }
        
        return AttendanceResponse(**response_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{class_id}/attendance/bulk", response_model=List[AttendanceResponse])
def bulk_update_attendance(
    *,
    db: Session = Depends(deps.get_db),
    class_id: UUID,
    bulk_attendance: BulkAttendanceUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Actualiza la asistencia de múltiples estudiantes en una clase.
    Solo docentes pueden marcar asistencia masiva.
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden marcar asistencia"
        )
    
    try:
        updated_attendances = crud_class.class_crud.bulk_mark_attendance(
            db,
            class_id=class_id,
            attendance_data=bulk_attendance.attendance_data
        )
        
        # Formatear respuestas
        response_data = []
        for att in updated_attendances:
            response_data.append({
                "id": att.id,
                "class_id": att.class_id,
                "student_id": att.student_id,
                "status": att.status,
                "created_at": att.created_at,
                "student_first_names": att.student.user.first_names,
                "student_last_names": att.student.user.last_names,
                "student_email": att.student.user.institutional_email,
                "student_document_number": att.student.user.document_number
            })
        
        return [AttendanceResponse(**data) for data in response_data]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{class_id}/reschedule", response_model=ClassResponse)
def reschedule_class(
    *,
    db: Session = Depends(deps.get_db),
    class_id: UUID,
    reschedule_data: ClassReschedule,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Reprograma una clase.
    Solo el docente asignado puede reprogramar.
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden reprogramar clases"
        )
    
    try:
        class_obj = crud_class.class_crud.reschedule_class(
            db,
            class_id=class_id,
            new_start_time=reschedule_data.new_start_time,
            new_duration=reschedule_data.new_duration
        )
        return class_obj
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{class_id}/cancel", response_model=ClassResponse)
def cancel_class(
    *,
    db: Session = Depends(deps.get_db),
    class_id: UUID,
    cancellation_data: ClassCancellation,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Cancela una clase.
    Solo el docente asignado puede cancelar.
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los docentes pueden cancelar clases"
        )
    
    try:
        class_obj = crud_class.class_crud.cancel_class(
            db,
            class_id=class_id,
            reason=cancellation_data.reason
        )
        return class_obj
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )