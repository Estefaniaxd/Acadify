from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Integer, DateTime, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
import enum

# ----------------------------
# ENUMS
# ----------------------------
class BadgeType(enum.Enum):
    """Tipos de insignia"""
    OBJECTIVE = "objective"
    GRADE = "grade"
    STREAK = "streak"
    MANUAL = "manual"

# ----------------------------
# BADGES
# ----------------------------
class Badge(BaseModel):
    """Insignia o medalla"""
    __tablename__ = "badges"
    
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    image_url = Column(Text, unique=True)
    badge_type = Column(SQLEnum(BadgeType), default=BadgeType.MANUAL, nullable=False)
    is_unique = Column(Boolean, nullable=False, default=False)
    
    # Relaciones
    user_badges = relationship("UserBadge", back_populates="badge")

# ----------------------------
# USER BADGES
# ----------------------------
class UserBadge(BaseModel):
    """Insignias asignadas a usuario"""
    __tablename__ = "user_badges"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relaciones
    user = relationship("User", back_populates="user_badges", foreign_keys=[user_id])
    badge = relationship("Badge", back_populates="user_badges")
    granted_by_user = relationship("User", foreign_keys=[granted_by])

    __table_args__ = (
        UniqueConstraint('user_id', 'badge_id', name='uix_user_badge'),
    )

# ----------------------------
# REWARDS
# ----------------------------
class Reward(BaseModel):
    """Recompensa canjeable"""
    __tablename__ = "rewards"
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    points_cost = Column(Integer, nullable=False)
    
    # Relaciones
    user_rewards = relationship("UserReward", back_populates="reward")

# ----------------------------
# USER REWARDS
# ----------------------------
class UserReward(BaseModel):
    """Recompensas de usuario"""
    __tablename__ = "user_rewards"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reward_id = Column(UUID(as_uuid=True), ForeignKey("rewards.id", ondelete="CASCADE"), nullable=False)
    redemption_date = Column(DateTime(timezone=True), nullable=False)
    
    # Relaciones
    user = relationship("User", back_populates="user_rewards")
    reward = relationship("Reward", back_populates="user_rewards")

# ----------------------------
# USER POINTS
# ----------------------------
class UserPoints(BaseModel):
    """Puntos de usuario"""
    __tablename__ = "user_points"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    accumulated_points = Column(Integer, default=0, nullable=False)
    
    user = relationship("User", back_populates="user_points")

# ----------------------------
# THEMES
# ----------------------------
class Theme(BaseModel):
    """Tema de interfaz"""
    __tablename__ = "themes"
    
    name = Column(String(100), nullable=False, unique=True)
    emoji = Column(String(8), nullable=False)
    is_custom = Column(Boolean, nullable=False, default=False)
    
    user_themes = relationship("UserTheme", back_populates="theme")

# ----------------------------
# USER THEMES
# ----------------------------
class UserTheme(BaseModel):
    """Tema asignado a usuario"""
    __tablename__ = "user_themes"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    theme_id = Column(UUID(as_uuid=True), ForeignKey("themes.id", ondelete="CASCADE"), nullable=False)
    
    user = relationship("User", back_populates="user_themes")
    theme = relationship("Theme", back_populates="user_themes")

    __table_args__ = (
        UniqueConstraint('user_id', 'theme_id', name='uix_user_theme'),
    )

StudentBadge = UserBadge
LeaderboardEntry = UserPoints
