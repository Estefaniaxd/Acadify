import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useToast } from '../context/ToastContext'
import { 
  HiOutlineShoppingBag,
  HiOutlineStar,
  HiOutlineHeart,
  HiOutlineShoppingCart,
  HiOutlineFilter,
  HiOutlineSearch,
  HiOutlineTrendingUp,
  HiOutlineGift,
  HiOutlineLightningBolt,
  HiOutlineBadgeCheck,
  HiOutlineColorSwatch,
  HiOutlineBookOpen,
  HiOutlineMoon,
  HiOutlineMusicNote,
  HiOutlineTag,
  HiOutlineUser,
  HiOutlineCamera,
  HiOutlineSparkles,
  HiOutlineBeaker,
  HiOutlineCash,
  HiOutlineCode,
  HiOutlineEye,
  HiOutlineX,
  HiOutlineCheck,
} from 'react-icons/hi'
import { HiSparkles, HiFire, HiLightningBolt } from 'react-icons/hi'

interface StoreItem {
  id: string
  name: string
  description: string
  category: 'themes' | 'avatar-accessories' | 'profile-badges' | 'animations' | 'sounds' | 'special-effects' | 'premium-features'
  subcategory?: string
  price: number
  originalPrice?: number
  currency: 'coins' | 'gems' | 'premium'
  rarity: 'common' | 'rare' | 'epic' | 'legendary' | 'mythic'
  icon: any
  preview?: string
  colors?: string[]
  isNew?: boolean
  isPopular?: boolean
  isLimited?: boolean
  discount?: number
  owned?: boolean
  likes: number
  purchases: number
  tags: string[]
}

interface UserInventory {
  coins: number
  gems: number
  premium: boolean
  cart: string[]
  wishlist: string[]
}

const mockUserInventory: UserInventory = {
  coins: 2450,
  gems: 38,
  premium: false,
  cart: [],
  wishlist: ['theme-cyberpunk', 'badge-bookworm']
}

const storeCategories = [
  { 
    id: 'all', 
    name: 'Todo', 
    icon: HiOutlineShoppingBag, 
    color: 'text-gray-500' 
  },
  { 
    id: 'themes', 
    name: 'Temas de Perfil', 
    icon: HiOutlineColorSwatch, 
    color: 'text-purple-500',
    description: 'Etiquetas y estilos para tu perfil'
  },
  { 
    id: 'avatar-accessories', 
    name: 'Accesorios Avatar', 
    icon: HiOutlineBadgeCheck, 
    color: 'text-yellow-500',
    description: 'Sombreros, gafas, joyas y más'
  },
  { 
    id: 'profile-badges', 
    name: 'Insignias', 
    icon: HiOutlineStar, 
    color: 'text-blue-500',
    description: 'Insignias especiales para mostrar'
  },
  { 
    id: 'animations', 
    name: 'Animaciones', 
    icon: HiOutlineLightningBolt, 
    color: 'text-green-500',
    description: 'Efectos animados para tu perfil'
  },
  // Sonidos y otros pueden agregarse con íconos válidos si se desea
  { 
    id: 'special-effects', 
    name: 'Efectos Especiales', 
    icon: HiOutlineStar, 
    color: 'text-pink-500',
    description: 'Partículas y efectos únicos'
  },
  { 
    id: 'premium-features', 
    name: 'Funciones Premium', 
    icon: HiOutlineLightningBolt, 
    color: 'text-orange-500',
    description: 'Características exclusivas'
  }
]

const mockStoreItems: StoreItem[] = [
  // TEMAS DE PERFIL
  {
    id: 'theme-reader',
    name: 'Etiqueta: Lector',
    description: 'Muestra tu pasión por la lectura con esta elegante etiqueta',
    category: 'themes',
    subcategory: 'hobbies',
    price: 150,
    currency: 'coins',
    rarity: 'common',
  icon: HiOutlineBookOpen,
    colors: ['#8B4513', '#DEB887'],
    isPopular: true,
    likes: 234,
    purchases: 1450,
    tags: ['lectura', 'libros', 'conocimiento']
  },
  {
    id: 'theme-gamer',
    name: 'Etiqueta: Gamer Pro',
    description: 'Para los verdaderos gamers que dominan todos los juegos',
    category: 'themes',
    subcategory: 'gaming',
    price: 200,
    currency: 'coins',
    rarity: 'rare',
  icon: HiOutlineLightningBolt,
    colors: ['#00FF41', '#000000'],
    isNew: true,
    likes: 567,
    purchases: 890,
    tags: ['gaming', 'videojuegos', 'competitivo']
  },
  {
    id: 'theme-sleepy',
    name: 'Etiqueta: Dormilón',
    description: 'Para quienes valoran un buen descanso',
    category: 'themes',
    subcategory: 'lifestyle',
    price: 100,
    currency: 'coins',
    rarity: 'common',
  icon: HiOutlineMoon,
    colors: ['#191970', '#E6E6FA'],
    likes: 189,
    purchases: 2100,
    tags: ['descanso', 'sueño', 'relajación']
  },
  {
    id: 'theme-cyberpunk',
    name: 'Etiqueta: Cyberpunk',
    description: 'Estilo futurista cyberpunk con efectos neón',
    category: 'themes',
    subcategory: 'futuristic',
    price: 15,
    currency: 'gems',
    rarity: 'epic',
  icon: HiOutlineLightningBolt,
    colors: ['#FF0080', '#00FFFF'],
    isLimited: true,
    discount: 25,
    originalPrice: 20,
    likes: 892,
    purchases: 234,
    tags: ['futurista', 'neón', 'tech']
  },
  {
    id: 'theme-nature',
    name: 'Etiqueta: Amante Naturaleza',
    description: 'Conecta con la naturaleza y muestra tu lado eco-friendly',
    category: 'themes',
    subcategory: 'nature',
    price: 180,
    currency: 'coins',
    rarity: 'rare',
  icon: HiOutlineBeaker,
    colors: ['#228B22', '#90EE90'],
    likes: 345,
    purchases: 678,
    tags: ['naturaleza', 'eco', 'verde']
  },

  // ACCESORIOS AVATAR
  {
    id: 'acc-crown-golden',
    name: 'Corona Dorada Real',
    description: 'Una majestuosa corona dorada para verdaderos reyes',
    category: 'avatar-accessories',
    subcategory: 'headwear',
    price: 50,
    currency: 'gems',
    rarity: 'legendary',
  icon: HiOutlineBadgeCheck,
    colors: ['#FFD700', '#FFA500'],
    isPopular: true,
    likes: 1234,
    purchases: 567,
    tags: ['corona', 'real', 'elegante']
  },
  {
    id: 'acc-glasses-cyber',
    name: 'Gafas Cyber RGB',
    description: 'Gafas futuristas con luces LED que cambian de color',
    category: 'avatar-accessories',
    subcategory: 'eyewear',
    price: 25,
    currency: 'gems',
    rarity: 'epic',
  icon: HiOutlineEye,
    colors: ['#FF0000', '#00FF00', '#0000FF'],
    isNew: true,
    likes: 678,
    purchases: 234,
    tags: ['gafas', 'futurista', 'LED']
  },
  {
    id: 'acc-headphones-dj',
    name: 'Auriculares DJ Pro',
    description: 'Auriculares profesionales para DJs y productores',
    category: 'avatar-accessories',
    subcategory: 'audio',
    price: 300,
    currency: 'coins',
    rarity: 'rare',
  icon: HiOutlineMusicNote,
    colors: ['#000000', '#FF6B35'],
    likes: 456,
    purchases: 789,
    tags: ['auriculares', 'música', 'DJ']
  },
  {
    id: 'acc-watch-smart',
    name: 'Smartwatch Elite',
    description: 'Reloj inteligente de última generación',
    category: 'avatar-accessories',
    subcategory: 'tech',
    price: 400,
    currency: 'coins',
    rarity: 'epic',
  icon: HiOutlineCash,
    colors: ['#1E1E1E', '#00D4FF'],
    likes: 567,
    purchases: 123,
    tags: ['reloj', 'smart', 'tecnología']
  },

  // INSIGNIAS
  {
    id: 'badge-bookworm',
    name: 'Insignia: Ratón de Biblioteca',
    description: 'Para los verdaderos devoradores de libros',
    category: 'profile-badges',
    subcategory: 'achievement',
    price: 5,
    currency: 'gems',
    rarity: 'rare',
  icon: HiOutlineBookOpen,
    colors: ['#8B4513', '#F5DEB3'],
    likes: 890,
    purchases: 2340,
    tags: ['libros', 'lectura', 'conocimiento']
  },
  {
    id: 'badge-code-master',
    name: 'Insignia: Maestro del Código',
    description: 'Para programadores expertos',
    category: 'profile-badges',
    subcategory: 'skill',
    price: 12,
    currency: 'gems',
    rarity: 'epic',
  icon: HiOutlineCode,
    colors: ['#00FF00', '#000000'],
    isPopular: true,
    likes: 1567,
    purchases: 890,
    tags: ['programación', 'código', 'tech']
  },
  {
    id: 'badge-coffee-lover',
    name: 'Insignia: Adicto al Café',
    description: 'Para los que no pueden vivir sin café',
    category: 'profile-badges',
    subcategory: 'lifestyle',
    price: 150,
    currency: 'coins',
    rarity: 'common',
  icon: HiOutlineBeaker,
    colors: ['#8B4513', '#D2691E'],
    likes: 2890,
    purchases: 5670,
    tags: ['café', 'energía', 'mañanas']
  },

  // ANIMACIONES
  {
    id: 'anim-sparkles',
    name: 'Chispas Mágicas',
    description: 'Partículas brillantes que rodean tu avatar',
    category: 'animations',
    subcategory: 'particles',
    price: 20,
    currency: 'gems',
    rarity: 'epic',
    icon: HiSparkles,
    colors: ['#FFD700', '#FFFFFF'],
    isNew: true,
    likes: 1234,
    purchases: 567,
    tags: ['magia', 'brillos', 'partículas']
  },
  {
    id: 'anim-fire-trail',
    name: 'Rastro de Fuego',
    description: 'Deja un rastro de fuego donde camines',
    category: 'animations',
    subcategory: 'trails',
    price: 35,
    currency: 'gems',
    rarity: 'legendary',
    icon: HiFire,
    colors: ['#FF4500', '#FF0000'],
    isLimited: true,
    likes: 890,
    purchases: 123,
    tags: ['fuego', 'rastro', 'épico']
  },

  // FUNCIONES PREMIUM
  {
    id: 'premium-profile-music',
    name: 'Música de Perfil',
    description: 'Añade una canción de fondo a tu perfil',
    category: 'premium-features',
    subcategory: 'profile',
    price: 1,
    currency: 'premium',
    rarity: 'mythic',
  icon: HiOutlineMusicNote,
    colors: ['#9B59B6', '#E74C3C'],
    likes: 3456,
    purchases: 890,
    tags: ['música', 'premium', 'perfil']
  },
  {
    id: 'premium-custom-url',
    name: 'URL Personalizada',
    description: 'Crea una URL única para tu perfil',
    category: 'premium-features',
    subcategory: 'profile',
    price: 1,
    currency: 'premium',
    rarity: 'mythic',
  icon: HiOutlineTag,
    colors: ['#3498DB', '#2ECC71'],
    likes: 2345,
    purchases: 567,
    tags: ['URL', 'personalización', 'único']
  }
]

const rarityStyles = {
  common: { 
    bg: 'bg-gray-100 dark:bg-gray-800', 
    border: 'border-gray-300 dark:border-gray-600', 
    text: 'text-gray-600 dark:text-gray-400',
    glow: 'shadow-gray-200 dark:shadow-gray-800'
  },
  rare: { 
    bg: 'bg-blue-100 dark:bg-blue-900/30', 
    border: 'border-blue-300 dark:border-blue-600', 
    text: 'text-blue-600 dark:text-blue-400',
    glow: 'shadow-blue-200 dark:shadow-blue-800'
  },
  epic: { 
    bg: 'bg-purple-100 dark:bg-purple-900/30', 
    border: 'border-purple-300 dark:border-purple-600', 
    text: 'text-purple-600 dark:text-purple-400',
    glow: 'shadow-purple-200 dark:shadow-purple-800'
  },
  legendary: { 
    bg: 'bg-yellow-100 dark:bg-yellow-900/30', 
    border: 'border-yellow-300 dark:border-yellow-600', 
    text: 'text-yellow-600 dark:text-yellow-400',
    glow: 'shadow-yellow-200 dark:shadow-yellow-800'
  },
  mythic: { 
    bg: 'bg-gradient-to-r from-pink-100 to-purple-100 dark:from-pink-900/30 dark:to-purple-900/30', 
    border: 'border-pink-300 dark:border-pink-600', 
    text: 'text-pink-600 dark:text-pink-400',
    glow: 'shadow-pink-200 dark:shadow-pink-800'
  }
}

export default function TiendaPage() {
  const toast = useToast()
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'popular' | 'newest' | 'price-low' | 'price-high'>('popular')
  const [showOwned, setShowOwned] = useState(false)
  const [selectedItem, setSelectedItem] = useState<StoreItem | null>(null)
  const [userInventory, setUserInventory] = useState(mockUserInventory)
  const [cartItems, setCartItems] = useState<string[]>([])
  const [wishlistItems, setWishlistItems] = useState<string[]>(mockUserInventory.wishlist)

  const filteredItems = mockStoreItems.filter(item => {
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory
    const matchesSearch = searchQuery === '' || 
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesOwned = !showOwned || item.owned
    
    return matchesCategory && matchesSearch && matchesOwned
  }).sort((a, b) => {
    switch (sortBy) {
      case 'newest': return (a.isNew ? 1 : 0) - (b.isNew ? 1 : 0)
      case 'price-low': return a.price - b.price
      case 'price-high': return b.price - a.price
      case 'popular':
      default: return b.purchases - a.purchases
    }
  })

  const addToCart = (itemId: string) => {
    if (!cartItems.includes(itemId)) {
      setCartItems(prev => [...prev, itemId])
      toast.success('¡Añadido!', 'Producto añadido al carrito')
    }
  }

  const toggleWishlist = (itemId: string) => {
    if (wishlistItems.includes(itemId)) {
      setWishlistItems(prev => prev.filter(id => id !== itemId))
      toast.success('Eliminado', 'Producto eliminado de favoritos')
    } else {
      setWishlistItems(prev => [...prev, itemId])
      toast.success('¡Guardado!', 'Producto añadido a favoritos')
    }
  }

  const getCurrencyIcon = (currency: string) => {
    switch (currency) {
      case 'coins': return '🪙'
      case 'gems': return '💎'
      case 'premium': return '👑'
      default: return '🪙'
    }
  }

  const getRarityName = (rarity: string) => {
    const names = {
      common: 'Común',
      rare: 'Raro',
      epic: 'Épico',
      legendary: 'Legendario',
      mythic: 'Mítico'
    }
    return names[rarity as keyof typeof names] || 'Común'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50/30 to-indigo-50/50 dark:from-gray-900 dark:via-purple-950/30 dark:to-blue-950/30">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                <HiOutlineShoppingBag className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Tienda Acadify
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Personaliza tu experiencia
                </p>
              </div>
            </div>

            {/* User Currency & Cart */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3 bg-white/50 dark:bg-gray-800/50 rounded-xl px-4 py-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  🪙 {userInventory.coins}
                </span>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  💎 {userInventory.gems}
                </span>
                {userInventory.premium && (
                  <span className="text-sm font-medium text-yellow-600 dark:text-yellow-400">
                    👑 Premium
                  </span>
                )}
              </div>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="relative p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
              >
                <HiOutlineShoppingCart className="w-5 h-5" />
                {cartItems.length > 0 && (
                  <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-white">{cartItems.length}</span>
                  </div>
                )}
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filters */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-8">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <HiOutlineSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar productos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 bg-white/50 dark:bg-gray-800/50 border border-gray-300/50 dark:border-gray-600/50 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent w-80"
              />
            </div>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-4 py-2 bg-white/50 dark:bg-gray-800/50 border border-gray-300/50 dark:border-gray-600/50 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="popular">Más Popular</option>
              <option value="newest">Más Nuevo</option>
              <option value="price-low">Precio: Menor a Mayor</option>
              <option value="price-high">Precio: Mayor a Menor</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowOwned(!showOwned)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                showOwned
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                  : 'bg-white/50 dark:bg-gray-800/50 text-gray-600 dark:text-gray-400'
              }`}
            >
              Solo mis productos
            </motion.button>
          </div>
        </div>

        {/* Categories */}
        <div className="flex flex-wrap gap-3 mb-8">
          {storeCategories.map((category) => (
            <motion.button
              key={category.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSelectedCategory(category.id)}
              className={`flex items-center space-x-2 px-4 py-3 rounded-xl transition-all ${
                selectedCategory === category.id
                  ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300 ring-2 ring-purple-500'
                  : 'bg-white/50 dark:bg-gray-800/50 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50'
              }`}
            >
              <category.icon className={`w-5 h-5 ${category.color}`} />
              <span className="font-medium">{category.name}</span>
            </motion.button>
          ))}
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredItems.map((item, index) => {
            const rarityStyle = rarityStyles[item.rarity]
            const finalPrice = item.discount ? Math.round(item.price * (1 - item.discount / 100)) : item.price
            const isInCart = cartItems.includes(item.id)
            const isInWishlist = wishlistItems.includes(item.id)

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ y: -8, transition: { duration: 0.2 } }}
                onClick={() => setSelectedItem(item)}
                className={`relative cursor-pointer rounded-2xl p-6 border-2 transition-all duration-300 hover:shadow-xl ${rarityStyle.bg} ${rarityStyle.border} ${rarityStyle.glow} hover:shadow-lg`}
              >
                {/* Badges */}
                <div className="absolute top-3 left-3 flex flex-col space-y-1">
                  {item.isNew && (
                    <span className="px-2 py-1 bg-green-500 text-white text-xs font-bold rounded-full">
                      NUEVO
                    </span>
                  )}
                  {item.isPopular && (
                    <span className="px-2 py-1 bg-orange-500 text-white text-xs font-bold rounded-full">
                      POPULAR
                    </span>
                  )}
                  {item.isLimited && (
                    <span className="px-2 py-1 bg-red-500 text-white text-xs font-bold rounded-full">
                      LIMITADO
                    </span>
                  )}
                  {item.discount && (
                    <span className="px-2 py-1 bg-red-600 text-white text-xs font-bold rounded-full">
                      -{item.discount}%
                    </span>
                  )}
                </div>

                {/* Wishlist Button */}
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={(e) => {
                    e.stopPropagation()
                    toggleWishlist(item.id)
                  }}
                  className={`absolute top-3 right-3 p-2 rounded-full transition-colors ${
                    isInWishlist 
                      ? 'bg-red-500 text-white' 
                      : 'bg-white/50 dark:bg-gray-800/50 text-gray-400 hover:text-red-500'
                  }`}
                >
                  <HiOutlineHeart className="w-4 h-4" />
                </motion.button>

                {/* Item Icon */}
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 mt-8 ${rarityStyle.bg}`}>
                  <item.icon className={`w-8 h-8 ${item.colors ? '' : rarityStyle.text}`} 
                    style={item.colors ? { color: item.colors[0] } : {}} />
                </div>

                {/* Item Info */}
                <div className="mb-4">
                  <h3 className="font-bold text-gray-900 dark:text-white mb-2 line-clamp-2">
                    {item.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                    {item.description}
                  </p>

                  {/* Rarity */}
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${rarityStyle.text} ${rarityStyle.bg}`}>
                    {getRarityName(item.rarity)}
                  </span>
                </div>

                {/* Stats */}
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-4">
                  <span className="flex items-center space-x-1">
                    <HiOutlineHeart className="w-3 h-3" />
                    <span>{item.likes}</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <HiOutlineShoppingBag className="w-3 h-3" />
                    <span>{item.purchases}</span>
                  </span>
                </div>

                {/* Price */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg font-bold text-gray-900 dark:text-white">
                      {getCurrencyIcon(item.currency)} {finalPrice}
                    </span>
                    {item.originalPrice && item.discount && (
                      <span className="text-sm line-through text-gray-500">
                        {item.originalPrice}
                      </span>
                    )}
                  </div>

                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={(e) => {
                      e.stopPropagation()
                      addToCart(item.id)
                    }}
                    disabled={isInCart || item.owned}
                    className={`p-2 rounded-lg transition-colors ${
                      isInCart || item.owned
                        ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 cursor-not-allowed'
                        : 'bg-purple-600 hover:bg-purple-700 text-white'
                    }`}
                  >
                    {item.owned ? <HiOutlineCheck className="w-4 h-4" /> :
                     isInCart ? <HiOutlineCheck className="w-4 h-4" /> :
                     <HiOutlineShoppingCart className="w-4 h-4" />}
                  </motion.button>
                </div>

                {/* Owned Overlay */}
                {item.owned && (
                  <div className="absolute inset-0 bg-green-500/20 rounded-2xl flex items-center justify-center">
                    <div className="bg-green-500 text-white px-4 py-2 rounded-lg font-bold">
                      TIENES ESTE PRODUCTO
                    </div>
                  </div>
                )}
              </motion.div>
            )
          })}
        </div>

        {filteredItems.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-16"
          >
            <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <HiOutlineShoppingBag className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No se encontraron productos
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              Intenta cambiar los filtros o términos de búsqueda.
            </p>
          </motion.div>
        )}
      </div>

      {/* Product Detail Modal */}
      <AnimatePresence>
        {selectedItem && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedItem(null)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white dark:bg-gray-900 rounded-2xl p-6 max-w-lg w-full border border-gray-200 dark:border-gray-700 max-h-[80vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                  Detalles del Producto
                </h3>
                <button
                  onClick={() => setSelectedItem(null)}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  <HiOutlineX className="w-5 h-5" />
                </button>
              </div>

              <div className="text-center mb-6">
                <div className={`w-24 h-24 rounded-2xl flex items-center justify-center mx-auto mb-4 ${rarityStyles[selectedItem.rarity].bg}`}>
                  <selectedItem.icon className={`w-12 h-12 ${rarityStyles[selectedItem.rarity].text}`} />
                </div>

                <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                  {selectedItem.name}
                </h4>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {selectedItem.description}
                </p>

                <div className="flex items-center justify-center space-x-4 mb-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${rarityStyles[selectedItem.rarity].text} ${rarityStyles[selectedItem.rarity].bg}`}>
                    {getRarityName(selectedItem.rarity)}
                  </span>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {getCurrencyIcon(selectedItem.currency)} {selectedItem.discount ? Math.round(selectedItem.price * (1 - selectedItem.discount / 100)) : selectedItem.price}
                  </span>
                </div>
              </div>

              {/* Tags */}
              <div className="mb-6">
                <h5 className="font-semibold text-gray-900 dark:text-white mb-2">Etiquetas:</h5>
                <div className="flex flex-wrap gap-2">
                  {selectedItem.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded-full text-xs"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {selectedItem.likes}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Me gusta</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {selectedItem.purchases}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Compras</div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-3">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => addToCart(selectedItem.id)}
                  disabled={cartItems.includes(selectedItem.id) || selectedItem.owned}
                  className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 text-white rounded-lg transition-colors disabled:cursor-not-allowed"
                >
                  <HiOutlineShoppingCart className="w-4 h-4" />
                  <span>
                    {selectedItem.owned ? 'Ya lo tienes' : 
                     cartItems.includes(selectedItem.id) ? 'En carrito' : 
                     'Añadir al carrito'}
                  </span>
                </motion.button>
                
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => toggleWishlist(selectedItem.id)}
                  className={`px-4 py-3 rounded-lg transition-colors ${
                    wishlistItems.includes(selectedItem.id)
                      ? 'bg-red-500 hover:bg-red-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  <HiOutlineHeart className="w-4 h-4" />
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}