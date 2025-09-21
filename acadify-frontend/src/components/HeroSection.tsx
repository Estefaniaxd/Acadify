import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Star, 
  Users, 
  BookOpen, 
  Trophy, 
  Zap, 
  Heart,
  Target,
  ArrowRight,
  Sparkles
} from 'lucide-react';

const HeroSection: React.FC = () => {
  const [rutilioEmotion, setRutilioEmotion] = useState<'happy' | 'excited' | 'winking'>('happy');

  useEffect(() => {
    // Cambiar emoción de Rutilio cada 3 segundos
    const emotionInterval = setInterval(() => {
      const emotions: ('happy' | 'excited' | 'winking')[] = ['happy', 'excited', 'winking'];
      setRutilioEmotion(emotions[Math.floor(Math.random() * emotions.length)]);
    }, 3000);

    return () => clearInterval(emotionInterval);
  }, []);

  const stats = [
    { icon: Users, value: '50,000+', label: 'Estudiantes Felices', color: 'text-primary-500' },
    { icon: BookOpen, value: '1,200+', label: 'Lecciones Interactivas', color: 'text-secondary-500' },
    { icon: Trophy, value: '100,000+', label: 'Logros Desbloqueados', color: 'text-accent-yellow' },
    { icon: Target, value: '98%', label: 'Tasa de Éxito', color: 'text-accent-pink' }
  ];

  const getRutilioImage = () => {
    const images = {
      happy: '/src/assets/rutilio/rutilio-happy.png',
      excited: '/src/assets/rutilio/rutilio-excited.png', 
      winking: '/src/assets/rutilio/rutilio-winking.png'
    };
    return images[rutilioEmotion];
  };

  return (
        <section id="home" className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 relative overflow-hidden flex items-center">
      {/* Background Effects */}
      <div className="absolute inset-0">
        {/* Animated Gradient Orbs */}
        <motion.div
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-full mix-blend-multiply filter blur-3xl opacity-30"
          animate={{ 
            scale: [1, 1.2, 1],
            x: [0, 100, 0],
            y: [0, -50, 0]
          }}
          transition={{ duration: 20, repeat: Infinity }}
        />
        <motion.div
          className="absolute top-1/3 right-1/4 w-96 h-96 bg-secondary-200 rounded-full mix-blend-multiply filter blur-xl opacity-70"
          animate={{ 
            scale: [1, 1.3, 1],
            x: [0, -30, 0],
            y: [0, 40, 0]
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        />
        <motion.div
          className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-accent-pink/30 rounded-full mix-blend-multiply filter blur-xl opacity-70"
          animate={{ 
            scale: [1, 1.1, 1],
            rotate: [0, 180, 360]
          }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut", delay: 2 }}
        />

      </div>

      <div className="container mx-auto px-6 py-20 relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Contenido izquierdo */}
          <motion.div
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="text-center lg:text-left"
          >
            {/* Badge superior */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.8 }}
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-100 to-secondary-100 px-6 py-3 rounded-full mb-8 border border-primary-200"
            >
              <motion.div
                animate={{ rotate: [0, 20, -20, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Star className="w-5 h-5 text-accent-yellow" />
              </motion.div>
              <span className="text-sm font-semibold text-gray-700">
                #1 Plataforma Educativa Gamificada en Colombia
              </span>
              <Sparkles className="w-4 h-4 text-primary-500" />
            </motion.div>

            {/* Título principal */}
            <motion.h1
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
              className="text-5xl lg:text-7xl font-display font-bold mb-8 leading-tight text-gray-900"
            >
              Aprende con{' '}
              <motion.span
                className="text-gradient inline-block"
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                Rutilio
              </motion.span>
              <br />
              y convierte la{' '}
              <motion.span
                className="relative inline-block"
                whileHover={{ scale: 1.05 }}
              >
                <span className="text-gradient">educación</span>
                <motion.div
                  className="absolute -bottom-2 left-0 right-0 h-2 bg-gradient-secondary opacity-30 rounded-full"
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ delay: 1, duration: 0.8 }}
                />
              </motion.span>
              <br />
              en una{' '}
              <motion.span
                className="text-gradient"
                animate={{ textShadow: ["0 0 0px #8b5cf6", "0 0 20px #8b5cf6", "0 0 0px #8b5cf6"] }}
                transition={{ duration: 3, repeat: Infinity }}
              >
                aventura
              </motion.span>
            </motion.h1>

            {/* Subtítulo */}
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
              className="text-xl lg:text-2xl text-gray-600 mb-10 leading-relaxed max-w-2xl"
            >
              Descubre una forma{' '}
              <span className="font-semibold text-primary-600">revolucionaria</span>{' '}
              de aprender donde cada logro cuenta, cada desafío emociona y cada estudiante 
              se convierte en el{' '}
              <span className="font-semibold text-secondary-600">héroe</span>{' '}
              de su propia historia educativa.
            </motion.p>

            {/* Estadísticas */}
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.8 }}
              className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-10"
            >
              {stats.map((stat, index) => (
                <motion.div
                  key={index}
                  className="text-center"
                  whileHover={{ scale: 1.05, y: -5 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1 + index * 0.1 }}
                >
                  <div className="flex items-center justify-center mb-3">
                    <div className={`p-3 rounded-full bg-gradient-to-r from-gray-100 to-gray-50 shadow-lg ${stat.color}`}>
                      <stat.icon className="w-6 h-6" />
                    </div>
                  </div>
                  <div className="text-2xl lg:text-3xl font-bold text-gray-800 mb-1">
                    {stat.value}
                  </div>
                  <div className="text-sm text-gray-600 font-medium">{stat.label}</div>
                </motion.div>
              ))}
            </motion.div>

            {/* Botones CTA */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2, duration: 0.8 }}
              className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
            >
              <motion.button
                className="group px-8 py-4 bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-2xl font-bold shadow-2xl hover:shadow-3xl transition-all duration-300 flex items-center justify-center space-x-2"
                whileHover={{ scale: 1.05, y: -3 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  const element = document.getElementById('features');
                  element?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                <Zap className="w-5 h-5" />
                <span>¡Comenzar mi Aventura!</span>
                <ArrowRight className="w-5 h-5" />
              </motion.button>
              
              <motion.button
                className="group px-8 py-4 border-2 border-primary-300 text-primary-600 bg-white rounded-2xl font-bold hover:bg-primary-50 transition-all duration-300 flex items-center justify-center space-x-2"
                whileHover={{ scale: 1.05, y: -3 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  window.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ', '_blank');
                }}
              >
                <Play className="w-5 h-5" />
                <span>Ver Demo Interactiva</span>
              </motion.button>
            </motion.div>
          </motion.div>

          {/* Contenido derecho - Rutilio Showcase */}
          <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, delay: 0.3, ease: "easeOut" }}
            className="relative flex justify-center"
          >
            {/* Rutilio principal */}
            <div className="relative">
              {/* Rutilio */}
              <div className="relative w-80 h-80 bg-gradient-to-br from-primary-400 via-primary-300 to-secondary-400 rounded-full flex items-center justify-center mx-auto shadow-2xl">
                <div className="w-64 h-64 rounded-full overflow-hidden bg-white/10 flex items-center justify-center">
                  <img 
                    src="/rutilio-cat.svg" 
                    alt="Rutilio el gato mascota" 
                    className="w-32 h-32 object-contain"
                  />
                </div>
              </div>

              {/* Elementos flotantes alrededor de Rutilio */}
              <div className="absolute -top-6 -right-6 bg-accent-yellow p-4 rounded-2xl shadow-xl">
                <Trophy className="w-8 h-8 text-white" />
              </div>
              
              <div className="absolute -bottom-6 -left-6 bg-accent-pink p-4 rounded-2xl shadow-xl">
                <Heart className="w-8 h-8 text-white" />
              </div>
              
              <div className="absolute top-1/2 -left-12 bg-accent-blue p-4 rounded-2xl shadow-xl">
                <BookOpen className="w-8 h-8 text-white" />
              </div>

              <div className="absolute top-1/2 -right-12 bg-secondary-500 p-4 rounded-2xl shadow-xl">
                <Target className="w-8 h-8 text-white" />
              </div>
            </div>

            {/* Notificaciones flotantes */}
            <div className="absolute top-16 right-8 bg-white p-4 rounded-2xl shadow-xl border border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-secondary-500 rounded-full animate-pulse" />
                <span className="text-sm font-semibold text-gray-700">+150 XP</span>
                <Star className="w-4 h-4 text-accent-yellow" />
              </div>
            </div>

            <div className="absolute bottom-16 left-8 bg-white p-4 rounded-2xl shadow-xl border border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-primary-500 rounded-full animate-pulse" />
                <Trophy className="w-5 h-5 text-accent-yellow" />
                <span className="text-sm font-semibold text-gray-700">¡Nuevo Logro!</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Indicador de scroll */}
      <motion.div
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2 text-gray-400"
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="flex flex-col items-center space-y-2">
          <span className="text-sm font-medium text-gray-600">Descubre más</span>
          <div className="w-6 h-10 border-2 border-gray-300 rounded-full flex justify-center">
            <motion.div
              className="w-1 h-3 bg-primary-500 rounded-full mt-2"
              animate={{ y: [0, 12, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </div>
        </div>
      </motion.div>
    </section>
  );
};

export default HeroSection;