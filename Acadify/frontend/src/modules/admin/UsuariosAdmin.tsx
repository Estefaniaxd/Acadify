// Gestión de usuarios y coordinadores (mock)
export default function UsuariosAdmin() {
  return (
    <section className="mb-8">
      <h2 className="text-xl font-bold mb-2 text-primary">Usuarios y Coordinadores</h2>
      <ul className="list-disc ml-6">
        <li>Coordinador Juan (Institución A)</li>
        <li>Coordinador Ana (Institución B)</li>
        <li>Usuario Esteban (Estudiante)</li>
      </ul>
      <button className="mt-2 px-4 py-1 bg-primary text-white rounded">Crear usuario</button>
    </section>
  );
}
