import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
;

// Importar componentes del módulo
import { BancoPreguntas } from './components/banco/BancoPreguntas';
import { CreadorPregunta } from './components/banco/CreadorPregunta';
import { FormularioExamen } from './components/creador/FormularioExamen';
import { TomadorExamen } from './components/tomador/TomadorExamen';
import { BarChart, Edit3, FileText, Filter, Play, Plus, Search } from 'lucide-react';

interface Evaluacion {
  id: string;
  titulo: string;
  tipo: 'examen' | 'quiz' | 'tarea';
  estado: 'draft' | 'published' | 'completed';
  fechaCreacion: string;
  fechaVencimiento?: string;
  numeroPreguntas: number;
  duracion?: number; // en minutos
  intentos: number;
}

const evaluacionesMock: Evaluacion[] = [
  {
    id: '1',
    titulo: 'Examen de Matemáticas - Unidad 1',
    tipo: 'examen',
    estado: 'published',
    fechaCreacion: '2024-01-10',
    fechaVencimiento: '2024-01-20',
    numeroPreguntas: 20,
    duracion: 90,
    intentos: 0
  },
  {
    id: '2',
    titulo: 'Quiz Química Orgánica',
    tipo: 'quiz',
    estado: 'draft',
    fechaCreacion: '2024-01-12',
    numeroPreguntas: 10,
    duracion: 30,
    intentos: 2
  },
  {
    id: '3',
    titulo: 'Tarea Historia Universal',
    tipo: 'tarea',
    estado: 'completed',
    fechaCreacion: '2024-01-05',
    fechaVencimiento: '2024-01-15',
    numeroPreguntas: 5,
    intentos: 1
  }
];

export default function ModuloEvaluaciones() {
  const [activeTab, setActiveTab] = useState<'lista' | 'banco' | 'crear' | 'tomador'>('lista');
  const [evaluaciones, setEvaluaciones] = useState<Evaluacion[]>(evaluacionesMock);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTipo, setFilterTipo] = useState<'all' | 'examen' | 'quiz' | 'tarea'>('all');

  const evaluacionesFiltradas = evaluaciones.filter(evaluacion => {
    const matchSearch = evaluacion.titulo.toLowerCase().includes(searchTerm.toLowerCase());
    const matchFilter = filterTipo === 'all' || evaluacion.tipo === filterTipo;
    return matchSearch && matchFilter;
  });

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'draft': return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-800 dark:text-yellow-300';
      case 'published': return 'bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-300';
      case 'completed': return 'bg-green-100 text-green-700 dark:bg-green-800 dark:text-green-300';
      default: return 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case 'examen': return FileText;
      case 'quiz': return Play;
      case 'tarea': return Edit3;
      default: return FileText;
    }
  };

  return (
    <div className="bg-gradient-to-br from-indigo-50 via-white to-purple-100 dark:from-gray-900 dark:via-gray-800 dark:to-indigo-900 p-6">
      <div className="max-w-7xl mx-auto mt-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Módulo de Evaluaciones
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestiona examenes, quizzes y tareas de manera integral
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap bg-white dark:bg-gray-800 rounded-xl p-2 mb-6 border border-gray-200 dark:border-gray-700">
          {[
            { key: 'lista', label: 'Evaluaciones', icon: FileText },
            { key: 'banco', label: 'Banco de Preguntas', icon: Edit3 },
            { key: 'crear', label: 'Crear Evaluación', icon: Plus },
            { key: 'tomador', label: 'Tomar Evaluación', icon: Play }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`
                flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                ${activeTab === tab.key
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'
                }
              `}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'lista' && (
            <motion.div
              key="lista"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              {/* Filters */}
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Buscar evaluaciones..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                  </div>
                  
                  <div className="relative">
                    <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <select
                      value={filterTipo}
                      onChange={(e) => setFilterTipo(e.target.value as any)}
                      className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    >
                      <option value="all">Todos los tipos</option>
                      <option value="examen">Exámenes</option>
                      <option value="quiz">Quizzes</option>
                      <option value="tarea">Tareas</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Evaluaciones List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {evaluacionesFiltradas.map((evaluacion, index) => {
                  const TipoIcon = getTipoIcon(evaluacion.tipo);
                  return (
                    <motion.div
                      key={evaluacion.id}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.1, duration: 0.3 }}
                      className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all duration-300"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                            <TipoIcon className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white text-sm line-clamp-1">
                              {evaluacion.titulo}
                            </h3>
                            <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getEstadoColor(evaluacion.estado)}`}>
                              {evaluacion.estado === 'draft' ? 'Borrador' :
                               evaluacion.estado === 'published' ? 'Publicada' : 'Completada'}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                        <div className="flex justify-between">
                          <span>Preguntas:</span>
                          <span className="font-medium">{evaluacion.numeroPreguntas}</span>
                        </div>
                        {evaluacion.duracion && (
                          <div className="flex justify-between">
                            <span>Duración:</span>
                            <span className="font-medium">{evaluacion.duracion} min</span>
                          </div>
                        )}
                        <div className="flex justify-between">
                          <span>Intentos:</span>
                          <span className="font-medium">{evaluacion.intentos}</span>
                        </div>
                        {evaluacion.fechaVencimiento && (
                          <div className="flex justify-between">
                            <span>Vencimiento:</span>
                            <span className="font-medium">{evaluacion.fechaVencimiento}</span>
                          </div>
                        )}
                      </div>

                      <div className="mt-4 flex gap-2">
                        <button className="flex-1 px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm">
                          {evaluacion.estado === 'draft' ? 'Editar' : 'Ver'}
                        </button>
                        <button className="px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                          <BarChart className="w-4 h-4" />
                        </button>
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              {evaluacionesFiltradas.length === 0 && (
                <div className="text-center py-12">
                  <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400">No se encontraron evaluaciones</p>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'banco' && (
            <motion.div
              key="banco"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <BancoPreguntas />
            </motion.div>
          )}

          {activeTab === 'crear' && (
            <motion.div
              key="crear"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <FormularioExamen 
                onGuardar={async (datos) => {
                  console.log('Guardando evaluación:', datos);
                  // TODO: Implementar guardado
                }}
                onCancelar={() => {
                  console.log('Cancelando creación de evaluación');
                }}
              />
            </motion.div>
          )}

          {activeTab === 'tomador' && (
            <motion.div
              key="tomador"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700 text-center">
                <Play className="w-16 h-16 text-indigo-500 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Seleccionar Evaluación
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Elige una evaluación disponible para comenzar
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {evaluacionesFiltradas.filter(e => e.estado === 'published').map((evaluacion) => (
                    <button
                      key={evaluacion.id}
                      className="p-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all duration-300 text-left"
                    >
                      <h4 className="font-semibold mb-2">{evaluacion.titulo}</h4>
                      <div className="text-indigo-100 text-sm">
                        {evaluacion.numeroPreguntas} preguntas • {evaluacion.duracion} min
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}