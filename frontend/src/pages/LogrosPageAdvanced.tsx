import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useToast } from '../context/ToastContext'
import { 
  HiAcademicCap,
  HiBadgeCheck,
  HiStar,
  HiCalendar,
  HiUser,
  HiUsers,
  HiBookOpen,
  HiLightningBolt,
  HiHeart,
  HiClock,
  HiCheck,
  HiGift,
  HiFire,
  HiX,
  HiEye,
  HiShare,
  HiSearch
} from 'react-icons/hi'
import { HiSparkles } from 'react-icons/hi'

interface Achievement {
  id: string
  title: string
  description: string
  category: 'learning' | 'social' | 'milestone' | 'special' | 'daily' | 'weekly'
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
  points: number
  icon: any
  color: string
  progress: number
  maxProgress: number
  unlocked: boolean
  unlockedDate?: string
  requirements: string[]
  nextLevelReward?: string
}

interface UserStats {
  totalPoints: number
  level: number
  experienceToNext: number
  totalExperience: number
  achievementsUnlocked: number
  totalAchievements: number
  streak: number
  rank: number
  totalUsers: number
}

const mockUserStats: UserStats = {
  totalPoints: 2850,
  level: 12,
  experienceToNext: 450,
  totalExperience: 3850,
  achievementsUnlocked: 18,
  totalAchievements: 45,
  streak: 7,
  rank: 156,
  totalUsers: 12400
}

const mockAchievements: Achievement[] = [
  {
    id: '1',
    title: 'Primer Paso',
    description: 'Completa tu primer curso en Acadify',
    category: 'milestone',
    rarity: 'common',
    points: 100,
  icon: HiBookOpen,
    color: 'text-green-500',
    progress: 1,
    maxProgress: 1,
    unlocked: true,
    unlockedDate: '2025-08-10',
    requirements: ['Completar 1 curso'],
    nextLevelReward: '200 puntos por completar 5 cursos'
  },
  {
    id: '2',
    title: 'Estudiante Dedicado',
    description: 'Mantén una racha de 7 días estudiando',
    category: 'daily',
    rarity: 'rare',
    points: 250,
  icon: HiFire,
    color: 'text-orange-500',
    progress: 7,
    maxProgress: 7,
    unlocked: true,
    unlockedDate: '2025-09-15',
    requirements: ['Estudiar 7 días consecutivos'],
    nextLevelReward: '500 puntos por 30 días'
  },
  {
    id: '3',
    title: 'Social Butterfly',
    description: 'Únete a 5 comunidades diferentes',
    category: 'social',
    rarity: 'rare',
    points: 200,
  icon: HiUsers,
    color: 'text-blue-500',
    progress: 3,
    maxProgress: 5,
    unlocked: false,
    requirements: ['Unirse a 5 comunidades'],
    nextLevelReward: 'Acceso a comunidades premium'
  },
  {
    id: '4',
    title: 'Maestro del Conocimiento',
    description: 'Alcanza el nivel 10 en cualquier materia',
    category: 'learning',
    rarity: 'epic',
    points: 500,
  icon: HiBadgeCheck,
    color: 'text-purple-500',
    progress: 8,
    maxProgress: 10,
    unlocked: false,
    requirements: ['Nivel 10 en una materia'],
    nextLevelReward: 'Insignia de experto'
  },
  {
    id: '5',
    title: 'Leyenda Acadify',
    description: 'Alcanza 10,000 puntos totales',
    category: 'special',
    rarity: 'legendary',
    points: 1000,
  icon: HiBadgeCheck,
    color: 'text-yellow-500',
    progress: 2850,
    maxProgress: 10000,
    unlocked: false,
    requirements: ['Acumular 10,000 puntos'],
    nextLevelReward: 'Título exclusivo y avatar especial'
  },
  {
    id: '6',
    title: 'Ayudante Comunitario',
    description: 'Ayuda a 10 compañeros con sus dudas',
    category: 'social',
    rarity: 'rare',
    points: 300,
  icon: HiHeart,
    color: 'text-pink-500',
    progress: 6,
    maxProgress: 10,
    unlocked: false,
    requirements: ['Ayudar a 10 compañeros'],
    nextLevelReward: 'Insignia de mentor'
  },
  {
    id: '7',
    title: 'Velocista',
    description: 'Completa un curso en menos de 24 horas',
    category: 'special',
    rarity: 'epic',
    points: 400,
  icon: HiLightningBolt,
    color: 'text-yellow-400',
    progress: 0,
    maxProgress: 1,
    unlocked: false,
    requirements: ['Completar curso en <24h'],
    nextLevelReward: '50% descuento en siguiente curso'
  },
  {
    id: '8',
    title: 'Madrugador',
    description: 'Estudia antes de las 6 AM durante 5 días',
    category: 'daily',
    rarity: 'rare',
    points: 250,
  icon: HiClock,
    color: 'text-indigo-500',
    progress: 2,
    maxProgress: 5,
    unlocked: false,
    requirements: ['Estudiar antes de 6 AM por 5 días'],
    nextLevelReward: 'Acceso anticipado a nuevos cursos'
  }
]

const categories = [
  { id: 'all', name: 'Todos', icon: HiBadgeCheck, color: 'text-gray-500' },
  { id: 'learning', name: 'Aprendizaje', icon: HiBookOpen, color: 'text-blue-500' },
  { id: 'social', name: 'Social', icon: HiUsers, color: 'text-green-500' },
  { id: 'milestone', name: 'Hitos', icon: HiBadgeCheck, color: 'text-purple-500' },
  { id: 'daily', name: 'Diarios', icon: HiCalendar, color: 'text-orange-500' },
  { id: 'special', name: 'Especiales', icon: HiStar, color: 'text-yellow-500' }
]

const rarityColors = {
  common: { bg: 'bg-gray-100 dark:bg-gray-800', border: 'border-gray-300 dark:border-gray-600', text: 'text-gray-600' },
  rare: { bg: 'bg-blue-100 dark:bg-blue-900/30', border: 'border-blue-300 dark:border-blue-600', text: 'text-blue-600' },
  epic: { bg: 'bg-purple-100 dark:bg-purple-900/30', border: 'border-purple-300 dark:border-purple-600', text: 'text-purple-600' },
  legendary: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', border: 'border-yellow-300 dark:border-yellow-600', text: 'text-yellow-600' }
}

export default function LogrosPageAdvanced() {
  const toast = useToast()
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [showUnlockedOnly, setShowUnlockedOnly] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedAchievement, setSelectedAchievement] = useState<Achievement | null>(null)

  const filteredAchievements = mockAchievements.filter(achievement => {
    const matchesCategory = selectedCategory === 'all' || achievement.category === selectedCategory
    const matchesUnlocked = !showUnlockedOnly || achievement.unlocked
    const matchesSearch = searchQuery === '' || 
      achievement.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      achievement.description.toLowerCase().includes(searchQuery.toLowerCase())
    
    return matchesCategory && matchesUnlocked && matchesSearch
  })

  const getProgressPercentage = (current: number, max: number) => {
    return Math.min((current / max) * 100, 100)
  }

  const getRarityName = (rarity: string) => {
    const names = {
      common: 'Común',
      rare: 'Raro',
      epic: 'Épico',
      legendary: 'Legendario'
    }
    return names[rarity as keyof typeof names] || 'Común'
  }

  const levelProgress = (mockUserStats.totalExperience % 1000) / 1000 * 100

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/50 dark:from-gray-900 dark:via-gray-900 dark:to-blue-950/30">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-2xl flex items-center justify-center">
                <HiBadgeCheck className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  Logros y Recompensas
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                  Desbloquea logros y gana recompensas por tu progreso
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <HiStar className="w-4 h-4" />
                <span>Compartir</span>
              </motion.button>
            </div>
          </div>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {/* Level & Experience */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl p-6 text-white"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-blue-100">Nivel</span>
                <HiLightningBolt className="w-5 h-5 text-blue-200" />
              </div>
              <div className="text-3xl font-bold mb-2">{mockUserStats.level}</div>
              <div className="w-full bg-blue-400/30 rounded-full h-2 mb-2">
                <div 
                  className="bg-white rounded-full h-2 transition-all duration-300"
                  style={{ width: `${levelProgress}%` }}
                />
              </div>
              <span className="text-xs text-blue-100">
                {mockUserStats.experienceToNext} XP para siguiente nivel
              </span>
            </motion.div>

            {/* Total Points */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-gray-600 dark:text-gray-400">Puntos</span>
                <HiStar className="w-5 h-5 text-yellow-500" />
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                {mockUserStats.totalPoints.toLocaleString()}
              </div>
              <span className="text-sm text-green-600 dark:text-green-400">
                +150 esta semana
              </span>
            </motion.div>

            {/* Achievements */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-gray-600 dark:text-gray-400">Logros</span>
                <HiBadgeCheck className="w-5 h-5 text-purple-500" />
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                {mockUserStats.achievementsUnlocked}/{mockUserStats.totalAchievements}
              </div>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {Math.round((mockUserStats.achievementsUnlocked / mockUserStats.totalAchievements) * 100)}% completado
              </span>
            </motion.div>

            {/* Ranking */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-gray-600 dark:text-gray-400">Ranking</span>
                <HiSparkles className="w-5 h-5 text-orange-500" />
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                #{mockUserStats.rank}
              </div>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                de {mockUserStats.totalUsers.toLocaleString()} usuarios
              </span>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
          {/* Category Filters */}
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <motion.button
                key={category.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedCategory(category.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-colors ${
                  selectedCategory === category.id
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                    : 'bg-white/50 dark:bg-gray-800/50 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50'
                }`}
              >
                <category.icon className={`w-4 h-4 ${category.color}`} />
                <span className="font-medium">{category.name}</span>
              </motion.button>
            ))}
          </div>

          {/* Search and Filters */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <HiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar logros..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 bg-white/50 dark:bg-gray-800/50 border border-gray-300/50 dark:border-gray-600/50 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowUnlockedOnly(!showUnlockedOnly)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                showUnlockedOnly
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                  : 'bg-white/50 dark:bg-gray-800/50 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50'
              }`}
            >
              {showUnlockedOnly ? 'Todos' : 'Solo desbloqueados'}
            </motion.button>
          </div>
        </div>

        {/* Achievements Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAchievements.map((achievement, index) => {
            const rarityStyle = rarityColors[achievement.rarity]
            const progressPercentage = getProgressPercentage(achievement.progress, achievement.maxProgress)

            return (
              <motion.div
                key={achievement.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ y: -5, transition: { duration: 0.2 } }}
                onClick={() => setSelectedAchievement(achievement)}
                className={`relative cursor-pointer rounded-2xl p-6 border-2 transition-all duration-300 hover:shadow-lg ${
                  achievement.unlocked 
                    ? `${rarityStyle.bg} ${rarityStyle.border}` 
                    : 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 opacity-75'
                }`}
              >
                {/* Rarity Badge */}
                <div className={`absolute top-3 right-3 px-2 py-1 rounded-full text-xs font-medium ${rarityStyle.text} ${rarityStyle.bg}`}>
                  {getRarityName(achievement.rarity)}
                </div>

                {/* Lock/Unlock Status */}
                <div className="absolute top-3 left-3">
                  {achievement.unlocked ? (
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                      <HiCheck className="w-4 h-4 text-white" />
                    </div>
                  ) : (
                    <div className="w-6 h-6 bg-gray-400 rounded-full flex items-center justify-center">
                      <HiAcademicCap className="w-4 h-4 text-white" />
                    </div>
                  )}
                </div>

                {/* Achievement Icon */}
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 mt-2 ${
                  achievement.unlocked ? rarityStyle.bg : 'bg-gray-200 dark:bg-gray-700'
                }`}>
                  <achievement.icon className={`w-8 h-8 ${achievement.unlocked ? achievement.color : 'text-gray-400'}`} />
                </div>

                {/* Achievement Info */}
                <div className="mb-4">
                  <h3 className={`text-lg font-bold mb-2 ${
                    achievement.unlocked ? 'text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {achievement.title}
                  </h3>
                  <p className={`text-sm mb-3 ${
                    achievement.unlocked ? 'text-gray-600 dark:text-gray-300' : 'text-gray-400 dark:text-gray-500'
                  }`}>
                    {achievement.description}
                  </p>
                </div>

                {/* Progress Bar */}
                {!achievement.unlocked && (
                  <div className="mb-4">
                    <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                      <span>Progreso</span>
                      <span>{achievement.progress}/{achievement.maxProgress}</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-blue-500 rounded-full h-2 transition-all duration-300"
                        style={{ width: `${progressPercentage}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Points */}
                <div className="flex items-center justify-between">
                  <span className={`font-bold ${achievement.unlocked ? rarityStyle.text : 'text-gray-400'}`}>
                    +{achievement.points} puntos
                  </span>
                  {achievement.unlocked && achievement.unlockedDate && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(achievement.unlockedDate).toLocaleDateString()}
                    </span>
                  )}
                </div>

                {/* Sparkle Effect for Unlocked */}
                {achievement.unlocked && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute top-2 right-2"
                  >
                    <HiSparkles className="w-5 h-5 text-yellow-400" />
                  </motion.div>
                )}
              </motion.div>
            )
          })}
        </div>

        {filteredAchievements.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-16"
          >
            <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <HiSearch className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No se encontraron logros
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              Prueba cambiando los filtros o el término de búsqueda.
            </p>
          </motion.div>
        )}
      </div>

      {/* Achievement Detail Modal */}
      <AnimatePresence>
        {selectedAchievement && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedAchievement(null)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white dark:bg-gray-900 rounded-2xl p-6 max-w-md w-full border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                  Detalles del Logro
                </h3>
                <button
                  onClick={() => setSelectedAchievement(null)}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  <HiX className="w-5 h-5" />
                </button>
              </div>

              <div className="text-center mb-6">
                <div className={`w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 ${
                  selectedAchievement.unlocked ? rarityColors[selectedAchievement.rarity].bg : 'bg-gray-200 dark:bg-gray-700'
                }`}>
                  <selectedAchievement.icon className={`w-10 h-10 ${
                    selectedAchievement.unlocked ? selectedAchievement.color : 'text-gray-400'
                  }`} />
                </div>

                <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                  {selectedAchievement.title}
                </h4>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {selectedAchievement.description}
                </p>

                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                  rarityColors[selectedAchievement.rarity].text
                } ${rarityColors[selectedAchievement.rarity].bg}`}>
                  {getRarityName(selectedAchievement.rarity)} • +{selectedAchievement.points} puntos
                </div>
              </div>

              {/* Requirements */}
              <div className="mb-6">
                <h5 className="font-semibold text-gray-900 dark:text-white mb-3">Requisitos:</h5>
                <ul className="space-y-2">
                  {selectedAchievement.requirements.map((req, index) => (
                    <li key={index} className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                      <div className={`w-4 h-4 rounded-full flex items-center justify-center ${
                        selectedAchievement.unlocked ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'
                      }`}>
                        <HiCheck className={`w-3 h-3 ${
                          selectedAchievement.unlocked ? 'text-white' : 'text-gray-500'
                        }`} />
                      </div>
                      <span>{req}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Progress */}
              {!selectedAchievement.unlocked && (
                <div className="mb-6">
                  <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                    <span>Tu progreso</span>
                    <span>{selectedAchievement.progress}/{selectedAchievement.maxProgress}</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                    <div 
                      className="bg-blue-500 rounded-full h-3 transition-all duration-300"
                      style={{ width: `${getProgressPercentage(selectedAchievement.progress, selectedAchievement.maxProgress)}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Next Level Reward */}
              {selectedAchievement.nextLevelReward && (
                <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-4 mb-6">
                  <h5 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">
                    Siguiente recompensa:
                  </h5>
                  <p className="text-sm text-blue-700 dark:text-blue-400">
                    {selectedAchievement.nextLevelReward}
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="flex space-x-3">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <HiShare className="w-4 h-4" />
                  <span>Compartir</span>
                </motion.button>
                
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                >
                  <HiEye className="w-4 h-4" />
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}