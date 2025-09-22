
import { useNavigate } from 'react-router-dom';
import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const mockClases = [
	{ id: 1, name: 'Matemáticas 2025', color: 'from-blue-500 to-purple-600', students: 28 },
	{ id: 2, name: 'Historia Universal', color: 'from-emerald-500 to-blue-600', students: 24 },
	{ id: 3, name: 'Física Cuántica', color: 'from-purple-500 to-pink-600', students: 19 },
];

// Utilidad para detectar la ruta activa
import { useLocation } from 'react-router-dom';

type SidebarLeftProps = { open: boolean; onClose: () => void; role?: string };

export default function SidebarLeft({ open, onClose, role = 'estudiante' }: SidebarLeftProps) {
	const navigate = useNavigate();
	const location = useLocation();

		// Menú por rol (iconos SVG animados, microinteracciones, indicador activo)
		const menu = useMemo(() => {
			// ...iconos SVG como antes...
			if (role === 'admin') {
				return [
					{ label: 'Panel Admin', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>, path: '/admin' },
					{ label: 'Instituciones', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/></svg>, path: '/admin/instituciones' },
					{ label: 'Usuarios', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>, path: '/admin/usuarios' },
				];
			}
			if (role === 'coordinador') {
				return [
					{ label: 'Panel', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>, path: '/coordinador' },
					{ label: 'Mi Institución', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 21h18"/><path d="M5 21V7l8-4v18"/></svg>, path: '/coordinador/institucion' },
				];
			}
			if (role === 'profesor') {
				return [
					{ label: 'Panel', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/></svg>, path: '/profesor' },
					{ label: 'Mis Clases', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>, path: '/mis-clases' },
				];
			}
			// estudiante o default
			return [
				{ label: 'Mis Clases', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>, path: '/mis-clases' },
				{ label: 'Unirse a Clase', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="M12 14h.01"/></svg>, path: '/unirse-clase' },
				{ label: 'Tienda', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" x2="21" y1="6" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>, path: '/tienda' },
				{ label: 'Logros', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>, path: '/logros' },
				{ label: 'Avatar', icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>, path: '/avatar' },
			];
		}, [role]);

	// Retos y ranking (igual que antes, solo iconos SVG)
	const retos = useMemo(() => [
		{ id: 1, name: 'Desafío Semanal', desc: 'Completa 5 lecciones esta semana', progress: 60, icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="13,2 3,14 12,14 11,22 21,10 12,10"/></svg> },
		{ id: 2, name: 'Racha de Estudio', desc: 'Estudia 7 días seguidos', progress: 85, icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg> },
	], []);
	const ranking = useMemo(() => [
		{ id: 1, name: 'Tú', puntos: 1250, position: 1, avatar: 'bg-gradient-to-br from-yellow-400 to-orange-500' },
		{ id: 2, name: 'Ana García', puntos: 1180, position: 2, avatar: 'bg-gradient-to-br from-pink-400 to-purple-500' },
		{ id: 3, name: 'Luis Rodriguez', puntos: 1050, position: 3, avatar: 'bg-gradient-to-br from-blue-400 to-emerald-500' },
	], []);

		return (
			<AnimatePresence>
				{open && (
					<motion.div
						initial={{ x: -320, opacity: 0 }}
						animate={{ x: 0, opacity: 1 }}
						exit={{ x: -320, opacity: 0 }}
						transition={{ duration: 0.25, ease: 'easeOut' }}
						className="fixed top-0 left-0 h-full z-40 w-80 bg-white dark:bg-[#18181b] shadow-lg border-r border-gray-200 dark:border-gray-800"
						tabIndex={-1}
						aria-modal="true"
						role="dialog"
					>
						{/* Header */}
						<div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-gray-700">
							<span className="text-xl font-bold text-primary tracking-tight">Navegación</span>
							<button onClick={onClose} className="text-2xl text-gray-500 hover:text-primary">×</button>
						</div>
						<div className="px-6 py-4 overflow-y-auto h-[calc(100vh-64px)] flex flex-col gap-8">
							{/* Menú principal atractivo */}
							<div>
								<div className="flex flex-col gap-1">
									{menu.map((item, idx) => {
										const active = location.pathname === item.path;
										return (
											<motion.button
												key={item.label}
												onClick={() => { navigate(item.path); onClose(); }}
												className={`group flex items-center gap-3 px-3 py-2 rounded-lg relative transition-colors duration-200 font-medium text-base ${active ? 'bg-primary/10 text-primary shadow' : 'text-gray-700 dark:text-gray-200 hover:bg-primary/5 hover:text-primary'}`}
												whileHover={{ scale: 1.04 }}
												whileTap={{ scale: 0.97 }}
												initial={false}
											>
												<span className="flex items-center justify-center w-10 h-10 rounded-lg transition-all duration-200 group-hover:bg-primary/10 group-active:bg-primary/20 relative">
													<motion.span
														animate={active ? { scale: 1.18, rotate: 2 } : { scale: 1, rotate: 0 }}
														transition={{ type: 'spring', stiffness: 300, damping: 20 }}
														className="inline-block"
													>
														{item.icon}
													</motion.span>
																			{/* Eliminado indicador visual lateral para evitar superposición */}
												</span>
												<span className="text-sm tracking-tight opacity-90 group-hover:opacity-100 transition-opacity duration-200">
													{item.label}
												</span>
											</motion.button>
										);
									})}
								</div>
							</div>
						{/* Clases del estudiante */}
						{role === 'estudiante' && (
							<div>
								<div className="flex items-center justify-between mb-2">
									<span className="text-sm font-semibold text-gray-500 dark:text-gray-400">Tus Clases</span>
									<button className="text-xs text-primary hover:underline" onClick={() => navigate('/mis-clases')}>Ver todas</button>
								</div>
								<div className="flex flex-col gap-2">
									{mockClases.map((clase) => (
										<button
											key={clase.id}
											className="flex items-center justify-between px-3 py-2 rounded bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-800 dark:to-gray-900 text-gray-800 dark:text-gray-100 shadow hover:shadow-md transition-all"
											onClick={() => { navigate(`/clase/${clase.id}`); onClose(); }}
										>
											<div>
												<div className="font-semibold text-sm">{clase.name}</div>
												<div className="text-xs text-gray-500">{clase.students} estudiantes</div>
											</div>
											<div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center">
												<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>
											</div>
										</button>
									))}
								</div>
							</div>
						)}
						{/* Retos activos */}
						<div>
							<div className="flex items-center justify-between mb-2">
								<span className="text-sm font-semibold text-orange-600">Retos Activos</span>
								<button className="text-xs text-primary hover:underline" onClick={() => navigate('/retos')}>Ver todos</button>
							</div>
							<div className="flex flex-col gap-2">
								{retos.map((reto) => (
									<div key={reto.id} className="flex items-center gap-3 p-2 rounded bg-orange-50 dark:bg-orange-900/10 border border-orange-200 dark:border-orange-700">
										<div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-400 to-red-400 flex items-center justify-center text-white">
											{reto.icon}
										</div>
										<div className="flex-1 min-w-0">
											<div className="font-medium text-gray-900 dark:text-white text-sm">{reto.name}</div>
											<div className="text-gray-500 dark:text-gray-400 text-xs mb-1">{reto.desc}</div>
											<div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
												<div className="h-1.5 bg-gradient-to-r from-orange-400 to-red-400 rounded-full" style={{ width: reto.progress + '%' }} />
											</div>
										</div>
									</div>
								))}
							</div>
						</div>
						{/* Ranking semanal */}
						<div>
							<div className="flex items-center justify-between mb-2">
								<span className="text-sm font-semibold text-blue-600">Top Ranking</span>
								<button className="text-xs text-primary hover:underline" onClick={() => navigate('/ranking')}>Ver todo</button>
							</div>
							<div className="flex flex-col gap-2">
								{ranking.map((user) => (
									<div key={user.id} className={`flex items-center gap-3 p-2 rounded border ${user.position === 1 ? 'bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border-yellow-200 dark:border-yellow-700' : 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700'}`}>
										<div className={`w-6 h-6 rounded-lg ${user.avatar} flex items-center justify-center text-white text-xs font-bold`}>{user.position}</div>
										<div className={`w-8 h-8 rounded-full ${user.avatar} flex items-center justify-center`}>
											<svg width="16" height="16" viewBox="0 0 24 24" fill="white" stroke="white" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
										</div>
										<div className="flex-1">
											<div className="font-medium text-gray-900 dark:text-white text-sm">{user.name}</div>
											<div className="text-gray-500 dark:text-gray-400 text-xs">{user.puntos} puntos</div>
										</div>
										{user.position <= 3 && (
											<div className="text-yellow-500">
												<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>
											</div>
										)}
									</div>
								))}
							</div>
						</div>
					</div>
				</motion.div>
			)}
		</AnimatePresence>
	);
}
