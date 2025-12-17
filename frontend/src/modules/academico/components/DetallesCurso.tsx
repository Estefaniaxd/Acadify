import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Curso, EstadoCurso, ConfiguracionCurso } from '../types.js';
import GestorMaterial from '../material/GestorMaterial';
import { apiClientTareas } from '../../tareas/api';

interface DetallesCursoProps {
  cursoId?: string;
}

const DetallesCurso: React.FC<DetallesCursoProps> = ({ cursoId: propCursoId }) => {
  const { cursoId: paramCursoId } = useParams<{ cursoId: string }>();
  const navigate = useNavigate();
  const cursoId = propCursoId || paramCursoId;

  const [curso, setCurso] = useState<Curso | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'informacion' | 'material' | 'tareas' | 'estadisticas' | 'configuracion'>('informacion');
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    if (cursoId) {
      cargarCurso();
    }
  }, [cursoId]);

  const cargarCurso = async () => {
    try {
      setLoading(true);
      setError(null);

      // Simular llamada a API
      const cursoSimulado: Curso = {
        curso_id: cursoId || '1',
        institucion_id: 'inst-1',
        programa_id: 'prog-1',
        nombre: 'Matemáticas Avanzadas',
        descripcion: 'Curso completo de matemáticas para estudiantes universitarios. Incluye álgebra lineal, cálculo diferencial e integral, y análisis matemático.',
        codigo_curso: 'MATH-401',
        codigo: 'MATH-401',
        categoria: 'Matemáticas',
        nivel: 'Avanzado',
        duracion_estimada: 120,
        creditos: 4,
        horas_academicas: 120,
        modalidad: 'semestral' as any,
        idioma: 'Español',
        activo: true,
        estado: EstadoCurso.ACTIVO,
        permite_inscripcion: true,
        fecha_inicio: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        fecha_fin: new Date(Date.now() + 120 * 24 * 60 * 60 * 1000).toISOString(),
        maximo_estudiantes: 30,
        minimo_estudiantes: 5,
        estudiantes_actuales: 18,
        permite_material_estudiantes: true,
        requiere_aprobacion_material: false,
        configuracion: {
          permite_auto_inscripcion: true,
          requiere_aprobacion: false,
          es_publico: true,
          permite_invitados: false,
          notificar_nuevos_materiales: true,
          notificar_nuevas_clases: true,
        } as ConfiguracionCurso,
        fecha_creacion: new Date().toISOString(),
      };

      setCurso(cursoSimulado);
    } catch (err) {
      setError('Error al cargar el curso');
      console.error('Error cargando curso:', err);
    } finally {
      setLoading(false);
    }
  };

  const getEstadoColor = (estado?: EstadoCurso) => {
    if (!estado) return 'bg-gray-100 text-gray-800';
    const colores = {
      [EstadoCurso.ACTIVO]: 'bg-green-100 text-green-800',
      [EstadoCurso.INACTIVO]: 'bg-gray-100 text-gray-800',
      [EstadoCurso.ARCHIVADO]: 'bg-yellow-100 text-yellow-800',
      [EstadoCurso.BORRADOR]: 'bg-blue-100 text-blue-800',
    };
    return colores[estado] || 'bg-gray-100 text-gray-800';
  };

  const formatearFecha = (fecha?: string) => {
    if (!fecha) return 'No definida';
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const calcularProgreso = () => {
    if (!curso?.fecha_inicio || !curso?.fecha_fin) return 0;

    const inicio = new Date(curso.fecha_inicio);
    const fin = new Date(curso.fecha_fin);
    const ahora = new Date();

    if (ahora < inicio) return 0;
    if (ahora > fin) return 100;

    const total = fin.getTime() - inicio.getTime();
    const transcurrido = ahora.getTime() - inicio.getTime();

    return Math.round((transcurrido / total) * 100);
  };

  // Handler para exportar reporte CSV
  const handleExportCSV = async () => {
    if (!cursoId) {
      alert("No se puede exportar: ID de curso no disponible");
      return;
    }

    setIsExporting(true);

    try {
      const blob = await apiClientTareas.exportarReporteCurso(cursoId);

      // Crear URL y descargar
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      const timestamp = new Date().toISOString().slice(0, 10);
      link.download = `reporte_curso_${cursoId}_${timestamp}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      alert("✅ Reporte descargado exitosamente");
    } catch (error) {
      console.error("Error exportando reporte:", error);
      alert("❌ Error al exportar el reporte. Por favor intente nuevamente.");
    } finally {
      setIsExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !curso) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 15.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {error || 'Curso no encontrado'}
        </h3>
        <button
          onClick={() => navigate('/cursos')}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Volver a Cursos
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header del curso */}
      <div className="bg-white rounded-lg border shadow-sm">
        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-gray-900">{curso.nombre}</h1>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getEstadoColor(curso.estado)}`}>
                  {curso.estado}
                </span>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                <span>📚 {curso.codigo}</span>
                <span>🎓 {curso.categoria}</span>
                <span>📊 {curso.nivel}</span>
                <span>⏰ {curso.duracion_estimada} horas</span>
                <span>🏆 {curso.creditos} créditos</span>
              </div>
              {curso.descripcion && (
                <p className="text-gray-700 leading-relaxed">{curso.descripcion}</p>
              )}
            </div>
            <div className="ml-6 text-right">
              <div className="text-sm text-gray-600 mb-2">
                {curso.estudiantes_actuales || 0} / {curso.maximo_estudiantes || 0} estudiantes
              </div>
              <div className="w-32 bg-gray-200 rounded-full h-2 mb-3">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{
                    width: `${curso.estudiantes_actuales && curso.maximo_estudiantes
                        ? (curso.estudiantes_actuales / curso.maximo_estudiantes) * 100
                        : 0
                      }%`
                  }}
                ></div>
              </div>
            </div>
          </div>

          {/* Información de fechas y progreso */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
            <div>
              <div className="text-sm font-medium text-gray-700 mb-1">Fecha de inicio</div>
              <div className="text-gray-900">{formatearFecha(curso.fecha_inicio)}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-700 mb-1">Fecha de fin</div>
              <div className="text-gray-900">{formatearFecha(curso.fecha_fin)}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-700 mb-1">Progreso del curso</div>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${calcularProgreso()}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-gray-900">{calcularProgreso()}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navegación de pestañas */}
      <div className="bg-white rounded-lg border shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'informacion', label: 'Información', icon: 'ℹ️' },
              { id: 'material', label: 'Material', icon: '📚' },
              { id: 'tareas', label: 'Tareas', icon: '📝' },
              { id: 'estadisticas', label: 'Estadísticas', icon: '📊' },
              { id: 'configuracion', label: 'Configuración', icon: '⚙️' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 py-4 px-1 border-b-2 text-sm font-medium transition-colors ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Contenido de las pestañas */}
        <div className="p-6">
          {activeTab === 'informacion' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Información general */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Información General</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Idioma:</span>
                      <span className="text-sm font-medium text-gray-900">{curso.idioma}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Duración:</span>
                      <span className="text-sm font-medium text-gray-900">{curso.duracion_estimada} horas</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Créditos:</span>
                      <span className="text-sm font-medium text-gray-900">{curso.creditos}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Nivel:</span>
                      <span className="text-sm font-medium text-gray-900">{curso.nivel}</span>
                    </div>
                  </div>
                </div>

                {/* Configuración */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuración</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Auto-inscripción:</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${curso.configuracion?.permite_auto_inscripcion
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                        }`}>
                        {curso.configuracion?.permite_auto_inscripcion ? 'Habilitada' : 'Deshabilitada'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Requiere aprobación:</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${curso.configuracion?.requiere_aprobacion
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                        }`}>
                        {curso.configuracion?.requiere_aprobacion ? 'Sí' : 'No'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Curso público:</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${curso.configuracion?.es_publico
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                        }`}>
                        {curso.configuracion?.es_publico ? 'Público' : 'Privado'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Estadísticas rápidas */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Estadísticas</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: 'Estudiantes', value: curso.estudiantes_actuales, icon: '👥' },
                    { label: 'Grupos', value: '3', icon: '📚' },
                    { label: 'Clases', value: '24', icon: '🏫' },
                    { label: 'Materiales', value: '156', icon: '📄' },
                  ].map((stat, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-4 text-center">
                      <div className="text-2xl mb-2">{stat.icon}</div>
                      <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                      <div className="text-sm text-gray-600">{stat.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'material' && (
            <GestorMaterial />
          )}

          {activeTab === 'tareas' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">Tareas del Curso</h3>
                <button
                  onClick={handleExportCSV}
                  disabled={isExporting}
                  className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white rounded-lg font-semibold transition-colors shadow-lg"
                >
                  {isExporting ? (
                    <>
                      <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Exportando...
                    </>
                  ) : (
                    <>
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Exportar Reporte CSV
                    </>
                  )}
                </button>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800">
                      Reporte de Tareas
                    </h3>
                    <div className="mt-2 text-sm text-blue-700">
                      <p>El reporte CSV incluye: información del curso, lista de estudiantes, todas las tareas, calificaciones, y métricas (promedio, % entregas). Los estudiantes sin entrega aparecen como "No entregó".</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'estadisticas' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Estadísticas Detalladas</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Actividad reciente */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h4 className="font-semibold text-gray-900 mb-4">📈 Actividad Reciente</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Nuevos estudiantes (7d)</span>
                      <span className="font-medium text-green-600">+5</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Material subido (7d)</span>
                      <span className="font-medium text-blue-600">8</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Clases realizadas (7d)</span>
                      <span className="font-medium text-purple-600">3</span>
                    </div>
                  </div>
                </div>

                {/* Descargas */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h4 className="font-semibold text-gray-900 mb-4">📥 Descargas</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Total descargas</span>
                      <span className="font-medium text-gray-900">1,234</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Esta semana</span>
                      <span className="font-medium text-gray-900">89</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Material más popular</span>
                      <span className="font-medium text-gray-900 text-xs truncate">Guía de Álgebra</span>
                    </div>
                  </div>
                </div>

                {/* Participación */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h4 className="font-semibold text-gray-900 mb-4">📊 Participación</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Asistencia promedio</span>
                      <span className="font-medium text-green-600">85%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Estudiantes activos</span>
                      <span className="font-medium text-gray-900">16/18</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Tareas entregadas</span>
                      <span className="font-medium text-blue-600">92%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'configuracion' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Configuración del Curso</h3>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">
                      Configuración avanzada
                    </h3>
                    <div className="mt-2 text-sm text-yellow-700">
                      <p>Esta sección está en desarrollo. Pronto podrás modificar la configuración del curso desde aquí.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DetallesCurso;