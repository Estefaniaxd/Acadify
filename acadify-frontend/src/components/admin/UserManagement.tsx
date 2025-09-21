import React, { useEffect, useState } from 'react';
import adminService from '../../services/adminService';

interface User {
  usuario_id: string;
  nombres: string;
  apellidos: string;
  correo_institucional?: string;
  username?: string;
  rol: string;
  estado_cuenta: string;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      setError('');
      try {
        // Ajusta este método según tu backend
        const data = await adminService.getUsers();
        setUsers(data);
      } catch (err: any) {
        setError('Error al cargar usuarios');
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Gestión de Usuarios</h2>
      {loading && <p>Cargando usuarios...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && !error && (
        <table className="min-w-full bg-white border rounded-xl">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b">Nombre</th>
              <th className="py-2 px-4 border-b">Correo/Usuario</th>
              <th className="py-2 px-4 border-b">Rol</th>
              <th className="py-2 px-4 border-b">Estado</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.usuario_id}>
                <td className="py-2 px-4 border-b">{user.nombres} {user.apellidos}</td>
                <td className="py-2 px-4 border-b">{user.correo_institucional || user.username}</td>
                <td className="py-2 px-4 border-b">{user.rol}</td>
                <td className="py-2 px-4 border-b">{user.estado_cuenta}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default UserManagement;
