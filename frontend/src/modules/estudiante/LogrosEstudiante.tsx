// Bloque de logros del estudiante (mock)
export default function LogrosEstudiante() {
  return (
    <section className="mb-6">
      <h2 className="text-lg font-bold text-primary mb-2">Logros</h2>
      <ul className="flex gap-2">
        <li className="bg-yellow-200 rounded px-2 py-1">Primer entrega</li>
        <li className="bg-yellow-300 rounded px-2 py-1">Participante</li>
        <li className="bg-yellow-400 rounded px-2 py-1">Constante</li>
      </ul>
    </section>
  );
}