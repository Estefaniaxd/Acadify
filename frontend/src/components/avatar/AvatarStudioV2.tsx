import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiShuffle, 
  FiDownload, 
  FiSave, 
  FiRefreshCw,
  FiUser,
  FiEye
} from 'react-icons/fi';
import { HiSparkles } from 'react-icons/hi';
import { useToast } from '../../context/ToastContext';
import { avatarAPI, LayerItem, AssetInfo, ManifestResponse } from './avatarAPI';

interface AvatarStudioV2Props {
  onSave?: (avatar: any) => void;
  onPreview?: (previewUrl: string) => void;
}

const AvatarStudioV2: React.FC<AvatarStudioV2Props> = ({ onSave, onPreview }) => {
  const { success, error: showError, info, warning } = useToast();
  
  // Estados principales
  const [selectedGender, setSelectedGender] = useState<'male' | 'female'>('male');
  const [manifest, setManifest] = useState<ManifestResponse | null>(null);
  const [selectedLayers, setSelectedLayers] = useState<LayerItem[]>([]);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [avatarName, setAvatarName] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estados de UI
  const [activeCategory, setActiveCategory] = useState<string>('hair');
  const [activeGenderFilter, setActiveGenderFilter] = useState<string>('all'); // all, male, female, unisex

  // Cargar manifest cuando cambia el género
  useEffect(() => {
    loadManifest();
  }, [selectedGender]);

  // Cargar avatar guardado del usuario al inicializar el componente
  useEffect(() => {
    loadUserSavedAvatar();
  }, []);

  // Generar preview cuando cambian las capas O cuando se carga el manifest por primera vez
  useEffect(() => {
    if (selectedLayers.length > 0 || manifest) {
      generatePreview();
    }
  }, [selectedLayers, selectedGender, manifest]);

  const loadUserSavedAvatar = async () => {
    try {
      console.log('🔄 Loading user saved avatar...');
      
      const avatarData = await avatarAPI.getMyAvatars();
      console.log('✅ User avatars response:', avatarData);
      
      // Buscar el avatar activo del usuario
      const activeAvatar = avatarData.avatars.find(avatar => avatar.is_active);
      console.log('🎯 Active avatar found:', activeAvatar);
      
      if (activeAvatar) {
        // Cargar el avatar en el editor
        console.log('🔄 Loading active avatar in editor:', activeAvatar);
        
        // Establecer el género
        setSelectedGender(activeAvatar.base_gender as 'male' | 'female');
        
        // Establecer el nombre
        setAvatarName(activeAvatar.name);
        
        // Convertir las capas al formato del editor
        const editorLayers: LayerItem[] = activeAvatar.layers.map(layer => {
          // Las capas guardadas pueden tener estructura {category, file} o {category, filename}
          const filename = (layer as any).filename || (layer as any).file;
          return {
            category: layer.category,
            filename: filename,
            url: `http://localhost:8000/static/assets/${filename}`
          };
        });
        
        console.log('🔄 Editor layers:', editorLayers);
        setSelectedLayers(editorLayers);
        
        success(`Avatar "${activeAvatar.name}" cargado en el editor`);
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
        
        setSelectedLayers([{
          category: 'base',
          filename: baseAsset.filename,
          url: baseAsset.url
        }]);
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
    try {
      console.log('🖼️ Generating preview with layers:', selectedLayers);
      
      // Asegurar que siempre haya una base
      let layersWithBase = [...selectedLayers];
      
      // Verificar si ya hay una base
      const hasBase = layersWithBase.some(layer => layer.category === 'base');
      
      if (!hasBase && manifest?.categories.base?.length > 0) {
        // Agregar la base automáticamente
        const baseAsset = manifest.categories.base[0];
        console.log('🎯 Auto-adding base:', baseAsset.filename);
        
        layersWithBase.unshift({
          category: 'base',
          filename: baseAsset.filename,
          url: baseAsset.url
        });
      }
      
      console.log('🔄 Has base after check:', layersWithBase.some(l => l.category === 'base'));
      console.log('🔄 All layers:', layersWithBase.map(l => ({category: l.category, filename: l.filename})));
      
      if (layersWithBase.length === 0) {
        console.log('⚠️ No layers to generate preview');
        return;
      }
      
      console.log('🔄 Final layers for preview:', layersWithBase);
      
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
      setSelectedLayers(prev => prev.filter(layer => layer.category !== category));
      return;
    }

    const newLayer: LayerItem = {
      category,
      filename: asset.filename,
      url: asset.url
    };

    console.log('🔧 Adding new layer:', newLayer);

    setSelectedLayers(prev => {
      // Reemplazar o agregar la capa para esta categoría
      const filtered = prev.filter(layer => layer.category !== category);
      const newLayers = [...filtered, newLayer];
      console.log('🔧 Updated selected layers:', newLayers);
      return newLayers;
    });
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
      // Transformar layers a formato backend
      const layersForSave = selectedLayers.map(layer => ({
        category: layer.category,
        file: layer.filename
      }));
      // Guardar en la base de datos usando la API
      const savedAvatar = await avatarAPI.saveAvatar(
        avatarName.trim(),
        selectedGender,
        layersForSave,
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

    // Debug: Verificar estado de autenticación
    const token = localStorage.getItem('access_token');
    console.log('🔐 DEBUG: Token state:', {
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
      showError(`Error al guardar el avatar: ${error instanceof Error ? error.message : 'Error desconocido'}`);
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

  // Configuración de categorías con iconos y nombres
  const getCategoryConfig = () => [
    { key: 'hair', label: 'Cabello', icon: '💇', color: 'from-amber-500 to-orange-500' },
    { key: 'eyes', label: 'Ojos', icon: '👁️', color: 'from-blue-500 to-indigo-500' },
    { key: 'mouth', label: 'Boca', icon: '👄', color: 'from-pink-500 to-rose-500' },
    { key: 'makeup', label: 'Maquillaje', icon: '💄', color: 'from-purple-500 to-violet-500' },
    { key: 'shirt', label: 'Camisas', icon: '👕', color: 'from-green-500 to-emerald-500' },
    { key: 'pants', label: 'Pantalones', icon: '👖', color: 'from-blue-600 to-blue-700' },
    { key: 'shoes', label: 'Zapatos', icon: '👠', color: 'from-gray-600 to-gray-700' },
    { key: 'jacket', label: 'Chaquetas', icon: '🧥', color: 'from-indigo-600 to-purple-600' },
    { key: 'accessories', label: 'Accesorios', icon: '👑', color: 'from-yellow-500 to-amber-500' },
    { key: 'backgrounds', label: 'Fondos', icon: '🎨', color: 'from-teal-500 to-cyan-500' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Cargando elementos del avatar...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-xl shadow-lg">
          <div className="text-red-500 text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadManifest}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4"
          >
            <HiSparkles className="inline mr-3 text-purple-600" />
            Estudio de Avatars
          </motion.h1>
          <p className="text-gray-600 text-lg">Crea tu avatar personalizado</p>
        </div>

        <div className="grid xl:grid-cols-5 gap-8">
          {/* Panel de Preview - Más espacio */}
          <div className="xl:col-span-2">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-2xl shadow-xl p-8"
            >
              <h3 className="text-2xl font-semibold mb-6 flex items-center">
                <FiEye className="mr-3 text-purple-600" />
                Vista Previa
              </h3>
              
              {/* Selector de Género */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">Género</label>
                <div className="flex gap-3">
                  {['male', 'female'].map((gender) => (
                    <motion.button
                      key={gender}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setSelectedGender(gender as 'male' | 'female')}
                      className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                        selectedGender === gender
                          ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {gender === 'male' ? '👨 Masculino' : '👩 Femenino'}
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Preview del Avatar */}
              <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-8 mb-6 flex items-center justify-center min-h-[400px]">
                {previewUrl ? (
                  <motion.img
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    src={previewUrl}
                    alt="Avatar Preview"
                    className="max-w-full max-h-full object-contain rounded-lg shadow-lg"
                  />
                ) : (
                  <div className="text-center text-gray-400">
                    <FiUser className="text-6xl mx-auto mb-4" />
                    <p className="text-lg">Selecciona elementos para ver tu avatar</p>
                  </div>
                )}
              </div>

              {/* Controles */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre del Avatar
                  </label>
                  <input
                    type="text"
                    value={avatarName}
                    onChange={(e) => setAvatarName(e.target.value)}
                    placeholder="Ingresa un nombre..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleRandomize}
                    className="bg-gradient-to-r from-amber-500 to-orange-500 text-white py-3 px-4 rounded-lg font-medium hover:shadow-lg transition-all"
                  >
                    <FiShuffle className="inline mr-2" />
                    Aleatorio
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleDownload}
                    disabled={!previewUrl}
                    className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white py-3 px-4 rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50"
                  >
                    <FiDownload className="inline mr-2" />
                    Descargar
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={loadManifest}
                    className="bg-gradient-to-r from-gray-500 to-gray-600 text-white py-3 px-4 rounded-lg font-medium hover:shadow-lg transition-all"
                  >
                    <FiRefreshCw className="inline mr-2" />
                    Recargar
                  </motion.button>
                </div>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSave}
                  disabled={saving || !avatarName.trim() || selectedLayers.length === 0}
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-4 px-6 rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white inline mr-3"></div>
                      Guardando...
                    </>
                  ) : (
                    <>
                      <FiSave className="inline mr-3" />
                      Guardar Avatar
                    </>
                  )}
                </motion.button>
              </div>
            </motion.div>
          </div>

          {/* Panel de Categorías */}
          <div className="xl:col-span-3">
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-2xl shadow-xl p-8"
            >
              <h3 className="text-2xl font-semibold mb-6 flex items-center">
                <span className="mr-3">🎨</span>
                Personalización
                {manifest && (
                  <span className="ml-auto text-sm text-gray-500 font-normal">
                    {Object.values(manifest.categories).reduce((acc, assets) => acc + assets.length, 0)} elementos disponibles
                  </span>
                )}
              </h3>

              {manifest && (
                <div className="space-y-6">
                  {/* Tabs de Categorías */}
                  <div className="flex flex-wrap gap-2">
                    {getCategoryConfig()
                      .filter(category => manifest.categories[category.key] && manifest.categories[category.key].length > 0)
                      .map((category) => (
                        <motion.button
                          key={category.key}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => {
                            setActiveCategory(category.key);
                            setActiveGenderFilter('all'); // Reset filter when changing category
                          }}
                          className={`px-4 py-2 rounded-lg font-medium transition-all ${
                            activeCategory === category.key
                              ? `bg-gradient-to-r ${category.color} text-white shadow-lg`
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          }`}
                        >
                          <span className="mr-2">{category.icon}</span>
                          {category.label}
                        </motion.button>
                      ))}
                  </div>

                  {/* Assets de la Categoría Activa */}
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeCategory}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="space-y-4"
                    >
                      {/* Filtros de Género para la categoría */}
                      {activeCategory !== 'base' && (
                        <div className="flex flex-wrap gap-2 mb-4">
                          <span className="text-sm font-medium text-gray-700 flex items-center mr-2">
                            Filtrar:
                          </span>
                          {['all', 'male', 'female', 'unisex'].map((filter) => (
                            <motion.button
                              key={filter}
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => setActiveGenderFilter(filter)}
                              className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
                                activeGenderFilter === filter
                                  ? 'bg-purple-600 text-white shadow-md'
                                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                              }`}
                            >
                              {filter === 'all' ? 'Todos' : 
                               filter === 'male' ? '👨 Hombre' :
                               filter === 'female' ? '👩 Mujer' : 
                               '🤝 Unisex'}
                            </motion.button>
                          ))}
                        </div>
                      )}

                      <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                        {/* Opción "Ninguno" para categorías opcionales */}
                        {activeCategory !== 'base' && (
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => handleLayerSelect(activeCategory, null)}
                            className={`aspect-square rounded-xl border-2 transition-all p-4 flex items-center justify-center ${
                              !getSelectedAssetForCategory(activeCategory)
                                ? 'border-purple-500 bg-purple-50 shadow-lg'
                                : 'border-gray-300 bg-gray-50 hover:border-gray-400'
                            }`}
                          >
                            <span className="text-2xl">🚫</span>
                          </motion.button>
                        )}

                        {/* Assets de la categoría filtrados */}
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
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => handleLayerSelect(activeCategory, asset)}
                              className={`aspect-square rounded-xl border-2 overflow-hidden transition-all relative ${
                                isSelected
                                  ? 'border-purple-500 bg-purple-50 shadow-lg ring-2 ring-purple-200'
                                  : 'border-gray-300 bg-white hover:border-gray-400 hover:shadow-md'
                              }`}
                            >
                              <img
                                src={asset.url}
                                alt={asset.filename}
                                className="w-full h-full object-cover"
                                loading="lazy"
                                onError={(e) => {
                                  console.error('Error loading image:', asset.url);
                                  e.currentTarget.style.display = 'none';
                                }}
                              />
                              {/* Badge de género */}
                              <div className={`absolute top-1 right-1 px-2 py-1 rounded-full text-xs font-medium ${
                                asset.target_gender === 'male' ? 'bg-blue-500 text-white' :
                                asset.target_gender === 'female' ? 'bg-pink-500 text-white' :
                                'bg-green-500 text-white'
                              }`}>
                                {asset.target_gender === 'male' ? '👨' :
                                 asset.target_gender === 'female' ? '👩' : '🤝'}
                              </div>
                            </motion.button>
                          );
                        })}
                      </div>
                    </motion.div>
                  </AnimatePresence>
                </div>
              )}

              {(!manifest || Object.keys(manifest.categories).length === 0) && (
                <div className="text-center py-12 text-gray-500">
                  <FiUser className="text-6xl mx-auto mb-4" />
                  <p className="text-lg">No hay elementos disponibles</p>
                  <p className="text-sm">Selecciona un género para comenzar</p>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AvatarStudioV2;