import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Nav from './Nav'
import Footer from './Footer'
import HamburgerButton from '../nav/HamburgerButton'
import SidebarLeft from '../nav/SidebarLeft'
import UserAvatarButton from '../nav/UserAvatarButton'
import SidebarRight from '../nav/SidebarRight'
import { useAuth } from '../../context/AuthContext'

type Props = {
  children: React.ReactNode
}

export default function Layout({ children }: Props) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sidebarRightOpen, setSidebarRightOpen] = useState(false)
  const { isAuthenticated, user } = useAuth();
  const anySidebarOpen = sidebarOpen || sidebarRightOpen;
  
  // Cerrar sidebars con ESC
  React.useEffect(() => {
    if (!anySidebarOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSidebarOpen(false);
        setSidebarRightOpen(false);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [anySidebarOpen]);

  // Cerrar sidebars cuando se navega a una nueva ruta
  React.useEffect(() => {
    setSidebarOpen(false);
    setSidebarRightOpen(false);
  }, [children]);

  // Función para cerrar ambos sidebars
  const closeAllSidebars = React.useCallback(() => {
    setSidebarOpen(false);
    setSidebarRightOpen(false);
  }, []);

  // Función para alternar sidebar izquierdo (cierra el derecho si está abierto)
  const toggleSidebarLeft = React.useCallback(() => {
    setSidebarRightOpen(false);
    setSidebarOpen(prev => !prev);
  }, []);

  // Función para alternar sidebar derecho (cierra el izquierdo si está abierto)
  const toggleSidebarRight = React.useCallback(() => {
    setSidebarOpen(false);
    setSidebarRightOpen(prev => !prev);
  }, []);

  return (
    <div className="min-h-screen bg-[var(--color-bg)] text-[var(--color-text)]">
      <Nav />
      {/* Overlay para sidebars: solo cubre el contenido, nunca la barra superior */}
      <AnimatePresence>
        {anySidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed left-0 right-0 top-20 bottom-0 z-[80] bg-black/40 backdrop-blur-sm"
            tabIndex={0}
            aria-label="Cerrar menú lateral"
            onClick={closeAllSidebars}
            onKeyDown={e => {
              if (e.key === 'Escape' || e.key === 'Enter' || e.key === ' ') {
                closeAllSidebars();
              }
            }}
          />
        )}
      </AnimatePresence>

      {isAuthenticated && (
        <>
          {/* Botones flotantes para abrir sidebars - solo visibles cuando ambos están cerrados */}
          {!sidebarOpen && !sidebarRightOpen && (
            <>
              <HamburgerButton onClick={toggleSidebarLeft} />
              <UserAvatarButton onClick={toggleSidebarRight} />
            </>
          )}
          
          {/* Sidebar izquierdo: z-[90] para estar debajo de Nav pero sobre overlay */}
          <div className="z-[90] fixed top-20 left-0 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 5rem)' }}>
            <SidebarLeft open={sidebarOpen} onClose={() => setSidebarOpen(false)} role={user?.role || 'estudiante'} />
          </div>
          
          {/* Sidebar derecho: z-[90] para estar debajo de Nav pero sobre overlay */}
          <div className="z-[90] fixed top-20 right-0 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 5rem)' }}>
            <SidebarRight open={sidebarRightOpen} onClose={() => setSidebarRightOpen(false)} role={user?.role || 'estudiante'} />
          </div>
        </>
      )}
      {/* Cuando SidebarLeft está abierta, empuja el contenido a la derecha. Ajuste para que nunca se superponga a Nav. */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1, ease: "easeOut" }}
        className={`transition-all pt-24 pb-8 main-content ${sidebarOpen ? 'md:ml-80 ml-64' : ''} ${sidebarOpen || sidebarRightOpen ? 'blur-none pointer-events-auto select-auto' : ''}`}
        style={{ minHeight: 'calc(100vh - 6rem)', zIndex: 1 }}
      >
        {children}
      </motion.div>
      <Footer />
    </div>
  )
}
