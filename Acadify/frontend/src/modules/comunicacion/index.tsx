import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiMessageSquare, 
  FiUsers, 
  FiVideo,
  FiPhone,
  FiSend,
  FiPaperclip,
  FiSmile,
  FiSearch,
  FiMoreVertical
} from 'react-icons/fi';

interface Chat {
  id: string;
  nombre: string;
  tipo: 'individual' | 'grupo' | 'clase';
  ultimoMensaje: string;
  timestamp: string;
  noLeidos: number;
  avatar?: string;
  participantes?: string[];
}

interface Mensaje {
  id: string;
  autor: string;
  contenido: string;
  timestamp: string;
  tipo: 'texto' | 'archivo' | 'imagen';
  esPropio: boolean;
}

const chatsMock: Chat[] = [
  {
    id: '1',
    nombre: 'Matemáticas 11A',
    tipo: 'clase',
    ultimoMensaje: 'La tarea para mañana está en la plataforma',
    timestamp: '15:30',
    noLeidos: 3,
    participantes: ['Prof. García', '28 estudiantes']
  },
  {
    id: '2',
    nombre: 'Ana García',
    tipo: 'individual',
    ultimoMensaje: '¿Podemos revisar el ejercicio 5?',
    timestamp: '14:15',
    noLeidos: 1
  },
  {
    id: '3',
    nombre: 'Grupo de Estudio',
    tipo: 'grupo',
    ultimoMensaje: 'Luis: Nos vemos en la biblioteca',
    timestamp: '12:45',
    noLeidos: 0,
    participantes: ['Luis', 'María', 'Carlos', 'Sofía']
  }
];

const mensajesMock: Mensaje[] = [
  {
    id: '1',
    autor: 'Prof. García',
    contenido: 'Buenos días clase, recuerden que hoy revisaremos la tarea',
    timestamp: '10:00',
    tipo: 'texto',
    esPropio: false
  },
  {
    id: '2',
    autor: 'Tú',
    contenido: 'Profesora, tengo una duda sobre el ejercicio 3',
    timestamp: '10:15',
    tipo: 'texto',
    esPropio: true
  },
  {
    id: '3',
    autor: 'Prof. García',
    contenido: 'Perfecto, lo revisamos en clase',
    timestamp: '10:16',
    tipo: 'texto',
    esPropio: false
  }
];

export default function ModuloComunicacion() {
  const [activeTab, setActiveTab] = useState<'chats' | 'videollamadas' | 'notificaciones'>('chats');
  const [chatActivo, setChatActivo] = useState<string | null>('1');
  const [nuevoMensaje, setNuevoMensaje] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const chatsFiltrados = chatsMock.filter(chat =>
    chat.nombre.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const enviarMensaje = () => {
    if (nuevoMensaje.trim()) {
      // Aquí se enviaría el mensaje al backend
      console.log('Enviando mensaje:', nuevoMensaje);
      setNuevoMensaje('');
    }
  };

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case 'individual': return FiMessageSquare;
      case 'grupo': return FiUsers;
      case 'clase': return FiVideo;
      default: return FiMessageSquare;
    }
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 via-white to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
      <div className="max-w-7xl mx-auto p-6 mt-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Centro de Comunicación
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Chats, videollamadas y notificaciones en tiempo real
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap bg-white dark:bg-gray-800 rounded-xl p-2 mb-6 border border-gray-200 dark:border-gray-700">
          {[
            { key: 'chats', label: 'Chats', icon: FiMessageSquare },
            { key: 'videollamadas', label: 'Videollamadas', icon: FiVideo },
            { key: 'notificaciones', label: 'Notificaciones', icon: FiUsers }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`
                flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                ${activeTab === tab.key
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'
                }
              `}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'chats' && (
            <motion.div
              key="chats"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]"
            >
              {/* Lista de Chats */}
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <div className="relative">
                    <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      type="text"
                      placeholder="Buscar chats..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-sm"
                    />
                  </div>
                </div>
                
                <div className="overflow-y-auto h-full">
                  {chatsFiltrados.map((chat) => {
                    const TipoIcon = getTipoIcon(chat.tipo);
                    return (
                      <button
                        key={chat.id}
                        onClick={() => setChatActivo(chat.id)}
                        className={`w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                          chatActivo === chat.id ? 'bg-blue-50 dark:bg-blue-900/20 border-r-2 border-blue-500' : ''
                        }`}
                      >
                        <div className="flex items-start space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                            <TipoIcon className="w-5 h-5 text-white" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <p className="font-medium text-gray-900 dark:text-white text-sm truncate">
                                {chat.nombre}
                              </p>
                              <div className="flex items-center space-x-2">
                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                  {chat.timestamp}
                                </span>
                                {chat.noLeidos > 0 && (
                                  <span className="bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                                    {chat.noLeidos}
                                  </span>
                                )}
                              </div>
                            </div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-1">
                              {chat.ultimoMensaje}
                            </p>
                            {chat.participantes && (
                              <p className="text-xs text-gray-400 dark:text-gray-500 truncate mt-1">
                                {chat.participantes.join(', ')}
                              </p>
                            )}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Chat Activo */}
              <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden flex flex-col">
                {chatActivo ? (
                  <>
                    {/* Header del Chat */}
                    <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                            <FiMessageSquare className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white">
                              {chatsMock.find(c => c.id === chatActivo)?.nombre}
                            </h3>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              En línea
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                            <FiVideo className="w-5 h-5" />
                          </button>
                          <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                            <FiPhone className="w-5 h-5" />
                          </button>
                          <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                            <FiMoreVertical className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Mensajes */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                      {mensajesMock.map((mensaje) => (
                        <div
                          key={mensaje.id}
                          className={`flex ${mensaje.esPropio ? 'justify-end' : 'justify-start'}`}
                        >
                          <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                            mensaje.esPropio
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                          }`}>
                            {!mensaje.esPropio && (
                              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                                {mensaje.autor}
                              </p>
                            )}
                            <p className="text-sm">{mensaje.contenido}</p>
                            <p className={`text-xs mt-1 ${
                              mensaje.esPropio ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
                            }`}>
                              {mensaje.timestamp}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Input de Mensaje */}
                    <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                      <div className="flex items-center space-x-2">
                        <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                          <FiPaperclip className="w-5 h-5" />
                        </button>
                        <div className="flex-1 relative">
                          <input
                            type="text"
                            placeholder="Escribe un mensaje..."
                            value={nuevoMensaje}
                            onChange={(e) => setNuevoMensaje(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && enviarMensaje()}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                          />
                        </div>
                        <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                          <FiSmile className="w-5 h-5" />
                        </button>
                        <button
                          onClick={enviarMensaje}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          <FiSend className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                      <FiMessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500 dark:text-gray-400">
                        Selecciona un chat para comenzar
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'videollamadas' && (
            <motion.div
              key="videollamadas"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700 text-center"
            >
              <FiVideo className="w-16 h-16 text-blue-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Videollamadas
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Inicia o únete a videollamadas con tu clase
              </p>
              <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Iniciar Videollamada
              </button>
            </motion.div>
          )}

          {activeTab === 'notificaciones' && (
            <motion.div
              key="notificaciones"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              {[
                { titulo: 'Nueva tarea asignada', mensaje: 'Matemáticas - Ejercicios de álgebra', tiempo: '5 min' },
                { titulo: 'Mensaje de profesor', mensaje: 'Prof. García: Revisen el material adicional', tiempo: '15 min' },
                { titulo: 'Recordatorio de clase', mensaje: 'Historia Universal en 30 minutos', tiempo: '30 min' }
              ].map((notif, index) => (
                <div key={index} className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">{notif.titulo}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{notif.mensaje}</p>
                    </div>
                    <span className="text-xs text-gray-500 dark:text-gray-400">{notif.tiempo}</span>
                  </div>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}