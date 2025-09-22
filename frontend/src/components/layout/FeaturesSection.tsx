import React from 'react';
import { motion } from 'framer-motion';
import { AcademicCapIcon, SparklesIcon, PuzzlePieceIcon, UserGroupIcon } from '@heroicons/react/24/outline';

const features = [
  {
    title: 'Gamificación',
    description: 'Aprende jugando con retos, logros y recompensas que te motivan a avanzar cada día.',
    icon: <PuzzlePieceIcon className="w-10 h-10 text-primary dark:text-purple-300" />,
  },
  {
    title: 'Inteligencia Artificial',
    description: 'Recibe recomendaciones y ayuda personalizada gracias a IA educativa avanzada.',
    icon: <SparklesIcon className="w-10 h-10 text-primary dark:text-purple-300" />,
  },
  {
    title: 'Personalización',
    description: 'Adapta tu experiencia, elige tu avatar y sigue tu propio ritmo de aprendizaje.',
    icon: <UserGroupIcon className="w-10 h-10 text-primary dark:text-purple-300" />,
  },
  {
    title: 'Certificados y logros',
    description: 'Demuestra tu progreso y obtén certificados digitales y medallas exclusivas.',
    icon: <AcademicCapIcon className="w-10 h-10 text-primary dark:text-purple-300" />,
  },
];

export default function FeaturesSection() {
  return (
    <section className="w-full py-20 bg-gradient-to-b from-white via-[#f3f0ff] to-[#f7f7fb] dark:from-[#18181b] dark:via-[#18181b] dark:to-black">
      <div className="max-w-6xl mx-auto px-4">
        <motion.h2
          className="text-3xl md:text-5xl font-extrabold text-center mb-10 text-primary dark:text-purple-200"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
        >
          ¿Por qué elegir Acadify?
        </motion.h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
          {features.map((feature, idx) => (
            <motion.div
              key={feature.title}
              className="rounded-2xl shadow-xl bg-white/90 dark:bg-[#18181b] border border-gray-100 dark:border-gray-800 p-7 flex flex-col items-center text-center hover:scale-105 hover:shadow-2xl transition-transform duration-300 group"
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * idx, duration: 0.7, type: 'spring' }}
            >
              <div className="mb-4 flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 dark:bg-purple-900/20 border-2 border-primary/20 dark:border-purple-400/20 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold mb-2 text-primary dark:text-purple-200">{feature.title}</h3>
              <p className="text-gray-700 dark:text-gray-300 text-base">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
