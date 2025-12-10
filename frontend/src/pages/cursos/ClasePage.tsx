import { useState } from 'react';
import { useParams } from 'react-router-dom';
import ClaseTablonPage from '../clase/TablonPage';
import ClaseTareasPage from '../clase/TareasPage';
import ClaseMaterialesPage from '../clase/MaterialesPage';
import ClasePersonasPage from '../clase/PersonasPage';
import ClaseCalificacionesPage from '../clase/CalificacionesPage';

const TABS = [
  { id: 'tablon', label: 'Tablón' },
  { id: 'tareas', label: 'Tareas' },
  { id: 'materiales', label: 'Materiales' },
  { id: 'personas', label: 'Personas' },
  { id: 'calificaciones', label: 'Calificaciones' },
];

export default function ClasePage() {
  const { id: cursoId } = useParams<{ id: string }>();
  const [tab, setTab] = useState('tablon');
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#18181b]">
      {/* Header con título y botones */}
      <div className="sticky top-0 z-40 bg-white dark:bg-zinc-900 border-b border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-3xl font-bold text-primary">Nombre de la clase</h2>
            <div className="flex gap-2">
              <button className="px-4 py-2 rounded-lg bg-primary/10 text-primary font-semibold hover:bg-primary/20 transition-colors">
                ⚙️ Ajustes
              </button>
              <button className="px-4 py-2 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 font-semibold hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors">
                👋 Abandonar
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 border-b border-gray-200 dark:border-gray-700">
            {TABS.map(t => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`px-4 py-3 font-semibold transition-all border-b-2 ${
                  tab === t.id
                    ? 'text-primary border-primary'
                    : 'text-gray-600 dark:text-gray-400 border-transparent hover:text-gray-900 dark:hover:text-gray-200'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Contenido dinámico */}
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {tab === 'tablon' && <ClaseTablonPage />}
          {tab === 'tareas' && <ClaseTareasPage />}
          {tab === 'materiales' && <ClaseMaterialesPage />}
          {tab === 'personas' && <ClasePersonasPage />}
          {tab === 'calificaciones' && <ClaseCalificacionesPage />}
        </div>
      </div>
    </div>
  );
}
