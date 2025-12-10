// Tipos explícitos para mensajes y respuestas
type Respuesta = {
  id: number;
  autor: string;
  rol: string;
  avatar: string;
  texto: string;
  fecha: string;
};

type Mensaje = {
  id: number;
  autor: string;
  rol: string;
  avatar: string;
  texto: string;
  fecha: string;
  tipo: 'anuncio' | 'pregunta' | 'recordatorio' | 'mensaje';
  fijado: boolean;
  reacciones: { emoji: string; usuarios: string[]; cantidad: number }[];
  respuestas: Respuesta[];
  archivos: { nombre: string; tipo: string; tamaño: string }[];
};
import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, Edit3, Eye, File, Filter, Heart, Image, MoreVertical, Search, Send, Trash2, Users } from 'lucide-react';
;
;
;

// Mock data para mensajes del chat tipo classroom
const mockMensajes: Mensaje[] = [
  {
    id: 1,
    autor: 'Prof. María García',
    rol: 'profesor',
    avatar: '👩‍🏫',
    texto: '¡Bienvenidos a nuestra clase de Matemáticas Avanzadas! Espero que tengan una excelente experiencia de aprendizaje.',
    fecha: '2025-01-21T09:00:00Z',
    tipo: 'anuncio',
    fijado: true,
    reacciones: [{ emoji: '👍', usuarios: ['Ana', 'Carlos', 'Luis'], cantidad: 3 }],
    respuestas: [],
    archivos: []
  },
  {
    id: 2,
    autor: 'Ana Martínez',
    rol: 'estudiante',
    avatar: '👩‍🎓',
    texto: '¡Hola profesora! ¿Podría aclarar la duda sobre integrales que mencionó ayer?',
    fecha: '2025-01-21T10:30:00Z',
    tipo: 'pregunta',
    fijado: false,
    reacciones: [{ emoji: '❓', usuarios: ['Carlos', 'Luis'], cantidad: 2 }],
    respuestas: [
      {
        id: 201,
        autor: 'Prof. María García',
        rol: 'profesor',
        avatar: '👩‍🏫',
        texto: 'Por supuesto Ana, revisaremos las integrales por partes en la próxima clase. Mientras tanto, pueden revisar el material que subí.',
        fecha: '2025-01-21T11:00:00Z'
      }
    ],
    archivos: []
  },
  {
    id: 3,
    autor: 'Carlos Rodríguez',
    rol: 'estudiante',
    avatar: '👨‍🎓',
    texto: 'Hola a todos! ¿Alguien tiene el libro de referencia en PDF?',
    fecha: '2025-01-21T14:15:00Z',
    tipo: 'mensaje',
    fijado: false,
    reacciones: [],
    respuestas: [
      {
        id: 301,
        autor: 'Luis González',
        rol: 'estudiante',
        avatar: '👨‍🎓',
        texto: 'Yo lo tengo, te lo comparto por mensaje privado.',
        fecha: '2025-01-21T14:20:00Z'
      }
    ],
    archivos: []
  },
  {
    id: 4,
    autor: 'Prof. María García',
    rol: 'profesor',
    avatar: '👩‍🏫',
    texto: 'Recordatorio: El examen será el próximo viernes. Estudien los capítulos 5 y 6.',
    fecha: '2025-01-21T16:00:00Z',
    tipo: 'recordatorio',
    fijado: false,
    reacciones: [{ emoji: '📚', usuarios: ['Ana', 'Carlos', 'Luis', 'María'], cantidad: 4 }],
    respuestas: [],
    archivos: [
      { nombre: 'Guía_Examen.pdf', tipo: 'pdf', tamaño: '2.3 MB' },
      { nombre: 'Ejercicios_Practica.docx', tipo: 'docx', tamaño: '1.1 MB' }
    ]
  }
];

const tiposMensaje = {
  anuncio: { color: 'from-blue-500 to-cyan-500', icono: '📢', label: 'Anuncio' },
  pregunta: { color: 'from-orange-500 to-yellow-500', icono: '❓', label: 'Pregunta' },
  recordatorio: { color: 'from-red-500 to-pink-500', icono: '⏰', label: 'Recordatorio' },
  mensaje: { color: 'from-gray-500 to-gray-600', icono: '💬', label: 'Mensaje' }
};

export default function ChatClasePage() {
  const [mensajes, setMensajes] = useState<Mensaje[]>(mockMensajes);
  const [nuevoMensaje, setNuevoMensaje] = useState('');
  const [tipoMensaje, setTipoMensaje] = useState('mensaje');
  const [busqueda, setBusqueda] = useState('');
  const [filtroTipo, setFiltroTipo] = useState('todos');
  const [mostrarEmojis, setMostrarEmojis] = useState(false);
  const [respondiendo, setRespondiendo] = useState<number | null>(null);
  const chatRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Usuario actual (mock)
  const usuarioActual = {
    nombre: 'Estudiante Demo',
    rol: 'estudiante',
    avatar: '👨‍🎓'
  };

  // Filtrar mensajes
  const mensajesFiltrados = mensajes.filter(mensaje => {
    const coincideBusqueda = mensaje.texto.toLowerCase().includes(busqueda.toLowerCase()) ||
                           mensaje.autor.toLowerCase().includes(busqueda.toLowerCase());
    const coincideTipo = filtroTipo === 'todos' || mensaje.tipo === filtroTipo;
    return coincideBusqueda && coincideTipo;
  });

  // Ordenar mensajes: fijados primero, luego por fecha
  const mensajesOrdenados = [...mensajesFiltrados].sort((a, b) => {
    if (a.fijado && !b.fijado) return -1;
    if (!a.fijado && b.fijado) return 1;
    return new Date(a.fecha).getTime() - new Date(b.fecha).getTime();
  });

  const enviarMensaje = () => {
    if (!nuevoMensaje.trim()) return;

    const mensaje = {
      id: Date.now(),
      autor: usuarioActual.nombre,
      rol: usuarioActual.rol,
      avatar: usuarioActual.avatar,
      texto: nuevoMensaje,
      fecha: new Date().toISOString(),
      tipo: tipoMensaje as 'anuncio' | 'pregunta' | 'recordatorio' | 'mensaje',
      fijado: false,
      reacciones: [],
      respuestas: [],
      archivos: []
    };

    if (respondiendo) {
      // Agregar como respuesta
      setMensajes(prev => prev.map(msg => {
        if (msg.id === respondiendo) {
          const respuestas = Array.isArray(msg.respuestas) ? msg.respuestas : [];
          return { ...msg, respuestas: [...respuestas, { ...mensaje, id: Date.now() + 1 }] };
        }
        return msg;
      }));
      setRespondiendo(null);
    } else {
      // Agregar como mensaje nuevo
      setMensajes([...mensajes, mensaje]);
    }

    setNuevoMensaje('');
    
    // Scroll al final
    setTimeout(() => {
      chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' });
    }, 100);
  };

  const agregarReaccion = (mensajeId: number, emoji: string) => {
    setMensajes(prev => prev.map(msg => {
      if (msg.id === mensajeId) {
        const reaccionExistente = msg.reacciones.find(r => r.emoji === emoji);
        if (reaccionExistente) {
          // Si ya reaccionó, quitar reacción
          if (reaccionExistente.usuarios.includes(usuarioActual.nombre)) {
            return {
              ...msg,
              reacciones: msg.reacciones.map(r => 
                r.emoji === emoji 
                  ? { ...r, usuarios: r.usuarios.filter(u => u !== usuarioActual.nombre), cantidad: r.cantidad - 1 }
                  : r
              ).filter(r => r.cantidad > 0)
            };
          } else {
            // Agregar reacción
            return {
              ...msg,
              reacciones: msg.reacciones.map(r => 
                r.emoji === emoji 
                  ? { ...r, usuarios: [...r.usuarios, usuarioActual.nombre], cantidad: r.cantidad + 1 }
                  : r
              )
            };
          }
        } else {
          // Nueva reacción
          return {
            ...msg,
            reacciones: [...msg.reacciones, { emoji, usuarios: [usuarioActual.nombre], cantidad: 1 }]
          };
        }
      }
      return msg;
    }));
  };

  const formatearFecha = (fecha: string) => {
    const date = new Date(fecha);
    const ahora = new Date();
    const esHoy = date.toDateString() === ahora.toDateString();
    
    if (esHoy) {
      return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
    }
  };

  useEffect(() => {
    // Scroll al final al cargar
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' });
  }, []);

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header del chat */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex-shrink-0 p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-violet-50 to-purple-50 dark:from-gray-800 dark:to-gray-700"
      >
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Chat de Clase
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Matemáticas Avanzadas • 28 participantes
              </p>
            </div>
          </div>

          {/* Controles de búsqueda y filtros */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Buscar mensajes..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                className="pl-10 pr-4 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all duration-300 w-48"
              />
            </div>

            <select
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value)}
              className="px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all duration-300"
            >
              <option value="todos">Todos</option>
              <option value="anuncio">Anuncios</option>
              <option value="pregunta">Preguntas</option>
              <option value="recordatorio">Recordatorios</option>
              <option value="mensaje">Mensajes</option>
            </select>
          </div>
        </div>

        {/* Respondiendo a... */}
        {respondiendo && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-4 p-3 bg-violet-100 dark:bg-violet-900/30 rounded-lg border-l-4 border-violet-500"
          >
            <div className="flex items-center justify-between">
              <p className="text-sm text-violet-700 dark:text-violet-300">
                Respondiendo a {mensajes.find(m => m.id === respondiendo)?.autor}
              </p>
              <button
                onClick={() => setRespondiendo(null)}
                className="text-violet-600 hover:text-violet-800 dark:text-violet-400 dark:hover:text-violet-200"
              >
                ✕
              </button>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Lista de mensajes */}
      <div
        ref={chatRef}
        className="flex-1 overflow-y-auto p-6 space-y-6"
        style={{ maxHeight: 'calc(100vh - 300px)' }}
      >
        <AnimatePresence>
          {mensajesOrdenados.map((mensaje, idx) => {
            const tipoInfo = tiposMensaje[mensaje.tipo as keyof typeof tiposMensaje];
            return (
              <motion.div
                key={mensaje.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 * idx }}
                className={`relative ${mensaje.fijado ? 'ring-2 ring-yellow-300 dark:ring-yellow-600' : ''}`}
              >
                {mensaje.fijado && (
                  <div className="absolute -top-2 -left-2 bg-yellow-500 text-white p-1 rounded-full">
                    <BiPin className="w-3 h-3" />
                  </div>
                )}

                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                  {/* Header del mensaje */}
                  <div className={`p-4 bg-gradient-to-r ${tipoInfo.color} text-white`}>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{mensaje.avatar}</span>
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="font-semibold">
                              {(() => {
                                if (typeof mensaje.autor === 'object' && mensaje.autor?.nombre) {
                                  return `${mensaje.autor.nombre} ${mensaje.autor.apellido || ''}`.trim();
                                } else if (typeof mensaje.autor === 'string') {
                                  return mensaje.autor;
                                } else {
                                  return 'Usuario';
                                }
                              })()}
                            </h4>
                            <span className="px-2 py-1 bg-white/20 rounded-full text-xs font-medium">
                              {mensaje.rol}
                            </span>
                            {mensaje.tipo !== 'mensaje' && (
                              <span className="px-2 py-1 bg-white/20 rounded-full text-xs font-medium flex items-center gap-1">
                                <span>{tipoInfo.icono}</span>
                                {tipoInfo.label}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-white/80">
                            {formatearFecha(mensaje.fecha)}
                          </p>
                        </div>
                      </div>

                      <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Contenido del mensaje */}
                  <div className="p-4">
                    <p className="text-gray-900 dark:text-white mb-4 leading-relaxed">
                      {mensaje.texto}
                    </p>

                    {/* Archivos adjuntos */}
                    {mensaje.archivos.length > 0 && (
                      <div className="mb-4 space-y-2">
                        {mensaje.archivos.map((archivo, idx) => (
                          <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <File className="w-5 h-5 text-gray-500" />
                            <div className="flex-1">
                              <p className="font-medium text-gray-900 dark:text-white">{archivo.nombre}</p>
                              <p className="text-sm text-gray-500">{archivo.tamaño}</p>
                            </div>
                            <button className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors">
                              <Download className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Reacciones */}
                    {mensaje.reacciones.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-4">
                        {mensaje.reacciones.map((reaccion, idx) => (
                          <button
                            key={idx}
                            onClick={() => agregarReaccion(mensaje.id, reaccion.emoji)}
                            className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm transition-all duration-300 ${
                              reaccion.usuarios.includes(usuarioActual.nombre)
                                ? 'bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300 ring-2 ring-violet-300'
                                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                            }`}
                          >
                            <span>{reaccion.emoji}</span>
                            <span className="font-medium">{reaccion.cantidad}</span>
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Acciones */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {['👍', '❤️', '😊', '👏', '🔥'].map(emoji => (
                          <button
                            key={emoji}
                            onClick={() => agregarReaccion(mensaje.id, emoji)}
                            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                          >
                            {emoji}
                          </button>
                        ))}
                      </div>

                      <button
                        onClick={() => setRespondiendo(mensaje.id)}
                        className="flex items-center gap-2 px-3 py-2 text-gray-600 dark:text-gray-400 hover:text-violet-600 dark:hover:text-violet-400 hover:bg-violet-50 dark:hover:bg-violet-900/30 rounded-lg transition-all duration-300"
                      >
                        <BiReply className="w-4 h-4" />
                        Responder
                      </button>
                    </div>

                    {/* Respuestas */}
                    {mensaje.respuestas.length > 0 && (
                      <div className="mt-4 space-y-3 border-l-2 border-violet-200 dark:border-violet-700 pl-4">
                        {mensaje.respuestas.map((respuesta, idx) => (
                          <motion.div
                            key={respuesta.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.1 * idx }}
                            className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3"
                          >
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-lg">{respuesta.avatar}</span>
                              <span className="font-semibold text-gray-900 dark:text-white text-sm">
                                {(() => {
                                  if (typeof respuesta.autor === 'object' && respuesta.autor?.nombre) {
                                    return `${respuesta.autor.nombre} ${respuesta.autor.apellido || ''}`.trim();
                                  } else if (typeof respuesta.autor === 'string') {
                                    return respuesta.autor;
                                  } else {
                                    return 'Usuario';
                                  }
                                })()}
                              </span>
                              <span className="text-xs text-gray-500">
                                {formatearFecha(respuesta.fecha)}
                              </span>
                            </div>
                            <p className="text-gray-800 dark:text-gray-200 text-sm">
                              {respuesta.texto}
                            </p>
                          </motion.div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {mensajesOrdenados.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">
              No hay mensajes
            </h3>
            <p className="text-gray-500">
              {busqueda ? 'No se encontraron mensajes con esa búsqueda' : 'Sé el primero en escribir un mensaje'}
            </p>
          </div>
        )}
      </div>

      {/* Input para nuevo mensaje */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex-shrink-0 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800"
      >
        {/* Selector de tipo de mensaje (solo para profesores) */}
        {usuarioActual.rol === 'profesor' && (
          <div className="mb-4">
            <div className="flex gap-2">
              {Object.entries(tiposMensaje).map(([tipo, info]) => (
                <button
                  key={tipo}
                  onClick={() => setTipoMensaje(tipo)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300 flex items-center gap-2 ${
                    tipoMensaje === tipo
                      ? `bg-gradient-to-r ${info.color} text-white shadow-lg`
                      : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }`}
                >
                  <span>{info.icono}</span>
                  {info.label}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={nuevoMensaje}
              onChange={(e) => setNuevoMensaje(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && enviarMensaje()}
              placeholder={respondiendo ? 'Escribe tu respuesta...' : 'Escribe un mensaje...'}
              className="w-full px-4 py-3 pr-24 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all duration-300 resize-none"
            />
            
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
              <button
                type="button"
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                <FiPaperclip className="w-4 h-4 text-gray-500" />
              </button>
              <button
                type="button"
                onClick={() => setMostrarEmojis(!mostrarEmojis)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                <FiSmile className="w-4 h-4 text-gray-500" />
              </button>
            </div>
          </div>

          <motion.button
            onClick={enviarMensaje}
            disabled={!nuevoMensaje.trim()}
            className="px-6 py-3 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center gap-2"
            whileHover={{ scale: nuevoMensaje.trim() ? 1.05 : 1 }}
            whileTap={{ scale: nuevoMensaje.trim() ? 0.95 : 1 }}
          >
            <Send className="w-4 h-4" />
            Enviar
          </motion.button>
        </div>

        {/* Panel de emojis */}
        <AnimatePresence>
          {mostrarEmojis && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-3 p-3 bg-white dark:bg-gray-700 rounded-xl border border-gray-200 dark:border-gray-600"
            >
              <div className="grid grid-cols-8 gap-2">
                {['😊', '😂', '😍', '🤔', '👍', '👏', '🔥', '❤️', '🎉', '📚', '✅', '❌', '❓', '💡', '⭐', '🚀'].map(emoji => (
                  <button
                    key={emoji}
                    onClick={() => setNuevoMensaje(prev => prev + emoji)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors text-xl"
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
