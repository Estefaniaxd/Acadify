/**
 * TareaDetallePage
 * 
 * Página completa para mostrar el detalle de una tarea.
 * Coordina TareaDetalle y CalificarEntregaModal.
 */

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TareaDetalle, CalificarEntregaModal } from '../../modules/tareas/components';
import { EntregaTarea, CalificacionResponse } from '../../modules/tareas/types';

export default function TareaDetallePage() {
  const { cursoId, tareaId } = useParams<{ cursoId: string; tareaId: string }>();
  const navigate = useNavigate();
  const [entregaSeleccionada, setEntregaSeleccionada] = useState<EntregaTarea | null>(null);

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

  const handleCalificarEntrega = (entrega: EntregaTarea) => {
    setEntregaSeleccionada(entrega);
  };

  const handleCalificacionGuardada = (_response: CalificacionResponse) => {
    // Calificación guardada exitosamente
    setEntregaSeleccionada(null);
    // Recargar la página para ver los cambios
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <TareaDetalle
          tareaId={tareaId}
          cursoId={cursoId}
          onBack={handleBack}
          onCalificarEntrega={handleCalificarEntrega}
        />
      </div>

      {/* Modal de calificación */}
      {entregaSeleccionada && (
        <CalificarEntregaModal
          entrega={entregaSeleccionada}
          puntos_maximos={100} // TODO: Obtener de la tarea
          onClose={() => setEntregaSeleccionada(null)}
          onCalificacionGuardada={handleCalificacionGuardada}
        />
      )}
    </div>
  );
}
