"""Tests comprehensivos del sistema de avatares (gamificación)."""

import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from src.models.users.usuario import Usuario
from src.models.avatar.user_avatar import UserAvatar
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.crud.avatar.user_avatar_crud import crud_user_avatar
from src.services.avatar_service import avatar_service
from src.schemas.avatar.avatar_schemas import SaveAvatarRequest
from src.crud.gamification.historial_puntos import asignar_puntos, descontar_puntos
from src.schemas.gamification.historial_puntos import AsignarPuntosRequest, DescontarPuntosRequest


# ==================== TESTS DE CREACIÓN DE AVATARES ====================


def test_save_avatar_basico(db_session: Session, estudiante_1: Usuario):
    """Test guardar avatar básico."""
    avatar = crud_user_avatar.create_avatar(
        db=db_session,
        user_id=estudiante_1.usuario_id,
        name="Mi Primer Avatar",
        base_gender="male",
        layers=[
            {"category": "hair", "file": "hair/short_black.png"},
            {"category": "clothes", "file": "clothes/casual_shirt.png"}
        ],
        image_url="/static/avatars/test.png",
        layers_hash="test_hash",
        is_active=True,
        is_public=False
    )
    
    assert avatar is not None
    assert avatar.name == "Mi Primer Avatar"
    assert avatar.base_gender == "male"
    assert avatar.user_id == estudiante_1.usuario_id
    assert avatar.is_active is True


def test_save_avatar_female(db_session: Session, estudiante_2: Usuario):
    """Test guardar avatar femenino."""
    avatar = crud_user_avatar.create_avatar(
        db=db_session,
        user_id=estudiante_2.usuario_id,
        name="Avatar Femenino",
        base_gender="female",
        layers=[
            {"category": "hair", "file": "hair/long_blonde.png"},
            {"category": "clothes", "file": "clothes/dress.png"}
        ],
        image_url="/static/avatars/female.png",
        layers_hash="female_hash",
        is_active=False,
        is_public=True
    )
    
    assert avatar is not None
    assert avatar.base_gender == "female"
    assert avatar.is_public is True


def test_save_multiple_avatars(db_session: Session, estudiante_1: Usuario):
    """Test usuario puede tener múltiples avatares."""
    for i in range(3):
        crud_user_avatar.create_avatar(
            db=db_session,
            user_id=estudiante_1.usuario_id,
            name=f"Avatar {i + 1}",
            base_gender="male",
            layers=[{"category": "hair", "file": f"hair/style_{i}.png"}],
            image_url=f"/static/avatars/avatar_{i}.png",
            layers_hash=f"hash_{i}",
            is_active=(i == 0),  # Solo el primero activo
            is_public=False
        )
    
    avatars = crud_user_avatar.get_by_user(db_session, user_id=estudiante_1.usuario_id)
    assert len(avatars) >= 3


# ==================== TESTS DE ACTIVACIÓN DE AVATARES ====================


def test_set_active_avatar(
    db_session: Session,
    estudiante_1: Usuario,
    avatar_basico: UserAvatar,
    avatar_premium: UserAvatar,
):
    """Test cambiar avatar activo."""
    # Activar el avatar premium
    updated_avatar = crud_user_avatar.set_active_avatar(
        db_session,
        user_id=estudiante_1.usuario_id,
        avatar_id=avatar_premium.id
    )
    
    assert updated_avatar is not None
    assert updated_avatar.is_active is True
    
    # Verificar que el anterior se desactivó
    db_session.refresh(avatar_basico)
    assert avatar_basico.is_active is False


def test_only_one_active_avatar(db_session: Session, estudiante_1: Usuario):
    """Test solo un avatar puede estar activo a la vez."""
    # Crear 3 avatares
    avatars = []
    for i in range(3):
        avatar = crud_user_avatar.create_avatar(
            db=db_session,
            user_id=estudiante_1.usuario_id,
            name=f"Avatar {i}",
            base_gender="male",
            layers=[{"category": "hair", "file": f"hair/style_{i}.png"}],
            image_url=f"/static/avatars/{i}.png",
            layers_hash=f"hash{i}",
            is_active=False,
            is_public=False
        )
        avatars.append(avatar)
    
    # Activar el segundo
    crud_user_avatar.set_active_avatar(
        db_session,
        user_id=estudiante_1.usuario_id,
        avatar_id=avatars[1].id
    )
    
    # Verificar que solo uno está activo
    all_avatars = crud_user_avatar.get_by_user(db_session, user_id=estudiante_1.usuario_id)
    active_count = sum(1 for a in all_avatars if a.is_active)
    assert active_count == 1


def test_get_active_avatar(
    db_session: Session,
    estudiante_1: Usuario,
    avatar_basico: UserAvatar,
):
    """Test obtener avatar activo del usuario."""
    active = crud_user_avatar.get_active_avatar(db_session, user_id=estudiante_1.usuario_id)
    
    assert active is not None
    assert active.id == avatar_basico.id
    assert active.is_active is True


def test_get_active_avatar_sin_avatar_activo(db_session: Session, estudiante_2: Usuario):
    """Test obtener avatar activo cuando no hay ninguno."""
    active = crud_user_avatar.get_active_avatar(db_session, user_id=estudiante_2.usuario_id)
    
    assert active is None


# ==================== TESTS DE PRIVACIDAD ====================


def test_update_avatar_privacy_to_public(
    db_session: Session,
    estudiante_1: Usuario,
    avatar_basico: UserAvatar,
):
    """Test hacer avatar público."""
    updated = crud_user_avatar.update_avatar_privacy(
        db_session,
        user_id=estudiante_1.usuario_id,
        avatar_id=avatar_basico.id,
        is_public=True
    )
    
    assert updated is not None
    assert updated.is_public is True


def test_update_avatar_privacy_to_private(
    db_session: Session,
    estudiante_1: Usuario,
):
    """Test hacer avatar privado."""
    # Crear avatar público
    avatar = crud_user_avatar.create_avatar(
        db=db_session,
        user_id=estudiante_1.usuario_id,
        name="Avatar Público",
        base_gender="male",
        layers=[{"category": "hair", "file": "hair/basic.png"}],
        image_url="/static/avatars/public.png",
        layers_hash="public_hash",
        is_active=False,
        is_public=True
    )
    
    # Hacerlo privado
    updated = crud_user_avatar.update_avatar_privacy(
        db_session,
        user_id=estudiante_1.usuario_id,
        avatar_id=avatar.id,
        is_public=False
    )
    
    assert updated.is_public is False


# ==================== TESTS DE ELIMINACIÓN ====================


def test_delete_avatar(
    db_session: Session,
    estudiante_1: Usuario,
    avatar_premium: UserAvatar,
):
    """Test eliminar avatar."""
    deleted = crud_user_avatar.delete_user_avatar(
        db_session,
        user_id=estudiante_1.usuario_id,
        avatar_id=avatar_premium.id
    )
    
    assert deleted is not None
    
    # Verificar que ya no existe
    avatar = crud_user_avatar.get(db_session, avatar_premium.id)
    assert avatar is None


def test_delete_avatar_no_puede_eliminar_ajeno(
    db_session: Session,
    estudiante_1: Usuario,
    estudiante_2: Usuario,
    avatar_basico: UserAvatar,
):
    """Test no se puede eliminar avatar de otro usuario."""
    # avatar_basico pertenece a estudiante_1
    deleted = crud_user_avatar.delete_user_avatar(
        db_session,
        user_id=estudiante_2.usuario_id,  # Intentar eliminar como otro usuario
        avatar_id=avatar_basico.id
    )
    
    assert deleted is None
    
    # Verificar que aún existe
    avatar = crud_user_avatar.get(db_session, avatar_basico.id)
    assert avatar is not None


# ==================== TESTS DE ESTADÍSTICAS ====================


def test_get_user_stats_sin_avatares(db_session: Session, estudiante_1: Usuario):
    """Test estadísticas de usuario sin avatares."""
    stats = crud_user_avatar.get_user_stats(db_session, user_id=estudiante_1.usuario_id)
    
    assert stats["total_avatars"] >= 0
    assert stats["public_avatars"] >= 0
    assert stats["private_avatars"] >= 0
    assert stats["total_avatars"] == stats["public_avatars"] + stats["private_avatars"]


def test_get_user_stats_con_avatares(
    db_session: Session,
    estudiante_1: Usuario,
    avatar_basico: UserAvatar,
    avatar_premium: UserAvatar,
):
    """Test estadísticas de usuario con avatares."""
    stats = crud_user_avatar.get_user_stats(db_session, user_id=estudiante_1.usuario_id)
    
    assert stats["total_avatars"] >= 2
    assert stats["has_active_avatar"] is True
    assert stats["active_avatar_id"] == avatar_basico.id  # avatar_basico es el activo


def test_get_user_stats_calculo_correcto(db_session: Session, estudiante_1: Usuario):
    """Test cálculo correcto de estadísticas."""
    # Crear 3 públicos y 2 privados
    for i in range(5):
        crud_user_avatar.create_avatar(
            db=db_session,
            user_id=estudiante_1.usuario_id,
            name=f"Avatar {i}",
            base_gender="male",
            layers=[{"category": "hair", "file": f"hair/style_{i}.png"}],
            image_url=f"/static/avatars/{i}.png",
            layers_hash=f"hash{i}",
            is_active=(i == 0),
            is_public=(i < 3)  # Primeros 3 públicos
        )
    
    stats = crud_user_avatar.get_user_stats(db_session, user_id=estudiante_1.usuario_id)
    
    assert stats["total_avatars"] >= 5
    assert stats["public_avatars"] >= 3
    assert stats["private_avatars"] >= 2


# ==================== TESTS DE INTEGRACIÓN CON PUNTOS ====================


def test_desbloquear_avatar_premium_con_puntos(
    db_session: Session,
    estudiante_1: Usuario,
):
    """Test desbloquear avatar premium usando puntos."""
    # 1. Usuario gana puntos
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=100,
            motivo="Completar tareas"
        )
    )
    
    # 2. Usuario gasta puntos para desbloquear avatar premium
    descontar_puntos(
        db_session,
        DescontarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=50,
            motivo="Desbloquear avatar premium"
        )
    )
    
    # 3. Crear avatar premium
    avatar = crud_user_avatar.create_avatar(
        db=db_session,
        user_id=estudiante_1.usuario_id,
        name="Avatar Premium Desbloqueado",
        base_gender="male",
        layers=[
            {"category": "hair", "file": "hair/premium_style.png"},
            {"category": "clothes", "file": "clothes/premium_suit.png"}
        ],
        image_url="/static/avatars/premium.png",
        layers_hash="premium_hash",
        is_active=True,
        is_public=False
    )
    
    assert avatar is not None
    assert "Premium" in avatar.name


def test_no_puede_desbloquear_sin_puntos(
    db_session: Session,
    estudiante_1: Usuario,
):
    """Test no se puede desbloquear avatar sin puntos suficientes."""
    # Usuario no tiene puntos
    
    # Intentar descontar puntos debería fallar
    with pytest.raises(ValueError, match="suficientes puntos"):
        descontar_puntos(
            db_session,
            DescontarPuntosRequest(
                usuario_id=estudiante_1.usuario_id,
                puntos=50,
                motivo="Intento de desbloqueo"
            )
        )


# ==================== TESTS DE BÚSQUEDA Y FILTRADO ====================


def test_get_avatars_by_user(
    db_session: Session,
    estudiante_1: Usuario,
    avatar_basico: UserAvatar,
    avatar_premium: UserAvatar,
):
    """Test obtener todos los avatares de un usuario."""
    avatars = crud_user_avatar.get_by_user(
        db_session,
        user_id=estudiante_1.usuario_id
    )
    
    assert len(avatars) >= 2
    assert all(a.user_id == estudiante_1.usuario_id for a in avatars)


def test_get_avatars_paginacion(db_session: Session, estudiante_1: Usuario):
    """Test paginación de avatares."""
    # Crear 10 avatares
    for i in range(10):
        crud_user_avatar.create_avatar(
            db=db_session,
            user_id=estudiante_1.usuario_id,
            name=f"Avatar {i}",
            base_gender="male",
            layers=[{"category": "hair", "file": f"hair/style_{i}.png"}],
            image_url=f"/static/avatars/{i}.png",
            layers_hash=f"hash{i}",
            is_active=False,
            is_public=False
        )
    
    # Primera página
    page1 = crud_user_avatar.get_by_user(
        db_session,
        user_id=estudiante_1.usuario_id,
        skip=0,
        limit=5
    )
    
    # Segunda página
    page2 = crud_user_avatar.get_by_user(
        db_session,
        user_id=estudiante_1.usuario_id,
        skip=5,
        limit=5
    )
    
    assert len(page1) == 5
    assert len(page2) >= 5
    assert page1[0].id != page2[0].id


def test_get_public_avatars(db_session: Session, estudiante_1: Usuario, estudiante_2: Usuario):
    """Test obtener solo avatares públicos."""
    # Crear avatares públicos y privados
    for is_public in [True, False, True]:
        crud_user_avatar.create_avatar(
            db=db_session,
            user_id=estudiante_1.usuario_id,
            name=f"Avatar {'Público' if is_public else 'Privado'}",
            base_gender="male",
            layers=[{"category": "hair", "file": "hair/basic.png"}],
            image_url="/static/avatars/test.png",
            layers_hash="test_hash",
            is_active=False,
            is_public=is_public
        )
    
    # Obtener todos los avatares del usuario
    all_avatars = crud_user_avatar.get_by_user(db_session, user_id=estudiante_1.usuario_id)
    public_avatars = [a for a in all_avatars if a.is_public]
    
    assert len(public_avatars) >= 2


# ==================== TESTS DE ACTUALIZACIÓN ====================


def test_update_avatar_name(
    db_session: Session,
    estudiante_1: Usuario,
    avatar_basico: UserAvatar,
):
    """Test actualizar nombre de avatar."""
    # Usar update() de CRUDBase directamente
    updated = crud_user_avatar.update(
        db_session,
        db_obj=avatar_basico,
        obj_in={"name": "Nuevo Nombre de Avatar"}
    )
    
    assert updated is not None
    assert updated.name == "Nuevo Nombre de Avatar"


def test_update_avatar_multiple_fields(
    db_session: Session,
    estudiante_1: Usuario,
    avatar_basico: UserAvatar,
):
    """Test actualizar múltiples campos."""
    # Usar update() de CRUDBase directamente
    updated = crud_user_avatar.update(
        db_session,
        db_obj=avatar_basico,
        obj_in={"name": "Avatar Actualizado", "is_public": True}
    )
    
    assert updated.name == "Avatar Actualizado"
    assert updated.is_public is True


# ==================== TESTS DE FLUJO COMPLETO ====================


def test_flujo_completo_avatar_gamification(
    db_session: Session,
    estudiante_1: Usuario,
):
    """Test flujo completo: ganar puntos, desbloquear y crear avatar."""
    # 1. Ganar puntos
    asignar_puntos(
        db_session,
        AsignarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=150,
            motivo="Completar módulo de aprendizaje"
        )
    )
    
    # 2. Gastar puntos para desbloquear avatar
    descontar_puntos(
        db_session,
        DescontarPuntosRequest(
            usuario_id=estudiante_1.usuario_id,
            puntos=75,
            motivo="Desbloquear avatar especial"
        )
    )
    
    # 3. Crear avatar desbloqueado
    avatar = crud_user_avatar.create_avatar(
        db=db_session,
        user_id=estudiante_1.usuario_id,
        name="Avatar Especial",
        base_gender="male",
        layers=[
            {"category": "hair", "file": "hair/special_style.png"},
            {"category": "clothes", "file": "clothes/special_outfit.png"}
        ],
        image_url="/static/avatars/special.png",
        layers_hash="special_hash",
        is_active=True,
        is_public=True
    )
    
    # 4. Verificar avatar creado
    assert avatar is not None
    assert avatar.is_active is True
    assert avatar.is_public is True
    
    # 5. Verificar estadísticas
    stats = crud_user_avatar.get_user_stats(db_session, user_id=estudiante_1.usuario_id)
    assert stats["total_avatars"] >= 1
    assert stats["public_avatars"] >= 1
    assert stats["has_active_avatar"] is True
