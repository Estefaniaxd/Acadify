import React, { useState } from 'react';
import { 
  ListaTareas, 
  FormularioTarea, 
  DetalleTarea,
  TareasApi,
  Tarea,
  TareaCreate 
} from '../modules/tareas';

interface SistemaTareasProps {
  grupoId: string;
  docenteId: string;
  esDocente: boolean;
  estudianteId?: string;
}

export const SistemaTareas: React.FC<SistemaTareasProps> = ({
  grupoId,
  docenteId,
  esDocente,
  estudianteId
}) => {
  const [vistaActual, setVistaActual] = useState<'lista' | 'formulario' | 'detalle'>('lista');
  const [tareaSeleccionada, setTareaSeleccionada] = useState<Tarea | null>(null);
  const [modoEdicion, setModoEdicion] = useState(false);
  const [actualizarLista, setActualizarLista] = useState(0);

  const tareasApi = new TareasApi();

  const handleCrearTarea = () => {
    setTareaSeleccionada(null);
    setModoEdicion(false);
    setVistaActual('formulario');
  };

  const handleEditarTarea = (tarea: Tarea) => {
    setTareaSeleccionada(tarea);
    setModoEdicion(true);
    setVistaActual('formulario');
  };

  const handleVerDetalle = (tarea: Tarea) => {
    setTareaSeleccionada(tarea);
    setVistaActual('detalle');
  };

  const handleGuardarTarea = async (dataTarea: TareaCreate) => {
    try {
      if (modoEdicion && tareaSeleccionada?.id) {
        // Actualizar tarea existente
        await tareasApi.actualizarTarea(tareaSeleccionada.id, dataTarea);
      } else {
        // Crear nueva tarea
        await tareasApi.crearTarea(dataTarea);
      }
      
      // Actualizar la lista de tareas
      setActualizarLista(prev => prev + 1);
      setVistaActual('lista');
      setTareaSeleccionada(null);
      setModoEdicion(false);
    } catch (error) {
      console.error('Error al guardar tarea:', error);
      throw error;
    }
  };

  const handleEliminarTarea = (tareaId: string) => {
    // Actualizar la lista de tareas
    setActualizarLista(prev => prev + 1);
    setVistaActual('lista');
    setTareaSeleccionada(null);
  };

  const handleCerrarModal = () => {
    setVistaActual('lista');
    setTareaSeleccionada(null);
    setModoEdicion(false);
  };

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sistema de Tareas</h1>
          <p className="text-gray-600">Gestiona las tareas y asignaciones del grupo</p>
        </div>
        
        {esDocente && vistaActual === 'lista' && (
          <button
            onClick={handleCrearTarea}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Nueva Tarea
          </button>
        )}
      </div>

      {/* Contenido Principal */}
      {vistaActual === 'lista' && (
        <ListaTareas
          grupoId={grupoId}
          onTareaSeleccionada={handleVerDetalle}
          onCrearTarea={handleCrearTarea}
          key={actualizarLista} // Forzar re-render cuando se actualiza
          filtrosIniciales={{
            solo_activas: true,
            ordenar_por: 'fecha_limite',
            orden_desc: false
          }}
        />
      )}

      {vistaActual === 'formulario' && (
        <FormularioTarea
          onSubmit={handleGuardarTarea}
          onCancel={handleCerrarModal}
          grupoId={grupoId}
          docenteId={docenteId}
          tareaInicial={modoEdicion ? tareaSeleccionada : null}
        />
      )}

      {vistaActual === 'detalle' && tareaSeleccionada && (
        <DetalleTarea
          tarea={tareaSeleccionada}
          onClose={handleCerrarModal}
          onEdit={esDocente ? handleEditarTarea : undefined}
          onDelete={esDocente ? handleEliminarTarea : undefined}
          esDocente={esDocente}
          estudianteId={estudianteId}
        />
      )}
    </div>
  );
};

export default SistemaTareas;