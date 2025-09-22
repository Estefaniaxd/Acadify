import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { user, logout } = useAuth()

  if (!user) return null

  return (
    <div className="max-w-2xl mx-auto mt-10 p-8 bg-white dark:bg-[#18181b] rounded-xl shadow-lg">
      <h2 className="text-2xl font-bold mb-2 text-primary">¡Bienvenido, {user.username || user.email}!</h2>
      <p className="mb-4 text-gray-700 dark:text-gray-200">Tu rol: <span className="font-semibold text-accent">{user.role}</span></p>
      {user.role === 'admin' && (
        <div className="mb-4 p-4 bg-primary/10 rounded">Panel de administración: gestiona usuarios, cursos y reportes.</div>
      )}
      {user.role === 'profesor' && (
        <div className="mb-4 p-4 bg-accent/10 rounded">Panel de profesor: crea clases, asigna tareas y revisa progreso.</div>
      )}
      {user.role === 'estudiante' && (
        <div className="mb-4 p-4 bg-gray-100 dark:bg-[#222] rounded">Panel de estudiante: accede a tus cursos y gamificación.</div>
      )}
      <button onClick={logout} className="mt-4 px-4 py-2 rounded bg-primary text-white hover:bg-primary/90">Cerrar sesión</button>
    </div>
  )
}
