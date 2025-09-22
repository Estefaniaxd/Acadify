import React from 'react';
import { motion } from 'framer-motion';
import { SiReact, SiFastapi, SiPostgresql, SiTailwindcss, SiVite, SiGithub, SiPython, SiTypescript } from 'react-icons/si';

const techs = [
  { name: 'React', icon: <SiReact className="w-10 h-10 text-sky-500" /> },
  { name: 'FastAPI', icon: <SiFastapi className="w-10 h-10 text-emerald-500" /> },
  { name: 'PostgreSQL', icon: <SiPostgresql className="w-10 h-10 text-blue-700" /> },
  { name: 'Tailwind CSS', icon: <SiTailwindcss className="w-10 h-10 text-cyan-400" /> },
  { name: 'Vite', icon: <SiVite className="w-10 h-10 text-yellow-400" /> },
  { name: 'Python', icon: <SiPython className="w-10 h-10 text-yellow-500" /> },
  { name: 'TypeScript', icon: <SiTypescript className="w-10 h-10 text-blue-500" /> },
  { name: 'GitHub', icon: <SiGithub className="w-10 h-10 text-gray-800 dark:text-gray-200" /> },
];

export default function OpenSourceSection() {
  return (
    <section className="w-full py-20 bg-gradient-to-b from-white via-[#f3f0ff] to-[#f7f7fb] dark:from-[#18181b] dark:via-[#18181b] dark:to-black">
      <div className="max-w-4xl mx-auto px-4 flex flex-col items-center text-center">
        <motion.h2
          className="text-3xl md:text-5xl font-extrabold mb-4 text-primary dark:text-purple-200"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
        >
          100% Open Source
        </motion.h2>
        <motion.p
          className="text-lg md:text-xl text-gray-700 dark:text-gray-300 max-w-2xl mb-8"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.7 }}
        >
          Acadify está construido con tecnologías modernas y abiertas. ¡Explora, aprende y contribuye a la comunidad!
        </motion.p>
        <div className="flex flex-wrap justify-center gap-6 mb-8">
          {techs.map((tech, idx) => (
            <motion.div
              key={tech.name}
              className="flex flex-col items-center group"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.05 * idx, duration: 0.5 }}
            >
              <div className="bg-white dark:bg-[#18181b] rounded-full shadow-lg p-4 mb-2 border border-gray-100 dark:border-gray-800 group-hover:scale-110 transition-transform">
                {tech.icon}
              </div>
              <span className="text-xs text-gray-600 dark:text-gray-400 font-semibold">{tech.name}</span>
            </motion.div>
          ))}
        </div>
        <motion.a
          href="https://github.com/Estefaniaxd/Acadify"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block px-8 py-3 rounded-xl bg-gradient-to-r from-primary to-purple-600 text-white font-bold shadow-lg hover:scale-105 transition-transform text-lg"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3, duration: 0.7 }}
        >
          Ver repositorio en GitHub
        </motion.a>
      </div>
    </section>
  );
}
