import React from 'react';
import { motion } from 'framer-motion';
import { FiPlay, FiArrowRight, FiStar, FiUsers, FiTrendingUp, FiZap } from 'react-icons/fi';

export default function HeroSection() {
  return (
    <section className="relative w-full min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-white via-purple-50/30 to-violet-100/40 dark:from-gray-900 dark:via-purple-900/20 dark:to-violet-900/30">
      {/* Fondo animado con formas geométricas */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Círculos animados de fondo */}
        <motion.div
          className="absolute -top-20 -left-20 w-96 h-96 rounded-full bg-gradient-to-br from-violet-400/20 to-purple-600/20 blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
        />
        <motion.div
          className="absolute -bottom-20 -right-20 w-80 h-80 rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [360, 180, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear"
          }}
        />
        <motion.div
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-blue-400/10 to-violet-400/10 blur-3xl"
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />

        {/* Partículas flotantes */}
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-gradient-to-r from-violet-400 to-purple-500 rounded-full opacity-60"
            style={{
              left: `${20 + (i * 15)}%`,
              top: `${30 + (i * 10)}%`,
            }}
            animate={{
              y: [-20, 20, -20],
              opacity: [0.6, 1, 0.6],
            }}
            transition={{
              duration: 3 + i,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.5,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 container mx-auto px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* Contenido principal */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
            className="text-center lg:text-left space-y-8"
          >
            {/* Badge de presentación */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-violet-100 to-purple-100 dark:from-violet-900/50 dark:to-purple-900/50 border border-violet-200 dark:border-violet-700 text-violet-700 dark:text-violet-300 font-medium text-sm"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              >
                <FiZap className="w-4 h-4" />
              </motion.div>
              Plataforma educativa del futuro
            </motion.div>

            {/* Título principal */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="text-4xl md:text-5xl lg:text-6xl font-black leading-tight"
            >
              <span className="text-gray-900 dark:text-white">Aprende, </span>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600">
                juega
              </span>
              <br />
              <span className="text-gray-900 dark:text-white">y </span>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 via-teal-500 to-blue-500">
                potencia
              </span>
              <br />
              <span className="text-gray-900 dark:text-white">tu futuro</span>
            </motion.h1>

            {/* Descripción */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="text-lg md:text-xl text-gray-600 dark:text-gray-300 leading-relaxed max-w-2xl"
            >
              Únete a la revolución educativa con nuestra plataforma gamificada. 
              Logros, retos y una mascota que te acompaña en cada paso de tu aprendizaje.
            </motion.p>

            {/* Estadísticas */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="flex flex-wrap gap-6 justify-center lg:justify-start"
            >
              {[
                { icon: FiUsers, value: "10K+", label: "Estudiantes" },
                { icon: FiStar, value: "500+", label: "Instituciones" },
                { icon: FiTrendingUp, value: "98%", label: "Satisfacción" },
              ].map((stat, index) => (
                <motion.div
                  key={stat.label}
                  whileHover={{ scale: 1.05 }}
                  className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-white/50 dark:border-gray-700/50 shadow-lg"
                >
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                    <stat.icon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="text-xl font-bold text-gray-900 dark:text-white">{stat.value}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</div>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {/* Botones de acción */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7, duration: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
            >
              <motion.a
                href="/register"
                className="group relative inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-violet-600 to-purple-600 text-white font-bold text-lg shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden"
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="relative z-10">¡Comienza gratis!</span>
                <motion.div
                  className="relative z-10"
                  animate={{ x: [0, 4, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <FiArrowRight className="w-5 h-5" />
                </motion.div>
                
                {/* Efecto de brillo */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                  animate={{
                    x: ['-100%', '100%'],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    repeatDelay: 3,
                  }}
                />
              </motion.a>

              <motion.a
                href="/demo"
                className="group inline-flex items-center gap-3 px-8 py-4 rounded-2xl border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-bold text-lg hover:border-violet-300 dark:hover:border-violet-500 hover:text-violet-600 dark:hover:text-violet-400 transition-all duration-300 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm"
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <FiPlay className="w-5 h-5" />
                <span>Ver demo</span>
              </motion.a>
            </motion.div>
          </motion.div>

          {/* Área visual con mascota y elementos 3D */}
          <motion.div
            initial={{ opacity: 0, x: 50, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            transition={{ delay: 0.4, duration: 1, type: 'spring', stiffness: 100 }}
            className="relative flex items-center justify-center"
          >
            {/* Contenedor principal de la mascota */}
            <div className="relative w-80 h-80 lg:w-96 lg:h-96">
              {/* Círculo de fondo con gradiente */}
              <motion.div
                className="absolute inset-0 rounded-full bg-gradient-to-br from-violet-400/20 via-purple-500/20 to-pink-500/20 blur-xl"
                animate={{
                  scale: [1, 1.1, 1],
                  rotate: [0, 180, 360],
                }}
                transition={{
                  duration: 8,
                  repeat: Infinity,
                  ease: "linear"
                }}
              />
              
              {/* Círculo principal */}
              <motion.div
                className="relative w-full h-full rounded-full flex items-center justify-center shadow-2xl border-4 border-white/20 dark:border-gray-700/50 overflow-hidden bg-gradient-to-br from-white/90 to-gray-50/95 dark:from-gray-800/90 dark:to-gray-700/95"
                style={{
                  backdropFilter: 'blur(20px)',
                }}
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                {/* Placeholder para mascota */}
                <div className="text-center">
                  <motion.div
                    animate={{ y: [-5, 5, -5] }}
                    transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                    className="text-6xl mb-4"
                  >
                    🚀
                  </motion.div>
                  <p className="text-gray-600 dark:text-gray-300 text-lg font-medium">
                    Tu mascota de aprendizaje
                  </p>
                  <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">
                    ¡Pronto tendrás tu compañero!
                  </p>
                </div>
                
                {/* Efectos de partículas alrededor de la mascota */}
                {[...Array(8)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-3 h-3 bg-gradient-to-r from-violet-400 to-purple-500 rounded-full"
                    style={{
                      left: `${50 + 30 * Math.cos((i * Math.PI) / 4)}%`,
                      top: `${50 + 30 * Math.sin((i * Math.PI) / 4)}%`,
                    }}
                    animate={{
                      scale: [0.5, 1, 0.5],
                      opacity: [0.3, 1, 0.3],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      delay: i * 0.2,
                    }}
                  />
                ))}
              </motion.div>

              {/* Elementos flotantes alrededor */}
              <motion.div
                className="absolute -top-4 -right-4 w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg border border-white/30"
                animate={{
                  y: [-5, 5, -5],
                  rotate: [0, 5, 0],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.5,
                }}
              >
                <FiStar className="w-8 h-8 text-white" />
              </motion.div>

              <motion.div
                className="absolute -bottom-4 -left-4 w-14 h-14 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl flex items-center justify-center shadow-lg border border-white/30"
                animate={{
                  y: [5, -5, 5],
                  rotate: [0, -5, 0],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 1,
                }}
              >
                <FiTrendingUp className="w-6 h-6 text-white" />
              </motion.div>

              <motion.div
                className="absolute top-1/2 -left-8 w-12 h-12 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-2xl flex items-center justify-center shadow-lg border border-white/30"
                animate={{
                  x: [-3, 3, -3],
                  rotate: [0, 10, 0],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 1.5,
                }}
              >
                <FiUsers className="w-5 h-5 text-white" />
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
