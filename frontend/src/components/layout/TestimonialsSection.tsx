import React from 'react';
import { motion } from 'framer-motion';
import { FiStar, FiUsers, FiHeart } from 'react-icons/fi';
import { RiDoubleQuotesL } from 'react-icons/ri';

const testimonials = [
  {
    name: 'María López',
    role: 'Estudiante de Ingeniería',
    university: 'Universidad Tecnológica',
    text: 'Acadify transformó completamente mi experiencia de aprendizaje. Los retos gamificados me mantienen motivada y las recompensas hacen que cada logro se sienta increíble. ¡Mi rendimiento académico mejoró un 40%!',
    avatar: 'https://randomuser.me/api/portraits/women/44.jpg',
    rating: 5,
    color: 'from-pink-500 to-rose-600',
    bgColor: 'from-pink-50 to-rose-50',
  },
  {
    name: 'Carlos Pérez',
    role: 'Docente universitario',
    university: 'Instituto de Ciencias',
    text: 'La inteligencia artificial y la gamificación de Acadify revolucionaron mi metodología de enseñanza. Mis estudiantes están más comprometidos que nunca y los resultados de aprendizaje son extraordinarios.',
    avatar: 'https://randomuser.me/api/portraits/men/32.jpg',
    rating: 5,
    color: 'from-blue-500 to-indigo-600',
    bgColor: 'from-blue-50 to-indigo-50',
  },
  {
    name: 'Ana Torres',
    role: 'Desarrolladora Full-Stack',
    university: 'Freelancer & Mentora',
    text: 'Como desarrolladora, aprecio profundamente que Acadify sea open source. La comunidad es increíble y el impacto social que genera es inspirador. La plataforma es técnicamente excelente y visualmente stunning.',
    avatar: 'https://randomuser.me/api/portraits/women/68.jpg',
    rating: 5,
    color: 'from-emerald-500 to-teal-600',
    bgColor: 'from-emerald-50 to-teal-50',
  },
];

export default function TestimonialsSection() {
  return (
    <section className="relative w-full py-24 bg-gradient-to-b from-white via-violet-50/30 to-gray-50 dark:from-gray-900 dark:via-violet-900/40 dark:to-gray-900 overflow-hidden">
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute top-20 right-20 w-72 h-72 rounded-full bg-gradient-to-br from-violet-200/30 to-purple-300/30 dark:from-violet-900/30 dark:to-purple-900/30 blur-3xl"
          animate={{ scale: [1, 1.4, 1], rotate: [0, 180, 360] }}
          transition={{ duration: 30, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-32 left-20 w-64 h-64 rounded-full bg-gradient-to-br from-blue-200/30 to-indigo-300/30 dark:from-blue-900/30 dark:to-indigo-900/30 blur-3xl"
          animate={{ scale: [1.2, 1, 1.2], rotate: [360, 180, 0] }}
          transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
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
            <FiUsers className="w-4 h-4" />
            Testimonios reales
          </motion.div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-gray-900 dark:text-white mb-6">
            Lo que dicen nuestros{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600">
              usuarios
            </span>
          </h2>
          
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Miles de estudiantes y educadores ya han transformado su experiencia de aprendizaje. 
            Descubre por qué Acadify es la plataforma educativa más amada del momento.
          </p>
        </motion.div>

        {/* Grid de testimonios */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {testimonials.map((testimonial, idx) => (
            <motion.div
              key={testimonial.name}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 * idx, duration: 0.8 }}
              whileHover={{ y: -10, scale: 1.02 }}
              className="group relative"
            >
              {/* Tarjeta principal */}
              <div className="relative h-full p-8 rounded-3xl bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm border border-white/50 dark:border-gray-800/60 shadow-xl transition-all duration-500 group-hover:shadow-2xl overflow-hidden">
                {/* Fondo gradiente sutil */}
                <div 
                  className={`absolute inset-0 bg-gradient-to-br ${testimonial.bgColor} dark:from-gray-800 dark:to-gray-900 opacity-0 group-hover:opacity-60 dark:group-hover:opacity-40 transition-opacity duration-500`}
                />
                
                {/* Icono de comillas */}
                <motion.div
                  className={`absolute top-6 right-6 w-12 h-12 rounded-2xl bg-gradient-to-br ${testimonial.color} dark:from-violet-900 dark:to-purple-900 flex items-center justify-center shadow-lg opacity-20 group-hover:opacity-100 transition-opacity duration-300`}
                  whileHover={{ rotate: 10, scale: 1.1 }}
                >
                  <RiDoubleQuotesL className="w-6 h-6 text-white" />
                </motion.div>

                {/* Avatar con efecto 3D */}
                <motion.div
                  className="relative mb-6"
                  whileHover={{ scale: 1.05 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <div className={`w-20 h-20 rounded-full bg-gradient-to-br ${testimonial.color} dark:from-violet-900 dark:to-purple-900 p-1 mx-auto shadow-lg`}>
                    <img 
                      src={testimonial.avatar} 
                      alt={testimonial.name} 
                      className="w-full h-full rounded-full object-cover border-2 border-white dark:border-gray-800"
                    />
                  </div>
                  
                  {/* Badge de verificación */}
                  <motion.div
                    className="absolute -bottom-1 -right-1 w-6 h-6 bg-gradient-to-br from-emerald-500 to-teal-600 dark:from-emerald-800 dark:to-teal-800 rounded-full flex items-center justify-center shadow-lg border-2 border-white dark:border-gray-800"
                    whileHover={{ scale: 1.2 }}
                  >
                    <FiHeart className="w-3 h-3 text-white" />
                  </motion.div>
                </motion.div>

                {/* Rating */}
                <div className="flex justify-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, scale: 0 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.5 + (i * 0.1), duration: 0.3 }}
                      whileHover={{ scale: 1.2 }}
                    >
                      <FiStar className="w-5 h-5 text-yellow-400 fill-current" />
                    </motion.div>
                  ))}
                </div>

                {/* Texto del testimonio */}
                <div className="relative z-10 mb-6">
                  <p className="text-gray-700 dark:text-gray-200 leading-relaxed text-center group-hover:text-gray-800 dark:group-hover:text-white transition-colors duration-300 italic">
                    "{testimonial.text}"
                  </p>
                </div>

                {/* Información del usuario */}
                <div className="relative z-10 text-center">
                  <h4 className="font-bold text-gray-900 dark:text-white mb-1 group-hover:text-violet-700 dark:group-hover:text-violet-300 transition-colors duration-300">
                    {testimonial.name}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-1 group-hover:text-gray-700 dark:group-hover:text-gray-200 transition-colors duration-300">
                    {testimonial.role}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors duration-300">
                    {testimonial.university}
                  </p>
                </div>

                {/* Elementos decorativos */}
                <div className="absolute bottom-4 left-4 w-2 h-2 bg-violet-400 dark:bg-violet-700 rounded-full opacity-40"></div>
                <div className="absolute top-4 left-4 w-1 h-1 bg-purple-400 dark:bg-purple-700 rounded-full opacity-60"></div>
                
                {/* Efecto de brillo eliminado por feedback */}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Estadísticas de confianza */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 1, duration: 0.8 }}
          className="mt-20 text-center"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { number: '50K+', label: 'Estudiantes activos' },
              { number: '1.2K+', label: 'Educadores certificados' },
              { number: '4.9', label: 'Rating promedio' },
              { number: '96%', label: 'Tasa de satisfacción' }
            ].map((stat, idx) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 1.2 + (0.1 * idx), duration: 0.6 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-purple-600 dark:from-violet-400 dark:to-purple-400 mb-2">
                  {stat.number}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300 font-medium">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}