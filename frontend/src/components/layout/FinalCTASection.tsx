import React from 'react';
import { motion } from 'framer-motion';

export default function FinalCTASection() {
  return (
    <section className="relative w-full py-24 flex items-center justify-center overflow-hidden bg-white dark:bg-[#18181b]">
      <div className="relative z-10 max-w-2xl mx-auto px-4 flex flex-col items-center text-center">
        <motion.div
          className="backdrop-blur-xl bg-white/80 dark:bg-[#23232b]/90 rounded-3xl shadow-2xl border border-gray-200 dark:border-primary/30 px-8 py-14 flex flex-col items-center"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <motion.h2
            className="text-4xl md:text-5xl font-extrabold mb-6 text-primary dark:text-purple-200 drop-shadow-xl tracking-tight"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
          >
            ¡Haz parte de la revolución educativa!
          </motion.h2>
          <motion.p
            className="text-lg md:text-2xl text-gray-700 dark:text-gray-200 mb-10 max-w-xl font-medium"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.7 }}
          >
            Regístrate gratis y comienza a aprender, jugar y crecer con Acadify.<br className="hidden md:block" />
            ¡Convierte tu educación en una experiencia divertida y significativa!
          </motion.p>
          <motion.a
            href="/register"
            className="inline-block px-14 py-5 rounded-2xl bg-gradient-to-r from-primary to-purple-600 text-white font-extrabold text-2xl shadow-xl hover:scale-105 hover:from-purple-700 hover:to-primary transition-all duration-300 drop-shadow-xl border-4 border-white/80 dark:border-primary/40"
            whileTap={{ scale: 0.97 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.7 }}
          >
            ¡Comenzar ahora!
          </motion.a>
        </motion.div>
      </div>
    </section>
  );
}
