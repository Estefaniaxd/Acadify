// Bloque de avatar del estudiante (mock)
export default function AvatarEstudiante() {
  return (
    <section className="mb-6 flex flex-col items-center">
      <h2 className="text-lg font-bold text-primary mb-2">Mi Avatar</h2>
      <div className="w-24 h-24 rounded-full bg-gray-200 mb-2 flex items-center justify-center">
        <span className="text-4xl">🧑‍🎓</span>
      </div>
      <button className="px-4 py-1 bg-primary text-white rounded">Editar avatar</button>
    </section>
  );
}