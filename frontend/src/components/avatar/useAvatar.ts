// Hook personalizado para manejar avatars
import { useState, useEffect, useCallback } from 'react';
import { avatarAPI, type LayerItem, type ManifestResponse, type UserAvatar } from './avatarAPI';
import { formatApiError } from '../../utils/api';

export interface UseAvatarEditorReturn {
  // Estado del editor
  selectedLayers: LayerItem[];
  previewUrl: string | null;
  isGeneratingPreview: boolean;
  isSaving: boolean;
  
  // Estado del manifest
  manifest: ManifestResponse | null;
  isLoadingManifest: boolean;
  
  // Errores
  error: string | null;
  
  // Acciones
  setLayer: (category: string, file: string) => void;
  removeLayer: (category: string) => void;
  clearAllLayers: () => void;
  generatePreview: () => Promise<void>;
  saveAvatar: (name: string, isActive?: boolean, isPublic?: boolean) => Promise<UserAvatar>;
  
  // Helpers
  hasLayer: (category: string) => boolean;
  getLayer: (category: string) => LayerItem | undefined;
  clearError: () => void;
}

export function useAvatarEditor(): UseAvatarEditorReturn {
  // Estado principal
  const [selectedLayers, setSelectedLayers] = useState<LayerItem[]>([]);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [manifest, setManifest] = useState<ManifestResponse | null>(null);
  
  // Estados de carga
  const [isGeneratingPreview, setIsGeneratingPreview] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingManifest, setIsLoadingManifest] = useState(true);
  
  // Error
  const [error, setError] = useState<string | null>(null);

  // Cargar manifest al inicializar
  useEffect(() => {
    loadManifest();
  }, []);

  // Generar preview automáticamente cuando cambien las capas
  useEffect(() => {
    if (selectedLayers.length > 0) {
      generatePreview();
    } else {
      setPreviewUrl(null);
    }
  }, [selectedLayers]);

  const loadManifest = async () => {
    try {
      setIsLoadingManifest(true);
      setError(null);
      const manifestData = await avatarAPI.getAssetsManifest();
      setManifest(manifestData);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setIsLoadingManifest(false);
    }
  };

  const setLayer = useCallback((category: string, file: string) => {
    setSelectedLayers(prev => {
      // Remover capa existente de esta categoría si la hay
      const filtered = prev.filter(layer => layer.category !== category);
      // Añadir nueva capa
      return [...filtered, { category, file }];
    });
  }, []);

  const removeLayer = useCallback((category: string) => {
    setSelectedLayers(prev => prev.filter(layer => layer.category !== category));
  }, []);

  const clearAllLayers = useCallback(() => {
    setSelectedLayers([]);
  }, []);

  const generatePreview = useCallback(async () => {
    if (selectedLayers.length === 0) {
      setPreviewUrl(null);
      return;
    }

    try {
      setIsGeneratingPreview(true);
      setError(null);
      
      const previewData = await avatarAPI.generatePreview(selectedLayers);
      setPreviewUrl(previewData.preview_url);
    } catch (err) {
      setError(formatApiError(err));
      setPreviewUrl(null);
    } finally {
      setIsGeneratingPreview(false);
    }
  }, [selectedLayers]);

  const saveAvatar = useCallback(async (
    name: string, 
    isActive: boolean = false,
    isPublic: boolean = true
  ): Promise<UserAvatar> => {
    if (selectedLayers.length === 0) {
      throw new Error('No se han seleccionado capas para el avatar');
    }

    if (!name.trim()) {
      throw new Error('El nombre del avatar es requerido');
    }

    try {
      setIsSaving(true);
      setError(null);
      
      const avatar = await avatarAPI.saveAvatar(name, selectedLayers, isActive, isPublic);
      return avatar;
    } catch (err) {
      const errorMsg = formatApiError(err);
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setIsSaving(false);
    }
  }, [selectedLayers]);

  const hasLayer = useCallback((category: string): boolean => {
    return selectedLayers.some(layer => layer.category === category);
  }, [selectedLayers]);

  const getLayer = useCallback((category: string): LayerItem | undefined => {
    return selectedLayers.find(layer => layer.category === category);
  }, [selectedLayers]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // Estado
    selectedLayers,
    previewUrl,
    isGeneratingPreview,
    isSaving,
    manifest,
    isLoadingManifest,
    error,
    
    // Acciones
    setLayer,
    removeLayer,
    clearAllLayers,
    generatePreview,
    saveAvatar,
    
    // Helpers
    hasLayer,
    getLayer,
    clearError,
  };
}

export interface UseUserAvatarsReturn {
  avatars: UserAvatar[];
  total: number;
  hasActive: boolean;
  activeAvatarId: string | null;
  isLoading: boolean;
  error: string | null;
  
  loadAvatars: () => Promise<void>;
  setActiveAvatar: (avatarId: string) => Promise<void>;
  deleteAvatar: (avatarId: string) => Promise<void>;
  toggleAvatarPrivacy: (avatarId: string, isPublic: boolean) => Promise<void>;
  clearError: () => void;
}

export function useUserAvatars(): UseUserAvatarsReturn {
  const [avatars, setAvatars] = useState<UserAvatar[]>([]);
  const [total, setTotal] = useState(0);
  const [hasActive, setHasActive] = useState(false);
  const [activeAvatarId, setActiveAvatarId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAvatars();
  }, []);

  const loadAvatars = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const data = await avatarAPI.getMyAvatars();
      setAvatars(data.avatars);
      setTotal(data.total);
      setHasActive(data.has_active);
      setActiveAvatarId(data.active_avatar_id || null);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const setActiveAvatar = async (avatarId: string) => {
    try {
      setError(null);
      await avatarAPI.setActiveAvatar(avatarId);
      
      // Actualizar estado local
      setAvatars(prev => 
        prev.map(avatar => ({
          ...avatar,
          is_active: avatar.id === avatarId
        }))
      );
      setActiveAvatarId(avatarId);
      setHasActive(true);
    } catch (err) {
      setError(formatApiError(err));
      throw err;
    }
  };

  const deleteAvatar = async (avatarId: string) => {
    try {
      setError(null);
      await avatarAPI.deleteAvatar(avatarId);
      
      // Actualizar estado local
      const deletedAvatar = avatars.find(a => a.id === avatarId);
      setAvatars(prev => prev.filter(avatar => avatar.id !== avatarId));
      setTotal(prev => prev - 1);
      
      // Si se eliminó el avatar activo, actualizar estado
      if (deletedAvatar?.is_active) {
        setHasActive(false);
        setActiveAvatarId(null);
      }
    } catch (err) {
      setError(formatApiError(err));
      throw err;
    }
  };

  const toggleAvatarPrivacy = async (avatarId: string, isPublic: boolean) => {
    try {
      setError(null);
      await avatarAPI.toggleAvatarPrivacy(avatarId, isPublic);
      
      // Actualizar estado local
      setAvatars(prev => 
        prev.map(avatar => 
          avatar.id === avatarId 
            ? { ...avatar, is_public: isPublic }
            : avatar
        )
      );
    } catch (err) {
      setError(formatApiError(err));
      throw err;
    }
  };

  const clearError = () => {
    setError(null);
  };

  return {
    avatars,
    total,
    hasActive,
    activeAvatarId,
    isLoading,
    error,
    loadAvatars,
    setActiveAvatar,
    deleteAvatar,
    toggleAvatarPrivacy,
    clearError,
  };
}