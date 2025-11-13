import React, { useEffect, useState, useMemo, useCallback, memo } from 'react';
import { useAuth } from '../../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { getMainNavItems, getSidebarItems, type UserRole } from '../../config/navigation';
import NotificationCenter from '../../modules/invitaciones/components/NotificationCenter';
import NotificacionBadge from '../notificaciones/NotificacionBadge';

function Nav() {
  const { isAuthenticated, user } = useAuth();
  const role = (user?.role || (isAuthenticated ? 'estudiante' : 'guest')) as UserRole;
  
  // Memoizar navegación basada en rol (solo recalcula si cambia el rol)
  // Aumentado a 8 para mostrar todos los items importantes del admin
  const mainNavLinks = useMemo(() => getMainNavItems(role, 8), [role]);
  const allLinks = useMemo(() => getSidebarItems(role), [role]);
  
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  // Callbacks estables
  const handleToggle = useCallback(() => setOpen(prev => !prev), []);
  const handleClose = useCallback(() => setOpen(false), []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleClose();
    };
    globalThis.window.addEventListener('keydown', onKey);
    return () => globalThis.window.removeEventListener('keydown', onKey);
  }, [handleClose]);

  // Optimizar scroll listener con requestAnimationFrame (evita jank)
  useEffect(() => {
    let ticking = false;
    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          setScrolled(globalThis.window.scrollY > 8);
          ticking = false;
        });
        ticking = true;
      }
    };
    onScroll();
    globalThis.window.addEventListener('scroll', onScroll, { passive: true });
    return () => globalThis.window.removeEventListener('scroll', onScroll);
  }, []);

  // Detectar modo oscuro del sistema (comentado - no se usa actualmente)
  // const [isDark, setIsDark] = useState(
  //   globalThis.window?.matchMedia?.('(prefers-color-scheme: dark)')?.matches ?? false
  // );

  // useEffect(() => {
  //   const mediaQuery = globalThis.window?.matchMedia('(prefers-color-scheme: dark)');
  //   const handleChange = (e: MediaQueryListEvent) => setIsDark(e.matches);
  //   mediaQuery?.addEventListener('change', handleChange);
  //   return () => mediaQuery?.removeEventListener('change', handleChange);
  // }, []);

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
      className={`fixed left-0 right-0 top-0 z-[100] transition-all duration-500 ${
        scrolled 
          ? 'bg-white/90 dark:bg-neutral-950/90 border-b border-neutral-200 dark:border-neutral-800 shadow-lg'
          : 'bg-white/70 dark:bg-neutral-950/70 border-b border-white/20 dark:border-neutral-900/20'
      }`}
      style={{
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
      }}
    >
      <div className="mx-auto px-4 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo con efecto 3D y animaciones */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center group"
          >
            <Link to="/" className="flex items-center gap-3 relative">
              <motion.div 
                className="relative ml-12"
                whileHover={{ rotate: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <img 
                  src="/rutilio_read.png" 
                  alt="Rutilio" 
                  className="w-16 h-16 object-contain"
                  style={{ mixBlendMode: 'multiply' }}
                />
              </motion.div>
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="flex flex-col"
              >
                <span className="text-2xl font-black bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 dark:from-violet-400 dark:via-purple-400 dark:to-fuchsia-400 bg-clip-text text-transparent tracking-tight">
                  Acadify
                </span>
                <motion.div 
                  className="h-0.5 bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 dark:from-violet-400 dark:via-purple-400 dark:to-fuchsia-400 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ delay: 0.8, duration: 0.8 }}
                />
              </motion.div>
            </Link>
          </motion.div>

          {/* Navegación principal - Desktop */}
          <nav className="hidden lg:flex items-center gap-2">
            {mainNavLinks.map((link, index) => {
              const active = location.pathname === link.href;
              const Icon = link.icon;
              return (
                <motion.div
                  key={link.label}
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index, duration: 0.5 }}
                >
                  <Link
                    to={link.href}
                    onClick={(e) => {
                      // Manejar scroll suave para secciones del home
                      if (link.href.startsWith('/#')) {
                        e.preventDefault();
                        const sectionId = link.href.substring(2);
                        const element = document.getElementById(sectionId);
                        if (element) {
                          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                      }
                    }}
                    className={`relative group flex items-center gap-2 px-4 py-3 rounded-xl transition-all duration-300 font-medium text-sm ${
                      active 
                        ? 'bg-gradient-to-r from-violet-600 to-purple-600 dark:from-violet-500 dark:to-purple-500 text-white shadow-lg shadow-violet-500/30' 
                        : 'text-neutral-700 dark:text-neutral-300 hover:bg-violet-50 dark:hover:bg-violet-950/50 hover:text-violet-700 dark:hover:text-violet-300'
                    }`}
                    title={link.description}
                  >
                    {/* Indicador activo animado */}
                    {active && (
                      <motion.div
                        layoutId="activeIndicator"
                        className="absolute inset-0 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 dark:from-violet-500 dark:to-purple-500"
                        transition={{ type: "spring", duration: 0.6, bounce: 0.2 }}
                      />
                    )}
                    
                    <motion.div
                      className="relative z-10 flex items-center gap-2"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Icon className={`w-4 h-4 ${active ? 'text-white' : 'text-current'}`} />
                      <span>{link.label}</span>
                      {link.badge && (
                        <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-white/20 text-white font-bold">
                          {link.badge}
                        </span>
                      )}
                    </motion.div>
                  </Link>
                </motion.div>
              );
            })}
          </nav>

          {/* Botones de acción */}
          <div className="hidden lg:flex items-center gap-3">
            {isAuthenticated ? (
              <motion.div
                className="flex items-center gap-2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
              >
                {/* Badge de notificaciones del sistema de comunicación */}
                <NotificacionBadge />
                
                {/* Centro de notificaciones de invitaciones */}
                <NotificationCenter />
              </motion.div>
            ) : (
              <motion.div 
                className="flex items-center gap-3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
              >
                <Link to="/login">
                  <motion.button 
                    className="px-6 py-2.5 rounded-xl border-2 border-violet-200 dark:border-violet-800 text-violet-700 dark:text-violet-300 bg-white dark:bg-neutral-900 font-medium hover:bg-violet-50 dark:hover:bg-violet-950/50 hover:border-violet-300 dark:hover:border-violet-700 transition-all duration-300"
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Iniciar sesión
                  </motion.button>
                </Link>
                <Link to="/register">
                  <motion.button 
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 dark:from-violet-500 dark:via-purple-500 dark:to-fuchsia-500 text-white font-semibold shadow-lg shadow-violet-500/30 hover:shadow-xl hover:shadow-violet-500/40 relative overflow-hidden"
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span className="relative z-10">Crear cuenta</span>
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-violet-500 via-purple-500 to-fuchsia-500"
                      initial={{ opacity: 0 }}
                      whileHover={{ opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    />
                  </motion.button>
                </Link>
              </motion.div>
            )}
          </div>

          {/* Botón hamburguesa móvil mejorado */}
          <div className="flex items-center gap-2 lg:hidden">
            {isAuthenticated && (
              <>
                {/* Badge de notificaciones en móvil */}
                <NotificacionBadge />
              </>
            )}
            <motion.button
              onClick={handleToggle}
              className="p-2 rounded-xl hover:bg-violet-500/10 transition-all duration-300"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              {open ? (
                <X className="w-6 h-6 text-violet-600 dark:text-violet-400" />
              ) : (
                <Menu className="w-6 h-6 text-violet-600 dark:text-violet-400" />
              )}
            </motion.button>
          </div>
        </div>
      </div>

      {/* Menú móvil con glassmorphism */}
      <AnimatePresence>
        {open && (
          <>
            <motion.div 
              className="fixed inset-0 z-40 bg-black/40 dark:bg-black/60 backdrop-blur-sm lg:hidden" 
              onClick={() => setOpen(false)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            />
            <motion.nav
              initial={{ opacity: 0, y: -50, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -50, scale: 0.95 }}
              transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
              className="lg:hidden fixed left-4 right-4 top-24 z-50 rounded-2xl shadow-2xl border-2 border-violet-200 dark:border-violet-800 overflow-hidden bg-white/95 dark:bg-neutral-950/95 backdrop-blur-xl"
            >
              <div className="p-6">
                <div className="grid gap-2">
                  {allLinks.map((link, index) => {
                    const Icon = link.icon;
                    return (
                      <motion.div
                        key={link.label}
                        initial={{ opacity: 0, x: -30 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.05 * index, duration: 0.3 }}
                      >
                        <Link 
                          to={link.href} 
                          onClick={(e) => {
                            setOpen(false);
                            // Manejar scroll suave para secciones del home
                            if (link.href.startsWith('/#')) {
                              e.preventDefault();
                              const sectionId = link.href.substring(2);
                              const element = document.getElementById(sectionId);
                              if (element) {
                                element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                              }
                            }
                          }}
                          className="flex items-center gap-4 px-5 py-4 rounded-xl hover:bg-violet-50 dark:hover:bg-violet-950/30 text-neutral-800 dark:text-neutral-200 font-medium transition-all duration-300 group border border-transparent hover:border-violet-200 dark:hover:border-violet-800"
                          title={link.description}
                        >
                          <motion.div
                            className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-100 to-purple-100 dark:from-violet-900/50 dark:to-purple-900/50 flex items-center justify-center group-hover:from-violet-200 group-hover:to-purple-200 dark:group-hover:from-violet-800/50 dark:group-hover:to-purple-800/50 transition-all duration-300"
                            whileHover={{ scale: 1.1, rotate: 5 }}
                          >
                            <Icon className="w-5 h-5 text-violet-600 dark:text-violet-400" />
                          </motion.div>
                          <div className="flex-1">
                            <span className="group-hover:translate-x-1 transition-transform duration-300 text-base block font-semibold">
                              {link.label}
                            </span>
                            {link.description && (
                              <span className="text-xs text-neutral-500 dark:text-neutral-400 block mt-0.5">
                                {link.description}
                              </span>
                            )}
                          </div>
                          {link.badge && (
                            <span className="px-2 py-1 text-xs rounded-full bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300 font-bold">
                              {link.badge}
                            </span>
                          )}
                        </Link>
                      </motion.div>
                    )
                  })}
                  
                  {!isAuthenticated && (
                    <motion.div 
                      className="pt-4 mt-4 border-t-2 border-violet-100 dark:border-violet-900 space-y-3"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.4 }}
                    >
                      <Link to="/login" onClick={() => setOpen(false)}>
                        <motion.button 
                          className="w-full px-5 py-4 rounded-xl border-2 border-violet-200 dark:border-violet-800 text-violet-700 dark:text-violet-300 bg-white dark:bg-neutral-900 font-semibold hover:bg-violet-50 dark:hover:bg-violet-950/50 transition-all duration-300"
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          Iniciar sesión
                        </motion.button>
                      </Link>
                      <Link to="/register" onClick={() => setOpen(false)}>
                        <motion.button 
                          className="w-full px-5 py-4 rounded-xl bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 dark:from-violet-500 dark:via-purple-500 dark:to-fuchsia-500 text-white font-semibold shadow-lg shadow-violet-500/30"
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          Crear cuenta
                        </motion.button>
                      </Link>
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.nav>
          </>
        )}
      </AnimatePresence>
    </motion.header>
  );
}

// Memoizar componente para evitar re-renders innecesarios
export default memo(Nav);
