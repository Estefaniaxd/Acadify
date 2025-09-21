import React, { useState, useRef, useEffect } from 'react';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import { Star, Quote, ChevronLeft, ChevronRight, Play, Heart, Award, GraduationCap, TrendingUp } from 'lucide-react';

interface Testimonial {
  id: string;
  name: string;
  role: string;
  institution: string;
  avatar: string;
  rating: number;
  text: string;
  achievement: string;
  videoUrl?: string;
  beforeGrade: number;
  afterGrade: number;
}

const TestimonialsSection: React.FC = () => {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" });

  const testimonials: Testimonial[] = [
    {
      id: '1',
      name: 'María García',
      role: 'Estudiante de Medicina',
      institution: 'Universidad Nacional',
      avatar: '👩‍⚕️',
      rating: 5,
      text: 'Antes de Acadify, las matemáticas eran mi pesadilla. Ahora son mi materia favorita. Rutilio me ayudó a entender conceptos que creía imposibles. ¡Mi nota subió de 6.2 a 9.4!',
      achievement: 'Maestro de las Matemáticas',
      beforeGrade: 6.2,
      afterGrade: 9.4
    },
    {
      id: '2',
      name: 'Carlos Rodríguez',
      role: 'Estudiante de Ingeniería',
      institution: 'TEC Costa Rica',
      avatar: '👨‍💻',
      rating: 5,
      text: 'La gamificación cambió completamente mi perspectiva sobre estudiar. Cada día espero con ansias mis "misiones" de aprendizaje. Es adictivo de la mejor manera.',
      achievement: 'Estudiante Excepcional',
      beforeGrade: 7.1,
      afterGrade: 9.7
    },
    {
      id: '3',
      name: 'Ana Sofía Luna',
      role: 'Estudiante de Psicología',
      institution: 'Universidad de Costa Rica',
      avatar: '👩‍🎓',
      rating: 5,
      text: 'Como estudiante con TDAH, siempre me costó mantener la concentración. Las técnicas interactivas de Acadify me han ayudado enormemente. Rutilio es el mejor compañero de estudio.',
      achievement: 'Concentración Zen',
      beforeGrade: 5.8,
      afterGrade: 8.9
    },
    {
      id: '4',
      name: 'Diego Fernández',
      role: 'Estudiante de Administración',
      institution: 'UNED',
      avatar: '👨‍💼',
      rating: 5,
      text: 'Estudiar a distancia era un reto enorme. Acadify me dio la estructura y motivación que necesitaba. Los recordatorios de Rutilio son perfectos, y las recompensas me mantienen motivado.',
      achievement: 'Estudiante Autodidacta',
      beforeGrade: 6.7,
      afterGrade: 9.2
    },
    {
      id: '5',
      name: 'Valeria Jiménez',
      role: 'Estudiante de Diseño',
      institution: 'Universidad Veritas',
      avatar: '👩‍🎨',
      rating: 5,
      text: 'La visualización de mi progreso es increíble. Ver cómo crezco día a día me llena de orgullo. Rutilio celebra cada pequeño logro conmigo. ¡Es como tener un coach personal!',
      achievement: 'Artista del Progreso',
      beforeGrade: 7.3,
      afterGrade: 9.6
    }
  ];

  useEffect(() => {
    if (!isAutoPlaying) return;

    const interval = setInterval(() => {
      setCurrentTestimonial(prev => (prev + 1) % testimonials.length);
    }, 6000);

    return () => clearInterval(interval);
  }, [isAutoPlaying, testimonials.length]);

  const nextTestimonial = () => {
    setCurrentTestimonial(prev => (prev + 1) % testimonials.length);
    setIsAutoPlaying(false);
  };

  const prevTestimonial = () => {
    setCurrentTestimonial(prev => (prev - 1 + testimonials.length) % testimonials.length);
    setIsAutoPlaying(false);
  };

  const current = testimonials[currentTestimonial];
  const improvement = ((current.afterGrade - current.beforeGrade) / current.beforeGrade * 100).toFixed(1);

  return (
    <section id="testimonials" ref={sectionRef} className="py-20 lg:py-32 bg-gradient-to-br from-white via-primary-50 to-secondary-50 relative overflow-hidden">
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0">
        {/* Formas flotantes */}
        <motion.div
          className="absolute top-20 left-10 w-20 h-20 bg-gradient-to-r from-primary-200 to-secondary-200 rounded-full blur-xl opacity-40"
          animate={{ 
            y: [0, -20, 0]
          }}
          transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-32 right-16 w-32 h-32 bg-gradient-to-r from-secondary-200 to-primary-200 rounded-full blur-xl opacity-40"
          animate={{ 
            y: [0, 20, 0]
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        />
        
        {/* Estrellas flotantes sutiles */}
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute text-primary-300 text-sm opacity-30"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -10, 0],
              opacity: [0.2, 0.4, 0.2],
            }}
            transition={{
              duration: 6 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
              ease: "easeInOut"
            }}
          >
            ⭐
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
            <span>Historias de Éxito</span>
            <Star className="w-5 h-5" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-4xl lg:text-6xl font-display font-bold text-gray-900 mb-6"
          >
            Transformaciones
            <br />
            <span className="text-primary-600">
              Extraordinarias
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed"
          >
            Conoce las increíbles historias de estudiantes que transformaron su vida académica con Acadify.
            Cada testimonio es una prueba del poder del aprendizaje gamificado.
          </motion.p>
        </motion.div>

        {/* Main Testimonial Card */}
        <motion.div
          initial={{ opacity: 0, y: 100 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1, delay: 0.5 }}
          className="max-w-5xl mx-auto"
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={currentTestimonial}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.4 }}
              className="bg-gradient-to-br from-white via-primary-50/50 to-secondary-50/50 backdrop-blur-xl rounded-3xl shadow-xl p-8 lg:p-12 border border-primary-200/50 relative overflow-hidden"
            >
              {/* Elementos decorativos de fondo */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-primary-200/30 to-transparent rounded-bl-3xl"></div>
              <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-secondary-200/30 to-transparent rounded-tr-3xl"></div>

              <div className="relative z-10">
                {/* Quote Icon más elegante */}
                <motion.div
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3, type: "spring" }}
                  className="flex justify-center mb-6"
                >
                  <div className="w-12 h-12 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <Quote className="w-6 h-6 text-white" />
                  </div>
                </motion.div>

                <div className="grid lg:grid-cols-3 gap-8 items-center">
                {/* Avatar y Info */}
                <motion.div
                  className="text-center lg:text-left"
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  {/* Avatar mejorado */}
                  <motion.div
                    className="relative mx-auto lg:mx-0 mb-6"
                    whileHover={{ scale: 1.05 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="w-24 h-24 bg-gradient-to-br from-primary-500 via-primary-400 to-secondary-500 rounded-2xl flex items-center justify-center text-4xl shadow-xl border-4 border-white">
                      {current.avatar}
                    </div>
                    {/* Indicador de verificación */}
                    <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center border-2 border-white">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </motion.div>

                  {/* Info Personal */}
                  <h3 className="text-xl font-bold text-gray-900 mb-1">{current.name}</h3>
                  <p className="text-primary-600 font-semibold mb-1">{current.role}</p>
                  <p className="text-gray-600 text-sm mb-4">{current.institution}</p>

                  {/* Rating */}
                  <motion.div 
                    className="flex justify-center lg:justify-start space-x-1 mb-4"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6 }}
                  >
                    {[...Array(5)].map((_, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 + i * 0.1 }}
                      >
                        <Star 
                          className={`w-5 h-5 ${
                            i < current.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                          }`} 
                        />
                      </motion.div>
                    ))}
                  </motion.div>

                  {/* Achievement Badge */}
                  <motion.div
                    className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-500 to-secondary-500 px-3 py-2 rounded-full text-white text-sm font-bold"
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.4, duration: 0.3 }}
                  >
                    <Award className="w-4 h-4" />
                    <span>{current.achievement}</span>
                  </motion.div>
                </motion.div>

                {/* Testimonio */}
                <motion.div
                  className="lg:col-span-2"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <blockquote className="text-lg lg:text-xl text-gray-700 leading-relaxed mb-6 italic">
                    "{current.text}"
                  </blockquote>

                  {/* Progreso Académico */}
                  <motion.div
                    className="bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl p-6 border border-green-200"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7 }}
                  >
                    <h4 className="text-center text-gray-700 font-semibold mb-4">
                      📈 Transformación Académica
                    </h4>
                    
                    <div className="flex items-center justify-between mb-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600 mb-1">
                          {current.beforeGrade.toFixed(1)}
                        </div>
                        <div className="text-sm text-gray-600">Antes</div>
                      </div>

                      <motion.div
                        className="flex-1 mx-6"
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: 1 }}
                        transition={{ delay: 0.9, duration: 1 }}
                      >
                        <div className="relative">
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <motion.div
                              className="h-full bg-gradient-to-r from-red-400 via-yellow-400 to-green-400 rounded-full"
                              initial={{ width: `${(current.beforeGrade / 10) * 100}%` }}
                              animate={{ width: `${(current.afterGrade / 10) * 100}%` }}
                              transition={{ delay: 1, duration: 1.5 }}
                            />
                          </div>
                          <motion.div
                            className="absolute -top-8 right-0 bg-green-500 text-white px-2 py-1 rounded-lg text-sm font-bold"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 1.5 }}
                          >
                            +{improvement}%
                          </motion.div>
                        </div>
                      </motion.div>

                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600 mb-1">
                          {current.afterGrade.toFixed(1)}
                        </div>
                        <div className="text-sm text-gray-600">Después</div>
                      </div>
                    </div>

                    <div className="text-center text-green-600 font-semibold">
                      ¡Mejora del {improvement}% en sus calificaciones!
                    </div>
                  </motion.div>
                </motion.div>
              </div>
              </div> {/* Cierre del div relativo */}
            </motion.div>
          </AnimatePresence>

          {/* Navigation Controls */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 1 }}
            className="flex items-center justify-center space-x-6 mt-8"
          >
            <motion.button
              onClick={prevTestimonial}
              className="p-3 bg-white/80 backdrop-blur-xl rounded-full shadow-lg hover:shadow-xl transition-all duration-300 border border-white/20"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <ChevronLeft className="w-6 h-6 text-gray-700" />
            </motion.button>

            {/* Dots Indicator */}
            <div className="flex space-x-2">
              {testimonials.map((_, index) => (
                <motion.button
                  key={index}
                  onClick={() => {
                    setCurrentTestimonial(index);
                    setIsAutoPlaying(false);
                  }}
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${
                    index === currentTestimonial
                      ? 'bg-primary-600 scale-125'
                      : 'bg-gray-300 hover:bg-gray-400'
                  }`}
                  whileHover={{ scale: 1.2 }}
                  whileTap={{ scale: 0.8 }}
                />
              ))}
            </div>

            <motion.button
              onClick={nextTestimonial}
              className="p-3 bg-white/80 backdrop-blur-xl rounded-full shadow-lg hover:shadow-xl transition-all duration-300 border border-white/20"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <ChevronRight className="w-6 h-6 text-gray-700" />
            </motion.button>
          </motion.div>

          {/* Autoplay Toggle */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            transition={{ delay: 1.2 }}
            className="text-center mt-6"
          >
            <motion.button
              onClick={() => setIsAutoPlaying(!isAutoPlaying)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 ${
                isAutoPlaying
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isAutoPlaying ? (
                <span className="flex items-center space-x-2">
                  <Play className="w-4 h-4" />
                  <span>Reproducción automática activa</span>
                </span>
              ) : (
                <span>Activar reproducción automática</span>
              )}
            </motion.button>
          </motion.div>
        </motion.div>

        {/* Statistics Summary */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 1.3 }}
          className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
        >
          {[
            { number: '10,000+', label: 'Estudiantes Transformados', icon: GraduationCap },
            { number: '8.7/10', label: 'Promedio de Mejora', icon: TrendingUp },
            { number: '95%', label: 'Satisfacción Garantizada', icon: Star }
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 1.4 + index * 0.1 }}
              className="text-center p-6 bg-white/60 backdrop-blur-xl rounded-2xl border border-white/20"
              whileHover={{ scale: 1.05, y: -5 }}
            >
              <div className="flex justify-center mb-3">
                <stat.icon className="w-10 h-10 text-primary-600" />
              </div>
              <div className="text-3xl font-bold text-primary-600 mb-2">{stat.number}</div>
              <div className="text-gray-700 font-semibold">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default TestimonialsSection;