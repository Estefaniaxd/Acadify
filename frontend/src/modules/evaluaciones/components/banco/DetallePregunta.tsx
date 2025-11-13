import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Copy, Star, Tag } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../common/LayoutComponents';
import { BancoPregunta } from '../../types';
import { 
  TIPO_PREGUNTA_LABELS, 
  DIFICULTAD_LABELS,
  obtenerColorDificultad,
  formatearFecha
} from '../../utils';

interface DetallePreguntaProps {
  pregunta: BancoPregunta;
  onEditar: () => void;
  onDuplicar: () => void;
  onEliminar: () => void;
  onCerrar: () => void;
}

export function DetallePregunta({
  pregunta,
  onEditar,
  onDuplicar,
  onEliminar,
  onCerrar
}: DetallePreguntaProps) {
  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardHeader
          title="Detalle de Pregunta"
          subtitle="Vista completa de la pregunta del banco"
          actions={
            <div className="flex items-center space-x-2">
              <button
                onClick={onEditar}
                className="flex items-center space-x-2 px-3 py-2 text-blue-600 dark:text-blue-400 border border-blue-300 dark:border-blue-600 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
              >
                <Edit className="h-4 w-4" />
                <span>Editar</span>
              </button>
              <button
                onClick={onDuplicar}
                className="flex items-center space-x-2 px-3 py-2 text-green-600 dark:text-green-400 border border-green-300 dark:border-green-600 rounded-lg hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors"
              >
                <Copy className="h-4 w-4" />
                <span>Duplicar</span>
              </button>
              <button
                onClick={onEliminar}
                className="flex items-center space-x-2 px-3 py-2 text-red-600 dark:text-red-400 border border-red-300 dark:border-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                <Trash className="h-4 w-4" />
                <span>Eliminar</span>
              </button>
              <button
                onClick={onCerrar}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          }
        />
        <CardContent>
          <div className="space-y-8">
            {/* Información básica */}
            <div>
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                    {pregunta.titulo}
                  </h2>
                  {pregunta.descripcion && (
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      {pregunta.descripcion}
                    </p>
                  )}
                </div>
                
                <div className="flex items-center space-x-3 ml-6">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${obtenerColorDificultad(pregunta.dificultad)}`}>
                    {DIFICULTAD_LABELS[pregunta.dificultad]}
                  </span>
                  <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm">
                    {TIPO_PREGUNTA_LABELS[pregunta.tipo_pregunta]}
                  </span>
                </div>
              </div>

              {/* Estadísticas */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <Star className="h-5 w-5 text-yellow-500" />
                  </div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {pregunta.puntuacion_sugerida}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Puntos</p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <Eye className="h-5 w-5 text-blue-500" />
                  </div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {pregunta.veces_utilizada}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Usos</p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <Clock className="h-5 w-5 text-green-500" />
                  </div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {pregunta.tiempo_estimado_segundos ? Math.round(pregunta.tiempo_estimado_segundos / 60) : '-'}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Min</p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <div className="w-5 h-5 bg-purple-500 rounded"></div>
                  </div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {pregunta.promedio_aciertos ? `${Math.round(pregunta.promedio_aciertos * 100)}%` : '-'}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Aciertos</p>
                </div>
              </div>
            </div>

            {/* Multimedia */}
            {(pregunta.imagen_url || pregunta.audio_url || pregunta.video_url) && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Contenido Multimedia
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {pregunta.imagen_url && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Imagen
                      </p>
                      <img
                        src={pregunta.imagen_url}
                        alt="Imagen de la pregunta"
                        className="w-full max-h-64 object-cover rounded-lg border border-gray-200 dark:border-gray-600"
                      />
                    </div>
                  )}
                  
                  {pregunta.audio_url && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Audio
                      </p>
                      <audio
                        controls
                        className="w-full"
                        src={pregunta.audio_url}
                      />
                    </div>
                  )}
                  
                  {pregunta.video_url && (
                    <div className="md:col-span-2">
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Video
                      </p>
                      <video
                        controls
                        className="w-full max-h-64 rounded-lg"
                        src={pregunta.video_url}
                      />
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Opciones de respuesta */}
            {pregunta.opciones_respuesta && pregunta.opciones_respuesta.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Opciones de Respuesta
                </h3>
                <div className="space-y-3">
                  {pregunta.opciones_respuesta.map((opcion, index) => (
                    <motion.div
                      key={opcion.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`p-4 border rounded-lg ${
                        opcion.es_correcta
                          ? 'border-green-300 bg-green-50 dark:bg-green-900/20'
                          : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900 dark:text-white">
                            {String.fromCharCode(65 + index)}. {opcion.texto}
                          </p>
                          {opcion.explicacion && (
                            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                              {opcion.explicacion}
                            </p>
                          )}
                        </div>
                        {opcion.es_correcta && (
                          <span className="ml-3 px-2 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full text-xs font-medium">
                            Correcta
                          </span>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Explicación */}
            {pregunta.explicacion && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Explicación
                </h3>
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p className="text-blue-700 dark:text-blue-300">
                    {pregunta.explicacion}
                  </p>
                </div>
              </div>
            )}

            {/* Metadatos */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Clasificación
                </h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Materia
                    </p>
                    <p className="text-gray-900 dark:text-white">{pregunta.materia}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Tema
                    </p>
                    <p className="text-gray-900 dark:text-white">{pregunta.tema}</p>
                  </div>
                  {pregunta.subtema && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Subtema
                      </p>
                      <p className="text-gray-900 dark:text-white">{pregunta.subtema}</p>
                    </div>
                  )}
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Categoría
                    </p>
                    <p className="text-gray-900 dark:text-white">{pregunta.categoria}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Nivel Educativo
                    </p>
                    <p className="text-gray-900 dark:text-white">{pregunta.nivel_educativo}</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Información Adicional
                </h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Estado
                    </p>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      pregunta.estado_revision === 'APROBADO'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : pregunta.estado_revision === 'PENDIENTE'
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}>
                      {pregunta.estado_revision}
                    </span>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Creada
                    </p>
                    <p className="text-gray-900 dark:text-white">
                      {formatearFecha(pregunta.fecha_creacion)}
                    </p>
                  </div>
                  
                  {pregunta.fecha_actualizacion && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Última actualización
                      </p>
                      <p className="text-gray-900 dark:text-white">
                        {formatearFecha(pregunta.fecha_actualizacion)}
                      </p>
                    </div>
                  )}
                  
                  {pregunta.ultima_vez_utilizada && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Último uso
                      </p>
                      <p className="text-gray-900 dark:text-white">
                        {formatearFecha(pregunta.ultima_vez_utilizada)}
                      </p>
                    </div>
                  )}

                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Visibilidad
                    </p>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      pregunta.es_publica
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                    }`}>
                      {pregunta.es_publica ? 'Pública' : 'Privada'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Etiquetas/Tags */}
            {pregunta.tags && pregunta.tags.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Etiquetas
                </h3>
                <div className="flex flex-wrap gap-2">
                  {pregunta.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-sm"
                    >
                      <Tag className="h-3 w-3 mr-1" />
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}