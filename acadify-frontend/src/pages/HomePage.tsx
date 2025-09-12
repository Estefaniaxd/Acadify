export default function HomePage() {
  
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-violet-600 to-indigo-900 text-white py-20 text-center">
        <h1 className="text-4xl md:text-5xl font-bold">
          Bienvenido a <span className="text-green-300">Acadify </span>
        </h1>
        <p className="mt-4 text-lg max-w-2xl mx-auto">
          La plataforma educativa que combina innovación, diversión y aprendizaje para transformar tu experiencia académica.
        </p>
      </section>

      {/* Sobre la plataforma */}
      <section className="py-16 px-6 max-w-5xl mx-auto text-center">
        <h2 className="text-3xl font-bold text-violet-900">¿Qué es Acadify?</h2>
        <p className="mt-4 text-gray-700 text-lg">
          Acadify es una plataforma educativa diseñada para estudiantes, docentes y padres de familia, 
          que busca potenciar el aprendizaje con recursos modernos y dinámicos. Nuestro objetivo es 
          ofrecer un espacio accesible, flexible y motivador para cada usuario.
        </p>
      </section>

      {/* Beneficios principales */}
      <section className="py-16 px-6 bg-gray-50">
        <h2 className="text-3xl font-bold text-center text-violet-900">¿Cómo mejora tu aprendizaje?</h2>
        <div className="grid md:grid-cols-3 gap-8 mt-10 max-w-6xl mx-auto">
          <div className="p-6 bg-white shadow-lg rounded-2xl hover:scale-105 transition">
            <h3 className="text-xl font-semibold text-violet-900"> *ੈ✩‧₊˚ Gamificación</h3>
            <p className="mt-3 text-gray-600">
              Aprende jugando: recompensas, insignias y retos diarios que aumentan tu motivación
              y hacen que el aprendizaje sea más entretenido.
            </p>
          </div>
          <div className="p-6 bg-white shadow-lg rounded-2xl hover:scale-105 transition">
            <h3 className="text-xl font-semibold text-red-900">˚ ༘♡ ⋆｡˚ ❀Personalización</h3>
            <p className="mt-3 text-gray-600">
              Cada estudiante tiene un recorrido único. Nuestro sistema adapta el contenido 
              a tu estilo de aprendizaje y nivel de progreso.
            </p>
          </div>
          <div className="p-6 bg-white shadow-lg rounded-2xl hover:scale-105 transition">
            <h3 className="text-xl font-semibold text-green-500">.˚ ᵎ┊͙◟̆◞̆Chatbot inteligente</h3>
            <p className="mt-3 text-gray-600">
              Un asistente virtual disponible 24/7 para responder preguntas, dar apoyo en tareas 
              y guiar tu experiencia en la plataforma.
            </p>
          </div>
        </div>
      </section>

      {/* Mascota Rutilio */}
      <section className="py-16 px-6 max-w-5xl mx-auto text-center">
        <h2 className="text-3xl font-bold text-indigo-900">♥ Conoce a Rutilio, nuestra mascota ♥</h2>
        <p className="mt-4 text-gray-700 text-lg">
          Rutilio es un simpático pez que nos acompaña en el viaje del aprendizaje. Representa la 
          curiosidad, la constancia y la alegría de descubrir cosas nuevas.
        </p>

        <div className="mt-10 flex flex-col md:flex-row items-center justify-center gap-8">
         
        <img
            src="images/rutiliolike.png"
            className="w-40 h-40 rounded-full shadow-lg"
          />
          <div className="max-w-md text-left">
            <h3 className="text-xl font-semibold text-indigo-600">¿Por qué una mascota?</h3>
            <p className="mt-3 text-gray-600">
              Está comprobado que las mascotas aportan motivación, compañía y ayudan a reducir el estrés.  
              Rutilio simboliza la importancia de tener un compañero en el camino educativo, 
              recordándonos que aprender también puede ser divertido y cercano.



              😈😈😈😈😈😈🐈🐳🍧🍧🎲👩‍🏫👨‍🏫👩‍🏫👩‍🏫👩‍🏫👩‍🏫👩‍🏫👩‍🏫👩‍🏫👩‍🏫👩‍🏫👩‍🏫👩‍🏫👩‍🏫🥅🥅🥅🥅🥋🥋🥋🥊🥊🥊🥊⚽⚽⚽⚽⚽⚽👨‍🦽👨‍🦽👨‍🦽👨‍🦽👨‍🦽👨‍🦽👨‍🦽👨‍🦽👨‍🦽👨‍🦽🌏🌏🌏🌏🌏🌏9️⃣9️⃣9️⃣9️⃣4️⃣4️⃣4️⃣4️⃣4️⃣4️⃣4️⃣4️⃣6️⃣6️⃣6️⃣6️⃣6️⃣6️⃣6️⃣6️⃣
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
