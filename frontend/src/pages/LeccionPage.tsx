export default function LeccionPage() {
  // Mock de lección
  const leccion = {
    titulo: 'Introducción a React',
    contenido: 'React es una biblioteca de JavaScript para construir interfaces de usuario.',
    video: 'https://www.youtube.com/embed/dGcsHMXbSOA',
    quiz: [
      { id: 1, pregunta: '¿Qué es React?', opciones: ['Framework', 'Librería', 'Lenguaje'], respuesta: 1 },
    ],
  };
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-primary mb-2">{leccion.titulo}</h2>
        <div className="mb-4">
          <iframe width="100%" height="315" src={leccion.video} title="Video" allowFullScreen className="rounded-xl" />
        </div>
        <div className="mb-6 text-gray-700 dark:text-gray-200">{leccion.contenido}</div>
        <h3 className="text-lg font-bold text-primary mb-2">Quiz</h3>
        <ul className="flex flex-col gap-2">
          {leccion.quiz.map(q => (
            <li key={q.id} className="p-3 rounded bg-gray-100 dark:bg-zinc-800">
              <div className="mb-1 font-semibold">{q.pregunta}</div>
              <div className="flex gap-2">
                {q.opciones.map((op, idx) => (
                  <button key={op} className="px-3 py-1 rounded bg-primary/10 text-primary text-sm font-semibold hover:bg-primary/20 transition-colors">{op}</button>
                ))}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
