from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...core.security import get_current_user
from ...models.user import User, UserRole, Student
from ...schemas.gamification import (
    Badge, BadgeCreate, BadgeUpdate,
    UserBadge, Reward, RewardCreate, UserReward,
    UserPoints, PointsTransaction,
    Theme, ThemeCreate, UserTheme,
    UserGameProfile, Leaderboard, GamificationStats,
    UserAchievementProgress
)
from ...services.gamification_service import GamificationService
from ...services.notification_service import NotificationService
from ...crud import gamification as crud

router = APIRouter()


# =============================
# DEPENDENCIAS DE ROLES
# =============================

async def get_current_admin_or_coordinator(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and coordinators can perform this action"
        )
    return current_user


async def get_current_student(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Student:
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can perform this action"
        )
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student


# =============================
# BADGES
# =============================

@router.post("/badges", response_model=Badge, status_code=status.HTTP_201_CREATED)
async def create_badge(
    badge_in: BadgeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_coordinator)
):
    """Crear nueva insignia"""
    return crud.badge.create(db=db, obj_in=badge_in)


@router.get("/badges", response_model=List[Badge])
async def read_badges(
    skip: int = 0,
    limit: int = 100,
    badge_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener todas las insignias"""
    if badge_type:
        return crud.badge.get_by_type(db=db, badge_type=badge_type)
    return crud.badge.get_multi(db=db, skip=skip, limit=limit)


@router.get("/badges/{badge_id}", response_model=Badge)
async def read_badge(
    badge_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener insignia específica"""
    badge = crud.badge.get(db=db, id=badge_id)
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    return badge


@router.put("/badges/{badge_id}", response_model=Badge)
async def update_badge(
    badge_id: UUID,
    badge_in: BadgeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_coordinator)
):
    """Actualizar insignia"""
    db_badge = crud.badge.get(db=db, id=badge_id)
    if not db_badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    return crud.badge.update(db=db, db_obj=db_badge, obj_in=badge_in)


@router.delete("/badges/{badge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_badge(
    badge_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_coordinator)
):
    """Eliminar insignia"""
    badge = crud.badge.get(db=db, id=badge_id)
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    crud.badge.remove(db=db, id=badge_id)


@router.post("/badges/{badge_id}/grant/{user_id}", response_model=UserBadge)
async def grant_badge_to_user(
    badge_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_coordinator)
):
    """Otorgar insignia a un usuario"""
    user_badge = crud.user_badge.grant_badge(db=db, user_id=user_id, badge_id=badge_id, granted_by=current_user.id)
    if not user_badge:
        raise HTTPException(status_code=400, detail="Badge already granted or unique and assigned")
    await NotificationService.notify_badge_earned(db, user_id, badge_id)
    return user_badge


@router.get("/users/{user_id}/badges", response_model=List[UserBadge])
async def get_user_badges(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener insignias de un usuario"""
    if current_user.role == UserRole.STUDENT and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.user_badge.get_by_user(db=db, user_id=user_id)


@router.get("/my-badges", response_model=List[UserBadge])
async def get_my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener mis insignias"""
    return crud.user_badge.get_by_user(db=db, user_id=current_user.id)


# =============================
# REWARDS
# =============================

@router.post("/rewards", response_model=Reward, status_code=status.HTTP_201_CREATED)
async def create_reward(
    reward_in: RewardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_coordinator)
):
    """Crear nueva recompensa"""
    return crud.reward.create(db=db, obj_in=reward_in)


@router.get("/rewards", response_model=List[Reward])
async def read_rewards(
    skip: int = 0,
    limit: int = 100,
    affordable_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener recompensas disponibles"""
    if affordable_only:
        return crud.reward.get_affordable_for_user(db=db, user_id=current_user.id)
    return crud.reward.get_multi(db=db, skip=skip, limit=limit)


@router.post("/rewards/{reward_id}/redeem", response_model=UserReward)
async def redeem_reward(
    reward_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Canjear recompensa"""
    user_reward, message = crud.user_reward.redeem_reward(db=db, user_id=current_user.id, reward_id=reward_id)
    if not user_reward:
        raise HTTPException(status_code=400, detail=message)
    await NotificationService.notify_reward_redeemed(db, current_user.id, reward_id)
    return user_reward


@router.get("/my-rewards", response_model=List[UserReward])
async def get_my_rewards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener mis recompensas canjeadas"""
    return crud.user_reward.get_by_user(db=db, user_id=current_user.id)


# =============================
# PUNTOS
# =============================

@router.get("/points/my", response_model=UserPoints)
async def get_my_points(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener mis puntos"""
    user_points = crud.user_points.get_by_user(db=db, user_id=current_user.id)
    if not user_points:
        user_points = crud.user_points.create(db=db, obj_in={"user_id": current_user.id, "accumulated_points": 0})
    return user_points


@router.post("/points/add", response_model=UserPoints)
async def add_points_to_user(
    transaction: PointsTransaction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_coordinator)
):
    """Agregar puntos a un usuario manualmente"""
    user_points = crud.user_points.add_points(db=db, user_id=transaction.user_id, points=transaction.points, reason=transaction.reason)
    await NotificationService.notify_points_earned(db, transaction.user_id, transaction.points)
    return user_points


@router.get("/leaderboard", response_model=Leaderboard)
async def get_leaderboard(
    limit: int = 10,
    program_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener ranking de usuarios"""
    entries = crud.user_points.get_leaderboard(db=db, limit=limit, program_id=program_id)
    current_user_rank = None
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student:
            current_user_rank = crud.user_points.get_user_rank(db=db, user_id=current_user.id, program_id=student.program_id)
    return Leaderboard(entries=entries, total_users=len(entries), current_user_rank=current_user_rank)


# =============================
# THEMES
# =============================

@router.post("/themes", response_model=Theme, status_code=status.HTTP_201_CREATED)
async def create_theme(theme_in: ThemeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_or_coordinator)):
    """Crear nuevo tema"""
    return crud.theme.create(db=db, obj_in=theme_in)


@router.get("/themes", response_model=List[Theme])
async def read_themes(custom_only: bool = False, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Obtener temas disponibles"""
    if custom_only:
        return crud.theme.get_custom_themes(db=db)
    return crud.theme.get_multi(db=db)


@router.post("/themes/{theme_id}/select", response_model=UserTheme)
async def select_theme(theme_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Seleccionar tema para el usuario"""
    theme = crud.theme.get(db=db, id=theme_id)
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    return crud.user_theme.set_user_theme(db=db, user_id=current_user.id, theme_id=theme_id)


@router.get("/my-theme", response_model=Optional[UserTheme])
async def get_my_active_theme(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Obtener mi tema activo"""
    return crud.user_theme.get_active_theme(db=db, user_id=current_user.id)


# =============================
# PERFIL GAMIFICACIÓN
# =============================

@router.get("/profile", response_model=UserGameProfile)
async def get_game_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await GamificationService.get_user_game_profile(db, current_user.id)


@router.get("/profile/{user_id}", response_model=UserGameProfile)
async def get_user_game_profile(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.COORDINATOR] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await GamificationService.get_user_game_profile(db, user_id)


@router.get("/achievements/progress", response_model=List[UserAchievementProgress])
async def get_achievement_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await GamificationService.get_user_achievement_progress(db, current_user.id)


# =============================
# ADMIN
# =============================

@router.post("/check-achievements/{user_id}")
async def check_user_achievements(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_or_coordinator)):
    earned_badges = await GamificationService.check_and_award_achievements(db, user_id)
    return {"message": f"Checked achievements for user {user_id}", "earned_badges": len(earned_badges), "badge_ids": earned_badges}


@router.get("/stats", response_model=GamificationStats)
async def get_gamification_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_or_coordinator)):
    return await GamificationService.get_gamification_stats(db)


@router.post("/reset-user-progress/{user_id}")
async def reset_user_progress(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_or_coordinator)):
    success = await GamificationService.reset_user_progress(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"Progress reset for user {user_id}"}


# =============================
# HISTORIAL DE PUNTOS
# =============================

@router.get("/points/history", response_model=List[PointsTransaction])
async def get_points_history(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Pendiente de implementación"""
    return []


@router.get("/points/transactions/{user_id}", response_model=List[PointsTransaction])
async def get_user_points_history(user_id: UUID, skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_or_coordinator)):
    """Pendiente de implementación"""
    return []
