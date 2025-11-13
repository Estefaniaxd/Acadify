"""CRUD operations para avatars."""

from src.crud.avatar.avatar_asset_crud import CRUDAvatarAsset, crud_avatar_asset
from src.crud.avatar.user_avatar_crud import CRUDUserAvatar, crud_user_avatar


__all__ = ["CRUDAvatarAsset", "CRUDUserAvatar", "crud_avatar_asset", "crud_user_avatar"]
