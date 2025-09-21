import React, { useState, useRef, useEffect } from 'react';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import { 
  Trophy, 
  Star, 
  Crown, 
  Shield, 
  Target, 
  Zap,
  Award,
  Gem,
  Sword,
  Flame,
  Heart,
  Gift,
  Medal,
  Sparkles
} from 'lucide-react';
import type { Achievement } from '../types/landing';

const GamificationSection: React.FC = () => {
  const [selectedAchievement, setSelectedAchievement] = useState<number>(0);
  const [rutilioLevel, setRutilioLevel] = useState(1);
  const [experience, setExperience] = useState(150);
  const [showLevelUp, setShowLevelUp] = useState(false);
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" });

  const achievements: Achievement[] = [
    {
      id: '1',
      title: 'Primer Paso',
      description: 'Completa tu primera lección',
      icon: 'Star',
      unlocked: true,
      points: 50,
      rarity: 'common'
    },
    {
      id: '2',
      title: 'Racha de Fuego',
      description: 'Mantén una racha de 7 días',
      icon: 'Flame',
      unlocked: true,
      points: 200,
      rarity: 'rare'
    },
    {
      id: '3',
      title: 'Maestro del Saber',
      description: 'Alcanza 95% en 10 evaluaciones',
      icon: 'Crown',
      unlocked: true,
      points: 500,
      rarity: 'epic'
    },
    {
      id: '4',
      title: 'Leyenda Académica',
      description: 'Completa 50 cursos perfectos',
      icon: 'Sword',
      unlocked: false,
      points: 1000,
      rarity: 'legendary'
    },
    {
      id: '5',
      title: 'Colaborador Estrella',
      description: 'Ayuda a 20 compañeros',
      icon: 'Heart',
      unlocked: true,
      points: 300,
      rarity: 'rare'
    },
    {
      id: '6',
      title: 'Explorador Curioso',
      description: 'Descubre 15 temas nuevos',
      icon: 'Target',
      unlocked: false,
      points: 150,
      rarity: 'common'
    }
  ];

  const rarityColors = {
    common: 'from-gray-400 to-gray-600',
    rare: 'from-blue-400 to-blue-600',
    epic: 'from-purple-400 to-purple-600',
    legendary: 'from-primary-500 to-secondary-500'
  };

  const getIcon = (iconName: string) => {
    const icons: { [key: string]: React.ComponentType<any> } = {
      Trophy, Star, Crown, Shield, Target, Zap, Award, Gem, Sword, Flame, Heart, Gift, Medal, Sparkles
    };
    return icons[iconName] || Star;
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setExperience(prev => {
        const newExp = prev + Math.floor(Math.random() * 20) + 5;
        if (newExp >= 1000 && rutilioLevel < 5) {
          setRutilioLevel(level => level + 1);
          setShowLevelUp(true);
          setTimeout(() => setShowLevelUp(false), 3000);
          return newExp - 1000;
        }
        return newExp;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [rutilioLevel]);

  const rutilioEmojis = ['�', '😸', '�', '😊', '👑'];
  const progressPercentage = (experience / 1000) * 100;

  return (
    <section id="gamification" ref={sectionRef} className="py-20 lg:py-32 bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-900 relative overflow-hidden">
      {/* Fondo estrellado animado */}
      <div className="absolute inset-0">
        {[...Array(50)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0, 1, 0],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 2 + Math.random() * 3,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
        
        {/* Nebulosas de color */}
        <motion.div
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
          animate={{ 
            scale: [1, 1.3, 1],
            rotate: [0, 180, 360]
          }}
          transition={{ duration: 20, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-green-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
          animate={{ 
            scale: [1, 1.2, 1],
            x: [0, 50, 0]
          }}
          transition={{ duration: 15, repeat: Infinity, delay: 2 }}
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
            className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-600 to-secondary-600 px-6 py-3 rounded-full text-white font-bold mb-6"
          >
            <Trophy className="w-5 h-5" />
            <span>Sistema de Gamificación</span>
            <Crown className="w-5 h-5" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-4xl lg:text-6xl font-display font-bold text-white mb-6"
          >
            Conviértete en un
            <br />
            <span className="text-secondary-300">
              Héroe del Aprendizaje
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed"
          >
            Cada lección es una aventura, cada logro una victoria épica. 
            Junto a Rutilio, descubre un mundo donde aprender se convierte en la experiencia más emocionante de tu vida.
          </motion.p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Rutilio y Progreso */}
          <motion.div
            initial={{ opacity: 0, x: -100 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 1 }}
            className="relative"
          >
            {/* Rutilio Container */}
            <motion.div
              className="relative flex flex-col items-center"
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 4, repeat: Infinity }}
            >
              {/* Level Badge */}
              <motion.div
                className="absolute -top-4 -right-4 z-20 bg-gradient-to-r from-primary-500 to-secondary-500 px-4 py-2 rounded-full shadow-xl"
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <span className="text-white font-bold text-sm">Nivel {rutilioLevel}</span>
              </motion.div>

              {/* Anillo de experiencia */}
              <motion.div className="relative w-80 h-80">
                <svg className="absolute inset-0 w-full h-full -rotate-90">
                  <circle
                    cx="160"
                    cy="160"
                    r="140"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="8"
                    fill="none"
                  />
                  <motion.circle
                    cx="160"
                    cy="160"
                    r="140"
                    stroke="url(#experienceGradient)"
                    strokeWidth="8"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={`${2 * Math.PI * 140}`}
                    strokeDashoffset={`${2 * Math.PI * 140 * (1 - progressPercentage / 100)}`}
                    className="drop-shadow-lg"
                  />
                  <defs>
                    <linearGradient id="experienceGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#10b981" />
                      <stop offset="50%" stopColor="#8b5cf6" />
                      <stop offset="100%" stopColor="#f59e0b" />
                    </linearGradient>
                  </defs>
                </svg>

                {/* Rutilio */}
                <motion.div
                  className="absolute inset-8 bg-gradient-to-br from-primary-400 via-primary-300 to-secondary-400 rounded-full flex items-center justify-center shadow-2xl"
                  whileHover={{ scale: 1.05 }}
                  animate={{ 
                    boxShadow: [
                      "0 0 0 0 rgba(139, 92, 246, 0.7)",
                      "0 0 0 20px rgba(139, 92, 246, 0)",
                      "0 0 0 0 rgba(139, 92, 246, 0)"
                    ]
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <motion.div
                    className="text-8xl"
                    animate={{ 
                      scale: [1, 1.1, 1],
                      rotate: [0, 5, -5, 0]
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                  >
                    {rutilioEmojis[rutilioLevel - 1]}
                  </motion.div>
                </motion.div>

                {/* Partículas mágicas */}
                {[...Array(8)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-3 h-3 bg-primary-400 rounded-full"
                    style={{
                      left: `${50 + 45 * Math.cos((i * 45 * Math.PI) / 180)}%`,
                      top: `${50 + 45 * Math.sin((i * 45 * Math.PI) / 180)}%`,
                      transform: 'translate(-50%, -50%)',
                    }}
                    animate={{
                      scale: [0, 1, 0],
                      opacity: [0, 1, 0],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      delay: i * 0.2,
                    }}
                  />
                ))}
              </motion.div>

              {/* Experience Bar */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.8 }}
                className="mt-8 text-center"
              >
                <div className="text-white font-semibold mb-2">
                  {experience}/1000 XP
                </div>
                <div className="w-64 h-3 bg-white/20 rounded-full overflow-hidden mx-auto">
                  <motion.div
                    className="h-full bg-gradient-to-r from-green-400 to-blue-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${progressPercentage}%` }}
                    transition={{ duration: 1, delay: 1 }}
                  />
                </div>
                <div className="text-gray-300 text-sm mt-2">
                  ¡Sigue así para subir de nivel!
                </div>
              </motion.div>

              {/* Level Up Animation */}
              <AnimatePresence>
                {showLevelUp && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0, y: 50 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0, y: -50 }}
                    className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-30"
                  >
                    <div className="bg-gradient-to-r from-primary-500 to-secondary-500 px-6 py-4 rounded-2xl shadow-2xl text-white font-bold text-xl">
                      🎉 ¡NIVEL {rutilioLevel}! 🎉
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </motion.div>

          {/* Logros y Achievements */}
          <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 1, delay: 0.3 }}
            className="space-y-6"
          >
            <motion.h3
              className="text-3xl font-bold text-white mb-8 flex items-center space-x-3"
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.5 }}
            >
              <Trophy className="w-8 h-8 text-primary-400" />
              <span>Tus Logros Épicos</span>
            </motion.h3>

            <div className="space-y-4">
              {achievements.map((achievement, index) => {
                const IconComponent = getIcon(achievement.icon);
                
                return (
                  <motion.div
                    key={achievement.id}
                    initial={{ opacity: 0, x: 50 }}
                    animate={isInView ? { opacity: 1, x: 0 } : {}}
                    transition={{ delay: 0.6 + index * 0.1, duration: 0.6 }}
                    className={`group p-4 rounded-2xl border-2 transition-all duration-300 cursor-pointer ${
                      achievement.unlocked 
                        ? 'bg-white/10 border-white/20 hover:bg-white/20' 
                        : 'bg-gray-900/50 border-gray-700'
                    }`}
                    whileHover={{ scale: 1.02, y: -2 }}
                    onClick={() => setSelectedAchievement(index)}
                  >
                    <div className="flex items-center space-x-4">
                      {/* Icono del logro */}
                      <motion.div
                        className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                          achievement.unlocked 
                            ? `bg-gradient-to-br ${rarityColors[achievement.rarity]} shadow-lg` 
                            : 'bg-gray-700'
                        }`}
                        animate={achievement.unlocked ? {
                          boxShadow: [
                            "0 0 0 0 rgba(255, 255, 255, 0.7)",
                            "0 0 0 10px rgba(255, 255, 255, 0)",
                            "0 0 0 0 rgba(255, 255, 255, 0)"
                          ]
                        } : {}}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        <IconComponent className={`w-6 h-6 ${achievement.unlocked ? 'text-white' : 'text-gray-500'}`} />
                      </motion.div>

                      {/* Información */}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <h4 className={`font-bold ${achievement.unlocked ? 'text-white' : 'text-gray-500'}`}>
                            {achievement.title}
                          </h4>
                          <motion.div
                            className={`px-2 py-1 rounded-full text-xs font-bold ${
                              achievement.rarity === 'legendary' ? 'bg-yellow-500 text-black' :
                              achievement.rarity === 'epic' ? 'bg-purple-500 text-white' :
                              achievement.rarity === 'rare' ? 'bg-blue-500 text-white' :
                              'bg-gray-500 text-white'
                            }`}
                            animate={achievement.rarity === 'legendary' ? {
                              scale: [1, 1.1, 1],
                              boxShadow: [
                                "0 0 0 0 rgba(255, 215, 0, 0.7)",
                                "0 0 0 10px rgba(255, 215, 0, 0)",
                                "0 0 0 0 rgba(255, 215, 0, 0)"
                              ]
                            } : {}}
                            transition={{ duration: 2, repeat: Infinity }}
                          >
                            {achievement.rarity.toUpperCase()}
                          </motion.div>
                        </div>
                        <p className={`text-sm ${achievement.unlocked ? 'text-gray-300' : 'text-gray-600'}`}>
                          {achievement.description}
                        </p>
                        <div className={`text-xs font-bold mt-1 ${achievement.unlocked ? 'text-primary-400' : 'text-gray-600'}`}>
                          +{achievement.points} XP
                        </div>
                      </div>

                      {/* Estado */}
                      <motion.div
                        animate={achievement.unlocked ? { rotate: 360 } : {}}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        {achievement.unlocked ? (
                          <div className="text-green-400 text-2xl flex items-center justify-center">
                            <Trophy className="w-6 h-6" />
                          </div>
                        ) : (
                          <div className="text-gray-600 text-2xl flex items-center justify-center">
                            <Target className="w-6 h-6" />
                          </div>
                        )}
                      </motion.div>
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {/* CTA */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 1.2 }}
              className="mt-8"
            >
              <motion.button
                className="w-full py-4 bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-2xl font-bold shadow-xl hover:shadow-2xl transition-all duration-300 flex items-center justify-center space-x-2"
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <Sparkles className="w-5 h-5" />
                <span>¡Empezar mi Aventura Épica!</span>
                <Crown className="w-5 h-5" />
              </motion.button>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default GamificationSection;