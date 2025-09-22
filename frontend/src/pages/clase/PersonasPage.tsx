export default function ClasePersonasPage() {
  // Mock de personas
  const profesores = [
    { id: 1, nombre: 'Profe Ana', rol: 'Profesor' },
  ];
  const estudiantes = [
    { id: 2, nombre: 'Esteban', rol: 'Estudiante' },
    { id: 3, nombre: 'Laura', rol: 'Estudiante' },
  ];
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h4 className="font-bold text-primary mb-2">Profesores</h4>
        <ul className="flex flex-col gap-2">
          {profesores.map(p => (
            <li key={p.id} className="p-2 rounded bg-gray-100 dark:bg-zinc-800">{p.nombre}</li>
          ))}
        </ul>
      </div>
      <div>
        <h4 className="font-bold text-primary mb-2">Estudiantes</h4>
        <ul className="flex flex-col gap-2">
          {estudiantes.map(e => (
            <li key={e.id} className="p-2 rounded bg-gray-100 dark:bg-zinc-800">{e.nombre}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
