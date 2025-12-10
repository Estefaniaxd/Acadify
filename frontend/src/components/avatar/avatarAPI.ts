// API client para avatars
import { API_BASE_URL } from "../../utils/api";
import type {
  AssetInfo,
  LayerItem,
  ManifestResponse,
  PreviewRequest,
  PreviewResponse,
  SaveAvatarRequest,
  UserAvatarResponse,
  UserAvatarListResponse,
  GenderType,
  CategoryType,
  SubcategoryType,
} from "../../types/avatar";

// Re-export types for backwards compatibility
export type { 
  AssetInfo, 
  LayerItem, 
  ManifestResponse, 
  PreviewResponse, 
  UserAvatarListResponse,
  GenderType,
  CategoryType,
  SubcategoryType,
} from "../../types/avatar";

// Legacy interfaces for backwards compatibility
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

export class AvatarAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_BASE_URL}/avatar`;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    // Para endpoints públicos como /assets, no incluir credenciales
    const isPublicEndpoint = endpoint.startsWith("/assets");

    // Obtener token de localStorage
    const token = localStorage.getItem("access_token");

    // Si no es endpoint público y no hay token, lanzar error específico
    if (!isPublicEndpoint && !token) {
      throw new Error("No estás autenticado. Por favor, inicia sesión primero.");
    }

    const defaultOptions: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        // Agregar Authorization header si hay token y no es endpoint público
        ...(token && !isPublicEndpoint ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    };

    console.log(`🔗 Fetching: ${url}`);
    console.log(`🔧 Public endpoint: ${isPublicEndpoint}`);
    console.log(`🔑 Token exists: ${token ? "YES" : "NO"}`);
    console.log(`🔒 Authorization header: ${token && !isPublicEndpoint ? "SENT" : "NOT_SENT"}`);

    const response = await fetch(url, { ...defaultOptions, ...options });

    console.log(`📊 Response status: ${response.status}`);
    console.log(`📊 Response ok: ${response.ok}`);

    if (!response.ok) {
      // Manejo especial para errores de autenticación
      if (response.status === 401) {
        // Intentar refresh automático
        const refreshToken = localStorage.getItem("refresh_token");
        if (refreshToken) {
          try {
            const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ refresh_token: refreshToken }),
            });
            if (refreshRes.ok) {
              const refreshData = await refreshRes.json();
              if (refreshData.access_token) {
                localStorage.setItem("access_token", refreshData.access_token);
                // Reintentar la petición original con el nuevo token
                const retryOptions = {
                  ...defaultOptions,
                  headers: {
                    ...defaultOptions.headers,
                    Authorization: `Bearer ${refreshData.access_token}`,
                  },
                };
                const retryResponse = await fetch(url, { ...retryOptions, ...options });
                if (retryResponse.ok) {
                  const retryData = await retryResponse.json();
                  return retryData;
                } else {
                  // Si sigue fallando, limpiar tokens y disparar logout
                  localStorage.removeItem("access_token");
                  localStorage.removeItem("refresh_token");
                  window.dispatchEvent(new CustomEvent("auth-token-expired"));
                  throw new Error(
                    "No se pudo renovar la sesión. Por favor, inicia sesión nuevamente."
                  );
                }
              }
            } else {
              // Refresh falló
              localStorage.removeItem("access_token");
              localStorage.removeItem("refresh_token");
              window.dispatchEvent(new CustomEvent("auth-token-expired"));
              throw new Error("No se pudo renovar la sesión. Por favor, inicia sesión nuevamente.");
            }
          } catch (refreshErr) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            window.dispatchEvent(new CustomEvent("auth-token-expired"));
            throw new Error("No se pudo renovar la sesión. Por favor, inicia sesión nuevamente.");
          }
        } else {
          // No hay refresh token, cerrar sesión
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.dispatchEvent(new CustomEvent("auth-token-expired"));
          throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
        }
      }
      const errorData = await response.json().catch(() => ({
        detail: `Network error: ${response.status} ${response.statusText}`,
      }));
      console.error("❌ API Error:", errorData);
      throw new Error(`HTTP ${response.status}: ${JSON.stringify(errorData)}`);
    }

    const data = await response.json();
    console.log("✅ API Success:", { endpoint, dataKeys: Object.keys(data) });
    return data;
  }

  /**
   * Obtiene el manifest de assets disponibles.
   * 
   * IMPORTANTE: El parámetro `gender` es INFORMATIVO únicamente.
   * No bloquea la selección de items - cualquier avatar puede usar cualquier item
   * independientemente del género objetivo del asset.
   * 
   * @param gender - Filtro opcional de género (male, female, unisex) - solo informativo
   * @returns Manifest con estructura plana (categories) y jerárquica (hierarchical)
   */
  async getAssetsManifest(gender?: GenderType): Promise<ManifestResponse> {
    const params = gender ? `?gender=${gender}` : "";
    const response = await this.request<any>(`/assets${params}`);

    // Transform snake_case backend response to camelCase frontend
    const transformed: ManifestResponse = {
      resolution: response.resolution,
      categories: {} as Record<string, AssetInfo[]>,
      hierarchical: undefined,
      totalAssets: response.total_assets || response.totalAssets || 0,
      gender: response.gender as GenderType | undefined,
    };

    // Transform flat categories (snake_case → camelCase)
    if (response.categories) {
      for (const [category, assets] of Object.entries(response.categories)) {
        transformed.categories[category as CategoryType] = (assets as any[]).map((asset: any) => ({
          id: asset.id || "",
          filename: asset.filename,
          displayName: asset.display_name || asset.displayName || asset.filename.split("/").pop() || "",
          category: asset.category || category,
          subcategory: asset.subcategory || undefined,
          targetGender: (asset.target_gender || asset.targetGender || "unisex") as GenderType,
          url: asset.url,
          width: asset.width || 512,
          height: asset.height || 512,
          fileSize: asset.file_size || asset.fileSize || 0,
          isNormalized: asset.is_normalized ?? asset.isNormalized ?? true,
          metaInfo: asset.meta_info || asset.metaInfo || {},
        }));
      }
    }

    // Transform hierarchical structure (category → subcategory → items)
    if (response.hierarchical) {
      transformed.hierarchical = {};
      
      for (const [category, subcategories] of Object.entries(response.hierarchical)) {
        transformed.hierarchical[category as CategoryType] = {} as Record<string, AssetInfo[]>;
        
        for (const [subcategory, assets] of Object.entries(subcategories as Record<string, any[]>)) {
          transformed.hierarchical[category as CategoryType][subcategory] = assets.map((asset: any) => ({
            id: asset.id || "",
            filename: asset.filename,
            displayName: asset.display_name || asset.displayName || asset.filename.split("/").pop() || "",
            category: asset.category || category,
            subcategory: asset.subcategory || subcategory,
            targetGender: (asset.target_gender || asset.targetGender || "unisex") as GenderType,
            url: asset.url,
            width: asset.width || 512,
            height: asset.height || 512,
            fileSize: asset.file_size || asset.fileSize || 0,
            isNormalized: asset.is_normalized ?? asset.isNormalized ?? true,
            metaInfo: asset.meta_info || asset.metaInfo || {},
          }));
        }
      }
    }

    return transformed;
  }

  /**
   * Genera avatar directamente como blob para preview (OPTIMIZADO)
   */
  async generateAvatar(layers: LayerItem[], baseGender: "male" | "female"): Promise<Blob> {
    const url = `${this.baseURL}/preview`;

    console.log(`🖼️ Generating avatar preview with ${layers.length} layers`);
    const startTime = performance.now();

    // Convertir el formato de layers
    // Normalizar: if filename is a basename (no '/'), prepend category so backend receives category/path
    const requestLayers = layers.map((layer) => ({
      category: layer.category,
      file: layer.filename.includes("/") ? layer.filename : `${layer.category}/${layer.filename}`,
    }));

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        base_gender: baseGender,
        layers: requestLayers,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => "Unknown error");
      console.error("❌ Preview Error:", errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    // El endpoint devuelve JSON con preview_url
    const data = await response.json();

    // OPTIMIZACIÓN: Retornar URL directamente sin segundo fetch
    // Crear blob URL desde la preview_url del servidor
    const fullUrl = data.preview_url.startsWith("http")
      ? data.preview_url
      : `http://localhost:8000${data.preview_url}`;

    // Fetch paralelo con señal de abort para cancelar si tarda mucho
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

    try {
      const imageResponse = await fetch(fullUrl, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (!imageResponse.ok) {
        throw new Error(`Failed to fetch preview image: ${imageResponse.status}`);
      }

      const blob = await imageResponse.blob();
      const elapsed = performance.now() - startTime;
      console.log(
        `✅ Preview generated in ${elapsed.toFixed(0)}ms (${blob.size} bytes, cached: ${
          data.from_cache
        })`
      );
      return blob;
    } catch (err: any) {
      clearTimeout(timeoutId);
      if (err.name === "AbortError") {
        console.error("❌ Preview timeout after 5s");
        throw new Error("Preview generation timeout");
      }
      throw err;
    }
  }

  /**
   * Guarda avatar permanentemente
   */
  async saveAvatar(
    name: string,
    baseGender: "male" | "female",
    layers: LayerItem[],
    isActive: boolean = false,
    isPublic: boolean = true
  ): Promise<UserAvatar> {
    console.log(`💾 Saving avatar with layers:`, layers);

    // Verificar que todas las capas tengan filename
    const invalidLayers = layers.filter((layer) => !layer.filename);
    if (invalidLayers.length > 0) {
      console.error("❌ Layers without filename:", invalidLayers);
      throw new Error("Some layers are missing filename property");
    }

    // Verificar token antes de proceder
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("No estás autenticado. Por favor, inicia sesión primero.");
    }

    // Forzar que solo se envíen {category, file} (nunca filename)
    // Limpiar cualquier propiedad extra: solo category y file
    const backendLayers = layers.map((layer) => {
      console.log(`📝 Mapping layer:`, layer);
      // Ensure backend always receives category-prefixed path
      return {
        category: layer.category,
        file: layer.filename.includes("/") ? layer.filename : `${layer.category}/${layer.filename}`,
      };
    });

    console.log(`💾 Backend layers format:`, backendLayers);

    // Crear el body JSON (el backend espera POST con body, NO query params)
    const requestBody = {
      name: name,
      base_gender: baseGender,
      layers: backendLayers,
      is_active: isActive,
      is_public: isPublic,
    };

    const url = `${this.baseURL}/save`;

    console.log("🔗 Save URL:", url);
    console.log("📦 Request body:", JSON.stringify(requestBody, null, 2));
    console.log("🔑 Token from localStorage:", token ? "TOKEN_PRESENT" : "NO_TOKEN");
    console.log("🔑 Token preview:", token ? token.substring(0, 20) + "..." : "N/A");

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    };

    console.log("✅ Authorization header set");

    let response = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(requestBody),
      credentials: "include",
    });

    console.log(`📊 Save response status: ${response.status}`);

    if (!response.ok) {
      // Manejo especial para errores de autenticación
      if (response.status === 401) {
        // Intentar refresh automático antes de forzar logout
        const refreshToken = localStorage.getItem("refresh_token");
        if (refreshToken) {
          try {
            const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ refresh_token: refreshToken }),
            });
            if (refreshRes.ok) {
              const refreshData = await refreshRes.json();
              if (refreshData.access_token) {
                localStorage.setItem("access_token", refreshData.access_token);
                // Reintentar la petición original con el nuevo token
                const retryHeaders = {
                  ...headers,
                  Authorization: `Bearer ${refreshData.access_token}`,
                };
                response = await fetch(url, {
                  method: "POST",
                  headers: retryHeaders,
                  body: JSON.stringify(requestBody),
                  credentials: "include",
                });
                if (response.ok) {
                  const data = await response.json();
                  console.log("✅ Avatar saved successfully after token refresh:", data);
                  return data;
                }
              }
            }
          } catch (refreshErr) {
            console.error("❌ Error refreshing token during avatar save:", refreshErr);
          }
        }
        // Si el refresh falla, forzar logout
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.dispatchEvent(new CustomEvent("auth-token-expired"));
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      const errorText = await response.text().catch(() => "Unknown error");
      console.error("❌ Save Error:", errorText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log("✅ Avatar saved successfully:", data);
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
   * Obtiene avatars de un usuario específico (solo para el usuario actual)
   */
  async getUserAvatars(
    userId: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<UserAvatarListResponse> {
    // Para avatars, solo podemos obtener los propios
    // Redirigir a /me independientemente del userId
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    return this.request<UserAvatarListResponse>(`/me?${params}`);
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
      method: "PUT",
      body: JSON.stringify(updates),
    });
  }

  /**
   * Elimina un avatar
   */
  async deleteAvatar(avatarId: string): Promise<void> {
    await this.request<void>(`/${avatarId}`, {
      method: "DELETE",
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
    return this.request("/stats/user");
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
      return response.avatars.filter((avatar) => avatar.is_public);
    } catch (error) {
      console.warn("Error fetching public avatars, using mock data:", error);
      return [];
    }
  }
}

// Instancia global de la API
export const avatarAPI = new AvatarAPI();
