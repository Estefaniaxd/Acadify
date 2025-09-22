import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';

const getLinksByRole = (role?: string) => {
  if (role === 'admin') {
    return [
      { label: 'Panel Admin', href: '/admin' },
      { label: 'Instituciones', href: '/admin/instituciones' },
      { label: 'Usuarios', href: '/admin/usuarios' },
      { label: 'Estadísticas', href: '/admin/estadisticas' },
    ];
  }
  if (role === 'coordinador') {
    return [
      { label: 'Panel Coordinador', href: '/coordinador' },
      { label: 'Mi institución', href: '/coordinador/institucion' },
      { label: 'Profesores', href: '/coordinador/profesores' },
      { label: 'Clases', href: '/coordinador/clases' },
      { label: 'Estadísticas', href: '/coordinador/estadisticas' },
    ];
  }
  if (role === 'profesor') {
    return [
      { label: 'Panel Profesor', href: '/profesor' },
      { label: 'Mis clases', href: '/mis-clases' },
      { label: 'Tareas', href: '/profesor/tareas' },
      { label: 'Materiales', href: '/profesor/materiales' },
      { label: 'Progreso', href: '/profesor/progreso' },
    ];
  }
  if (role === 'estudiante') {
    return [
      { label: 'Mis clases', href: '/mis-clases' },
      { label: 'Unirse a clase', href: '/unirse-clase' },
      { label: 'Tienda', href: '/tienda' },
      { label: 'Logros', href: '/logros' },
      { label: 'Avatar', href: '/avatar' },
    ];
  }
  // No autenticado o rol desconocido
  return [
    { label: 'Inicio', href: '/' },
    { label: 'Cursos', href: '/courses' },
    { label: 'Gamificación', href: '/gamification' },
    { label: 'Acerca', href: '/about' }
  ];
};

export default function Nav() {
  const { isAuthenticated, user } = useAuth();
  const role = user?.role || (isAuthenticated ? 'estudiante' : undefined);
  const LINKS = getLinksByRole(role);
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.23, 1, 0.32, 1] }}
      className="fixed left-0 right-0 top-0 z-50 transition-all duration-300"
      style={{
        background: scrolled
          ? 'linear-gradient(180deg, rgba(8,8,20,0.95) 0%, rgba(15,8,25,0.90) 100%)'
          : 'linear-gradient(180deg, rgba(8,8,20,0.80) 0%, rgba(15,8,25,0.70) 100%)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderBottom: scrolled ? '1px solid rgba(120,80,200,0.15)' : '1px solid rgba(255,255,255,0.05)'
      }}
    >
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16 w-full">
          {/* Navegación principal en una sola línea, centrada */}
          <nav className="flex-1 flex items-center justify-center gap-2">
            <Link to="/" className="flex items-center gap-2 group mr-6">
              <span className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary via-purple-500 to-purple-700 flex items-center justify-center shadow-lg border border-white/10 text-white text-lg font-bold">A</span>
              <span className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-400">Acadify</span>
            </Link>
            {LINKS.slice(0, 5).map((link, index) => {
              const active = location.pathname === link.href;
              return (
                <Link
                  key={link.label}
                  to={link.href}
                  className={`relative flex items-center justify-center px-3 py-2 rounded-lg transition-all duration-300 group text-sm font-medium ${
                    active 
                      ? 'bg-gradient-to-br from-primary/40 to-purple-600/40 text-primary shadow-md' 
                      : 'hover:bg-white/5 text-gray-400 hover:text-primary'
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
      {/* Menú móvil elegante */}
      <AnimatePresence>
        {open && (
          <>
            <motion.div 
              className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm" 
              onClick={() => setOpen(false)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            />
            <motion.nav
              initial={{ opacity: 0, y: -30, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -30, scale: 0.9 }}
              transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
              className="lg:hidden fixed left-4 right-4 top-20 bg-gradient-to-br from-gray-900/98 via-gray-800/98 to-gray-900/98 backdrop-blur-xl rounded-2xl shadow-2xl p-6 z-50 border border-gray-700/50"
            >
              <div className="flex flex-col gap-2">
                {LINKS.map((link, index) => (
                  <motion.div
                    key={link.label}
                    initial={{ opacity: 0, x: -30 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * index, duration: 0.3 }}
                  >
                    <Link 
                      to={link.href} 
                      onClick={() => setOpen(false)} 
                      className="flex items-center gap-4 px-4 py-3 rounded-xl hover:bg-white/5 text-gray-100 text-base font-medium transition-all duration-300 group border border-transparent hover:border-gray-600/50"
                    >
                      <span className="group-hover:translate-x-1 transition-transform duration-300">{link.label}</span>
                    </Link>
                  </motion.div>
                ))}
                {!isAuthenticated ? (
                  <motion.div 
                    className="pt-4 mt-4 border-t border-gray-700/50 space-y-3"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                  >
                    <Link to="/login" onClick={() => setOpen(false)}>
                      <motion.button 
                        className="w-full px-4 py-3 rounded-xl border border-gray-600/50 text-gray-100 hover:bg-white/5 hover:border-gray-500/50 transition-all duration-300"
                        whileHover={{ scale: 1.01 }}
                        whileTap={{ scale: 0.99 }}
                      >
                        Iniciar sesión
                      </motion.button>
                    </Link>
                    <Link to="/register" onClick={() => setOpen(false)}>
                      <motion.button 
                        className="w-full px-4 py-3 rounded-xl bg-gradient-to-r from-primary to-purple-600 text-white font-semibold shadow-lg"
                        whileHover={{ scale: 1.01, boxShadow: "0 8px 25px rgba(139,92,246,0.3)" }}
                        whileTap={{ scale: 0.99 }}
                      >
                        Crear cuenta
                      </motion.button>
                    </Link>
                  </motion.div>
                ) : null}
              </div>
            </motion.nav>
          </>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
