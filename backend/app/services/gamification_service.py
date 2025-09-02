# backend/app/services/gamification_service.py
from typing import List, Tuple
from sqlalchemy.orm import Session
from uuid import UUID

from ..crud import gamification as crud_gamification
from ..models.user import User, Student
from ..models.assignment import AssignmentSubmission
from ..models.gamification import Badge, UserBadge, UserReward
from ..schemas.gamification import (
    UserGameProfile, UserAchievementProgress
)


class GamificationService:
    """Servicio completo de gamificación"""

    @staticmethod
    def award_points_for_submission(db: Session, student_id: UUID, assignment_id: UUID) -> int:
        """Otorgar puntos por entrega de tarea"""
        submission = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == student_id
        ).first()

        if not submission:
            return 0

        points = crud_gamification.GamificationLogic.calculate_points_for_submission(
            db, assignment_id, submission.submission_date
        )

        if points > 0:
            crud_gamification.user_points.add_points(
                db=db,
                user_id=submission.student.user_id,
                points=points,
                reason=f"Assignment submission: {submission.assignment.title}"
            )
            GamificationService.check_and_award_achievements(db, submission.student.user_id)

        return points

    @staticmethod
    def award_points_for_grade(db: Session, student_id: UUID, grade_value_id: UUID) -> int:
        """Otorgar puntos por calificación obtenida"""
        points = crud_gamification.GamificationLogic.calculate_points_for_grade(db, grade_value_id)

        if points > 0:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                crud_gamification.user_points.add_points(
                    db=db,
                    user_id=student.user_id,
                    points=points,
                    reason="Grade received"
                )
                GamificationService.check_and_award_achievements(db, student.user_id)

        return points

    @staticmethod
    def check_and_award_achievements(db: Session, user_id: UUID) -> List[UUID]:
        """Verificar y otorgar logros automáticos"""
        earned_badges = []

        # Rachas
        streak_badges = crud_gamification.GamificationLogic.check_streak_achievements(db, user_id)
        for badge_id in streak_badges:
            user_badge = crud_gamification.user_badge.grant_badge(db, user_id=user_id, badge_id=badge_id)
            if user_badge:
                earned_badges.append(badge_id)

        # Entregas y puntos
        GamificationService._check_submission_count_achievements(db, user_id, earned_badges)
        GamificationService._check_points_achievements(db, user_id, earned_badges)

        return earned_badges

    @staticmethod
    def _check_submission_count_achievements(db: Session, user_id: UUID, earned_badges: List[UUID]) -> None:
        """Verificar logros por cantidad de entregas"""
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if not student:
            return

        submission_count = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.student_id == student.id
        ).count()

        badges = db.query(Badge).filter(Badge.badge_type == "objective").filter(Badge.name.like("%entrega%")).all()
        for badge in badges:
            try:
                required_count = getattr(badge, "threshold", int(badge.name.split()[0]))
                if submission_count >= required_count and not crud_gamification.user_badge.has_badge(db, user_id=user_id, badge_id=badge.id):
                    user_badge = crud_gamification.user_badge.grant_badge(db, user_id=user_id, badge_id=badge.id)
                    if user_badge:
                        earned_badges.append(badge.id)
            except (ValueError, IndexError):
                continue

    @staticmethod
    def _check_points_achievements(db: Session, user_id: UUID, earned_badges: List[UUID]) -> None:
        """Verificar logros por puntos acumulados"""
        points_record = crud_gamification.user_points.get_by_user(db=db, user_id=user_id)
        if not points_record:
            return
        points = points_record.accumulated_points

        badges = db.query(Badge).filter(Badge.badge_type == "objective").filter(Badge.name.like("%punto%")).all()
        for badge in badges:
            try:
                required_points = getattr(badge, "threshold", int(badge.name.split()[0]))
                if points >= required_points and not crud_gamification.user_badge.has_badge(db, user_id=user_id, badge_id=badge.id):
                    user_badge = crud_gamification.user_badge.grant_badge(db, user_id=user_id, badge_id=badge.id)
                    if user_badge:
                        earned_badges.append(badge.id)
            except (ValueError, IndexError):
                continue

    @staticmethod
    def get_user_game_profile(db: Session, user_id: UUID) -> UserGameProfile:
        """Obtener perfil completo de gamificación de un usuario"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        points_record = crud_gamification.user_points.get_by_user(db=db, user_id=user_id)
        total_points = points_record.accumulated_points if points_record else 0

        user_badges = crud_gamification.user_badge.get_by_user(db=db, user_id=user_id)
        badges = [ub.badge for ub in user_badges if ub.badge]

        current_theme = crud_gamification.user_theme.get_active_theme(db=db, user_id=user_id)

        rank_position = None
        total_assignments = 0
        average_grade = None

        if user.role == "student":
            student = db.query(Student).filter(Student.user_id == user_id).first()
            if student:
                rank_position = crud_gamification.user_points.get_user_rank(db=db, user_id=user_id, program_id=student.program_id)
                total_assignments = db.query(AssignmentSubmission).filter(AssignmentSubmission.student_id == student.id).count()
                graded_submissions = db.query(AssignmentSubmission).filter(
                    AssignmentSubmission.student_id == student.id,
                    AssignmentSubmission.grade_value_id.isnot(None)
                ).all()
                if graded_submissions:
                    # Promedio simple (puedes implementar lógica real)
                    average_grade = sum([1 for _ in graded_submissions]) / len(graded_submissions)

        return UserGameProfile(
            user_id=user_id,
            user_name=f"{user.first_names} {user.last_names}",
            total_points=total_points,
            badges=badges,
            current_theme=current_theme.theme if current_theme else None,
            rank_position=rank_position,
            total_assignments_submitted=total_assignments,
            average_grade=average_grade
        )

    @staticmethod
    def get_user_achievement_progress(db: Session, user_id: UUID) -> List[UserAchievementProgress]:
        """Obtener progreso de logros del usuario"""
        all_badges = crud_gamification.badge.get_multi(db=db)
        user_badges = crud_gamification.user_badge.get_by_user(db=db, user_id=user_id)
        earned_ids = {ub.badge_id for ub in user_badges}

        progress_list = []
        for badge in all_badges:
            is_completed = badge.id in earned_ids
            current_progress, required_progress = 0, getattr(badge, "threshold", 1)

            if not is_completed:
                if badge.badge_type.value == "streak":
                    current_progress, required_progress = GamificationService._calculate_streak_progress(db, user_id, badge)
                elif badge.badge_type.value == "objective":
                    current_progress, required_progress = GamificationService._calculate_objective_progress(db, user_id, badge)
            else:
                current_progress = required_progress

            progress_percentage = (current_progress / required_progress * 100) if required_progress > 0 else 0
            progress_list.append(UserAchievementProgress(
                badge_id=badge.id,
                badge_name=badge.name,
                badge_description=badge.description or "",
                badge_image_url=badge.image_url,
                current_progress=current_progress,
                required_progress=required_progress,
                progress_percentage=min(progress_percentage, 100.0),
                is_completed=is_completed
            ))

        return progress_list

    @staticmethod
    def _calculate_streak_progress(db: Session, user_id: UUID, badge: Badge) -> Tuple[int, int]:
        """Calcular progreso de rachas"""
        required_streak = getattr(badge, "threshold", 1)
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if not student:
            return 0, required_streak

        recent_submissions = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.student_id == student.id
        ).order_by(AssignmentSubmission.submission_date.desc()).limit(required_streak).all()

        return min(len(recent_submissions), required_streak), required_streak

    @staticmethod
    def _calculate_objective_progress(db: Session, user_id: UUID, badge: Badge) -> Tuple[int, int]:
        """Calcular progreso de objetivos"""
        threshold = getattr(badge, "threshold", 1)
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if not student:
            return 0, threshold

        if "entrega" in badge.name.lower():
            current = db.query(AssignmentSubmission).filter(AssignmentSubmission.student_id == student.id).count()
            return min(current, threshold), threshold
        elif "punto" in badge.name.lower():
            points_record = crud_gamification.user_points.get_by_user(db=db, user_id=user_id)
            current = points_record.accumulated_points if points_record else 0
            return min(current, threshold), threshold

        return 0, threshold

    @staticmethod
    def reset_user_progress(db: Session, user_id: UUID) -> bool:
        """Resetear progreso de un usuario"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        db.query(UserBadge).filter(UserBadge.user_id == user_id).delete()
        points_record = crud_gamification.user_points.get_by_user(db=db, user_id=user_id)
        if points_record:
            points_record.accumulated_points = 0
        db.query(UserReward).filter(UserReward.user_id == user_id).delete()

        db.commit()
        return True
