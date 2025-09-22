// Gestión de materiales del profesor (mock)
export default function MaterialesProfesor() {
  return (
    <section className="mb-8">
      <h2 className="text-xl font-bold mb-2 text-primary">Materiales</h2>
      <ul className="list-disc ml-6">
        <li>Guía de ejercicios.pdf <button className="ml-2 text-xs text-blue-600 underline">Ver</button></li>
        <li>Video explicativo.mp4 <button className="ml-2 text-xs text-blue-600 underline">Ver</button></li>
      </ul>
      <button className="mt-2 px-4 py-1 bg-primary text-white rounded">Subir material</button>
    </section>
  );
}
