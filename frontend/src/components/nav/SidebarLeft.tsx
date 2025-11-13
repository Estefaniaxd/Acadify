import { useNavigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Book, Building2, ChevronDown, ChevronRight, Clock, Target, X } from 'lucide-react';
import { 
  getNavigationBySection, 
  SECTION_NAMES,
  type UserRole 
} from '../../config/navigation';

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
        icon: Building2,
        routePrefix: '/admin/institucion'
      };
    case 'coordinador':
      return {
        title: 'Clase Reciente',
        items: mockClases,
        icon: Book,
        routePrefix: '/coordinador/clase'
      };
    case 'profesor':
    case 'docente':
      return {
        title: 'Tarea Reciente',
        items: mockTareas,
        icon: Target,
        routePrefix: '/profesor/tarea'
      };
    case 'estudiante':
    default:
      return {
        title: 'Clase Reciente',
        items: mockClases,
        icon: Book,
        routePrefix: '/clase'
      };
  }
};

interface SidebarLeftProps {
  open: boolean;
  onClose: () => void;
  role: string;
}

export default function SidebarLeft({ open, onClose, role }: Readonly<SidebarLeftProps>) {
  const navigate = useNavigate();
  const location = useLocation();
  const [expandedSections, setExpandedSections] = useState<string[]>(['main', 'academic']);

  // Detectar modo oscuro igual que en Nav
  const [isDark, setIsDark] = useState(false);
  useEffect(() => {
    const match = globalThis.window?.matchMedia?.('(prefers-color-scheme: dark)');
    if (match) {
      setIsDark(match.matches);
      const handler = (e: MediaQueryListEvent) => setIsDark(e.matches);
      match.addEventListener('change', handler);
      return () => match.removeEventListener('change', handler);
    }
  }, []);

  // Obtener navegación por sección
  const navigationSections = getNavigationBySection(role as UserRole);

  // Toggle de secciones
  const toggleSection = (section: string) => {
    setExpandedSections(prev =>
      prev.includes(section)
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  if (!open) return null;

  // Fondos igual que Nav
  const darkBg = 'rgba(24, 16, 48, 0.92)';
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
            <X className="w-5 h-5" />
          </motion.button>
        </motion.div>

        {/* Contenido scrolleable */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Navegación por secciones */}
          {Object.entries(navigationSections).map(([section, items], sectionIdx) => {
            const isExpanded = expandedSections.includes(section);
            const sectionName = SECTION_NAMES[section] || section;

            return (
              <motion.div
                key={section}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * sectionIdx }}
              >
                {/* Header de sección (colapsable) */}
                <motion.button
                  className={`w-full flex items-center justify-between mb-3 px-2 py-1 rounded-lg transition-colors ${
                    isDark ? 'hover:bg-gray-800' : 'hover:bg-gray-100'
                  }`}
                  onClick={() => toggleSection(section)}
                  whileHover={{ x: 2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <h3 className={`text-sm font-bold uppercase tracking-wide ${
                    isDark ? 'text-gray-400' : 'text-gray-600'
                  }`}>
                    {sectionName}
                  </h3>
                  <motion.div
                    animate={{ rotate: isExpanded ? 0 : -90 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ChevronDown className={`w-4 h-4 ${
                      isDark ? 'text-gray-400' : 'text-gray-600'
                    }`} />
                  </motion.div>
                </motion.button>

                {/* Items de la sección */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-1 overflow-hidden"
                    >
                      {items.map((item, idx) => {
                        const active = location.pathname === item.href;
                        const Icon = item.icon;
                        
                        const inactiveClasses = isDark
                          ? 'text-gray-300 hover:bg-violet-900/50 hover:text-violet-300'
                          : 'text-gray-800 hover:bg-violet-50 hover:text-violet-700';
                        const buttonClasses = active
                          ? 'bg-gradient-to-r from-violet-500 to-purple-600 text-white shadow-lg'
                          : inactiveClasses;
                        
                        return (
                          <motion.button
                            key={item.label}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 text-left group ${buttonClasses}`}
                            onClick={() => {
                              navigate(item.href);
                              onClose();
                            }}
                            whileHover={{ x: active ? 0 : 4 }}
                            whileTap={{ scale: 0.95 }}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.05 * idx }}
                            title={item.description}
                          >
                            <Icon className={`w-5 h-5 flex-shrink-0 ${active ? 'text-white' : 'text-current'}`} />
                            <div className="flex-1 min-w-0">
                              <span className="font-medium block truncate">{item.label}</span>
                              {item.description && !active && (
                                <span className="text-xs block truncate text-gray-500">
                                  {item.description}
                                </span>
                              )}
                            </div>
                            {item.badge && (
                              <span className={`px-2 py-1 text-xs rounded-full font-bold ${
                                active 
                                  ? 'bg-white/20 text-white'
                                  : 'bg-violet-100 text-violet-700 dark:bg-violet-900/50 dark:text-violet-300'
                              }`}>
                                {item.badge}
                              </span>
                            )}
                          </motion.button>
                        );
                      })}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}

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
                      <Clock className="w-5 h-5 text-violet-600 dark:text-violet-400" />
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
                          {(() => {
                            if (role === 'admin') return `${(mostRecent as any).usuarios} usuarios`;
                            if (role === 'profesor' || role === 'docente') return `${(mostRecent as any).pendientes} pendientes`;
                            return `${(mostRecent as any).students} estudiantes`;
                          })()}
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
                        {role === 'admin' && (mostRecent as any).estado && (() => {
                          const isActive = (mostRecent as any).estado === 'Activa';
                          const activeColor = isDark ? 'text-green-400' : 'text-green-600';
                          const inactiveColor = isDark ? 'text-yellow-400' : 'text-yellow-600';
                          const statusColor = isActive ? activeColor : inactiveColor;
                          
                          return (
                            <p className={`text-xs mt-1 font-medium ${statusColor}`}>
                              {(mostRecent as any).estado}
                            </p>
                          );
                        })()}
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
                    <ChevronRight className="w-4 h-4 ml-auto" />
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
