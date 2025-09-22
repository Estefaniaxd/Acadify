import React from 'react';
import { motion } from 'framer-motion';

const testimonials = [
  {
    name: 'María López',
    role: 'Estudiante de Ingeniería',
    text: 'Acadify hizo que aprender fuera divertido y motivador. ¡Los retos y logros me impulsaron a superarme cada semana!',
    avatar: 'https://randomuser.me/api/portraits/women/44.jpg',
  },
  {
    name: 'Carlos Pérez',
    role: 'Docente universitario',
    text: 'La gamificación y la IA de Acadify han transformado la forma en que mis alumnos participan y aprenden.',
    avatar: 'https://randomuser.me/api/portraits/men/32.jpg',
  },
  {
    name: 'Ana Torres',
    role: 'Desarrolladora y mentora',
    text: 'Me encanta que sea open source y que la comunidad pueda aportar. ¡El diseño es moderno y funcional!',
    avatar: 'https://randomuser.me/api/portraits/women/68.jpg',
  },
];

export default function TestimonialsSection() {
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
          Lo que dicen nuestros usuarios
        </motion.h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((t, idx) => (
            <motion.div
              key={t.name}
              className="rounded-2xl shadow-xl bg-white/90 dark:bg-[#18181b] border border-gray-100 dark:border-gray-800 p-8 flex flex-col items-center text-center group hover:scale-105 transition-transform duration-300"
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * idx, duration: 0.7, type: 'spring' }}
            >
              <img src={t.avatar} alt={t.name} className="w-20 h-20 rounded-full mb-4 border-4 border-primary/30 dark:border-purple-400/30 shadow-lg object-cover" />
              <p className="text-gray-700 dark:text-gray-300 text-base mb-4 italic">“{t.text}”</p>
              <span className="font-bold text-primary dark:text-purple-200">{t.name}</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">{t.role}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
