import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Award, Book, Calendar, Filter, Heart, Lock, Search, Shield, Sparkles, Star, Target, TrendingUp, Unlock, Users, Zap } from 'lucide-react';
;
;

// Datos mock de insignias
const insigniasData = [
  {
    id: 1,
    name: 'Primer Paso',
    description: 'Completaste tu primer curso en Acadify',
    icon: Book,
    category: 'Aprendizaje',
    rarity: 'común',
    points: 100,
    obtained: true,
    dateObtained: '2024-01-15',
    color: 'from-blue-500 to-blue-600',
    requirements: 'Completa tu primer curso',
    progress: 100
  },
  {
    id: 2,
    name: 'Colaborador',
    description: 'Ayudaste a otros estudiantes en los foros',
    icon: Users,
    category: 'Social',
    rarity: 'común',
    points: 150,
    obtained: true,
    dateObtained: '2024-01-20',
    color: 'from-emerald-500 to-emerald-600',
    requirements: 'Ayuda a 5 compañeros en los foros',
    progress: 100
  },
  {
    id: 3,
    name: 'Maestro del Conocimiento',
    description: 'Alcanzaste una puntuación perfecta en 10 evaluaciones',
    icon: Star,
    category: 'Excelencia',
    rarity: 'raro',
    points: 500,
    obtained: true,
    dateObtained: '2024-02-01',
    color: 'from-yellow-500 to-orange-500',
    requirements: 'Obtén 100% en 10 evaluaciones',
    progress: 100
  },
  {
    id: 4,
    name: 'Explorador',
    description: 'Descubriste todas las funciones de la plataforma',
    icon: Target,
    category: 'Exploración',
    rarity: 'común',
    points: 200,
    obtained: false,
    dateObtained: null,
    color: 'from-purple-500 to-purple-600',
    requirements: 'Explora todas las secciones de Acadify',
    progress: 75
  },
  {
    id: 5,
    name: 'Rayo de Aprendizaje',
    description: 'Completaste 3 cursos en una semana',
    icon: Zap,
    category: 'Velocidad',
    rarity: 'raro',
    points: 400,
    obtained: false,
    dateObtained: null,
    color: 'from-yellow-400 to-yellow-600',
    requirements: 'Completa 3 cursos en 7 días',
    progress: 33
  },
  {
    id: 6,
    name: 'Corazón de Oro',
    description: 'Recibiste 50 "me gusta" en tus contribuciones',
    icon: Heart,
    category: 'Social',
    rarity: 'épico',
    points: 750,
    obtained: false,
    dateObtained: null,
    color: 'from-pink-500 to-red-500',
    requirements: 'Recibe 50 likes en tus publicaciones',
    progress: 60
  },
  {
    id: 7,
    name: 'Guardián del Saber',
    description: 'Moderaste contenido y mantuviste la calidad',
    icon: Shield,
    category: 'Moderación',
    rarity: 'épico',
    points: 1000,
    obtained: false,
    dateObtained: null,
    color: 'from-indigo-500 to-purple-600',
    requirements: 'Modera contenido por 30 días',
    progress: 0
  },
  {
    id: 8,
    name: 'Corona de Sabiduría',
    description: 'Alcanzaste el nivel máximo en una materia',
  icon: Star,
    category: 'Maestría',
    rarity: 'legendario',
    points: 2000,
    obtained: false,
    dateObtained: null,
    color: 'from-yellow-400 via-yellow-500 to-orange-500',
    requirements: 'Completa todos los cursos de una materia',
    progress: 25
  }
];

const categories = [
  { id: 'all', name: 'Todas', color: 'from-gray-500 to-gray-600' },
  { id: 'Aprendizaje', name: 'Aprendizaje', color: 'from-blue-500 to-blue-600' },
  { id: 'Social', name: 'Social', color: 'from-emerald-500 to-emerald-600' },
  { id: 'Excelencia', name: 'Excelencia', color: 'from-yellow-500 to-orange-500' },
  { id: 'Exploración', name: 'Exploración', color: 'from-purple-500 to-purple-600' },
  { id: 'Velocidad', name: 'Velocidad', color: 'from-yellow-400 to-yellow-600' },
  { id: 'Moderación', name: 'Moderación', color: 'from-indigo-500 to-purple-600' },
  { id: 'Maestría', name: 'Maestría', color: 'from-yellow-400 via-yellow-500 to-orange-500' }
];

const rarityConfig = {
  común: { 
    color: 'from-gray-400 to-gray-500', 
    glow: 'shadow-gray-200', 
    border: 'border-gray-300',
    bg: 'bg-gray-50'
  },
  raro: { 
    color: 'from-blue-400 to-blue-600', 
    glow: 'shadow-blue-200', 
    border: 'border-blue-300',
    bg: 'bg-blue-50'
  },
  épico: { 
    color: 'from-purple-500 to-pink-600', 
    glow: 'shadow-purple-200', 
    border: 'border-purple-300',
    bg: 'bg-purple-50'
  },
  legendario: { 
    color: 'from-yellow-400 via-orange-500 to-red-500', 
    glow: 'shadow-yellow-200', 
    border: 'border-yellow-400',
    bg: 'bg-gradient-to-br from-yellow-50 to-orange-50'
  }
};

export default function InsigniasPage() {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedInsignia, setSelectedInsignia] = useState<any>(null);

  const filteredInsignias = insigniasData.filter(insignia => {
    const matchesCategory = selectedCategory === 'all' || insignia.category === selectedCategory;
    const matchesSearch = insignia.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         insignia.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const totalInsignias = insigniasData.length;
  const obtainedInsignias = insigniasData.filter(i => i.obtained).length;
  const totalPoints = insigniasData.filter(i => i.obtained).reduce((sum, i) => sum + i.points, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 dark:from-gray-900 dark:via-purple-900/20 dark:to-indigo-900/20">
      
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-40"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate(-1)}
                className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </motion.button>
              
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center">
                  <Award className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    Mis Insignias
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {obtainedInsignias} de {totalInsignias} desbloqueadas
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-500 to-orange-600">
                  {totalPoints}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Puntos totales
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Stats Cards */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center">
                <Unlock className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {obtainedInsignias}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Insignias Obtenidas
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Math.round((obtainedInsignias / totalInsignias) * 100)}%
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Progreso Total
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {totalPoints}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Puntos de Insignias
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 mb-8"
        >
          <div className="flex flex-col md:flex-row gap-4">
            
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Buscar insignias..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            {/* Category Filter */}
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <motion.button
                  key={category.id}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    selectedCategory === category.id
                      ? `bg-gradient-to-r ${category.color} text-white shadow-lg`
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {category.name}
                </motion.button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Insignias Grid */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
        >
          {filteredInsignias.map((insignia, index) => {
            const Icon = insignia.icon;
            const rarity = rarityConfig[insignia.rarity as keyof typeof rarityConfig];
            
            return (
              <motion.div
                key={insignia.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                onClick={() => setSelectedInsignia(insignia)}
                className={`relative cursor-pointer group ${
                  insignia.obtained 
                    ? `bg-white dark:bg-gray-800 ${rarity.border} border-2` 
                    : 'bg-gray-100 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600'
                } rounded-2xl p-6 hover:shadow-xl transition-all duration-300 overflow-hidden`}
              >
                
                {/* Background Effect for Legendary */}
                {insignia.rarity === 'legendario' && insignia.obtained && (
                  <motion.div
                    className="absolute inset-0 opacity-20"
                    animate={{
                      background: [
                        'radial-gradient(circle at 20% 50%, rgba(255, 215, 0, 0.3) 0%, transparent 50%)',
                        'radial-gradient(circle at 80% 50%, rgba(255, 140, 0, 0.3) 0%, transparent 50%)',
                        'radial-gradient(circle at 20% 50%, rgba(255, 215, 0, 0.3) 0%, transparent 50%)',
                      ]
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                  />
                )}

                {/* Lock/Unlock Status */}
                <div className="absolute top-4 right-4">
                  {insignia.obtained ? (
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                      <Unlock className="w-3 h-3 text-white" />
                    </div>
                  ) : (
                    <div className="w-6 h-6 bg-gray-400 rounded-full flex items-center justify-center">
                      <Lock className="w-3 h-3 text-white" />
                    </div>
                  )}
                </div>

                {/* Rarity Badge */}
                <div className={`absolute top-4 left-4 px-2 py-1 bg-gradient-to-r ${rarity.color} text-white text-xs font-bold rounded-full capitalize`}>
                  {insignia.rarity}
                </div>

                {/* Icon */}
                <div className="flex justify-center mb-4">
                  <motion.div
                    className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${insignia.color} flex items-center justify-center shadow-lg ${
                      !insignia.obtained ? 'grayscale opacity-50' : ''
                    } ${rarity.glow}`}
                    whileHover={{ rotate: 10, scale: 1.1 }}
                  >
                    <Icon className="w-10 h-10 text-white" />
                    
                    {/* Sparkle Effect for Obtained Insignias */}
                    {insignia.obtained && (
                      <motion.div
                        className="absolute inset-0 rounded-2xl"
                        animate={{
                          background: [
                            'radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.3) 0%, transparent 50%)',
                            'radial-gradient(circle at 70% 70%, rgba(255, 255, 255, 0.3) 0%, transparent 50%)',
                            'radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.3) 0%, transparent 50%)',
                          ]
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                      />
                    )}
                  </motion.div>
                </div>

                {/* Content */}
                <div className="text-center">
                  <h3 className={`text-lg font-bold mb-2 ${
                    insignia.obtained 
                      ? 'text-gray-900 dark:text-white' 
                      : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {insignia.name}
                  </h3>
                  
                  <p className={`text-sm mb-3 ${
                    insignia.obtained 
                      ? 'text-gray-600 dark:text-gray-300' 
                      : 'text-gray-400 dark:text-gray-500'
                  }`}>
                    {insignia.description}
                  </p>

                  {/* Points */}
                  <div className={`flex items-center justify-center space-x-2 mb-3 ${
                    insignia.obtained ? 'text-yellow-600' : 'text-gray-400'
                  }`}>
                    <Sparkles className="w-4 h-4" />
                    <span className="font-semibold">{insignia.points} puntos</span>
                  </div>

                  {/* Progress Bar for Unobtained */}
                  {!insignia.obtained && insignia.progress > 0 && (
                    <div className="mb-3">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-xs text-gray-500">Progreso</span>
                        <span className="text-xs text-gray-500">{insignia.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <motion.div
                          className={`h-2 bg-gradient-to-r ${insignia.color} rounded-full`}
                          initial={{ width: 0 }}
                          animate={{ width: `${insignia.progress}%` }}
                          transition={{ duration: 1, delay: index * 0.1 }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Date Obtained */}
                  {insignia.obtained && insignia.dateObtained && (
                    <div className="flex items-center justify-center space-x-1 text-xs text-gray-500">
                      <Calendar className="w-3 h-3" />
                      <span>Obtenida: {new Date(insignia.dateObtained).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </motion.div>

        {/* No Results */}
        {filteredInsignias.length === 0 && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">
              No se encontraron insignias
            </h3>
            <p className="text-gray-500 dark:text-gray-500">
              Intenta con otros términos de búsqueda o categorías
            </p>
          </motion.div>
        )}
      </div>

      {/* Modal de Detalle */}
      <AnimatePresence>
        {selectedInsignia && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedInsignia(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white dark:bg-gray-800 rounded-3xl p-8 max-w-md w-full shadow-2xl"
            >
              <div className="text-center">
                <div className="flex justify-center mb-6">
                  <motion.div
                    className={`w-24 h-24 rounded-3xl bg-gradient-to-br ${selectedInsignia.color} flex items-center justify-center shadow-2xl ${
                      !selectedInsignia.obtained ? 'grayscale opacity-50' : ''
                    }`}
                    animate={{ rotate: [0, 10, -10, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <selectedInsignia.icon className="w-12 h-12 text-white" />
                  </motion.div>
                </div>

                <div className={`px-3 py-1 bg-gradient-to-r ${rarityConfig[selectedInsignia.rarity as keyof typeof rarityConfig].color} text-white text-sm font-bold rounded-full inline-block mb-4 capitalize`}>
                  {selectedInsignia.rarity}
                </div>

                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                  {selectedInsignia.name}
                </h2>
                
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                  {selectedInsignia.description}
                </p>

                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-xl">
                    <span className="text-gray-600 dark:text-gray-300">Puntos</span>
                    <div className="flex items-center space-x-1 text-yellow-600">
                      <Sparkles className="w-4 h-4" />
                      <span className="font-bold">{selectedInsignia.points}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-xl">
                    <span className="text-gray-600 dark:text-gray-300">Categoría</span>
                    <span className="font-semibold text-gray-900 dark:text-white">
                      {selectedInsignia.category}
                    </span>
                  </div>

                  <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-xl">
                    <span className="text-gray-600 dark:text-gray-300 block mb-2">Requisitos</span>
                    <span className="text-gray-900 dark:text-white font-medium">
                      {selectedInsignia.requirements}
                    </span>
                  </div>

                  {!selectedInsignia.obtained && (
                    <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-blue-700 dark:text-blue-300 font-medium">Progreso</span>
                        <span className="text-blue-700 dark:text-blue-300 font-bold">{selectedInsignia.progress}%</span>
                      </div>
                      <div className="w-full bg-blue-200 dark:bg-blue-800 rounded-full h-3">
                        <motion.div
                          className="h-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${selectedInsignia.progress}%` }}
                          transition={{ duration: 1 }}
                        />
                      </div>
                    </div>
                  )}

                  {selectedInsignia.obtained && selectedInsignia.dateObtained && (
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-xl">
                      <div className="flex items-center justify-center space-x-2 text-green-700 dark:text-green-300">
                        <Calendar className="w-4 h-4" />
                        <span className="font-medium">
                          Desbloqueada el {new Date(selectedInsignia.dateObtained).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setSelectedInsignia(null)}
                  className="mt-6 w-full bg-gradient-to-r from-purple-500 to-pink-600 text-white font-semibold py-3 rounded-xl hover:shadow-lg transition-all duration-300"
                >
                  Cerrar
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
