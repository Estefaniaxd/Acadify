/**
 * Custom Hook for Avatar Studio
 * Encapsula toda la lógica de estado y efectos secundarios
 */

import { useCallback, useEffect, useMemo, useReducer, useRef } from "react";
import { useToast } from "../../context/ToastContext";
import { avatarAPI, LayerItem } from "./avatarAPI";
import { AvatarGender, avatarReducer, GenderFilter, getInitialState } from "./avatarReducer";

export function useAvatarStudio() {
  const [state, dispatch] = useReducer(avatarReducer, getInitialState());
  const { success, error: showError, info, warning } = useToast();

  // Refs para efectos y limpieza
  const saveToLocalStorage = useRef<number | null>(null);
  const lastPreviewLayers = useRef<string>("");
  const genderChangeTimeout = useRef<number | null>(null);
  const hasShownInitialToast = useRef(false);
  const hasLoadedUserAvatar = useRef(false);

  // ============================================
  // EFFECTS: Persistence
  // ============================================

  // Sync male layers to localStorage (debounced)
  useEffect(() => {
    if (saveToLocalStorage.current) clearTimeout(saveToLocalStorage.current);

    saveToLocalStorage.current = window.setTimeout(() => {
      try {
        localStorage.setItem("avatar_male_layers", JSON.stringify(state.maleLayers));
      } catch (err) {
        console.warn("Failed to save male layers to localStorage", err);
      }
    }, 200);
  }, [state.maleLayers]);

  // Sync female layers to localStorage (debounced)
  useEffect(() => {
    if (saveToLocalStorage.current) clearTimeout(saveToLocalStorage.current);

    saveToLocalStorage.current = window.setTimeout(() => {
      try {
        localStorage.setItem("avatar_female_layers", JSON.stringify(state.femaleLayers));
      } catch (err) {
        console.warn("Failed to save female layers to localStorage", err);
      }
    }, 200);
  }, [state.femaleLayers]);

  // ============================================
  // EFFECTS: Cleanup
  // ============================================

  useEffect(() => {
    return () => {
      // Cleanup timeouts
      if (genderChangeTimeout.current) clearTimeout(genderChangeTimeout.current);
      if (saveToLocalStorage.current) clearTimeout(saveToLocalStorage.current);

      // Cleanup object URLs
      if (state.previewUrl) {
        URL.revokeObjectURL(state.previewUrl);
      }
    };
  }, []);

  // Cleanup preview URL when it changes
  useEffect(() => {
    return () => {
      if (state.previewUrl) {
        URL.revokeObjectURL(state.previewUrl);
      }
    };
  }, [state.previewUrl]);

  // ============================================
  // EFFECTS: Gender Change Notification
  // ============================================

  useEffect(() => {
    if (!state.isManualGenderChange) return;

    if (genderChangeTimeout.current) clearTimeout(genderChangeTimeout.current);

    const genderLabel = state.selectedGender === "male" ? "Masculino" : "Femenino";
    const currentGenderLayers =
      state.selectedGender === "male" ? state.maleLayers : state.femaleLayers;

    genderChangeTimeout.current = window.setTimeout(() => {
      if (currentGenderLayers.length > 0) {
        info(
          `Se restauraron ${currentGenderLayers.length} elementos para ${genderLabel.toLowerCase()}`
        );
      } else {
        info(`Cambiando a ${genderLabel.toLowerCase()} - Selecciona nuevos elementos`);
      }
    }, 400);

    // Reset flag
    dispatch({ type: "SET_GENDER", payload: state.selectedGender, isManual: false });
  }, [
    state.isManualGenderChange,
    state.selectedGender,
    state.maleLayers,
    state.femaleLayers,
    info,
  ]);

  // ============================================
  // API FUNCTIONS
  // ============================================

  const loadManifest = useCallback(async () => {
    try {
      console.log(`📦 [loadManifest] Iniciando carga para género: ${state.selectedGender}`);
      dispatch({ type: "SET_LOADING", payload: true });
      const manifestData = await avatarAPI.getAssetsManifest(state.selectedGender);
      console.log(`✅ [loadManifest] Manifest recibido:`, manifestData);
      console.log(
        `📊 [loadManifest] Categorías disponibles:`,
        Object.keys(manifestData.categories)
      );
      dispatch({ type: "SET_MANIFEST", payload: manifestData });
      dispatch({ type: "SET_LOADING", payload: false });
      console.log(`✅ [loadManifest] Estado actualizado, loading = false`);
    } catch (err: any) {
      console.error("❌ [loadManifest] Error loading manifest:", err);
      dispatch({ type: "SET_ERROR", payload: err.message || "Error al cargar el manifest" });
      dispatch({ type: "SET_LOADING", payload: false });
      showError("Error al cargar los assets del avatar");
    }
  }, [state.selectedGender, showError]);

  const loadUserSavedAvatar = useCallback(async () => {
    try {
      console.log("🔄 Loading user saved avatar...");
      const avatarData = await avatarAPI.getMyAvatars();
      console.log("✅ User avatars response:", avatarData);
      console.log("📊 Total avatars:", avatarData.avatars.length);

      if (avatarData.avatars.length > 0) {
        console.log(
          "👤 Avatar user_ids:",
          avatarData.avatars.map((a) => ({
            user_id: a.user_id,
            name: a.name,
            is_active: a.is_active,
          }))
        );
      }

      const activeAvatar = avatarData.avatars.find((avatar) => avatar.is_active);
      console.log("🎯 Active avatar found:", activeAvatar);

      if (activeAvatar) {
        dispatch({ type: "SET_AVATAR_NAME", payload: activeAvatar.name });

        if (activeAvatar.layers && activeAvatar.layers.length > 0) {
          // Transform backend format {category, file} to frontend format {category, filename, url}
          const transformedLayers = activeAvatar.layers.map((layer: any) => ({
            category: layer.category,
            filename: layer.file || layer.filename, // Backend sends "file", frontend expects "filename"
            url: layer.url || `http://localhost:8000/static/assets/${layer.file || layer.filename}`, // Generate URL if missing
          }));

          console.log("🔄 [loadUserSavedAvatar] Transformed layers:", transformedLayers);

          // IMPORTANTE: Cambiar gender PRIMERO con isManual=false para que NO restaure capas vacías
          const targetGender = activeAvatar.base_gender as AvatarGender;
          console.log(
            `🔄 [loadUserSavedAvatar] Setting gender to ${targetGender} (isManual=false)`
          );
          dispatch({
            type: "SET_GENDER",
            payload: targetGender,
            isManual: false, // ← CLAVE: No restaurar capas, solo cambiar género
          });

          // LUEGO cargar las capas (esto actualizará selectedLayers Y maleLayers/femaleLayers)
          console.log(`📦 [loadUserSavedAvatar] Setting ${transformedLayers.length} layers`);
          dispatch({ type: "SET_LAYERS", payload: transformedLayers });

          if (!hasShownInitialToast.current) {
            info(
              `Avatar "${activeAvatar.name}" cargado con ${activeAvatar.layers.length} elementos`
            );
            hasShownInitialToast.current = true;
          }
        }
      }
    } catch (err: any) {
      console.warn("Could not load user avatar:", err);
    }
  }, [info]);

  const generatePreview = useCallback(async () => {
    if (!state.manifest || state.selectedLayers.length === 0) {
      dispatch({ type: "SET_PREVIEW_URL", payload: "" });
      return;
    }

    // Validar que todas las capas tengan filename
    const invalidLayers = state.selectedLayers.filter((layer) => !layer.filename);
    if (invalidLayers.length > 0) {
      console.error("❌ [generatePreview] Capas inválidas sin filename:", invalidLayers);
      showError("Error: Algunas capas no tienen archivo válido");
      return;
    }

    const layersKey = JSON.stringify(state.selectedLayers);
    if (layersKey === lastPreviewLayers.current) {
      console.log("⚡ [Cache HIT] Preview ya generado, saltando...");
      return;
    }

    console.log(
      `🎨 [generatePreview] Generando con ${state.selectedLayers.length} capas:`,
      state.selectedLayers.map((l) => `${l.category}:${l.filename}`).join(", ")
    );

    // Reordenar las capas según un orden canónico de composición
    // para asegurar que ciertos elementos (p.ej. jacket) se rendericen
    // por encima de otros (p.ej. hair). Si el backend asume que la
    // última capa del array se dibuja encima, colocamos las capas con
    // mayor 'z' al final.
    const reorderLayersForComposition = (layers: LayerItem[]) => {
      const order: Record<string, number> = {
        backgrounds: -100,
        base: -50,
        pants: 0,
        skirt: 0,
        shirt: 10,
        makeup: 20,
        hair: 30,
        eyes: 40,
        mouth: 45,
        accessories: 50,
        jacket: 70, // asegurar que jacket se pinte por encima del hair
        shoes: 80,
        socks: 85,
      };

      // Asignar prioridad por categoría y mantener orden relativo cuando
      // la prioridad es la misma (estable).
      return [...layers].sort((a, b) => {
        const pa = order[a.category] ?? 0;
        const pb = order[b.category] ?? 0;
        if (pa === pb) return 0;
        return pa - pb;
      });
    };

    // Marcar como visualizing INMEDIATAMENTE para feedback instantáneo
    dispatch({ type: "SET_VISUALIZING", payload: true });

    try {
      const layersToSend = reorderLayersForComposition(state.selectedLayers);

      const blob = await avatarAPI.generateAvatar(layersToSend, state.selectedGender);
      const url = URL.createObjectURL(blob);

      // Revoke old URL
      if (state.previewUrl) {
        URL.revokeObjectURL(state.previewUrl);
      }

      dispatch({ type: "SET_PREVIEW_URL", payload: url });
      // Guardar el caché con la representación ordenada para evitar falsos hits
      lastPreviewLayers.current = JSON.stringify(layersToSend);
      console.log("✅ [generatePreview] Preview URL actualizada exitosamente");
    } catch (err: any) {
      console.error("❌ [generatePreview] Error detallado:", {
        message: err.message,
        stack: err.stack,
        layers: state.selectedLayers,
        gender: state.selectedGender,
      });

      // NO mostrar error en la primera carga (puede ser race condition temporal)
      if (state.previewUrl) {
        showError(`Error al generar preview: ${err.message}`);
      } else {
        console.warn("⚠️ Error en primera carga de preview, ignorando...");
      }
    } finally {
      dispatch({ type: "SET_VISUALIZING", payload: false });
    }
  }, [state.manifest, state.selectedLayers, state.selectedGender, state.previewUrl, showError]);

  const saveAvatar = useCallback(async () => {
    if (state.selectedLayers.length === 0) {
      warning("Selecciona al menos un elemento para tu avatar");
      return;
    }

    if (!state.avatarName.trim()) {
      warning("Ingresa un nombre para tu avatar");
      return;
    }

    try {
      dispatch({ type: "SET_SAVING", payload: true });

      await avatarAPI.saveAvatar(
        state.avatarName,
        state.selectedGender,
        state.selectedLayers,
        true, // isActive
        true // isPublic
      );

      success(`Avatar "${state.avatarName}" guardado exitosamente`);
    } catch (err: any) {
      console.error("Error saving avatar:", err);
      showError(err.message || "Error al guardar el avatar");
    } finally {
      dispatch({ type: "SET_SAVING", payload: false });
    }
  }, [state.selectedLayers, state.avatarName, state.selectedGender, success, warning, showError]);

  // ============================================
  // EFFECTS: Auto-load
  // ============================================

  // Load manifest on mount FIRST (antes que todo)
  useEffect(() => {
    console.log("🚀 [MOUNT] Iniciando carga de manifest inicial");
    loadManifest();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Solo en mount

  // Load manifest when gender changes (pero no en mount)
  useEffect(() => {
    // Skip en primer render (ya se cargó arriba)
    if (state.manifest === null) return;

    console.log(`🔄 [GENDER CHANGE] Recargando manifest para ${state.selectedGender}`);
    loadManifest();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.selectedGender]);

  // Load user saved avatar AFTER manifest is ready (SOLO UNA VEZ)
  useEffect(() => {
    console.log("🔍 [useEffect loadUserAvatar] Check:", {
      hasManifest: !!state.manifest,
      hasLoadedAlready: hasLoadedUserAvatar.current,
      manifestCategories: state.manifest ? Object.keys(state.manifest.categories).length : 0,
    });

    if (!state.manifest) {
      console.log("⏳ [loadUserSavedAvatar] Esperando manifest...");
      return;
    }

    if (hasLoadedUserAvatar.current) {
      console.log("⏭️ [loadUserSavedAvatar] Ya se cargó antes, saltando...");
      return;
    }

    console.log("✅ [loadUserSavedAvatar] Manifest listo, cargando avatar guardado (primera vez)");
    hasLoadedUserAvatar.current = true;
    loadUserSavedAvatar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.manifest]); // Ejecutar cuando manifest esté listo

  // Auto-load base when manifest loads and no base exists (FALLBACK)
  useEffect(() => {
    if (state.manifest && state.manifest.categories.base?.length > 0) {
      const hasBase = state.selectedLayers.some((layer) => layer.category === "base");
      if (!hasBase && state.selectedLayers.length === 0) {
        console.log(`🎯 [useEffect] Auto-cargando base fallback para ${state.selectedGender}`);
        const baseAsset = state.manifest.categories.base[0];
        dispatch({
          type: "ADD_LAYER",
          payload: {
            category: "base",
            filename: baseAsset.filename,
            url: baseAsset.url,
          },
        });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.manifest, state.selectedGender]); // NO incluir state.selectedLayers para evitar loop

  // Generate preview when layers change (con debounce para mejor UX)
  useEffect(() => {
    if (!state.manifest) {
      console.log("⏸️ [Preview] Manifest no cargado, esperando...");
      return;
    }

    if (state.selectedLayers.length === 0) {
      console.log("⏸️ [Preview] Sin capas seleccionadas");
      dispatch({ type: "SET_PREVIEW_URL", payload: "" });
      return;
    }

    // Verificar que las capas tengan datos válidos
    const hasInvalidLayers = state.selectedLayers.some(
      (layer) => !layer.filename || !layer.category
    );
    if (hasInvalidLayers) {
      console.warn("⚠️ [Preview] Capas inválidas detectadas, esperando datos completos...");
      return;
    }

    // --- NUEVO: Asegurar que la base corresponda a si hay ojos o no ---
    const ensureBaseMatchesEyes = () => {
      try {
        if (!state.manifest) return;
        const baseAssets = state.manifest.categories.base || [];
        if (!Array.isArray(baseAssets) || baseAssets.length === 0) return;

        // Si el usuario tiene una capa de ojos seleccionada (custom eyes),
        // necesitamos elegir la variante de base SIN ojos para que las capas
        // de ojos personalizadas se muestren correctamente encima.
        const hasCustomEyes = state.selectedLayers.some(
          (l) => l.category === "eyes" && l.filename && l.filename !== "none"
        );

        // Queremos candidate.meta_info.has_eyes === !hasCustomEyes
        let candidate =
          baseAssets.find(
            (a) =>
              a.meta_info &&
              typeof a.meta_info.has_eyes !== "undefined" &&
              Boolean(a.meta_info.has_eyes) === Boolean(!hasCustomEyes)
          ) || null;

        // Fallback heuristics: si el manifest no incluye meta_info, buscar por
        // sufijos conocidos (timestamps) presentes en el repo para las variantes
        // con/sin ojos. Esto cubre los assets actuales del proyecto.
        if (!candidate) {
          const fallbackMap: Record<string, { withEyes: string; noEyes: string }> = {
            male: {
              withEyes: "167 sin título_20250923002615.png",
              noEyes: "167 sin título_20250922233558.png",
            },
            female: {
              withEyes: "167 sin título_20250923002534.png",
              noEyes: "167 sin título_20250922233650.png",
            },
          };

          const genderKey = state.selectedGender === "male" ? "male" : "female";
          const targetFilename = hasCustomEyes
            ? fallbackMap[genderKey].noEyes
            : fallbackMap[genderKey].withEyes;

          candidate =
            baseAssets.find((a) => a.filename && a.filename.includes(targetFilename)) ||
            baseAssets[0];
        }

        const currentBase = state.selectedLayers.find((l) => l.category === "base");
        if (!currentBase) {
          // Insertar base al inicio si no existe
          dispatch({
            type: "ADD_LAYER",
            payload: { category: "base", filename: candidate.filename, url: candidate.url },
          });
        } else if (currentBase.filename !== candidate.filename) {
          // Reemplazar la base por la variante correcta
          dispatch({
            type: "UPDATE_LAYER",
            payload: {
              category: "base",
              asset: { category: "base", filename: candidate.filename, url: candidate.url },
            },
          });
        }
      } catch (err) {
        console.warn("[ensureBaseMatchesEyes] fallo al asegurar base:", err);
      }
    };

    // Ejecutar la verificación de base antes del debounce de preview
    ensureBaseMatchesEyes();

    // Debounce de 150ms - suficiente para evitar spam pero lo suficientemente rápido
    const debounceTimer = setTimeout(() => {
      console.warn("⏱️ [Debounce] Generando preview después de 150ms...");
      generatePreview();
    }, 150);

    return () => {
      clearTimeout(debounceTimer);
      console.warn("🚫 [Debounce] Preview cancelado (usuario sigue seleccionando)");
    };

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.manifest, state.selectedLayers]);

  // ============================================
  // MEMOIZED SELECTORS
  // ============================================

  const currentLayers = useMemo(() => state.selectedLayers, [state.selectedLayers]);

  const hasLayers = useMemo(() => state.selectedLayers.length > 0, [state.selectedLayers]);

  const isLoading = useMemo(() => state.loading || state.saving, [state.loading, state.saving]);

  // ============================================
  // ACTION CREATORS
  // ============================================

  const setGender = useCallback((gender: AvatarGender, isManual = true) => {
    dispatch({ type: "SET_GENDER", payload: gender, isManual });
  }, []);

  const setLayers = useCallback((layers: LayerItem[]) => {
    dispatch({ type: "SET_LAYERS", payload: layers });
  }, []);

  const addLayer = useCallback((layer: LayerItem) => {
    dispatch({ type: "ADD_LAYER", payload: layer });
  }, []);

  const removeLayer = useCallback((category: string) => {
    dispatch({ type: "REMOVE_LAYER", payload: category });
  }, []);

  const updateLayer = useCallback((category: string, asset: LayerItem) => {
    dispatch({ type: "UPDATE_LAYER", payload: { category, asset } });
  }, []);

  const setAvatarName = useCallback((name: string) => {
    dispatch({ type: "SET_AVATAR_NAME", payload: name });
  }, []);

  const setActiveCategory = useCallback((category: string) => {
    dispatch({ type: "SET_ACTIVE_CATEGORY", payload: category });
  }, []);

  const setGenderFilter = useCallback((filter: GenderFilter) => {
    dispatch({ type: "SET_GENDER_FILTER", payload: filter });
  }, []);

  const setPreviewModal = useCallback((show: boolean) => {
    dispatch({ type: "SET_PREVIEW_MODAL", payload: show });
  }, []);

  const resetState = useCallback(() => {
    dispatch({ type: "RESET_STATE" });
  }, []);

  const generateRandom = useCallback(() => {
    if (!state.manifest) return;

    const newLayers: LayerItem[] = [];

    // Siempre incluir la base
    if (state.manifest.categories.base?.length > 0) {
      const baseAsset = state.manifest.categories.base[0];
      newLayers.push({
        category: "base",
        filename: baseAsset.filename,
        url: baseAsset.url,
      });
    }

    // Randomizar otras categorías
    Object.entries(state.manifest.categories).forEach(([category, assets]) => {
      if (category === "base") return; // Ya manejamos la base

      if (Math.random() > 0.4) {
        // 60% chance de incluir cada categoría
        const randomAsset = assets[Math.floor(Math.random() * assets.length)];
        newLayers.push({
          category,
          filename: randomAsset.filename,
          url: randomAsset.url,
        });
      }
    });

    dispatch({ type: "SET_LAYERS", payload: newLayers });
  }, [state.manifest]);

  // ============================================
  // RETURN API
  // ============================================

  return {
    // State
    state,

    // Derived state (memoized)
    currentLayers,
    hasLayers,
    isLoading,

    // Actions
    setGender,
    setLayers,
    addLayer,
    removeLayer,
    updateLayer,
    setAvatarName,
    setActiveCategory,
    setGenderFilter,
    setPreviewModal,
    resetState,
    generateRandom,

    // API Functions
    loadManifest,
    loadUserSavedAvatar,
    generatePreview,
    saveAvatar,
  };
}
