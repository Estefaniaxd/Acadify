import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import AdminPanel from '../components/AdminPanel';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Acceso no autorizado
          </h2>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="py-10">
        <main>
          <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div className="px-4 py-8 sm:px-0">
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  Bienvenido, {user.name}
                </h1>
                <p className="mt-2 text-gray-600 dark:text-gray-400">
                  Rol: {user.role === 'admin' ? 'Administrador' : 'Usuario'}
                </p>
              </div>

              {user.role === 'admin' ? (
                <AdminPanel />
              ) : (
                <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                    Panel de Usuario
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Contenido para usuarios regulares aquí.
                  </p>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
