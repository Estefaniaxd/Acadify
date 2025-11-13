import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Building2, Users, BookOpen, GraduationCap, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import axios from 'axios';

interface Institucion {
  id: number;
  nombre: string;
  tipo: string;
  ubicacion?: string;
  estado: string;
  created_at: string;
}

interface EstadisticasInstitucion {
  total_estudiantes: number;
  total_profesores: number;
  total_cursos: number;
  usuarios_pendientes: number;
}

const obtenerMiInstitucion = async (): Promise<Institucion> => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('No hay token de autenticación');
  }

  const response = await axios.get(
    'http://localhost:8000/api/coordinador/mi-institucion',
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  return response.data;
};

const obtenerEstadisticas = async (institucionId: number): Promise<EstadisticasInstitucion> => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('No hay token de autenticación');
  }

  const response = await axios.get(
    `http://localhost:8000/api/coordinador/institucion/${institucionId}/estadisticas`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  return response.data;
};

export default function CoordinadorInstitucionPage() {
  const { data: institucion, isLoading, error } = useQuery({
    queryKey: ['mi-institucion'],
    queryFn: obtenerMiInstitucion,
    retry: 3, // Reintentar 3 veces
    retryDelay: 1000, // Esperar 1 segundo entre reintentos
    staleTime: 0 // Siempre considerar los datos como obsoletos
  });

  const { data: estadisticas } = useQuery({
    queryKey: ['estadisticas-institucion', institucion?.id],
    queryFn: () => obtenerEstadisticas(institucion!.id),
    enabled: !!institucion?.id
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center"
        >
          <AlertCircle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            No tienes una institución asignada
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Para empezar, necesitas aceptar una invitación de coordinador.
          </p>
          <a
            href="/invitaciones/aceptar"
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            <CheckCircle className="w-5 h-5" />
            Aceptar Invitación
          </a>
        </motion.div>
      </div>
    );
  }

  const estadoColor = {
    activa: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    pendiente: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    inactiva: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
  }[institucion?.estado || 'pendiente'];

  const estadoIconMap = {
    activa: CheckCircle,
    pendiente: Clock,
    inactiva: AlertCircle
  };
  
  const EstadoIcon = estadoIconMap[institucion?.estado as keyof typeof estadoIconMap] || Clock;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Mi Institución
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestiona tu institución educativa
          </p>
        </motion.div>

        {/* Información de la Institución */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6"
        >
          <div className="flex items-start gap-4">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg">
              <Building2 className="w-8 h-8 text-white" />
            </div>
            <div className="flex-1">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {institucion?.nombre}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 capitalize">
                    {institucion?.tipo}
                  </p>
                </div>
                <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${estadoColor}`}>
                  <EstadoIcon className="w-4 h-4" />
                  {institucion?.estado}
                </span>
              </div>
              {institucion?.ubicacion && (
                <p className="text-gray-500 dark:text-gray-400">
                  📍 {institucion.ubicacion}
                </p>
              )}
            </div>
          </div>
        </motion.div>

        {/* Estadísticas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <GraduationCap className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Estudiantes</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {estadisticas?.total_estudiantes || 0}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <Users className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Profesores</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {estadisticas?.total_profesores || 0}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <BookOpen className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Cursos</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {estadisticas?.total_cursos || 0}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
                <Clock className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Pendientes</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {estadisticas?.usuarios_pendientes || 0}
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Acciones Rápidas */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Acciones Rápidas
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="/coordinador/aprobar-usuarios"
              className="flex items-center gap-3 p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <CheckCircle className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Aprobar Usuarios</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {estadisticas?.usuarios_pendientes || 0} pendientes
                </p>
              </div>
            </a>
            
            <a
              href="/cursos"
              className="flex items-center gap-3 p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <BookOpen className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Gestionar Cursos</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Ver todos los cursos</p>
              </div>
            </a>
            
            <a
              href="/comunicacion"
              className="flex items-center gap-3 p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <Users className="w-5 h-5 text-green-600 dark:text-green-400" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Comunicación</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Mensajes y chats</p>
              </div>
            </a>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
