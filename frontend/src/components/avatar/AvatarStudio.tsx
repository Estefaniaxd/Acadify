import React, { useState, useCallback, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  FiShuffle, 
  FiDownload, 
  FiSave, 
  FiRotateCw, 
  FiEye, 
  FiEyeOff,
  FiLayers,
  FiUser,
  FiChevronLeft,
  FiChevronRight,
  FiPlus,
  FiMinus,
  FiRefreshCw
} from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'
import { useToast } from '../../context/ToastContext'
import { avatarAPI } from './avatarAPI'

// Definir el tipo AvatarConfig
interface AvatarConfig {
  background: string
  body: string
  hair: string
  hairColor: string
  eyes: string
  eyebrows: string
  mouth: string
  accessories: string
  clothing: string
  clothingColor: string
}

// Definición de assets por capas
const avatarAssets = {
  backgrounds: [
    { id: 'gradient1', name: 'Atardecer', style: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
    { id: 'gradient2', name: 'Océano', style: 'linear-gradient(135deg, #667eea 0%, #43e97b 100%)' },
    { id: 'gradient3', name: 'Fuego', style: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
    { id: 'gradient4', name: 'Aurora', style: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
    { id: 'solid1', name: 'Azul', style: '#3B82F6' },
    { id: 'solid2', name: 'Púrpura', style: '#8B5CF6' },
    { id: 'solid3', name: 'Rosa', style: '#EC4899' },
    { id: 'none', name: 'Transparente', style: 'transparent' }
  ],
  
  bodies: [
    { id: 'default', name: 'Normal', color: '#F9D7B5' },
    { id: 'tan', name: 'Bronceado', color: '#F2B07A' },
    { id: 'brown', name: 'Marrón', color: '#D2996B' },
    { id: 'dark', name: 'Oscuro', color: '#A86B3C' },
    { id: 'deep', name: 'Profundo', color: '#6B3F1D' }
  ],

  hairs: [
    { id: 'none', name: 'Calvo', paths: [] },
    { id: 'short', name: 'Corto', paths: ['M30,35 Q60,20 90,35 Q85,45 75,50 Q60,45 45,50 Q35,45 30,35'] },
    { id: 'medium', name: 'Medio', paths: ['M25,30 Q60,15 95,30 Q90,55 80,65 Q60,60 40,65 Q30,55 25,30'] },
    { id: 'long', name: 'Largo', paths: ['M20,25 Q60,10 100,25 Q95,70 85,85 Q60,80 35,85 Q25,70 20,25'] },
    { id: 'curly', name: 'Rizado', paths: ['M25,30 Q45,15 65,25 Q85,15 95,30 Q90,50 80,60 Q60,55 40,60 Q30,50 25,30'] },
    { id: 'ponytail', name: 'Cola', paths: ['M30,35 Q60,20 90,35 Q95,40 100,45', 'M25,40 Q60,25 95,40 Q90,50 85,55'] }
  ],

  hairColors: [
    '#1a1a1a', '#8B4513', '#D2691E', '#DAA520', '#FFD700', '#F5DEB3', '#FFF8DC', '#E6E6FA', '#FF69B4', '#00CED1'
  ],

  eyes: [
    { id: 'normal', name: 'Normal', paths: ['M45,55 Q50,50 55,55 Q50,60 45,55', 'M65,55 Q70,50 75,55 Q70,60 65,55'] },
    { id: 'closed', name: 'Cerrados', paths: ['M45,55 L55,55', 'M65,55 L75,55'] },
    { id: 'wink', name: 'Guiño', paths: ['M45,55 L55,55', 'M65,55 Q70,50 75,55 Q70,60 65,55'] },
    { id: 'surprised', name: 'Sorprendido', paths: ['M45,55 Q50,45 55,55 Q50,65 45,55', 'M65,55 Q70,45 75,55 Q70,65 65,55'] }
  ],

  eyebrows: [
    { id: 'normal', name: 'Normal', paths: ['M43,48 Q50,45 57,48', 'M63,48 Q70,45 77,48'] },
    { id: 'thick', name: 'Gruesas', paths: ['M43,47 Q50,44 57,47 Q50,49 43,47', 'M63,47 Q70,44 77,47 Q70,49 63,47'] },
    { id: 'raised', name: 'Alzadas', paths: ['M43,45 Q50,42 57,45', 'M63,45 Q70,42 77,45'] },
    { id: 'angry', name: 'Enojadas', paths: ['M43,50 Q50,44 57,47', 'M63,47 Q70,44 77,50'] }
  ],

  mouths: [
    { id: 'smile', name: 'Sonrisa', paths: ['M45,75 Q60,85 75,75'] },
    { id: 'laugh', name: 'Risa', paths: ['M45,75 Q60,90 75,75 Q60,80 45,75'] },
    { id: 'neutral', name: 'Neutral', paths: ['M50,78 L70,78'] },
    { id: 'frown', name: 'Triste', paths: ['M45,82 Q60,72 75,82'] },
    { id: 'open', name: 'Abierta', paths: ['M45,75 Q60,85 75,75 Q60,82 45,75'] }
  ],

  accessories: [
    { id: 'none', name: 'Ninguno', paths: [] },
    { id: 'glasses', name: 'Gafas', paths: ['M38,52 Q45,48 52,52 Q52,58 45,62 Q38,58 38,52', 'M68,52 Q75,48 82,52 Q82,58 75,62 Q68,58 68,52', 'M52,54 Q60,52 68,54'] },
    { id: 'sunglasses', name: 'Lentes de Sol', paths: ['M38,52 Q45,48 52,52 Q52,58 45,62 Q38,58 38,52', 'M68,52 Q75,48 82,52 Q82,58 75,62 Q68,58 68,52', 'M52,54 Q60,52 68,54'] },
    { id: 'hat', name: 'Sombrero', paths: ['M25,35 Q60,20 95,35 Q100,30 105,35 Q100,25 95,20 Q60,15 25,20 Q20,25 25,35'] }
  ],

  clothing: [
    { id: 'tshirt', name: 'Camiseta', paths: ['M35,85 Q40,80 50,82 Q60,80 70,82 Q80,80 85,85 L85,120 L35,120 Z'] },
    { id: 'hoodie', name: 'Sudadera', paths: ['M30,85 Q35,80 45,82 Q60,80 75,82 Q85,80 90,85 L90,120 L30,120 Z', 'M45,82 Q60,75 75,82'] },
    { id: 'suit', name: 'Traje', paths: ['M35,85 Q40,80 50,82 Q60,80 70,82 Q80,80 85,85 L85,120 L35,120 Z', 'M50,82 L50,120', 'M45,90 Q50,88 55,90'] },
    { id: 'dress', name: 'Vestido', paths: ['M40,85 Q50,80 60,80 Q70,80 80,85 Q85,95 90,120 L30,120 Q35,95 40,85'] }
  ],

  clothingColors: [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#6B7280', '#1F2937'
  ]
}

interface AvatarLayerProps {
  config: AvatarConfig
  showLayer: { [key: string]: boolean }
  onConfigChange: (key: keyof AvatarConfig, value: string) => void
}

const AvatarPreview: React.FC<AvatarLayerProps> = ({ config, showLayer }) => {
  const background = avatarAssets.backgrounds.find(b => b.id === config.background)
  const body = avatarAssets.bodies.find(b => b.id === config.body)
  const hair = avatarAssets.hairs.find(h => h.id === config.hair)
  const eyes = avatarAssets.eyes.find(e => e.id === config.eyes)
  const eyebrows = avatarAssets.eyebrows.find(e => e.id === config.eyebrows)
  const mouth = avatarAssets.mouths.find(m => m.id === config.mouth)
  const accessories = avatarAssets.accessories.find(a => a.id === config.accessories)
  const clothing = avatarAssets.clothing.find(c => c.id === config.clothing)

  return (
    <div className="relative">
      <svg
        width="200"
        height="200"
        viewBox="0 0 120 120"
        className="rounded-2xl shadow-2xl border-4 border-white/20"
        style={{ background: background?.style }}
      >
        {/* Background Layer */}
        {showLayer.background && background && background.id !== 'none' && (
          <defs>
            <pattern id="bg-pattern" patternUnits="userSpaceOnUse" width="120" height="120">
              <rect width="120" height="120" fill={background.style.includes('gradient') ? `url(#${background.id})` : background.style} />
            </pattern>
            {background.style.includes('gradient') && (
              <linearGradient id={background.id} x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{ stopColor: '#667eea' }} />
                <stop offset="100%" style={{ stopColor: '#764ba2' }} />
              </linearGradient>
            )}
          </defs>
        )}

        {/* Body/Head */}
        {showLayer.body && body && (
          <circle cx="60" cy="60" r="35" fill={body.color} stroke="#333" strokeWidth="1.5" />
        )}

        {/* Hair */}
        {showLayer.hair && hair && hair.paths.map((path, i) => (
          <path key={i} d={path} fill={config.hairColor} stroke="#333" strokeWidth="1" />
        ))}

        {/* Eyebrows */}
        {showLayer.eyebrows && eyebrows && eyebrows.paths.map((path, i) => (
          <path key={i} d={path} fill={config.hairColor} stroke="none" strokeWidth="1" />
        ))}

        {/* Eyes */}
        {showLayer.eyes && eyes && eyes.paths.map((path, i) => (
          <path key={i} d={path} fill={eyes.id === 'closed' || eyes.id === 'wink' ? '#333' : '#fff'} stroke="#333" strokeWidth="1.5" />
        ))}

        {/* Eye pupils */}
        {showLayer.eyes && eyes && eyes.id !== 'closed' && eyes.id !== 'wink' && (
          <>
            <circle cx="50" cy="55" r="2" fill="#333" />
            {eyes.id !== 'wink' && <circle cx="70" cy="55" r="2" fill="#333" />}
          </>
        )}

        {/* Mouth */}
        {showLayer.mouth && mouth && mouth.paths.map((path, i) => (
          <path key={i} d={path} fill={mouth.id === 'open' || mouth.id === 'laugh' ? '#8B4513' : 'none'} stroke="#333" strokeWidth="2" strokeLinecap="round" />
        ))}

        {/* Clothing */}
        {showLayer.clothing && clothing && clothing.paths.map((path, i) => (
          <path key={i} d={path} fill={i === 0 ? config.clothingColor : '#333'} stroke="#333" strokeWidth="1" />
        ))}

        {/* Accessories */}
        {showLayer.accessories && accessories && accessories.paths.map((path, i) => (
          <path 
            key={i} 
            d={path} 
            fill={accessories.id === 'sunglasses' ? '#333' : accessories.id === 'glasses' ? 'rgba(255,255,255,0.3)' : config.hairColor} 
            stroke="#333" 
            strokeWidth="1.5" 
          />
        ))}
      </svg>

      {/* Layer indicators */}
      <div className="absolute -right-2 top-2 space-y-1">
        {Object.entries(showLayer).map(([layer, visible]) => (
          <div
            key={layer}
            className={`w-3 h-3 rounded-full border-2 ${
              visible ? 'bg-emerald-500 border-emerald-300' : 'bg-gray-300 border-gray-200'
            }`}
            title={`Capa: ${layer}`}
          />
        ))}
      </div>
    </div>
  )
}

export default function AvatarCustomizerAdvanced() {
  const [activeCategory, setActiveCategory] = useState('body')
  const [selectedGender, setSelectedGender] = useState<'male' | 'female'>('male')
  const [isLoading, setIsLoading] = useState(false)
  const [isInitialized, setIsInitialized] = useState(false)
  
  // Dos configuraciones separadas - una para cada género
  const [maleConfig, setMaleConfig] = useState<AvatarConfig>({
    background: 'gradient1',
    body: 'default',
    hair: 'short',
    hairColor: '#1a1a1a',
    eyes: 'normal',
    eyebrows: 'normal',
    mouth: 'smile',
    accessories: 'none',
    clothing: 'tshirt',
    clothingColor: '#3B82F6'
  })
  
  const [femaleConfig, setFemaleConfig] = useState<AvatarConfig>({
    background: 'gradient2',
    body: 'default',
    hair: 'long',
    hairColor: '#8B4513',
    eyes: 'normal',
    eyebrows: 'normal',
    mouth: 'smile',
    accessories: 'none',
    clothing: 'dress',
    clothingColor: '#EC4899'
  })
  
  // La configuración actual según el género seleccionado
  const currentConfig = selectedGender === 'male' ? maleConfig : femaleConfig
  const setCurrentConfig = selectedGender === 'male' ? setMaleConfig : setFemaleConfig

  const [showLayer, setShowLayer] = useState({
    background: true,
    body: true,
    hair: true,
    eyebrows: true,
    eyes: true,
    mouth: true,
    accessories: true,
    clothing: true
  })

  const [savedAvatars, setSavedAvatars] = useState<AvatarConfig[]>([])

  // Cargar avatares del usuario automáticamente (sin bloquear UI)
  useEffect(() => {
    const loadUserAvatars = async () => {
      try {
        console.log('🔄 Cargando avatares del usuario...')
        setIsLoading(true)
        const response = await avatarAPI.getMyAvatars()
        
        if (response.avatars.length > 0) {
          response.avatars.forEach(avatar => {
            if (avatar.base_gender === 'male') {
              // Configurar avatar masculino si existe
              const maleAvatar = convertAvatarToConfig(avatar)
              if (maleAvatar) setMaleConfig(maleAvatar)
            } else if (avatar.base_gender === 'female') {
              // Configurar avatar femenino si existe
              const femaleAvatar = convertAvatarToConfig(avatar)
              if (femaleAvatar) setFemaleConfig(femaleAvatar)
            }
          })
          console.log('✅ Avatares cargados exitosamente')
        } else {
          console.log('ℹ️ No hay avatares guardados, usando configuraciones por defecto')
        }
      } catch (error) {
        console.error('⚠️ Error cargando avatares (usando defaults):', error)
      } finally {
        setIsLoading(false)
        setIsInitialized(true)
        console.log('🎯 Sistema de avatar inicializado')
      }
    }

    loadUserAvatars()
  }, [])

  // Función para convertir avatar del backend a configuración del editor
  const convertAvatarToConfig = (avatar: any): AvatarConfig | null => {
    if (!avatar.layers || avatar.layers.length === 0) return null

    const config: AvatarConfig = {
      background: 'gradient1',
      body: 'default', 
      hair: 'short',
      hairColor: '#1a1a1a',
      eyes: 'normal',
      eyebrows: 'normal',
      mouth: 'smile', 
      accessories: 'none',
      clothing: 'tshirt',
      clothingColor: '#3B82F6'
    }

    avatar.layers.forEach((layer: any) => {
      const assetName = layer.filename.split('.')[0]
      
      switch (layer.category) {
        case 'hair':
          if (avatarAssets.hairs.find(h => h.id === assetName)) {
            config.hair = assetName
          }
          break
        case 'eyes':
          if (avatarAssets.eyes.find(e => e.id === assetName)) {
            config.eyes = assetName
          }
          break
        case 'eyebrows':
          if (avatarAssets.eyebrows.find(e => e.id === assetName)) {
            config.eyebrows = assetName
          }
          break
        case 'mouth':
          if (avatarAssets.mouths.find(m => m.id === assetName)) {
            config.mouth = assetName
          }
          break
        case 'accessories':
          if (avatarAssets.accessories.find(a => a.id === assetName)) {
            config.accessories = assetName
          }
          break
        case 'clothing':
          if (avatarAssets.clothing.find(c => c.id === assetName)) {
            config.clothing = assetName
          }
          break
        case 'body':
          if (avatarAssets.bodies.find(b => b.id === assetName)) {
            config.body = assetName
          }
          break
        case 'background':
          if (avatarAssets.backgrounds.find(b => b.id === assetName)) {
            config.background = assetName
          }
          break
      }
    })

    return config
  }

  const categories = [
    { id: 'body', name: 'Cuerpo', icon: FiUser, color: 'from-orange-500 to-red-600' },
    { id: 'hair', name: 'Cabello', icon: FiRefreshCw, color: 'from-amber-500 to-orange-600' },
    { id: 'face', name: 'Rostro', icon: FiEye, color: 'from-emerald-500 to-teal-600' },
    { id: 'accessories', name: 'Accesorios', icon: FiLayers, color: 'from-purple-500 to-pink-600' },
    { id: 'clothing', name: 'Ropa', icon: FiLayers, color: 'from-blue-500 to-indigo-600' },
    { id: 'background', name: 'Fondo', icon: HiSparkles, color: 'from-gray-500 to-gray-700' }
  ]

  const handleConfigChange = useCallback((key: keyof AvatarConfig, value: string) => {
    setCurrentConfig(prev => ({ ...prev, [key]: value }))
  }, [selectedGender])

  const randomizeAvatar = () => {
    const random = {
      background: avatarAssets.backgrounds[Math.floor(Math.random() * avatarAssets.backgrounds.length)].id,
      body: avatarAssets.bodies[Math.floor(Math.random() * avatarAssets.bodies.length)].id,
      hair: avatarAssets.hairs[Math.floor(Math.random() * avatarAssets.hairs.length)].id,
      hairColor: avatarAssets.hairColors[Math.floor(Math.random() * avatarAssets.hairColors.length)],
      eyes: avatarAssets.eyes[Math.floor(Math.random() * avatarAssets.eyes.length)].id,
      eyebrows: avatarAssets.eyebrows[Math.floor(Math.random() * avatarAssets.eyebrows.length)].id,
      mouth: avatarAssets.mouths[Math.floor(Math.random() * avatarAssets.mouths.length)].id,
      accessories: avatarAssets.accessories[Math.floor(Math.random() * avatarAssets.accessories.length)].id,
      clothing: avatarAssets.clothing[Math.floor(Math.random() * avatarAssets.clothing.length)].id,
      clothingColor: avatarAssets.clothingColors[Math.floor(Math.random() * avatarAssets.clothingColors.length)]
    }
    setCurrentConfig(random)
    console.log('🎲 Avatar aleatorio generado para género:', selectedGender)
  }

  const saveAvatar = () => {
    setSavedAvatars(prev => [...prev, currentConfig])
    console.log('💾 Avatar guardado para género:', selectedGender)
  }

  const switchGender = (gender: 'male' | 'female') => {
    setSelectedGender(gender)
    console.log('🚻 Cambiado a género:', gender)
  }

  const toggleLayer = (layer: keyof typeof showLayer) => {
    setShowLayer(prev => ({ ...prev, [layer]: !prev[layer] }))
  }

  const renderCategoryContent = () => {
    switch (activeCategory) {
      case 'body':
        return (
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Tono de Piel</h4>
              <div className="grid grid-cols-5 gap-2">
                {avatarAssets.bodies.map(body => (
                  <motion.button
                    key={body.id}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleConfigChange('body', body.id)}
                    className={`w-12 h-12 rounded-xl border-2 ${
                      currentConfig.body === body.id ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-300'
                    } hover:border-blue-400 transition-all duration-200`}
                    style={{ backgroundColor: body.color }}
                    title={body.name}
                  />
                ))}
              </div>
            </div>
          </div>
        )

      case 'hair':
        return (
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Estilo de Cabello</h4>
              <div className="grid grid-cols-3 gap-2">
                {avatarAssets.hairs.map(hair => (
                  <motion.button
                    key={hair.id}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleConfigChange('hair', hair.id)}
                    className={`p-3 rounded-lg border-2 text-sm font-medium ${
                      currentConfig.hair === hair.id 
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' 
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                    } transition-all duration-200`}
                  >
                    {hair.name}
                  </motion.button>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Color de Cabello</h4>
              <div className="grid grid-cols-5 gap-2">
                {avatarAssets.hairColors.map(color => (
                  <motion.button
                    key={color}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleConfigChange('hairColor', color)}
                    className={`w-12 h-12 rounded-xl border-2 ${
                      currentConfig.hairColor === color ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-300'
                    } hover:border-blue-400 transition-all duration-200`}
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
            </div>
          </div>
        )

      case 'face':
        return (
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Ojos</h4>
              <div className="grid grid-cols-2 gap-2">
                {avatarAssets.eyes.map(eye => (
                  <motion.button
                    key={eye.id}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleConfigChange('eyes', eye.id)}
                    className={`p-3 rounded-lg border-2 text-sm font-medium ${
                      currentConfig.eyes === eye.id 
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' 
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                    } transition-all duration-200`}
                  >
                    {eye.name}
                  </motion.button>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Cejas</h4>
              <div className="grid grid-cols-2 gap-2">
                {avatarAssets.eyebrows.map(eyebrow => (
                  <motion.button
                    key={eyebrow.id}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleConfigChange('eyebrows', eyebrow.id)}
                    className={`p-3 rounded-lg border-2 text-sm font-medium ${
                      currentConfig.eyebrows === eyebrow.id 
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' 
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                    } transition-all duration-200`}
                  >
                    {eyebrow.name}
                  </motion.button>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Boca</h4>
              <div className="grid grid-cols-2 gap-2">
                {avatarAssets.mouths.map(mouth => (
                  <motion.button
                    key={mouth.id}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleConfigChange('mouth', mouth.id)}
                    className={`p-3 rounded-lg border-2 text-sm font-medium ${
                      currentConfig.mouth === mouth.id 
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' 
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                    } transition-all duration-200`}
                  >
                    {mouth.name}
                  </motion.button>
                ))}
              </div>
            </div>
          </div>
        )

      case 'accessories':
        return (
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Accesorios</h4>
              <div className="grid grid-cols-2 gap-2">
                {avatarAssets.accessories.map(accessory => (
                  <motion.button
                    key={accessory.id}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleConfigChange('accessories', accessory.id)}
                    className={`p-3 rounded-lg border-2 text-sm font-medium ${
                      currentConfig.accessories === accessory.id 
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' 
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                    } transition-all duration-200`}
                  >
                    {accessory.name}
                  </motion.button>
                ))}
              </div>
            </div>
          </div>
        )

      case 'clothing':
        return (
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Tipo de Ropa</h4>
              <div className="grid grid-cols-2 gap-2">
                {avatarAssets.clothing.map(cloth => (
                  <motion.button
                    key={cloth.id}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleConfigChange('clothing', cloth.id)}
                    className={`p-3 rounded-lg border-2 text-sm font-medium ${
                      currentConfig.clothing === cloth.id 
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' 
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                    } transition-all duration-200`}
                  >
                    {cloth.name}
                  </motion.button>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Color de Ropa</h4>
              <div className="grid grid-cols-4 gap-2">
                {avatarAssets.clothingColors.map(color => (
                  <motion.button
                    key={color}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleConfigChange('clothingColor', color)}
                    className={`w-12 h-12 rounded-xl border-2 ${
                      currentConfig.clothingColor === color ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-300'
                    } hover:border-blue-400 transition-all duration-200`}
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
            </div>
          </div>
        )

      case 'background':
        return (
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Fondos</h4>
              <div className="grid grid-cols-2 gap-3">
                {avatarAssets.backgrounds.map(bg => (
                  <motion.button
                    key={bg.id}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleConfigChange('background', bg.id)}
                    className={`h-16 rounded-lg border-2 text-xs font-medium text-white relative overflow-hidden ${
                      currentConfig.background === bg.id 
                        ? 'border-blue-500 ring-2 ring-blue-200' 
                        : 'border-gray-300 hover:border-blue-400'
                    } transition-all duration-200`}
                    style={{ background: bg.style }}
                  >
                    <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                      {bg.name}
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/30 to-pink-50/50 dark:from-gray-900 dark:via-gray-900 dark:to-purple-950/30">
      {/* Loading overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-2xl">
            <div className="flex items-center space-x-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Cargando Avatar
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Preparando tu editor personalizado...
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                  <HiSparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    Avatar Studio
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Crea tu avatar perfecto
                  </p>
                </div>
              </div>

              {/* Gender Selector */}
              <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
                <button
                  onClick={() => {
                    setSelectedGender('male')
                    // toast.info('Género cambiado', 'Editando avatar masculino')
                  }}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    selectedGender === 'male'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 dark:text-gray-400 hover:text-blue-600'
                  }`}
                >
                  ♂ Masculino
                </button>
                <button
                  onClick={() => {
                    setSelectedGender('female')
                    // toast.info('Género cambiado', 'Editando avatar femenino')
                  }}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    selectedGender === 'female'
                      ? 'bg-pink-600 text-white'
                      : 'text-gray-600 dark:text-gray-400 hover:text-pink-600'
                  }`}
                >
                  ♀ Femenino
                </button>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={randomizeAvatar}
                className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
              >
                <FiShuffle className="w-4 h-4" />
                <span className="hidden sm:block">Aleatorio</span>
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={saveAvatar}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <FiSave className="w-4 h-4" />
                <span className="hidden sm:block">Guardar</span>
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Avatar Preview */}
          <div className="lg:col-span-1">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 sticky top-24">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Vista Previa
                </h3>
                <div className="flex items-center space-x-2">
                  <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                    <FiDownload className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                    <FiRotateCw className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="flex justify-center mb-6">
                <div className="relative">
                  <AvatarPreview 
                    key={`${selectedGender}-${currentConfig.hair}-${currentConfig.clothing}`}
                    config={currentConfig} 
                    showLayer={showLayer} 
                    onConfigChange={handleConfigChange} 
                  />
                  {/* Indicador de estado del sistema */}
                  <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
                    <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                      isInitialized 
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' 
                        : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                    }`}>
                      {isInitialized ? `✅ ${selectedGender === 'male' ? 'Masculino' : 'Femenino'}` : '⏳ Cargando...'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Layer Controls */}
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Control de Capas
                </h4>
                {Object.entries(showLayer).map(([layer, visible]) => (
                  <div key={layer} className="flex items-center justify-between py-1">
                    <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                      {layer}
                    </span>
                    <button
                      onClick={() => toggleLayer(layer as keyof typeof showLayer)}
                      className={`flex items-center space-x-1 px-2 py-1 rounded text-xs ${
                        visible 
                          ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' 
                          : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-500'
                      }`}
                    >
                      {visible ? <FiEye className="w-3 h-3" /> : <FiEyeOff className="w-3 h-3" />}
                      <span>{visible ? 'Visible' : 'Oculto'}</span>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Customization Panel */}
          <div className="lg:col-span-2">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 dark:border-gray-700/50 overflow-hidden">
              
              {/* Category Tabs */}
              <div className="border-b border-gray-200/50 dark:border-gray-700/50">
                <div className="flex overflow-x-auto">
                  {categories.map((category) => (
                    <motion.button
                      key={category.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setActiveCategory(category.id)}
                      className={`flex items-center space-x-2 px-6 py-4 text-sm font-medium whitespace-nowrap border-b-2 transition-all duration-200 ${
                        activeCategory === category.id
                          ? 'border-blue-500 text-blue-600 dark:text-blue-400 bg-blue-50/50 dark:bg-blue-900/20'
                          : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-lg bg-gradient-to-r ${category.color} flex items-center justify-center`}>
                        <category.icon className="w-4 h-4 text-white" />
                      </div>
                      <span>{category.name}</span>
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Content */}
              <div className="p-6">
                {/* Gender Selector - Always Visible */}
                <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-6 rounded-2xl shadow-xl text-white mb-6">
                  <h3 className="text-lg font-bold mb-4 flex items-center">
                    <FiUser className="mr-2" />
                    🚻 Sistema de Género Intercambiable
                  </h3>
                  <p className="text-sm opacity-90 mb-4">
                    Crea avatares masculinos y femeninos por separado. Puedes cambiar entre ellos cuando quieras.
                  </p>
                  <div className="flex gap-3">
                    <button
                      onClick={() => switchGender('male')}
                      className={`flex-1 py-3 px-4 rounded-xl font-bold transition-all ${
                        selectedGender === 'male' 
                          ? 'bg-white text-purple-600 shadow-lg' 
                          : 'bg-white/20 text-white border border-white/30'
                      }`}
                    >
                      👨 Masculino
                    </button>
                    <button
                      onClick={() => switchGender('female')}
                      className={`flex-1 py-3 px-4 rounded-xl font-bold transition-all ${
                        selectedGender === 'female' 
                          ? 'bg-white text-purple-600 shadow-lg' 
                          : 'bg-white/20 text-white border border-white/30'
                      }`}
                    >
                      👩 Femenino
                    </button>
                  </div>
                  <div className="mt-3 text-xs opacity-75 text-center">
                    Configuración actual: {selectedGender === 'male' ? 'Masculino' : 'Femenino'}
                  </div>
                </div>

                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeCategory}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.2 }}
                  >
                    {renderCategoryContent()}
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>

            {/* Saved Avatars Gallery */}
            {savedAvatars.length > 0 && (
              <div className="mt-8 bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Avatares Guardados ({savedAvatars.length})
                </h3>
                <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-4">
                  {savedAvatars.map((avatar, index) => (
                    <motion.button
                      key={index}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setCurrentConfig(avatar)}
                      className="relative group"
                    >
                      <div className="w-full aspect-square">
                        <AvatarPreview 
                          config={avatar} 
                          showLayer={showLayer} 
                          onConfigChange={handleConfigChange} 
                        />
                      </div>
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 rounded-2xl transition-colors flex items-center justify-center">
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                          <FiEye className="w-6 h-6 text-white" />
                        </div>
                      </div>
                    </motion.button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}