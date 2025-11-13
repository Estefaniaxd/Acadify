import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Building2, 
  Users, 
  BookOpen, 
  GraduationCap, 
  AlertCircle,
  Plus,
  Settings,
  BarChart3,
  X
} from 'lucide-react';
import axios from 'axios';
import CrearProgramaModal from '../../components/coordinador/CrearProgramaModal';
import EditarInstitucionModal from '../../components/coordinador/EditarInstitucionModal';
import CrearClaseModal from '../../components/coordinador/CrearClaseModal';
import CrearCursoModal from '../../components/coordinador/CrearCursoModal';

interface Institucion {
  id: string;
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
  total_programas: number;
}

interface Programa {
  programa_id: string;
  nombre: string;
  codigo?: string;
  nivel: string;
  tipo: string;
  descripcion?: string;
  estado: string;
  duracion_periodos?: number;
  duracion_tipo?: string;
  creditos_totales?: number;
  costo_matricula?: number;
  institucion_id: string;
}

interface Grupo {
  grupo_id: string;
  nombre: string;
  jornada: string;
  programa_id?: string;
  docente_tutor_id?: string;
}

interface Curso {
  curso_id: string;
  nombre: string;
  descripcion?: string;
  modalidad: string;
  creditos?: number;
  codigo_acceso?: string;
  activo: boolean;
  permite_inscripcion: boolean;
}

type TabType = 'general' | 'programas' | 'cursos' | 'clases' | 'profesores' | 'estudiantes' | 'estadisticas';

const obtenerMiInstitucion = async (): Promise<Institucion> => {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await axios.get(
    'http://localhost:8000/api/coordinador/mi-institucion',
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return response.data;
};

const obtenerEstadisticas = async (institucionId: string): Promise<EstadisticasInstitucion> => {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await axios.get(
    `http://localhost:8000/api/coordinador/institucion/${institucionId}/estadisticas`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return response.data;
};

export default function CoordinadorInstitucionPageV2() {
  const [activeTab, setActiveTab] = useState<TabType>('general');

  const { data: institucion, isLoading, error } = useQuery({
    queryKey: ['mi-institucion'],
    queryFn: obtenerMiInstitucion,
    retry: 3,
    retryDelay: 1000,
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

  if (error || !institucion) {
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
          <p className="text-gray-600 dark:text-gray-400">
            Contacta con el administrador para que te asigne una institución.
          </p>
        </motion.div>
      </div>
    );
  }

  const tabs: { id: TabType; label: string; icon: typeof Building2 }[] = [
    { id: 'general', label: 'Información General', icon: Building2 },
    { id: 'programas', label: 'Programas', icon: GraduationCap },
    { id: 'cursos', label: 'Cursos', icon: BookOpen },
    { id: 'clases', label: 'Clases/Grupos', icon: Users },
    { id: 'profesores', label: 'Profesores', icon: Users },
    { id: 'estudiantes', label: 'Estudiantes', icon: Users },
    { id: 'estadisticas', label: 'Estadísticas', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {institucion.nombre}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {institucion.tipo} • {institucion.ubicacion}
          </p>
        </motion.div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Programas', value: estadisticas?.total_programas || 0, icon: GraduationCap, color: 'blue' },
            { label: 'Cursos', value: estadisticas?.total_cursos || 0, icon: BookOpen, color: 'green' },
            { label: 'Profesores', value: estadisticas?.total_profesores || 0, icon: Users, color: 'purple' },
            { label: 'Estudiantes', value: estadisticas?.total_estudiantes || 0, icon: Users, color: 'orange' },
          ].map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 dark:text-gray-400 text-sm">{stat.label}</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                      {stat.value}
                    </p>
                  </div>
                  <Icon className={`w-12 h-12 text-${stat.color}-500`} />
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Tabs Navigation */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm mb-6 overflow-x-auto">
          <div className="flex border-b border-gray-200 dark:border-gray-700">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                    isActive
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {tab.label}
                </button>
              );
            })}
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
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6"
          >
            {activeTab === 'general' && <TabGeneral institucion={institucion} />}
            {activeTab === 'programas' && <TabProgramas institucionId={institucion.id} />}
            {activeTab === 'cursos' && <TabCursos institucionId={institucion.id} />}
            {activeTab === 'clases' && <TabClases institucionId={institucion.id} />}
            {activeTab === 'profesores' && <TabProfesores institucionId={institucion.id} />}
            {activeTab === 'estudiantes' && <TabEstudiantes institucionId={institucion.id} />}
            {activeTab === 'estadisticas' && <TabEstadisticas estadisticas={estadisticas} />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

// Tab Components
function TabGeneral({ institucion }: { institucion: Institucion }) {
  const [showEditModal, setShowEditModal] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Información General
        </h2>
        <button 
          onClick={() => setShowEditModal(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Settings className="w-5 h-5" />
          Editar
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Nombre de la Institución
          </label>
          <p className="text-lg text-gray-900 dark:text-white">{institucion.nombre}</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Tipo de Institución
          </label>
          <p className="text-lg text-gray-900 dark:text-white">{institucion.tipo}</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Ubicación
          </label>
          <p className="text-lg text-gray-900 dark:text-white">{institucion.ubicacion || 'No especificada'}</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Estado
          </label>
          <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
            institucion.estado === 'activa'
              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
              : 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300'
          }`}>
            {institucion.estado}
          </span>
        </div>
      </div>

      {showEditModal && (
        <EditarInstitucionModal
          institucion={institucion}
          onClose={() => setShowEditModal(false)}
        />
      )}
    </div>
  );
}

function TabProgramas({ institucionId }: { institucionId: string }) {
  const [showModal, setShowModal] = useState(false);
  const [selectedPrograma, setSelectedPrograma] = useState<Programa | null>(null);

  const { data: programas, isLoading } = useQuery({
    queryKey: ['programas', institucionId],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/programas/', {
        headers: { Authorization: `Bearer ${token}` },
        params: { institucion_id: institucionId }
      });
      return response.data;
    },
  });

  const queryClient = useQueryClient();
  const deleteMutation = useMutation({
    mutationFn: async (programaId: string) => {
      const token = localStorage.getItem('access_token');
      await axios.delete(`http://localhost:8000/api/programas/${programaId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programas'] });
      queryClient.invalidateQueries({ queryKey: ['estadisticas-institucion'] });
    },
  });

  if (isLoading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Programas Académicos
        </h2>
        <button 
          onClick={() => { setSelectedPrograma(null); setShowModal(true); }}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          Nuevo Programa
        </button>
      </div>

      {programas && programas.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {programas.map((programa: Programa) => (
            <div key={programa.programa_id} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <GraduationCap className="w-8 h-8 text-blue-600" />
                <div className="flex gap-2">
                  <button
                    onClick={() => { setSelectedPrograma(programa); setShowModal(true); }}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(programa.programa_id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <h3 className="font-bold text-gray-900 dark:text-white mb-1">{programa.nombre}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">{programa.codigo}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">{programa.nivel}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <GraduationCap className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>No hay programas registrados</p>
          <p className="text-sm mt-2">Haz clic en "Nuevo Programa" para comenzar</p>
        </div>
      )}

      {showModal && (
        <CrearProgramaModal
          institucionId={institucionId}
          programa={selectedPrograma}
          onClose={() => { setShowModal(false); setSelectedPrograma(null); }}
        />
      )}
    </div>
  );
}

function TabCursos({ institucionId }: { institucionId: string }) {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [selectedCurso, setSelectedCurso] = useState<Curso | null>(null);

  const { data: cursos, isLoading } = useQuery({
    queryKey: ['cursos', institucionId],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/cursos/mis-cursos', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data.data || [];
    },
    enabled: !!institucionId
  });

  const deleteMutation = useMutation({
    mutationFn: async (cursoId: string) => {
      const token = localStorage.getItem('access_token');
      await axios.delete(`http://localhost:8000/api/cursos/${cursoId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cursos'] });
      queryClient.invalidateQueries({ queryKey: ['estadisticas-institucion'] });
    }
  });

  if (isLoading) {
    return <div className="text-center py-12">Cargando cursos...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Cursos
        </h2>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          Nuevo Curso
        </button>
      </div>

      {cursos && cursos.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cursos.map((curso: Curso) => (
            <div key={curso.curso_id} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <BookOpen className="w-8 h-8 text-green-600" />
                <div className="flex gap-2">
                  <button
                    onClick={() => { setSelectedCurso(curso); setShowModal(true); }}
                    className="text-green-600 hover:text-green-700"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(curso.curso_id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <h3 className="font-bold text-gray-900 dark:text-white mb-1">{curso.nombre}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300 capitalize mb-2">{curso.modalidad}</p>
              {curso.codigo_acceso && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded px-2 py-1 mt-2">
                  <p className="text-xs text-gray-600 dark:text-gray-400">Código de acceso:</p>
                  <p className="text-sm font-mono font-bold text-blue-600 dark:text-blue-400">{curso.codigo_acceso}</p>
                </div>
              )}
              {curso.creditos && curso.creditos > 0 && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{curso.creditos} créditos</p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>No hay cursos registrados</p>
          <p className="text-sm mt-2">Haz clic en "Nuevo Curso" para comenzar</p>
        </div>
      )}

      {showModal && (
        <CrearCursoModal
          institucionId={institucionId}
          curso={selectedCurso || undefined}
          onClose={() => { setShowModal(false); setSelectedCurso(null); }}
        />
      )}
    </div>
  );
}

function TabClases({ institucionId }: { institucionId: string }) {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [selectedGrupo, setSelectedGrupo] = useState<Grupo | null>(null);

  const { data: grupos, isLoading } = useQuery({
    queryKey: ['grupos', institucionId],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/grupos/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    enabled: !!institucionId
  });

  const deleteMutation = useMutation({
    mutationFn: async (grupoId: string) => {
      const token = localStorage.getItem('access_token');
      await axios.delete(`http://localhost:8000/api/grupos/${grupoId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grupos'] });
      queryClient.invalidateQueries({ queryKey: ['estadisticas-institucion'] });
    }
  });

  if (isLoading) {
    return <div className="text-center py-12">Cargando clases...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Clases / Grupos
        </h2>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          Nueva Clase
        </button>
      </div>

      {grupos && grupos.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {grupos.map((grupo: Grupo) => (
            <div key={grupo.grupo_id} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <Users className="w-8 h-8 text-purple-600" />
                <div className="flex gap-2">
                  <button
                    onClick={() => { setSelectedGrupo(grupo); setShowModal(true); }}
                    className="text-purple-600 hover:text-purple-700"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(grupo.grupo_id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <h3 className="font-bold text-gray-900 dark:text-white mb-1">{grupo.nombre}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300 capitalize">{grupo.jornada.replace('_', ' ')}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <Users className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>No hay clases/grupos registrados</p>
          <p className="text-sm mt-2">Haz clic en "Nueva Clase" para comenzar</p>
        </div>
      )}

      {showModal && (
        <CrearClaseModal
          institucionId={institucionId}
          grupo={selectedGrupo || undefined}
          onClose={() => { setShowModal(false); setSelectedGrupo(null); }}
        />
      )}
    </div>
  );
}

function TabProfesores({ institucionId: _institucionId }: { institucionId: string }) {
  const [codigoGenerado, setCodigoGenerado] = useState<string | null>(null);
  const [copiado, setCopiado] = useState(false);

  const generarCodigoMutation = useMutation({
    mutationFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        'http://localhost:8000/api/cursos/inscripciones/generar-codigo-invitacion',
        { tipo_codigo: 'institucion', dias_validez: 30 },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      console.log('📝 Respuesta generar código (Profesores):', response.data);
      return response.data;
    },
    onSuccess: (data) => {
      console.log('✅ Código generado exitosamente:', data);
      // La respuesta viene en formato { success, message, data: { codigo, expira_en, dias_validez } }
      const codigo = data.data?.codigo || data.codigo;
      setCodigoGenerado(codigo);
    },
    onError: (error) => {
      console.error('❌ Error al generar código:', error);
      if (axios.isAxiosError(error)) {
        console.error('Detalles del error:', error.response?.data);
      }
    }
  });

  const copiarCodigo = () => {
    if (codigoGenerado) {
      navigator.clipboard.writeText(codigoGenerado);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Profesores
        </h2>
        <button
          onClick={() => generarCodigoMutation.mutate()}
          disabled={generarCodigoMutation.isPending}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          {generarCodigoMutation.isPending ? 'Generando...' : 'Generar Código de Invitación'}
        </button>
      </div>

      {generarCodigoMutation.isError && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200 text-sm">
            ❌ Error al generar código. {axios.isAxiosError(generarCodigoMutation.error) ? generarCodigoMutation.error.message : 'Por favor recarga la página e intenta de nuevo.'}
          </p>
        </div>
      )}

      {codigoGenerado && (
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 border-2 border-indigo-200 dark:border-indigo-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Código de Invitación para Profesores
            </h3>
            <button
              onClick={copiarCodigo}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors text-sm"
            >
              {copiado ? '✓ Copiado!' : 'Copiar Código'}
            </button>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border-2 border-dashed border-indigo-300 dark:border-indigo-700">
            <p className="text-3xl font-mono font-bold text-center text-indigo-600 dark:text-indigo-400 tracking-wider">
              {codigoGenerado}
            </p>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-3">
            💡 Comparte este código con los profesores para que se vinculen a la institución. El código es válido por 30 días.
          </p>
        </div>
      )}

      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
          📋 Instrucciones para Profesores
        </h3>
        <ol className="text-sm text-blue-800 dark:text-blue-200 space-y-1 list-decimal list-inside">
          <li>Genera un código de invitación usando el botón superior</li>
          <li>Comparte el código con los profesores que deseas invitar</li>
          <li>Los profesores deben registrarse en la plataforma usando el código</li>
          <li>Una vez registrados, quedarán vinculados automáticamente a la institución</li>
        </ol>
      </div>

      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-8 text-center">
        <Users className="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Sistema de Invitaciones
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Los profesores aparecerán aquí una vez se vinculen usando el código de invitación
        </p>
      </div>
    </div>
  );
}

function TabEstudiantes({ institucionId: _institucionId }: { institucionId: string }) {
  const [codigoGenerado, setCodigoGenerado] = useState<string | null>(null);
  const [copiado, setCopiado] = useState(false);

  const generarCodigoMutation = useMutation({
    mutationFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        'http://localhost:8000/api/cursos/inscripciones/generar-codigo-invitacion',
        { tipo_codigo: 'institucion', dias_validez: 30 },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      console.log('📝 Respuesta generar código (Estudiantes):', response.data);
      return response.data;
    },
    onSuccess: (data) => {
      console.log('✅ Código generado exitosamente:', data);
      // La respuesta viene en formato { success, message, data: { codigo, expira_en, dias_validez } }
      const codigo = data.data?.codigo || data.codigo;
      setCodigoGenerado(codigo);
    },
    onError: (error) => {
      console.error('❌ Error al generar código:', error);
      if (axios.isAxiosError(error)) {
        console.error('Detalles del error:', error.response?.data);
      }
    }
  });

  const copiarCodigo = () => {
    if (codigoGenerado) {
      navigator.clipboard.writeText(codigoGenerado);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Estudiantes
        </h2>
        <button
          onClick={() => generarCodigoMutation.mutate()}
          disabled={generarCodigoMutation.isPending}
          className="flex items-center gap-2 bg-orange-600 hover:bg-orange-700 disabled:bg-orange-400 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          {generarCodigoMutation.isPending ? 'Generando...' : 'Generar Código de Invitación'}
        </button>
      </div>

      {generarCodigoMutation.isError && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200 text-sm">
            ❌ Error al generar código. {axios.isAxiosError(generarCodigoMutation.error) ? generarCodigoMutation.error.message : 'Por favor recarga la página e intenta de nuevo.'}
          </p>
        </div>
      )}

      {codigoGenerado && (
        <div className="bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 border-2 border-orange-200 dark:border-orange-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Código de Invitación para Estudiantes
            </h3>
            <button
              onClick={copiarCodigo}
              className="flex items-center gap-2 bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg transition-colors text-sm"
            >
              {copiado ? '✓ Copiado!' : 'Copiar Código'}
            </button>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border-2 border-dashed border-orange-300 dark:border-orange-700">
            <p className="text-3xl font-mono font-bold text-center text-orange-600 dark:text-orange-400 tracking-wider">
              {codigoGenerado}
            </p>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-3">
            💡 Comparte este código con los estudiantes para que se vinculen a la institución. El código es válido por 30 días.
          </p>
        </div>
      )}

      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
          📋 Instrucciones para Estudiantes
        </h3>
        <ol className="text-sm text-blue-800 dark:text-blue-200 space-y-1 list-decimal list-inside">
          <li>Genera un código de invitación usando el botón superior</li>
          <li>Comparte el código con los estudiantes que deseas invitar</li>
          <li>Los estudiantes deben registrarse en la plataforma usando el código</li>
          <li>Una vez registrados, quedarán vinculados automáticamente a la institución</li>
          <li>Los estudiantes podrán inscribirse en cursos usando los códigos de acceso de cada curso</li>
        </ol>
      </div>

      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-8 text-center">
        <Users className="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Sistema de Invitaciones
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Los estudiantes aparecerán aquí una vez se vinculen usando el código de invitación
        </p>
      </div>
    </div>
  );
}

function TabEstadisticas({ estadisticas }: { estadisticas?: EstadisticasInstitucion }) {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
        Estadísticas de la Institución
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6">
          <p className="text-blue-600 dark:text-blue-400 text-sm font-medium">Total Programas</p>
          <p className="text-4xl font-bold text-blue-900 dark:text-blue-100 mt-2">
            {estadisticas?.total_programas || 0}
          </p>
        </div>

        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-6">
          <p className="text-green-600 dark:text-green-400 text-sm font-medium">Total Cursos</p>
          <p className="text-4xl font-bold text-green-900 dark:text-green-100 mt-2">
            {estadisticas?.total_cursos || 0}
          </p>
        </div>

        <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-6">
          <p className="text-purple-600 dark:text-purple-400 text-sm font-medium">Total Profesores</p>
          <p className="text-4xl font-bold text-purple-900 dark:text-purple-100 mt-2">
            {estadisticas?.total_profesores || 0}
          </p>
        </div>

        <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-6">
          <p className="text-orange-600 dark:text-orange-400 text-sm font-medium">Total Estudiantes</p>
          <p className="text-4xl font-bold text-orange-900 dark:text-orange-100 mt-2">
            {estadisticas?.total_estudiantes || 0}
          </p>
        </div>
      </div>

      <div className="mt-8">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Próximamente
        </h3>
        <ul className="space-y-2 text-gray-600 dark:text-gray-400">
          <li>• Gráficos de inscripciones por mes</li>
          <li>• Tasa de aprobación por programa</li>
          <li>• Cursos más populares</li>
          <li>• Promedio de calificaciones</li>
        </ul>
      </div>
    </div>
  );
}
