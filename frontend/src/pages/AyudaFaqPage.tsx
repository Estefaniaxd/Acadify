export default function AyudaFaqPage() {
  // Mock de ayuda y FAQ
  const faqs = [
    { id: 1, pregunta: '¿Cómo me registro?', respuesta: 'Haz clic en Crear cuenta y completa el formulario.' },
    { id: 2, pregunta: '¿Cómo cambio mi avatar?', respuesta: 'Ve a tu perfil y selecciona Personalizar avatar.' },
    { id: 3, pregunta: '¿Cómo reporto un problema?', respuesta: 'Desde Ajustes puedes enviar sugerencias o reportes.' },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Ayuda y preguntas frecuentes</h2>
        <ul className="flex flex-col gap-4">
          {faqs.map(f => (
            <li key={f.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800">
              <div className="font-semibold text-primary mb-1">{f.pregunta}</div>
              <div className="text-gray-700 dark:text-gray-200">{f.respuesta}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
