"""
CRUD operations para avatars.
"""

from src.crud.avatar.avatar_asset_crud import crud_avatar_asset, CRUDAvatarAsset
from src.crud.avatar.user_avatar_crud import crud_user_avatar, CRUDUserAvatar

__all__ = [
    "crud_avatar_asset",
    "CRUDAvatarAsset",
    "crud_user_avatar", 
    "CRUDUserAvatar"
]