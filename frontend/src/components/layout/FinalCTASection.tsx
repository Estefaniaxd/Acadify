import React from 'react';
import { motion } from 'framer-motion';
import { FiStar, FiArrowRight, FiZap, FiHeart, FiPlay } from 'react-icons/fi';
import { RiRocketLine } from 'react-icons/ri';

export default function FinalCTASection() {
  return (
    <section className="relative w-full py-32 overflow-hidden bg-gradient-to-br from-violet-900 via-purple-900 to-indigo-900">
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-gradient-to-br from-violet-400/30 to-purple-500/30 blur-3xl"
          animate={{
            scale: [1, 1.5, 1],
            rotate: [0, 180, 360],
            x: [0, 100, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-gradient-to-br from-pink-400/30 to-rose-500/30 blur-3xl"
          animate={{
            scale: [1.5, 1, 1.5],
            rotate: [360, 180, 0],
            x: [0, -80, 0],
            y: [0, 60, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        
        {/* Partículas flotantes */}
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white/20 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.2, 0.8, 0.2],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-6 lg:px-8">
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1 }}
        >
          {/* Badge superior */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-white font-medium text-sm mb-8"
          >
            <RiRocketLine className="w-4 h-4" />
            ¡Únete a la revolución educativa!
          </motion.div>

          {/* Título principal */}
          <motion.h2
            className="text-5xl md:text-6xl lg:text-7xl font-black text-white mb-8 leading-tight"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            Tu futuro comienza{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400">
              aquí
            </span>
          </motion.h2>

          {/* Descripción */}
          <motion.p
            className="text-xl md:text-2xl text-white/90 mb-12 max-w-4xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4, duration: 0.7 }}
          >
            Más de <strong className="text-yellow-400">50,000 estudiantes</strong> ya han transformado 
            su manera de aprender. Únete a la comunidad educativa más innovadora y 
            <strong className="text-pink-400"> gamificada</strong> del mundo.
          </motion.p>

          {/* Grid de estadísticas */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5, duration: 0.8 }}
          >
            {[
              { 
                icon: FiStar, 
                number: '4.9/5', 
                label: 'Rating promedio',
                color: 'from-yellow-400 to-orange-500'
              },
              { 
                icon: FiZap, 
                number: '95%', 
                label: 'Mejora en notas',
                color: 'from-blue-400 to-purple-500'
              },
              { 
                icon: FiHeart, 
                number: '∞', 
                label: 'Diversión garantizada',
                color: 'from-pink-400 to-rose-500'
              }
            ].map((stat, idx) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  className="text-center"
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.6 + (idx * 0.1), duration: 0.6 }}
                  whileHover={{ scale: 1.05 }}
                >
                  <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${stat.color} flex items-center justify-center mx-auto mb-4 shadow-lg`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <div className="text-3xl md:text-4xl font-black text-white mb-2">
                    {stat.number}
                  </div>
                  <div className="text-white/80 font-medium">
                    {stat.label}
                  </div>
                </motion.div>
              );
            })}
          </motion.div>

          {/* Call to action principal */}
          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.8, duration: 0.8 }}
          >
            <motion.a
              href="/register"
              className="group relative inline-flex items-center gap-3 px-10 py-5 rounded-2xl bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-500 text-black font-black text-xl shadow-2xl transition-all duration-300 overflow-hidden"
              whileHover={{ 
                scale: 1.05, 
                boxShadow: "0 25px 50px -12px rgba(245, 158, 11, 0.5)" 
              }}
              whileTap={{ scale: 0.95 }}
            >
              {/* Efecto de brillo animado */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -skew-x-12"
                animate={{
                  x: ['-100%', '200%'],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  repeatDelay: 3,
                  ease: "easeInOut"
                }}
              />
              
              <RiRocketLine className="w-6 h-6 relative z-10 group-hover:rotate-12 transition-transform duration-300" />
              <span className="relative z-10">¡Comenzar gratis ahora!</span>
              <FiArrowRight className="w-6 h-6 relative z-10 group-hover:translate-x-1 transition-transform duration-300" />
            </motion.a>

            <motion.a
              href="/demo"
              className="inline-flex items-center gap-2 px-8 py-5 rounded-2xl border-2 border-white/30 text-white font-bold text-lg hover:bg-white/10 transition-all duration-300"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <span>Ver demo</span>
            </motion.a>
          </motion.div>

          {/* Texto adicional */}
          <motion.p
            className="text-white/70 text-sm mt-8"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1, duration: 0.6 }}
          >
            ✨ Registro gratuito • Sin tarjeta de crédito • Comienza en segundos
          </motion.p>
        </motion.div>
      </div>
    </section>
  );
}
