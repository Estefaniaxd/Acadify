// Gestión de clases del profesor (mock)
export default function ClasesProfesor() {
  return (
    <section className="mb-8">
      <h2 className="text-xl font-bold mb-2 text-primary">Mis Clases</h2>
      <ul className="list-disc ml-6">
        <li>Matemáticas 2025 <button className="ml-2 text-xs text-blue-600 underline">Ver</button></li>
        <li>Historia Universal <button className="ml-2 text-xs text-blue-600 underline">Ver</button></li>
      </ul>
      <button className="mt-2 px-4 py-1 bg-primary text-white rounded">Crear nueva clase</button>
    </section>
  );
}
