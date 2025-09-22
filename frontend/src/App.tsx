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
import EditorPerfilPage from './pages/EditorPerfilPage';
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
import Home from './pages/Home'
import ThemeToggle from './components/ThemeToggle'
import Layout from './components/layout/Layout'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import RecoverPassword from './pages/auth/RecoverPassword'
import ResetPassword from './pages/auth/ResetPassword'
import Dashboard from './pages/Dashboard'
import { Routes, Route } from 'react-router-dom'
import AvatarCustomizerPage from './pages/avatar/AvatarCustomizerPage';
import LogrosPage from './pages/LogrosPage';
import InsigniasPage from './pages/InsigniasPage';
import AjustesPage from './pages/AjustesPage';
import PerfilPage from './pages/PerfilPage';
import BorradoresPage from './pages/BorradoresPage';
import UnirseComunidadPage from './pages/UnirseComunidadPage';
import GuardadoPage from './pages/GuardadoPage';
import HistoriaPage from './pages/HistoriaPage';

export default function App() {
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

  return (
    <Layout>
      {/* Botón de modo oscuro solo en el menú lateral derecho */}
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/recover" element={<RecoverPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/avatar" element={<AvatarCustomizerPage />} />
          <Route path="/logros" element={<LogrosPage />} />
          <Route path="/insignias" element={<InsigniasPage />} />
          <Route path="/ajustes" element={<AjustesPage theme={theme} setTheme={setTheme} />} />
          <Route path="/perfil" element={<PerfilPage />} />
          <Route path="/borradores" element={<BorradoresPage />} />
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
    <Route path="/editor-perfil" element={<EditorPerfilPage />} />
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
        </Routes>
      </main>
    </Layout>
  )
}
