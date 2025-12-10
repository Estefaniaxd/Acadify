import { useNavigate, useParams } from 'react-router-dom';
import { TareaDetalle } from '../../modules/tareas/components';
import { EntregaTarea } from '../../modules/tareas/types';

export default function TareaDetallePage() {
  const { cursoId, tareaId } = useParams<{ cursoId: string; tareaId: string }>();
  const navigate = useNavigate();

  if (!cursoId || !tareaId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-[#18181b]">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-2">Error</h2>
          <p className="text-gray-600 dark:text-gray-400">
            No se pudo cargar la información de la tarea
          </p>
        </div>
      </div>
    );
  }

  const handleBack = () => {
    navigate(`/cursos/${cursoId}/clase`);
  };

  const handleIrACalificar = () => {
    navigate(`/academic/tareas/${tareaId}/calificar`);
  };

  const handleCalificarEntrega = (_entrega: EntregaTarea) => {
    // Navegar a la página de calificación
    // Podríamos pasar el ID de la entrega en el futuro para pre-seleccionar
    navigate(`/academic/tareas/${tareaId}/calificar`);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <TareaDetalle
          tareaId={tareaId}
          cursoId={cursoId}
          onBack={handleBack}
          onCalificarEntrega={handleCalificarEntrega}
          onIrACalificar={handleIrACalificar}
        />
      </div>
    </div>
  );
}
