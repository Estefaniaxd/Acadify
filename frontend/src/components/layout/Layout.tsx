import React, { useState } from 'react'
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

  // Mostrar sidebars solo si está autenticado
  return (
    <div className="min-h-screen bg-[var(--color-bg)] text-[var(--color-text)]">
      <Nav />
      {/* Overlay para sidebars: solo cubre el contenido, nunca la barra superior */}
      {(sidebarOpen || sidebarRightOpen) && (
        <div
          className="fixed left-0 right-0 top-16 bottom-0 z-40 bg-black/40 backdrop-blur-sm transition-opacity animate-fade-in"
          tabIndex={0}
          aria-label="Cerrar menú lateral"
          onClick={() => { setSidebarOpen(false); setSidebarRightOpen(false); }}
          onKeyDown={e => {
            if (e.key === 'Escape' || e.key === 'Tab') {
              setSidebarOpen(false); setSidebarRightOpen(false);
            }
          }}
        />
      )}
      {isAuthenticated && (
        <>
          {/* Botón hamburguesa solo si sidebar izquierdo está cerrado y derecho no está abierto */}
          {!sidebarOpen && !sidebarRightOpen && <HamburgerButton onClick={() => setSidebarOpen(true)} />}
          {/* Botón avatar solo si sidebar derecho está cerrado y izquierdo no está abierto */}
          {!sidebarOpen && !sidebarRightOpen && <UserAvatarButton onClick={() => setSidebarRightOpen(true)} />}
          {/* Sidebar izquierdo: z-50 para estar sobre el overlay pero debajo de Nav */}
          <div className="z-50 fixed top-16 left-0">
            <SidebarLeft open={sidebarOpen} onClose={() => setSidebarOpen(false)} role={user?.role || 'estudiante'} />
          </div>
          {/* Sidebar derecho: z-50 para estar sobre el overlay pero debajo de Nav */}
          <div className="z-50 fixed top-16 right-0">
            <SidebarRight open={sidebarRightOpen} onClose={() => setSidebarRightOpen(false)} role={user?.role || 'estudiante'} />
          </div>
        </>
      )}
      {/* Cuando SidebarLeft está abierta, empuja el contenido a la derecha. Ajuste para que nunca se superponga a Nav. */}
      <div
        className={`transition-all pt-28 pb-8 main-content ${sidebarOpen ? 'md:ml-80 ml-64' : ''} ${sidebarOpen || sidebarRightOpen ? 'blur-sm pointer-events-none select-none' : ''}`}
        style={{ minHeight: 'calc(100vh - 4rem)' }}
      >
        {children}
      </div>
      <Footer />
    </div>
  )
}
