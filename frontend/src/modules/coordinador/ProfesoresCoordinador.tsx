import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Edit3, Mail, Phone, Plus, Search, Trash2, User } from 'lucide-react';
;

interface Profesor {
  id: string;
  nombre: string;
  email: string;
  telefono: string;
  materia: string;
  estado: 'activo' | 'inactivo';
}

// Datos mock para desarrollo
const profesoresMock: Profesor[] = [
  {
    id: '1',
    nombre: 'Ana García',
    email: 'ana.garcia@institucion.edu',
    telefono: '+1 234 567 8901',
    materia: 'Matemáticas',
    estado: 'activo'
  },
  {
    id: '2',
    nombre: 'Luis Rodríguez',
    email: 'luis.rodriguez@institucion.edu',
    telefono: '+1 234 567 8902',
    materia: 'Historia',
    estado: 'activo'
  },
  {
    id: '3',
    nombre: 'María López',
    email: 'maria.lopez@institucion.edu',
    telefono: '+1 234 567 8903',
    materia: 'Ciencias',
    estado: 'inactivo'
  }
];

export default function ProfesoresCoordinador() {
  const [profesores, setProfesores] = useState<Profesor[]>(profesoresMock);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newProfesor, setNewProfesor] = useState({
    nombre: '',
    email: '',
    telefono: '',
    materia: ''
  });

  const filteredProfesores = profesores.filter(profesor =>
    profesor.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    profesor.materia.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddProfesor = () => {
    if (newProfesor.nombre && newProfesor.email && newProfesor.materia) {
      const profesor: Profesor = {
        id: Date.now().toString(),
        ...newProfesor,
        estado: 'activo'
      };
      setProfesores([...profesores, profesor]);
      setNewProfesor({ nombre: '', email: '', telefono: '', materia: '' });
      setShowAddForm(false);
    }
  };

  const handleDeleteProfesor = (id: string) => {
    setProfesores(profesores.filter(p => p.id !== id));
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Gestión de Profesores
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Administra los profesores de tu institución
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Agregar Profesor</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Buscar por nombre o materia..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      {/* Add Professor Form */}
      {showAddForm && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Agregar Nuevo Profesor
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Nombre completo"
              value={newProfesor.nombre}
              onChange={(e) => setNewProfesor({ ...newProfesor, nombre: e.target.value })}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <input
              type="email"
              placeholder="Correo electrónico"
              value={newProfesor.email}
              onChange={(e) => setNewProfesor({ ...newProfesor, email: e.target.value })}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <input
              type="tel"
              placeholder="Teléfono"
              value={newProfesor.telefono}
              onChange={(e) => setNewProfesor({ ...newProfesor, telefono: e.target.value })}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <input
              type="text"
              placeholder="Materia"
              value={newProfesor.materia}
              onChange={(e) => setNewProfesor({ ...newProfesor, materia: e.target.value })}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          <div className="flex justify-end space-x-2 mt-4">
            <button
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
            >
              Cancelar
            </button>
            <button
              onClick={handleAddProfesor}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Agregar
            </button>
          </div>
        </motion.div>
      )}

      {/* Professors List */}
      <div className="space-y-4">
        {filteredProfesores.length === 0 ? (
          <div className="text-center py-8">
            <User className="w-12 h-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-500 dark:text-gray-400">
              {searchTerm ? 'No se encontraron profesores' : 'No hay profesores registrados'}
            </p>
          </div>
        ) : (
          filteredProfesores.map((profesor) => (
            <motion.div
              key={profesor.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                    <User className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {profesor.nombre}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">{profesor.materia}</p>
                    <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <Mail className="w-4 h-4" />
                        <span>{profesor.email}</span>
                      </div>
                      {profesor.telefono && (
                        <div className="flex items-center space-x-1">
                          <Phone className="w-4 h-4" />
                          <span>{profesor.telefono}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${
                      profesor.estado === 'activo'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                        : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                    }`}
                  >
                    {profesor.estado}
                  </span>
                  <button className="p-2 text-gray-500 hover:text-blue-600 dark:hover:text-blue-400">
                    <Edit3 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteProfesor(profesor.id)}
                    className="p-2 text-gray-500 hover:text-red-600 dark:hover:text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Summary */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {profesores.length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Profesores</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {profesores.filter(p => p.estado === 'activo').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Activos</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {new Set(profesores.map(p => p.materia)).size}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Materias</div>
          </div>
        </div>
      </div>
    </div>
  );
}
