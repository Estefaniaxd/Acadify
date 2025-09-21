// Este archivo se elimina por completo - contenido removido

import React, { useEffect, useState } from 'react';
import adminService from '../../services/adminService';

interface Institution {
  institucion_id: string;
  nombre: string;
  direccion?: string;
  telefono?: string;
  estado?: string;
  fecha_creacion?: string;
}

const InstitutionManagement: React.FC = () => {
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchInstitutions = async () => {
      setLoading(true);
      setError('');
      try {
        // Ajusta este método según tu backend
        const data = await adminService.getInstitutions();
        setInstitutions(data);
      } catch (err: any) {
        setError('Error al cargar instituciones');
      } finally {
        setLoading(false);
      }
    };
    fetchInstitutions();
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Gestión de Instituciones</h2>
      {loading && <p>Cargando instituciones...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && !error && (
        <table className="min-w-full bg-white border rounded-xl">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b">Nombre</th>
              <th className="py-2 px-4 border-b">Dirección</th>
              <th className="py-2 px-4 border-b">Teléfono</th>
              <th className="py-2 px-4 border-b">Estado</th>
              <th className="py-2 px-4 border-b">Fecha de Creación</th>
            </tr>
          </thead>
          <tbody>
            {institutions.map((inst: Institution) => (
              <tr key={inst.institucion_id}>
                <td className="py-2 px-4 border-b">{inst.nombre}</td>
                <td className="py-2 px-4 border-b">{inst.direccion || '-'}</td>
                <td className="py-2 px-4 border-b">{inst.telefono || '-'}</td>
                <td className="py-2 px-4 border-b">{inst.estado || '-'}</td>
                <td className="py-2 px-4 border-b">{inst.fecha_creacion ? new Date(inst.fecha_creacion).toLocaleDateString() : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default InstitutionManagement;
