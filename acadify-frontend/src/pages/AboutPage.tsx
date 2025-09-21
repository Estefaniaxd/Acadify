import React from 'react';

const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Acerca de Acadify
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Transformando la educación a través de la tecnología
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-12 mb-16">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              Nuestra Misión
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              En Acadify, creemos que la educación de calidad debe ser accesible para todos. 
              Nuestra plataforma conecta estudiantes y educadores en un ambiente digital 
              innovador que facilita el aprendizaje efectivo.
            </p>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Educación accesible y de calidad
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Tecnología al servicio del aprendizaje
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                Comunidad global de estudiantes
              </li>
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              Nuestra Visión
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Ser la plataforma educativa líder que empodere a millones de estudiantes 
              alrededor del mundo, proporcionando herramientas innovadoras para el 
              aprendizaje del siglo XXI.
            </p>
            <div className="bg-indigo-50 dark:bg-indigo-900/20 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-indigo-900 dark:text-indigo-200 mb-2">
                ¿Por qué elegir Acadify?
              </h3>
              <p className="text-indigo-700 dark:text-indigo-300">
                Ofrecemos una experiencia de aprendizaje personalizada, contenido de 
                alta calidad y una comunidad vibrante de estudiantes y educadores.
              </p>
            </div>
          </div>
        </div>

        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-8">
            Estadísticas
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <div className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">10K+</div>
              <div className="text-gray-600 dark:text-gray-400">Estudiantes</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">500+</div>
              <div className="text-gray-600 dark:text-gray-400">Cursos</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">50+</div>
              <div className="text-gray-600 dark:text-gray-400">Instructores</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">98%</div>
              <div className="text-gray-600 dark:text-gray-400">Satisfacción</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;