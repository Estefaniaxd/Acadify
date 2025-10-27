// Bloque de clases del estudiante (mock)
export default function ClasesEstudiante() {
  return (
    <section className="mb-6">
      <h2 className="text-lg font-bold text-primary mb-2">Mis Clases</h2>
      <ul className="list-disc ml-6">
        <li>Matemáticas 2025</li>
        <li>Historia Universal</li>
      </ul>
      <div className="flex gap-2 mt-2">
        <button className="px-3 py-1 bg-primary text-white rounded">Unirse a clase</button>
        <button className="px-3 py-1 bg-primary/80 text-white rounded">Crear clase</button>
      </div>
    </section>
  );
}