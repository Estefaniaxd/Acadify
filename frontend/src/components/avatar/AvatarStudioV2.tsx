import { AnimatePresence, motion } from "framer-motion";
import {
  Check,
  Download,
  Eye,
  Filter,
  Gem,
  Grid,
  Grid3x3,
  Hand,
  Heart,
  Palette,
  RefreshCw,
  RotateCcw,
  Save,
  Shirt,
  Shuffle,
  Sparkles,
  Trash2,
  User,
  Users,
  Watch,
  X,
} from "lucide-react";
import React, { useEffect, useRef, useState } from "react";

import { useAuth } from "../../context/AuthContext";
import { useToast } from "../../context/ToastContext";
import { AssetInfo, avatarAPI, LayerItem, ManifestResponse } from "./avatarAPI";
import { useAvatarStudio } from "./useAvatarStudio";

interface AvatarStudioV2Props {
  onSave?: (avatar: any) => void;
  onPreview?: (previewUrl: string) => void;
}

const AvatarStudioV2: React.FC<AvatarStudioV2Props> = ({ onSave, onPreview }) => {
  const { success, error: showError, info, warning } = useToast();
  const { isAuthenticated } = useAuth();

  // 🎯 NEW: useAvatarStudio hook (replaces 16 useState + 8 useEffect)
  const avatarStudio = useAvatarStudio();

  // 🔄 MIGRATION FLAG: Set to true to use new hook
  const USE_NEW_HOOK = true;

  // Refs para limpieza
  const saveToLocalStorage = useRef<number | null>(null);
  const hasShownInitialAvatarToast = useRef(false);
  const lastPreviewLayers = useRef<string>("");
  const previewRef = useRef<HTMLDivElement | null>(null);
  const [isPreviewVisible, setIsPreviewVisible] = useState<boolean>(true);

  // Estados principales
  const [selectedGender, setSelectedGender] = useState<"male" | "female">("male");
  const [manifest, setManifest] = useState<ManifestResponse | null>(null);
  const [selectedLayers, setSelectedLayers] = useState<LayerItem[]>([]);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [avatarName, setAvatarName] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estados para persistencia de capas por género (con localStorage)
  const [maleLayers, setMaleLayers] = useState<LayerItem[]>(() => {
    const saved = localStorage.getItem("avatar_male_layers");
    return saved ? JSON.parse(saved) : [];
  });
  const [femaleLayers, setFemaleLayers] = useState<LayerItem[]>(() => {
    const saved = localStorage.getItem("avatar_female_layers");
    return saved ? JSON.parse(saved) : [];
  });

  // Sincronizar cambios con localStorage - optimizado con debounce
  useEffect(() => {
    if (saveToLocalStorage.current) clearTimeout(saveToLocalStorage.current);
    saveToLocalStorage.current = window.setTimeout(() => {
      localStorage.setItem("avatar_male_layers", JSON.stringify(maleLayers));
    }, 500);
  }, [maleLayers]);

  useEffect(() => {
    if (saveToLocalStorage.current) clearTimeout(saveToLocalStorage.current);
    saveToLocalStorage.current = window.setTimeout(() => {
      localStorage.setItem("avatar_female_layers", JSON.stringify(femaleLayers));
    }, 500);
  }, [femaleLayers]);

  // Estados de UI
  const [activeCategory, setActiveCategory] = useState<string>("hair");
  const [activeSubcategory, setActiveSubcategory] = useState<string | null>(null); // Para categories con subcategorías (ej: accessories)
  const [activeGenderFilter, setActiveGenderFilter] = useState<string>("all"); // all, male, female, unisex
  const [genderChangeTimeout, setGenderChangeTimeout] = useState<number | null>(null);
  // Ref para controlar si ya se mostró el toast inicial
  // Estado para distinguir cambio manual de género
  const [isManualGenderChange, setIsManualGenderChange] = useState(false);
  const [isVisualizing, setIsVisualizing] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);

  // 🎯 CONDITIONAL STATE: Use new hook or old state
  const actualGender = USE_NEW_HOOK ? avatarStudio.state.selectedGender : selectedGender;
  const actualManifest = USE_NEW_HOOK ? avatarStudio.state.manifest : manifest;
  const actualLayers = USE_NEW_HOOK ? avatarStudio.currentLayers : selectedLayers;
  const actualPreviewUrl = USE_NEW_HOOK ? avatarStudio.state.previewUrl : previewUrl;
  const actualAvatarName = USE_NEW_HOOK ? avatarStudio.state.avatarName : avatarName;
  const actualLoading = USE_NEW_HOOK ? avatarStudio.isLoading : loading;
  const actualSaving = USE_NEW_HOOK ? avatarStudio.state.saving : saving;
  const actualError = USE_NEW_HOOK ? avatarStudio.state.error : error;
  const actualActiveCategory = USE_NEW_HOOK ? avatarStudio.state.activeCategory : activeCategory;
  const actualGenderFilter = USE_NEW_HOOK
    ? avatarStudio.state.activeGenderFilter
    : activeGenderFilter;
  const actualVisualizing = USE_NEW_HOOK ? avatarStudio.state.isVisualizing : isVisualizing;
  const actualShowPreviewModal = USE_NEW_HOOK
    ? avatarStudio.state.showPreviewModal
    : showPreviewModal;

  // Cargar manifest cuando cambia el género
  useEffect(() => {
    if (!USE_NEW_HOOK) {
      loadManifest();
    }
  }, [selectedGender]);

  // Resetear subcategoría activa cuando cambia la categoría
  useEffect(() => {
    setActiveSubcategory(null);
  }, [actualActiveCategory]);

  // Limpiar localStorage de paths inválidos al montar
  useEffect(() => {
    try {
      // Limpiar layers con paths viejos (mounth)
      const maleLayers = localStorage.getItem("avatar_male_layers");
      const femaleLayers = localStorage.getItem("avatar_female_layers");

      if (maleLayers && maleLayers.includes("mounth")) {
        console.warn("⚠️ Limpiando male layers con paths inválidos");
        localStorage.removeItem("avatar_male_layers");
      }
      if (femaleLayers && femaleLayers.includes("mounth")) {
        console.warn("⚠️ Limpiando female layers con paths inválidos");
        localStorage.removeItem("avatar_female_layers");
      }
    } catch (e) {
      console.error("Error limpiando localStorage:", e);
    }
  }, []);

  // El manifest se carga automáticamente en useAvatarStudio hook
  // NO duplicar la carga aquí para evitar re-renders

  // Actualizar selectedLayers cuando cambia el género (recuperar de memoria) - optimizado
  useEffect(() => {
    const layersForGender = selectedGender === "male" ? maleLayers : femaleLayers;
    if (JSON.stringify(selectedLayers) !== JSON.stringify(layersForGender)) {
      setSelectedLayers(layersForGender);
    }
    // Notificación SOLO si es cambio manual
    if (isManualGenderChange) {
      if (genderChangeTimeout) clearTimeout(genderChangeTimeout);
      const genderLabel = selectedGender === "male" ? "Masculino" : "Femenino";
      const currentGenderLayers = selectedGender === "male" ? maleLayers : femaleLayers;
      const timeoutId = window.setTimeout(() => {
        if (currentGenderLayers.length > 0) {
          info(
            `Se restauraron ${
              currentGenderLayers.length
            } elementos para ${genderLabel.toLowerCase()}`
          );
        } else {
          info(`Cambiando a ${genderLabel.toLowerCase()} - Selecciona nuevos elementos`);
        }
      }, 400);
      setGenderChangeTimeout(timeoutId as number);
      setIsManualGenderChange(false);
    }
  }, [selectedGender, maleLayers, femaleLayers, isManualGenderChange]);

  // Cargar avatar guardado del usuario al inicializar el componente
  // NOTA: Deshabilitado cuando USE_NEW_HOOK=true porque el hook ya lo hace
  useEffect(() => {
    if (!USE_NEW_HOOK) {
      loadUserSavedAvatar();
    }
  }, []);

  // Limpiar timeouts y URLs al desmontar el componente
  useEffect(() => {
    return () => {
      // Limpiar todos los timeouts
      if (genderChangeTimeout) {
        clearTimeout(genderChangeTimeout);
      }
      if (saveToLocalStorage.current) {
        clearTimeout(saveToLocalStorage.current);
      }
      // Limpiar URLs de objetos
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, []);

  // Limpiar URLs cuando cambia el preview
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  // Generar preview cuando cambian las capas - optimizado para evitar ciclos
  // NOTA: Deshabilitado cuando USE_NEW_HOOK=true porque el hook ya lo hace
  useEffect(() => {
    if (USE_NEW_HOOK) return; // El hook maneja esto

    if (!manifest) return;
    if (!selectedLayers || selectedLayers.length === 0) return;
    const layersKey = JSON.stringify(selectedLayers);
    if (layersKey !== lastPreviewLayers.current) {
      lastPreviewLayers.current = layersKey;
      const timeoutId = setTimeout(() => generatePreview(), 200);
      return () => clearTimeout(timeoutId);
    }
  }, [manifest, selectedLayers]);

  // IntersectionObserver para saber si el preview está visible
  useEffect(() => {
    const el = previewRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        setIsPreviewVisible(entries[0]?.isIntersecting ?? false);
      },
      { root: null, threshold: 0.1 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [previewRef.current]);

  const loadUserSavedAvatar = async () => {
    try {
      console.log("🔄 Loading user saved avatar...");
      const avatarData = await avatarAPI.getMyAvatars();
      console.log("✅ User avatars response:", avatarData);
      // Buscar el avatar activo del usuario
      const activeAvatar = avatarData.avatars.find((avatar) => avatar.is_active);
      console.log("🎯 Active avatar found:", activeAvatar);
      if (activeAvatar) {
        setSelectedGender(activeAvatar.base_gender as "male" | "female");
        setAvatarName(activeAvatar.name);
        const editorLayers: LayerItem[] = activeAvatar.layers.map((layer) => {
          const filename = (layer as any).filename || (layer as any).file;
          return {
            category: layer.category,
            filename: filename,
            url: `http://localhost:8000/static/assets/${filename}`,
          };
        });
        setSelectedLayers(editorLayers);
        // Mostrar solo una vez la notificación al cargar el avatar inicial
        if (!hasShownInitialAvatarToast.current) {
          success(`Avatar "${activeAvatar.name}" cargado en el editor`);
          hasShownInitialAvatarToast.current = true;
        }
      } else {
        console.log("ℹ️ No active avatar found, starting with empty editor");
      }
    } catch (error) {
      console.error("❌ Error loading user saved avatar:", error);
      // No mostrar error toast aquí, porque es normal no tener avatar guardado
      console.log("ℹ️ Starting with empty editor");
    }
  };

  const loadManifest = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log("🔄 Loading manifest for gender:", selectedGender);

      const data = await avatarAPI.getAssetsManifest(selectedGender);
      console.log("✅ Manifest loaded successfully:", {
        totalAssets: data.total_assets,
        categories: Object.keys(data.categories),
        resolution: data.resolution,
      });

      setManifest(data);

      // Auto-seleccionar la base correspondiente al género
      if (data.categories.base && data.categories.base.length > 0) {
        const baseAsset = data.categories.base[0]; // Tomar la primera base
        console.log("🎯 Auto-selecting base:", baseAsset.filename);

        const baseLayer = {
          category: "base",
          filename: baseAsset.filename,
          url: baseAsset.url,
        };

        // Solo agregar la base si no hay capas ya cargadas para este género
        const currentGenderLayers = selectedGender === "male" ? maleLayers : femaleLayers;
        const hasBaseAlready = currentGenderLayers.some((layer) => layer.category === "base");

        if (!hasBaseAlready && currentGenderLayers.length === 0) {
          // Solo auto-seleccionar base si no hay nada guardado para este género
          setSelectedLayers([baseLayer]);
          if (selectedGender === "male") {
            setMaleLayers([baseLayer]);
          } else {
            setFemaleLayers([baseLayer]);
          }
        }
      }
    } catch (error) {
      console.error("❌ Error loading manifest:", error);
      setError("Error al cargar los assets del avatar");
      showError("Error al cargar los elementos del avatar");
    } finally {
      setLoading(false);
    }
  };

  const generatePreview = async () => {
    if (!manifest) return;

    try {
      console.log("🖼️ Generating preview with layers:", selectedLayers);

      // Asegurar que siempre haya una base
      const layersWithBase = [...selectedLayers];

      // Verificar si ya hay una base
      const hasBase = layersWithBase.some((layer) => layer.category === "base");

      if (
        !hasBase &&
        manifest &&
        manifest.categories &&
        Array.isArray(manifest.categories.base) &&
        manifest.categories.base.length > 0
      ) {
        // Agregar la base automáticamente
        const baseAsset = manifest.categories.base[0];
        if (baseAsset) {
          console.log("🎯 Auto-adding base:", baseAsset.filename);
          layersWithBase.unshift({
            category: "base",
            filename: baseAsset.filename,
            url: baseAsset.url,
          });
        }
      }

      if (layersWithBase.length === 0) {
        console.log("⚠️ No layers to generate preview");
        return;
      }

      const blob = await avatarAPI.generateAvatar(layersWithBase, selectedGender);
      const url = URL.createObjectURL(blob);

      // Liberar URL anterior si existe
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }

      setPreviewUrl(url);

      if (onPreview) {
        onPreview(url);
      }

      console.log("✅ Preview generated successfully");
    } catch (error) {
      console.error("❌ Error generating preview:", error);
      showError("Error al generar la vista previa");
    }
  };

  const handleLayerSelect = async (category: string, asset: AssetInfo | null) => {
    if (USE_NEW_HOOK) {
      // 🎯 NEW: Use hook methods
      if (!asset) {
        avatarStudio.removeLayer(category);

        // Si el preview no está visible, hacer scroll hacia él y forzar generación inmediata
        try {
          if (previewRef.current && !isPreviewVisible) {
            previewRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
          }
          await avatarStudio.generatePreview();
        } catch (e) {
          // no-op: generar preview puede fallar si aún no hay capas
        }

        return;
      }

      const newLayer: LayerItem = {
        category,
        filename: asset.filename,
        url: asset.url,
      };

      avatarStudio.addLayer(newLayer);

      // Si el preview no está visible, hacer scroll hacia él y forzar generación inmediata
      try {
        if (previewRef.current && !isPreviewVisible) {
          previewRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
        }
        await avatarStudio.generatePreview();
      } catch (e) {
        // no-op
      }

      return;
    }

    // OLD: Keep old logic for fallback
    if (!asset) {
      const updatedLayers = selectedLayers.filter((layer) => layer.category !== category);
      setSelectedLayers(updatedLayers);

      if (selectedGender === "male") {
        setMaleLayers(updatedLayers);
      } else {
        setFemaleLayers(updatedLayers);
      }
      return;
    }

    const newLayer: LayerItem = {
      category,
      filename: asset.filename,
      url: asset.url,
    };

    const updatedLayers = (() => {
      const filtered = selectedLayers.filter((layer) => layer.category !== category);
      return [...filtered, newLayer];
    })();

    setSelectedLayers(updatedLayers);

    if (selectedGender === "male") {
      setMaleLayers(updatedLayers);
    } else {
      setFemaleLayers(updatedLayers);
    }
  };

  const getSelectedAssetForCategory = (category: string): AssetInfo | null => {
    const layers = USE_NEW_HOOK ? avatarStudio.currentLayers : selectedLayers;
    const manifestData = USE_NEW_HOOK ? avatarStudio.state.manifest : manifest;

    const layer = layers.find((l) => l.category === category);
    if (!layer || !manifestData) return null;

    const categoryAssets = manifestData.categories[category] || [];
    return categoryAssets.find((asset) => asset.filename === layer.filename) || null;
  };

  const getFilteredAssetsForCategory = (category: string, subcategory?: string | null): AssetInfo[] => {
    const manifestData = USE_NEW_HOOK ? avatarStudio.state.manifest : manifest;
    const genderFilter = USE_NEW_HOOK ? avatarStudio.state.activeGenderFilter : activeGenderFilter;

    if (!manifestData) return [];

    // Usar estructura jerárquica si está disponible (mejor organización)
    let categoryAssets: AssetInfo[] = [];
    
    if (manifestData.hierarchical && manifestData.hierarchical[category]) {
      const subcategories = manifestData.hierarchical[category];
      
      // Si hay una subcategoría activa, usar solo esa subcategoría
      if (subcategory && subcategories[subcategory]) {
        categoryAssets = subcategories[subcategory];
      } else {
        // Aplanar todas las subcategorías de la categoría actual
        categoryAssets = Object.values(subcategories).flat();
      }
    } else {
      // Fallback a estructura plana
      categoryAssets = manifestData.categories[category] || [];
    }

    console.log(`🔍 Filtering category "${category}" with gender "${genderFilter}"`, {
      totalAssets: categoryAssets.length,
      sampleAsset: categoryAssets[0],
      sampleAssetKeys: categoryAssets[0] ? Object.keys(categoryAssets[0]) : [],
    });

    // IMPORTANTE: Los filtros de género son INFORMATIVOS, NO bloquean selección
    // Mostrar todos los items pero resaltando los sugeridos
    if (genderFilter === "all") {
      console.log(`✅ Showing all ${categoryAssets.length} assets (filter: "all")`);
      return categoryAssets;
    }

    // Filtrar por género: incluir unisex siempre + el género específico
    const filtered = categoryAssets.filter((asset) => {
      // Usar tanto targetGender (camelCase) como target_gender (snake_case) para compatibilidad
      const assetGender = (asset as any).targetGender || (asset as any).target_gender || "unisex";
      const matches = assetGender === genderFilter || assetGender === "unisex";
      
      console.log(`  - ${asset.filename}: targetGender="${assetGender}" matches ${genderFilter}? ${matches}`);
      
      return matches;
    });

    console.log(`✅ Filtered ${filtered.length}/${categoryAssets.length} assets for gender "${genderFilter}"`);
    return filtered;
  };

  const handleGenderChange = (newGender: "male" | "female", genderLabel: string) => {
    if (USE_NEW_HOOK) {
      // 🎯 NEW: Use hook method with manual flag
      avatarStudio.setGender(newGender, true);
      return;
    }

    // OLD: Keep old logic
    if (genderChangeTimeout) {
      clearTimeout(genderChangeTimeout);
    }
    setIsManualGenderChange(true);
    setSelectedGender((prev) => {
      if (prev === newGender) return prev;
      if (prev === "male") {
        setMaleLayers((layers) => (selectedLayers.length ? [...selectedLayers] : layers));
      } else {
        setFemaleLayers((layers) => (selectedLayers.length ? [...selectedLayers] : layers));
      }
      return newGender;
    });
  };

  const handleVisualize = async () => {
    if (USE_NEW_HOOK) {
      // 🎯 NEW: Use hook methods
      if (!avatarStudio.hasLayers) {
        showError("Selecciona al menos un elemento para visualizar");
        return;
      }
      await avatarStudio.generatePreview();
      avatarStudio.setPreviewModal(true);
      if (onPreview && avatarStudio.state.previewUrl) {
        onPreview(avatarStudio.state.previewUrl);
      }
      return;
    }

    // OLD: Keep old logic
    if (selectedLayers.length === 0) {
      showError("Selecciona al menos un elemento para visualizar");
      return;
    }
    setShowPreviewModal(true);
  };

  const handleReset = () => {
    if (USE_NEW_HOOK) {
      avatarStudio.clearLayers();
      success("Avatar reiniciado - volviendo a base vacía");
    } else {
      const manifestData = manifest;
      if (!manifestData) return;

      // Solo mantener la base del género actual
      const baseLayer: LayerItem[] = [];
      if (manifestData.categories.base?.length > 0) {
        const baseAsset = manifestData.categories.base[0];
        baseLayer.push({
          category: "base",
          filename: baseAsset.filename,
          url: baseAsset.url,
        });
      }

      setSelectedLayers(baseLayer);
      
      // Actualizar el storage del género actual
      if (selectedGender === "male") {
        setMaleLayers(baseLayer);
      } else {
        setFemaleLayers(baseLayer);
      }

      success("Avatar reiniciado - volviendo a base original");
    }
  };

  const handleRandomize = () => {
    if (USE_NEW_HOOK) {
      avatarStudio.generateRandom();
      success("¡Avatar aleatorio generado! 🎲");
      return;
    }
    
    // OLD logic (fallback)
    const manifestData = manifest;
    if (!manifestData) {
      showError("No se pudo cargar el manifest");
      return;
    }

    const newLayers: LayerItem[] = [];

    // Siempre incluir la base
    if (manifestData.categories.base?.length > 0) {
      const baseAsset = manifestData.categories.base[0];
      newLayers.push({
        category: "base",
        filename: baseAsset.filename,
        url: baseAsset.url,
      });
    }

    // Randomizar otras categorías (usar estructura jerárquica si está disponible)
    const categoriesToRandomize = Object.keys(manifestData.categories).filter(
      (cat) => cat !== "base"
    );

    categoriesToRandomize.forEach((category) => {
      if (Math.random() > 0.4) {
        // 60% chance de incluir cada categoría
        let categoryAssets: AssetInfo[] = [];
        
        if (manifestData.hierarchical && manifestData.hierarchical[category]) {
          const subcategories = manifestData.hierarchical[category];
          categoryAssets = Object.values(subcategories).flat();
        } else {
          categoryAssets = manifestData.categories[category] || [];
        }

        if (categoryAssets.length > 0) {
          const randomAsset = categoryAssets[Math.floor(Math.random() * categoryAssets.length)];
          newLayers.push({
            category,
            filename: randomAsset.filename,
            url: randomAsset.url,
          });
        }
      }
    });

    console.log("🎲 Randomized layers:", newLayers);
    setSelectedLayers(newLayers);
    
    // Guardar en el estado correspondiente al género
    if (selectedGender === "male") {
      setMaleLayers(newLayers);
    } else {
      setFemaleLayers(newLayers);
    }

    success("Avatar aleatorio generado");
  };

  const handleSaveAvatar = async () => {
    if (selectedLayers.length === 0) {
      showError("Selecciona al menos una capa para guardar");
      return;
    }

    if (!avatarName.trim()) {
      showError("Ingresa un nombre para tu avatar");
      return;
    }

    try {
      console.log("💾 Saving avatar:", {
        name: avatarName,
        gender: selectedGender,
        layers: selectedLayers,
      });
      // Guardar en la base de datos usando la API
      const savedAvatar = await avatarAPI.saveAvatar(
        avatarName.trim(),
        selectedGender,
        selectedLayers,
        true, // Activar este avatar
        true // Hacer público
      );

      console.log("✅ Avatar saved successfully:", savedAvatar);

      // Guardar en localStorage como backup
      const avatarData = {
        id: savedAvatar.id,
        name: savedAvatar.name,
        layers: selectedLayers,
        timestamp: new Date().toISOString(),
      };
      localStorage.setItem("saved_avatar", JSON.stringify(avatarData));

      // Actualizar la navegación para mostrar el nuevo avatar
      window.dispatchEvent(new CustomEvent("avatar-updated", { detail: savedAvatar }));

      success(`Avatar "${avatarName}" guardado exitosamente`);

      // Limpiar el nombre para el siguiente avatar
      setAvatarName("");
    } catch (error) {
      console.error("Error saving avatar:", error);
      showError(
        `Error al guardar el avatar: ${
          error instanceof Error ? error.message : "Error desconocido"
        }`
      );
    }
  };

  const handleSave = async () => {
    if (USE_NEW_HOOK) {
      // 🎯 NEW: Use hook method with validation
      if (!avatarStudio.state.avatarName.trim()) {
        showError("Por favor ingresa un nombre para el avatar");
        return;
      }

      if (!avatarStudio.hasLayers) {
        showError("Selecciona al menos un elemento para el avatar");
        return;
      }

      if (!isAuthenticated) {
        showError("Debes iniciar sesión para guardar avatares");
        warning("Serás redirigido al login");
        setTimeout(() => {
          window.location.href = "/login";
        }, 2000);
        return;
      }

      try {
        await avatarStudio.saveAvatar();
        success(`Avatar "${avatarStudio.state.avatarName}" guardado exitosamente`);

        if (onSave) {
          await onSave({
            name: avatarStudio.state.avatarName,
            gender: avatarStudio.state.selectedGender,
            layers: avatarStudio.currentLayers,
          });
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Error desconocido";
        if (
          errorMessage.includes("sesión ha expirado") ||
          errorMessage.includes("No estás autenticado")
        ) {
          showError("Tu sesión ha expirado. Inicia sesión nuevamente.");
          warning("Serás redirigido al login en unos segundos...");
          setTimeout(() => {
            window.location.href = "/login";
          }, 3000);
        } else {
          showError(`Error al guardar el avatar: ${errorMessage}`);
        }
      }
      return;
    }

    // OLD: Keep old logic
    if (!avatarName.trim()) {
      showError("Por favor ingresa un nombre para el avatar");
      return;
    }

    if (selectedLayers.length === 0) {
      showError("Selecciona al menos un elemento para el avatar");
      return;
    }

    if (!isAuthenticated) {
      showError("Debes iniciar sesión para guardar avatares");
      warning("Serás redirigido al login");
      setTimeout(() => {
        window.location.href = "/login";
      }, 2000);
      return;
    }

    // Debug: Verificar estado de autenticación
    const token = localStorage.getItem("access_token");
    console.log("🔐 DEBUG: Authentication state:", {
      isAuthenticated,
      hasToken: !!token,
      tokenPreview: token ? token.substring(0, 30) + "..." : "NO_TOKEN",
    });

    try {
      setSaving(true);

      console.log("💾 handleSave: Starting save process:", {
        name: avatarName,
        gender: selectedGender,
        layers: selectedLayers,
      });

      // Guardar en la base de datos usando la API (la API manejará la conversión)
      const savedAvatar = await avatarAPI.saveAvatar(
        avatarName.trim(),
        selectedGender,
        selectedLayers, // Pasar directamente selectedLayers
        true, // Activar este avatar
        true // Hacer público
      );

      console.log("✅ handleSave: Avatar saved successfully:", savedAvatar);

      // Guardar en localStorage como backup
      const avatarData = {
        id: savedAvatar.id,
        name: savedAvatar.name,
        layers: selectedLayers,
        timestamp: new Date().toISOString(),
      };
      localStorage.setItem("saved_avatar", JSON.stringify(avatarData));

      // Llamar callback si existe
      if (onSave) {
        await onSave({
          name: avatarName,
          gender: selectedGender,
          layers: selectedLayers,
        });
      }

      // Actualizar la navegación para mostrar el nuevo avatar
      console.log("📢 handleSave: Dispatching avatar-updated event");
      window.dispatchEvent(
        new CustomEvent("avatar-updated", {
          detail: {
            ...savedAvatar,
            timestamp: Date.now(), // Para forzar refresh
            action: "saved",
          },
        })
      );

      // También disparar evento global de refresh
      window.dispatchEvent(
        new CustomEvent("avatar-refresh", {
          detail: {
            userId: savedAvatar.user_id,
            avatarId: savedAvatar.id,
            timestamp: Date.now(),
          },
        })
      );

      success(`Avatar "${avatarName}" guardado exitosamente`);
    } catch (error) {
      console.error("❌ handleSave: Error saving avatar:", error);

      const errorMessage = error instanceof Error ? error.message : "Error desconocido";

      // Manejo especial para errores de autenticación
      if (
        errorMessage.includes("sesión ha expirado") ||
        errorMessage.includes("No estás autenticado")
      ) {
        showError("Tu sesión ha expirado. Inicia sesión nuevamente.");
        warning("Serás redirigido al login en unos segundos...");
        setTimeout(() => {
          window.location.href = "/login";
        }, 3000);
      } else {
        showError(`Error al guardar el avatar: ${errorMessage}`);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleDownload = () => {
    const urlToDownload = USE_NEW_HOOK ? avatarStudio.state.previewUrl : previewUrl;

    if (!urlToDownload) {
      showError("Genera un avatar primero");
      return;
    }

    try {
      const link = document.createElement("a");
      link.href = urlToDownload;
      link.download = `avatar-${actualAvatarName || "custom"}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      success("Avatar descargado");
    } catch (err) {
      console.error("❌ Error al descargar avatar:", err);
      showError("No se pudo descargar el avatar");
    }
  };

  // Configuración de categorías con iconos y nombres modernos
  const getCategoryConfig = () => [
    {
      key: "hair",
      label: "Cabello",
      icon: Sparkles,
      color: "from-amber-500 to-orange-500",
      description: "Estilos",
    },
    {
      key: "eyes",
      label: "Ojos",
      icon: Eye,
      color: "from-blue-500 to-indigo-500",
      description: "Forma",
    },
    {
      key: "mouth",
      label: "Boca",
      icon: Heart,
      color: "from-pink-500 to-rose-500",
      description: "Expresión",
    },
    {
      key: "makeup",
      label: "Maquillaje",
      icon: Palette,
      color: "from-purple-500 to-violet-500",
      description: "Detalles",
    },
    {
      key: "shirt",
      label: "Camisas",
      icon: Shirt,
      color: "from-green-500 to-emerald-500",
      description: "Tops",
    },
    {
      key: "pants",
      label: "Pantalones",
      icon: Grid3x3,
      color: "from-blue-600 to-blue-700",
      description: "Leggins",
    },
    {
      key: "skirt",
      label: "Faldas",
      icon: Grid3x3,
      color: "from-pink-500 to-rose-500",
      description: "Vestidos",
    },
    {
      key: "shoes",
      label: "Zapatos",
      icon: Grid3x3,
      color: "from-gray-600 to-gray-700",
      description: "Calzado",
    },
    {
      key: "socks",
      label: "Medias",
      icon: Grid3x3,
      color: "from-purple-500 to-violet-500",
      description: "Calcetines",
    },
    {
      key: "jacket",
      label: "Chaquetas",
      icon: Grid3x3,
      color: "from-indigo-600 to-purple-600",
      description: "Sacos",
    },
    {
      key: "accessories",
      label: "Accesorios",
      icon: Watch,
      color: "from-yellow-500 to-amber-500",
      description: "Extras",
    },
    {
      key: "backgrounds",
      label: "Fondos",
      icon: Palette,
      color: "from-teal-500 to-cyan-500",
      description: "Escenarios",
    },
  ];

  if (actualLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-blue-900/20 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg p-12 rounded-3xl shadow-2xl"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: 2, ease: "linear" }}
            className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full mx-auto mb-6"
          />
          <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
            Preparando el estudio
          </h3>
          <p className="text-gray-600 dark:text-gray-400">Cargando elementos del avatar...</p>
        </motion.div>
      </div>
    );
  }

  if (actualError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-blue-900/20 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg p-12 rounded-3xl shadow-2xl max-w-md"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", bounce: 0.5 }}
            className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-6"
          >
            <X className="text-3xl text-red-600 dark:text-red-400" />
          </motion.div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">
            Oops, algo salió mal
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-8">{error}</p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => (USE_NEW_HOOK ? avatarStudio.loadManifest() : loadManifest())}
            className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all"
          >
            <RefreshCw className="inline mr-2" />
            Reintentar
          </motion.button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-blue-900/20 mt-6">
      {/* Modal de preview grande */}
      <AnimatePresence>
        {actualShowPreviewModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
            onClick={() =>
              USE_NEW_HOOK ? avatarStudio.setPreviewModal(false) : setShowPreviewModal(false)
            }
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 relative flex flex-col items-center"
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={actualPreviewUrl}
                alt="Preview Avatar"
                className="w-[400px] h-[400px] rounded-2xl border-4 border-blue-500 bg-white object-contain"
                style={{ objectPosition: "center 25%" }}
              />
              <button
                className="absolute top-4 right-4 w-10 h-10 bg-white/80 rounded-full flex items-center justify-center hover:bg-white"
                onClick={() =>
                  USE_NEW_HOOK ? avatarStudio.setPreviewModal(false) : setShowPreviewModal(false)
                }
              >
                <X className="text-gray-700 text-xl" />
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header mejorado */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center mb-6">
            <motion.div
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 4, repeat: 3, ease: "easeInOut" }}
              className="w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl flex items-center justify-center mr-4 shadow-lg"
            >
              <Sparkles className="text-3xl text-white" />
            </motion.div>
            <div>
              <h1 className="text-5xl font-black bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Estudio de Avatars
              </h1>
              <p className="text-gray-600 dark:text-gray-400 text-lg font-medium mt-2">
                Diseña tu identidad digital única
              </p>
            </div>
          </div>
        </motion.div>

        <div className="grid xl:grid-cols-5 gap-8">
          {/* Panel de Preview Mejorado */}
          <div className="xl:col-span-2">
            <motion.div
              ref={previewRef}
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              className="sticky top-24 self-start bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20 dark:border-gray-700/30"
            >
              {/* Header del Panel */}
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl flex items-center justify-center mr-3">
                    <Eye className="text-white text-lg" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                      Vista Previa
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Tu avatar personalizado
                    </p>
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => (USE_NEW_HOOK ? avatarStudio.loadManifest() : loadManifest())}
                  className="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-xl flex items-center justify-center hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  <RefreshCw className="text-gray-600 dark:text-gray-400" />
                </motion.button>
              </div>

              {/* Selector de Género Mejorado */}
              <div className="mb-8">
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
                  Identidad de Género
                </label>
                <div className="grid grid-cols-2 gap-3 p-2 bg-gray-100 dark:bg-gray-700 rounded-2xl">
                  {[
                    { value: "male", label: "Masculino", icon: User },
                    { value: "female", label: "Femenino", icon: User },
                  ].map((gender) => (
                    <motion.button
                      key={gender.value}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() =>
                        handleGenderChange(gender.value as "male" | "female", gender.label)
                      }
                      className={`relative overflow-hidden py-4 px-4 rounded-xl font-semibold transition-all duration-300 ${
                        actualGender === gender.value
                          ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg"
                          : "bg-white dark:bg-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-500"
                      }`}
                    >
                      <gender.icon className="inline mr-2 text-lg" />
                      {gender.label}
                      {actualGender === gender.value && (
                        <motion.div
                          layoutId="genderSelector"
                          className="absolute inset-0 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl -z-10"
                        />
                      )}
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Preview del Avatar Mejorado */}
              <div className="relative bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 rounded-2xl p-8 mb-8 min-h-[400px] flex items-center justify-center overflow-hidden">
                {/* Fondo decorativo */}
                <div className="absolute inset-0 opacity-5">
                  <div className="absolute top-4 left-4 w-16 h-16 bg-purple-500 rounded-full blur-xl"></div>
                  <div className="absolute bottom-4 right-4 w-20 h-20 bg-blue-500 rounded-full blur-xl"></div>
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-indigo-500 rounded-full blur-2xl"></div>
                </div>

                {actualPreviewUrl ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.5, y: 50 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ type: "spring", damping: 20, stiffness: 300 }}
                    className="relative z-10"
                  >
                    <motion.img
                      whileHover={{ scale: 1.05 }}
                      src={actualPreviewUrl}
                      alt="Avatar Preview"
                      className="max-w-full max-h-full object-contain rounded-xl shadow-2xl"
                    />
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="absolute -inset-4 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-2xl blur-xl -z-10"
                    />
                  </motion.div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center text-gray-400 dark:text-gray-500 z-10"
                  >
                    <motion.div
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 3, repeat: 2 }}
                      className="w-20 h-20 bg-gray-200 dark:bg-gray-600 rounded-2xl flex items-center justify-center mx-auto mb-6"
                    >
                      <User className="text-4xl" />
                    </motion.div>
                    <h4 className="text-lg font-semibold mb-2">Tu lienzo está listo</h4>
                    <p className="text-sm">Selecciona elementos para crear tu avatar</p>
                  </motion.div>
                )}
              </div>

              {/* Controles Mejorados */}
              <div className="space-y-6">
                {/* Input del nombre */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Nombre del Avatar
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={actualAvatarName}
                      onChange={(e) =>
                        USE_NEW_HOOK
                          ? avatarStudio.setAvatarName(e.target.value)
                          : setAvatarName(e.target.value)
                      }
                      placeholder="Dale vida con un nombre único..."
                      className="w-full px-4 py-4 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500"
                    />
                    <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                      <User className="text-gray-400" />
                    </div>
                  </div>
                </div>

                {/* Botones de acción */}
                <div className="grid grid-cols-4 gap-3">
                  <motion.button
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleReset}
                    className="bg-gradient-to-r from-red-500 to-pink-500 text-white py-3 px-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all group"
                    title="Reiniciar avatar a base original (deshacer todo)"
                  >
                    <RotateCcw className="inline mr-2" />
                    <span className="text-sm">Reset</span>
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleRandomize}
                    className="bg-gradient-to-r from-amber-500 to-orange-500 text-white py-3 px-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all group"
                  >
                    <Shuffle className="inline mr-2" />
                    <span className="text-sm">Aleatorio</span>
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleDownload}
                    disabled={!actualPreviewUrl}
                    className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white py-3 px-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                  >
                    <Download className="inline mr-2" />
                    <span className="text-sm">Descargar</span>
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleVisualize}
                    disabled={actualLayers.length === 0 || actualVisualizing}
                    className="bg-gradient-to-r from-teal-500 to-cyan-500 text-white py-3 px-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                    title="Generar vista previa actualizada del avatar"
                  >
                    {actualVisualizing ? (
                      <div className="flex items-center justify-center">
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: 2, ease: "linear" }}
                          className="w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"
                        />
                        <span className="text-sm">Generando...</span>
                      </div>
                    ) : (
                      <>
                        <Eye className="inline mr-2" />
                        <span className="text-sm">Preview</span>
                      </>
                    )}
                  </motion.button>
                </div>

                {/* Botón de guardar principal */}
                <motion.button
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSave}
                  disabled={
                    actualSaving ||
                    !actualAvatarName.trim() ||
                    actualLayers.length === 0 ||
                    !isAuthenticated
                  }
                  className={`relative w-full py-5 px-6 rounded-xl font-bold text-lg shadow-xl hover:shadow-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden group ${
                    !isAuthenticated
                      ? "bg-gradient-to-r from-gray-500 to-gray-600 text-white"
                      : "bg-gradient-to-r from-green-600 to-emerald-600 text-white"
                  }`}
                >
                  {actualSaving ? (
                    <div className="flex items-center justify-center">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: 2, ease: "linear" }}
                        className="w-6 h-6 border-2 border-white border-t-transparent rounded-full mr-3"
                      />
                      Creando tu avatar...
                    </div>
                  ) : !isAuthenticated ? (
                    <div className="flex items-center justify-center">
                      <User className="mr-3 text-xl" />
                      Inicia sesión para guardar
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center justify-center">
                        <Save className="mr-3 text-xl" />
                        Guardar Avatar
                      </div>
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-green-400 to-emerald-400 opacity-0 group-hover:opacity-20 transition-opacity"
                        whileHover={{ scale: 1.05 }}
                      />
                    </>
                  )}
                </motion.button>
              </div>
            </motion.div>
          </div>

          {/* Panel de Categorías Mejorado */}
          <div className="xl:col-span-3">
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20 dark:border-gray-700/30"
            >
              {/* Header del Panel de Personalización */}
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mr-3">
                    <Palette className="text-white text-lg" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                      Personalización
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {actualManifest &&
                        Object.values(actualManifest.categories).reduce(
                          (acc, assets) => acc + assets.length,
                          0
                        )}{" "}
                      elementos disponibles
                    </p>
                  </div>
                </div>
                <motion.div
                  animate={{ rotate: [0, 5, -5, 0] }}
                  transition={{ duration: 3, repeat: Infinity }}
                  className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center"
                >
                  <Sparkles className="text-purple-600 dark:text-purple-400" />
                </motion.div>
              </div>

              {actualManifest && (
                <div className="space-y-8">
                  {/* Navegación de Categorías Mejorada */}
                  <div className="relative">
                    <div className="flex flex-wrap gap-3">
                      {actualManifest &&
                        getCategoryConfig()
                          .filter(
                            (category) =>
                              actualManifest.categories[category.key] &&
                              actualManifest.categories[category.key].length > 0
                          )
                          .map((category, index) => {
                            const IconComponent = category.icon;
                            const isActive = actualActiveCategory === category.key;

                            return (
                              <motion.button
                                key={category.key}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.05 }}
                                whileHover={{ scale: 1.05, y: -2 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => {
                                  if (USE_NEW_HOOK) {
                                    avatarStudio.setActiveCategory(category.key);
                                    avatarStudio.setGenderFilter("all");
                                  } else {
                                    setActiveCategory(category.key);
                                    setActiveGenderFilter("all");
                                  }
                                }}
                                className={`relative overflow-hidden group px-3 py-2.5 rounded-xl font-semibold text-sm transition-all duration-300 ${
                                  isActive
                                    ? "text-white shadow-lg"
                                    : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 shadow-sm"
                                }`}
                              >
                                {isActive && (
                                  <motion.div
                                    layoutId="activeCategory"
                                    className={`absolute inset-0 bg-gradient-to-r ${category.color} rounded-xl`}
                                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                  />
                                )}
                                <div className="relative flex items-center gap-1.5">
                                  <IconComponent className="w-4 h-4" />
                                  <div className="flex flex-col items-start">
                                    <span className="font-bold text-xs leading-tight">{category.label}</span>
                                    <span
                                      className={`text-[10px] leading-tight ${
                                        isActive ? "text-white/70" : "text-gray-400"
                                      }`}
                                    >
                                      {category.description}
                                    </span>
                                  </div>
                                </div>
                                {!isActive && (
                                  <motion.div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 to-blue-500/0 group-hover:from-purple-500/10 group-hover:to-blue-500/10 rounded-xl transition-all duration-300" />
                                )}
                              </motion.button>
                            );
                          })}
                        </div>
                      </div>

                  {/* Contenido de la Categoría Activa */}
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeCategory}
                      initial={{ opacity: 0, y: 30 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -30 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-6"
                    >
                      {/* Filtros de Género Rediseñados */}
                      {actualActiveCategory !== "base" && (
                        <div className="space-y-4">
                          {/* Header de Filtros */}
                          <div className="flex items-center gap-2 px-1">
                            <Filter className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                            <span className="text-sm font-bold text-gray-800 dark:text-gray-200">
                              Filtrar por género
                            </span>
                            <div className="flex-1 h-px bg-gradient-to-r from-purple-200 to-transparent dark:from-purple-800" />
                          </div>
                          
                          {/* Botones de Filtro */}
                          <div className="flex gap-3 flex-wrap">
                            {[
                              { key: "all", label: "Todos", icon: Grid },
                              { key: "male", label: "Hombre", icon: User },
                              { key: "female", label: "Mujer", icon: User },
                              { key: "unisex", label: "Unisex", icon: Users },
                            ].map((filter) => {
                              const FilterIcon = filter.icon;
                              const isActive = actualGenderFilter === filter.key;
                              
                              // Obtener assets de la categoría actual (jerárquica o plana)
                              let categoryAssets: AssetInfo[] = [];
                              if (actualManifest?.hierarchical && actualManifest.hierarchical[actualActiveCategory]) {
                                const subcategories = actualManifest.hierarchical[actualActiveCategory];
                                categoryAssets = Object.values(subcategories).flat();
                              } else {
                                categoryAssets = actualManifest?.categories[actualActiveCategory] || [];
                              }
                              
                              // Calcular count con compatibilidad snake_case y camelCase
                              const filteredCount =
                                filter.key === "all"
                                  ? categoryAssets.length
                                  : categoryAssets.filter((asset) => {
                                      const assetGender = (asset as any).targetGender || (asset as any).target_gender || "unisex";
                                      return assetGender === filter.key || assetGender === "unisex";
                                    }).length;

                              return (
                                <motion.button
                                  key={filter.key}
                                  whileHover={{ scale: 1.03, y: -2 }}
                                  whileTap={{ scale: 0.97 }}
                                  onClick={() =>
                                    USE_NEW_HOOK
                                      ? avatarStudio.setGenderFilter(
                                          filter.key as "all" | "male" | "female" | "unisex"
                                        )
                                      : setActiveGenderFilter(filter.key)
                                  }
                                  className={`group relative px-5 py-3 rounded-xl font-semibold transition-all duration-300 border-2 ${
                                    filter.key === "all"
                                      ? isActive
                                        ? "bg-gradient-to-br from-gray-600 via-gray-700 to-gray-800 text-white border-gray-600 shadow-xl shadow-gray-500/30"
                                        : "bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:border-gray-400 hover:shadow-lg"
                                      : filter.key === "male"
                                      ? isActive
                                        ? "bg-gradient-to-br from-blue-500 via-blue-600 to-blue-700 text-white border-blue-500 shadow-xl shadow-blue-500/30"
                                        : "bg-white dark:bg-gray-800 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-600 hover:border-blue-400 hover:shadow-lg hover:shadow-blue-500/20"
                                      : filter.key === "female"
                                      ? isActive
                                        ? "bg-gradient-to-br from-pink-500 via-pink-600 to-pink-700 text-white border-pink-500 shadow-xl shadow-pink-500/30"
                                        : "bg-white dark:bg-gray-800 text-pink-700 dark:text-pink-300 border-pink-300 dark:border-pink-600 hover:border-pink-400 hover:shadow-lg hover:shadow-pink-500/20"
                                      : isActive
                                      ? "bg-gradient-to-br from-purple-500 via-purple-600 to-purple-700 text-white border-purple-500 shadow-xl shadow-purple-500/30"
                                      : "bg-white dark:bg-gray-800 text-purple-700 dark:text-purple-300 border-purple-300 dark:border-purple-600 hover:border-purple-400 hover:shadow-lg hover:shadow-purple-500/20"
                                  }`}
                                  title={`Filtrar por ${filter.label.toLowerCase()}: ${filteredCount} items disponibles`}
                                >
                                  <div className="flex items-center gap-2.5">
                                    <div className={`p-1.5 rounded-lg ${
                                      isActive 
                                        ? "bg-white/20" 
                                        : filter.key === "all"
                                        ? "bg-gray-100 dark:bg-gray-700 group-hover:bg-gray-200"
                                        : filter.key === "male"
                                        ? "bg-blue-100 dark:bg-blue-900/30 group-hover:bg-blue-200"
                                        : filter.key === "female"
                                        ? "bg-pink-100 dark:bg-pink-900/30 group-hover:bg-pink-200"
                                        : "bg-purple-100 dark:bg-purple-900/30 group-hover:bg-purple-200"
                                    }`}>
                                      <FilterIcon className={`w-4 h-4 ${
                                        isActive ? "text-white" : ""
                                      }`} />
                                    </div>
                                    <span className="text-sm">{filter.label}</span>
                                    <div className={`ml-auto px-2.5 py-1 rounded-lg text-xs font-bold ${
                                      isActive
                                        ? "bg-white/25 text-white backdrop-blur-sm"
                                        : filter.key === "all"
                                        ? "bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200"
                                        : filter.key === "male"
                                        ? "bg-blue-200 dark:bg-blue-900/50 text-blue-900 dark:text-blue-100"
                                        : filter.key === "female"
                                        ? "bg-pink-200 dark:bg-pink-900/50 text-pink-900 dark:text-pink-100"
                                        : "bg-purple-200 dark:bg-purple-900/50 text-purple-900 dark:text-purple-100"
                                    }`}>
                                      {filteredCount}
                                    </div>
                                  </div>
                                  
                                  {/* Indicador de activo */}
                                  {isActive && (
                                    <motion.div
                                      layoutId="activeGenderFilter"
                                      className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-2 h-2 rounded-full bg-white shadow-lg"
                                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                                    />
                                  )}
                                </motion.button>
                              );
                            })}
                          </div>

                          {/* Mensaje informativo mejorado */}
                          <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="flex items-start gap-3 px-4 py-3 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border-l-4 border-purple-500 dark:border-purple-400 rounded-lg"
                          >
                            <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                              <p className="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-1">
                                Los filtros son sugerencias
                              </p>
                              <p className="text-xs text-gray-600 dark:text-gray-400">
                                Puedes usar cualquier item independientemente del género. ¡Crea tu avatar único!
                              </p>
                            </div>
                          </motion.div>
                        </div>
                      )}

                      {/* Tabs de Subcategorías Rediseñados */}
                      {actualManifest?.hierarchical && actualManifest.hierarchical[actualActiveCategory] && (
                        <div className="space-y-3">
                          {/* Header de Subcategorías */}
                          <div className="flex items-center gap-2 px-1">
                            <Grid3x3 className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                            <span className="text-sm font-bold text-gray-800 dark:text-gray-200">
                              Subcategorías
                            </span>
                            <div className="flex-1 h-px bg-gradient-to-r from-blue-200 to-transparent dark:from-blue-800" />
                          </div>
                          
                          {/* Tabs Container */}
                          <div className="relative bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800/50 dark:to-gray-900/30 p-1.5 rounded-2xl border border-gray-200 dark:border-gray-700">
                            <div className="flex gap-2 flex-wrap">
                              {/* Botón "Todos" */}
                              <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => setActiveSubcategory(null)}
                                className={`relative px-5 py-2.5 rounded-xl font-semibold text-sm transition-all duration-300 ${
                                  activeSubcategory === null
                                    ? "bg-gradient-to-br from-white to-gray-50 dark:from-gray-700 dark:to-gray-800 text-gray-900 dark:text-white shadow-lg border-2 border-purple-300 dark:border-purple-600"
                                    : "bg-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                                }`}
                              >
                                <div className="flex items-center gap-2">
                                  <Grid className="w-4 h-4" />
                                  <span>Todos</span>
                                </div>
                                {activeSubcategory === null && (
                                  <motion.div
                                    layoutId="activeSubcategory"
                                    className="absolute inset-0 bg-gradient-to-r from-purple-100/50 to-blue-100/50 dark:from-purple-900/30 dark:to-blue-900/30 rounded-xl -z-10"
                                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                                  />
                                )}
                              </motion.button>

                              {/* Botones de subcategorías */}
                              {Object.keys(actualManifest.hierarchical[actualActiveCategory]).map((subcat) => {
                                const isActive = activeSubcategory === subcat;
                                
                                // Mapeo de iconos y nombres para subcategorías
                                let IconComponent = Sparkles;
                                let label = subcat.charAt(0).toUpperCase() + subcat.slice(1);
                                
                                if (subcat === "head") { IconComponent = User; label = "Cabeza"; }
                                else if (subcat === "face") { IconComponent = Eye; label = "Cara"; }
                                else if (subcat === "hand") { IconComponent = Hand; label = "Mano"; }
                                else if (subcat === "wrist") { IconComponent = Watch; label = "Muñeca"; }
                                else if (subcat === "neck") { IconComponent = Heart; label = "Cuello"; }
                                else if (subcat === "body") { IconComponent = Palette; label = "Cuerpo"; }
                                
                                return (
                                  <motion.button
                                    key={subcat}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => setActiveSubcategory(subcat)}
                                    className={`relative px-5 py-2.5 rounded-xl font-semibold text-sm transition-all duration-300 ${
                                      isActive
                                        ? "bg-gradient-to-br from-white to-gray-50 dark:from-gray-700 dark:to-gray-800 text-gray-900 dark:text-white shadow-lg border-2 border-purple-300 dark:border-purple-600"
                                        : "bg-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                                    }`}
                                  >
                                    <div className="flex items-center gap-2">
                                      <IconComponent className="w-4 h-4" />
                                      <span>{label}</span>
                                    </div>
                                    {isActive && (
                                      <motion.div
                                        layoutId="activeSubcategory"
                                        className="absolute inset-0 bg-gradient-to-r from-purple-100/50 to-blue-100/50 dark:from-purple-900/30 dark:to-blue-900/30 rounded-xl -z-10"
                                        transition={{ type: "spring", stiffness: 500, damping: 30 }}
                                      />
                                    )}
                                  </motion.button>
                                );
                              })}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Grid de Assets Mejorado */}
                      <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-8">
                        {/* Opción "Ninguno" mejorada */}
                        {actualActiveCategory !== "base" && (
                          <motion.button
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            whileHover={{ scale: 1.05, y: -2 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => handleLayerSelect(actualActiveCategory, null)}
                            className={`aspect-square rounded-2xl border-2 transition-all duration-300 flex flex-col items-center justify-center p-4 group ${
                              !getSelectedAssetForCategory(actualActiveCategory)
                                ? "border-purple-500 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 shadow-lg ring-2 ring-purple-200 dark:ring-purple-700"
                                : "border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-md"
                            }`}
                          >
                            <motion.div
                              whileHover={{ rotate: 180 }}
                              transition={{ duration: 0.3 }}
                              className={`text-3xl mb-2 ${
                                !getSelectedAssetForCategory(activeCategory)
                                  ? "text-purple-600 dark:text-purple-400"
                                  : "text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-400"
                              }`}
                            >
                              <X />
                            </motion.div>
                            <span
                              className={`text-xs font-medium ${
                                !getSelectedAssetForCategory(activeCategory)
                                  ? "text-purple-600 dark:text-purple-400"
                                  : "text-gray-500 dark:text-gray-400"
                              }`}
                            >
                              Sin{" "}
                              {getCategoryConfig()
                                .find((c) => c.key === activeCategory)
                                ?.label?.toLowerCase()}
                            </span>
                          </motion.button>
                        )}

                        {/* Assets de la categoría */}
                        {getFilteredAssetsForCategory(actualActiveCategory, activeSubcategory).map((asset, index) => {
                          const isSelected =
                            getSelectedAssetForCategory(actualActiveCategory)?.filename ===
                            asset.filename;

                          return (
                            <motion.button
                              key={asset.filename}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{
                                opacity: 1,
                                scale: 1,
                                transition: { delay: index * 0.05 },
                              }}
                              whileHover={{ scale: 1.05, y: -4 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => handleLayerSelect(actualActiveCategory, asset)}
                              className={`aspect-square rounded-2xl border-2 overflow-hidden transition-all duration-300 relative group ${
                                isSelected
                                  ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20 shadow-xl ring-2 ring-purple-200 dark:ring-purple-700"
                                  : "border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-lg"
                              }`}
                            >
                              <img
                                src={asset.url}
                                alt={asset.filename}
                                className="w-full h-full object-contain transition-transform duration-200 group-hover:scale-110"
                                loading="lazy"
                                onError={(e) => {
                                  console.error("Error loading image:", asset.url);
                                  e.currentTarget.style.display = "none";
                                }}
                              />

                              {/* Overlay de selección */}
                              {isSelected && (
                                <motion.div
                                  initial={{ opacity: 0 }}
                                  animate={{ opacity: 1 }}
                                  className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center"
                                >
                                  <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ delay: 0.1, type: "spring", bounce: 0.5 }}
                                    className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center shadow-lg"
                                  >
                                    <Check className="text-white text-sm" />
                                  </motion.div>
                                </motion.div>
                              )}

                              {/* Badge de género INFORMATIVO (NO bloquea selección) */}
                              <div
                                className={`absolute top-2 right-2 px-2 py-1 rounded-lg text-xs font-semibold backdrop-blur-md shadow-lg transition-all ${
                                  asset.targetGender === "male"
                                    ? "bg-blue-500/95 text-white border border-blue-300/50"
                                    : asset.targetGender === "female"
                                    ? "bg-pink-500/95 text-white border border-pink-300/50"
                                    : "bg-purple-500/95 text-white border border-purple-300/50"
                                }`}
                                title={`Sugerido para avatares ${
                                  asset.targetGender === "male" ? "masculinos" : 
                                  asset.targetGender === "female" ? "femeninos" : 
                                  "unisex (todos)"
                                } - Puedes usarlo en cualquier avatar`}
                              >
                                {asset.targetGender === "male" ? (
                                  <span className="flex items-center gap-1">♂ Hombre</span>
                                ) : asset.targetGender === "female" ? (
                                  <span className="flex items-center gap-1">♀ Mujer</span>
                                ) : (
                                  <span className="flex items-center gap-1">⚲ Unisex</span>
                                )}
                              </div>

                              {/* Badge de subcategoría (si existe) */}
                              {asset.subcategory && asset.subcategory !== "other" && (
                                <div className="absolute top-2 left-2 px-2 py-1 rounded-lg text-xs font-medium bg-white/90 dark:bg-gray-800/90 text-gray-700 dark:text-gray-300 backdrop-blur-sm shadow-md capitalize">
                                  {asset.subcategory}
                                </div>
                              )}

                              {/* Hover effect */}
                              <motion.div className="absolute inset-0 bg-gradient-to-t from-black/0 via-transparent to-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                            </motion.button>
                          );
                        })}
                      </div>

                      {/* Estado vacío mejorado */}
                      {getFilteredAssetsForCategory(actualActiveCategory, activeSubcategory).length === 0 && (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-center py-16"
                        >
                          <motion.div
                            animate={{ scale: [1, 1.1, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                            className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-6"
                          >
                            <Filter className="text-3xl text-gray-400 dark:text-gray-500" />
                          </motion.div>
                          <h4 className="text-lg font-semibold text-gray-600 dark:text-gray-400 mb-2">
                            No hay elementos que coincidan
                          </h4>
                          <p className="text-sm text-gray-500 dark:text-gray-500">
                            Intenta con un filtro diferente para ver más opciones
                          </p>
                        </motion.div>
                      )}
                    </motion.div>
                  </AnimatePresence>
                  </div>
              )}

              {/* Estado cuando no hay manifest */}
              {USE_NEW_HOOK &&
                (!avatarStudio.state.manifest ||
                  Object.keys(avatarStudio.state.manifest.categories || {}).length === 0) && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center py-16"
                  >
                    <motion.div
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-6"
                    >
                      <User className="text-3xl text-gray-400 dark:text-gray-500" />
                    </motion.div>
                    <h4 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-3">
                      Preparando el catálogo
                    </h4>
                    <p className="text-gray-500 dark:text-gray-500 mb-6">
                      Los elementos se están cargando automáticamente...
                    </p>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      className="w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full mx-auto"
                    />
                  </motion.div>
                )}
              {!USE_NEW_HOOK && (!manifest || Object.keys(manifest.categories).length === 0) && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center py-16"
                >
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => (USE_NEW_HOOK ? avatarStudio.loadManifest() : loadManifest())}
                    className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-xl font-semibold shadow-lg"
                  >
                    <RefreshCw className="inline mr-2" />
                    Cargar elementos
                  </motion.button>
                </motion.div>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AvatarStudioV2;
