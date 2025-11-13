import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, Check, X, Mail, Phone, Calendar, Shield } from 'lucide-react';

interface UsuarioPendiente {
  id: string;
  nombre: string;
  email: string;
  telefono: string;
  rolSolicitado: string;
  institucion: string;
  fechaSolicitud: string;
  documento: string;
}

// TODO: Reemplazar con datos reales de la API
const mockUsuarios: UsuarioPendiente[] = [
  {
    id: '1',
    nombre: 'Juan Pérez',
    email: 'juan.perez@mail.com',
    telefono: '+57 300 1234567',
    rolSolicitado: 'Profesor',
    institucion: 'SENA',
    fechaSolicitud: '2024-11-08',
    documento: '1234567890'
  },
  {
    id: '2',
    nombre: 'María García',
    email: 'maria.garcia@mail.com',
    telefono: '+57 310 9876543',
    rolSolicitado: 'Coordinador',
    institucion: 'Universidad Nacional',
    fechaSolicitud: '2024-11-07',
    documento: '0987654321'
  }
];

export default function AdminUsuariosPendientesPage() {
  const [usuarios] = useState<UsuarioPendiente[]>(mockUsuarios);

  const handleAprobar = (id: string) => {
    // TODO: Implementar aprobación
    alert(`Usuario ${id} aprobado`);
  };

  const handleRechazar = (id: string) => {
    if (confirm('¿Rechazar esta solicitud?')) {
      // TODO: Implementar rechazo
      alert(`Usuario ${id} rechazado`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Users className="w-8 h-8 text-blue-600" />
            Usuarios Pendientes de Aprobación
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Revisa y aprueba las solicitudes de nuevos usuarios
          </p>
        </motion.div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-4">
          <div className="text-center p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg mb-4">
            <div className="text-2xl font-bold text-yellow-600">{usuarios.length}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Solicitudes pendientes</div>
          </div>

          <div className="space-y-4">
            {usuarios.map((usuario, index) => (
              <motion.div
                key={usuario.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 border border-gray-200 dark:border-gray-600"
              >
                <div className="flex flex-col md:flex-row justify-between gap-4">
                  <div className="space-y-3 flex-1">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                      {usuario.nombre}
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                        <Mail className="w-4 h-4" />
                        {usuario.email}
                      </div>
                      <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                        <Phone className="w-4 h-4" />
                        {usuario.telefono}
                      </div>
                      <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                        <Shield className="w-4 h-4" />
                        {usuario.rolSolicitado} - {usuario.institucion}
                      </div>
                      <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                        <Calendar className="w-4 h-4" />
                        {usuario.fechaSolicitud}
                      </div>
                    </div>
                  </div>
                  <div className="flex md:flex-col gap-2">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleAprobar(usuario.id)}
                      className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <Check className="w-4 h-4" />
                      Aprobar
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleRechazar(usuario.id)}
                      className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      <X className="w-4 h-4" />
                      Rechazar
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
