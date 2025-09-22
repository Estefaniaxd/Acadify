import React from 'react';
import { motion } from 'framer-motion';
// import mascot from '../../assets/mascot.png'; // Descomenta y coloca tu imagen aquí

export default function HeroSection() {
  return (
    <section className="relative w-full min-h-[70vh] flex flex-col md:flex-row items-center justify-center bg-gradient-to-br from-[#f3f0ff] via-[#e9e4fa] to-[#f7f7fb] dark:from-black dark:via-[#18181b] dark:to-[#18181b] py-16 overflow-hidden">
      {/* Fondo animado */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
        style={{ zIndex: 0 }}
      >
        <svg width="100%" height="100%" viewBox="0 0 1440 320" fill="none" className="absolute bottom-0 left-0">
          <path fill="#8b5cf6" fillOpacity="0.10" d="M0,160L60,170.7C120,181,240,203,360,197.3C480,192,600,160,720,133.3C840,107,960,85,1080,101.3C1200,117,1320,171,1380,197.3L1440,224L1440,320L1380,320C1320,320,1200,320,1080,320C960,320,840,320,720,320C600,320,480,320,360,320C240,320,120,320,60,320L0,320Z"></path>
        </svg>
      </motion.div>
      {/* Contenido principal */}
      <div className="relative z-10 flex-1 flex flex-col items-center md:items-start text-center md:text-left gap-6 px-6">
        <motion.h1
          className="text-4xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-400 dark:from-primary dark:to-purple-300"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          Aprende, juega y potencia tu futuro
        </motion.h1>
        <motion.p
          className="text-lg md:text-2xl text-gray-700 dark:text-gray-300 max-w-xl"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.7 }}
        >
          Plataforma educativa gamificada con retos, logros y una mascota que te acompaña en tu aprendizaje. ¡Haz que estudiar sea divertido!
        </motion.p>
        <motion.div
          className="flex flex-col sm:flex-row gap-4 mt-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.7 }}
        >
          <a href="/register">
            <button className="px-8 py-3 rounded-xl bg-gradient-to-r from-primary to-purple-600 text-white font-bold shadow-lg hover:scale-105 transition-transform text-lg">
              ¡Comienza gratis!
            </button>
          </a>
          <a href="/about">
            <button className="px-8 py-3 rounded-xl border border-primary text-primary dark:text-purple-300 bg-white/70 dark:bg-black/10 font-bold hover:bg-primary/10 hover:scale-105 transition-all text-lg">
              Saber más
            </button>
          </a>
        </motion.div>
      </div>
      {/* Espacio para la mascota */}
      <motion.div
        className="relative z-10 flex-1 flex items-center justify-center mt-10 md:mt-0"
        initial={{ opacity: 0, scale: 0.8, x: 60 }}
        animate={{ opacity: 1, scale: 1, x: 0 }}
        transition={{ delay: 0.3, duration: 0.8, type: 'spring' }}
      >
        <div className="w-[260px] h-[260px] md:w-[340px] md:h-[340px] rounded-full flex items-center justify-center shadow-2xl border-4 border-black/10 dark:border-white/10 bg-white/90 dark:bg-black/40">
          {/* Coloca aquí tu imagen de mascota, ejemplo: */}
          {/* <img src={mascot} alt=\"Mascota Acadify\" className=\"w-48 md:w-72 object-contain drop-shadow-xl\" /> */}
          <span className="text-gray-400 dark:text-gray-500 text-center text-base select-none">Agrega aquí tu imagen de mascota</span>
        </div>
      </motion.div>
    </section>
  );
}
