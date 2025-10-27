// Panel principal para el rol Coordinador
import { useEffect, useState } from 'react';
import InstitucionCoordinador from './InstitucionCoordinador';
import ClasesCoordinador from './ClasesCoordinador';
import ProfesoresCoordinador from './ProfesoresCoordinador';
import EstadisticasCoordinador from './EstadisticasCoordinador';
import InvitacionesCoordinador from './InvitacionesCoordinador';
import { getInvitacionesPendientes, aceptarInvitacion } from './api';

export default function PanelCoordinador() {

  const [invitaciones, setInvitaciones] = useState<{ id: number, institucion: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getInvitacionesPendientes()
      .then(data => {
        setInvitaciones(data);
        setLoading(false);
      })
      .catch(() => {
        setError('Error al cargar invitaciones');
        setLoading(false);
      });
  }, []);

  const handleAceptar = async (id: number) => {
    try {
      await aceptarInvitacion(id);
      setInvitaciones(invitaciones.filter(i => i.id !== id));
    } catch {
      setError('Error al aceptar invitación');
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6 text-primary">Panel de Coordinador</h1>
      {loading ? (
        <div className="text-gray-500">Cargando invitaciones...</div>
      ) : (
        <InvitacionesCoordinador invitaciones={invitaciones} onAceptar={handleAceptar} />
      )}
      {error && <div className="text-red-600 mb-2">{error}</div>}
      <InstitucionCoordinador />
      <ClasesCoordinador />
      <ProfesoresCoordinador />
      <EstadisticasCoordinador />
    </div>
  );
}
