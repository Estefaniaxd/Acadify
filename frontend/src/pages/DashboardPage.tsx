import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user?.role) {
      // Redirigir al dashboard específico según el rol
      switch (user.role) {
        case 'admin':
          navigate('/dashboard-admin', { replace: true });
          break;
        case 'coordinador':
          navigate('/dashboard-coordinador', { replace: true });
          break;
        case 'profesor':
          navigate('/dashboard-teacher', { replace: true });
          break;
        case 'estudiante':
          navigate('/dashboard-student', { replace: true });
          break;
        default:
          // Si no hay rol específico, mostrar dashboard genérico
          navigate('/dashboard-student', { replace: true });
      }
    } else {
      // Si no hay usuario, redirigir a login
      navigate('/login', { replace: true });
    }
  }, [user, navigate]);

  // Mostrar loading mientras se redirige
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">Cargando panel de control...</p>
      </div>
    </div>
  );
}
