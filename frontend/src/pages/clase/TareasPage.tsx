import { useNavigate, useParams } from 'react-router-dom';
import { useState } from 'react';
import { TareasList } from '../../modules/tareas/components';
import { TareaEnriquecida } from '../../modules/tareas/types';
import CrearTareaModal from '../../modules/tareas/components/CrearTareaModal';

export default function ClaseTareasPage() {
  const navigate = useNavigate();
  const { cursoId } = useParams<{ cursoId: string }>();
  const [mostrarModalCrear, setMostrarModalCrear] = useState(false);

  const handleTareaClick = (tarea: TareaEnriquecida) => {
    // Navegar al detalle de la tarea
    navigate(`/cursos/${cursoId}/tareas/${tarea.tarea_id}`);
  };

  const handleCrearTarea = () => {
    setMostrarModalCrear(true);
  };

  const handleTareaCreada = () => {
    setMostrarModalCrear(false);
    // Recargar lista de tareas
    window.location.reload();
  };

  if (!cursoId) {
    return (
      <div className="text-center py-8 text-red-600">
        Error: No se pudo obtener el ID del curso
      </div>
    );
  }

  return (
    <div>
      <TareasList
        cursoId={cursoId}
        onTareaClick={handleTareaClick}
        onCrearTarea={handleCrearTarea}
      />

      {mostrarModalCrear && (
        <CrearTareaModal
          cursoId={cursoId}
          onClose={() => setMostrarModalCrear(false)}
          onTareaCreada={handleTareaCreada}
        />
      )}
    </div>
  );
}
