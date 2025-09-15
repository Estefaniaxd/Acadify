import React from 'react';

const AboutPage: React.FC = () => {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-violet-600 to-indigo-900 text-white py-20 text-center">
        <h1 className="text-4xl md:text-5xl font-bold">
          Nuestra misión en <span className="text-green-300">Acadify</span>
        </h1>
        <p className="mt-4 text-lg max-w-2xl mx-auto">
          Estamos comprometidos a transformar el futuro de la educación a través de la tecnología y la innovación.
        </p>
      </section>

      {/* Misión y Visión */}
      <section className="py-16 px-6 max-w-5xl mx-auto text-center">
        <h2 className="text-3xl font-bold text-violet-900 mb-12">Nuestros pilares</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="flex flex-col items-center">
            <span className="text-5xl text-green-500 mb-4">✧.*</span>
            <h3 className="text-xl font-semibold text-indigo-900">Visión</h3>
            <p className="mt-2 text-gray-700">
              Ser la plataforma líder que inspire a millones de estudiantes a alcanzar su máximo potencial.
            </p>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-5xl text-green-500 mb-4">ೃ⁀➷</span>
            <h3 className="text-xl font-semibold text-indigo-900">Misión</h3>
            <p className="mt-2 text-gray-700">
              Proveer herramientas educativas innovadoras que fomenten el aprendizaje divertido y accesible.
            </p>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-5xl text-green-500 mb-4">⸜❤︎⸝</span>
            <h3 className="text-xl font-semibold text-indigo-900">Valores</h3>
            <p className="mt-2 text-gray-700">
              Innovación, accesibilidad y pasión por el conocimiento son el corazón de todo lo que hacemos.
            </p>
          </div>
        </div>
      </section>

      {/* Sección del equipo */}
      <section className="py-16 px-6 bg-gray-50">
        <h2 className="text-3xl font-bold text-center text-violet-900 mb-10">Conoce a nuestro equipo</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-12 max-w-6xl mx-auto">
          {/* Desarrollador Principal */}
          <div className="flex flex-col items-center text-center">
            <img
              src="src/components/images/harrison.png"
              alt="Desarrollador Principal"
              className="w-40 h-40 rounded-full object-cover shadow-lg"
            />
            <h3 className="mt-4 text-xl font-semibold text-indigo-900">Harrison Guerrero</h3>
            <p className="text-sm text-green-500 font-medium">₊˚ˑ༄ؘ Desarrollador Principal</p>
            <p className="mt-2 text-gray-600">
              Lidera el desarrollo del núcleo de la plataforma, asegurando un código robusto y eficiente.
            </p>
          </div>

          {/* Diseñadora Frontend */}
          <div className="flex flex-col items-center text-center">
            <img
              src="src/components/images/yo.png"
              alt="Diseñadora Frontend"
              className="w-40 h-40 rounded-full object-cover shadow-lg"
            />
            <h3 className="mt-4 text-xl font-semibold text-indigo-900">Estefania Londoño</h3>
            <p className="text-sm text-green-500 font-medium">✧ ೃ༄*ੈ✩ Diseñadora Frontend</p>
            <p className="mt-2 text-gray-600">
              Transforma nuestras ideas en interfaces intuitivas y visualmente atractivas para los usuarios.
            </p>
          </div>

          {/* Diseñador Backend */}
          <div className="flex flex-col items-center text-center">
            <img
              src="src/components/images/juan.png"
              alt="Diseñador Backend"
              className="w-40 h-40 rounded-full object-cover shadow-lg"
            />
            <h3 className="mt-4 text-xl font-semibold text-indigo-900">Juan Martinez</h3>
            <p className="text-sm text-green-500 font-medium">·˚ ༘ ꒱Diseñador Backend</p>
            <p className="mt-2 text-gray-600">
              Construye la arquitectura del servidor y las bases de datos que dan vida a nuestra plataforma.
            </p>
          </div>
          
          {/* QA Tester */}
          <div className="flex flex-col items-center text-center">
            <img
              src="src/components/images/harry.png"
              alt="QA Tester"
              className="w-40 h-40 rounded-full object-cover shadow-lg"
            />
            <h3 className="mt-4 text-clip text-xl font-semibold text-indigo-900 ">Harryson Vanegas</h3>
            <p className="text-sm text-green-500 font-medium">*+:｡.｡➷QA Tester</p>
            <p className="mt-2 text-gray-600">
              Garantiza la calidad de nuestro producto, encontrando y corrigiendo errores para una experiencia perfecta.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;