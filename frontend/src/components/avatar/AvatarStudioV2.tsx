import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiShuffle, 
  FiDownload, 
  FiSave, 
  FiRefreshCw,
  FiUser,
  FiEye,
  FiFilter,
  FiGrid,
  FiHeart,
  FiStar,
  FiCheck,
  FiX,
  FiUsers
} from 'react-icons/fi';
import { HiSparkles, HiColorSwatch } from 'react-icons/hi';
import { GiMale, GiFemale } from 'react-icons/gi';

import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import { avatarAPI, LayerItem, AssetInfo, ManifestResponse } from './avatarAPI';

interface AvatarStudioV2Props {
  onSave?: (avatar: any) => void;
  onPreview?: (previewUrl: string) => void;
}

const AvatarStudioV2: React.FC<AvatarStudioV2Props> = ({ onSave, onPreview }) => {
  const { success, error: showError, info, warning } = useToast();
  const { isAuthenticated } = useAuth();

  // Refs para limpieza
  const saveToLocalStorage = useRef<number | null>(null);
  const hasShownInitialAvatarToast = useRef(false);
  const lastPreviewLayers = useRef<string>('');

  // Estados principales
  const [selectedGender, setSelectedGender] = useState<'male' | 'female'>('male');
  const [manifest, setManifest] = useState<ManifestResponse | null>(null);
  const [selectedLayers, setSelectedLayers] = useState<LayerItem[]>([]);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [avatarName, setAvatarName] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estados para persistencia de capas por género (con localStorage)
  const [maleLayers, setMaleLayers] = useState<LayerItem[]>(() => {
    const saved = localStorage.getItem('avatar_male_layers');
    return saved ? JSON.parse(saved) : [];
  });
  const [femaleLayers, setFemaleLayers] = useState<LayerItem[]>(() => {
    const saved = localStorage.getItem('avatar_female_layers');
    return saved ? JSON.parse(saved) : [];
  });

  // Sincronizar cambios con localStorage - optimizado con debounce
  useEffect(() => {
    if (saveToLocalStorage.current) clearTimeout(saveToLocalStorage.current);
    saveToLocalStorage.current = setTimeout(() => {
      localStorage.setItem('avatar_male_layers', JSON.stringify(maleLayers));
    }, 500);
  }, [maleLayers]);
  
  useEffect(() => {
    if (saveToLocalStorage.current) clearTimeout(saveToLocalStorage.current);
    saveToLocalStorage.current = setTimeout(() => {
      localStorage.setItem('avatar_female_layers', JSON.stringify(femaleLayers));
    }, 500);
  }, [femaleLayers]);

  // Estados de UI
  const [activeCategory, setActiveCategory] = useState<string>('hair');
  const [activeGenderFilter, setActiveGenderFilter] = useState<string>('all'); // all, male, female, unisex
  const [genderChangeTimeout, setGenderChangeTimeout] = useState<number | null>(null);
  // Ref para controlar si ya se mostró el toast inicial
  // Estado para distinguir cambio manual de género
  const [isManualGenderChange, setIsManualGenderChange] = useState(false);
  const [isVisualizing, setIsVisualizing] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);

  // Cargar manifest cuando cambia el género
  useEffect(() => {
    loadManifest();
  }, [selectedGender]);

  // Actualizar selectedLayers cuando cambia el género (recuperar de memoria) - optimizado
  useEffect(() => {
    const layersForGender = selectedGender === 'male' ? maleLayers : femaleLayers;
    if (JSON.stringify(selectedLayers) !== JSON.stringify(layersForGender)) {
      setSelectedLayers(layersForGender);
    }
    // Notificación SOLO si es cambio manual
    if (isManualGenderChange) {
      if (genderChangeTimeout) clearTimeout(genderChangeTimeout);
      const genderLabel = selectedGender === 'male' ? 'Masculino' : 'Femenino';
      const currentGenderLayers = selectedGender === 'male' ? maleLayers : femaleLayers;
      const timeoutId = setTimeout(() => {
        if (currentGenderLayers.length > 0) {
          info(`Se restauraron ${currentGenderLayers.length} elementos para ${genderLabel.toLowerCase()}`);
        } else {
          info(`Cambiando a ${genderLabel.toLowerCase()} - Selecciona nuevos elementos`);
        }
      }, 400);
      setGenderChangeTimeout(timeoutId);
      setIsManualGenderChange(false);
    }
  }, [selectedGender, maleLayers, femaleLayers, isManualGenderChange]);

  // Cargar avatar guardado del usuario al inicializar el componente
  useEffect(() => {
    loadUserSavedAvatar();
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
  useEffect(() => {
    const layersKey = JSON.stringify(selectedLayers);
    if (selectedLayers.length > 0 && layersKey !== lastPreviewLayers.current) {
      lastPreviewLayers.current = layersKey;
      const timeoutId = setTimeout(() => generatePreview(), 200);
      return () => clearTimeout(timeoutId);
    }
  }, [selectedLayers]);

  const loadUserSavedAvatar = async () => {
    try {
      console.log('🔄 Loading user saved avatar...');
      const avatarData = await avatarAPI.getMyAvatars();
      console.log('✅ User avatars response:', avatarData);
      // Buscar el avatar activo del usuario
      const activeAvatar = avatarData.avatars.find(avatar => avatar.is_active);
      console.log('🎯 Active avatar found:', activeAvatar);
      if (activeAvatar) {
        setSelectedGender(activeAvatar.base_gender as 'male' | 'female');
        setAvatarName(activeAvatar.name);
        const editorLayers: LayerItem[] = activeAvatar.layers.map(layer => {
          const filename = (layer as any).filename || (layer as any).file;
          return {
            category: layer.category,
            filename: filename,
            url: `http://localhost:8000/static/assets/${filename}`
          };
        });
        setSelectedLayers(editorLayers);
        // Mostrar solo una vez la notificación al cargar el avatar inicial
        if (!hasShownInitialAvatarToast.current) {
          success(`Avatar "${activeAvatar.name}" cargado en el editor`);
          hasShownInitialAvatarToast.current = true;
        }
      } else {
        console.log('ℹ️ No active avatar found, starting with empty editor');
      }
    } catch (error) {
      console.error('❌ Error loading user saved avatar:', error);
      // No mostrar error toast aquí, porque es normal no tener avatar guardado
      console.log('ℹ️ Starting with empty editor');
    }
  };

  const loadManifest = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔄 Loading manifest for gender:', selectedGender);
      
      const data = await avatarAPI.getAssetsManifest(selectedGender);
      console.log('✅ Manifest loaded successfully:', {
        totalAssets: data.total_assets,
        categories: Object.keys(data.categories),
        resolution: data.resolution
      });
      
      setManifest(data);
      
      // Auto-seleccionar la base correspondiente al género
      if (data.categories.base && data.categories.base.length > 0) {
        const baseAsset = data.categories.base[0]; // Tomar la primera base
        console.log('🎯 Auto-selecting base:', baseAsset.filename);
        
        const baseLayer = {
          category: 'base',
          filename: baseAsset.filename,
          url: baseAsset.url
        };
        
        // Solo agregar la base si no hay capas ya cargadas para este género
        const currentGenderLayers = selectedGender === 'male' ? maleLayers : femaleLayers;
        const hasBaseAlready = currentGenderLayers.some(layer => layer.category === 'base');
        
        if (!hasBaseAlready && currentGenderLayers.length === 0) {
          // Solo auto-seleccionar base si no hay nada guardado para este género
          setSelectedLayers([baseLayer]);
          if (selectedGender === 'male') {
            setMaleLayers([baseLayer]);
          } else {
            setFemaleLayers([baseLayer]);
          }
        }
      }
      
    } catch (error) {
      console.error('❌ Error loading manifest:', error);
      setError('Error al cargar los assets del avatar');
      showError('Error al cargar los elementos del avatar');
    } finally {
      setLoading(false);
    }
  };

  const generatePreview = async () => {
    if (!manifest) return;
    
    try {
      console.log('🖼️ Generating preview with layers:', selectedLayers);
      
      // Asegurar que siempre haya una base
      let layersWithBase = [...selectedLayers];
      
      // Verificar si ya hay una base
      const hasBase = layersWithBase.some(layer => layer.category === 'base');
      
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
          console.log('🎯 Auto-adding base:', baseAsset.filename);
          layersWithBase.unshift({
            category: 'base',
            filename: baseAsset.filename,
            url: baseAsset.url
          });
        }
      }
      
      if (layersWithBase.length === 0) {
        console.log('⚠️ No layers to generate preview');
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
      
      console.log('✅ Preview generated successfully');
    } catch (error) {
      console.error('❌ Error generating preview:', error);
      showError('Error al generar la vista previa');
    }
  };

  const handleLayerSelect = (category: string, asset: AssetInfo | null) => {
    if (!asset) {
      // Remover la capa de esta categoría
      const updatedLayers = selectedLayers.filter(layer => layer.category !== category);
      setSelectedLayers(updatedLayers);
      
      // Guardar en el estado correspondiente al género
      if (selectedGender === 'male') {
        setMaleLayers(updatedLayers);
      } else {
        setFemaleLayers(updatedLayers);
      }
      return;
    }

    const newLayer: LayerItem = {
      category,
      filename: asset.filename,
      url: asset.url
    };

    console.log('🔧 Adding new layer:', newLayer);

    const updatedLayers = (() => {
      // Reemplazar o agregar la capa para esta categoría
      const filtered = selectedLayers.filter(layer => layer.category !== category);
      const newLayers = [...filtered, newLayer];
      console.log('🔧 Updated selected layers:', newLayers);
      return newLayers;
    })();
    
    setSelectedLayers(updatedLayers);
    
    // Guardar en el estado correspondiente al género
    if (selectedGender === 'male') {
      setMaleLayers(updatedLayers);
    } else {
      setFemaleLayers(updatedLayers);
    }
  };

  const getSelectedAssetForCategory = (category: string): AssetInfo | null => {
    const layer = selectedLayers.find(l => l.category === category);
    if (!layer || !manifest) return null;
    
    const categoryAssets = manifest.categories[category] || [];
    return categoryAssets.find(asset => asset.filename === layer.filename) || null;
  };

  const getFilteredAssetsForCategory = (category: string): AssetInfo[] => {
    if (!manifest) return [];
    
    const categoryAssets = manifest.categories[category] || [];
    
    if (activeGenderFilter === 'all') {
      return categoryAssets;
    }
    
    return categoryAssets.filter(asset => asset.target_gender === activeGenderFilter);
  };

  const handleGenderChange = (newGender: 'male' | 'female', genderLabel: string) => {
    // Limpiar timeout anterior si existe
    if (genderChangeTimeout) {
      clearTimeout(genderChangeTimeout);
    }
    // Guardar las capas actuales en el género actual antes de cambiar, usando función para obtener el valor más reciente
    setIsManualGenderChange(true);
    setSelectedGender(prev => {
      if (prev === newGender) return prev;
      if (prev === 'male') {
        setMaleLayers(layers => selectedLayers.length ? [...selectedLayers] : layers);
      } else {
        setFemaleLayers(layers => selectedLayers.length ? [...selectedLayers] : layers);
      }
      return newGender;
    });
  };

  const handleVisualize = () => {
    if (selectedLayers.length === 0) {
      showError('Selecciona al menos un elemento para visualizar');
      return;
    }
    setShowPreviewModal(true);
  };

  const handleRandomize = () => {
    if (!manifest) return;

    const newLayers: LayerItem[] = [];
    
    // Siempre incluir la base
    if (manifest.categories.base?.length > 0) {
      const baseAsset = manifest.categories.base[0]; // Siempre tomar la primera base del género
      newLayers.push({
        category: 'base',
        filename: baseAsset.filename,
        url: baseAsset.url
      });
    }

    // Randomizar otras categorías
    Object.entries(manifest.categories).forEach(([category, assets]) => {
      if (category === 'base') return; // Ya manejamos la base
      
      if (Math.random() > 0.4) { // 60% chance de incluir cada categoría
        const randomAsset = assets[Math.floor(Math.random() * assets.length)];
        newLayers.push({
          category,
          filename: randomAsset.filename,
          url: randomAsset.url
        });
      }
    });

    console.log('🎲 Randomized layers:', newLayers);
    setSelectedLayers(newLayers);
    
    // Guardar en el estado correspondiente al género
    if (selectedGender === 'male') {
      setMaleLayers(newLayers);
    } else {
      setFemaleLayers(newLayers);
    }
    
    success('Avatar aleatorio generado');
  };

  const handleSaveAvatar = async () => {
    if (selectedLayers.length === 0) {
      showError('Selecciona al menos una capa para guardar');
      return;
    }

    if (!avatarName.trim()) {
      showError('Ingresa un nombre para tu avatar');
      return;
    }

    try {
      console.log('💾 Saving avatar:', {
        name: avatarName,
        gender: selectedGender,
        layers: selectedLayers
      });
      // Guardar en la base de datos usando la API
      const savedAvatar = await avatarAPI.saveAvatar(
        avatarName.trim(),
        selectedGender,
        selectedLayers,
        true, // Activar este avatar
        true  // Hacer público
      );

      console.log('✅ Avatar saved successfully:', savedAvatar);
      
      // Guardar en localStorage como backup
      const avatarData = {
        id: savedAvatar.id,
        name: savedAvatar.name,
        layers: selectedLayers,
        timestamp: new Date().toISOString()
      };
      localStorage.setItem('saved_avatar', JSON.stringify(avatarData));
      
      // Actualizar la navegación para mostrar el nuevo avatar
      window.dispatchEvent(new CustomEvent('avatar-updated', { detail: savedAvatar }));
      
      success(`Avatar "${avatarName}" guardado exitosamente`);
      
      // Limpiar el nombre para el siguiente avatar
      setAvatarName('');
      
    } catch (error) {
      console.error('Error saving avatar:', error);
      showError(`Error al guardar el avatar: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  };

  const handleSave = async () => {
    if (!avatarName.trim()) {
      showError('Por favor ingresa un nombre para el avatar');
      return;
    }

    if (selectedLayers.length === 0) {
      showError('Selecciona al menos un elemento para el avatar');
      return;
    }

    // Verificar autenticación antes de proceder
    if (!isAuthenticated) {
      showError('Debes iniciar sesión para guardar avatares');
      warning('Serás redirigido al login');
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
      return;
    }

    // Debug: Verificar estado de autenticación
    const token = localStorage.getItem('access_token');
    console.log('🔐 DEBUG: Authentication state:', {
      isAuthenticated,
      hasToken: !!token,
      tokenPreview: token ? token.substring(0, 30) + '...' : 'NO_TOKEN'
    });

    try {
      setSaving(true);
      
      console.log('💾 handleSave: Starting save process:', {
        name: avatarName,
        gender: selectedGender,
        layers: selectedLayers
      });
      
      // Guardar en la base de datos usando la API (la API manejará la conversión)
      const savedAvatar = await avatarAPI.saveAvatar(
        avatarName.trim(),
        selectedGender,
        selectedLayers, // Pasar directamente selectedLayers
        true, // Activar este avatar
        true  // Hacer público
      );

      console.log('✅ handleSave: Avatar saved successfully:', savedAvatar);
      
      // Guardar en localStorage como backup
      const avatarData = {
        id: savedAvatar.id,
        name: savedAvatar.name,
        layers: selectedLayers,
        timestamp: new Date().toISOString()
      };
      localStorage.setItem('saved_avatar', JSON.stringify(avatarData));
      
      // Llamar callback si existe
      if (onSave) {
        await onSave({
          name: avatarName,
          gender: selectedGender,
          layers: selectedLayers
        });
      }
      
      // Actualizar la navegación para mostrar el nuevo avatar
      console.log('📢 handleSave: Dispatching avatar-updated event');
      window.dispatchEvent(new CustomEvent('avatar-updated', { 
        detail: {
          ...savedAvatar,
          timestamp: Date.now(), // Para forzar refresh
          action: 'saved'
        }
      }));
      
      // También disparar evento global de refresh
      window.dispatchEvent(new CustomEvent('avatar-refresh', { 
        detail: { 
          userId: savedAvatar.user_id,
          avatarId: savedAvatar.id,
          timestamp: Date.now()
        }
      }));
      
      success(`Avatar "${avatarName}" guardado exitosamente`);
      
    } catch (error) {
      console.error('❌ handleSave: Error saving avatar:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      
      // Manejo especial para errores de autenticación
      if (errorMessage.includes('sesión ha expirado') || errorMessage.includes('No estás autenticado')) {
        showError('Tu sesión ha expirado. Inicia sesión nuevamente.');
        warning('Serás redirigido al login en unos segundos...');
        setTimeout(() => {
          window.location.href = '/login';
        }, 3000);
      } else {
        showError(`Error al guardar el avatar: ${errorMessage}`);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleDownload = () => {
    if (!previewUrl) {
      showError('Genera un avatar primero');
      return;
    }

    const link = document.createElement('a');
    link.href = previewUrl;
    link.download = `avatar-${avatarName || 'custom'}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    success('Avatar descargado');
  };

  // Configuración de categorías con iconos y nombres modernos
  const getCategoryConfig = () => [
    { key: 'hair', label: 'Cabello', icon: FiUser, color: 'from-amber-500 to-orange-500', description: 'Estilos de cabello' },
    { key: 'eyes', label: 'Ojos', icon: FiEye, color: 'from-blue-500 to-indigo-500', description: 'Color y forma de ojos' },
    { key: 'mouth', label: 'Boca', icon: FiHeart, color: 'from-pink-500 to-rose-500', description: 'Expresiones y labios' },
  { key: 'makeup', label: 'Maquillaje', icon: HiColorSwatch, color: 'from-purple-500 to-violet-500', description: 'Maquillaje y detalles' },
    { key: 'shirt', label: 'Camisas', icon: FiGrid, color: 'from-green-500 to-emerald-500', description: 'Ropa superior' },
    { key: 'pants', label: 'Pantalones', icon: FiGrid, color: 'from-blue-600 to-blue-700', description: 'Ropa inferior' },
    { key: 'shoes', label: 'Zapatos', icon: FiStar, color: 'from-gray-600 to-gray-700', description: 'Calzado' },
    { key: 'jacket', label: 'Chaquetas', icon: FiGrid, color: 'from-indigo-600 to-purple-600', description: 'Prendas exteriores' },
    { key: 'accessories', label: 'Accesorios', icon: HiColorSwatch, color: 'from-yellow-500 to-amber-500', description: 'Complementos' },
  { key: 'backgrounds', label: 'Fondos', icon: HiColorSwatch, color: 'from-teal-500 to-cyan-500', description: 'Fondos y escenarios' }
  ];

  if (loading) {
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
          <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">Preparando el estudio</h3>
          <p className="text-gray-600 dark:text-gray-400">Cargando elementos del avatar...</p>
        </motion.div>
      </div>
    );
  }

  if (error) {
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
            <FiX className="text-3xl text-red-600 dark:text-red-400" />
          </motion.div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">Oops, algo salió mal</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-8">{error}</p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={loadManifest}
            className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all"
          >
            <FiRefreshCw className="inline mr-2" />
            Reintentar
          </motion.button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-blue-900/20 pt-20">
      {/* Modal de preview grande */}
      <AnimatePresence>
        {showPreviewModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
            onClick={() => setShowPreviewModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 relative flex flex-col items-center"
              onClick={e => e.stopPropagation()}
            >
              <img
                src={previewUrl}
                alt="Preview Avatar"
                className="w-[400px] h-[400px] rounded-2xl border-4 border-blue-500 bg-white object-contain"
                style={{ objectPosition: 'center 25%' }}
              />
              <button
                className="absolute top-4 right-4 w-10 h-10 bg-white/80 rounded-full flex items-center justify-center hover:bg-white"
                onClick={() => setShowPreviewModal(false)}
              >
                <FiX className="text-gray-700 text-xl" />
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
              <HiSparkles className="text-3xl text-white" />
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
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20 dark:border-gray-700/30"
            >
              {/* Header del Panel */}
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl flex items-center justify-center mr-3">
                    <FiEye className="text-white text-lg" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200">Vista Previa</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Tu avatar personalizado</p>
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={loadManifest}
                  className="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-xl flex items-center justify-center hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  <FiRefreshCw className="text-gray-600 dark:text-gray-400" />
                </motion.button>
              </div>
              
              {/* Selector de Género Mejorado */}
              <div className="mb-8">
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
                  Identidad de Género
                </label>
                <div className="grid grid-cols-2 gap-3 p-2 bg-gray-100 dark:bg-gray-700 rounded-2xl">
                  {[
                    { value: 'male', label: 'Masculino', icon: GiMale },
                    { value: 'female', label: 'Femenino', icon: GiFemale }
                  ].map((gender) => (
                    <motion.button
                      key={gender.value}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleGenderChange(gender.value as 'male' | 'female', gender.label)}
                      className={`relative overflow-hidden py-4 px-4 rounded-xl font-semibold transition-all duration-300 ${
                        selectedGender === gender.value
                          ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                          : 'bg-white dark:bg-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-500'
                      }`}
                    >
                      <gender.icon className="inline mr-2 text-lg" />
                      {gender.label}
                      {selectedGender === gender.value && (
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

                {previewUrl ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.5, y: 50 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ type: "spring", damping: 20, stiffness: 300 }}
                    className="relative z-10"
                  >
                    <motion.img
                      whileHover={{ scale: 1.05 }}
                      src={previewUrl}
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
                      <FiUser className="text-4xl" />
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
                      value={avatarName}
                      onChange={(e) => setAvatarName(e.target.value)}
                      placeholder="Dale vida con un nombre único..."
                      className="w-full px-4 py-4 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500"
                    />
                    <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                      <FiUser className="text-gray-400" />
                    </div>
                  </div>
                </div>

                {/* Botones de acción */}
                <div className="grid grid-cols-3 gap-3">
                  <motion.button
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleRandomize}
                    className="bg-gradient-to-r from-amber-500 to-orange-500 text-white py-3 px-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all group"
                  >
                    <FiShuffle className="inline mr-2" />
                    <span className="text-sm">Sorprender</span>
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleDownload}
                    disabled={!previewUrl}
                    className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white py-3 px-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                  >
                    <FiDownload className="inline mr-2" />
                    <span className="text-sm">Obtener</span>
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleVisualize}
                    disabled={selectedLayers.length === 0 || isVisualizing}
                    className="bg-gradient-to-r from-teal-500 to-cyan-500 text-white py-3 px-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                    title="Generar vista previa actualizada del avatar"
                  >
                    {isVisualizing ? (
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
                        <FiEye className="inline mr-2" />
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
                  disabled={saving || !avatarName.trim() || selectedLayers.length === 0 || !isAuthenticated}
                  className={`relative w-full py-5 px-6 rounded-xl font-bold text-lg shadow-xl hover:shadow-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden group ${
                    !isAuthenticated 
                      ? 'bg-gradient-to-r from-gray-500 to-gray-600 text-white'
                      : 'bg-gradient-to-r from-green-600 to-emerald-600 text-white'
                  }`}
                >
                  {saving ? (
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
                      <FiUser className="mr-3 text-xl" />
                      Inicia sesión para guardar
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center justify-center">
                        <FiSave className="mr-3 text-xl" />
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
                    <HiColorSwatch className="text-white text-lg" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200">Personalización</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {manifest && Object.values(manifest.categories).reduce((acc, assets) => acc + assets.length, 0)} elementos disponibles
                    </p>
                  </div>
                </div>
                <motion.div
                  animate={{ rotate: [0, 5, -5, 0] }}
                  transition={{ duration: 3, repeat: Infinity }}
                  className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center"
                >
                  <HiSparkles className="text-purple-600 dark:text-purple-400" />
                </motion.div>
              </div>

              {manifest && (
                <div className="space-y-8">
                  {/* Navegación de Categorías Mejorada */}
                  <div className="relative">
                    <div className="flex flex-wrap gap-3">
                      {getCategoryConfig()
                        .filter(category => manifest.categories[category.key] && manifest.categories[category.key].length > 0)
                        .map((category, index) => {
                          const IconComponent = category.icon;
                          const isActive = activeCategory === category.key;
                          
                          return (
                            <motion.button
                              key={category.key}
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: index * 0.1 }}
                              whileHover={{ scale: 1.05, y: -2 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => {
                                setActiveCategory(category.key);
                                setActiveGenderFilter('all');
                              }}
                              className={`relative overflow-hidden group px-6 py-4 rounded-2xl font-semibold transition-all duration-300 ${
                                isActive
                                  ? 'text-white shadow-xl'
                                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 shadow-md'
                              }`}
                            >
                              {isActive && (
                                <motion.div
                                  layoutId="activeCategory"
                                  className={`absolute inset-0 bg-gradient-to-r ${category.color} rounded-2xl`}
                                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                />
                              )}
                              <div className="relative flex items-center">
                                <IconComponent className="mr-3 text-lg" />
                                <div className="text-left">
                                  <div className="font-bold">{category.label}</div>
                                  <div className={`text-xs ${isActive ? 'text-white/80' : 'text-gray-400'}`}>
                                    {category.description}
                                  </div>
                                </div>
                              </div>
                              {!isActive && (
                                <motion.div
                                  className="absolute inset-0 bg-gradient-to-r from-purple-500/0 to-blue-500/0 group-hover:from-purple-500/10 group-hover:to-blue-500/10 rounded-2xl transition-all duration-300"
                                />
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
                      {/* Filtros de Género Mejorados */}
                      {activeCategory !== 'base' && (
                        <div className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-2xl">
                          <div className="flex items-center text-sm font-semibold text-gray-700 dark:text-gray-300">
                            <FiFilter className="mr-2" />
                            Filtrar por:
                          </div>
                          <div className="flex gap-2">
                            {[
                              { key: 'all', label: 'Todos', icon: FiUsers },
                              { key: 'male', label: 'Hombre', icon: GiMale },
                              { key: 'female', label: 'Mujer', icon: GiFemale },
                              { key: 'unisex', label: 'Unisex', icon: FiUsers }
                            ].map((filter) => {
                              const FilterIcon = filter.icon;
                              const isActive = activeGenderFilter === filter.key;
                              const categoryAssets = manifest?.categories[activeCategory] || [];
                              const filteredCount = filter.key === 'all' 
                                ? categoryAssets.length 
                                : categoryAssets.filter(asset => asset.target_gender === filter.key).length;
                              
                              return (
                                <motion.button
                                  key={filter.key}
                                  whileHover={{ scale: 1.05 }}
                                  whileTap={{ scale: 0.95 }}
                                  onClick={() => setActiveGenderFilter(filter.key)}
                                  disabled={filteredCount === 0}
                                  className={`relative px-4 py-2 rounded-xl text-sm font-medium transition-all disabled:opacity-30 disabled:cursor-not-allowed ${
                                    isActive
                                      ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                                      : 'bg-white dark:bg-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-500'
                                  }`}
                                >
                                  {isActive && (
                                    <motion.div
                                      layoutId="genderFilter"
                                      className="absolute inset-0 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl"
                                      transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                    />
                                  )}
                                  <div className="relative flex items-center">
                                    <FilterIcon className="mr-2" />
                                    {filter.label}
                                    <span className={`ml-2 text-xs px-2 py-1 rounded-full ${
                                      isActive 
                                        ? 'bg-white/20 text-white' 
                                        : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                                    }`}>
                                      {filteredCount}
                                    </span>
                                  </div>
                                </motion.button>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* Grid de Assets Mejorado */}
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                        {/* Opción "Ninguno" mejorada */}
                        {activeCategory !== 'base' && (
                          <motion.button
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            whileHover={{ scale: 1.05, y: -2 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => handleLayerSelect(activeCategory, null)}
                            className={`aspect-square rounded-2xl border-2 transition-all duration-300 flex flex-col items-center justify-center p-4 group ${
                              !getSelectedAssetForCategory(activeCategory)
                                ? 'border-purple-500 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 shadow-lg ring-2 ring-purple-200 dark:ring-purple-700'
                                : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-md'
                            }`}
                          >
                            <motion.div
                              whileHover={{ rotate: 180 }}
                              transition={{ duration: 0.3 }}
                              className={`text-3xl mb-2 ${
                                !getSelectedAssetForCategory(activeCategory)
                                  ? 'text-purple-600 dark:text-purple-400'
                                  : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-600 dark:group-hover:text-gray-400'
                              }`}
                            >
                              <FiX />
                            </motion.div>
                            <span className={`text-xs font-medium ${
                              !getSelectedAssetForCategory(activeCategory)
                                ? 'text-purple-600 dark:text-purple-400'
                                : 'text-gray-500 dark:text-gray-400'
                            }`}>
                              Sin {getCategoryConfig().find(c => c.key === activeCategory)?.label?.toLowerCase()}
                            </span>
                          </motion.button>
                        )}

                        {/* Assets de la categoría */}
                        {getFilteredAssetsForCategory(activeCategory).map((asset, index) => {
                          const isSelected = getSelectedAssetForCategory(activeCategory)?.filename === asset.filename;
                          
                          return (
                            <motion.button
                              key={asset.filename}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ 
                                opacity: 1, 
                                scale: 1,
                                transition: { delay: index * 0.05 }
                              }}
                              whileHover={{ scale: 1.05, y: -4 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => handleLayerSelect(activeCategory, asset)}
                              className={`aspect-square rounded-2xl border-2 overflow-hidden transition-all duration-300 relative group ${
                                isSelected
                                  ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20 shadow-xl ring-2 ring-purple-200 dark:ring-purple-700'
                                  : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-lg'
                              }`}
                            >
                              <img
                                src={asset.url}
                                alt={asset.filename}
                                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                                loading="lazy"
                                onError={(e) => {
                                  console.error('Error loading image:', asset.url);
                                  e.currentTarget.style.display = 'none';
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
                                    <FiCheck className="text-white text-sm" />
                                  </motion.div>
                                </motion.div>
                              )}

                              {/* Badge de género mejorado */}
                              <div className={`absolute top-2 right-2 px-2 py-1 rounded-lg text-xs font-bold backdrop-blur-sm ${
                                asset.target_gender === 'male' 
                                  ? 'bg-blue-500/90 text-white' 
                                  : asset.target_gender === 'female' 
                                  ? 'bg-pink-500/90 text-white' 
                                  : 'bg-green-500/90 text-white'
                              }`}>
                                {asset.target_gender === 'male' ? (
                                  <GiMale className="inline" />
                                ) : asset.target_gender === 'female' ? (
                                  <GiFemale className="inline" />
                                ) : (
                                  <FiUsers className="inline" />
                                )}
                              </div>

                              {/* Hover effect */}
                              <motion.div
                                className="absolute inset-0 bg-gradient-to-t from-black/0 via-transparent to-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                              />
                            </motion.button>
                          );
                        })}
                      </div>

                      {/* Estado vacío mejorado */}
                      {getFilteredAssetsForCategory(activeCategory).length === 0 && (
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
                            <FiFilter className="text-3xl text-gray-400 dark:text-gray-500" />
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
              {(!manifest || Object.keys(manifest.categories).length === 0) && (
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
                    <FiUser className="text-3xl text-gray-400 dark:text-gray-500" />
                  </motion.div>
                  <h4 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-3">
                    Preparando el catálogo
                  </h4>
                  <p className="text-gray-500 dark:text-gray-500 mb-6">
                    Selecciona un género para comenzar a personalizar
                  </p>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={loadManifest}
                    className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-xl font-semibold shadow-lg"
                  >
                    <FiRefreshCw className="inline mr-2" />
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