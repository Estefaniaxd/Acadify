import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useToast } from '../context/ToastContext'
import { 
  FiSearch, 
  FiBook, 
  FiHelpCircle, 
  FiMessageSquare, 
  FiMail,
  FiPhone,
  FiChevronDown,
  FiChevronRight,
  FiExternalLink,
  FiStar,
  FiThumbsUp,
  FiThumbsDown,
  FiVideo,
  FiDownload,
  FiUser,
  FiSettings,
  FiShield,
  FiCreditCard,
  FiSmartphone,
  FiMonitor,
  FiWifi,
  FiAlertCircle,
  FiCheckCircle,
  FiClock,
  FiTrendingUp,
  FiBookOpen,
  FiUsers,
  FiAward
} from 'react-icons/fi'

interface FAQ {
  id: string
  category: string
  question: string
  answer: string
  helpful: number
  views: number
  tags: string[]
  relatedArticles?: string[]
}

interface Category {
  id: string
  name: string
  icon: any
  color: string
  description: string
  articleCount: number
}

const categories: Category[] = [
  {
    id: 'getting-started',
    name: 'Primeros pasos',
    icon: FiAward,
    color: 'text-blue-500',
    description: 'Todo lo que necesitas saber para empezar',
    articleCount: 12
  },
  {
    id: 'account',
    name: 'Cuenta y perfil',
    icon: FiUser,
    color: 'text-green-500',
    description: 'Gestión de tu cuenta y configuración',
    articleCount: 8
  },
  {
    id: 'courses',
    name: 'Cursos y clases',
    icon: FiBookOpen,
    color: 'text-purple-500',
    description: 'Cómo navegar y usar los cursos',
    articleCount: 15
  },
  {
    id: 'technical',
    name: 'Problemas técnicos',
    icon: FiSettings,
    color: 'text-orange-500',
    description: 'Soluciones a problemas comunes',
    articleCount: 10
  },
  {
    id: 'payments',
    name: 'Pagos y suscripciones',
    icon: FiCreditCard,
    color: 'text-red-500',
    description: 'Información sobre pagos y facturación',
    articleCount: 6
  },
  {
    id: 'community',
    name: 'Comunidad',
    icon: FiUsers,
    color: 'text-indigo-500',
    description: 'Interacción social y comunidades',
    articleCount: 9
  }
]

const mockFAQs: FAQ[] = [
  {
    id: '1',
    category: 'getting-started',
    question: '¿Cómo me registro en Acadify?',
    answer: 'Para registrarte en Acadify, haz clic en "Crear cuenta" en la página principal. Puedes registrarte usando tu email o con tus cuentas de Google/Facebook. Solo necesitas proporcionar tu nombre, email y crear una contraseña segura.',
    helpful: 42,
    views: 156,
    tags: ['registro', 'cuenta', 'primeros pasos'],
    relatedArticles: ['2', '3']
  },
  {
    id: '2',
    category: 'getting-started',
    question: '¿Cómo navego por la plataforma?',
    answer: 'La navegación en Acadify es intuitiva. Usa el menú lateral para acceder a tus cursos, dashboard, mensajes y configuración. La barra superior te permite buscar cursos y acceder a tu perfil.',
    helpful: 38,
    views: 124,
    tags: ['navegación', 'interfaz', 'menú'],
    relatedArticles: ['1', '4']
  },
  {
    id: '3',
    category: 'account',
    question: '¿Cómo cambio mi avatar?',
    answer: 'Ve a tu perfil haciendo clic en tu foto de perfil en la esquina superior derecha. Selecciona "Personalizar avatar" para elegir entre cientos de opciones de personalización, incluyendo cara, cabello, ropa y accesorios.',
    helpful: 56,
    views: 89,
    tags: ['avatar', 'perfil', 'personalización'],
    relatedArticles: ['4', '5']
  },
  {
    id: '4',
    category: 'account',
    question: '¿Cómo cambio mi contraseña?',
    answer: 'Ve a Configuración > Seguridad. Ingresa tu contraseña actual y luego tu nueva contraseña dos veces. Asegúrate de usar una contraseña fuerte con al menos 8 caracteres, incluyendo mayúsculas, minúsculas y números.',
    helpful: 31,
    views: 67,
    tags: ['contraseña', 'seguridad', 'cuenta']
  },
  {
    id: '5',
    category: 'courses',
    question: '¿Cómo me inscribo en un curso?',
    answer: 'Navega al catálogo de cursos, encuentra el curso que te interesa y haz clic en "Inscribirse". Algunos cursos son gratuitos, otros requieren pago o suscripción premium.',
    helpful: 44,
    views: 201,
    tags: ['inscripción', 'cursos', 'catálogo']
  },
  {
    id: '6',
    category: 'technical',
    question: 'No puedo acceder a mis cursos',
    answer: 'Si no puedes acceder a tus cursos, verifica tu conexión a internet. Si el problema persiste, cierra sesión y vuelve a iniciarla. Si sigues teniendo problemas, contacta a soporte.',
    helpful: 29,
    views: 45,
    tags: ['acceso', 'problemas', 'cursos', 'soporte']
  },
  {
    id: '7',
    category: 'payments',
    question: '¿Qué métodos de pago aceptan?',
    answer: 'Aceptamos tarjetas de crédito y débito (Visa, MasterCard, American Express), PayPal, y transferencias bancarias. Todos los pagos están protegidos con cifrado SSL.',
    helpful: 33,
    views: 78,
    tags: ['pagos', 'métodos', 'seguridad']
  },
  {
    id: '8',
    category: 'community',
    question: '¿Cómo me uno a una comunidad?',
    answer: 'Ve a la sección "Comunidades" en el menú principal. Puedes explorar comunidades por tema o usar la búsqueda. Haz clic en "Unirse" para formar parte de la conversación.',
    helpful: 27,
    views: 92,
    tags: ['comunidades', 'social', 'participación']
  }
]

export default function AyudaFaqPageAdvanced() {
  const toast = useToast()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [expandedFAQ, setExpandedFAQ] = useState<string | null>(null)
  const [helpfulVotes, setHelpfulVotes] = useState<{[key: string]: 'up' | 'down' | null}>({})

  const filteredFAQs = mockFAQs.filter(faq => {
    const matchesSearch = searchQuery === '' || 
      faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    
    const matchesCategory = selectedCategory === 'all' || faq.category === selectedCategory
    
    return matchesSearch && matchesCategory
  })

  const handleVote = (faqId: string, vote: 'up' | 'down') => {
    setHelpfulVotes(prev => ({
      ...prev,
      [faqId]: prev[faqId] === vote ? null : vote
    }))
    
    toast.success(
      vote === 'up' ? '¡Gracias!' : 'Gracias por el feedback',
      vote === 'up' ? 'Tu voto nos ayuda a mejorar' : 'Trabajaremos en mejorar esta respuesta'
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/50 dark:from-gray-900 dark:via-gray-900 dark:to-blue-950/30">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-center space-x-3 mb-4"
            >
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center">
                <FiHelpCircle className="w-8 h-8 text-white" />
              </div>
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-3xl font-bold text-gray-900 dark:text-white mb-4"
            >
              Centro de Ayuda
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-lg text-gray-600 dark:text-gray-400 mb-8"
            >
              Encuentra respuestas rápidas a tus preguntas más frecuentes
            </motion.p>

            {/* Search */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="relative max-w-xl mx-auto"
            >
              <FiSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar en el centro de ayuda..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-4 bg-white/50 dark:bg-gray-800/50 border border-gray-300/50 dark:border-gray-600/50 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent backdrop-blur-sm text-lg"
              />
            </motion.div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-6">
              {/* Categories */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Categorías
                </h3>
                
                <div className="space-y-2">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSelectedCategory('all')}
                    className={`w-full flex items-center space-x-3 p-3 rounded-xl transition-colors text-left ${
                      selectedCategory === 'all'
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700/50 text-gray-700 dark:text-gray-300'
                    }`}
                  >
                    <FiBook className="w-5 h-5" />
                    <span className="font-medium">Todas las categorías</span>
                  </motion.button>

                  {categories.map((category) => (
                    <motion.button
                      key={category.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`w-full flex items-center justify-between p-3 rounded-xl transition-colors text-left ${
                        selectedCategory === category.id
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700/50 text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <category.icon className={`w-5 h-5 ${category.color}`} />
                        <span className="font-medium">{category.name}</span>
                      </div>
                      <span className="text-xs bg-gray-200 dark:bg-gray-600 px-2 py-1 rounded-full">
                        {category.articleCount}
                      </span>
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Contact Support */}
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">¿Necesitas más ayuda?</h3>
                <p className="text-blue-100 text-sm mb-4">
                  Nuestro equipo de soporte está aquí para ayudarte.
                </p>
                
                <div className="space-y-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="w-full flex items-center space-x-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-lg p-2 transition-colors"
                  >
                    <FiMessageSquare className="w-4 h-4" />
                    <span className="text-sm font-medium">Chat en vivo</span>
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="w-full flex items-center space-x-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-lg p-2 transition-colors"
                  >
                    <FiMail className="w-4 h-4" />
                    <span className="text-sm font-medium">Enviar email</span>
                  </motion.button>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Results header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {selectedCategory === 'all' ? 'Todas las preguntas' : 
                   categories.find(c => c.id === selectedCategory)?.name}
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {filteredFAQs.length} {filteredFAQs.length === 1 ? 'resultado' : 'resultados'} encontrados
                </p>
              </div>
            </div>

            {/* FAQ List */}
            {filteredFAQs.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-16"
              >
                <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <FiSearch className="w-12 h-12 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  No se encontraron resultados
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  Intenta con diferentes palabras clave o explora las categorías.
                </p>
              </motion.div>
            ) : (
              <div className="space-y-4">
                {filteredFAQs.map((faq, index) => (
                  <motion.div
                    key={faq.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
                  >
                    <motion.button
                      onClick={() => setExpandedFAQ(expandedFAQ === faq.id ? null : faq.id)}
                      className="w-full p-6 text-left flex items-center justify-between hover:bg-gray-50/50 dark:hover:bg-gray-700/30 transition-colors"
                    >
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                          {faq.question}
                        </h3>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                          <span className="flex items-center space-x-1">
                            <FiThumbsUp className="w-3 h-3" />
                            <span>{faq.helpful}</span>
                          </span>
                          <span className="flex items-center space-x-1">
                            <FiStar className="w-3 h-3" />
                            <span>{faq.views} vistas</span>
                          </span>
                        </div>
                      </div>

                      <motion.div
                        animate={{ rotate: expandedFAQ === faq.id ? 90 : 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <FiChevronRight className="w-5 h-5 text-gray-400" />
                      </motion.div>
                    </motion.button>

                    <AnimatePresence>
                      {expandedFAQ === faq.id && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.3 }}
                          className="border-t border-gray-200/50 dark:border-gray-700/50"
                        >
                          <div className="p-6">
                            <p className="text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
                              {faq.answer}
                            </p>

                            {/* Tags */}
                            <div className="flex flex-wrap gap-2 mb-6">
                              {faq.tags.map((tag) => (
                                <span
                                  key={tag}
                                  className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full text-xs"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>

                            {/* Actions */}
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <span className="text-sm text-gray-600 dark:text-gray-400">
                                  ¿Te ayudó esta respuesta?
                                </span>
                                
                                <motion.button
                                  whileHover={{ scale: 1.1 }}
                                  whileTap={{ scale: 0.9 }}
                                  onClick={() => handleVote(faq.id, 'up')}
                                  className={`p-2 rounded-lg transition-colors ${
                                    helpfulVotes[faq.id] === 'up'
                                      ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
                                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 hover:bg-green-50 dark:hover:bg-green-900/20'
                                  }`}
                                >
                                  <FiThumbsUp className="w-4 h-4" />
                                </motion.button>

                                <motion.button
                                  whileHover={{ scale: 1.1 }}
                                  whileTap={{ scale: 0.9 }}
                                  onClick={() => handleVote(faq.id, 'down')}
                                  className={`p-2 rounded-lg transition-colors ${
                                    helpfulVotes[faq.id] === 'down'
                                      ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
                                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20'
                                  }`}
                                >
                                  <FiThumbsDown className="w-4 h-4" />
                                </motion.button>
                              </div>

                              <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="flex items-center space-x-1 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
                              >
                                <FiExternalLink className="w-4 h-4" />
                                <span>Ver artículo completo</span>
                              </motion.button>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}