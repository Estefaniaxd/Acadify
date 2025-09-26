import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';
import { 
  FiHome, FiBook, FiTrendingUp, FiInfo, FiMenu, FiX,
  FiSettings, FiUsers, FiBarChart, FiUserCheck,
  FiPlus, FiShoppingBag, FiAward, FiUser
} from 'react-icons/fi';
import { HiOutlineOfficeBuilding } from 'react-icons/hi';
import { avatarAPI } from '../avatar/avatarAPI';

const getLinksByRole = (role?: string) => {
  if (role === 'admin') {
    return [
      { label: 'Panel Admin', href: '/admin', icon: FiSettings },
      { label: 'Instituciones', href: '/admin/instituciones', icon: HiOutlineOfficeBuilding },
      { label: 'Usuarios', href: '/admin/usuarios', icon: FiUsers },
      { label: 'Estadísticas', href: '/admin/estadisticas', icon: FiBarChart },
    ];
  }
  if (role === 'coordinador') {
    return [
      { label: 'Panel Coordinador', href: '/coordinador', icon: FiSettings },
      { label: 'Mi institución', href: '/coordinador/institucion', icon: HiOutlineOfficeBuilding },
      { label: 'Profesores', href: '/coordinador/profesores', icon: FiUserCheck },
      { label: 'Clases', href: '/coordinador/clases', icon: FiBook },
      { label: 'Estadísticas', href: '/coordinador/estadisticas', icon: FiBarChart },
    ];
  }
  if (role === 'profesor') {
    return [
      { label: 'Panel Profesor', href: '/profesor', icon: FiSettings },
      { label: 'Mis clases', href: '/mis-clases', icon: FiBook },
      { label: 'Tareas', href: '/profesor/tareas', icon: FiUserCheck },
      { label: 'Materiales', href: '/profesor/materiales', icon: HiOutlineOfficeBuilding },
      { label: 'Progreso', href: '/profesor/progreso', icon: FiTrendingUp },
    ];
  }
  if (role === 'estudiante') {
    return [
      { label: 'Mis clases', href: '/mis-clases', icon: FiBook },
      { label: 'Unirse a clase', href: '/unirse-clase', icon: FiPlus },
      { label: 'Tienda', href: '/tienda', icon: FiShoppingBag },
      { label: 'Logros', href: '/logros', icon: FiAward },
      { label: 'Avatar', href: '/avatar', icon: FiUser },
    ];
  }
  // No autenticado o rol desconocido
  return [
    { label: 'Inicio', href: '/', icon: FiHome },
    { label: 'Características', href: '/#features', icon: FiBook },
    { label: 'Cómo funciona', href: '/#how', icon: FiTrendingUp },
    { label: 'Open Source', href: '/#opensource', icon: FiInfo },
    { label: 'Testimonios', href: '/#testimonials', icon: FiUserCheck },
    { label: 'Instituciones', href: '/#institutions', icon: HiOutlineOfficeBuilding },
    { label: 'Roadmap', href: '/#roadmap', icon: FiBarChart },
    { label: 'Contacto', href: '/#cta', icon: FiAward }
  ];
};

export default function Nav() {
  const { isAuthenticated, user } = useAuth();
  const role = user?.role || (isAuthenticated ? 'estudiante' : undefined);
  const LINKS = getLinksByRole(role);
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [userAvatarUrl, setUserAvatarUrl] = useState<string | null>(null);
  const [loadingAvatar, setLoadingAvatar] = useState(true);
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

  // Cargar avatar del usuario
  useEffect(() => {
    const loadUserAvatar = async () => {
      if (!user || !isAuthenticated) {
        console.log('🔍 Nav: No user or not authenticated');
        setLoadingAvatar(false);
        return;
      }

      console.log('🔍 Nav: Loading avatar for user:', user.username);

      // Verificar si hay token de autenticación
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('🔍 Nav: No auth token found, skipping avatar load');
        setLoadingAvatar(false);
        return;
      }

      try {
        const avatars = await avatarAPI.getMyAvatars();
        console.log('🔍 Nav: Avatars response:', avatars);
        
        const activeAvatar = avatars.avatars.find(avatar => avatar.is_active);
        console.log('🔍 Nav: Active avatar:', activeAvatar);
        
        if (activeAvatar && activeAvatar.image_url) {
          console.log('🔍 Nav: Setting avatar URL:', activeAvatar.image_url);
          setUserAvatarUrl(activeAvatar.image_url);
        }
      } catch (error) {
        console.error('🔍 Nav: Error loading user avatar:', error);
      } finally {
        setLoadingAvatar(false);
      }
    };

    loadUserAvatar();
  }, [user, isAuthenticated]);

  // Escuchar actualizaciones de avatar
  useEffect(() => {
    const handleAvatarUpdate = (event: CustomEvent) => {
      console.log('🔍 Nav: Avatar update event received:', event.detail);
      const avatarData = event.detail;
      if (avatarData && avatarData.image_url) {
        console.log('🔍 Nav: Updating avatar URL from event:', avatarData.image_url);
        setUserAvatarUrl(avatarData.image_url);
      }
    };

    window.addEventListener('avatar-updated', handleAvatarUpdate as EventListener);
    
    return () => {
      window.removeEventListener('avatar-updated', handleAvatarUpdate as EventListener);
    };
  }, []);

  // Detectar modo oscuro
  const isDark = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const darkBg = scrolled
    ? 'rgba(24, 16, 48, 0.92)'
    : 'rgba(24, 16, 48, 0.80)';
  const lightBg = scrolled
    ? 'rgba(255, 255, 255, 0.85)'
    : 'rgba(255, 255, 255, 0.65)';
  const headerBg = isDark ? darkBg : lightBg;
  const borderColor = isDark
    ? (scrolled ? '1px solid rgba(139, 92, 246, 0.35)' : '1px solid rgba(40, 20, 80, 0.25)')
    : (scrolled ? '1px solid rgba(139, 92, 246, 0.2)' : '1px solid rgba(255, 255, 255, 0.1)');
  const boxShadow = isDark
    ? (scrolled ? '0 8px 32px rgba(139, 92, 246, 0.18)' : '0 4px 20px rgba(40, 20, 80, 0.10)')
    : (scrolled ? '0 8px 32px rgba(139, 92, 246, 0.12)' : '0 4px 20px rgba(0, 0, 0, 0.05)');

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
      className="fixed left-0 right-0 top-0 z-50 transition-all duration-500"
      style={{
        background: headerBg,
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderBottom: borderColor,
        boxShadow: boxShadow,
      }}
    >
      <div 
        className="mx-auto px-4 lg:px-8"
        style={{
          background: isDark
            ? 'linear-gradient(90deg, rgba(40, 20, 80, 0.10) 0%, rgba(139, 92, 246, 0.10) 50%, rgba(40, 20, 80, 0.10) 100%)'
            : 'linear-gradient(90deg, rgba(139, 92, 246, 0.03) 0%, rgba(124, 58, 237, 0.06) 50%, rgba(139, 92, 246, 0.03) 100%)',
        }}
      >
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
                  className="w-20 h-20 rounded-2xl object-cover shadow-lg"
                />
              </motion.div>
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <span className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-violet-600 via-purple-600 to-purple-700 tracking-tight">
                  Acadify
                </span>
                <motion.div 
                  className="h-0.5 bg-gradient-to-r from-violet-600 to-purple-600 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ delay: 0.8, duration: 0.8 }}
                />
              </motion.div>
            </Link>
          </motion.div>

          {/* Navegación principal - Desktop */}
          <nav className="hidden lg:flex items-center gap-2">
            {LINKS.slice(0, 5).map((link, index) => {
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
                    className={`relative group flex items-center gap-2 px-4 py-3 rounded-2xl transition-all duration-300 font-medium text-sm ${
                      active 
                        ? 'text-white shadow-lg' 
                        : 'text-neutral-800 hover:text-purple-700 dark:text-neutral-200 dark:hover:text-purple-300'
                    }`}
                    style={{
                      background: active 
                        ? 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' 
                        : 'transparent'
                    }}
                  >
                    {/* Efecto hover de fondo */}
                    <motion.div
                      className="absolute inset-0 rounded-2xl bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/10 dark:to-purple-900/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                      whileHover={{ scale: 1.02 }}
                    />
                    
                    {/* Indicador activo */}
                    {active && (
                      <motion.div
                        layoutId="activeIndicator"
                        className="absolute inset-0 rounded-2xl"
                        style={{
                          background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(124, 58, 237, 0.15) 100%)',
                          border: '1px solid rgba(139, 92, 246, 0.3)'
                        }}
                        transition={{ type: "spring", duration: 0.6 }}
                      />
                    )}
                    
                    <motion.div
                      className="relative z-10 flex items-center gap-2"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Icon className={`w-4 h-4 ${active ? 'text-white' : 'text-current'}`} />
                      <span>{link.label}</span>
                    </motion.div>
                    
                    {/* Efecto de brillo eliminado por feedback */}
                  </Link>
                </motion.div>
              );
            })}
          </nav>

          {/* Botones de acción */}
          <div className="hidden lg:flex items-center gap-3">
            {!isAuthenticated ? (
              <motion.div 
                className="flex items-center gap-3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
              >
                <Link to="/login">
                  <motion.button 
                    className="px-6 py-2.5 rounded-xl border border-purple-200 dark:border-purple-700 text-purple-700 dark:text-purple-300 bg-white/80 dark:bg-black/20 font-medium hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all duration-300 backdrop-blur-sm"
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Iniciar sesión
                  </motion.button>
                </Link>
                <Link to="/register">
                  <motion.button 
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 text-white font-semibold shadow-lg hover:shadow-xl relative overflow-hidden"
                    whileHover={{ scale: 1.02, y: -1 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span className="relative z-10">Crear cuenta</span>
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-violet-500 to-purple-500 opacity-0 hover:opacity-100 transition-opacity duration-300"
                    />
                  </motion.button>
                </Link>
              </motion.div>
            ) : (
              loadingAvatar ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : <></>
            )}
          </div>

          {/* Botón hamburguesa móvil */}
          <motion.button
            className="lg:hidden p-2 rounded-xl bg-white/80 dark:bg-black/20 backdrop-blur-sm border border-purple-200 dark:border-purple-700"
            onClick={() => setOpen(!open)}
            whileTap={{ scale: 0.95 }}
          >
            <motion.div
              animate={{ rotate: open ? 180 : 0 }}
              transition={{ duration: 0.3 }}
            >
              {open ? <FiX className="w-6 h-6 text-purple-700" /> : <FiMenu className="w-6 h-6 text-purple-700" />}
            </motion.div>
          </motion.button>
        </div>
      </div>

      {/* Menú móvil con glassmorphism */}
      <AnimatePresence>
        {open && (
          <>
            <motion.div 
              className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm lg:hidden" 
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
              className="lg:hidden fixed left-4 right-4 top-24 z-50 rounded-3xl shadow-2xl border border-white/20 overflow-hidden"
              style={{
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(25px)',
                WebkitBackdropFilter: 'blur(25px)',
              }}
            >
              <div className="p-6">
                <div className="grid gap-2">
                  {LINKS.map((link, index) => {
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
                          onClick={() => setOpen(false)} 
                          className="flex items-center gap-4 px-5 py-4 rounded-2xl hover:bg-gradient-to-r hover:from-violet-50 hover:to-purple-50 text-neutral-800 dark:text-neutral-200 font-medium transition-all duration-300 group border border-transparent hover:border-purple-200 dark:hover:text-purple-300"
                        >
                          <motion.div
                            className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-100 to-purple-100 flex items-center justify-center group-hover:from-violet-200 group-hover:to-purple-200 transition-all duration-300"
                            whileHover={{ scale: 1.1, rotate: 5 }}
                          >
                            <Icon className="w-5 h-5 text-purple-600" />
                          </motion.div>
                          <span className="group-hover:translate-x-1 transition-transform duration-300 text-lg">
                            {link.label}
                          </span>
                        </Link>
                      </motion.div>
                    )
                  })}
                  
                  {!isAuthenticated && (
                    <motion.div 
                      className="pt-4 mt-4 border-t border-purple-100 space-y-3"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.4 }}
                    >
                      <Link to="/login" onClick={() => setOpen(false)}>
                        <motion.button 
                          className="w-full px-5 py-4 rounded-2xl border border-purple-200 text-purple-700 bg-white font-medium hover:bg-purple-50 transition-all duration-300"
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          Iniciar sesión
                        </motion.button>
                      </Link>
                      <Link to="/register" onClick={() => setOpen(false)}>
                        <motion.button 
                          className="w-full px-5 py-4 rounded-2xl bg-gradient-to-r from-violet-600 to-purple-600 text-white font-semibold shadow-lg"
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
