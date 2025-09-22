import React from 'react';
import { motion } from 'framer-motion';
import { 
  FiTarget, FiZap, FiUsers, FiAward, FiTrendingUp, FiStar,
  FiBookOpen, FiHeart, FiShield, FiGlobe, FiCpu, FiGift
} from 'react-icons/fi';

const features = [
  {
    title: 'Gamificación Avanzada',
    description: 'Sistema de puntos, logros y retos que convierten cada lección en una aventura emocionante.',
    icon: FiTarget,
    color: 'from-violet-500 to-purple-600',
    bgColor: 'from-violet-50 to-purple-50',
  },
  {
    title: 'IA Personalizada',
    description: 'Inteligencia artificial que adapta el contenido a tu ritmo y estilo de aprendizaje único.',
    icon: FiCpu,
    color: 'from-blue-500 to-indigo-600',
    bgColor: 'from-blue-50 to-indigo-50',
  },
  {
    title: 'Comunidad Global',
    description: 'Conecta con estudiantes de todo el mundo y forma equipos para proyectos colaborativos.',
    icon: FiGlobe,
    color: 'from-emerald-500 to-teal-600',
    bgColor: 'from-emerald-50 to-teal-50',
  },
  {
    title: 'Certificaciones',
    description: 'Obtén certificados reconocidos internacionalmente y badges digitales para tu perfil.',
    icon: FiAward,
    color: 'from-yellow-500 to-orange-600',
    bgColor: 'from-yellow-50 to-orange-50',
  },
  {
    title: 'Mascota Virtual',
    description: 'Tu compañero de aprendizaje que evoluciona contigo y te motiva en cada paso.',
    icon: FiHeart,
    color: 'from-pink-500 to-rose-600',
    bgColor: 'from-pink-50 to-rose-50',
  },
  {
    title: 'Progreso Visual',
    description: 'Dashboards interactivos que muestran tu evolución y áreas de mejora en tiempo real.',
    icon: FiTrendingUp,
    color: 'from-cyan-500 to-blue-600',
    bgColor: 'from-cyan-50 to-blue-50',
  },
];

export default function FeaturesSection() {
  return (
    <section className="relative w-full py-24 bg-gradient-to-b from-white via-gray-50/30 to-white overflow-hidden">
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute top-20 left-10 w-64 h-64 rounded-full bg-gradient-to-br from-violet-200/30 to-purple-300/30 blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-20 right-10 w-80 h-80 rounded-full bg-gradient-to-br from-blue-200/30 to-indigo-300/30 blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [180, 270, 180],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header de sección */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-violet-100 to-purple-100 border border-violet-200 text-violet-700 font-medium text-sm mb-6"
          >
            <FiStar className="w-4 h-4" />
            Características únicas
          </motion.div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-gray-900 mb-6">
            ¿Por qué elegir{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600">
              Acadify
            </span>
            ?
          </h2>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Descubre las características revolucionarias que hacen de Acadify la plataforma 
            educativa más innovadora y atractiva del mercado.
          </p>
        </motion.div>

        {/* Grid de características */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 * idx, duration: 0.6 }}
                whileHover={{ y: -8, scale: 1.02 }}
                className="group relative"
              >
                {/* Tarjeta principal */}
                <div 
                  className="relative h-full p-8 rounded-3xl shadow-lg border border-white/50 backdrop-blur-sm transition-all duration-300 group-hover:shadow-2xl overflow-hidden"
                  style={{
                    background: `linear-gradient(145deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.95) 100%)`
                  }}
                >
                  {/* Fondo gradiente sutil */}
                  <div 
                    className={`absolute inset-0 bg-gradient-to-br ${feature.bgColor} opacity-0 group-hover:opacity-50 transition-opacity duration-300`}
                  />
                  
                  {/* Icono con efecto 3D */}
                  <motion.div
                    className={`relative w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center shadow-lg mb-6 mx-auto`}
                    whileHover={{ 
                      scale: 1.1, 
                      rotate: 5,
                      boxShadow: "0 20px 40px rgba(139, 92, 246, 0.3)"
                    }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    <Icon className="w-8 h-8 text-white" />
                    
                    {/* Efecto de brillo */}
                    <motion.div
                      className="absolute inset-0 rounded-2xl bg-gradient-to-r from-transparent via-white/30 to-transparent opacity-0 group-hover:opacity-100"
                      animate={{
                        x: ['-100%', '100%'],
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        repeatDelay: 2,
                      }}
                    />
                  </motion.div>

                  {/* Contenido */}
                  <div className="relative z-10 text-center">
                    <h3 className="text-xl font-bold text-gray-900 mb-4 group-hover:text-violet-700 transition-colors duration-300">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 leading-relaxed group-hover:text-gray-700 transition-colors duration-300">
                      {feature.description}
                    </p>
                  </div>

                  {/* Elementos decorativos */}
                  <div className="absolute top-4 right-4 w-2 h-2 bg-violet-400 rounded-full opacity-60"></div>
                  <div className="absolute bottom-4 left-4 w-1 h-1 bg-purple-400 rounded-full opacity-40"></div>
                  
                  {/* Efecto de borde animado */}
                  <motion.div
                    className="absolute inset-0 rounded-3xl border-2 border-transparent"
                    style={{
                      background: `linear-gradient(45deg, ${feature.color.replace('from-', '').replace(' to-', ', ')}) border-box`,
                      WebkitMask: 'linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0)',
                      WebkitMaskComposite: 'exclude',
                      opacity: 0,
                    }}
                    whileHover={{ opacity: 0.6 }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Call to action */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="text-center mt-16"
        >
          <motion.a
            href="/register"
            className="inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-violet-600 to-purple-600 text-white font-bold text-lg shadow-xl hover:shadow-2xl transition-all duration-300"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            <FiGift className="w-5 h-5" />
            <span>Empieza tu aventura gratis</span>
          </motion.a>
        </motion.div>
      </div>
    </section>
  );
}
