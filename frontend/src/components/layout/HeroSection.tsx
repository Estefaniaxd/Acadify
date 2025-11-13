import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Play, Star, TrendingUp, Users, Zap } from 'lucide-react';
;

export default function HeroSection() {
  return (
    <section className="relative w-full min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-white via-violet-50/40 to-purple-100/50 dark:from-neutral-950 dark:via-violet-950/30 dark:to-purple-950/40 py-32 md:py-24">
      {/* Fondo animado mejorado con formas geométricas */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Blob animado 1 */}
        <motion.div
          className="absolute -top-32 -left-32 w-[500px] h-[500px] rounded-full bg-gradient-to-br from-violet-400/30 to-purple-600/30 dark:from-violet-600/20 dark:to-purple-800/20 blur-3xl"
          animate={{ 
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
            y: [0, 30, 0],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
        />
        {/* Blob animado 2 */}
        <motion.div
          className="absolute -bottom-32 -right-32 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-fuchsia-500/30 to-pink-500/30 dark:from-fuchsia-700/20 dark:to-pink-700/20 blur-3xl"
          animate={{ 
            scale: [1.2, 1, 1.2],
            x: [0, -40, 0],
            y: [0, -50, 0],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: 'easeInOut' }}
        />
        {/* Blob animado 3 */}
        <motion.div
          className="absolute top-1/3 right-1/4 w-[400px] h-[400px] rounded-full bg-gradient-to-br from-blue-400/20 to-cyan-500/20 dark:from-blue-600/15 dark:to-cyan-700/15 blur-3xl"
          animate={{ 
            scale: [1, 1.15, 1],
            opacity: [0.4, 0.6, 0.4],
          }}
          transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut' }}
        />
        {/* Partículas flotantes mejoradas */}
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-3 h-3 bg-gradient-to-br from-violet-400 to-purple-500 dark:from-violet-500 dark:to-purple-600 rounded-full shadow-lg shadow-violet-500/50"
            style={{ 
              left: `${15 + i * 12}%`, 
              top: `${25 + i * 8}%`,
            }}
            animate={{ 
              y: [-30, 30, -30],
              x: [-10, 10, -10],
              opacity: [0.4, 1, 0.4],
              scale: [0.8, 1.2, 0.8],
            }}
            transition={{ 
              duration: 4 + i * 0.5, 
              repeat: Infinity, 
              ease: 'easeInOut', 
              delay: i * 0.3 
            }}
          />
        ))}
      </div>
      <div className="relative z-10 container mx-auto px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* Columna izquierda: contenido principal */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
            className="text-center lg:text-left space-y-6"
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-violet-100 via-purple-100 to-fuchsia-100 dark:from-violet-950/80 dark:via-purple-950/80 dark:to-fuchsia-950/80 border-2 border-violet-300/50 dark:border-violet-700/50 text-violet-700 dark:text-violet-300 font-semibold text-sm shadow-lg shadow-violet-500/20 backdrop-blur-sm"
            >
              <motion.div 
                animate={{ rotate: 360, scale: [1, 1.2, 1] }} 
                transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                className="flex items-center justify-center"
              >
                <Zap className="w-4 h-4 text-violet-600 dark:text-violet-400" />
              </motion.div>
              Plataforma educativa del futuro
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="text-4xl md:text-5xl lg:text-6xl font-black leading-tight tracking-tight"
            >
              <span className="text-neutral-900 dark:text-white drop-shadow-lg">Aprende, </span>
              <span className="bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 dark:from-violet-400 dark:via-purple-400 dark:to-fuchsia-400 bg-clip-text text-transparent drop-shadow-2xl">
                juega
              </span>
              <br />
              <span className="text-neutral-900 dark:text-white drop-shadow-lg">y </span>
              <span className="bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 dark:from-emerald-400 dark:via-teal-400 dark:to-cyan-400 bg-clip-text text-transparent drop-shadow-2xl">
                crece
              </span>
              <br />
              <span className="text-neutral-900 dark:text-white drop-shadow-lg">con</span>{' '}
              <span className="bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 dark:from-amber-400 dark:via-orange-400 dark:to-red-400 bg-clip-text text-transparent drop-shadow-2xl">
                Acadify
              </span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="text-lg md:text-xl text-neutral-600 dark:text-neutral-300 leading-relaxed max-w-2xl"
            >
              Transforma tu educación con{' '}
              <span className="text-violet-600 dark:text-violet-400 font-bold">gamificación</span>,{' '}
              <span className="text-purple-600 dark:text-purple-400 font-bold">logros</span> y{' '}
              <span className="text-fuchsia-600 dark:text-fuchsia-400 font-bold">tu mascota</span> personal 
              que te motiva en cada paso del camino.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="flex flex-wrap gap-3 justify-center lg:justify-start"
            >
              {[
                { icon: Users, value: '10K+', label: 'Estudiantes', gradient: 'from-violet-500 to-purple-600' },
                { icon: Star, value: '500+', label: 'Instituciones', gradient: 'from-fuchsia-500 to-pink-600' },
                { icon: TrendingUp, value: '98%', label: 'Satisfacción', gradient: 'from-emerald-500 to-teal-600' },
              ].map((stat) => {
                const Icon = stat.icon;
                return (
                  <motion.div
                    key={stat.label}
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/90 dark:bg-neutral-900/90 backdrop-blur-md border border-violet-200/50 dark:border-violet-800/50 shadow-lg hover:shadow-xl transition-all duration-300"
                  >
                    <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${stat.gradient} flex items-center justify-center shadow-md`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <div className="text-lg font-black text-neutral-900 dark:text-white">{stat.value}</div>
                      <div className="text-xs font-medium text-neutral-600 dark:text-neutral-400">{stat.label}</div>
                    </div>
                  </motion.div>
                );
              })}
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7, duration: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
            >
              <motion.a
                href="/register"
                className="group relative inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 dark:from-violet-500 dark:via-purple-500 dark:to-fuchsia-500 text-white font-bold text-base shadow-lg shadow-violet-500/30 hover:shadow-xl hover:shadow-violet-600/40 transition-all duration-300 overflow-hidden"
                whileHover={{ scale: 1.03, y: -2 }}
                whileTap={{ scale: 0.97 }}
              >
                <span className="relative z-10">¡Comienza gratis!</span>
                <motion.div
                  className="relative z-10"
                  animate={{ x: [0, 3, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <ArrowRight className="w-5 h-5" />
                </motion.div>
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                  animate={{ x: ['-200%', '200%'] }}
                  transition={{ duration: 3, repeat: Infinity, repeatDelay: 2 }}
                />
              </motion.a>
              <motion.a
                href="/demo"
                className="group inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl border-2 border-violet-300 dark:border-violet-700 text-violet-700 dark:text-violet-300 font-semibold text-base hover:border-violet-500 dark:hover:border-violet-500 hover:bg-violet-50 dark:hover:bg-violet-950/50 transition-all duration-300 bg-white/90 dark:bg-neutral-900/90 backdrop-blur-md shadow-md"
                whileHover={{ scale: 1.03, y: -2 }}
                whileTap={{ scale: 0.97 }}
              >
                <motion.div
                  whileHover={{ scale: 1.2, rotate: 360 }}
                  transition={{ duration: 0.5 }}
                >
                  <Play className="w-4 h-4" />
                </motion.div>
                <span>Ver demo</span>
              </motion.a>
            </motion.div>
          </motion.div>
          {/* Columna derecha: visual mascota */}
          <motion.div
            initial={{ opacity: 0, x: 50, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            transition={{ delay: 0.4, duration: 1, type: 'spring', stiffness: 100 }}
            className="relative flex items-center justify-center"
          >
            <div className="relative w-80 h-80 lg:w-96 lg:h-96">
              <motion.div
                className="absolute inset-0 rounded-full bg-gradient-to-br from-violet-400/20 via-purple-500/20 to-pink-500/20 blur-xl"
                animate={{ scale: [1, 1.1, 1], rotate: [0, 180, 360] }}
                transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
              />
              <motion.div
                className="relative w-full h-full rounded-full flex items-center justify-center shadow-2xl border-4 border-white/20 dark:border-gray-700/50 overflow-hidden bg-gradient-to-br from-white/90 to-gray-50/95 dark:from-gray-900/90 dark:to-gray-800/95"
                style={{ backdropFilter: 'blur(20px)' }}
                whileHover={{ scale: 1.05 }}
                transition={{ type: 'spring', stiffness: 300 }}
              >
                <div className="text-center">
                  <motion.img
                    src="/rutilio_home.png"
                    alt="Rutilio"
                    className="w-80 h-80 mx-auto mb-4 object-contain"
                    animate={{ y: [-5, 5, -5] }}
                    transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                  />
                </div>
                {[...Array(8)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-3 h-3 bg-gradient-to-r from-violet-400 to-purple-500 rounded-full dark:from-violet-700 dark:to-purple-900"
                    style={{
                      left: `${50 + 30 * Math.cos((i * Math.PI) / 4)}%`,
                      top: `${50 + 30 * Math.sin((i * Math.PI) / 4)}%`,
                    }}
                    animate={{ scale: [0.5, 1, 0.5], opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 2, repeat: Infinity, delay: i * 0.2 }}
                  />
                ))}
              </motion.div>
              <motion.div
                className="absolute -top-4 -right-4 w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg border border-white/30 dark:from-yellow-600 dark:to-orange-700"
                animate={{ y: [-5, 5, -5], rotate: [0, 5, 0] }}
                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
              >
                <Star className="w-8 h-8 text-white" />
              </motion.div>
              <motion.div
                className="absolute -bottom-4 -left-4 w-14 h-14 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl flex items-center justify-center shadow-lg border border-white/30 dark:from-emerald-700 dark:to-teal-800"
                animate={{ y: [5, -5, 5], rotate: [0, -5, 0] }}
                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
              >
                <TrendingUp className="w-6 h-6 text-white" />
              </motion.div>
              <motion.div
                className="absolute top-1/2 -left-8 w-12 h-12 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-2xl flex items-center justify-center shadow-lg border border-white/30 dark:from-blue-900 dark:to-indigo-900"
                animate={{ x: [-3, 3, -3], rotate: [0, 10, 0] }}
                transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 1.5 }}
              >
                <Users className="w-5 h-5 text-white" />
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
// ...fin del componente principal...
