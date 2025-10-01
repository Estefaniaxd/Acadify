import React, { useEffect, useState } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Layout from './components/layout/Layout';
import AuthLayout from './components/layout/AuthLayout';
import { ToastProvider } from './context/ToastContext';

// Páginas principales
import Home from './pages/Home';
import DashboardPage from './pages/DashboardPage';
import NotificacionesPage from './pages/NotificacionesPage';

// Auth pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import RecoverPassword from './pages/auth/RecoverPassword';
import ResetPassword from './pages/auth/ResetPassword';

// Dashboard por roles
import DashboardAdmin from './pages/DashboardAdmin';
import DashboardCoordinador from './pages/DashboardCoordinador';
import DashboardTeacher from './pages/DashboardTeacher';
import DashboardStudent from './pages/DashboardStudent';

// Páginas académicas
import CursosPage from './pages/CursosPage';
import ClasePage from './pages/ClasePage';
import EvaluacionesPage from './pages/EvaluacionesPage';

// Páginas de gamificación
import LogrosPage from './pages/LogrosPage';
import InsigniasPage from './pages/InsigniasPage';

// Comunicación
import ModuloComunicacion from './modules/comunicacion';
import { ComunicacionPage } from './pages/comunicacion/ComunicacionPage';

// Configuración y usuario
import AjustesPage from './pages/AjustesPage';
import AyudaFaqPage from './pages/AyudaFaqPage';

// Avatar
import AvatarCustomizerPage from './pages/avatar/AvatarCustomizerPage';

// Páginas de clase específicas
import TablonPage from './pages/clase/TablonPage';
import MaterialesPage from './pages/clase/MaterialesPage';
import TareasPage from './pages/clase/TareasPage';
import CalificacionesPage from './pages/clase/CalificacionesPage';
import PersonasPage from './pages/clase/PersonasPage';
import ChatClasePage from './pages/clase/ChatClasePage';

// Páginas legales
import TratamientoDatos from './pages/legal/TratamientoDatos';
import Consentimiento from './pages/legal/Consentimiento';

// Módulos principales
import ProfilePage from './modules/perfil/ProfilePage';
import EditorAvatar from './modules/avatar/EditorAvatar';
import LogrosUsuario from './modules/logros';
import PuntosUsuario from './modules/puntos';
import NivelesUsuario from './modules/niveles';
import TiendaPuntos from './modules/tienda';

export default function App() {
	const location = useLocation();
	const [sessionExpired, setSessionExpired] = useState(false);
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

	const authPages = ['/login', '/register', '/recover', '/reset-password'];
	const isAuthPage = authPages.includes(location.pathname);

	const routes = (
			<Routes>
				{/* Página principal */}
				<Route path="/" element={<Home />} />
				
				{/* Autenticación */}
				<Route path="/login" element={<Login />} />
				<Route path="/register" element={<Register />} />
				<Route path="/recover" element={<RecoverPassword />} />
				<Route path="/reset-password" element={<ResetPassword />} />
				
				{/* Dashboard principal */}
				<Route path="/dashboard" element={<DashboardPage />} />
				
				{/* Dashboards por rol */}
				<Route path="/dashboard-admin" element={<DashboardAdmin />} />
				<Route path="/dashboard-coordinador" element={<DashboardCoordinador />} />
				<Route path="/dashboard-teacher" element={<DashboardTeacher />} />
				<Route path="/dashboard-student" element={<DashboardStudent />} />
				
				{/* Páginas principales */}
				<Route path="/notificaciones" element={<NotificacionesPage />} />
				<Route path="/mensajes" element={<ModuloComunicacion />} />
				<Route path="/comunicacion" element={<ComunicacionPage />} />
				
				{/* Académico */}
				<Route path="/cursos" element={<CursosPage />} />
				<Route path="/clase/:id" element={<ClasePage />} />
				<Route path="/evaluaciones" element={<EvaluacionesPage />} />
				
				{/* Clase específica */}
				<Route path="/clase/:id/tablon" element={<TablonPage />} />
				<Route path="/clase/:id/materiales" element={<MaterialesPage />} />
				<Route path="/clase/:id/tareas" element={<TareasPage />} />
				<Route path="/clase/:id/calificaciones" element={<CalificacionesPage />} />
				<Route path="/clase/:id/personas" element={<PersonasPage />} />
				<Route path="/clase/:id/chat" element={<ChatClasePage />} />
				
				{/* Gamificación */}
				<Route path="/logros" element={<LogrosPage />} />
				<Route path="/insignias" element={<InsigniasPage />} />
				<Route path="/logros-usuario" element={<LogrosUsuario />} />
				<Route path="/puntos" element={<PuntosUsuario />} />
				<Route path="/niveles" element={<NivelesUsuario />} />
				<Route path="/tienda" element={<TiendaPuntos />} />
				
				{/* Usuario y configuración */}
				<Route path="/perfil" element={<ProfilePage />} />
				<Route path="/perfil/:userId" element={<ProfilePage />} />
				<Route path="/ajustes" element={<AjustesPage theme={theme} setTheme={setTheme} />} />
				<Route path="/ayuda" element={<AyudaFaqPage />} />
				
				{/* Avatar */}
				<Route path="/avatar" element={<AvatarCustomizerPage />} />
				<Route path="/editor-avatar" element={<EditorAvatar />} />
				
				{/* Páginas legales */}
				<Route path="/tratamiento-datos" element={<TratamientoDatos />} />
				<Route path="/consentimiento" element={<Consentimiento />} />
			</Routes>
	);

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
	);
}
