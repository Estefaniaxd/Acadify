// Panel principal para el rol Administrador
import InstitucionesAdmin from './InstitucionesAdmin';
import UsuariosAdmin from './UsuariosAdmin';
import EstadisticasAdmin from './EstadisticasAdmin';

export default function PanelAdmin() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6 text-primary">Panel de Administrador</h1>
      <InstitucionesAdmin />
      <UsuariosAdmin />
      <EstadisticasAdmin />
    </div>
  );
}
