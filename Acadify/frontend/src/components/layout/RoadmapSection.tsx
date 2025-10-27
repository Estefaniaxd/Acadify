import React from 'react';
import { motion } from 'framer-motion';
import { FiCalendar, FiTarget, FiUsers, FiSmartphone, FiGlobe, FiMail, FiArrowRight } from 'react-icons/fi';

const roadmap = [
  {
    title: 'Lanzamiento de la beta pública',
    date: 'Q4 2025',
    description: 'Acceso abierto a estudiantes y docentes, primeras instituciones registradas y sistema de feedback activo.',
    icon: FiTarget,
    color: 'from-violet-500 to-purple-600',
    status: 'próximo'
  },
  {
    title: 'Módulo de retos colaborativos',
    date: 'Q1 2026',
    description: 'Desafíos grupales avanzados, rankings competitivos y sistema de logros compartidos entre equipos.',
    icon: FiUsers,
    color: 'from-blue-500 to-indigo-600',
    status: 'planificado'
  },
  {
    title: 'Integración con IA generativa',
    date: 'Q2 2026',
    description: 'Recomendaciones personalizadas potenciadas por IA y generación automática de ejercicios adaptativos.',
    icon: FiTarget,
    color: 'from-emerald-500 to-teal-600',
    status: 'planificado'
  },
  {
    title: 'App móvil Acadify',
    date: 'Q3 2026',
    description: 'Lanzamiento oficial de aplicación nativa para iOS y Android con experiencia offline.',
    icon: FiSmartphone,
    color: 'from-pink-500 to-rose-600',
    status: 'planificado'
  },
  {
    title: 'Expansión internacional',
    date: 'Q4 2026',
    description: 'Soporte completo multiidioma, localización cultural y alianzas estratégicas globales.',
    icon: FiGlobe,
    color: 'from-yellow-500 to-orange-600',
    status: 'planificado'
  },
];

export default function RoadmapSection() {
  return (
  <section className="relative w-full py-24 bg-gradient-to-b from-white via-gray-50 to-violet-50/30 dark:bg-gradient-to-b dark:from-gray-900 dark:via-violet-950/60 dark:to-gray-900 overflow-hidden">
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute top-20 right-20 w-72 h-72 rounded-full bg-gradient-to-br from-violet-200/30 to-purple-300/30 dark:from-violet-900/30 dark:to-purple-900/30 blur-3xl"
          animate={{ scale: [1, 1.4, 1], rotate: [0, 120, 240, 360] }}
          transition={{ duration: 30, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-32 left-20 w-64 h-64 rounded-full bg-gradient-to-br from-blue-200/30 to-indigo-300/30 dark:from-blue-900/30 dark:to-indigo-900/30 blur-3xl"
          animate={{ scale: [1.2, 1, 1.2], rotate: [360, 240, 120, 0] }}
          transition={{ duration: 35, repeat: Infinity, ease: "easeInOut" }}
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
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-violet-100 to-purple-100 dark:from-violet-900 dark:to-purple-900 border border-violet-200 dark:border-violet-800 text-violet-700 dark:text-violet-200 font-medium text-sm mb-6"
          >
            <FiCalendar className="w-4 h-4" />
            Hoja de ruta 2025-2026
          </motion.div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-gray-900 dark:text-white mb-6">
            El futuro de{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600">
              Acadify
            </span>
          </h2>
          
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Esto es solo el comienzo de una revolución educativa. Conoce nuestros planes ambiciosos 
            y únete a nosotros para construir el futuro de la educación.
          </p>
        </motion.div>

        {/* Timeline del roadmap */}
        <div className="relative">
          {/* Línea temporal */}
          <div className="hidden lg:block absolute left-1/2 transform -translate-x-1/2 w-1 h-full bg-gradient-to-b from-violet-300 via-purple-400 to-pink-400 rounded-full opacity-30" />
          
          <div className="space-y-16">
            {roadmap.map((item, idx) => {
              const Icon = item.icon;
              const isEven = idx % 2 === 0;
              
              return (
                <motion.div
                  key={item.title}
                  className={`relative flex items-center ${isEven ? 'lg:flex-row' : 'lg:flex-row-reverse'}`}
                  initial={{ opacity: 0, y: 50 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.2 * idx, duration: 0.8 }}
                >
                  {/* Contenido de la tarjeta */}
                  <div className={`w-full lg:w-5/12 ${isEven ? 'lg:pr-12' : 'lg:pl-12'}`}>
                    <motion.div
                      className="relative p-8 rounded-3xl bg-white/90 dark:bg-gradient-to-br dark:from-gray-900 dark:via-violet-950/60 dark:to-gray-900 backdrop-blur-sm border border-white/50 dark:border-gray-800/60 shadow-xl transition-all duration-500 hover:shadow-2xl overflow-hidden group"
                      whileHover={{ y: -8, scale: 1.02 }}
                    >
                      {/* Fondo gradiente sutil */}
                      <div className={`absolute inset-0 bg-gradient-to-br ${item.color} opacity-0 group-hover:opacity-10 dark:group-hover:opacity-20 transition-opacity duration-500`} />
                      {/* Badge de estado */}
                      <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold ${
                        item.status === 'próximo' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/60 dark:text-emerald-200' : 'bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-200'
                      }`}>
                        {item.status === 'próximo' ? 'Próximo' : 'Planificado'}
                      </div>
                      {/* Contenido */}
                      <div className="relative z-10">
                        <div className="flex items-start gap-4 mb-4">
                          <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${item.color} flex items-center justify-center shadow-lg`}>
                            <Icon className="w-8 h-8 text-white" />
                          </div>
                          <div className="flex-1">
                            <div className="text-sm font-bold text-violet-600 dark:text-violet-300 mb-1">{item.date}</div>
                            <h3 className="text-xl font-bold text-gray-900 dark:text-white group-hover:text-violet-700 dark:group-hover:text-violet-300 transition-colors duration-300">
                              {item.title}
                            </h3>
                          </div>
                        </div>
                        <p className="text-gray-600 dark:text-gray-300 leading-relaxed group-hover:text-gray-700 dark:group-hover:text-white transition-colors duration-300">
                          {item.description}
                        </p>
                      </div>
                      {/* Elementos decorativos */}
                      <div className="absolute bottom-4 left-4 w-2 h-2 bg-violet-400 dark:bg-violet-700 rounded-full opacity-40"></div>
                      <div className="absolute top-4 left-4 w-1 h-1 bg-purple-400 dark:bg-purple-700 rounded-full opacity-60"></div>
                    </motion.div>
                  </div>

                  {/* Nodo central en la línea temporal */}
                  <div className="hidden lg:block absolute left-1/2 transform -translate-x-1/2 w-6 h-6 bg-white dark:bg-gray-900 border-4 border-violet-400 dark:border-violet-700 rounded-full shadow-lg z-10" />
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Call to action de la sección */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 1, duration: 0.8 }}
          className="mt-24 text-center"
        >
          <div className="relative p-12 rounded-3xl bg-gradient-to-br from-violet-900 via-purple-900 to-indigo-900 text-white overflow-hidden dark:bg-gradient-to-br dark:from-gray-900 dark:via-violet-950/60 dark:to-purple-900">
            {/* Elementos decorativos */}
            <div className="absolute top-8 right-8 w-32 h-32 rounded-full bg-gradient-to-br from-violet-400/20 to-purple-500/20 blur-2xl" />
            <div className="absolute bottom-8 left-8 w-24 h-24 rounded-full bg-gradient-to-br from-pink-400/20 to-rose-500/20 blur-2xl" />
            
            <div className="relative z-10">
              <h3 className="text-3xl md:text-4xl font-bold mb-6">
                ¿Quieres ser parte del equipo?
              </h3>
              <p className="text-xl text-white/90 mb-8 max-w-3xl mx-auto leading-relaxed">
                Buscamos desarrolladores apasionados, educadores visionarios, diseñadores creativos 
                y entusiastas de la tecnología educativa. ¡Únete y ayúdanos a transformar la educación mundial!
              </p>
              
              <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
                <motion.a
                  href="/about"
                  className="inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-white text-violet-900 font-bold text-lg shadow-xl hover:shadow-2xl transition-all duration-300"
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>Conoce más sobre nosotros</span>
                  <FiArrowRight className="w-5 h-5" />
                </motion.a>
                
                <motion.a
                  href="mailto:contacto@acadify.org"
                  className="inline-flex items-center gap-3 px-8 py-4 rounded-2xl border-2 border-white/30 text-white font-bold text-lg hover:bg-white/10 transition-all duration-300"
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <FiMail className="w-5 h-5" />
                  <span>Contáctanos</span>
                </motion.a>
              </div>

              {/* Estadísticas de progreso */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12 pt-8 border-t border-white/20">
                {[
                  { number: '75%', label: 'Beta completada' },
                  { number: '12+', label: 'Meses de desarrollo' },
                  { number: '∞', label: 'Posibilidades futuras' }
                ].map((stat, idx) => (
                  <motion.div
                    key={stat.label}
                    className="text-center"
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 1.2 + (idx * 0.1), duration: 0.6 }}
                  >
                    <div className="text-3xl md:text-4xl font-black text-yellow-400 dark:text-yellow-300 mb-2">
                      {stat.number}
                    </div>
                    <div className="text-white/80 dark:text-gray-200 font-medium">
                      {stat.label}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
