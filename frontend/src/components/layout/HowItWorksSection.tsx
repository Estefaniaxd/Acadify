import React from 'react';
import { motion } from 'framer-motion';
import { UserPlusIcon, PuzzlePieceIcon, TrophyIcon, AcademicCapIcon } from '@heroicons/react/24/outline';

const steps = [
  {
    title: 'Regístrate gratis',
    description: 'Crea tu cuenta en segundos y accede a todo el contenido de Acadify.',
    icon: <UserPlusIcon className="w-10 h-10 text-primary dark:text-purple-300" />,
  },
  {
    title: 'Explora y aprende',
    description: 'Accede a cursos, retos y recursos interactivos adaptados a tu nivel.',
    icon: <PuzzlePieceIcon className="w-10 h-10 text-primary dark:text-purple-300" />,
  },
  {
    title: 'Juega y gana logros',
    description: 'Completa desafíos, suma puntos y desbloquea recompensas exclusivas.',
    icon: <TrophyIcon className="w-10 h-10 text-primary dark:text-purple-300" />,
  },
  {
    title: 'Obtén certificados',
    description: 'Demuestra tu progreso y recibe certificados digitales por tus logros.',
    icon: <AcademicCapIcon className="w-10 h-10 text-primary dark:text-purple-300" />,
  },
];

export default function HowItWorksSection() {
  return (
    <section className="w-full py-20 bg-gradient-to-b from-[#f7f7fb] via-[#f3f0ff] to-white dark:from-black dark:via-[#18181b] dark:to-[#18181b]">
      <div className="max-w-5xl mx-auto px-4">
        <motion.h2
          className="text-3xl md:text-5xl font-extrabold text-center mb-12 text-primary dark:text-purple-200"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
        >
          ¿Cómo funciona Acadify?
        </motion.h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
          {steps.map((step, idx) => (
            <motion.div
              key={step.title}
              className="rounded-2xl shadow-xl bg-white/90 dark:bg-[#18181b] border border-gray-100 dark:border-gray-800 p-7 flex flex-col items-center text-center relative overflow-visible group"
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * idx, duration: 0.7, type: 'spring' }}
            >
              <div className="mb-4 flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 dark:bg-purple-900/20 border-2 border-primary/20 dark:border-purple-400/20 group-hover:scale-110 transition-transform">
                {step.icon}
              </div>
              <span className="absolute -top-5 left-1/2 -translate-x-1/2 bg-primary text-white dark:bg-purple-400 dark:text-black rounded-full w-10 h-10 flex items-center justify-center font-bold text-lg shadow-lg border-4 border-white dark:border-[#18181b]">{idx+1}</span>
              <h3 className="text-lg font-bold mb-2 text-primary dark:text-purple-200 mt-6">{step.title}</h3>
              <p className="text-gray-700 dark:text-gray-300 text-base">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
