import React from 'react';
import { motion } from 'framer-motion';

const roadmap = [
  {
    title: 'Lanzamiento de la beta pública',
    date: 'Q4 2025',
    description: 'Acceso abierto a estudiantes y docentes, primeras instituciones registradas.'
  },
  {
    title: 'Módulo de retos colaborativos',
    date: 'Q1 2026',
    description: 'Desafíos grupales, rankings y logros compartidos.'
  },
  {
    title: 'Integración con IA generativa',
    date: 'Q2 2026',
    description: 'Recomendaciones personalizadas y generación de ejercicios adaptativos.'
  },
  {
    title: 'App móvil Acadify',
    date: 'Q3 2026',
    description: 'Lanzamiento de la app para iOS y Android.'
  },
  {
    title: 'Expansión internacional',
    date: 'Q4 2026',
    description: 'Soporte multilenguaje y alianzas globales.'
  },
];

export default function RoadmapSection() {
  return (
    <section className="w-full py-20 bg-gradient-to-b from-white via-[#f3f0ff] to-[#f7f7fb] dark:from-[#18181b] dark:via-[#18181b] dark:to-black">
      <div className="max-w-5xl mx-auto px-4 flex flex-col items-center text-center">
        <motion.h2
          className="text-3xl md:text-5xl font-extrabold mb-4 text-primary dark:text-purple-200"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
        >
          Roadmap Acadify
        </motion.h2>
        <motion.p
          className="text-lg text-gray-700 dark:text-gray-300 mb-10 max-w-2xl"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.7 }}
        >
          ¡Esto es solo el comienzo! Mira lo que viene y súmate a construir el futuro de la educación.
        </motion.p>
        <div className="flex flex-col gap-8 w-full">
          {roadmap.map((item, idx) => (
            <motion.div
              key={item.title}
              className="relative bg-white/90 dark:bg-[#18181b] border border-gray-100 dark:border-gray-800 rounded-2xl shadow-xl px-8 py-6 flex flex-col md:flex-row md:items-center gap-4 md:gap-8 group hover:scale-[1.02] transition-transform"
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * idx, duration: 0.7, type: 'spring' }}
            >
              <div className="flex-shrink-0 w-16 h-16 rounded-full bg-primary/10 dark:bg-purple-900/20 flex items-center justify-center text-2xl font-bold text-primary dark:text-purple-200 border-2 border-primary/20 dark:border-purple-400/20">
                {item.date}
              </div>
              <div className="flex-1 text-left">
                <h3 className="text-xl font-bold text-primary dark:text-purple-200 mb-1">{item.title}</h3>
                <p className="text-gray-700 dark:text-gray-300 text-base">{item.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
        <motion.div
          className="mt-12 flex flex-col items-center gap-4"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5, duration: 0.7 }}
        >
          <h3 className="text-2xl font-bold text-primary dark:text-purple-200">¿Quieres ser parte del equipo?</h3>
          <p className="text-gray-700 dark:text-gray-300 max-w-xl mb-2">Buscamos desarrolladores, educadores, diseñadores y entusiastas de la tecnología educativa. ¡Súmate y ayúdanos a transformar la educación!</p>
          <div className="flex flex-col sm:flex-row gap-4">
            <a href="/about" className="px-8 py-3 rounded-xl bg-gradient-to-r from-primary to-purple-600 text-white font-bold shadow-lg hover:scale-105 transition-transform text-lg">Saber más</a>
            <a href="mailto:contacto@acadify.org" className="px-8 py-3 rounded-xl border border-primary text-primary dark:text-purple-300 bg-white/70 dark:bg-black/10 font-bold hover:bg-primary/10 hover:scale-105 transition-all text-lg">Contacto</a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
