from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from datetime import datetime

from .base import CRUDBase
from ..models.gamification import Badge, UserBadge, Reward, UserReward, UserPoints, Theme, UserTheme
from ..models.user import User, Student
from ..schemas.gamification import (
    BadgeCreate, BadgeUpdate,
    UserBadgeCreate,
    RewardCreate, RewardUpdate,
    UserRewardCreate,
    UserPointsCreate, UserPointsUpdate,
    ThemeCreate, ThemeUpdate,
    UserThemeCreate,
    LeaderboardEntry
)

# ----------------------------
# BADGE
# ----------------------------
class CRUDBadge(CRUDBase[Badge, BadgeCreate, BadgeUpdate]):
    def get_by_type(self, db: Session, badge_type: str) -> List[Badge]:
        return db.query(self.model).filter(Badge.badge_type == badge_type).all()

    def get_available_for_user(self, db: Session, user_id: UUID) -> List[Badge]:
        subquery = db.query(UserBadge.badge_id).filter(UserBadge.user_id == user_id).subquery()
        return db.query(self.model).filter(~Badge.id.in_(subquery)).all()

# ----------------------------
# USER BADGE
# ----------------------------
class CRUDUserBadge(CRUDBase[UserBadge, UserBadgeCreate, dict]):
    def get_by_user(self, db: Session, user_id: UUID) -> List[UserBadge]:
        return db.query(UserBadge).filter(UserBadge.user_id == user_id).options(joinedload(UserBadge.badge)).all()

    def has_badge(self, db: Session, user_id: UUID, badge_id: UUID) -> bool:
        return db.query(UserBadge).filter(
            UserBadge.user_id == user_id,
            UserBadge.badge_id == badge_id
        ).first() is not None

    def grant_badge(self, db: Session, user_id: UUID, badge_id: UUID, granted_by: Optional[UUID] = None) -> Optional[UserBadge]:
        if self.has_badge(db, user_id, badge_id):
            return None

        badge_obj = db.query(Badge).filter(Badge.id == badge_id).first()
        if badge_obj and badge_obj.is_unique:
            if db.query(UserBadge).filter(UserBadge.badge_id == badge_id).first():
                return None

        user_badge = UserBadge(user_id=user_id, badge_id=badge_id, granted_by=granted_by)
        try:
            db.add(user_badge)
            db.commit()
            db.refresh(user_badge)
            return user_badge
        except IntegrityError:
            db.rollback()
            return None

# ----------------------------
# REWARD
# ----------------------------
class CRUDReward(CRUDBase[Reward, RewardCreate, RewardUpdate]):
    def get_affordable_for_user(self, db: Session, user_id: UUID) -> List[Reward]:
        user_points = db.query(UserPoints).filter(UserPoints.user_id == user_id).first()
        available_points = user_points.accumulated_points if user_points else 0
        return db.query(Reward).filter(Reward.points_cost <= available_points).order_by(Reward.points_cost).all()

# ----------------------------
# USER REWARD
# ----------------------------
class CRUDUserReward(CRUDBase[UserReward, UserRewardCreate, dict]):
    def get_by_user(self, db: Session, user_id: UUID) -> List[UserReward]:
        return db.query(UserReward).filter(UserReward.user_id == user_id).options(joinedload(UserReward.reward)).order_by(desc(UserReward.redemption_date)).all()

    def redeem_reward(self, db: Session, user_id: UUID, reward_id: UUID) -> Tuple[Optional[UserReward], str]:
        reward_obj = db.query(Reward).filter(Reward.id == reward_id).first()
        if not reward_obj:
            return None, "Reward not found"

        user_points_obj = db.query(UserPoints).filter(UserPoints.user_id == user_id).first()
        if not user_points_obj or user_points_obj.accumulated_points < reward_obj.points_cost:
            return None, "Insufficient points"

        user_points_obj.accumulated_points -= reward_obj.points_cost
        user_reward = UserReward(user_id=user_id, reward_id=reward_id, redemption_date=datetime.utcnow())

        try:
            db.add(user_reward)
            db.commit()
            db.refresh(user_reward)
            return user_reward, "Success"
        except IntegrityError:
            db.rollback()
            return None, "Error during redemption"

# ----------------------------
# USER POINTS
# ----------------------------
class CRUDUserPoints(CRUDBase[UserPoints, UserPointsCreate, UserPointsUpdate]):
    def get_by_user(self, db: Session, user_id: UUID) -> Optional[UserPoints]:
        return db.query(UserPoints).filter(UserPoints.user_id == user_id).first()

    def add_points(self, db: Session, user_id: UUID, points: int, reason: str = "Manual addition") -> UserPoints:
        user_points = self.get_by_user(db, user_id)
        if not user_points:
            user_points = UserPoints(user_id=user_id, accumulated_points=points)
            db.add(user_points)
        else:
            user_points.accumulated_points += points
        db.commit()
        db.refresh(user_points)
        return user_points

    def subtract_points(self, db: Session, user_id: UUID, points: int) -> Optional[UserPoints]:
        user_points = self.get_by_user(db, user_id)
        if not user_points or user_points.accumulated_points < points:
            return None
        user_points.accumulated_points -= points
        db.commit()
        db.refresh(user_points)
        return user_points

    def get_leaderboard(self, db: Session, limit: int = 10, program_id: Optional[UUID] = None) -> List[LeaderboardEntry]:
        query = db.query(
            UserPoints.user_id,
            UserPoints.accumulated_points,
            User.first_names,
            User.last_names,
            User.profile_image_url,
            func.count(UserBadge.id).label("badges_count"),
            func.row_number().over(order_by=desc(UserPoints.accumulated_points)).label("rank")
        ).join(User, UserPoints.user_id == User.id).outerjoin(UserBadge, UserPoints.user_id == UserBadge.user_id).group_by(
            UserPoints.user_id,
            UserPoints.accumulated_points,
            User.first_names,
            User.last_names,
            User.profile_image_url
        ).order_by(desc(UserPoints.accumulated_points))

        if program_id:
            query = query.join(Student, User.id == Student.user_id).filter(Student.program_id == program_id)

        results = query.limit(limit).all()
        return [
            LeaderboardEntry(
                rank=r.rank,
                user_id=r.user_id,
                user_name=f"{r.first_names} {r.last_names}",
                points=r.accumulated_points,
                badges_count=r.badges_count,
                profile_image_url=r.profile_image_url
            ) for r in results
        ]

# ----------------------------
# THEME
# ----------------------------

class CRUDTheme(CRUDBase[Theme, ThemeCreate, ThemeUpdate]):
    def get_custom_themes(self, db: Session) -> List[Theme]:
        return db.query(self.model).filter(Theme.is_custom.is_(True)).all()

    def get_default_themes(self, db: Session) -> List[Theme]:
        return db.query(self.model).filter(Theme.is_custom.is_(False)).all()


# ----------------------------
# USER THEME
# ----------------------------
class CRUDUserTheme(CRUDBase[UserTheme, UserThemeCreate, dict]):
    def get_by_user(self, db: Session, user_id: UUID) -> List[UserTheme]:
        return db.query(UserTheme).filter(UserTheme.user_id == user_id).options(joinedload(UserTheme.theme)).all()

    def get_active_theme(self, db: Session, user_id: UUID) -> Optional[UserTheme]:
        return db.query(UserTheme).filter(UserTheme.user_id == user_id).options(joinedload(UserTheme.theme)).order_by(desc(UserTheme.created_at)).first()

    def set_user_theme(self, db: Session, user_id: UUID, theme_id: UUID) -> UserTheme:
        existing = db.query(UserTheme).filter(UserTheme.user_id == user_id, UserTheme.theme_id == theme_id).first()
        if existing:
            return existing
        user_theme = UserTheme(user_id=user_id, theme_id=theme_id)
        db.add(user_theme)
        db.commit()
        db.refresh(user_theme)
        return user_theme

# ----------------------------
# INSTANCIAS
# ----------------------------
badge = CRUDBadge(Badge)
user_badge = CRUDUserBadge(UserBadge)
reward = CRUDReward(Reward)
user_reward = CRUDUserReward(UserReward)
user_points = CRUDUserPoints(UserPoints)
theme = CRUDTheme(Theme)
user_theme = CRUDUserTheme(UserTheme)
