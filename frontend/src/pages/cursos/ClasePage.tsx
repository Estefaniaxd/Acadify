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
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-5xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4 mb-6">
          <h2 className="text-2xl font-bold text-primary">Nombre de la clase</h2>
          <div className="ml-auto flex gap-2">
            <button className="px-3 py-1 rounded bg-primary/10 text-primary font-semibold hover:bg-primary/20">Ajustes</button>
            <button className="px-3 py-1 rounded bg-primary/10 text-primary font-semibold hover:bg-primary/20">Abandonar</button>
          </div>
        </div>
        <div className="flex gap-2 mb-8">
          {TABS.map(t => (
            <button key={t.id} className={`px-4 py-2 rounded-t-lg font-semibold text-base ${tab === t.id ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200'}`} onClick={() => setTab(t.id)}>{t.label}</button>
          ))}
        </div>
        <div>
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
