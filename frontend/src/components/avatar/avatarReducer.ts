/**
 * Avatar Studio State Management
 * Reducer para manejar todo el estado del Avatar Studio de forma centralizada
 */

import type { LayerItem, ManifestResponse } from "./avatarAPI";

// ============================================
// TYPES
// ============================================

export type AvatarGender = "male" | "female";
export type GenderFilter = "all" | "male" | "female" | "unisex";

export interface AvatarState {
  // Core Data
  manifest: ManifestResponse | null;
  selectedGender: AvatarGender;
  selectedLayers: LayerItem[];
  avatarName: string;
  previewUrl: string;

  // Gender-specific persistence
  maleLayers: LayerItem[];
  femaleLayers: LayerItem[];

  // UI State
  activeCategory: string;
  activeGenderFilter: GenderFilter;
  isVisualizing: boolean;
  showPreviewModal: boolean;

  // Loading States
  loading: boolean;
  saving: boolean;
  error: string | null;

  // Internal flags
  isManualGenderChange: boolean;
}

// ============================================
// ACTIONS
// ============================================

export type AvatarAction =
  | { type: "SET_MANIFEST"; payload: ManifestResponse | null }
  | { type: "SET_GENDER"; payload: AvatarGender; isManual?: boolean }
  | { type: "SET_LAYERS"; payload: LayerItem[] }
  | { type: "ADD_LAYER"; payload: LayerItem }
  | { type: "REMOVE_LAYER"; payload: string } // category
  | { type: "UPDATE_LAYER"; payload: { category: string; asset: LayerItem } }
  | { type: "SET_AVATAR_NAME"; payload: string }
  | { type: "SET_PREVIEW_URL"; payload: string }
  | { type: "SET_MALE_LAYERS"; payload: LayerItem[] }
  | { type: "SET_FEMALE_LAYERS"; payload: LayerItem[] }
  | { type: "RESTORE_LAYERS_FOR_GENDER" }
  | { type: "SET_ACTIVE_CATEGORY"; payload: string }
  | { type: "SET_GENDER_FILTER"; payload: GenderFilter }
  | { type: "SET_VISUALIZING"; payload: boolean }
  | { type: "SET_PREVIEW_MODAL"; payload: boolean }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_SAVING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "CLEAR_ERROR" }
  | { type: "RESET_STATE" }
  | { type: "LOAD_FROM_STORAGE"; payload: { maleLayers: LayerItem[]; femaleLayers: LayerItem[] } };

// ============================================
// INITIAL STATE
// ============================================

export const getInitialState = (): AvatarState => {
  // Load from localStorage if available
  let maleLayers: LayerItem[] = [];
  let femaleLayers: LayerItem[] = [];

  try {
    const savedMale = localStorage.getItem("avatar_male_layers");
    const savedFemale = localStorage.getItem("avatar_female_layers");

    if (savedMale) maleLayers = JSON.parse(savedMale);
    if (savedFemale) femaleLayers = JSON.parse(savedFemale);
  } catch (err) {
    console.warn("Failed to load avatar layers from localStorage", err);
  }

  return {
    // Core Data
    manifest: null,
    selectedGender: "male",
    selectedLayers: maleLayers, // Start with male layers
    avatarName: "",
    previewUrl: "",

    // Gender-specific persistence
    maleLayers,
    femaleLayers,

    // UI State
    activeCategory: "hair",
    activeGenderFilter: "all",
    isVisualizing: false,
    showPreviewModal: false,

    // Loading States
    loading: false,
    saving: false,
    error: null,

    // Internal flags
    isManualGenderChange: false,
  };
};

// ============================================
// REDUCER
// ============================================

export function avatarReducer(state: AvatarState, action: AvatarAction): AvatarState {
  switch (action.type) {
    case "SET_MANIFEST":
      return {
        ...state,
        manifest: action.payload,
        error: null,
      };

    case "SET_GENDER": {
      const isManual = action.isManual ?? false;

      // Solo restaurar capas si es cambio manual
      // Si es automático (carga de avatar guardado), mantener las capas actuales
      let newSelectedLayers = state.selectedLayers;

      if (isManual) {
        // Cambio manual: restaurar capas guardadas para ese género
        const layersForGender = action.payload === "male" ? state.maleLayers : state.femaleLayers;
        newSelectedLayers = layersForGender;
        console.log(
          `🔄 [SET_GENDER] Cambio manual a ${action.payload}, restaurando ${layersForGender.length} capas`
        );
      } else {
        console.log(
          `✅ [SET_GENDER] Cambio automático a ${action.payload}, manteniendo ${state.selectedLayers.length} capas actuales`
        );
      }

      return {
        ...state,
        selectedGender: action.payload,
        selectedLayers: newSelectedLayers,
        isManualGenderChange: isManual,
      };
    }

    case "SET_LAYERS": {
      // Update the corresponding gender layers
      const newState = {
        ...state,
        selectedLayers: action.payload,
      };

      if (state.selectedGender === "male") {
        newState.maleLayers = action.payload;
      } else {
        newState.femaleLayers = action.payload;
      }

      return newState;
    }

    case "ADD_LAYER": {
      const newLayers = [...state.selectedLayers];
      const existingIndex = newLayers.findIndex((l) => l.category === action.payload.category);

      if (existingIndex >= 0) {
        newLayers[existingIndex] = action.payload;
      } else {
        newLayers.push(action.payload);
      }

      // Update both selectedLayers and gender-specific layers
      const newState = {
        ...state,
        selectedLayers: newLayers,
      };

      if (state.selectedGender === "male") {
        newState.maleLayers = newLayers;
      } else {
        newState.femaleLayers = newLayers;
      }

      return newState;
    }

    case "REMOVE_LAYER": {
      const newLayers = state.selectedLayers.filter((l) => l.category !== action.payload);

      const newState = {
        ...state,
        selectedLayers: newLayers,
      };

      if (state.selectedGender === "male") {
        newState.maleLayers = newLayers;
      } else {
        newState.femaleLayers = newLayers;
      }

      return newState;
    }

    case "UPDATE_LAYER": {
      const newLayers = state.selectedLayers.map((layer) =>
        layer.category === action.payload.category ? action.payload.asset : layer
      );

      const newState = {
        ...state,
        selectedLayers: newLayers,
      };

      if (state.selectedGender === "male") {
        newState.maleLayers = newLayers;
      } else {
        newState.femaleLayers = newLayers;
      }

      return newState;
    }

    case "SET_AVATAR_NAME":
      return {
        ...state,
        avatarName: action.payload,
      };

    case "SET_PREVIEW_URL":
      return {
        ...state,
        previewUrl: action.payload,
      };

    case "SET_MALE_LAYERS":
      return {
        ...state,
        maleLayers: action.payload,
        // If current gender is male, also update selectedLayers
        selectedLayers: state.selectedGender === "male" ? action.payload : state.selectedLayers,
      };

    case "SET_FEMALE_LAYERS":
      return {
        ...state,
        femaleLayers: action.payload,
        // If current gender is female, also update selectedLayers
        selectedLayers: state.selectedGender === "female" ? action.payload : state.selectedLayers,
      };

    case "RESTORE_LAYERS_FOR_GENDER": {
      const layersForGender =
        state.selectedGender === "male" ? state.maleLayers : state.femaleLayers;
      return {
        ...state,
        selectedLayers: layersForGender,
      };
    }

    case "SET_ACTIVE_CATEGORY":
      return {
        ...state,
        activeCategory: action.payload,
      };

    case "SET_GENDER_FILTER":
      return {
        ...state,
        activeGenderFilter: action.payload,
      };

    case "SET_VISUALIZING":
      return {
        ...state,
        isVisualizing: action.payload,
      };

    case "SET_PREVIEW_MODAL":
      return {
        ...state,
        showPreviewModal: action.payload,
      };

    case "SET_LOADING":
      return {
        ...state,
        loading: action.payload,
      };

    case "SET_SAVING":
      return {
        ...state,
        saving: action.payload,
      };

    case "SET_ERROR":
      return {
        ...state,
        error: action.payload,
        loading: false,
        saving: false,
      };

    case "CLEAR_ERROR":
      return {
        ...state,
        error: null,
      };

    case "RESET_STATE":
      return getInitialState();

    case "LOAD_FROM_STORAGE":
      return {
        ...state,
        maleLayers: action.payload.maleLayers,
        femaleLayers: action.payload.femaleLayers,
        selectedLayers:
          state.selectedGender === "male" ? action.payload.maleLayers : action.payload.femaleLayers,
      };

    default:
      return state;
  }
}

// ============================================
// SELECTORS (for better performance)
// ============================================

export const selectCurrentLayers = (state: AvatarState): LayerItem[] => {
  return state.selectedLayers;
};

export const selectLayersForGender = (state: AvatarState, gender: AvatarGender): LayerItem[] => {
  return gender === "male" ? state.maleLayers : state.femaleLayers;
};

export const selectIsLoading = (state: AvatarState): boolean => {
  return state.loading || state.saving;
};

export const selectHasLayers = (state: AvatarState): boolean => {
  return state.selectedLayers.length > 0;
};

export const selectLayerByCategory = (
  state: AvatarState,
  category: string
): LayerItem | undefined => {
  return state.selectedLayers.find((l) => l.category === category);
};
