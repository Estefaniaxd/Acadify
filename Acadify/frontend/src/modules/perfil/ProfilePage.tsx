import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiArrowLeft, 
  FiUser, 
  FiMail, 
  FiPhone, 
  FiCalendar, 
  FiMapPin,
  FiEdit3,
  FiCamera,
  FiBook,
  FiAward,
  FiActivity,
  FiSettings,
  FiShield,
  FiGlobe,
  FiClock,
  FiTrendingUp,
  FiTarget,
  FiStar,
  FiBookOpen,
  FiUsers,
  FiMessageCircle,
  FiHeart,
  FiCheck,
  FiX,
  FiSave,
  FiUpload,
  FiEye,
  FiEyeOff,
  FiLock,
  FiBell,
  FiGrid,
  FiList,
  FiBarChart,
  FiPieChart
} from 'react-icons/fi';

interface UserProfile {
  id: string;
  nombres: string;
  apellidos: string;
  correo_institucional: string;
  rol: string;
  estado_cuenta: string;
  telefono?: string;
  descripcion?: string;
  perfil_url?: string;
  portada_url?: string;
  fecha_creacion: string;
  ultimo_acceso?: string;
  email_verified: boolean;
  twofa_enabled: boolean;
}

interface UserStats {
  cursos_completados: number;
  cursos_activos: number;
  promedio_calificaciones: number;
  total_horas_estudio: number;
  logros_obtenidos: number;
  puntos_totales: number;
  rango_actual: string;
  nivel_actual: number;
}

interface RecentActivity {
  id: string;
  tipo: 'curso' | 'tarea' | 'examen' | 'logro';
  titulo: string;
  descripcion: string;
  fecha: string;
  calificacion?: number;
}

export default function ProfilePage(): JSX.Element {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    nombres: '',
    apellidos: '',
    telefono: '',
    descripcion: ''
  });

  useEffect(() => {
    loadUserData();
  }, [userId]);

  const loadUserData = async () => {
    try {
      setLoading(true);
      // Simular datos - aquí harías llamadas reales al API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockProfile: UserProfile = {
        id: userId || '',
        nombres: 'Estefanía',
        apellidos: 'Londoño',
        correo_institucional: 'estefania.londono@arp.edu.co',
        rol: 'estudiante',
        estado_cuenta: 'activo',
        telefono: '+57 300 123 4567',
        descripcion: 'Estudiante de Ingeniería de Sistemas apasionada por la tecnología y el desarrollo web. Me encanta aprender nuevas tecnologías y trabajar en proyectos desafiantes.',
        fecha_creacion: '2023-01-15T08:00:00Z',
        ultimo_acceso: new Date().toISOString(),
        email_verified: true,
        twofa_enabled: false
      };

      const mockStats: UserStats = {
        cursos_completados: 12,
        cursos_activos: 3,
        promedio_calificaciones: 4.7,
        total_horas_estudio: 245,
        logros_obtenidos: 18,
        puntos_totales: 2840,
        rango_actual: 'Estudiante Destacado',
        nivel_actual: 15
      };

      const mockActivities: RecentActivity[] = [
        {
          id: '1',
          tipo: 'curso',
          titulo: 'Programación Web Avanzada',
          descripcion: 'Completado módulo de React Hooks',
          fecha: '2025-09-29T14:30:00Z',
          calificacion: 4.8
        },
        {
          id: '2',
          tipo: 'tarea',
          titulo: 'Proyecto Final - API REST',
          descripcion: 'Entregado proyecto final',
          fecha: '2025-09-28T16:45:00Z',
          calificacion: 4.9
        },
        {
          id: '3',
          tipo: 'logro',
          titulo: 'Streak de 30 días',
          descripcion: 'Mantuviste actividad diaria por 30 días',
          fecha: '2025-09-27T10:00:00Z'
        }
      ];

      setProfile(mockProfile);
      setStats(mockStats);
      setActivities(mockActivities);
      setEditForm({
        nombres: mockProfile.nombres,
        apellidos: mockProfile.apellidos,
        telefono: mockProfile.telefono || '',
        descripcion: mockProfile.descripcion || ''
      });
    } catch (err) {
      setError('Error al cargar el perfil del usuario');
    } finally {
      setLoading(false);
    }
  };

  const isUserOnline = (lastAccess?: string) => {
    if (!lastAccess) return false;
    const lastAccessDate = new Date(lastAccess);
    const now = new Date();
    const diffInMinutes = (now.getTime() - lastAccessDate.getTime()) / (1000 * 60);
    return diffInMinutes <= 15;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRoleColor = (rol: string) => {
    switch (rol.toLowerCase()) {
      case 'estudiante':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'docente':
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200';
      case 'coordinador':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'administrador':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getActivityIcon = (tipo: string) => {
    switch (tipo) {
      case 'curso': return <FiBookOpen className="w-4 h-4" />;
      case 'tarea': return <FiEdit3 className="w-4 h-4" />;
      case 'examen': return <FiTarget className="w-4 h-4" />;
      case 'logro': return <FiAward className="w-4 h-4" />;
      default: return <FiActivity className="w-4 h-4" />;
    }
  };

  const getActivityColor = (tipo: string) => {
    switch (tipo) {
      case 'curso': return 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300';
      case 'tarea': return 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-300';
      case 'examen': return 'bg-purple-100 text-purple-600 dark:bg-purple-900 dark:text-purple-300';
      case 'logro': return 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900 dark:text-yellow-300';
      default: return 'bg-gray-100 text-gray-600 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const handleSaveProfile = async () => {
    try {
      // Aquí harías la llamada al API para guardar los cambios
      console.log('Guardando perfil:', editForm);
      
      if (profile) {
        setProfile({
          ...profile,
          nombres: editForm.nombres,
          apellidos: editForm.apellidos,
          telefono: editForm.telefono,
          descripcion: editForm.descripcion
        });
      }
      
      setIsEditing(false);
    } catch (err) {
      console.error('Error al guardar perfil:', err);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Resumen', icon: FiUser },
    { id: 'stats', label: 'Estadísticas', icon: FiBarChart },
    { id: 'activity', label: 'Actividad', icon: FiActivity },
    { id: 'settings', label: 'Configuración', icon: FiSettings }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400 text-lg">Cargando perfil...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <FiUser className="w-20 h-20 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Error al cargar el perfil
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {error || 'No se pudo encontrar el perfil del usuario.'}
          </p>
          <button
            onClick={() => navigate(-1)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Volver
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors group"
            >
              <FiArrowLeft className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" />
              Volver
            </button>
            
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Perfil de Usuario
            </h1>
            
            <div className="w-20"></div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden mb-8"
        >
          {/* Cover Image */}
          <div className="h-48 bg-gradient-to-br from-blue-600 via-purple-600 to-emerald-600 relative">
            <div className="absolute inset-0 bg-black/20"></div>
            <div className="absolute top-4 right-4">
              <button className="p-2 bg-black/30 backdrop-blur-sm rounded-lg text-white hover:bg-black/50 transition-colors">
                <FiCamera className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Profile Info */}
          <div className="relative px-8 pb-8">
            <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between">
              {/* Avatar and Basic Info */}
              <div className="flex flex-col lg:flex-row lg:items-end -mt-16 lg:-mt-20">
                <div className="relative mb-4 lg:mb-0 lg:mr-6">
                  {profile.perfil_url ? (
                    <img
                      src={profile.perfil_url}
                      alt={`${profile.nombres} ${profile.apellidos}`}
                      className="w-32 h-32 lg:w-40 lg:h-40 rounded-full border-4 border-white dark:border-gray-800 object-cover shadow-lg"
                    />
                  ) : (
                    <div className="w-32 h-32 lg:w-40 lg:h-40 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full border-4 border-white dark:border-gray-800 flex items-center justify-center shadow-lg">
                      <span className="text-3xl lg:text-4xl font-bold text-white">
                        {profile.nombres.charAt(0)}{profile.apellidos.charAt(0)}
                      </span>
                    </div>
                  )}
                  
                  <div className={`absolute -bottom-2 -right-2 w-8 h-8 rounded-full border-4 border-white dark:border-gray-800 flex items-center justify-center ${
                    isUserOnline(profile.ultimo_acceso) ? 'bg-green-500' : 'bg-gray-400'
                  }`}>
                    <div className={`w-3 h-3 rounded-full ${
                      isUserOnline(profile.ultimo_acceso) ? 'bg-green-400' : 'bg-gray-300'
                    }`}></div>
                  </div>
                  
                  <button className="absolute bottom-0 right-8 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors shadow-lg">
                    <FiCamera className="w-4 h-4" />
                  </button>
                </div>

                <div className="text-center lg:text-left lg:pb-4">
                  <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white mb-2">
                    {profile.nombres} {profile.apellidos}
                  </h1>
                  <div className="flex flex-wrap items-center justify-center lg:justify-start gap-3 mb-4">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRoleColor(profile.rol)}`}>
                      {profile.rol.charAt(0).toUpperCase() + profile.rol.slice(1)}
                    </span>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                      profile.estado_cuenta === 'activo' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}>
                      <div className={`w-2 h-2 rounded-full mr-2 ${
                        profile.estado_cuenta === 'activo' ? 'bg-green-500' : 'bg-red-500'
                      }`}></div>
                      {profile.estado_cuenta === 'activo' ? 'Activo' : 'Inactivo'}
                    </span>
                    {profile.email_verified && (
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        <FiCheck className="w-3 h-3 mr-1" />
                        Verificado
                      </span>
                    )}
                  </div>
                  <p className="text-gray-600 dark:text-gray-400 max-w-2xl">
                    {profile.descripcion}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3 mt-6 lg:mt-0 justify-center lg:justify-end">
                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  <FiEdit3 className="w-4 h-4 mr-2" />
                  {isEditing ? 'Cancelar' : 'Editar'}
                </button>
                <button
                  onClick={() => window.open(`mailto:${profile.correo_institucional}`, '_blank')}
                  className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium"
                >
                  <FiMail className="w-4 h-4 mr-2" />
                  Email
                </button>
                <button className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium">
                  <FiMessageCircle className="w-4 h-4 mr-2" />
                  Mensaje
                </button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-2">
            <div className="flex flex-wrap gap-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center px-4 py-3 rounded-lg font-medium transition-all ${
                      activeTab === tab.id
                        ? 'bg-blue-600 text-white shadow-lg'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Personal Information */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                        Información Personal
                      </h3>
                      {!isEditing && (
                        <button
                          onClick={() => setIsEditing(true)}
                          className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                        >
                          <FiEdit3 className="w-4 h-4" />
                        </button>
                      )}
                    </div>

                    {isEditing ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Nombres
                            </label>
                            <input
                              type="text"
                              value={editForm.nombres}
                              onChange={(e) => setEditForm({...editForm, nombres: e.target.value})}
                              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Apellidos
                            </label>
                            <input
                              type="text"
                              value={editForm.apellidos}
                              onChange={(e) => setEditForm({...editForm, apellidos: e.target.value})}
                              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            />
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Teléfono
                          </label>
                          <input
                            type="tel"
                            value={editForm.telefono}
                            onChange={(e) => setEditForm({...editForm, telefono: e.target.value})}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Descripción
                          </label>
                          <textarea
                            value={editForm.descripcion}
                            onChange={(e) => setEditForm({...editForm, descripcion: e.target.value})}
                            rows={3}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          />
                        </div>
                        <div className="flex gap-3 pt-4">
                          <button
                            onClick={handleSaveProfile}
                            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                          >
                            <FiSave className="w-4 h-4 mr-2" />
                            Guardar
                          </button>
                          <button
                            onClick={() => setIsEditing(false)}
                            className="flex items-center px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                          >
                            <FiX className="w-4 h-4 mr-2" />
                            Cancelar
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="flex items-center">
                            <FiMail className="w-5 h-5 text-gray-400 mr-3" />
                            <div>
                              <p className="text-sm text-gray-500 dark:text-gray-400">Email</p>
                              <p className="text-gray-900 dark:text-white font-medium">{profile.correo_institucional}</p>
                            </div>
                          </div>
                          
                          {profile.telefono && (
                            <div className="flex items-center">
                              <FiPhone className="w-5 h-5 text-gray-400 mr-3" />
                              <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Teléfono</p>
                                <p className="text-gray-900 dark:text-white font-medium">{profile.telefono}</p>
                              </div>
                            </div>
                          )}
                          
                          <div className="flex items-center">
                            <FiCalendar className="w-5 h-5 text-gray-400 mr-3" />
                            <div>
                              <p className="text-sm text-gray-500 dark:text-gray-400">Miembro desde</p>
                              <p className="text-gray-900 dark:text-white font-medium">{formatDate(profile.fecha_creacion)}</p>
                            </div>
                          </div>
                          
                          {profile.ultimo_acceso && (
                            <div className="flex items-center">
                              <FiActivity className="w-5 h-5 text-gray-400 mr-3" />
                              <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Último acceso</p>
                                <p className="text-gray-900 dark:text-white font-medium">
                                  {isUserOnline(profile.ultimo_acceso) 
                                    ? 'En línea ahora' 
                                    : formatTime(profile.ultimo_acceso)
                                  }
                                </p>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="space-y-6">
                  {stats && (
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                        Estadísticas Rápidas
                      </h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mr-3">
                              <FiBookOpen className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                            </div>
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white">{stats.cursos_activos}</p>
                              <p className="text-sm text-gray-500 dark:text-gray-400">Cursos activos</p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mr-3">
                              <FiCheck className="w-5 h-5 text-green-600 dark:text-green-400" />
                            </div>
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white">{stats.cursos_completados}</p>
                              <p className="text-sm text-gray-500 dark:text-gray-400">Cursos completados</p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-yellow-100 dark:bg-yellow-900 rounded-lg flex items-center justify-center mr-3">
                              <FiStar className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                            </div>
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white">{stats.promedio_calificaciones}</p>
                              <p className="text-sm text-gray-500 dark:text-gray-400">Promedio</p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mr-3">
                              <FiAward className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                            </div>
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white">{stats.logros_obtenidos}</p>
                              <p className="text-sm text-gray-500 dark:text-gray-400">Logros</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'stats' && stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Stats Cards */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                      <FiBookOpen className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <FiTrendingUp className="w-5 h-5 text-green-500" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{stats.cursos_completados}</h3>
                  <p className="text-gray-600 dark:text-gray-400">Cursos Completados</p>
                  <div className="mt-2 text-sm text-green-600 dark:text-green-400">
                    +2 este mes
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                      <FiStar className="w-6 h-6 text-green-600 dark:text-green-400" />
                    </div>
                    <FiTrendingUp className="w-5 h-5 text-green-500" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{stats.promedio_calificaciones}</h3>
                  <p className="text-gray-600 dark:text-gray-400">Promedio General</p>
                  <div className="mt-2 text-sm text-green-600 dark:text-green-400">
                    +0.2 este mes
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                      <FiClock className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                    </div>
                    <FiTrendingUp className="w-5 h-5 text-green-500" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_horas_estudio}</h3>
                  <p className="text-gray-600 dark:text-gray-400">Horas de Estudio</p>
                  <div className="mt-2 text-sm text-green-600 dark:text-green-400">
                    +15 esta semana
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900 rounded-lg flex items-center justify-center">
                      <FiAward className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                    </div>
                    <FiTrendingUp className="w-5 h-5 text-green-500" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{stats.logros_obtenidos}</h3>
                  <p className="text-gray-600 dark:text-gray-400">Logros Obtenidos</p>
                  <div className="mt-2 text-sm text-green-600 dark:text-green-400">
                    +3 este mes
                  </div>
                </div>

                {/* Progress Charts */}
                <div className="md:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                    Progreso del Nivel
                  </h3>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Nivel {stats.nivel_actual}</span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">{stats.puntos_totales} puntos</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-4">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full"
                      style={{ width: '75%' }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    160 puntos para el siguiente nivel
                  </p>
                </div>

                <div className="md:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                    Rango Actual
                  </h3>
                  <div className="flex items-center">
                    <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center mr-4">
                      <FiAward className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <h4 className="text-xl font-bold text-gray-900 dark:text-white">{stats.rango_actual}</h4>
                      <p className="text-gray-600 dark:text-gray-400">Top 15% de estudiantes</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'activity' && (
              <div className="space-y-6">
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                    Actividad Reciente
                  </h3>
                  <div className="space-y-4">
                    {activities.map((activity) => (
                      <div key={activity.id} className="flex items-start p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center mr-4 ${getActivityColor(activity.tipo)}`}>
                          {getActivityIcon(activity.tipo)}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 dark:text-white">{activity.titulo}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{activity.descripcion}</p>
                          <div className="flex items-center mt-2">
                            <FiClock className="w-4 h-4 text-gray-400 mr-1" />
                            <span className="text-sm text-gray-500 dark:text-gray-400">
                              {formatTime(activity.fecha)}
                            </span>
                            {activity.calificacion && (
                              <div className="ml-auto flex items-center">
                                <FiStar className="w-4 h-4 text-yellow-500 mr-1" />
                                <span className="text-sm font-medium text-gray-900 dark:text-white">
                                  {activity.calificacion}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Security Settings */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                    Configuración de Seguridad
                  </h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <FiShield className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">Autenticación de dos factores</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {profile.twofa_enabled ? 'Activada' : 'Desactivada'}
                          </p>
                        </div>
                      </div>
                      <button className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        profile.twofa_enabled 
                          ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}>
                        {profile.twofa_enabled ? 'Desactivar' : 'Activar'}
                      </button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <FiLock className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">Cambiar contraseña</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Actualiza tu contraseña</p>
                        </div>
                      </div>
                      <button className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm font-medium">
                        Cambiar
                      </button>
                    </div>
                  </div>
                </div>

                {/* Notification Settings */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                    Notificaciones
                  </h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <FiBell className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">Notificaciones por email</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Recibir actualizaciones por correo</p>
                        </div>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <FiMessageCircle className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">Notificaciones push</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Notificaciones en el navegador</p>
                        </div>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}