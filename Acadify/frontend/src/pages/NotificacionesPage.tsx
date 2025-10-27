import React from 'react'

export default function NotificacionesPage() {
  return (
    <div className="bg-gradient-to-br from-blue-50 via-white to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900 p-6 mt-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Notificaciones
        </h1>
        
        <div className="space-y-4">
          {[
            { titulo: 'Nueva tarea asignada', mensaje: 'Tienes una nueva tarea en Matemáticas', tiempo: '5 min', tipo: 'tarea' },
            { titulo: 'Mensaje de profesor', mensaje: 'Prof. García envió un mensaje', tiempo: '15 min', tipo: 'mensaje' },
            { titulo: 'Recordatorio', mensaje: 'Clase de Historia en 30 minutos', tiempo: '25 min', tipo: 'recordatorio' }
          ].map((notif, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">{notif.titulo}</h3>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">{notif.mensaje}</p>
                </div>
                <span className="text-sm text-gray-500 dark:text-gray-400">{notif.tiempo}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
