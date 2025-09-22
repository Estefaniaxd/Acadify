import { useAuth } from '../context/AuthContext'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import StudentDashboard from './DashboardStudent'
import TeacherDashboard from './DashboardTeacher'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!user) {
      navigate('/login')
      return
    }
  }, [user, navigate])

  if (!user) return null

  // Renderizar dashboard específico según el rol
  switch (user.role) {
    case 'estudiante':
      return <StudentDashboard />
    case 'profesor':
      return <TeacherDashboard />
    case 'admin':
      // Por ahora mostrar el dashboard del profesor para admin
      // Más tarde podemos crear un dashboard específico para admin
      return <TeacherDashboard />
    default:
      return <StudentDashboard />
  }
}
