// API client para avatars
import { API_BASE_URL } from '../../utils/api';

export interface LayerItem {
  category: string;
  filename: string;
  url: string;
}

export interface AssetInfo {
  id?: string;
  filename: string;
  display_name?: string;
  target_gender: string;
  width?: number;
  height?: number;
  file_size?: number;
  is_normalized?: boolean;
  meta_info?: Record<string, any>;
  url: string; // URL completa del asset
}

export interface ManifestResponse {
  resolution: [number, number];
  categories: Record<string, AssetInfo[]>;
  total_assets: number;
  gender?: string; // Para manifests filtrados por género
}

export interface PreviewResponse {
  preview_url: string;
  layers_hash: string;
  from_cache: boolean;
}

export interface UserAvatar {
  id: string;
  user_id: string;
  name: string;
  base_gender: string;
  layers: LayerItem[];
  image_url: string;
  layers_hash: string;
  is_active: boolean;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserAvatarListResponse {
  avatars: UserAvatar[];
  total: number;
  has_active: boolean;
  active_avatar_id?: string;
}

export class AvatarAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_BASE_URL}/avatar`;
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    // Para endpoints públicos como /assets, no incluir credenciales
    const isPublicEndpoint = endpoint.startsWith('/assets');
    
    // Obtener token de localStorage
    const token = localStorage.getItem('access_token');
    
    // Si no es endpoint público y no hay token, lanzar error específico
    if (!isPublicEndpoint && !token) {
      throw new Error('No estás autenticado. Por favor, inicia sesión primero.');
    }
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        // Agregar Authorization header si hay token y no es endpoint público
        ...(token && !isPublicEndpoint ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers,
      },
    };

    console.log(`🔗 Fetching: ${url}`);
    console.log(`🔧 Public endpoint: ${isPublicEndpoint}`);
    console.log(`🔑 Token exists: ${token ? 'YES' : 'NO'}`);
    console.log(`🔒 Authorization header: ${token && !isPublicEndpoint ? 'SENT' : 'NOT_SENT'}`);
    
    const response = await fetch(url, { ...defaultOptions, ...options });

    console.log(`📊 Response status: ${response.status}`);
    console.log(`📊 Response ok: ${response.ok}`);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        detail: `Network error: ${response.status} ${response.statusText}` 
      }));
      console.error('❌ API Error:', errorData);
      throw new Error(`HTTP ${response.status}: ${JSON.stringify(errorData)}`);
    }

    const data = await response.json();
    console.log('✅ API Success:', { endpoint, dataKeys: Object.keys(data) });
    return data;
  }

  /**
   * Obtiene el manifest de assets disponibles
   */
  async getAssetsManifest(gender?: 'male' | 'female'): Promise<ManifestResponse> {
    const params = gender ? `?gender=${gender}` : '';
    return this.request<ManifestResponse>(`/assets${params}`);
  }

  /**
   * Genera avatar directamente como blob para preview
   */
  async generateAvatar(layers: LayerItem[], baseGender: 'male' | 'female'): Promise<Blob> {
    const url = `${this.baseURL}/generate`;
    
    console.log(`🖼️ Generating avatar with layers:`, layers);
    
    // Convertir el formato de layers
    const requestLayers = layers.map(layer => ({
      category: layer.category,
      file: layer.filename
    }));
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        base_gender: baseGender,
        layers: requestLayers
      }),
    });

    console.log(`📊 Generate response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      console.error('❌ Generate Error:', errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const blob = await response.blob();
    console.log('✅ Avatar generated successfully, blob size:', blob.size);
    return blob;
  }

  /**
   * Guarda avatar permanentemente
   */
  async saveAvatar(
    name: string,
    baseGender: 'male' | 'female',
    layers: LayerItem[],
    isActive: boolean = false,
    isPublic: boolean = true
  ): Promise<UserAvatar> {
    console.log(`💾 Saving avatar with layers:`, layers);
    
    // Verificar que todas las capas tengan filename
    const invalidLayers = layers.filter(layer => !layer.filename);
    if (invalidLayers.length > 0) {
      console.error('❌ Layers without filename:', invalidLayers);
      throw new Error('Some layers are missing filename property');
    }
    
    // Forzar que solo se envíen {category, file} (nunca filename)
    // Limpiar cualquier propiedad extra: solo category y file
    const backendLayers = layers.map(layer => {
      console.log(`📝 Mapping layer:`, layer);
      return {
        category: layer.category,
        file: layer.filename
      };
    });
    
    console.log(`💾 Backend layers format:`, backendLayers);
    
    // Crear query parameters (el backend los espera así)
    const params = new URLSearchParams({
      name: name,
      base_gender: baseGender,
      layers: JSON.stringify(backendLayers),
      is_active: isActive.toString(),
      is_public: isPublic.toString()
    });
    
    const url = `${this.baseURL}/save?${params.toString()}`;
    
    // Obtener token para Authorization header
    const token = localStorage.getItem('access_token');
    console.log('🔑 Token from localStorage:', token ? 'TOKEN_PRESENT' : 'NO_TOKEN');
    console.log('🔑 Token preview:', token ? token.substring(0, 20) + '...' : 'N/A');
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      console.log('✅ Authorization header set');
    } else {
      console.error('❌ No token available in localStorage');
    }
    
    const response = await fetch(url, {
      method: 'POST',
      headers,
      credentials: 'include',
    });

    console.log(`📊 Save response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      console.error('❌ Save Error:', errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log('✅ Avatar saved successfully:', data);
    return data;
  }

  /**
   * Obtiene avatars del usuario autenticado
   */
  async getMyAvatars(skip: number = 0, limit: number = 100): Promise<UserAvatarListResponse> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    return this.request<UserAvatarListResponse>(`/me?${params}`);
  }

  /**
   * Obtiene avatars de un usuario específico
   */
  async getUserAvatars(
    userId: string, 
    skip: number = 0, 
    limit: number = 100
  ): Promise<UserAvatarListResponse> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    return this.request<UserAvatarListResponse>(`/user/${userId}?${params}`);
  }

  /**
   * Actualiza un avatar existente
   */
  async updateAvatar(
    avatarId: string,
    updates: {
      name?: string;
      is_active?: boolean;
      is_public?: boolean;
    }
  ): Promise<UserAvatar> {
    return this.request<UserAvatar>(`/${avatarId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Elimina un avatar
   */
  async deleteAvatar(avatarId: string): Promise<void> {
    await this.request<void>(`/${avatarId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Obtiene estadísticas del usuario
   */
  async getUserStats(): Promise<{
    total_avatars: number;
    public_avatars: number;
    private_avatars: number;
    has_active_avatar: boolean;
    active_avatar_id?: string;
  }> {
    return this.request('/stats/user');
  }

  /**
   * Activa un avatar específico
   */
  async setActiveAvatar(avatarId: string): Promise<UserAvatar> {
    return this.updateAvatar(avatarId, { is_active: true });
  }

  /**
   * Cambia la privacidad de un avatar
   */
  async toggleAvatarPrivacy(avatarId: string, isPublic: boolean): Promise<UserAvatar> {
    return this.updateAvatar(avatarId, { is_public: isPublic });
  }

  /**
   * Obtiene avatars públicos para la galería
   */
  async getPublicAvatars(skip: number = 0, limit: number = 20): Promise<UserAvatar[]> {
    // Por ahora usamos getMyAvatars como placeholder
    // TODO: Implementar endpoint específico para avatars públicos en el backend
    try {
      const response = await this.getMyAvatars(skip, limit);
      return response.avatars.filter(avatar => avatar.is_public);
    } catch (error) {
      console.warn('Error fetching public avatars, using mock data:', error);
      return [];
    }
  }
}

// Instancia global de la API
export const avatarAPI = new AvatarAPI();