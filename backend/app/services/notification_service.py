# backend/app/services/notification_service.py
"""
Servicio de notificaciones en tiempo real y escalable
- Centraliza la creación y envío de notificaciones
- Optimizado para cargas masivas y envío paralelo
- Compatible con todas las notificaciones del sistema, tareas y gamificación
"""

from typing import List, Optional, Dict
from uuid import UUID
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.user import User, Student, UserRole
from ..models.assignment import Assignment, AssignmentSubmission
from ..models.gamification import Badge, Reward
from ..models.class_model import Class
from ..models.group import StudentGroup, GroupCourse
from ..schemas.chat import WebSocketNotification
from ..utils.websocket_utils import ConnectionManager


class NotificationService:
    """Servicio centralizado para notificaciones en tiempo real"""

    @staticmethod
    def _get_manager() -> ConnectionManager:
        """Obtener instancia singleton del manager de websockets"""
        return ConnectionManager()

    @staticmethod
    async def _send(user_id: UUID, notification: WebSocketNotification) -> None:
        """Enviar notificación a un usuario"""
        manager = NotificationService._get_manager()
        await manager.send_notification_to_user(user_id, notification.dict())

    @staticmethod
    async def _send_bulk(user_ids: List[UUID], notification_factory) -> None:
        """Enviar notificación a múltiples usuarios en paralelo"""
        tasks = [NotificationService._send(uid, notification_factory(uid)) for uid in user_ids]
        await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    def _create_notification(
        type_: str,
        title: str,
        message: str,
        user_id: UUID,
        data: Optional[Dict] = None,
        priority: str = "normal"
    ) -> WebSocketNotification:
        """Crea un objeto de notificación estándar"""
        return WebSocketNotification(
            type=type_,
            title=title,
            message=message,
            data=data or {},
            priority=priority,
            user_id=user_id
        )

    # -----------------------------
    # NOTIFICACIONES DE TAREAS
    # -----------------------------
    @staticmethod
    async def notify_new_assignment(db: Session, assignment_id: UUID) -> None:
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            return

        students = (
            db.query(Student)
            .join(StudentGroup, Student.id == StudentGroup.student_id)
            .join(GroupCourse, StudentGroup.group_id == GroupCourse.group_id)
            .join(Class, GroupCourse.id == Class.group_course_id)
            .filter(Class.id == assignment.class_id)
            .all()
        )

        async def factory(user_id: UUID):
            return NotificationService._create_notification(
                type_="new_assignment",
                title="Nueva Tarea Asignada",
                message=f"Se ha asignado una nueva tarea: {assignment.title}",
                user_id=user_id,
                data={
                    "assignment_id": str(assignment.id),
                    "assignment_title": assignment.title,
                    "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
                    "class_id": str(assignment.class_id)
                },
                priority="high"
            )

        await NotificationService._send_bulk([s.user_id for s in students], factory)

    @staticmethod
    async def notify_assignment_graded(db: Session, submission_id: UUID) -> None:
        submission = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
        if not submission:
            return

        notification = NotificationService._create_notification(
            type_="assignment_graded",
            title="Tarea Calificada",
            message=f"Tu tarea '{submission.assignment.title}' ha sido calificada",
            user_id=submission.student.user_id,
            data={
                "submission_id": str(submission.id),
                "assignment_id": str(submission.assignment_id),
                "assignment_title": submission.assignment.title,
                "has_feedback": bool(submission.text_feedback or submission.audio_feedback)
            },
            priority="high"
        )
        await NotificationService._send(submission.student.user_id, notification)

    @staticmethod
    async def notify_assignment_due_soon(db: Session, assignment_id: UUID, hours_before: int = 24) -> None:
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment or not assignment.due_date:
            return

        students = (
            db.query(Student)
            .join(StudentGroup, Student.id == StudentGroup.student_id)
            .join(GroupCourse, StudentGroup.group_id == GroupCourse.group_id)
            .join(Class, GroupCourse.id == Class.group_course_id)
            .outerjoin(
                AssignmentSubmission,
                and_(
                    AssignmentSubmission.assignment_id == assignment_id,
                    AssignmentSubmission.student_id == Student.id
                )
            )
            .filter(Class.id == assignment.class_id, AssignmentSubmission.id.is_(None))
            .all()
        )

        async def factory(user_id: UUID):
            return NotificationService._create_notification(
                type_="assignment_due_soon",
                title="Tarea Próxima a Vencer",
                message=f"La tarea '{assignment.title}' vence en {hours_before} horas",
                user_id=user_id,
                data={
                    "assignment_id": str(assignment.id),
                    "assignment_title": assignment.title,
                    "due_date": assignment.due_date.isoformat(),
                    "hours_remaining": hours_before
                },
                priority="urgent"
            )

        await NotificationService._send_bulk([s.user_id for s in students], factory)

    # -----------------------------
    # NOTIFICACIONES DE GAMIFICACIÓN
    # -----------------------------
    @staticmethod
    async def notify_badge_earned(db: Session, user_id: UUID, badge_id: UUID) -> None:
        badge = db.query(Badge).filter(Badge.id == badge_id).first()
        if not badge:
            return

        notification = NotificationService._create_notification(
            type_="badge_earned",
            title="¡Insignia Desbloqueada!",
            message=f"Has ganado la insignia: {badge.name}",
            user_id=user_id,
            data={
                "badge_id": str(badge.id),
                "badge_name": badge.name,
                "badge_description": badge.description,
                "badge_image_url": badge.image_url
            },
            priority="high"
        )
        await NotificationService._send(user_id, notification)

    @staticmethod
    async def notify_points_earned(user_id: UUID, points: int) -> None:
        notification = NotificationService._create_notification(
            type_="points_earned",
            title="¡Puntos Ganados!",
            message=f"Has ganado {points} puntos",
            user_id=user_id,
            data={"points": points},
            priority="normal"
        )
        await NotificationService._send(user_id, notification)

    @staticmethod
    async def notify_reward_redeemed(db: Session, user_id: UUID, reward_id: UUID) -> None:
        reward = db.query(Reward).filter(Reward.id == reward_id).first()
        if not reward:
            return

        notification = NotificationService._create_notification(
            type_="reward_redeemed",
            title="Recompensa Canjeada",
            message=f"Has canjeado: {reward.name}",
            user_id=user_id,
            data={"reward_id": str(reward.id), "reward_name": reward.name, "points_cost": reward.points_cost},
            priority="normal"
        )
        await NotificationService._send(user_id, notification)

    # -----------------------------
    # NOTIFICACIONES DEL SISTEMA
    # -----------------------------
    @staticmethod
    async def notify_system_announcement(
        db: Session, title: str, message: str,
        target_role: Optional[UserRole] = None,
        institution_id: Optional[UUID] = None
    ) -> None:
        query = db.query(User)
        if target_role:
            query = query.filter(User.role == target_role)
        users = query.all()

        async def factory(user_id: UUID):
            return NotificationService._create_notification(
                type_="system_announcement",
                title=title,
                message=message,
                user_id=user_id,
                data={
                    "institution_id": str(institution_id) if institution_id else None,
                    "target_role": target_role.value if target_role else None
                },
                priority="high"
            )

        await NotificationService._send_bulk([u.id for u in users], factory)
