export default function CrearClasePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-md bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700 flex flex-col gap-6">
        <h2 className="text-xl font-bold text-primary mb-4">Crear nueva clase</h2>
        <form className="flex flex-col gap-4">
          <input
            type="text"
            required
            placeholder="Nombre de la clase"
            className="px-4 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-zinc-800"
          />
          <input
            type="text"
            required
            placeholder="Materia o tema"
            className="px-4 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-zinc-800"
          />
          <button type="submit" className="px-6 py-2 rounded bg-primary text-white font-semibold hover:bg-primary/90 transition-colors">Crear clase</button>
        </form>
      </div>
    </div>
  );
}
