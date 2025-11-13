import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';

// Importar API actualizada
import courseService from './services/courseService';
import CourseDetail from './CourseDetail';
import { AlertCircle, Book, Calendar, FileText, Filter, Loader2, Plus, RefreshCw, Search, User, Users } from 'lucide-react';

// Tipos
interface Curso {
  id: string | number;
  nombre: string;
  codigo: string;
  profesor: string;
  estudiantes: number;
  progreso: number;
  estado: string;
  descripcion: string;
  fechaInicio: string;
  fechaFin: string;
}

interface Grupo {
  id: string | number;
  nombre: string;
  curso: string;
  estudiantes: number;
  profesor: string;
  horario: string;
  aula: string;
}

export default function ModuloAcademico() {
  const [activeTab, setActiveTab] = useState('cursos');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterEstado, setFilterEstado] = useState('all');
  const [cursos, setCursos] = useState<Curso[]>([]);
  const [grupos, setGrupos] = useState<Grupo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [emptyMessage, setEmptyMessage] = useState<string | null>(null);
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
  
  // Estados para modal de inscripción
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [joinCode, setJoinCode] = useState('');
  const [joinLoading, setJoinLoading] = useState(false);
  const [joinError, setJoinError] = useState<string | null>(null);
  
  // Estados para vinculación inteligente de estudiante
  const [needsStudentProfile, setNeedsStudentProfile] = useState(false);
  const [linkingProfile, setLinkingProfile] = useState(false);
  const [showInvitationModal, setShowInvitationModal] = useState(false);
  const [invitationCode, setInvitationCode] = useState('');
  const [userEmail, setUserEmail] = useState('');

  // Cargar datos al montar el componente
  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Verificar autenticación antes de hacer la llamada
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setEmptyMessage('Debes iniciar sesión para ver tus cursos inscritos.');
        setCursos([]);
        setError(null);
        setLoading(false);
        return;
      }
      
      // Cargar cursos desde la API real
      const response = await courseService.getMyCourses();
      
      if (response.success) {
        // Verificar si hay un estado vacío específico
        if (response.empty_state && response.total === 0) {
          setCursos([]);
          setError(null); // No es un error, solo no tiene cursos
          setEmptyMessage(response.empty_message || 'Aún no te has unido a ningún curso');
        } else {
          // Transformar datos de la API para el componente
          interface CourseData {
            id?: string | number;
            curso_id?: string;
            title?: string;
            nombre?: string;
            codigo_acceso?: string;
            codigo?: string;
            instructor?: string;
            profesor?: string;
            total_estudiantes?: number;
            estudiantes?: number;
            progress?: number;
            progreso?: number;
            estado?: string;
            description?: string;
            descripcion?: string;
            fecha_inicio?: string;
            fecha_fin?: string;
          }
          
          const cursosTransformados: Curso[] = response.data.map((curso: CourseData) => ({
            id: curso.curso_id || curso.id || '',
            nombre: curso.title || curso.nombre || '',
            codigo: curso.codigo_acceso || curso.codigo || '',
            profesor: curso.instructor || curso.profesor || 'Profesor Asignado',
            estudiantes: curso.total_estudiantes || curso.estudiantes || 0,
            progreso: curso.progress || curso.progreso || 0,
            estado: curso.estado || 'activo',
            descripcion: curso.description || curso.descripcion || `Curso de ${curso.nombre}`,
            fechaInicio: curso.fecha_inicio || '2025-01-15',
            fechaFin: curso.fecha_fin || '2025-06-15'
          }));
          
          setCursos(cursosTransformados);
          setError(null);
          setEmptyMessage(null);
        }
      } else {
        console.warn('❌ Error en respuesta API:', response.message);
        
        // Detectar si el error es por falta de perfil de estudiante
        if (response.message && (
          response.message.includes('perfil de estudiante') || 
          response.message.includes('student profile') ||
          response.message.includes('vinculado a un programa') ||
          response.message.includes('vincular tu perfil')
        )) {
          setNeedsStudentProfile(true);
          setEmptyMessage('Necesitas vincular tu perfil de estudiante para ver tus cursos.');
        } else {
          setError(response.message || 'Error obteniendo cursos');
          setEmptyMessage(null);
        }
        
        setCursos([]);
      }
      
      // Cargar grupos reales desde la API - TEMPORALMENTE DESACTIVADO
      // Usar datos mock por ahora
      const gruposMock: Grupo[] = [
        {
          id: '1',
          nombre: 'Grupo A - Matemáticas',
          curso: 'Matemáticas Avanzadas',
          estudiantes: 15,
          profesor: 'Dr. García Rodríguez',
          horario: 'Lun-Mie-Vie 10:00-11:30',
          aula: 'Aula 105'
        }
      ];
      setGrupos(gruposMock);
      /*
      if (gruposResponse.success) {
        console.log(`✅ ${gruposResponse.total} grupos cargados desde ${gruposResponse.source}`);
        
        // Transformar datos de grupos para el componente
        const gruposTransformados: Grupo[] = gruposResponse.data.map((grupo) => ({
          id: grupo.id,
          nombre: grupo.nombre,
          curso: grupo.curso,
          estudiantes: grupo.estudiantes,
          profesor: grupo.profesor,
          horario: grupo.horario,
          aula: grupo.aula
        }));
        
        setGrupos(gruposTransformados);
        
        if (gruposResponse.source === 'database') {
          console.log('🎯 Grupos obtenidos directamente de PostgreSQL');
        }
      } else {
        console.warn('❌ Error obteniendo grupos:', gruposResponse.message);
        // Mantener datos mock como fallback para grupos
        const gruposMock: Grupo[] = [
          {
            id: '1',
            nombre: 'Grupo A - Matemáticas',
            curso: 'Matemáticas Avanzadas',
            estudiantes: 15,
            profesor: 'Dr. García Rodríguez',
            horario: 'Lun-Mie-Vie 10:00-11:30',
            aula: 'Aula 201'
          },
          {
            id: '2',
            nombre: 'Grupo B - Historia',
            curso: 'Historia Universal',
            estudiantes: 18,
            profesor: 'Dra. Martínez López',
            horario: 'Mar-Jue 14:00-15:30',
            aula: 'Aula 105'
          }
        ];
        setGrupos(gruposMock);
      }
      */
      
    } catch (error) {
      console.error('💥 Error crítico cargando datos:', error);
      setError(`Error crítico: ${error instanceof Error ? error.message : 'Error desconocido'}`);
      setCursos([]);
    } finally {
      setLoading(false);
    }
  };

  // Nueva función de auto-vinculación inteligente
  const handleAutoLinkStudentProfile = async () => {
    try {
      setLinkingProfile(true);
      
      // Verificar token antes de hacer la llamada
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('❌ No hay token de autenticación. Por favor, inicia sesión nuevamente.');
        return;
      }
      
      const response = await courseService.autoLinkStudentProfile();
      
      if (response.success) {
        setNeedsStudentProfile(false);
        setShowInvitationModal(false);
        
        // Recargar datos después de vincular
        await cargarDatos();
        
        // Mostrar mensaje específico según el método usado
        let mensaje = `✅ ${response.message}`;
        if (response.metodo === 'dominio_email') {
          mensaje += `\n\n🎯 Tu email fue reconocido automáticamente para '${response.institucion}'`;
        }
        alert(mensaje);
        
      } else if (response.requires_invitation) {
        // Guardar datos del usuario para el modal
        setUserEmail(response.user_email || '');
        setShowInvitationModal(true);
        
        alert(`📧 ${response.message}\n\nTe mostraremos el formulario para ingresar tu código de invitación.`);
      } else {
        console.error('❌ Error en auto-vinculación:', response.message);
        alert(`❌ Error: ${response.message}`);
      }
    } catch (error: unknown) {
      const err = error as { message?: string; response?: { data?: unknown; status?: number } };
      console.error('❌ Error inesperado en auto-vinculación:', error);
      alert(`❌ Error: ${err.message || 'Error inesperado al auto-vincular perfil'}`);
    } finally {
      setLinkingProfile(false);
    }
  };

  // Función para vincular por código de invitación
  const handleLinkByInvitationCode = async () => {
    if (!invitationCode.trim()) {
      alert('❌ Por favor, ingresa un código de invitación válido');
      return;
    }

    try {
      setLinkingProfile(true);
      
      const response = await courseService.linkByInvitationCode(invitationCode);
      
      if (response.success) {
        setNeedsStudentProfile(false);
        setShowInvitationModal(false);
        setInvitationCode('');
        
        // Recargar datos después de vincular
        await cargarDatos();
        
        alert(`✅ ${response.message}\n\n🎉 ¡Bienvenido a ${response.institucion}!`);
      } else {
        console.error('❌ Error en vinculación por código:', response.message);
        alert(`❌ Error: ${response.message}`);
      }
    } catch (error: unknown) {
      const err = error as { message?: string };
      console.error('❌ Error inesperado:', error);
      alert(`❌ Error: ${err.message || 'Error inesperado al vincular con código'}`);
    } finally {
      setLinkingProfile(false);
    }
  };

  const refrescarDatos = () => {
    cargarDatos();
  };

  // Filtrar cursos según búsqueda y estado
  const cursosFiltrados = cursos.filter(curso => {
    const matchSearch = curso.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                       curso.codigo.toLowerCase().includes(searchTerm.toLowerCase());
    const matchFilter = filterEstado === 'all' || curso.estado === filterEstado;
    return matchSearch && matchFilter;
  });

  // Filtrar grupos
  const gruposFiltrados = grupos.filter(grupo => {
    return grupo.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
           grupo.curso.toLowerCase().includes(searchTerm.toLowerCase());
  });

  // Manejar selección de curso
  const handleCourseSelect = (courseId: string) => {
    setSelectedCourse(courseId);
  };

  // Manejar inscripción a curso
  const handleJoinCourse = async () => {
    if (!joinCode.trim()) {
      setJoinError('Por favor ingresa un código de curso');
      return;
    }

    setJoinLoading(true);
    setJoinError(null);

    try {
      const result = await courseService.joinCourse(joinCode.trim());
      
      if (result.success) {
        // Mostrar mensaje de éxito
        alert(`¡Éxito! ${result.message}`);
        
        // Cerrar modal y limpiar
        setShowJoinModal(false);
        setJoinCode('');
        
        // Recargar cursos para mostrar el nuevo curso
        cargarDatos();
      } else {
        // Detectar si necesita crear perfil de estudiante
        if (result.message.includes('perfil de estudiante no está vinculado') || 
            result.message.includes('ninguna institución')) {
          setNeedsStudentProfile(true);
          setShowJoinModal(false);
          setJoinError(null);
        } else {
          setJoinError(result.message);
        }
      }
    } catch (error) {
      setJoinError('Error inesperado al inscribirse');
      console.error('Error en inscripción:', error);
    } finally {
      setJoinLoading(false);
    }
  };

  // Abrir modal de inscripción
  const handleNewCourse = () => {
    setShowJoinModal(true);
    setJoinCode('');
    setJoinError(null);
  };

  // Si hay un curso seleccionado, mostrar su detalle
  if (selectedCourse) {
    return (
      <CourseDetail 
        courseId={selectedCourse}
        onBack={() => setSelectedCourse(null)}
      />
    );
  }

  return (
    <div className="bg-gradient-to-br from-emerald-50 via-white to-teal-100 dark:from-gray-900 dark:via-gray-800 dark:to-emerald-900">
      <div className="max-w-7xl mx-auto px-6 py-6 mt-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Módulo Académico
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestión integral de cursos, grupos y actividades académicas
          </p>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap bg-white dark:bg-gray-800 rounded-xl p-2 mb-6 border border-gray-200 dark:border-gray-700">
          {[
            { key: 'cursos', label: 'Cursos', icon: Book },
            { key: 'grupos', label: 'Grupos', icon: Users },
            { key: 'materiales', label: 'Materiales', icon: FileText },
            { key: 'horarios', label: 'Horarios', icon: Calendar }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-emerald-600 text-white shadow-lg'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-emerald-50 dark:hover:bg-gray-700'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Controles */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between bg-white dark:bg-gray-800 rounded-xl p-6 mb-6 border border-gray-200 dark:border-gray-700 space-y-4 md:space-y-0">
          {/* Búsqueda */}
          <div className="flex items-center space-x-4 flex-1">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Buscar cursos, códigos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            {/* Filtros */}
            <div className="flex items-center space-x-2">
              <Filter className="text-gray-400 w-5 h-5" />
              <select
                value={filterEstado}
                onChange={(e) => setFilterEstado(e.target.value)}
                className="px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">Todos los estados</option>
                <option value="activo">Activos</option>
                <option value="próximo">Próximos</option>
                <option value="completado">Completados</option>
              </select>
            </div>
          </div>

          {/* Botones de acción */}
          <div className="flex items-center space-x-3">
            <button
              onClick={refrescarDatos}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-3 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              <span>Actualizar</span>
            </button>

            <button
              onClick={handleNewCourse}
              className="flex items-center space-x-2 px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors shadow-lg"
            >
              <Plus className="w-5 h-5" />
              <span>Nuevo {activeTab === 'cursos' ? 'Curso' : activeTab === 'grupos' ? 'Grupo' : 'Material'}</span>
            </button>
          </div>
        </div>

        {/* Contenido principal */}
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-20"
            >
              <Loader2 className="w-12 h-12 text-emerald-600 animate-spin mb-4" />
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                Cargando datos académicos...
              </p>
            </motion.div>
          ) : error ? (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-20"
            >
              <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
              <p className="text-red-600 dark:text-red-400 text-lg mb-4">
                {error}
              </p>
              <button
                onClick={refrescarDatos}
                className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
              >
                Reintentar
              </button>
            </motion.div>
          ) : (
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {activeTab === 'cursos' && (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {cursosFiltrados.length === 0 ? (
                    <div className="col-span-full text-center py-12">
                      <Book className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <div className="space-y-3">
                        <p className="text-gray-600 dark:text-gray-400 text-lg font-medium">
                          {emptyMessage || (searchTerm ? 'No se encontraron cursos con los criterios de búsqueda' : 'No hay cursos disponibles')}
                        </p>
                        {emptyMessage && !searchTerm && (
                          <div className="mt-6 space-y-3">
                            {emptyMessage.includes('sesión') || emptyMessage.includes('iniciar sesión') ? (
                              <button
                                onClick={() => window.location.href = '/login'}
                                className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                              >
                                <User className="w-5 h-5 mr-2" />
                                Iniciar Sesión
                              </button>
                            ) : (
                              <button
                                onClick={() => setShowJoinModal(true)}
                                className="inline-flex items-center px-6 py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 transition-colors"
                              >
                                <Plus className="w-5 h-5 mr-2" />
                                Unirme a un Curso
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    cursosFiltrados.map((curso, index) => (
                      <motion.div
                        key={curso.id}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.1, duration: 0.3 }}
                        className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
                        onClick={() => curso.id && handleCourseSelect(curso.id.toString())}
                      >
                        <div className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div>
                              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                                {curso.nombre}
                              </h3>
                              <p className="text-sm text-emerald-600 dark:text-emerald-400 font-medium">
                                {curso.codigo}
                              </p>
                            </div>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              curso.estado === 'activo' 
                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                : curso.estado === 'próximo'
                                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                                : curso.estado === 'completado'
                                ? 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                                : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                            }`}>
                              {curso.estado}
                            </span>
                          </div>

                          <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
                            {curso.descripcion}
                          </p>

                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                              <Users className="w-4 h-4" />
                              <span>{curso.estudiantes} estudiantes</span>
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {curso.progreso}% progreso
                            </div>
                          </div>

                          {/* Barra de progreso */}
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-4">
                            <div 
                              className="bg-emerald-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${curso.progreso}%` }}
                            ></div>
                          </div>

                          <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                            <span>{curso.profesor}</span>
                            <span>{curso.fechaInicio} - {curso.fechaFin}</span>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'grupos' && (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {gruposFiltrados.map((grupo, index) => (
                    <motion.div
                      key={grupo.id}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.1, duration: 0.3 }}
                      className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
                    >
                      <div className="p-6">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                          {grupo.nombre}
                        </h3>
                        <p className="text-emerald-600 dark:text-emerald-400 text-sm font-medium mb-4">
                          {grupo.curso}
                        </p>
                        
                        <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                          <div className="flex items-center space-x-2">
                            <Users className="w-4 h-4" />
                            <span>{grupo.estudiantes} estudiantes</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Calendar className="w-4 h-4" />
                            <span>{grupo.horario}</span>
                          </div>
                          <div>
                            <span className="font-medium">Profesor:</span> {grupo.profesor}
                          </div>
                          <div>
                            <span className="font-medium">Aula:</span> {grupo.aula}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}

              {(activeTab === 'materiales' || activeTab === 'horarios') && (
                <div className="text-center py-20">
                  <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400 text-lg">
                    Sección en desarrollo
                  </p>
                  <p className="text-gray-500 dark:text-gray-500 text-sm mt-2">
                    Esta funcionalidad será implementada próximamente
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Modal de inscripción */}
        <AnimatePresence>
          {showJoinModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
              onClick={() => setShowJoinModal(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white dark:bg-gray-800 rounded-xl p-6 m-4 max-w-md w-full"
                onClick={e => e.stopPropagation()}
              >
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                  Unirse a un Curso
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Ingresa el código del curso al que te quieres inscribir
                </p>

                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 mb-6">
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    ¿Aún no perteneces a una institución?{' '}
                    <Link 
                      to="/invitaciones/usar-codigo" 
                      className="font-medium underline hover:text-blue-600 dark:hover:text-blue-300"
                      onClick={() => setShowJoinModal(false)}
                    >
                      Usa un código de invitación aquí
                    </Link>
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Código del Curso
                    </label>
                    <input
                      type="text"
                      value={joinCode}
                      onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                      placeholder="Ej: MAT301, HIS201, POO301"
                      className="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>

                  {joinError && (
                    <div className="text-red-600 dark:text-red-400 text-sm">
                      {joinError}
                    </div>
                  )}

                  <div className="flex space-x-3">
                    <button
                      onClick={() => setShowJoinModal(false)}
                      className="flex-1 px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={handleJoinCourse}
                      disabled={joinLoading || !joinCode.trim()}
                      className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {joinLoading ? 'Inscribiendo...' : 'Inscribirse'}
                    </button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Modal para vincular perfil de estudiante */}
        <AnimatePresence>
          {needsStudentProfile && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
              onClick={() => setNeedsStudentProfile(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white dark:bg-gray-800 rounded-xl p-6 m-4 max-w-md w-full"
                onClick={e => e.stopPropagation()}
              >
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                  🎯 Vinculación Inteligente de Estudiante
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Nuestro sistema intentará vincularte automáticamente usando tu email institucional o 
                  podrás usar un código de invitación.
                </p>

                <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg p-4 mb-6">
                  <div className="flex items-start space-x-3">
                    <User className="w-5 h-5 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <h4 className="font-medium text-emerald-900 dark:text-emerald-100">
                        🚀 Vinculación Automática
                      </h4>
                      <p className="text-sm text-emerald-700 dark:text-emerald-300 mt-1">
                        • <strong>Email @arp.edu.co</strong> → Colegio Alejandro Obregón
                        <br />
                        • <strong>Email @uniejemplo.edu</strong> → Universidad Ejemplo
                        <br />
                        • <strong>Otros dominios</strong> → Código de invitación
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={() => setNeedsStudentProfile(false)}
                    className="flex-1 px-4 py-2 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleAutoLinkStudentProfile}
                    disabled={linkingProfile}
                    className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {linkingProfile ? 'Vinculando...' : '🎯 Auto-Vincular'}
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Modal para código de invitación */}
        <AnimatePresence>
          {showInvitationModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
              onClick={() => setShowInvitationModal(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white dark:bg-gray-800 rounded-xl p-6 m-4 max-w-md w-full"
                onClick={e => e.stopPropagation()}
              >
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                  📧 Código de Invitación
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Tu email <strong>{userEmail}</strong> no está registrado en nuestro sistema.
                  <br />Ingresa el código de invitación que te proporcionó tu institución.
                </p>

                <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 mb-6">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <h4 className="font-medium text-amber-900 dark:text-amber-100">
                        Ejemplos de códigos válidos:
                      </h4>
                      <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                        INV-2025-ARP-001, INV-2025-UNEJ-001, TEST-ARP-2025
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Código de Invitación
                    </label>
                    <input
                      type="text"
                      value={invitationCode}
                      onChange={(e) => setInvitationCode(e.target.value.toUpperCase())}
                      placeholder="INV-2025-ARP-001"
                      className="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={() => {
                        setShowInvitationModal(false);
                        setInvitationCode('');
                      }}
                      className="flex-1 px-4 py-2 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={handleLinkByInvitationCode}
                      disabled={linkingProfile || !invitationCode.trim()}
                      className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {linkingProfile ? 'Vinculando...' : 'Vincular'}
                    </button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}