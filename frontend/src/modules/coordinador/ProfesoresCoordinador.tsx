// Gestión de profesores (mock)
export default function ProfesoresCoordinador() {
  return (
    <section className="mb-8">
      <h2 className="text-xl font-bold mb-2 text-primary">Profesores</h2>
      <ul className="list-disc ml-6">
        <li>Profe Ana (Matemáticas)</li>
        <li>Profe Luis (Historia)</li>
      </ul>
      <button className="mt-2 px-4 py-1 bg-primary text-white rounded">Agregar profesor</button>
    </section>
  );
}
