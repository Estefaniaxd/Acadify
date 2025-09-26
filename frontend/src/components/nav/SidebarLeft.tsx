import { useNavigate, useLocation } from 'react-router-dom';
import { useMemo, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiHome, FiBook, FiUsers, FiBarChart, FiUserCheck,
  FiPlus, FiShoppingBag, FiTarget, FiSettings, FiX,
  FiChevronRight, FiTrendingUp, FiClock, FiUser
} from 'react-icons/fi';
import { HiOutlineOfficeBuilding } from 'react-icons/hi';

// Mock data para diferentes roles
const mockClases = [
  {
    id: 1,
    name: 'Matemáticas Avanzadas',
    students: 28,
    progress: 75,
    color: 'from-blue-500 to-blue-600',
    lastAccessed: '2025-01-21T10:30:00Z'
  },
  {
    id: 2,
    name: 'Historia Universal',
    students: 22,
    progress: 60,
    color: 'from-green-500 to-green-600',
    lastAccessed: '2025-01-20T15:45:00Z'
  },
  {
    id: 3,
    name: 'Ciencias Naturales',
    students: 30,
    progress: 40,
    color: 'from-purple-500 to-purple-600',
    lastAccessed: '2025-01-20T09:15:00Z'
  }
];

const mockInstituciones = [
  {
    id: 1,
    name: 'Universidad Nacional',
    usuarios: 1250,
    estado: 'Activa',
    color: 'from-emerald-500 to-emerald-600',
    lastAccessed: '2025-01-21T09:00:00Z'
  },
  {
    id: 2,
    name: 'Colegio San Martín',
    usuarios: 450,
    estado: 'Activa',
    color: 'from-blue-500 to-blue-600',
    lastAccessed: '2025-01-20T16:30:00Z'
  }
];

const mockTareas = [
  {
    id: 1,
    name: 'Revisión Exámenes Matemáticas',
    clase: 'Matemáticas Avanzadas',
    pendientes: 12,
    color: 'from-red-500 to-red-600',
    lastAccessed: '2025-01-21T08:45:00Z'
  },
  {
    id: 2,
    name: 'Calificar Ensayos Literatura',
    clase: 'Literatura Española',
    pendientes: 8,
    color: 'from-orange-500 to-orange-600',
    lastAccessed: '2025-01-20T17:20:00Z'
  }
];

const getRecentItemsByRole = (role: string) => {
  switch (role) {
    case 'admin':
      return {
        title: 'Institución Reciente',
        items: mockInstituciones,
        icon: HiOutlineOfficeBuilding,
        routePrefix: '/admin/institucion'
      };
    case 'coordinador':
      return {
        title: 'Clase Reciente',
        items: mockClases,
        icon: FiBook,
        routePrefix: '/coordinador/clase'
      };
    case 'profesor':
      return {
        title: 'Tarea Reciente',
        items: mockTareas,
        icon: FiTarget,
        routePrefix: '/profesor/tarea'
      };
    case 'estudiante':
    default:
      return {
        title: 'Clase Reciente',
        items: mockClases,
        icon: FiBook,
        routePrefix: '/clase'
      };
  }
};

interface SidebarLeftProps {
  open: boolean;
  onClose: () => void;
  role: string;
}

export default function SidebarLeft({ open, onClose, role }: SidebarLeftProps) {
  const navigate = useNavigate();
  const location = useLocation();

  // Detectar modo oscuro igual que en Nav
  const [isDark, setIsDark] = useState(false);
  useEffect(() => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      const match = window.matchMedia('(prefers-color-scheme: dark)');
      setIsDark(match.matches);
      const handler = (e: MediaQueryListEvent) => setIsDark(e.matches);
      match.addEventListener('change', handler);
      return () => match.removeEventListener('change', handler);
    }
  }, []);

  // Configuración de menú por rol
  const getMenuItems = useMemo(() => {
    const baseItems = [
      { label: 'Dashboard', icon: FiHome, href: '/dashboard' }
    ];

    switch (role) {
      case 'admin':
        return [
          ...baseItems,
          { label: 'Panel Admin', icon: FiSettings, href: '/admin' },
          { label: 'Usuarios', icon: FiUsers, href: '/admin' },
          { label: 'Instituciones', icon: HiOutlineOfficeBuilding, href: '/admin' },
          { label: 'Editor de Avatar', icon: FiUser, href: '/avatar' },
        ];
      case 'coordinador':
        return [
          ...baseItems,
          { label: 'Panel Coordinador', icon: FiSettings, href: '/coordinador' },
          { label: 'Profesores', icon: FiUserCheck, href: '/coordinador' },
          { label: 'Clases', icon: FiBook, href: '/coordinador' },
          { label: 'Editor de Avatar', icon: FiUser, href: '/avatar' },
        ];
      case 'profesor':
        return [
          ...baseItems,
          { label: 'Panel Profesor', icon: FiSettings, href: '/profesor' },
          { label: 'Mis clases', icon: FiBook, href: '/mis-clases' },
          { label: 'Crear clase', icon: FiPlus, href: '/crear-clase' },
          { label: 'Editor de Avatar', icon: FiUser, href: '/avatar' },
        ];
      case 'estudiante':
      default:
        return [
          ...baseItems,
          { label: 'Mis clases', icon: FiBook, href: '/mis-clases' },
          { label: 'Unirse a clase', icon: FiPlus, href: '/unirse-clase' },
          { label: 'Logros', icon: FiTarget, href: '/logros' },
          { label: 'Tienda', icon: FiShoppingBag, href: '/tienda' },
          { label: 'Editor de Avatar', icon: FiUser, href: '/avatar' },
          { label: 'Explorar Avatares', icon: FiUsers, href: '/explorar-avatares' },
        ];
    }
  }, [role]);

  if (!open) return null;

  // Fondos igual que Nav
  const darkBg = 'rgba(24, 16, 48, 0.92)';
  // Fondo blanco puro y sólido para modo claro
  const lightBg = '#fff';
  const sidebarBg = isDark ? darkBg : '#fff';
  const borderColor = isDark
    ? '1px solid rgba(139, 92, 246, 0.35)'
    : '1px solid #e5e7eb';
  const boxShadow = isDark
    ? '8px 0 32px rgba(139, 92, 246, 0.18)'
    : '8px 0 32px rgba(139, 92, 246, 0.04)';

  return (
    <AnimatePresence>
      <motion.aside
        initial={{ x: '-100%', opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: '-100%', opacity: 0 }}
        transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}
  className="h-full w-64 md:w-80 flex flex-col overflow-hidden"
        style={{
          background: sidebarBg,
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderRight: borderColor,
          boxShadow: boxShadow
        }}
      >
        {/* Header del sidebar */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700"
        >
          <h2 className={`text-xl font-bold capitalize ${isDark ? 'text-gray-200' : 'text-gray-900'}`}> 
            Panel {role}
          </h2>
          <motion.button
            className={`p-2 rounded-xl bg-transparent transition-colors duration-200 ${isDark ? 'hover:bg-gray-800' : 'hover:bg-gray-100'}`}
            onClick={onClose}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FiX className="w-5 h-5" />
          </motion.button>
        </motion.div>

        {/* Contenido scrolleable */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          {/* Menú principal */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <h3 className={`text-lg font-bold mb-4 ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>Navegación</h3>
            <div className="space-y-2">
              {getMenuItems.map((item, idx) => {
                const active = location.pathname === item.href;
                const Icon = item.icon;
                return (
                  <motion.button
                    key={item.label}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 text-left ${
                      active
                        ? 'bg-gradient-to-r from-violet-500 to-purple-600 text-white shadow-lg'
                        : isDark
                          ? 'text-gray-300 hover:bg-violet-900/50 hover:text-violet-300'
                          : 'text-gray-800 hover:bg-violet-50 hover:text-violet-700'
                    }`}
                    onClick={() => {
                      navigate(item.href);
                      onClose();
                    }}
                    whileHover={{ x: active ? 0 : 4 }}
                    whileTap={{ scale: 0.95 }}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.05 * idx }}
                  >
                    <Icon className={`w-5 h-5 ${active ? 'text-white' : 'text-current'}`} />
                    <span className="font-medium">{item.label}</span>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>

          {/* Elemento más reciente según el rol */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            {(() => {
              const recentData = getRecentItemsByRole(role);
              const mostRecent = recentData.items.sort((a, b) => 
                new Date(b.lastAccessed).getTime() - new Date(a.lastAccessed).getTime()
              )[0];
              const RecentIcon = recentData.icon;
              
              return (
                <>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className={`text-lg font-bold flex items-center gap-2 ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>
                      <FiClock className="w-5 h-5 text-violet-600 dark:text-violet-400" />
                      {recentData.title}
                    </h3>
                  </div>
                  <motion.button
                    className={`group relative p-4 rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden w-full border ${isDark ? 'bg-gray-800/90 border-gray-700' : 'bg-white border-gray-200'}`}
                    onClick={() => { navigate(`${recentData.routePrefix}/${mostRecent.id}`); onClose(); }}
                    whileHover={{ y: -2, scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${mostRecent.color}`} />
                    
                    <div className="flex items-center justify-between">
                      <div className="flex-1 text-left">
                        <h4 className={`font-bold text-sm transition-colors duration-300 ${isDark ? 'text-gray-100 group-hover:text-violet-300' : 'text-gray-900 group-hover:text-violet-700'}`}> 
                          {mostRecent.name}
                        </h4>
                        <p className={`text-xs mt-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}> 
                          {role === 'admin' ? `${(mostRecent as any).usuarios} usuarios` :
                           role === 'profesor' ? `${(mostRecent as any).pendientes} pendientes` :
                           `${(mostRecent as any).students} estudiantes`}
                        </p>
                        <p className={`text-xs mt-1 font-medium ${isDark ? 'text-violet-400' : 'text-violet-600'}`}> 
                          Accedido hoy
                        </p>
                        {(role === 'estudiante' || role === 'coordinador') && (mostRecent as any).progress && (
                          <>
                            <div className={`mt-2 w-full rounded-full h-1.5 ${isDark ? 'bg-gray-700' : 'bg-gray-200'}`}> 
                              <motion.div 
                                className={`h-1.5 bg-gradient-to-r ${mostRecent.color} rounded-full`}
                                initial={{ width: 0 }}
                                animate={{ width: `${(mostRecent as any).progress}%` }}
                                transition={{ duration: 1, delay: 0.2 }}
                              />
                            </div>
                            <p className={`text-xs mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{(mostRecent as any).progress}% completado</p>
                          </>
                        )}
                        {role === 'admin' && (mostRecent as any).estado && (
                          <p className={`text-xs mt-1 font-medium ${
                            (mostRecent as any).estado === 'Activa'
                              ? (isDark ? 'text-green-400' : 'text-green-600')
                              : (isDark ? 'text-yellow-400' : 'text-yellow-600')
                          }`}>
                            {(mostRecent as any).estado}
                          </p>
                        )}
                      </div>
                      <motion.div
                        className={`w-12 h-12 rounded-xl bg-gradient-to-br ${mostRecent.color} flex items-center justify-center shadow-lg`}
                        whileHover={{ rotate: 10, scale: 1.1 }}
                      >
                        <RecentIcon className="w-5 h-5 text-white" />
                      </motion.div>
                    </div>
                  </motion.button>
                </>
              );
            })()}
          </motion.div>

          {/* Para estudiantes, mostrar accesos rápidos a clases */}
          {role === 'estudiante' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h3 className={`text-lg font-bold mb-4 ${isDark ? 'text-gray-200' : 'text-gray-900'}`}>Clases Activas</h3>
              <div className="space-y-2">
                {mockClases.slice(0, 3).map((clase, idx) => (
                  <motion.button
                    key={clase.id}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 text-left ${isDark ? 'text-gray-300 hover:bg-violet-900/50 hover:text-violet-300' : 'text-gray-800 hover:bg-violet-50 hover:text-violet-700'}`}
                    onClick={() => {
                      navigate(`/clase/${clase.id}`);
                      onClose();
                    }}
                    whileHover={{ x: 4 }}
                    whileTap={{ scale: 0.95 }}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.05 * idx }}
                  >
                    <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${clase.color}`} />
                    <span className="font-medium text-sm">{clase.name}</span>
                    <FiChevronRight className="w-4 h-4 ml-auto" />
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </motion.aside>
    </AnimatePresence>
  );
}
