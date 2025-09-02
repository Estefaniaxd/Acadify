# backend/app/api/endpoints/assignments.py
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from ...database import get_db
from ...core.security import get_current_user
from ...crud import assignment
from ...models.user import User, UserRole, Teacher, Student
from ...schemas.assignment import (
    Assignment,
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentSubmission,
    AssignmentSubmissionCreate,
    AssignmentSubmissionUpdate,
    AssignmentStats,
    TeacherSubmissionView,
    StudentSubmissionDetail
)
from ...services.file_service import FileService
from ...services.notification_service import NotificationService
from ...services.gamification_service import GamificationService

router = APIRouter()


# -----------------------
# Dependencias de Roles
# -----------------------
async def get_current_teacher(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Optional[Teacher]:
    """Valida que el usuario sea docente, coordinador o administrador"""
    if current_user.role not in [UserRole.TEACHER, UserRole.COORDINATOR, UserRole.ADMINISTRATOR]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only teachers, coordinators, and administrators can perform this action")
    
    if current_user.role == UserRole.TEACHER:
        teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
        if not teacher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher profile not found")
        return teacher
    return None  # Coordinators and admins


async def get_current_student(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Student:
    """Valida que el usuario sea estudiante"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only students can perform this action")
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return student


# -----------------------
# Endpoints para Assignments
# -----------------------
@router.post("/", response_model=Assignment, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    *,
    db: Session = Depends(get_db),
    assignment_in: AssignmentCreate,
    current_teacher: Teacher = Depends(get_current_teacher)
) -> Any:
    """Crear nueva tarea"""
    if current_teacher:
        assignment_in.teacher_id = current_teacher.id

    new_assignment = assignment.create(db=db, obj_in=assignment_in)
    
    # Notificar estudiantes
    await NotificationService.notify_new_assignment(db, new_assignment.id)
    
    return new_assignment


@router.get("/", response_model=List[Assignment])
async def read_assignments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    class_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Obtener tareas según rol de usuario"""
    if current_user.role == UserRole.TEACHER:
        teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher profile not found")
        if class_id:
            return assignment.get_by_class(db=db, class_id=class_id, skip=skip, limit=limit)
        return assignment.get_by_teacher(db=db, teacher_id=teacher.id, skip=skip, limit=limit)

    elif current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        return assignment.get_assignments_for_student(db=db, student_id=student.id, skip=skip, limit=limit)

    # Coordinators or admins
    if class_id:
        return assignment.get_by_class(db=db, class_id=class_id, skip=skip, limit=limit)
    return assignment.get_multi(db=db, skip=skip, limit=limit)


@router.get("/pending", response_model=List[Assignment])
async def get_pending_assignments(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
) -> Any:
    """Obtener tareas pendientes del estudiante"""
    return assignment.get_pending_assignments_for_student(db=db, student_id=current_student.id)


@router.get("/{assignment_id}", response_model=Assignment)
async def read_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Obtener tarea específica"""
    db_assignment = assignment.get(db=db, id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return db_assignment


@router.get("/{assignment_id}/stats", response_model=AssignmentStats)
async def get_assignment_stats(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
) -> Any:
    """Obtener estadísticas de una tarea"""
    stats_data = assignment.get_with_submission_stats(db=db, assignment_id=assignment_id)
    if not stats_data:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return AssignmentStats(**stats_data['submission_stats'])


@router.put("/{assignment_id}", response_model=Assignment)
async def update_assignment(
    *,
    db: Session = Depends(get_db),
    assignment_id: UUID,
    assignment_in: AssignmentUpdate,
    current_teacher: Teacher = Depends(get_current_teacher)
) -> Any:
    """Actualizar tarea"""
    db_assignment = assignment.get(db=db, id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if current_teacher and db_assignment.teacher_id != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return assignment.update(db=db, db_obj=db_assignment, obj_in=assignment_in)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
) -> None:
    """Eliminar tarea"""
    db_assignment = assignment.get(db=db, id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if current_teacher and db_assignment.teacher_id != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    assignment.remove(db=db, id=assignment_id)


# -----------------------
# Endpoints para Assignment Submissions
# -----------------------
@router.post("/{assignment_id}/submissions", response_model=AssignmentSubmission, status_code=status.HTTP_201_CREATED)
async def submit_assignment(
    *,
    db: Session = Depends(get_db),
    assignment_id: UUID,
    file: UploadFile = File(...),
    current_student: Student = Depends(get_current_student)
) -> Any:
    """Entregar tarea"""
    db_assignment = assignment.get(db=db, id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    existing_submission = assignment.get_by_assignment_and_student(
        db=db, assignment_id=assignment_id, student_id=current_student.id
    )
    if existing_submission:
        raise HTTPException(status_code=400, detail="Assignment already submitted")

    if db_assignment.due_date and datetime.utcnow() > db_assignment.due_date and not db_assignment.allows_late_submissions:
        raise HTTPException(status_code=400, detail="Assignment deadline has passed")

    file_url = await FileService.upload_assignment_file(file, current_student.id, assignment_id)
    submission_in = AssignmentSubmissionCreate(assignment_id=assignment_id, file_url=file_url)
    new_submission = assignment.create_with_student(db=db, obj_in=submission_in, student_id=current_student.id)

    await GamificationService.award_points_for_submission(db, current_student.id, assignment_id)
    await NotificationService.notify_new_submission(db, new_submission.id)

    return new_submission


@router.get("/{assignment_id}/submissions", response_model=List[TeacherSubmissionView])
async def get_assignment_submissions(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_teacher: Teacher = Depends(get_current_teacher)
) -> Any:
    """Obtener entregas de una tarea (solo docentes)"""
    db_assignment = assignment.get(db=db, id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if current_teacher and db_assignment.teacher_id != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    submissions = assignment.get_by_assignment(db=db, assignment_id=assignment_id, skip=skip, limit=limit)
    return [
        TeacherSubmissionView(
            **submission.__dict__,
            student_name=f"{submission.student.user.first_names} {submission.student.user.last_names}",
            student_email=submission.student.user.institutional_email
        )
        for submission in submissions
    ]


@router.get("/submissions/my", response_model=List[StudentSubmissionDetail])
async def get_my_submissions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_student: Student = Depends(get_current_student)
) -> Any:
    """Obtener mis entregas (solo estudiantes)"""
    submissions = assignment.get_by_student(db=db, student_id=current_student.id, skip=skip, limit=limit)
    return [
        StudentSubmissionDetail(
            **submission.__dict__,
            assignment_title=submission.assignment.title,
            assignment_description=submission.assignment.description,
            assignment_due_date=submission.assignment.due_date
        )
        for submission in submissions
    ]


@router.get("/submissions/ungraded", response_model=List[TeacherSubmissionView])
async def get_ungraded_submissions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_teacher: Teacher = Depends(get_current_teacher)
) -> Any:
    """Obtener entregas sin calificar"""
    submissions = assignment.get_submissions_without_grade(db=db, teacher_id=current_teacher.id, skip=skip, limit=limit)
    return [
        TeacherSubmissionView(
            **submission.__dict__,
            student_name=f"{submission.student.user.first_names} {submission.student.user.last_names}",
            student_email=submission.student.user.institutional_email
        )
        for submission in submissions
    ]


@router.put("/submissions/{submission_id}/grade", response_model=AssignmentSubmission)
async def grade_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: UUID,
    grade_data: AssignmentSubmissionUpdate,
    current_teacher: Teacher = Depends(get_current_teacher)
) -> Any:
    """Calificar entrega de tarea"""
    db_submission = assignment.get(db=db, id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if current_teacher and db_submission.assignment.teacher_id != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_submission = assignment.update_grade_and_feedback(
        db=db,
        submission_id=submission_id,
        grade_value_id=grade_data.grade_value_id,
        text_feedback=grade_data.text_feedback,
        audio_feedback=grade_data.audio_feedback
    )

    if grade_data.grade_value_id:
        await GamificationService.award_points_for_grade(db, db_submission.student_id, grade_data.grade_value_id)

    await NotificationService.notify_assignment_graded(db, submission_id)
    return updated_submission


@router.get("/{assignment_id}/submissions/{student_id}", response_model=AssignmentSubmission)
async def get_student_submission(
    assignment_id: UUID,
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Obtener entrega específica de un estudiante"""
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student or student.id != student_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    submission = assignment.get_by_assignment_and_student(db=db, assignment_id=assignment_id, student_id=student_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.get("/{assignment_id}/late-submissions", response_model=List[TeacherSubmissionView])
async def get_late_submissions(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
) -> Any:
    """Obtener entregas tardías de una tarea"""
    db_assignment = assignment.get(db=db, id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if current_teacher and db_assignment.teacher_id != current_teacher.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    late_submissions = assignment.get_late_submissions(db=db, assignment_id=assignment_id)
    return [
        TeacherSubmissionView(
            **submission.__dict__,
            student_name=f"{submission.student.user.first_names} {submission.student.user.last_names}",
            student_email=submission.student.user.institutional_email
        )
        for submission in late_submissions
    ]
