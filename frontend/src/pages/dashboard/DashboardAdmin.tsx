import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  Award,
  BarChart,
  Building2,
  CheckCircle,
  Loader,
  Monitor,
  MoreVertical,
  Plus,
  Settings,
  Shield,
  ShoppingBag,
  TrendingUp,
  Users,
} from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useAdminStats, useSystemAlerts } from "../../hooks/useAdminData";

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<"overview" | "users" | "institutions" | "system">(
    "overview"
  );

  // 🔥 DATOS REALES desde API
  const { data: stats, isLoading: loadingStats } = useAdminStats();
  const { data: alerts = [], isLoading: loadingAlerts } = useSystemAlerts();

  return (
    <div className="bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 mt-6">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-pink-600 rounded-xl flex items-center justify-center">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    Panel de Administrador
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    ¡Hola, {user?.username || "Admin"}!
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1 overflow-x-auto">
                {[
                  { key: "overview", label: "Resumen", icon: TrendingUp },
                  { key: "institutions", label: "Instituciones", icon: Building2 },
                  { key: "users", label: "Usuarios", icon: Users },
                  { key: "system", label: "Sistema", icon: Monitor },
                ].map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key as "overview" | "users" | "institutions" | "system")}
                    className={`
                      flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 whitespace-nowrap
                      ${
                        activeTab === tab.key
                          ? "bg-white dark:bg-gray-700 text-red-600 dark:text-red-400 shadow-sm"
                          : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                      }
                    `}
                  >
                    <tab.icon className="w-4 h-4" />
                    <span className="hidden sm:block">{tab.label}</span>
                  </button>
                ))}
              </div>

              <button
                onClick={logout}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
              >
                Salir
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Loading state */}
        {loadingStats && (
          <div className="flex items-center justify-center py-12">
            <Loader className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-3 text-gray-600 dark:text-gray-400">Cargando estadísticas...</span>
          </div>
        )}

        {/* Content tabs */}
        {!loadingStats && stats && (
          <AnimatePresence mode="wait">
            {activeTab === "overview" && (
              <motion.div
                key="overview"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-8"
              >
                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  {[
                    {
                      label: "Total Usuarios",
                      value: stats.totalUsers.toLocaleString(),
                      icon: Users,
                      color: "from-blue-500 to-indigo-600",
                    },
                    {
                      label: "Instituciones",
                      value: stats.totalInstitutions.toString(),
                      icon: Building2,
                      color: "from-emerald-500 to-teal-600",
                    },
                    {
                      label: "Coordinadores Activos",
                      value: stats.activeCoordinators.toString(),
                      icon: Settings,
                      color: "from-purple-500 to-pink-600",
                    },
                    {
                      label: "Tiempo Activo Sistema",
                      value: stats.systemUptime,
                      icon: Activity,
                      color: "from-orange-500 to-red-600",
                    },
                  ].map((stat, index) => (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1, duration: 0.3 }}
                    className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                          {stat.label}
                        </p>
                        <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                          {stat.value}
                        </p>
                      </div>
                      <div
                        className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-xl flex items-center justify-center`}
                      >
                        <stat.icon className="w-6 h-6 text-white" />
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* System Alerts */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Alertas del Sistema
                </h3>
                {loadingAlerts && (
                  <div className="flex items-center justify-center py-4">
                    <Loader className="w-5 h-5 animate-spin text-blue-600" />
                    <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Cargando alertas...</span>
                  </div>
                )}
                {!loadingAlerts && alerts.length === 0 && (
                  <p className="text-center text-gray-500 dark:text-gray-400 py-4">
                    ✅ No hay alertas activas. Todo funciona correctamente.
                  </p>
                )}
                {!loadingAlerts && alerts.length > 0 && (
                  <div className="space-y-3">
                    {alerts.map((alert) => (
                    <div
                      key={alert.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50"
                    >
                      <div className="flex items-center space-x-3">
                        {alert.type === "warning" && (
                          <AlertTriangle className="w-5 h-5 text-orange-500" />
                        )}
                        {alert.type === "error" && (
                          <AlertTriangle className="w-5 h-5 text-red-500" />
                        )}
                        {alert.type === "info" && <CheckCircle className="w-5 h-5 text-blue-500" />}
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {alert.message}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            Hace {alert.timestamp}
                          </p>
                        </div>
                      </div>
                      <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                  </div>
                )}
              </div>

              {/* Quick Actions - Admin Panel */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* BOTÓN DESTACADO: CREAR INSTITUCIÓN */}
                <button
                  onClick={() => navigate("/admin/instituciones")}
                  className="relative bg-gradient-to-r from-red-500 to-pink-600 text-white p-6 rounded-2xl hover:shadow-2xl hover:scale-105 transition-all duration-300 text-left overflow-hidden group"
                >
                  <div className="absolute -top-8 -right-8 w-32 h-32 bg-white/10 rounded-full blur-2xl group-hover:scale-150 transition-transform"></div>
                  <Building2 className="w-8 h-8 mb-3 relative z-10" />
                  <h3 className="text-lg font-bold mb-2 relative z-10">🏛️ Gestionar Instituciones</h3>
                  <p className="text-red-100 text-sm relative z-10">Ver y administrar todas las instituciones</p>
                  <div className="absolute bottom-2 right-2">
                    <Plus className="w-6 h-6 text-white/30" />
                  </div>
                </button>

                <button
                  onClick={() => navigate("/admin/usuarios-pendientes")}
                  className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-6 rounded-2xl hover:shadow-xl hover:scale-105 transition-all duration-300 text-left"
                >
                  <Users className="w-8 h-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">Usuarios Pendientes</h3>
                  <p className="text-blue-100 text-sm">Aprobar solicitudes de acceso</p>
                  {stats && stats.pendingApprovals > 0 && (
                    <div className="absolute top-3 right-3 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full">
                      {stats.pendingApprovals}
                    </div>
                  )}
                </button>

                <button
                  onClick={() => navigate("/admin/reportes")}
                  className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white p-6 rounded-2xl hover:shadow-xl hover:scale-105 transition-all duration-300 text-left"
                >
                  <BarChart className="w-8 h-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">Reportes y Análisis</h3>
                  <p className="text-emerald-100 text-sm">Estadísticas y métricas del sistema</p>
                </button>

                <button
                  onClick={() => navigate("/admin/tienda")}
                  className="relative bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-6 rounded-2xl hover:shadow-xl hover:scale-105 transition-all duration-300 text-left overflow-hidden group"
                >
                  <ShoppingBag className="w-8 h-8 mb-3 relative z-10" />
                  <h3 className="text-lg font-bold mb-2 relative z-10">🛒 Gestionar Tienda</h3>
                  <p className="text-purple-100 text-sm relative z-10">Productos, categorías y premios</p>
                  <div className="absolute bottom-2 right-2">
                    <Plus className="w-6 h-6 text-white/30" />
                  </div>
                </button>

                <button
                  onClick={() => navigate("/admin/logros")}
                  className="relative bg-gradient-to-r from-amber-500 to-orange-600 text-white p-6 rounded-2xl hover:shadow-xl hover:scale-105 transition-all duration-300 text-left overflow-hidden group"
                >
                  <Award className="w-8 h-8 mb-3 relative z-10" />
                  <h3 className="text-lg font-bold mb-2 relative z-10">🏆 Gestionar Logros</h3>
                  <p className="text-amber-100 text-sm relative z-10">Insignias y medallas del sistema</p>
                  <div className="absolute bottom-2 right-2">
                    <Plus className="w-6 h-6 text-white/30" />
                  </div>
                </button>

                <button
                  onClick={() => navigate("/admin/configuracion")}
                  className="bg-gradient-to-r from-gray-600 to-gray-700 text-white p-6 rounded-2xl hover:shadow-xl hover:scale-105 transition-all duration-300 text-left"
                >
                  <Settings className="w-8 h-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">Configuración</h3>
                  <p className="text-gray-200 text-sm">Ajustes del sistema</p>
                </button>
              </div>
              </motion.div>
            )}

          {activeTab === "users" && (
            <motion.div
              key="users"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Gestión de Usuarios
                </h2>
                <button
                  onClick={() => navigate("/admin/usuarios-pendientes")}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors"
                >
                  <Users className="w-4 h-4" />
                  <span>Ver Usuarios Pendientes</span>
                </button>
              </div>

              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Administra usuarios, coordinadores y permisos desde la sección de usuarios pendientes.
                </p>
                <button
                  onClick={() => navigate("/admin/usuarios-pendientes")}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Ir a Usuarios Pendientes
                </button>
              </div>
            </motion.div>
          )}

          {activeTab === "institutions" && (
            <motion.div
              key="institutions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Instituciones</h2>
                <button
                  onClick={() => navigate("/admin/instituciones")}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors"
                >
                  <Building2 className="w-4 h-4" />
                  <span>Gestionar Instituciones</span>
                </button>
              </div>

              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Gestiona instituciones educativas, crea nuevas, edita información y administra sus configuraciones.
                </p>
                <button
                  onClick={() => navigate("/admin/instituciones")}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Ir a Instituciones
                </button>
              </div>
            </motion.div>
          )}

          {activeTab === "system" && (
            <motion.div
              key="system"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Estado del Sistema
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Estado de Servicios
                  </h3>
                  <div className="space-y-3">
                    {[
                      { name: "Servidor Web", status: "online" },
                      { name: "Base de Datos", status: "online" },
                      { name: "Sistema de Archivos", status: "online" },
                      { name: "WebSockets", status: "online" },
                    ].map((service) => (
                      <div key={service.name} className="flex items-center justify-between">
                        <span className="text-gray-700 dark:text-gray-300">{service.name}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span className="text-sm text-green-600 dark:text-green-400">
                            En línea
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Métricas del Sistema
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-700 dark:text-gray-300">Uso de CPU</span>
                      <span className="text-sm font-medium">12%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700 dark:text-gray-300">Uso de Memoria</span>
                      <span className="text-sm font-medium">34%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700 dark:text-gray-300">Espacio en Disco</span>
                      <span className="text-sm font-medium">67%</span>
                    </div>
                  </div>
                </div>
              </div>
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
