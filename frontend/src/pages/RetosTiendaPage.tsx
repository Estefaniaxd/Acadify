export default function RetosTiendaPage() {
  // Mock de retos y tienda
  const retos = [
    { id: 1, nombre: 'Reto diario', descripcion: 'Completa una lección hoy', puntos: 50 },
    { id: 2, nombre: 'Reto semanal', descripcion: 'Participa en 3 comunidades', puntos: 200 },
  ];
  const tienda = [
    { id: 1, nombre: 'Avatar especial', costo: 500 },
    { id: 2, nombre: 'Insignia dorada', costo: 1000 },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-3xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Retos y tienda de recompensas</h2>
        <div className="mb-8">
          <h3 className="text-lg font-bold text-primary mb-2">Retos</h3>
          <ul className="flex flex-col gap-2">
            {retos.map(r => (
              <li key={r.id} className="p-3 rounded bg-gray-100 dark:bg-zinc-800 flex items-center justify-between">
                <span>{r.nombre}: {r.descripcion}</span>
                <span className="text-primary font-bold">+{r.puntos} pts</span>
                <button className="ml-4 px-3 py-1 rounded bg-primary text-white text-sm font-semibold hover:bg-primary/90 transition-colors">Aceptar</button>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-lg font-bold text-primary mb-2">Tienda</h3>
          <ul className="flex flex-col gap-2">
            {tienda.map(t => (
              <li key={t.id} className="p-3 rounded bg-yellow-100 dark:bg-yellow-900 flex items-center justify-between">
                <span>{t.nombre}</span>
                <span className="text-yellow-700 font-bold">{t.costo} pts</span>
                <button className="ml-4 px-3 py-1 rounded bg-primary text-white text-sm font-semibold hover:bg-primary/90 transition-colors">Canjear</button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
