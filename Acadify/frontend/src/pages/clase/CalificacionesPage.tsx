export default function ClaseCalificacionesPage() {
  // Mock de calificaciones
  const calificaciones = [
    { id: 1, estudiante: 'Esteban', tarea: 'Tarea 1', nota: 4.5 },
    { id: 2, estudiante: 'Laura', tarea: 'Tarea 1', nota: 4.8 },
  ];
  return (
    <div>
      <h3 className="text-lg font-bold text-primary mb-4">Calificaciones</h3>
      <table className="w-full text-left">
        <thead>
          <tr>
            <th className="py-2">Estudiante</th>
            <th className="py-2">Tarea</th>
            <th className="py-2">Nota</th>
          </tr>
        </thead>
        <tbody>
          {calificaciones.map(c => (
            <tr key={c.id} className="border-b border-gray-200 dark:border-gray-700">
              <td className="py-2">{c.estudiante}</td>
              <td className="py-2">{c.tarea}</td>
              <td className="py-2">{c.nota}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
