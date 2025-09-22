// Gestión de tareas del profesor (mock)
export default function TareasProfesor() {
  return (
    <section className="mb-8">
      <h2 className="text-xl font-bold mb-2 text-primary">Tareas</h2>
      <ul className="list-disc ml-6">
        <li>Tarea 1: Ecuaciones <button className="ml-2 text-xs text-blue-600 underline">Ver</button></li>
        <li>Tarea 2: Ensayo <button className="ml-2 text-xs text-blue-600 underline">Ver</button></li>
      </ul>
      <button className="mt-2 px-4 py-1 bg-primary text-white rounded">Crear nueva tarea</button>
    </section>
  );
}
