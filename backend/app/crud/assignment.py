# backend/app/crud/assignment.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, and_, or_
from uuid import UUID
from datetime import datetime

from .base import CRUDBase
from ..models.assignment import Assignment, AssignmentSubmission, SubmissionStatus
from ..models.user import Student, Teacher
from ..models.class_model import Class
from ..models.group import GroupCourse, StudentGroup
from ..schemas.assignment import (
    AssignmentCreate, 
    AssignmentUpdate, 
    AssignmentSubmissionCreate, 
    AssignmentSubmissionUpdate
)

# -----------------------
# CRUD para Assignment
# -----------------------
class CRUDAssignment(CRUDBase[Assignment, AssignmentCreate, AssignmentUpdate]):

    def get_by_class(
        self, db: Session, *, class_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Assignment]:
        """Obtener todas las tareas de una clase"""
        return (
            db.query(self.model)
            .filter(self.model.class_id == class_id)
            .options(
                joinedload(self.model.teacher).joinedload(Teacher.user),
                selectinload(self.model.submissions)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_teacher(
        self, db: Session, *, teacher_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Assignment]:
        """Obtener todas las tareas de un docente"""
        return (
            db.query(self.model)
            .filter(self.model.teacher_id == teacher_id)
            .options(
                joinedload(self.model.class_session),
                selectinload(self.model.submissions)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_assignments_for_student(
        self, db: Session, *, student_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Assignment]:
        """Obtener todas las tareas disponibles para un estudiante"""
        return (
            db.query(self.model)
            .join(Class, self.model.class_id == Class.id)
            .join(GroupCourse, Class.group_course_id == GroupCourse.id)
            .join(StudentGroup, GroupCourse.group_id == StudentGroup.group_id)
            .filter(StudentGroup.student_id == student_id)
            .options(
                joinedload(self.model.teacher).joinedload(Teacher.user),
                joinedload(self.model.class_session),
                selectinload(self.model.submissions)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pending_assignments_for_student(
        self, db: Session, *, student_id: UUID
    ) -> List[Assignment]:
        """Obtener tareas pendientes para un estudiante"""
        submitted_assignments = db.query(AssignmentSubmission.assignment_id).filter(
            AssignmentSubmission.student_id == student_id
        ).subquery()

        return (
            db.query(self.model)
            .join(Class, self.model.class_id == Class.id)
            .join(GroupCourse, Class.group_course_id == GroupCourse.id)
            .join(StudentGroup, GroupCourse.group_id == StudentGroup.group_id)
            .filter(
                and_(
                    StudentGroup.student_id == student_id,
                    ~self.model.id.in_(submitted_assignments),
                    or_(
                        self.model.due_date.is_(None),
                        self.model.due_date > datetime.utcnow()
                    )
                )
            )
            .options(
                joinedload(self.model.teacher).joinedload(Teacher.user),
                joinedload(self.model.class_session),
                selectinload(self.model.submissions)
            )
            .all()
        )

    def get_with_submission_stats(
        self, db: Session, *, assignment_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Obtener tarea con estadísticas de entregas"""
        assignment = self.get(db, id=assignment_id)
        if not assignment:
            return None

        total_students = (
            db.query(func.count(StudentGroup.student_id))
            .join(GroupCourse, StudentGroup.group_id == GroupCourse.group_id)
            .join(Class, GroupCourse.id == Class.group_course_id)
            .filter(Class.id == assignment.class_id)
            .scalar()
        )

        submission_stats = (
            db.query(
                AssignmentSubmission.status,
                func.count(AssignmentSubmission.id)
            )
            .filter(AssignmentSubmission.assignment_id == assignment_id)
            .group_by(AssignmentSubmission.status)
            .all()
        )

        stats = {status.value: 0 for status in SubmissionStatus}
        stats['not_submitted'] = total_students

        for status, count in submission_stats:
            stats[status.value] = count
            stats['not_submitted'] -= count

        return {
            'assignment': assignment,
            'submission_stats': stats,
            'total_students': total_students
        }


# -----------------------
# CRUD para AssignmentSubmission
# -----------------------
class CRUDAssignmentSubmission(CRUDBase[AssignmentSubmission, AssignmentSubmissionCreate, AssignmentSubmissionUpdate]):

    def get_by_assignment_and_student(
        self, db: Session, *, assignment_id: UUID, student_id: UUID
    ) -> Optional[AssignmentSubmission]:
        """Obtener entrega específica de un estudiante para una tarea"""
        return (
            db.query(self.model)
            .filter(
                and_(
                    AssignmentSubmission.assignment_id == assignment_id,
                    AssignmentSubmission.student_id == student_id
                )
            )
            .first()
        )

    def get_by_assignment(
        self, db: Session, *, assignment_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AssignmentSubmission]:
        """Obtener todas las entregas de una tarea"""
        return (
            db.query(self.model)
            .filter(AssignmentSubmission.assignment_id == assignment_id)
            .options(
                joinedload(AssignmentSubmission.student).joinedload(Student.user),
                joinedload(AssignmentSubmission.grade_value)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_student(
        self, db: Session, *, student_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AssignmentSubmission]:
        """Obtener todas las entregas de un estudiante"""
        return (
            db.query(self.model)
            .filter(AssignmentSubmission.student_id == student_id)
            .options(
                joinedload(AssignmentSubmission.assignment),
                joinedload(AssignmentSubmission.grade_value)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_student(
        self, db: Session, *, obj_in: AssignmentSubmissionCreate, student_id: UUID
    ) -> AssignmentSubmission:
        """Crear una entrega de tarea con ID de estudiante"""
        db_obj = AssignmentSubmission(
            assignment_id=obj_in.assignment_id,
            student_id=student_id,
            file_url=obj_in.file_url,
            submission_date=obj_in.submission_date
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_grade_and_feedback(
        self, db: Session, *, submission_id: UUID,
        grade_value_id: Optional[UUID] = None,
        text_feedback: Optional[str] = None,
        audio_feedback: Optional[str] = None
    ) -> Optional[AssignmentSubmission]:
        """Actualizar calificación y retroalimentación de una entrega"""
        submission = self.get(db, id=submission_id)
        if not submission:
            return None

        update_data = {
            'status': SubmissionStatus.REVIEWED
        }
        if grade_value_id is not None:
            update_data['grade_value_id'] = grade_value_id
        if text_feedback is not None:
            update_data['text_feedback'] = text_feedback
        if audio_feedback is not None:
            update_data['audio_feedback'] = audio_feedback

        return self.update(db, db_obj=submission, obj_in=update_data)

    def get_late_submissions(
        self, db: Session, *, assignment_id: UUID
    ) -> List[AssignmentSubmission]:
        """Obtener entregas tardías de una tarea"""
        return (
            db.query(self.model)
            .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)
            .filter(
                and_(
                    AssignmentSubmission.assignment_id == assignment_id,
                    Assignment.due_date.isnot(None),
                    AssignmentSubmission.submission_date > Assignment.due_date
                )
            )
            .options(
                joinedload(AssignmentSubmission.student).joinedload(Student.user)
            )
            .all()
        )

    def get_submissions_without_grade(
        self, db: Session, *, teacher_id: Optional[UUID] = None,
        skip: int = 0, limit: int = 100
    ) -> List[AssignmentSubmission]:
        """Obtener entregas sin calificar"""
        query = (
            db.query(self.model)
            .filter(AssignmentSubmission.grade_value_id.is_(None))
            .options(
                joinedload(AssignmentSubmission.assignment),
                joinedload(AssignmentSubmission.student).joinedload(Student.user)
            )
        )
        if teacher_id:
            query = query.join(Assignment).filter(Assignment.teacher_id == teacher_id)

        return query.offset(skip).limit(limit).all()


# -----------------------
# Instancias de CRUD
# -----------------------
assignment = CRUDAssignment(Assignment)
assignment_submission = CRUDAssignmentSubmission(AssignmentSubmission)
