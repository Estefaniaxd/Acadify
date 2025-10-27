import React from 'react';
import { motion } from 'framer-motion';
import { FiPlayCircle } from 'react-icons/fi';

export default function VideoSection() {
  return (
    <section className="relative w-full py-28 px-4 bg-gradient-to-br from-violet-50 via-white to-purple-100 dark:from-[#1a1330] dark:via-[#2a1a3a] dark:to-[#0a0712] overflow-hidden">
      {/* Fondo decorativo animado */}
      <motion.div
        className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-gradient-to-br from-primary/20 to-purple-400/10 blur-3xl"
        animate={{ scale: [1, 1.2, 1], rotate: [0, 180, 360] }}
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute bottom-0 right-0 w-80 h-80 rounded-full bg-gradient-to-br from-pink-400/10 to-rose-500/10 blur-3xl"
        animate={{ scale: [1.2, 1, 1.2], rotate: [360, 180, 0] }}
        transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
      />
      <div className="relative z-10 max-w-4xl mx-auto flex flex-col items-center text-center">
        <motion.h2
          className="text-4xl md:text-5xl font-black mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary via-purple-500 to-pink-400 dark:from-yellow-300 dark:via-purple-400 dark:to-pink-400"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          Descubre Acadify en acción
        </motion.h2>
        <motion.p
          className="text-lg md:text-xl text-gray-700 dark:text-gray-200 mb-10 max-w-2xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.7 }}
        >
          Mira este video para conocer cómo Acadify transforma el aprendizaje en una experiencia divertida, gamificada y colaborativa.
        </motion.p>
        <motion.div
          className="w-full aspect-video rounded-3xl overflow-hidden shadow-2xl border-4 border-white/60 dark:border-white/10 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 flex items-center justify-center group relative"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3, duration: 0.7 }}
        >
          <div className="text-center">
            <FiPlayCircle className="text-gray-400 dark:text-gray-500 w-24 h-24 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg font-medium">
              Video de presentación próximamente
            </p>
            <p className="text-gray-500 dark:text-gray-500 text-sm mt-2">
              ¡Mantente atento para ver Acadify en acción!
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
