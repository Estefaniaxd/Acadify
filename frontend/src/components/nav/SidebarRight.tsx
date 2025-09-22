import { useNavigate } from 'react-router-dom';
import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

const mockUser = {
  avatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=acadify',
  estado: 'activo',
  diasActividad: 27,
  diasCharla: 12,
  logros: [
    { id: 1, name: 'Primer curso', img: 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png' },
    { id: 2, name: 'Participante', img: 'https://cdn-icons-png.flaticon.com/512/3135/3135789.png' },
    { id: 3, name: 'Comunidad', img: 'https://cdn-icons-png.flaticon.com/512/3135/3135768.png' },
  ],
};

type SidebarRightProps = { open: boolean; onClose: () => void; role?: string };

export default function SidebarRight({ open, onClose, role = 'estudiante' }: SidebarRightProps) {
  // ...existing code...
  // Estado de tema local para el botón
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    try {
      const t = localStorage.getItem('theme');
      return t === 'dark' ? 'dark' : 'light';
    } catch {
      return 'light';
    }
  });
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    try {
      localStorage.setItem('theme', theme);
    } catch {}
  }, [theme]);

  // Menú por rol (solo iconos SVG)
  const menu = useMemo(() => {
    const icons = {
      perfil: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="7" r="4"/><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/></svg>,
      admin: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>,
      inst: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 21h18"/><path d="M5 21V7l8-4v18"/></svg>,
      users: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
      stats: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 3v18h18"/><rect x="7" y="13" width="3" height="5"/><rect x="12" y="8" width="3" height="10"/><rect x="17" y="5" width="3" height="13"/></svg>,
      ajustes: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h.09a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h.09a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v.09a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>,
      clases: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M3 10h18"/></svg>,
      join: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14m7-7H5"/></svg>,
      shop: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" x2="21" y1="6" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>,
      logros: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>,
      avatar: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="7" r="4"/><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/></svg>,
      tareas: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15l-2-2 2-2"/></svg>,
      materiales: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/></svg>,
      progreso: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 17v-6a9 9 0 0 1 18 0v6"/><path d="M17 21v-2a4 4 0 0 0-4-4H11a4 4 0 0 0-4 4v2"/></svg>,
    };
    if (role === 'admin') {
      return [
        { label: 'Perfil', icon: icons.perfil, path: '/perfil' },
        { label: 'Panel Admin', icon: icons.admin, path: '/admin' },
        { label: 'Instituciones', icon: icons.inst, path: '/admin/instituciones' },
        { label: 'Usuarios', icon: icons.users, path: '/admin/usuarios' },
        { label: 'Estadísticas', icon: icons.stats, path: '/admin/estadisticas' },
        { label: 'Ajustes', icon: icons.ajustes, path: '/ajustes' },
      ];
    }
    if (role === 'coordinador') {
      return [
        { label: 'Perfil', icon: icons.perfil, path: '/perfil' },
        { label: 'Panel Coordinador', icon: icons.admin, path: '/coordinador' },
        { label: 'Mi institución', icon: icons.inst, path: '/coordinador/institucion' },
        { label: 'Profesores', icon: icons.users, path: '/coordinador/profesores' },
        { label: 'Clases', icon: icons.clases, path: '/coordinador/clases' },
        { label: 'Estadísticas', icon: icons.stats, path: '/coordinador/estadisticas' },
        { label: 'Ajustes', icon: icons.ajustes, path: '/ajustes' },
      ];
    }
    if (role === 'profesor') {
      return [
        { label: 'Perfil', icon: icons.perfil, path: '/perfil' },
        { label: 'Panel Profesor', icon: icons.admin, path: '/profesor' },
        { label: 'Mis clases', icon: icons.clases, path: '/mis-clases' },
        { label: 'Tareas', icon: icons.tareas, path: '/profesor/tareas' },
        { label: 'Materiales', icon: icons.materiales, path: '/profesor/materiales' },
        { label: 'Progreso', icon: icons.progreso, path: '/profesor/progreso' },
        { label: 'Ajustes', icon: icons.ajustes, path: '/ajustes' },
      ];
    }
    // estudiante o default
    return [
      { label: 'Perfil', icon: icons.perfil, path: '/perfil' },
      { label: 'Mis clases', icon: icons.clases, path: '/mis-clases' },
      { label: 'Unirse a clase', icon: icons.join, path: '/unirse-clase' },
      { label: 'Tienda', icon: icons.shop, path: '/tienda' },
      { label: 'Logros', icon: icons.logros, path: '/logros' },
      { label: 'Avatar', icon: icons.avatar, path: '/avatar' },
      { label: 'Ajustes', icon: icons.ajustes, path: '/ajustes' },
    ];
  }, [role]);

  // Creatividad extra: sección de insignias y progreso
  const badges = [
    { id: 1, name: 'Colaborador', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> },
    { id: 2, name: 'Explorador', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg> },
    { id: 3, name: 'Maestro', icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M3 10h18"/></svg> },
  ];
  const progreso = 75; // %
  const navigate = useNavigate();
  const { logout } = useAuth();
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ x: 320, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 320, opacity: 0 }}
          transition={{ duration: 0.25, ease: 'easeOut' }}
          className="fixed top-0 right-0 h-full z-40 w-96 max-w-[420px] bg-white dark:bg-[#18181b] shadow-lg border-l border-gray-200 dark:border-gray-800"
          tabIndex={-1}
          aria-modal="true"
          role="dialog"
        >
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-700">
            <span className="text-xl font-bold text-primary">Tu perfil</span>
            <button onClick={onClose} className="text-2xl text-gray-500 hover:text-primary">×</button>
          </div>
          <div className="px-6 py-4 overflow-y-auto h-[calc(100vh-64px)] flex flex-col gap-8">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="flex flex-col items-center gap-2">
              <img src={mockUser.avatar} alt="avatar" className="w-20 h-20 rounded-full border-4 border-primary shadow" />
              <button className="text-xs text-primary hover:underline mt-1" onClick={() => navigate('/avatar')}>Personalizar avatar</button>
              <div className="flex items-center gap-2 mt-2">
                <span className={`w-3 h-3 rounded-full ${mockUser.estado === 'activo' ? 'bg-green-500' : 'bg-gray-400'}`}></span>
                <span className="text-sm text-gray-600 dark:text-gray-300">{mockUser.estado === 'activo' ? 'Cuenta activa' : 'Cuenta inactiva'}</span>
              </div>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="flex flex-col items-center gap-2">
              <div className="flex gap-6">
                <div className="flex flex-col items-center">
                  <span className="text-lg font-bold text-primary">{mockUser.diasActividad}</span>
                  <span className="text-xs text-gray-500">Días de actividad</span>
                </div>
                <div className="flex flex-col items-center">
                  <span className="text-lg font-bold text-primary">{mockUser.diasCharla}</span>
                  <span className="text-xs text-gray-500">Días de charla</span>
                </div>
              </div>
            </motion.div>
            {/* Progreso de nivel */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-green-600">Progreso de nivel</span>
                <span className="text-xs text-gray-500">{progreso}%</span>
              </div>
              <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div className="h-3 bg-gradient-to-r from-green-400 to-primary" style={{ width: progreso + '%' }} initial={{ width: 0 }} animate={{ width: progreso + '%' }} transition={{ delay: 0.3, duration: 0.8 }} />
              </div>
            </motion.div>
            {/* Insignias */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-yellow-600">Insignias</span>
                <button className="text-xs text-primary hover:underline flex items-center gap-1" onClick={() => navigate('/insignias')}>Ver todas <span>→</span></button>
              </div>
              <div className="flex gap-2">
                {badges.map((b) => (
                  <span key={b.id} title={b.name} className="w-8 h-8 rounded-full bg-yellow-100 dark:bg-yellow-900 flex items-center justify-center border border-yellow-400 dark:border-yellow-700 text-primary">
                    {b.icon}
                  </span>
                ))}
              </div>
            </motion.div>
            {/* Logros previos (fotos) */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-gray-500">Logros</span>
                <button className="text-xs text-primary hover:underline flex items-center gap-1" onClick={() => navigate('/logros')}>Ver todas <span>→</span></button>
              </div>
              <div className="flex gap-2">
                {mockUser.logros.map(l => (
                  <img key={l.id} src={l.img} alt={l.name} title={l.name} className="w-8 h-8 rounded-full border border-primary" />
                ))}
              </div>
            </motion.div>
            {/* Menú y tema */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="flex flex-col gap-2 border-t border-gray-200 dark:border-gray-700 pt-4">
              <button
                className="flex items-center gap-3 px-3 py-2 rounded hover:bg-primary/10 text-base text-gray-700 dark:text-gray-200"
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              >
                <span className="text-lg">
                  {theme === 'dark'
                    ? <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2m0 18v2m11-11h-2M3 12H1m16.95 7.07l-1.41-1.41M6.34 6.34L4.93 4.93m12.02 0l-1.41 1.41M6.34 17.66l-1.41 1.41"/></svg>
                    : <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"/></svg>
                  }
                </span>
                Modo {theme === 'dark' ? 'claro' : 'oscuro'}
              </button>
              {menu.map((item) => (
                <button
                  key={item.label}
                  className="flex items-center gap-3 px-3 py-2 rounded hover:bg-primary/10 text-base text-gray-700 dark:text-gray-200 transition-colors"
                  onClick={() => item.path && navigate(item.path)}
                >
                  <span className="text-lg">{item.icon}</span> {item.label}
                </button>
              ))}
              {/* Botón de cerrar sesión moved here from top nav */}
              <button
                onClick={() => { logout(); onClose(); navigate('/'); }}
                className="flex items-center gap-3 px-3 py-2 rounded bg-gradient-to-r from-primary to-purple-600 text-white font-semibold shadow-md hover:from-purple-600 hover:to-primary transition-colors"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="opacity-90"><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/><path d="M13 5v-1a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h5a2 2 0 0 0 2-2v-1"/></svg>
                Cerrar sesión
              </button>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
