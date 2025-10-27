// Panel principal para el rol Profesor
import ClasesProfesor from './ClasesProfesor';
import TareasProfesor from './TareasProfesor';
import MaterialesProfesor from './MaterialesProfesor';
import ProgresoEstudiantes from './ProgresoEstudiantes';

export default function PanelProfesor() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6 text-primary">Panel de Profesor</h1>
      <ClasesProfesor />
      <TareasProfesor />
      <MaterialesProfesor />
      <ProgresoEstudiantes />
    </div>
  );
}
