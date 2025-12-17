import { useAuth } from "../../context/AuthContext";
import { useEffect, useState } from "react";
import { Building2, Users, BookOpen, GraduationCap, TrendingUp, AlertCircle } from "lucide-react";
import axios from "axios";

interface CoordinadorStats {
  institucion_nombre: string;
  total_programas: number;
  total_cursos: number;
  total_docentes: number;
  total_estudiantes: number;
  cursos_activos: number;
  estudiantes_activos_mes: number;
  tareas_pendiente_revision: number;
}

export function DashboardCoordinador() {
  const { user } = useAuth();
  const [stats, setStats] = useState<CoordinadorStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('access_token');
        const response = await axios.get('/api/v1/coordinador/dashboard-stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setStats(response.data);
      } catch (err: any) {
        console.error('Error al cargar estadísticas:', err);
        // Si falla, usar datos de ejemplo
        setStats({
          institucion_nombre: 'Sin institución asignada',
          total_programas: 0,
          total_cursos: 0,
          total_docentes: 0,
          total_estudiantes: 0,
          cursos_activos: 0,
          estudiantes_activos_mes: 0,
          tareas_pendiente_revision: 0
        });
        setError('No se pudieron cargar las estadísticas');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchStats();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Cargando estadísticas...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Dashboard Coordinador
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Bienvenido, {user?.username || "Coordinador"}
          </p>
          {stats && (
            <p className="text-lg font-semibold text-blue-600 dark:text-blue-400 mt-2 flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              {stats.institucion_nombre}
            </p>
          )}
        </div>

        {/* Alert de error si existe */}
        {error && (
          <div className="mb-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-yellow-800 dark:text-yellow-200 font-semibold">Atención</p>
              <p className="text-yellow-700 dark:text-yellow-300 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Stats Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Programas */}
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <BookOpen className="w-10 h-10 opacity-80" />
              <TrendingUp className="w-6 h-6 opacity-60" />
            </div>
            <h3 className="text-sm font-medium opacity-90 mb-1">Programas Académicos</h3>
            <p className="text-4xl font-bold">{stats?.total_programas || 0}</p>
          </div>

          {/* Cursos */}
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <GraduationCap className="w-10 h-10 opacity-80" />
              <div className="text-right">
                <p className="text-xs opacity-75">{stats?.cursos_activos || 0} activos</p>
              </div>
            </div>
            <h3 className="text-sm font-medium opacity-90 mb-1">Total Cursos</h3>
            <p className="text-4xl font-bold">{stats?.total_cursos || 0}</p>
          </div>

          {/* Docentes */}
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <Users className="w-10 h-10 opacity-80" />
            </div>
            <h3 className="text-sm font-medium opacity-90 mb-1">Docentes</h3>
            <p className="text-4xl font-bold">{stats?.total_docentes || 0}</p>
          </div>

          {/* Estudiantes */}
          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <Users className="w-10 h-10 opacity-80" />
              <div className="text-right">
                <p className="text-xs opacity-75">{stats?.estudiantes_activos_mes || 0} activos/mes</p>
              </div>
            </div>
            <h3 className="text-sm font-medium opacity-90 mb-1">Estudiantes</h3>
            <p className="text-4xl font-bold">{stats?.total_estudiantes || 0}</p>
          </div>
        </div>

        {/* Sección de métricas adicionales */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Actividad reciente */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              Actividad Reciente
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-3 border-b border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-400">Estudiantes activos (30 días)</span>
                <span className="text-2xl font-bold text-blue-600">
                  {stats?.estudiantes_activos_mes || 0}
                </span>
              </div>
              <div className="flex justify-between items-center pb-3 border-b border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-400">Cursos activos</span>
                <span className="text-2xl font-bold text-green-600">
                  {stats?.cursos_activos || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">Tareas pendientes de revisión</span>
                <span className="text-2xl font-bold text-orange-600">
                  {stats?.tareas_pendiente_revision || 0}
                </span>
              </div>
            </div>
          </div>

          {/* Acciones rápidas */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Acciones Rápidas
            </h3>
            <div className="grid grid-cols-1 gap-3">
              <a
                href="/coordinador/institucion"
                className="px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 text-center font-medium"
              >
                Gestionar Institución
              </a>
              <a
                href="/cursos"
                className="px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors duration-200 text-center font-medium"
              >
                Ver Cursos
              </a>
              <a
                href="/comunicacion"
                className="px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors duration-200 text-center font-medium"
              >
                Mensajes
              </a>
            </div>
          </div>
        </div>

        {/* Nota informativa si no hay institución */}
        {stats && stats.institucion_nombre === 'Sin institución asignada' && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
            <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
              Institución no asignada
            </h4>
            <p className="text-blue-700 dark:text-blue-300 text-sm">
              Actualmente no tienes una institución asignada. Contacta al administrador del sistema para que te asigne a una institución educativa.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardCoordinador;
