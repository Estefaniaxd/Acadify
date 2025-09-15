export default function HomePage() {
  
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-violet-600 to-indigo-900 text-white py-20 text-center">
        <h1 className="text-4xl md:text-5xl font-bold">
          Bienvenido a <span className="text-green-300">Acadify </span>
        import React, { useState } from "react";
        import RutilioImg from "../components/images/rutiliolike.png";

        // Optional framer-motion usage: try to require it at runtime. If not available, we fall back to simple interactions.
        let Motion: any = null;
        try {
          // @ts-ignore
          Motion = require("framer-motion");
        } catch (e) {
          Motion = null;
        }

        function Mascot(): JSX.Element {
          const [liked, setLiked] = useState(false);

          const img = (
            <img
              src={RutilioImg}
              alt="Rutilio la mascota"
              className="w-40 h-40 rounded-full shadow-lg object-cover"
            />
          );

          if (Motion && Motion.motion) {
            const { motion } = Motion;
            return (
              <motion.div
                initial={{ scale: 1 }}
                whileHover={{ scale: 1.05 }}
                animate={{ rotate: liked ? [0, -6, 6, 0] : 0 }}
                className="cursor-pointer"
                onClick={() => setLiked((s: boolean) => !s)}
                aria-pressed={liked}
              >
                {img}
              </motion.div>
            );
          }

          return (
            <button
              type="button"
              onClick={() => setLiked((s) => !s)}
              className="hover:scale-105 transition-transform"
              aria-pressed={liked}
            >
              {img}
            </button>
          );
        }

        export default function HomePage(): JSX.Element {
          return (
            <div className="flex flex-col">
              <section className="bg-gradient-to-r from-acadify-purple to-indigo-900 text-white py-20 text-center">
                <h1 className="text-4xl md:text-5xl font-bold">
                  Bienvenido a <span className="text-acadify-green">Acadify</span>
                </h1>
                <p className="mt-4 text-lg max-w-2xl mx-auto">
                  La plataforma educativa que combina innovación, diversión y aprendizaje para transformar tu experiencia académica.
                </p>
              </section>

              <section className="py-16 px-6 max-w-5xl mx-auto text-center">
                <h2 className="text-3xl font-bold text-acadify-purple">¿Qué es Acadify?</h2>
                <p className="mt-4 text-gray-700 text-lg">
                  Acadify es una plataforma educativa diseñada para estudiantes, docentes y familias. Potenciamos el aprendizaje con recursos modernos, adaptativos y motivadores.
                </p>
              </section>

              <section className="py-16 px-6 bg-gray-50">
                <h2 className="text-3xl font-bold text-center text-acadify-purple">¿Cómo mejora tu aprendizaje?</h2>
                <div className="grid md:grid-cols-3 gap-8 mt-10 max-w-6xl mx-auto px-4">
                  <div className="p-6 bg-white shadow-lg rounded-2xl hover:scale-105 transition-transform">
                    <h3 className="text-xl font-semibold text-acadify-purple">Gamificación</h3>
                    <p className="mt-3 text-gray-600">Aprende jugando: recompensas, insignias y retos diarios que aumentan tu motivación.</p>
                  </div>
                  <div className="p-6 bg-white shadow-lg rounded-2xl hover:scale-105 transition-transform">
                    <h3 className="text-xl font-semibold text-acadify-purple">Personalización</h3>
                    <p className="mt-3 text-gray-600">Recorridos adaptativos que se ajustan a tu ritmo y estilo de aprendizaje.</p>
                  </div>
                  <div className="p-6 bg-white shadow-lg rounded-2xl hover:scale-105 transition-transform">
                    <h3 className="text-xl font-semibold text-acadify-purple">Asistente inteligente</h3>
                    <p className="mt-3 text-gray-600">Un asistente disponible 24/7 para resolver dudas y orientar tareas.</p>
                  </div>
                </div>
              </section>

              <section className="py-16 px-6 max-w-5xl mx-auto text-center">
                <h2 className="text-3xl font-bold text-acadify-purple">Conoce a Rutilio, nuestra mascota</h2>
                <p className="mt-4 text-gray-700 text-lg">Rutilio representa la curiosidad y la constancia. Acompaña y celebra tus logros.</p>

                <div className="mt-10 flex flex-col md:flex-row items-center justify-center gap-8">
                  <Mascot />
                  <div className="max-w-md text-left">
                    <h3 className="text-xl font-semibold text-acadify-purple">¿Por qué una mascota?</h3>
                    <p className="mt-3 text-gray-600">Las mascotas digitales crean vínculo y motivación; Rutilio celebra logros y hace más cercano el aprendizaje.</p>
                  </div>
                </div>
              </section>
            </div>
          );
        }
        aria-pressed={liked}
