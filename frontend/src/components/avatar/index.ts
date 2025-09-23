// Exportaciones principales de componentes de avatar
export { default as AvatarStudio } from './AvatarStudio';
export { default as SimpleAvatar } from './SimpleAvatar';
export { default as PublicAvatarGallery } from './PublicAvatarGallery';
export { SaveAvatarDialog } from './SaveAvatarDialog';
export { AvatarGallery } from './AvatarGallery';

// Exportaciones de hooks
export { useAvatarEditor, useUserAvatars } from './useAvatar';
export type { UseAvatarEditorReturn, UseUserAvatarsReturn } from './useAvatar';

// Exportaciones de API y tipos
export { avatarAPI } from './avatarAPI';
export type { 
  LayerItem, 
  ManifestResponse, 
  AssetInfo,
  PreviewResponse,
  UserAvatar,
  UserAvatarListResponse
} from './avatarAPI';