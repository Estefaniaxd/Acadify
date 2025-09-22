import { useNavigate } from 'react-router-dom';

export default function ClaseTareasPage() {
  const navigate = useNavigate();
  // Mock de tareas
  const tareas = [
    { id: 1, titulo: 'Tarea 1: Ecuaciones', fechaEntrega: '2025-09-15', estado: 'Pendiente' },
    { id: 2, titulo: 'Tarea 2: Ensayo', fechaEntrega: '2025-09-22', estado: 'Entregada' },
  ];
  return (
    <div>
      <h3 className="text-lg font-bold text-primary mb-4">Tareas</h3>
      <ul className="flex flex-col gap-4">
        {tareas.map(t => (
          <li key={t.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800 flex justify-between items-center cursor-pointer hover:shadow transition" onClick={() => navigate(`/tarea/${t.id}`)}>
            <div>
              <div className="font-semibold text-primary">{t.titulo}</div>
              <div className="text-xs text-gray-400">Entrega: {t.fechaEntrega}</div>
            </div>
            <span className={`px-2 py-1 rounded text-xs font-semibold ${t.estado === 'Pendiente' ? 'bg-yellow-200 text-yellow-800' : 'bg-green-200 text-green-800'}`}>{t.estado}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
