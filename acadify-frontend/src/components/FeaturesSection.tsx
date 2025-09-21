import React, { useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { 
  Gamepad2, 
  Trophy, 
  Users, 
  BookOpen, 
  Zap, 
  Heart,
  Target,
  Award,
  Sparkles,
  Brain,
  Rocket,
  Crown
} from 'lucide-react';
import type { FeatureItem } from '../types/landing';

const FeaturesSection: React.FC = () => {
  const [activeFeature, setActiveFeature] = useState(0);
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" });

  const features: FeatureItem[] = [
    {
      id: '1',
      title: 'Gamificación Completa',
      description: 'Sistema de puntos, niveles, logros y recompensas que mantiene a los estudiantes motivados y comprometidos 24/7.',
      icon: 'Gamepad2',
      color: 'from-purple-500 to-pink-500',
      delay: 0.1
    },
    {
      id: '2',
      title: 'Rutilio, tu Compañero',
      description: 'Una adorable mascota que evoluciona contigo, celebra tus logros y te motiva en cada paso del aprendizaje.',
      icon: 'Heart',
      color: 'from-green-500 to-teal-500',
      delay: 0.2
    },
    {
      id: '3',
      title: 'Logros y Medallas',
      description: 'Desbloquea insignias especiales, medallas de honor y reconocimientos por tu progreso académico excepcional.',
      icon: 'Trophy',
      color: 'from-yellow-500 to-orange-500',
      delay: 0.3
    },
    {
      id: '4',
      title: 'Aprendizaje Social',
      description: 'Compite sanamente con compañeros, forma equipos épicos y participa en desafíos colaborativos emocionantes.',
      icon: 'Users',
      color: 'from-blue-500 to-indigo-500',
      delay: 0.4
    },
    {
      id: '5',
      title: 'Contenido Interactivo',
      description: 'Lecciones dinámicas, quizzes gamificados y actividades inmersivas que transforman el estudio en diversión pura.',
      icon: 'BookOpen',
      color: 'from-red-500 to-pink-500',
      delay: 0.5
    },
    {
      id: '6',
      title: 'Progreso en Tiempo Real',
      description: 'Seguimiento instantáneo de tu evolución con analytics avanzados y insights personalizados para mejorar.',
      icon: 'Zap',
      color: 'from-purple-600 to-blue-600',
      delay: 0.6
    },
    {
      id: '7',
      title: 'Inteligencia Adaptativa',
      description: 'IA que adapta el contenido a tu ritmo de aprendizaje, identificando fortalezas y áreas de mejora.',
      icon: 'Brain',
      color: 'from-teal-500 to-green-600',
      delay: 0.7
    },
    {
      id: '8',
      title: 'Misiones Épicas',
      description: 'Embárcate en aventuras educativas con misiones temáticas que hacen del aprendizaje una experiencia épica.',
      icon: 'Rocket',
      color: 'from-orange-500 to-red-500',
      delay: 0.8
    }
  ];

  const getIcon = (iconName: string) => {
    const icons: { [key: string]: React.ComponentType<any> } = {
      Gamepad2, Trophy, Users, BookOpen, Zap, Heart, Target, Award, Sparkles, Brain, Rocket, Crown
    };
    return icons[iconName] || Gamepad2;
  };

  return (
    <section id="features" ref={sectionRef} className="py-20 lg:py-32 bg-gradient-to-br from-gray-50 to-white relative overflow-hidden">
      {/* Elementos de fondo decorativos */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute top-1/4 -left-20 w-80 h-80 bg-primary-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30"
          animate={{ 
            scale: [1, 1.2, 1],
            x: [0, 50, 0]
          }}
          transition={{ duration: 15, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-1/4 -right-20 w-96 h-96 bg-secondary-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30"
          animate={{ 
            scale: [1, 1.3, 1],
            x: [0, -30, 0]
          }}
          transition={{ duration: 18, repeat: Infinity, delay: 2 }}
        />
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
            className="inline-flex items-center space-x-2 bg-gradient-primary px-6 py-3 rounded-full text-white font-semibold mb-6"
          >
            <Sparkles className="w-5 h-5" />
            <span>Características Revolucionarias</span>
            <Crown className="w-5 h-5" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-4xl lg:text-6xl font-display font-bold text-gradient mb-6"
          >
            Experiencia de Aprendizaje
            <br />
            <span className="text-gray-800">Completamente Redefinida</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed"
          >
            Descubre un ecosistema educativo donde la{' '}
            <span className="font-semibold text-primary-600">tecnología</span>,{' '}
            <span className="font-semibold text-secondary-600">gamificación</span> y{' '}
            <span className="font-semibold text-accent-pink">diversión</span>{' '}
            se combinan para crear la experiencia de aprendizaje más emocionante del mundo.
          </motion.p>
        </motion.div>

        {/* Grid de características */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => {
            const IconComponent = getIcon(feature.icon);
            
            return (
              <motion.div
                key={feature.id}
                initial={{ opacity: 0, y: 50, scale: 0.9 }}
                animate={isInView ? { opacity: 1, y: 0, scale: 1 } : {}}
                transition={{ 
                  delay: feature.delay,
                  duration: 0.6,
                  ease: "backOut"
                }}
                className="group relative"
                onHoverStart={() => setActiveFeature(index)}
              >
                {/* Card */}
                <motion.div
                  className="relative p-8 bg-white rounded-3xl shadow-lg hover:shadow-2xl transition-all duration-500 border border-gray-100 overflow-hidden"
                  whileHover={{ 
                    y: -10,
                    scale: 1.02
                  }}
                  transition={{ duration: 0.3 }}
                >
                  {/* Gradiente de fondo animado */}
                  <motion.div
                    className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-5 transition-opacity duration-500`}
                  />

                  {/* Icono con efectos */}
                  <div className="relative mb-6">
                    {/* Anillo mágico - movido debajo del icono */}
                    <motion.div
                      className={`absolute inset-0 w-16 h-16 border-2 bg-gradient-to-r ${feature.color} rounded-2xl opacity-30`}
                      animate={activeFeature === index ? { 
                        scale: [1, 1.1, 1]
                      } : {}}
                      transition={{ duration: 2, repeat: Infinity }}
                      style={{ zIndex: 0 }}
                    />
                    
                    <div
                      className={`relative w-16 h-16 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow duration-300`}
                      style={{ zIndex: 1 }}
                    >
                      <IconComponent className="w-8 h-8 text-white" />
                    </div>
                  </div>

                  {/* Contenido */}
                  <motion.h3
                    className="text-xl font-bold text-gray-800 mb-4 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-primary-600 group-hover:to-secondary-600 transition-all duration-300"
                  >
                    {feature.title}
                  </motion.h3>

                  <motion.p
                    className="text-gray-600 leading-relaxed text-sm"
                  >
                    {feature.description}
                  </motion.p>

                  {/* Efectos de partículas en hover */}
                  <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <Sparkles className="w-5 h-5 text-primary-400" />
                  </div>

                  {/* Indicador de progreso */}
                  <motion.div
                    className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-primary-500 to-secondary-500 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500 origin-left"
                  />
                </motion.div>

                {/* Efectos externos en hover */}
                <motion.div
                  className={`absolute -inset-4 bg-gradient-to-r ${feature.color} rounded-3xl opacity-0 group-hover:opacity-10 transition-opacity duration-500 -z-10 blur-xl`}
                />
              </motion.div>
            );
          })}
        </div>

        {/* CTA Bottom */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 1, duration: 0.8 }}
          className="text-center mt-16"
        >
          <motion.div
            className="inline-flex items-center space-x-4"
            whileHover={{ scale: 1.05 }}
          >
            <motion.button
              className="px-8 py-4 bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-2xl font-bold shadow-xl hover:shadow-2xl transition-all duration-300 flex items-center space-x-2"
              whileHover={{ y: -3 }}
              whileTap={{ scale: 0.98 }}
            >
              <Rocket className="w-5 h-5" />
              <span>Explorar Todas las Características</span>
            </motion.button>

            <motion.button
              className="text-primary-600 text-sm font-medium hover:text-primary-700 transition-colors cursor-pointer"
              onClick={() => {
                const element = document.getElementById('gamification');
                element?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              ¡Y muchas más sorpresas! →
            </motion.button>
          </motion.div>
        </motion.div>
      </div>

      {/* Elemento decorativo flotante */}
      <motion.div
        className="absolute top-20 right-20 text-6xl opacity-10"
        animate={{ 
          rotate: 360,
          scale: [1, 1.2, 1]
        }}
        transition={{ 
          rotate: { duration: 20, repeat: Infinity, ease: "linear" },
          scale: { duration: 4, repeat: Infinity }
        }}
      >
        🚀
      </motion.div>

      <motion.div
        className="absolute bottom-20 left-20 text-5xl opacity-10"
        animate={{ 
          y: [0, -20, 0],
          rotate: [0, 10, -10, 0]
        }}
        transition={{ duration: 6, repeat: Infinity }}
      >
        ⭐
      </motion.div>
    </section>
  );
};

export default FeaturesSection;