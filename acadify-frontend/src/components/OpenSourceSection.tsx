import React, { useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { 
  Code, 
  Github, 
  Heart, 
  Star, 
  GitBranch, 
  Users, 
  Globe, 
  Download,
  Zap,
  Shield,
  Sparkles,
  Trophy,
  Gift,
  Settings,
  Database,
  Container,
  Rocket,
  Lock,
  Unlock,
  Coffee
} from 'lucide-react';

const OpenSourceSection: React.FC = () => {
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" });

  const openSourceBenefits = [
    {
      icon: Unlock,
      title: '100% Gratuito',
      description: 'Sin costos ocultos, sin suscripciones. Solo acceso completo para siempre.',
      gradient: 'from-green-400 to-blue-500',
      delay: 0.1
    },
    {
      icon: Code,
      title: 'Código Abierto',
      description: 'Revisa, modifica y contribuye. La transparencia es nuestra filosofía.',
      gradient: 'from-purple-400 to-pink-500',
      delay: 0.2
    },
    {
      icon: Users,
      title: 'Comunidad Global',
      description: 'Miles de desarrolladores y educadores colaborando juntos.',
      gradient: 'from-orange-400 to-red-500',
      delay: 0.3
    },
    {
      icon: Shield,
      title: 'Seguro & Confiable',
      description: 'Código auditado por la comunidad, sin puertas traseras.',
      gradient: 'from-cyan-400 to-blue-500',
      delay: 0.4
    }
  ];

  const stats = [
    { icon: Star, number: '2.5K+', label: 'Stars en GitHub', color: 'text-yellow-400' },
    { icon: GitBranch, number: '150+', label: 'Contribuidores', color: 'text-green-400' },
    { icon: Download, number: '50K+', label: 'Descargas', color: 'text-blue-400' },
    { icon: Globe, number: '30+', label: 'Países', color: 'text-purple-400' }
  ];

  const techStack = [
    { name: 'React', color: '#61DAFB', icon: Code },
    { name: 'TypeScript', color: '#3178C6', icon: Code },
    { name: 'FastAPI', color: '#009688', icon: Rocket },
    { name: 'PostgreSQL', color: '#336791', icon: Database },
    { name: 'Redis', color: '#DC382D', icon: Database },
    { name: 'Docker', color: '#2496ED', icon: Container }
  ];

  return (
    <section id="opensource" ref={sectionRef} className="py-20 lg:py-32 bg-gradient-to-br from-gray-50 via-white to-primary-50 dark:from-dark-900 dark:via-dark-800 dark:to-primary-950 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0">
        {/* Geometric patterns */}
        <motion.div
          className="absolute top-1/4 left-1/6 w-32 h-32 bg-gradient-to-r from-primary-200 to-secondary-200 dark:from-neon-purple dark:to-neon-green rounded-full opacity-20 blur-xl"
          animate={{ 
            scale: [1, 1.3, 1],
            rotate: [0, 180, 360]
          }}
          transition={{ duration: 20, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-1/3 right-1/6 w-24 h-24 bg-gradient-to-r from-secondary-300 to-primary-300 dark:from-neon-green dark:to-neon-purple rounded-full opacity-20 blur-xl"
          animate={{ 
            scale: [1, 1.2, 1],
            x: [0, 30, 0],
            y: [0, -20, 0]
          }}
          transition={{ duration: 15, repeat: Infinity, delay: 3 }}
        />

        {/* Code symbols floating */}
        {['{', '}', '<', '>', '/', '*'].map((symbol, i) => (
          <motion.div
            key={i}
            className="absolute text-4xl font-mono text-primary-300 dark:text-neon-purple opacity-10"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -50, 0],
              rotate: [0, 180, 360],
              opacity: [0.1, 0.3, 0.1],
            }}
            transition={{
              duration: 8 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 5,
            }}
          >
            {symbol}
          </motion.div>
        ))}
      </div>

      <div className="container mx-auto px-6 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-600 to-secondary-600 px-6 py-3 rounded-full text-white font-bold mb-6"
          >
            <Heart className="w-5 h-5" />
            <span>Open Source & Gratuito</span>
            <Sparkles className="w-5 h-5" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-4xl lg:text-6xl font-display font-bold text-gray-900 mb-6"
          >
            Educación
            <br />
            <span className="text-primary-600">
              Libre Para Todos
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed"
          >
            Creemos que la educación de calidad debe ser <strong className="text-primary-600">accesible para todos</strong>. 
            Por eso Acadify es 100% gratuito, de código abierto y construido por la comunidad.
          </motion.p>
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-2 gap-16 items-center mb-20">
          {/* Left Side - Open Source Benefits */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 1 }}
          >
            <h3 className="text-2xl font-bold text-gray-900 mb-8 flex items-center justify-start space-x-3">
              <Heart className="w-7 h-7 text-primary-600" />
              <span>Beneficios del Código Abierto</span>
            </h3>
            
            <div className="grid grid-cols-1 gap-4">
              {openSourceBenefits.map((benefit, index) => {
                const IconComponent = benefit.icon;
                
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={isInView ? { opacity: 1, scale: 1 } : {}}
                    transition={{ delay: benefit.delay + 0.5, type: "spring" }}
                    className="flex items-center space-x-4 px-4 py-3 bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all duration-300"
                    whileHover={{ scale: 1.02, y: -2 }}
                  >
                    <IconComponent 
                      className="w-6 h-6 text-primary-600 flex-shrink-0" 
                    />
                    <div className="text-left">
                      <h4 className="font-semibold text-gray-900 text-sm">
                        {benefit.title}
                      </h4>
                      <p className="text-xs text-gray-600">
                        {benefit.description}
                      </p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>

          {/* Right Side - GitHub Integration */}
          <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 1, delay: 0.3 }}
            className="relative"
          >
            {/* GitHub Card */}
            <motion.div
              className="bg-white/80 backdrop-blur-xl rounded-3xl p-8 border border-gray-200 shadow-2xl"
              whileHover={{ scale: 1.02 }}
            >
              {/* GitHub Header */}
              <div className="flex items-center space-x-4 mb-6">
                <motion.div
                  className="w-16 h-16 bg-gradient-to-r from-gray-800 to-gray-900 rounded-2xl flex items-center justify-center"
                  animate={{ 
                    boxShadow: [
                      "0 0 0 0 rgba(31, 41, 55, 0.4)",
                      "0 0 0 20px rgba(31, 41, 55, 0)",
                      "0 0 0 0 rgba(31, 41, 55, 0)"
                    ]
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Github className="w-8 h-8 text-white" />
                </motion.div>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">
                    Estefaniaxd/Acadify
                  </h3>
                  <p className="text-gray-600">
                    Plataforma educativa gamificada
                  </p>
                </div>
              </div>

              {/* Repository Stats */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                {stats.map((stat, index) => {
                  const IconComponent = stat.icon;
                  
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={isInView ? { opacity: 1, y: 0 } : {}}
                      transition={{ delay: 0.8 + index * 0.1 }}
                      className="text-center p-4 bg-gray-50 rounded-2xl"
                      whileHover={{ scale: 1.05 }}
                    >
                      <IconComponent className={`w-6 h-6 mx-auto mb-2 ${stat.color}`} />
                      <div className="text-2xl font-bold text-gray-900 mb-1">
                        {stat.number}
                      </div>
                      <div className="text-sm text-gray-600">
                        {stat.label}
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                <motion.button
                  className="w-full py-3 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-2xl font-semibold flex items-center justify-center space-x-2 hover:shadow-xl transition-all duration-300"
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Github className="w-5 h-5" />
                  <span>Ver en GitHub</span>
                </motion.button>
                
                <motion.button
                  className="w-full py-3 bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-2xl font-semibold flex items-center justify-center space-x-2 hover:shadow-xl transition-all duration-300"
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Star className="w-5 h-5" />
                  <span>Dar Star ⭐</span>
                </motion.button>
              </div>
            </motion.div>

            {/* Floating Rutilio */}
            <motion.div
              className="absolute -top-6 -right-6 text-6xl"
              animate={{ 
                y: [0, -20, 0],
                rotate: [0, 10, -10, 0]
              }}
              transition={{ duration: 4, repeat: Infinity }}
            >
              😸
            </motion.div>
          </motion.div>
        </div>

        {/* Tech Stack */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 1 }}
          className="text-center mb-16"
        >
          <h3 className="text-2xl font-bold text-gray-900 mb-8 flex items-center justify-center space-x-3">
            <Settings className="w-7 h-7 text-primary-600" />
            <span>Construido con Tecnologías Modernas</span>
          </h3>
          
          <div className="flex flex-wrap justify-center gap-6">
            {techStack.map((tech, index) => {
              const IconComponent = tech.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0 }}
                  animate={isInView ? { opacity: 1, scale: 1 } : {}}
                  transition={{ delay: 1.2 + index * 0.1, type: "spring" }}
                  className="flex items-center space-x-3 px-6 py-3 bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200 shadow-sm"
                  whileHover={{ scale: 1.05, y: -5 }}
                >
                  <IconComponent 
                    className="w-6 h-6 text-primary-600" 
                    style={{ color: tech.color }} 
                  />
                  <span className="font-semibold text-gray-900">
                    {tech.name}
                  </span>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 1.5 }}
          className="text-center bg-gradient-to-r from-primary-50 to-secondary-50 rounded-3xl p-12 border border-primary-200"
        >
          <motion.div
            animate={{ 
              rotate: [0, 5, -5, 0],
              scale: [1, 1.05, 1]
            }}
            transition={{ duration: 4, repeat: Infinity }}
            className="text-6xl mb-6 flex justify-center"
          >
            <Rocket className="w-16 h-16 text-primary-600" />
          </motion.div>
          
          <h3 className="text-3xl font-bold text-gray-900 mb-4">
            ¿Listo para Contribuir?
          </h3>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Únete a nuestra comunidad de desarrolladores y educadores. 
            Cada contribución hace que la educación sea más accesible.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <motion.button
              className="px-8 py-4 bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-2xl font-bold shadow-xl hover:shadow-2xl transition-all duration-300 flex items-center justify-center space-x-2"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              <Rocket className="w-5 h-5" />
              <span>Empezar a Contribuir</span>
            </motion.button>
            
            <motion.button
              className="px-8 py-4 bg-white text-gray-900 rounded-2xl font-bold border-2 border-primary-600 hover:bg-primary-50 transition-all duration-300 flex items-center justify-center space-x-2"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              <Coffee className="w-5 h-5" />
              <span>Documentación</span>
            </motion.button>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default OpenSourceSection;