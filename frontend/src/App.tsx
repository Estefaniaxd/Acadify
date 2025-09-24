import MisClasesPage from './pages/MisClasesPage';
import UnirseClasePage from './pages/UnirseClasePage';
import CrearClasePage from './pages/CrearClasePage';
import ClasePage from './pages/ClasePage';
import TareaPage from './pages/TareaPage';
import NotificacionesPage from './pages/NotificacionesPage';
import MensajesPage from './pages/MensajesPage';
import RankingPage from './pages/RankingPage';
import RetosTiendaPage from './pages/RetosTiendaPage';
import ForoRecursosPage from './pages/ForoRecursosPage';
import Perfil from './pages/Perfil';
import ExplorarAvatarsPage from './pages/ExplorarAvatarsPage';
import PanelAdmin from './modules/admin';
import PanelCoordinador from './modules/coordinador';
import PanelProfesor from './modules/profesor';
import PanelEstudiante from './modules/estudiante';
import TiendaPuntos from './modules/tienda';
import EditorAvatar from './modules/avatar';
import LogrosUsuario from './modules/logros';
import PuntosUsuario from './modules/puntos';
import NivelesUsuario from './modules/niveles';
import AyudaFaqPage from './pages/AyudaFaqPage';
import ActividadGamificadaPage from './pages/ActividadGamificadaPage';
import React, { useEffect, useState } from 'react'
import { useToast } from './context/ToastContext';
import Home from './pages/Home'
import ThemeToggle from './components/ThemeToggle'
import Layout from './components/layout/Layout'
import AuthLayout from './components/layout/AuthLayout'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import RecoverPassword from './pages/auth/RecoverPassword'
import ResetPassword from './pages/auth/ResetPassword'
import DashboardPage from './pages/DashboardPage'
import { Routes, Route, useLocation } from 'react-router-dom'
import AvatarCustomizerPage from './pages/avatar/AvatarCustomizerPage';
import SimpleAvatarTest from './pages/SimpleAvatarTest';
import LogrosPage from './pages/LogrosPage';
import InsigniasPage from './pages/InsigniasPage';
import AjustesPage from './pages/AjustesPage';
import ProfilePageAdvanced from './pages/ProfilePageAdvanced';
import BorradoresPage from './pages/BorradoresPage';
import UnirseComunidadPage from './pages/UnirseComunidadPage';
import GuardadoPage from './pages/GuardadoPage';
import HistoriaPage from './pages/HistoriaPage';
import TiendaPage from './pages/TiendaPage';
import { ToastProvider } from './context/ToastContext';
import TratamientoDatos from './pages/legal/TratamientoDatos';
import Consentimiento from './pages/legal/Consentimiento';

export default function App() {
  const location = useLocation()
  const [sessionExpired, setSessionExpired] = useState(false);
  const toast = useToast();
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    try {
      const t = localStorage.getItem('theme')
      return (t === 'dark' ? 'dark' : 'light')
    } catch {
      return 'light'
    }
  })

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    try {
      localStorage.setItem('theme', theme)
    } catch {}
  }, [theme])

  // Manejar evento de expiración de sesión
  useEffect(() => {
    const handleTokenExpired = () => {
      setSessionExpired(true);
      toast.error('Tu sesión ha expirado', 'Por favor, inicia sesión nuevamente.');
    };
    window.addEventListener('auth-token-expired', handleTokenExpired);
    return () => {
      window.removeEventListener('auth-token-expired', handleTokenExpired);
    };
  }, [toast]);

  // Páginas que usan AuthLayout en lugar del Layout completo
  const authPages = ['/login', '/register', '/recover', '/reset-password']
  const isAuthPage = authPages.includes(location.pathname)

  const routes = (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/recover" element={<RecoverPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/avatar" element={<AvatarCustomizerPage />} />
      <Route path="/avatar-test" element={<SimpleAvatarTest />} />
      <Route path="/explorar-avatares" element={<ExplorarAvatarsPage />} />
      <Route path="/logros" element={<LogrosPage />} />
      <Route path="/insignias" element={<InsigniasPage />} />
      <Route path="/ajustes" element={<AjustesPage theme={theme} setTheme={setTheme} />} />
      <Route path="/perfil" element={<ProfilePageAdvanced />} />
      <Route path="/borradores" element={<BorradoresPage />} />
      <Route path="/tienda-acadify" element={<TiendaPage />} />
      <Route path="/mis-clases" element={<MisClasesPage />} />
      <Route path="/unirse-clase" element={<UnirseClasePage />} />
      <Route path="/crear-clase" element={<CrearClasePage />} />
      <Route path="/clase/:id" element={<ClasePage />} />
      <Route path="/tarea/:id" element={<TareaPage />} />
      <Route path="/notificaciones" element={<NotificacionesPage />} />
      <Route path="/mensajes" element={<MensajesPage />} />
      <Route path="/ranking" element={<RankingPage />} />
      <Route path="/retos-tienda" element={<RetosTiendaPage />} />
      <Route path="/foro-recursos" element={<ForoRecursosPage />} />
  <Route path="/perfil" element={<Perfil />} />
      <Route path="/admin" element={<PanelAdmin />} />
      <Route path="/coordinador" element={<PanelCoordinador />} />
      <Route path="/profesor" element={<PanelProfesor />} />
      <Route path="/estudiante" element={<PanelEstudiante />} />
      <Route path="/tienda" element={<TiendaPuntos />} />
      <Route path="/avatar-editor" element={<EditorAvatar />} />
      <Route path="/mis-logros" element={<LogrosUsuario />} />
      <Route path="/mis-puntos" element={<PuntosUsuario />} />
      <Route path="/mis-niveles" element={<NivelesUsuario />} />
      <Route path="/ayuda" element={<AyudaFaqPage />} />
      <Route path="/actividad-gamificada" element={<ActividadGamificadaPage />} />
      <Route path="/legal/TratamientoDatos" element={<TratamientoDatos />} />
      <Route path="/legal/Consentimiento" element={<Consentimiento />} />
    </Routes>
  )

  return (
    <ToastProvider>
      {sessionExpired && (
        <div className="fixed inset-0 z-[99999] flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-8 flex flex-col items-center gap-4 border-2 border-red-500">
            <h2 className="text-2xl font-bold text-red-600">Tu sesión ha expirado</h2>
            <p className="text-gray-700 dark:text-gray-200">Por seguridad, debes iniciar sesión nuevamente.</p>
            <button
              className="mt-4 px-6 py-3 rounded-xl bg-gradient-to-r from-red-500 to-pink-500 text-white font-semibold shadow-lg hover:shadow-xl transition-all"
              onClick={() => { window.location.href = '/login'; }}
            >
              Iniciar sesión
            </button>
          </div>
        </div>
      )}
      {isAuthPage ? (
        <AuthLayout>
          {routes}
        </AuthLayout>
      ) : (
        <Layout>
          <main>
            {routes}
          </main>
        </Layout>
      )}
    </ToastProvider>
  )
}
