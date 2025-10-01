import React, { useState, useEffect } from 'react';
import { ChatRoom } from '../../components/comunicacion';
import { 
  ChatBubbleLeftRightIcon,
  UserGroupIcon,
  AcademicCapIcon,
  DocumentTextIcon,
  PlusIcon
} from '@heroicons/react/24/outline';

interface SalaChat {
  id: string;
  nombre: string;
  descripcion?: string;
  tipo_sala: 'curso' | 'grupo' | 'tarea' | 'privado' | 'general';
  participantes_conectados: number;
  ultimo_mensaje_fecha?: string;
  ultimo_mensaje_contenido?: string;
}

export const ComunicacionPage: React.FC = () => {
  const [salas, setSalas] = useState<SalaChat[]>([]);
  const [salaActiva, setSalaActiva] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Mock user ID - en una aplicación real esto vendría del contexto de autenticación
  const currentUserId = 'user-123';

  useEffect(() => {
    // Cargar salas disponibles
    const fetchSalas = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/comunicacion/salas/mis-salas', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setSalas(data.salas || []);
        } else {
          console.error('Error cargando salas');
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSalas();
  }, []);

  const getSalaIcon = (tipo: string) => {
    switch (tipo) {
      case 'curso':
        return <AcademicCapIcon className="h-5 w-5" />;
      case 'tarea':
        return <DocumentTextIcon className="h-5 w-5" />;
      case 'grupo':
        return <UserGroupIcon className="h-5 w-5" />;
      default:
        return <ChatBubbleLeftRightIcon className="h-5 w-5" />;
    }
  };

  const getSalaColor = (tipo: string) => {
    switch (tipo) {
      case 'curso':
        return 'blue';
      case 'tarea':
        return 'purple';
      case 'grupo':
        return 'green';
      case 'privado':
        return 'pink';
      default:
        return 'gray';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando salas de chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {salaActiva ? (
          /* Vista de chat activo */
          <div className="h-[calc(100vh-8rem)] bg-white rounded-lg shadow-lg">
            <ChatRoom
              salaId={salaActiva}
              usuarioId={currentUserId}
              onClose={() => setSalaActiva(null)}
            />
          </div>
        ) : (
          /* Vista de selección de salas */
          <div>
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">Comunicación</h1>
                  <p className="mt-2 text-gray-600">
                    Chatea con tu clase, profesores y compañeros de trabajo
                  </p>
                </div>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Nueva sala
                </button>
              </div>
            </div>

            {/* Grid de salas */}
            {salas.length === 0 ? (
              <div className="text-center py-12">
                <ChatBubbleLeftRightIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No hay salas disponibles</h3>
                <p className="text-gray-600 mb-6">
                  Crea una nueva sala de chat o espera a que te inviten a una
                </p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Crear primera sala
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {salas.map((sala) => {
                  const color = getSalaColor(sala.tipo_sala);
                  
                  return (
                    <div
                      key={sala.id}
                      onClick={() => setSalaActiva(sala.id)}
                      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 hover:border-gray-300"
                    >
                      <div className="p-6">
                        {/* Header de la sala */}
                        <div className="flex items-center mb-4">
                          <div className={`w-10 h-10 bg-${color}-100 text-${color}-600 rounded-lg flex items-center justify-center mr-3`}>
                            {getSalaIcon(sala.tipo_sala)}
                          </div>
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900 truncate">
                              {sala.nombre}
                            </h3>
                            <p className="text-sm text-gray-500 capitalize">
                              {sala.tipo_sala}
                            </p>
                          </div>
                        </div>

                        {/* Descripción */}
                        {sala.descripcion && (
                          <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                            {sala.descripcion}
                          </p>
                        )}

                        {/* Último mensaje */}
                        {sala.ultimo_mensaje_contenido && (
                          <div className="bg-gray-50 rounded-lg p-3 mb-4">
                            <p className="text-sm text-gray-700 line-clamp-2">
                              {sala.ultimo_mensaje_contenido}
                            </p>
                            {sala.ultimo_mensaje_fecha && (
                              <p className="text-xs text-gray-500 mt-1">
                                {new Date(sala.ultimo_mensaje_fecha).toLocaleString()}
                              </p>
                            )}
                          </div>
                        )}

                        {/* Footer */}
                        <div className="flex items-center justify-between text-sm text-gray-500">
                          <span className="flex items-center">
                            <UserGroupIcon className="h-4 w-4 mr-1" />
                            {sala.participantes_conectados} conectados
                          </span>
                          <span className={`px-2 py-1 bg-${color}-100 text-${color}-700 rounded-full text-xs font-medium`}>
                            {sala.tipo_sala}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Sección de salas destacadas */}
            <div className="mt-12">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Salas destacadas</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Sala General */}
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg text-white p-6 cursor-pointer hover:from-blue-600 hover:to-purple-700 transition-all">
                  <div className="flex items-center mb-4">
                    <ChatBubbleLeftRightIcon className="h-8 w-8 mr-3" />
                    <div>
                      <h3 className="text-lg font-semibold">Sala General</h3>
                      <p className="text-blue-100">Chat general con @rutilio IA</p>
                    </div>
                  </div>
                  <p className="text-blue-100 text-sm">
                    Chatea con todos los estudiantes y profesores. Menciona @rutilio para obtener ayuda de la IA.
                  </p>
                </div>

                {/* Ayuda Académica */}
                <div className="bg-gradient-to-r from-green-500 to-blue-500 rounded-lg text-white p-6 cursor-pointer hover:from-green-600 hover:to-blue-600 transition-all">
                  <div className="flex items-center mb-4">
                    <AcademicCapIcon className="h-8 w-8 mr-3" />
                    <div>
                      <h3 className="text-lg font-semibold">Ayuda Académica</h3>
                      <p className="text-green-100">Dudas y consultas</p>
                    </div>
                  </div>
                  <p className="text-green-100 text-sm">
                    Espacio dedicado para resolver dudas académicas y obtener ayuda con tus tareas.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modal de crear sala (placeholder) */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96">
            <h3 className="text-lg font-semibold mb-4">Crear nueva sala</h3>
            <p className="text-gray-600 mb-4">
              Esta funcionalidad estará disponible próximamente
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancelar
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};