import ClasesEstudiante from './ClasesEstudiante';
import TareasEstudiante from './TareasEstudiante';
import RecordsEstudiante from './RecordsEstudiante';
import PuntosEstudiante from './PuntosEstudiante';
import RankingEstudiante from './RankingEstudiante';
import TiendaEstudiante from './TiendaEstudiante';
import LogrosEstudiante from './LogrosEstudiante';
import AvatarEstudiante from './AvatarEstudiante';

export default function PanelEstudiante() {
  return (
    <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <ClasesEstudiante />
        <TareasEstudiante />
        <RecordsEstudiante />
      </div>
      <div>
        <PuntosEstudiante />
        <RankingEstudiante />
        <TiendaEstudiante />
        <LogrosEstudiante />
        <AvatarEstudiante />
      </div>
    </div>
  );
}
