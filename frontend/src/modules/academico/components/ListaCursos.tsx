import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
;
import { Card, CardHeader, CardContent } from '../../evaluaciones/components/common/LayoutComponents';
import { LoadingSpinner } from '../../evaluaciones/components/common/LoadingComponents';
import { Curso, EstadoCurso, FiltrosCurso } from '../types.js';
import { formatearFecha } from '../../evaluaciones/utils';
import courseService, { type Course } from '../services/courseService';
import { BookOpen, Calendar, Plus, Search } from 'lucide-react';

interface ListaCursosProps {
  onCursoSeleccionado?: (curso: Curso) => void;
  onCrearCurso?: () => void;
  className?: string;
}

const ListaCursos: React.FC<ListaCursosProps> = ({
  onCursoSeleccionado,
  onCrearCurso,
  className = ''
}) => {
  const [cursos, setCursos] = useState<Curso[]>([]);
  const [cursosAPI, setCursosAPI] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busqueda, setBusqueda] = useState('');
  const [filtros, setFiltros] = useState<FiltrosCurso>({});
  const [mostrarFiltros, setMostrarFiltros] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);

  useEffect(() => {
    cargarCursos();
  }, [filtros]);

  // Convertir Course de API a Curso del componente
  const convertirCourseACurso = (course: Course): Curso => ({
    curso_id: course.id,
    institucion_id: 'inst-1', // Por ahora hardcoded
    programa_id: 'prog-1', // Por ahora hardcoded
    nombre: course.nombre,
    descripcion: course.descripcion,
    codigo_curso: course.codigo,
    creditos: course.creditos,
    horas_academicas: course.horas_academicas,
    modalidad: 'SEMESTRAL' as any,
    categoria: 'General',
    nivel: 'Intermedio',
    idioma: 'Español',
    fecha_inicio: course.fecha_creacion,
    fecha_fin: new Date(new Date(course.fecha_creacion).getTime() + 120 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // +4 meses
    activo: course.activo,
    estado: course.estado === 'activo' ? EstadoCurso.ACTIVO : EstadoCurso.INACTIVO,
    permite_inscripcion: true,
    maximo_estudiantes: course.estudiantes + 10, // Asumimos capacidad +10
    minimo_estudiantes: 5,
    estudiantes_actuales: course.estudiantes,
    permite_material_estudiantes: true,
    requiere_aprobacion_material: false,
    fecha_creacion: course.fecha_creacion,
  });

  const cargarCursos = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔄 Cargando cursos desde API...');
      const response = await courseService.getCourses();
      
      if (response.success) {
        // API conectada exitosamente
        console.log('✅ Cursos cargados desde API:', response.data);
        setCursosAPI(response.data);
        const cursosConvertidos = response.data.map(convertirCourseACurso);
        setCursos(cursosConvertidos);
        setApiConnected(true);
      } else {
        // Usar fallback
        console.log('⚠️ Usando datos de fallback:', response.data);
        setCursosAPI(response.data);
        const cursosConvertidos = response.data.map(convertirCourseACurso);
        setCursos(cursosConvertidos);
        setApiConnected(false);
        setError(response.error || 'Error conectando a API');
      }
    } catch (err) {
      setError('Error al cargar los cursos');
      console.error('❌ Error:', err);
      
      // Fallback manual si todo falla
      const cursosFallback: Curso[] = [
        {
          curso_id: '1',
          institucion_id: 'inst-1',
          programa_id: 'prog-1',
          nombre: 'Matemáticas Avanzadas',
          descripcion: 'Curso de cálculo diferencial e integral',
          codigo_curso: 'MAT301',
          creditos: 4,
          horas_academicas: 64,
          modalidad: 'SEMESTRAL' as any,
          categoria: 'Matemáticas',
          nivel: 'Avanzado',
          idioma: 'Español',
          fecha_inicio: '2024-03-01',
          fecha_fin: '2024-07-01',
          activo: true,
          estado: EstadoCurso.ACTIVO,
          permite_inscripcion: true,
          maximo_estudiantes: 30,
          minimo_estudiantes: 10,
          estudiantes_actuales: 28,
          permite_material_estudiantes: true,
          requiere_aprobacion_material: false,
          fecha_creacion: '2024-02-01',
        }
      ];
      setCursos(cursosFallback);
    } finally {
      setLoading(false);
    }
  };

  const handleBuscar = () => {
    const nuevosFiltros = {
      ...filtros,
      nombre: busqueda || undefined
    };
    setFiltros(nuevosFiltros);
  };

  const getEstadoColor = (estado: EstadoCurso) => {
    switch (estado) {
      case EstadoCurso.ACTIVO:
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300';
      case EstadoCurso.INACTIVO:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300';
      case EstadoCurso.ARCHIVADO:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300';
      case EstadoCurso.BORRADOR:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const cursosFiltrados = cursos.filter(curso => {
    if (busqueda) {
      return curso.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
             (curso.codigo_curso || '').toLowerCase().includes(busqueda.toLowerCase());
    }
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <h3 className="text-lg font-medium text-red-900 dark:text-red-200 mb-2">Error</h3>
        <p className="text-red-700 dark:text-red-300">{error}</p>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Estado de conexión */}
      <div className={`p-3 rounded-lg text-sm ${
        apiConnected 
          ? 'bg-green-50 border border-green-200 text-green-700 dark:bg-green-900/20 dark:border-green-800 dark:text-green-300' 
          : 'bg-yellow-50 border border-yellow-200 text-yellow-700 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-300'
      }`}>
        {apiConnected ? (
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            ✅ Conectado a la base de datos - Mostrando datos reales
          </div>
        ) : (
          <div className="flex items-center">
            <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
            ⚠️ Usando datos de fallback - API no disponible
            {error && <span className="ml-2 text-xs">({error})</span>}
          </div>
        )}
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Mis Cursos {apiConnected && '(BD Real)'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Gestiona tus cursos académicos {apiConnected ? '- Datos desde base de datos' : '- Datos de ejemplo'}
          </p>
        </div>

        {onCrearCurso && (
          <button
            onClick={onCrearCurso}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            <Plus className="h-5 w-5" />
            <span>Nuevo Curso</span>
          </button>
        )}
      </div>

      {/* Filtros y búsqueda */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <input
            type="text"
            placeholder="Buscar cursos..."
            value={busqueda}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setBusqueda(e.target.value)}
            onKeyPress={(e: React.KeyboardEvent) => e.key === 'Enter' && handleBuscar()}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
        
        <button
          onClick={() => setMostrarFiltros(!mostrarFiltros)}
          className="flex items-center space-x-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <FunnelIcon className="h-5 w-5" />
          <span>Filtros</span>
        </button>
      </div>

      {/* Panel de filtros */}
      {mostrarFiltros && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-4"
        >
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Estado
              </label>
              <select className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="">Todos</option>
                <option value="activo">Activo</option>
                <option value="inactivo">Inactivo</option>
                <option value="archivado">Archivado</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Modalidad
              </label>
              <select className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="">Todas</option>
                <option value="semestral">Semestral</option>
                <option value="anual">Anual</option>
                <option value="trimestral">Trimestral</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nivel
              </label>
              <select className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="">Todos</option>
                <option value="básico">Básico</option>
                <option value="intermedio">Intermedio</option>
                <option value="avanzado">Avanzado</option>
              </select>
            </div>
          </div>
        </motion.div>
      )}

      {/* Lista de cursos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cursosFiltrados.map((curso) => (
          <motion.div
            key={curso.curso_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -2 }}
            className="cursor-pointer"
            onClick={() => onCursoSeleccionado?.(curso)}
          >
            <Card className="h-full hover:shadow-lg transition-shadow">
              <CardHeader 
                title={curso.nombre}
                actions={
                  <div className="flex items-center space-x-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getEstadoColor(curso.estado!)}`}>
                      {curso.estado}
                    </span>
                    <button className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                      <EllipsisVerticalIcon className="h-5 w-5 text-gray-400" />
                    </button>
                  </div>
                }
              />

              <CardContent>
                <div className="space-y-4">
                  <p className="text-gray-600 dark:text-gray-300 text-sm line-clamp-2">
                    {curso.descripcion || 'Sin descripción disponible'}
                  </p>

                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <BookOpen className="h-4 w-4 mr-2" />
                      <span>{curso.codigo_curso}</span>
                    </div>
                    
                    <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <UsersIcon className="h-4 w-4 mr-2" />
                      <span>{curso.estudiantes_actuales} / {curso.maximo_estudiantes} estudiantes</span>
                    </div>
                    
                    {curso.fecha_inicio && (
                      <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <Calendar className="h-4 w-4 mr-2" />
                        <span>Inicia: {formatearFecha(curso.fecha_inicio)}</span>
                      </div>
                    )}
                  </div>

                  <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500 dark:text-gray-400">
                        {curso.creditos} créditos
                      </span>
                      <span className="text-gray-500 dark:text-gray-400">
                        {curso.horas_academicas}h académicas
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Estado vacío */}
      {cursosFiltrados.length === 0 && (
        <div className="text-center py-12">
          <BookOpen className="h-16 w-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No hay cursos disponibles
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {busqueda ? 'No se encontraron cursos que coincidan con la búsqueda' : 'Aún no tienes cursos creados'}
          </p>
        </div>
      )}
    </div>
  );
};

export default ListaCursos;