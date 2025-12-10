import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Si estamos cargando, no hacer nada aún
    if (loading) {
      console.log('DashboardPage: Auth loading...');
      return;
    }

    console.log('DashboardPage: Checking user state', { user, role: user?.role });

    if (user?.role) {
      console.log('DashboardPage: User has role, redirecting to specific dashboard', user.role);
      // Redirigir al dashboard específico según el rol
      switch (user.role) {
        case 'admin':
        case 'administrador': // Soporte para ambas variantes
          navigate('/dashboard-admin', { replace: true });
          break;
        case 'coordinador':
          navigate('/dashboard-coordinador', { replace: true });
          break;
        case 'profesor':
        case 'docente': // Backend retorna 'docente'
          navigate('/dashboard-teacher', { replace: true });
          break;
        case 'estudiante':
          navigate('/dashboard-student', { replace: true });
          break;
        default:
          // Si no hay rol específico, mostrar dashboard genérico
          console.log('DashboardPage: Unknown role, defaulting to student dashboard');
          navigate('/dashboard-student', { replace: true });
      }
    } else {
      // Si no hay usuario, redirigir a login
      console.warn('DashboardPage: No user or role found, redirecting to login');
      navigate('/login', { replace: true });
    }
  }, [user, loading, navigate]);

  // Mostrar loading mientras se redirige o se carga la sesión
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">
          {loading ? 'Verificando sesión...' : 'Cargando panel de control...'}
        </p>
      </div>
    </div>
  );
}
