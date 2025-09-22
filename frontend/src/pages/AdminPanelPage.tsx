export default function AdminPanelPage() {
  // Mock de panel admin
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-4xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-primary mb-6">Panel de administración</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-4 rounded bg-gray-100 dark:bg-zinc-800">
            <h3 className="font-bold mb-2">Usuarios</h3>
            <button className="px-4 py-1 rounded bg-primary text-white text-sm font-semibold hover:bg-primary/90 transition-colors">Gestionar</button>
          </div>
          <div className="p-4 rounded bg-gray-100 dark:bg-zinc-800">
            <h3 className="font-bold mb-2">Cursos</h3>
            <button className="px-4 py-1 rounded bg-primary text-white text-sm font-semibold hover:bg-primary/90 transition-colors">Gestionar</button>
          </div>
          <div className="p-4 rounded bg-gray-100 dark:bg-zinc-800">
            <h3 className="font-bold mb-2">Comunidades</h3>
            <button className="px-4 py-1 rounded bg-primary text-white text-sm font-semibold hover:bg-primary/90 transition-colors">Gestionar</button>
          </div>
          <div className="p-4 rounded bg-gray-100 dark:bg-zinc-800">
            <h3 className="font-bold mb-2">Reportes</h3>
            <button className="px-4 py-1 rounded bg-primary text-white text-sm font-semibold hover:bg-primary/90 transition-colors">Ver reportes</button>
          </div>
        </div>
      </div>
    </div>
  );
}
