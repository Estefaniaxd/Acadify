import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiBook, FiUsers, FiCalendar, FiPlus, FiEdit3, FiTrash2, FiEye, FiClock } from 'react-icons/fi';

interface Clase {
  id: string;
  nombre: string;
  profesor: string;
  materia: string;
  estudiantes: number;
  horario: string;
  aula: string;
  estado: 'activa' | 'inactiva' | 'programada';
  fechaInicio: string;
}

// Datos mock para desarrollo
const clasesMock: Clase[] = [
  {
    id: '1',
    nombre: 'Matemáticas Avanzadas 2025',
    profesor: 'Ana García',
    materia: 'Matemáticas',
    estudiantes: 28,
    horario: 'Lun, Mié, Vie 08:00-09:30',
    aula: 'A-101',
    estado: 'activa',
    fechaInicio: '2025-01-15'
  },
  {
    id: '2',
    nombre: 'Historia Universal',
    profesor: 'Luis Rodríguez',
    materia: 'Historia',
    estudiantes: 25,
    horario: 'Mar, Jue 10:00-11:30',
    aula: 'B-203',
    estado: 'activa',
    fechaInicio: '2025-01-16'
  },
  {
    id: '3',
    nombre: 'Biología Molecular',
    profesor: 'María López',
    materia: 'Ciencias',
    estudiantes: 0,
    horario: 'Lun, Mié 14:00-15:30',
    aula: 'C-301',
    estado: 'programada',
    fechaInicio: '2025-02-01'
  }
];

export default function ClasesCoordinador() {
  const [clases, setClases] = useState<Clase[]>(clasesMock);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newClase, setNewClase] = useState({
    nombre: '',
    profesor: '',
    materia: '',
    horario: '',
    aula: '',
    fechaInicio: ''
  });

  const handleAddClase = () => {
    if (newClase.nombre && newClase.profesor && newClase.materia) {
      const clase: Clase = {
        id: Date.now().toString(),
        ...newClase,
        estudiantes: 0,
        estado: 'programada'
      };
      setClases([...clases, clase]);
      setNewClase({ nombre: '', profesor: '', materia: '', horario: '', aula: '', fechaInicio: '' });
      setShowAddForm(false);
    }
  };

  const handleDeleteClase = (id: string) => {
    setClases(clases.filter(c => c.id !== id));
  };

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'activa':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'inactiva':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      case 'programada':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Gestión de Clases
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Administra las clases de tu institución
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <FiPlus className="w-4 h-4" />
          <span>Nueva Clase</span>
        </button>
      </div>

      {/* Add Class Form */}
      {showAddForm && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Crear Nueva Clase
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Nombre de la clase"
              value={newClase.nombre}
              onChange={(e) => setNewClase({ ...newClase, nombre: e.target.value })}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <input
              type="text"
              placeholder="Profesor asignado"
              value={newClase.profesor}
              onChange={(e) => setNewClase({ ...newClase, profesor: e.target.value })}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <input
              type="text"
              placeholder="Materia"
              value={newClase.materia}
              onChange={(e) => setNewClase({ ...newClase, materia: e.target.value })}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <input
              type="text"
              placeholder="Aula (ej: A-101)"
              value={newClase.aula}
              onChange={(e) => setNewClase({ ...newClase, aula: e.target.value })}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <input
              type="text"
              placeholder="Horario (ej: Lun, Mié 08:00-09:30)"
              value={newClase.horario}
              onChange={(e) => setNewClase({ ...newClase, horario: e.target.value })}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <input
              type="date"
              placeholder="Fecha de inicio"
              value={newClase.fechaInicio}
              onChange={(e) => setNewClase({ ...newClase, fechaInicio: e.target.value })}
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
              onClick={handleAddClase}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Crear Clase
            </button>
          </div>
        </motion.div>
      )}

      {/* Classes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {clases.map((clase) => (
          <motion.div
            key={clase.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-700 dark:to-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <FiBook className="w-4 h-4 text-white" />
                </div>
                <span
                  className={`px-2 py-1 text-xs font-medium rounded-full ${getEstadoColor(clase.estado)}`}
                >
                  {clase.estado}
                </span>
              </div>
              <div className="flex space-x-1">
                <button className="p-1 text-gray-500 hover:text-blue-600">
                  <FiEye className="w-4 h-4" />
                </button>
                <button className="p-1 text-gray-500 hover:text-blue-600">
                  <FiEdit3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDeleteClase(clase.id)}
                  className="p-1 text-gray-500 hover:text-red-600"
                >
                  <FiTrash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {clase.nombre}
            </h3>
            
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-center space-x-2">
                <FiUsers className="w-4 h-4" />
                <span>Profesor: {clase.profesor}</span>
              </div>
              <div className="flex items-center space-x-2">
                <FiBook className="w-4 h-4" />
                <span>Materia: {clase.materia}</span>
              </div>
              <div className="flex items-center space-x-2">
                <FiUsers className="w-4 h-4" />
                <span>{clase.estudiantes} estudiantes</span>
              </div>
              {clase.aula && (
                <div className="flex items-center space-x-2">
                  <FiCalendar className="w-4 h-4" />
                  <span>Aula: {clase.aula}</span>
                </div>
              )}
              {clase.horario && (
                <div className="flex items-center space-x-2">
                  <FiClock className="w-4 h-4" />
                  <span>{clase.horario}</span>
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">
                  Inicio: {new Date(clase.fechaInicio).toLocaleDateString()}
                </span>
                <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">
                  Ver detalles
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {clases.length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Clases</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {clases.filter(c => c.estado === 'activa').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Activas</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
              {clases.filter(c => c.estado === 'programada').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Programadas</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {clases.reduce((total, clase) => total + clase.estudiantes, 0)}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Estudiantes</div>
          </div>
        </div>
      </div>
    </div>
  );
}
