import React from 'react';
import { motion } from 'framer-motion';
import { 
  FiUserPlus, FiPlay, FiTrendingUp, FiAward, 
  FiArrowRight, FiCheckCircle, FiZap, FiStar 
} from 'react-icons/fi';

const steps = [
  {
    title: 'Regístrate gratis',
    description: 'Únete a nuestra comunidad en segundos y comienza tu aventura educativa inmediatamente.',
    icon: FiUserPlus,
    color: 'from-emerald-500 to-teal-600',
    bgPattern: 'emerald',
    number: '01'
  },
  {
    title: 'Explora y aprende',
    description: 'Sumérgete en contenido interactivo diseñado específicamente para tu nivel y objetivos.',
    icon: FiPlay,
    color: 'from-blue-500 to-indigo-600',
    bgPattern: 'blue',
    number: '02'
  },
  {
    title: 'Gana y crece',
    description: 'Completa retos emocionantes, acumula puntos y ve cómo tus habilidades evolucionan.',
    icon: FiTrendingUp,
    color: 'from-violet-500 to-purple-600',
    bgPattern: 'violet',
    number: '03'
  },
  {
    title: 'Certifícate',
    description: 'Recibe reconocimientos oficiales y certificados que validen tu progreso profesional.',
    icon: FiAward,
    color: 'from-yellow-500 to-orange-600',
    bgPattern: 'yellow',
    number: '04'
  },
];

export default function HowItWorksSection() {
  return (
  <section className="relative w-full py-24 bg-gradient-to-b from-gray-50 via-white to-violet-50/30 dark:from-gray-900 dark:via-gray-900/40 dark:to-violet-900/30 overflow-hidden">
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-gradient-to-br from-violet-200/20 to-purple-300/20 dark:from-violet-900/20 dark:to-purple-900/20 blur-3xl"
          animate={{ scale: [1, 1.3, 1], x: [0, 50, 0], y: [0, -30, 0] }}
          transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-gradient-to-br from-blue-200/20 to-indigo-300/20 dark:from-blue-900/20 dark:to-indigo-900/20 blur-3xl"
          animate={{ scale: [1.3, 1, 1.3], x: [0, -40, 0], y: [0, 40, 0] }}
          transition={{ duration: 25, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header de sección */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-violet-100 to-purple-100 border border-violet-200 text-violet-700 font-medium text-sm mb-6"
          >
            <FiZap className="w-4 h-4" />
            Proceso simple y efectivo
          </motion.div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-gray-900 dark:text-white mb-6">
            ¿Cómo funciona{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600">
              Acadify
            </span>
            ?
          </h2>
          
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Únete a miles de estudiantes que ya han transformado su manera de aprender 
            con nuestro revolucionario sistema en solo 4 pasos.
          </p>
        </motion.div>

        {/* Línea de conexión para escritorio */}
        <div className="hidden lg:block relative mb-16">
          <motion.div
            className="absolute top-24 left-32 right-32 h-0.5 bg-gradient-to-r from-violet-200 via-purple-300 to-pink-200"
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1, duration: 1.5, ease: "easeInOut" }}
          />
        </div>

        {/* Grid de pasos */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-6">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 * idx, duration: 0.8 }}
                className="relative group"
              >
                {/* Número de paso flotante */}
                <motion.div
                  className={`absolute -top-6 left-6 z-20 w-12 h-12 rounded-2xl bg-gradient-to-br ${step.color} shadow-lg flex items-center justify-center`}
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <span className="text-white font-black text-lg">{step.number}</span>
                </motion.div>

                {/* Tarjeta principal */}
                <motion.div
                  className="relative h-full pt-8 p-8 rounded-3xl bg-white/80 dark:bg-gray-900/90 backdrop-blur-sm border border-white/50 dark:border-gray-800/60 shadow-xl transition-all duration-500 group-hover:shadow-2xl overflow-hidden"
                  whileHover={{ y: -10, scale: 1.02 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  {/* Patrón de fondo animado */}
                  <motion.div
                    className={`absolute inset-0 opacity-0 group-hover:opacity-10 dark:group-hover:opacity-20 transition-opacity duration-500`}
                    style={{
                      background: `radial-gradient(circle at 30% 30%, ${step.color.includes('emerald') ? '#10b981' : step.color.includes('blue') ? '#3b82f6' : step.color.includes('violet') ? '#8b5cf6' : '#f59e0b'} 0%, transparent 50%)`
                    }}
                  />

                  {/* Icono principal */}
                  <motion.div
                    className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-lg mb-6 mx-auto relative overflow-hidden`}
                    whileHover={{ 
                      scale: 1.15, 
                      rotate: [0, -10, 10, 0],
                      boxShadow: "0 25px 50px -12px rgba(139, 92, 246, 0.4)"
                    }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    <Icon className="w-8 h-8 text-white relative z-10" />
                    {/* Efecto de brillo eliminado por feedback */}
                  </motion.div>

                  {/* Contenido */}
                  <div className="relative z-10 text-center">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 group-hover:text-violet-700 dark:group-hover:text-violet-300 transition-colors duration-300">
                      {step.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300 leading-relaxed group-hover:text-gray-700 dark:group-hover:text-violet-200 transition-colors duration-300">
                      {step.description}
                    </p>
                  </div>

                  {/* Indicador de progreso */}
                  <motion.div
                    className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    initial={{ y: 10 }}
                    whileHover={{ y: 0 }}
                  >
                    <FiCheckCircle className="w-4 h-4 text-emerald-500" />
                    <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400">Completado</span>
                  </motion.div>

                  {/* Elementos decorativos */}
                  <div className="absolute top-6 right-6 w-2 h-2 bg-violet-400 dark:bg-violet-700 rounded-full opacity-60"></div>
                  <div className="absolute bottom-6 left-6 w-1 h-1 bg-purple-400 dark:bg-purple-700 rounded-full opacity-40"></div>
                </motion.div>

                {/* Flecha de conexión (solo en desktop) */}
                {idx < steps.length - 1 && (
                  <motion.div
                    className="hidden lg:block absolute top-24 -right-3 z-10"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.8 + (0.2 * idx), duration: 0.6 }}
                  >
                    <div className="w-6 h-6 rounded-full bg-white border-2 border-violet-300 flex items-center justify-center shadow-lg">
                      <FiArrowRight className="w-3 h-3 text-violet-600" />
                    </div>
                  </motion.div>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Call to action de sección */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 1.2, duration: 0.8 }}
          className="text-center mt-20"
        >
          <motion.div
            className="inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-violet-600 to-purple-600 text-white font-bold text-lg shadow-xl hover:shadow-2xl transition-all duration-300 cursor-pointer focus:outline-none focus:ring-2 focus:ring-violet-400 dark:focus:ring-violet-700"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            <FiStar className="w-5 h-5" />
            <span>Comienza tu transformación ahora</span>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
