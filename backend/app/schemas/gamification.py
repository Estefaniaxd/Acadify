from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID

from ..models.gamification import BadgeType

# ----------------------------
# BADGES
# ----------------------------
class BadgeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    badge_type: BadgeType = BadgeType.MANUAL
    is_unique: bool = False

class BadgeCreate(BadgeBase):
    pass

class BadgeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    badge_type: Optional[BadgeType] = None
    is_unique: Optional[bool] = None

class BadgeInDB(BadgeBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class Badge(BadgeInDB):
    pass

# ----------------------------
# USER BADGES
# ----------------------------
class UserBadgeCreate(BaseModel):
    user_id: UUID
    badge_id: UUID
    granted_by: Optional[UUID] = None

class UserBadgeInDB(BaseModel):
    id: UUID
    user_id: UUID
    badge_id: UUID
    granted_by: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserBadge(UserBadgeInDB):
    badge: Optional[Badge] = None

class UserBadgeWithDetails(UserBadge):
    user_name: str
    granter_name: Optional[str] = None

# ----------------------------
# REWARDS
# ----------------------------
class RewardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    points_cost: int = Field(..., ge=0)

class RewardCreate(RewardBase):
    pass

class RewardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    points_cost: Optional[int] = Field(None, ge=0)

class RewardInDB(RewardBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class Reward(RewardInDB):
    pass

# ----------------------------
# USER REWARDS
# ----------------------------
class UserRewardBase(BaseModel):
    redemption_date: datetime

class UserRewardCreate(UserRewardBase):
    user_id: UUID
    reward_id: UUID

class UserRewardInDB(UserRewardBase):
    id: UUID
    user_id: UUID
    reward_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserReward(UserRewardInDB):
    reward: Optional[Reward] = None

# ----------------------------
# USER POINTS
# ----------------------------
class UserPointsBase(BaseModel):
    accumulated_points: int = Field(default=0, ge=0)

class UserPointsCreate(UserPointsBase):
    user_id: UUID

class UserPointsUpdate(BaseModel):
    accumulated_points: Optional[int] = Field(None, ge=0)

class UserPointsInDB(UserPointsBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserPoints(UserPointsInDB):
    pass

# ----------------------------
# THEMES
# ----------------------------
class ThemeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    emoji: str = Field(..., min_length=1, max_length=8)
    is_custom: bool = False

class ThemeCreate(ThemeBase):
    pass

class ThemeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    emoji: Optional[str] = Field(None, min_length=1, max_length=8)
    is_custom: Optional[bool] = None

class ThemeInDB(ThemeBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class Theme(ThemeInDB):
    pass

# ----------------------------
# USER THEMES
# ----------------------------
class UserThemeCreate(BaseModel):
    user_id: UUID
    theme_id: UUID

class UserThemeInDB(BaseModel):
    id: UUID
    user_id: UUID
    theme_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserTheme(UserThemeInDB):
    theme: Optional[Theme] = None

# ----------------------------
# GAMIFICATION ADVANCED
# ----------------------------
class PointsTransaction(BaseModel):
    user_id: UUID
    points: int
    reason: str
    transaction_type: Literal["earned", "spent"]
    reference_id: Optional[UUID] = None

class UserGameProfile(BaseModel):
    user_id: UUID
    user_name: str
    total_points: int
    badges: List[Badge]
    current_theme: Optional[Theme] = None
    rank_position: Optional[int] = None
    total_assignments_submitted: int
    average_grade: Optional[float] = None

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    user_name: str
    points: int
    badges_count: int
    profile_image_url: Optional[str] = None

class Leaderboard(BaseModel):
    entries: List[LeaderboardEntry]
    total_users: int
    current_user_rank: Optional[int] = None

# ----------------------------
# ACHIEVEMENTS
# ----------------------------
class AchievementRule(BaseModel):
    badge_id: UUID
    rule_type: Literal["assignment_count", "grade_average", "streak"]
    rule_value: int
    description: str

class UserAchievementProgress(BaseModel):
    badge_id: UUID
    badge_name: str
    badge_description: str
    badge_image_url: Optional[str]
    current_progress: int
    required_progress: int
    progress_percentage: float
    is_completed: bool

# ----------------------------
# GAMIFICATION STATS
# ----------------------------
class GamificationStats(BaseModel):
    total_badges: int
    unique_badges: int
    total_points_distributed: int
    total_rewards_redeemed: int
    most_popular_badge: Optional[str] = None
    top_user_points: int
    average_user_points: float
