import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Edit3, Image, Mail, MapPin, Phone, Save, Settings, Upload, Users, X } from 'lucide-react';
;

// Datos mock de la institución
const institucionMock = {
  nombre: 'Instituto Acadify',
  descripcion: 'Una institución educativa de excelencia dedicada a la formación integral de estudiantes.',
  direccion: 'Av. Educación 123, Ciudad Universitaria',
  telefono: '+1 234 567 8900',
  email: 'contacto@acadify.edu',
  website: 'www.acadify.edu',
  fechaFundacion: '2020-01-15',
  logo: '/api/placeholder/200/200',
  estadisticas: {
    profesores: 8,
    estudiantes: 90,
    clasesActivas: 6,
    graduados: 150
  },
  configuracion: {
    horariosClases: '08:00 - 18:00',
    diasActividad: 'Lunes a Viernes',
    periodoAcademico: 'Semestral',
    modalidad: 'Presencial y Virtual'
  }
};

export default function InstitucionCoordinador() {
  const [institucion, setInstitucion] = useState(institucionMock);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(institucionMock);

  const handleEdit = () => {
    setIsEditing(true);
    setEditData(institucion);
  };

  const handleSave = () => {
    setInstitucion(editData);
    setIsEditing(false);
    // Aquí se haría la llamada a la API
    console.log('Guardando cambios de institución:', editData);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditData(institucion);
  };

  const handleInputChange = (field: string, value: string) => {
    setEditData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleConfigChange = (field: string, value: string) => {
    setEditData(prev => ({
      ...prev,
      configuracion: {
        ...prev.configuracion,
        [field]: value
      }
    }));
  };

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-white rounded-xl flex items-center justify-center">
                <img 
                  src={institucion.logo} 
                  alt="Logo" 
                  className="w-12 h-12 rounded-lg object-cover"
                />
              </div>
              <div>
                <h1 className="text-2xl font-bold">{institucion.nombre}</h1>
                <p className="text-blue-100">Información institucional</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {!isEditing ? (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleEdit}
                  className="bg-white bg-opacity-20 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-opacity-30 transition-all"
                >
                  <Edit3 className="w-4 h-4" />
                  <span>Editar</span>
                </motion.button>
              ) : (
                <div className="flex space-x-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleSave}
                    className="bg-green-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-green-600 transition-colors"
                  >
                    <Save className="w-4 h-4" />
                    <span>Guardar</span>
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleCancel}
                    className="bg-red-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-red-600 transition-colors"
                  >
                    <X className="w-4 h-4" />
                    <span>Cancelar</span>
                  </motion.button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Información General */}
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Settings className="w-5 h-5 mr-2" />
                  Información General
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Nombre de la Institución
                    </label>
                    {isEditing ? (
                      <input
                        type="text"
                        value={editData.nombre}
                        onChange={(e) => handleInputChange('nombre', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                      />
                    ) : (
                      <p className="text-gray-900 dark:text-white font-medium">{institucion.nombre}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Descripción
                    </label>
                    {isEditing ? (
                      <textarea
                        value={editData.descripcion}
                        onChange={(e) => handleInputChange('descripcion', e.target.value)}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                      />
                    ) : (
                      <p className="text-gray-600 dark:text-gray-400">{institucion.descripcion}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        <MapPin className="w-4 h-4 inline mr-1" />
                        Dirección
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editData.direccion}
                          onChange={(e) => handleInputChange('direccion', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                        />
                      ) : (
                        <p className="text-gray-600 dark:text-gray-400">{institucion.direccion}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        <Calendar className="w-4 h-4 inline mr-1" />
                        Fecha de Fundación
                      </label>
                      {isEditing ? (
                        <input
                          type="date"
                          value={editData.fechaFundacion}
                          onChange={(e) => handleInputChange('fechaFundacion', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                        />
                      ) : (
                        <p className="text-gray-600 dark:text-gray-400">
                          {new Date(institucion.fechaFundacion).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        <Phone className="w-4 h-4 inline mr-1" />
                        Teléfono
                      </label>
                      {isEditing ? (
                        <input
                          type="tel"
                          value={editData.telefono}
                          onChange={(e) => handleInputChange('telefono', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                        />
                      ) : (
                        <p className="text-gray-600 dark:text-gray-400">{institucion.telefono}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        <Mail className="w-4 h-4 inline mr-1" />
                        Email
                      </label>
                      {isEditing ? (
                        <input
                          type="email"
                          value={editData.email}
                          onChange={(e) => handleInputChange('email', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                        />
                      ) : (
                        <p className="text-gray-600 dark:text-gray-400">{institucion.email}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Logo */}
              {isEditing && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
                    <Image className="w-5 h-5 mr-2" />
                    Logo de la Institución
                  </h3>
                  <div className="flex items-center space-x-4">
                    <img 
                      src={editData.logo} 
                      alt="Logo actual" 
                      className="w-20 h-20 rounded-lg object-cover border border-gray-300"
                    />
                    <button className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                      <Upload className="w-4 h-4 mr-2" />
                      Cambiar Logo
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Estadísticas y Configuración */}
            <div className="space-y-6">
              
              {/* Estadísticas */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  Estadísticas
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(institucion.estadisticas).map(([key, value]) => (
                    <motion.div
                      key={key}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg text-center"
                    >
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {value}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                        {key === 'clasesActivas' ? 'Clases Activas' : 
                         key === 'graduados' ? 'Graduados' : key}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Configuración */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Settings className="w-5 h-5 mr-2" />
                  Configuración Académica
                </h2>
                <div className="space-y-4">
                  {Object.entries(institucion.configuracion).map(([key, value]) => (
                    <div key={key}>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 capitalize">
                        {key === 'horariosClases' ? 'Horarios de Clases' :
                         key === 'diasActividad' ? 'Días de Actividad' :
                         key === 'periodoAcademico' ? 'Período Académico' :
                         key === 'modalidad' ? 'Modalidad' : key}
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editData.configuracion[key as keyof typeof editData.configuracion]}
                          onChange={(e) => handleConfigChange(key, e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                        />
                      ) : (
                        <p className="text-gray-600 dark:text-gray-400">{value}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
