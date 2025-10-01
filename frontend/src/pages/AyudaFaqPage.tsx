import React from 'react'

export default function AyudaFaqPage() {
  return (
    <div className="bg-gradient-to-br from-blue-50 via-white to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900 p-6 mt-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8 text-center">
          Ayuda y Preguntas Frecuentes
        </h1>
        
        <div className="grid gap-6">
          {[
            {
              question: "¿Cómo creo un nuevo curso?",
              answer: "Puedes crear un nuevo curso desde el módulo de Cursos haciendo clic en 'Crear Curso' y completando el formulario."
            },
            {
              question: "¿Cómo añado estudiantes a mi clase?",
              answer: "En el panel de tu clase, utiliza el código de invitación o añade estudiantes por email desde la sección de participantes."
            },
            {
              question: "¿Dónde encuentro las evaluaciones?",
              answer: "Las evaluaciones están disponibles en el módulo de Evaluaciones, donde puedes crear, editar y monitorear todas las evaluaciones."
            }
          ].map((faq, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                {faq.question}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {faq.answer}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
