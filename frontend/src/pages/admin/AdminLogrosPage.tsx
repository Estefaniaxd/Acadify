import { motion } from 'framer-motion';
import { useState } from 'react';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Award, 
  Trophy,
  Star,
  Search,
  Filter,
  Target,
  Zap
} from 'lucide-react';

interface Logro {
  id: string;
  nombre: string;
  descripcion: string;
  icono: string;
  categoria: 'academico' | 'social' | 'gamificacion' | 'especial';
  puntos: number;
  rareza: 'bronce' | 'plata' | 'oro' | 'platino';
  requisitos: string;
  activo: boolean;
}

export default function AdminLogrosPage() {
  const [logros, setLogros] = useState<Logro[]>([
    {
      id: '1',
      nombre: 'Primera Victoria',
      descripcion: 'Completa tu primera tarea',
      icono: '🏆',
      categoria: 'academico',
      puntos: 50,
      rareza: 'bronce',
      requisitos: 'Completar 1 tarea',
      activo: true
    },
    {
      id: '2',
      nombre: 'Estudiante Estrella',
      descripcion: 'Obtén 10 calificaciones perfectas',
      icono: '⭐',
      categoria: 'academico',
      puntos: 500,
      rareza: 'oro',
      requisitos: 'Obtener 10 calificaciones de 100%',
      activo: true
    },
    {
      id: '3',
      nombre: 'Social Butterfly',
      descripcion: 'Comenta en 50 publicaciones diferentes',
      icono: '🦋',
      categoria: 'social',
      puntos: 200,
      rareza: 'plata',
      requisitos: 'Comentar en 50 publicaciones',
      activo: true
    }
  ]);

  const [showModal, setShowModal] = useState(false);
  const [editingLogro, setEditingLogro] = useState<Logro | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategoria, setFilterCategoria] = useState<string>('todas');

  const categorias = [
    { value: 'todas', label: 'Todas las categorías' },
    { value: 'academico', label: '📚 Académico' },
    { value: 'social', label: '👥 Social' },
    { value: 'gamificacion', label: '🎮 Gamificación' },
    { value: 'especial', label: '✨ Especial' }
  ];

  const rarezas = [
    { value: 'bronce', label: 'Bronce', color: 'from-amber-700 to-amber-900', textColor: 'text-amber-700 dark:text-amber-400' },
    { value: 'plata', label: 'Plata', color: 'from-gray-400 to-gray-600', textColor: 'text-gray-600 dark:text-gray-400' },
    { value: 'oro', label: 'Oro', color: 'from-yellow-400 to-yellow-600', textColor: 'text-yellow-600 dark:text-yellow-400' },
    { value: 'platino', label: 'Platino', color: 'from-cyan-400 to-blue-600', textColor: 'text-cyan-600 dark:text-cyan-400' }
  ];

  const handleCreateLogro = () => {
    setEditingLogro(null);
    setShowModal(true);
  };

  const handleEditLogro = (logro: Logro) => {
    setEditingLogro(logro);
    setShowModal(true);
  };

  const handleDeleteLogro = (id: string) => {
    if (confirm('¿Estás seguro de eliminar este logro?')) {
      setLogros(logros.filter(l => l.id !== id));
    }
  };

  const filteredLogros = logros.filter(l => {
    const matchesSearch = l.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          l.descripcion.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategoria = filterCategoria === 'todas' || l.categoria === filterCategoria;
    return matchesSearch && matchesCategoria;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-r from-amber-500 to-orange-600 rounded-xl flex items-center justify-center">
                  <Award className="w-7 h-7 text-white" />
                </div>
                Gestión de Logros
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Administra insignias, medallas y logros del sistema de gamificación
              </p>
            </div>
            <button
              onClick={handleCreateLogro}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-600 to-orange-600 text-white rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-200"
            >
              <Plus className="w-5 h-5" />
              Nuevo Logro
            </button>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-2xl p-6 mb-6 shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar logros..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-amber-500 focus:border-transparent text-gray-900 dark:text-white"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={filterCategoria}
                onChange={(e) => setFilterCategoria(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-amber-500 focus:border-transparent text-gray-900 dark:text-white appearance-none"
              >
                {categorias.map(cat => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </select>
            </div>
          </div>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          {[
            { label: 'Total Logros', value: logros.length.toString(), icon: Trophy, color: 'from-blue-500 to-cyan-600' },
            { label: 'Logros Activos', value: logros.filter(l => l.activo).length.toString(), icon: Zap, color: 'from-green-500 to-emerald-600' },
            { label: 'Categorías', value: '4', icon: Target, color: 'from-purple-500 to-pink-600' },
            { label: 'Puntos Totales', value: logros.reduce((sum, l) => sum + l.puntos, 0).toString(), icon: Star, color: 'from-amber-500 to-orange-600' }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{stat.value}</p>
                </div>
                <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-xl flex items-center justify-center`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Logros Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {filteredLogros.map((logro, index) => (
            <motion.div
              key={logro.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white dark:bg-gray-800 rounded-2xl overflow-hidden shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300"
            >
              {/* Logro Header */}
              <div className={`h-32 bg-gradient-to-br ${rarezas.find(r => r.value === logro.rareza)?.color} flex items-center justify-center relative`}>
                <div className="text-6xl">{logro.icono}</div>
                {!logro.activo && (
                  <div className="absolute top-3 right-3 px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full">
                    Inactivo
                  </div>
                )}
              </div>

              {/* Logro Info */}
              <div className="p-6">
                <div className="mb-3">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                    {logro.nombre}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    {logro.descripcion}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500">
                    <strong>Requisito:</strong> {logro.requisitos}
                  </p>
                </div>

                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-medium text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-900/30 px-3 py-1 rounded-full">
                    {categorias.find(c => c.value === logro.categoria)?.label}
                  </span>
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 text-amber-500" />
                    <span className="text-lg font-bold text-amber-600 dark:text-amber-400">
                      {logro.puntos}
                    </span>
                  </div>
                </div>

                <div className="mb-4">
                  <span className={`text-xs font-bold uppercase ${rarezas.find(r => r.value === logro.rareza)?.textColor}`}>
                    ⬥ {rarezas.find(r => r.value === logro.rareza)?.label}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEditLogro(logro)}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-xl hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                    Editar
                  </button>
                  <button
                    onClick={() => handleDeleteLogro(logro.id)}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Eliminar
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Empty State */}
        {filteredLogros.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white dark:bg-gray-800 rounded-2xl p-12 text-center shadow-lg border border-gray-200 dark:border-gray-700"
          >
            <Award className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No se encontraron logros
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {searchTerm || filterCategoria !== 'todas' 
                ? 'Intenta ajustar los filtros de búsqueda'
                : 'Comienza agregando el primer logro al sistema'
              }
            </p>
            {(!searchTerm && filterCategoria === 'todas') && (
              <button
                onClick={handleCreateLogro}
                className="px-6 py-3 bg-gradient-to-r from-amber-600 to-orange-600 text-white rounded-xl hover:shadow-lg transition-all duration-200"
              >
                Crear Primer Logro
              </button>
            )}
          </motion.div>
        )}

        {/* Modal placeholder */}
        {showModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                {editingLogro ? 'Editar Logro' : 'Nuevo Logro'}
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Funcionalidad de formulario será implementada próximamente
              </p>
              <button
                onClick={() => setShowModal(false)}
                className="w-full px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Cerrar
              </button>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
}
