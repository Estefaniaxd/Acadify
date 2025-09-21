import React, { useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { 
  Rocket, 
  Crown, 
  Gift, 
  Star, 
  ArrowRight, 
  CheckCircle, 
  Sparkles,
  Zap,
  Trophy,
  Timer,
  Users,
  Shield
} from 'lucide-react';

const CTASection: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const sectionRef = useRef(null);
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsLoading(true);
    
    // Simular envío
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsLoading(false);
    setIsSubmitted(true);
  };

  const benefits = [
    'Acceso completo a todos los cursos',
    'Rutilio como compañero personal',
    'Sistema de logros y recompensas',
    'Seguimiento detallado del progreso',
    'Comunidad de estudiantes élite',
    'Soporte prioritario 24/7'
  ];

  const features = [
    { icon: Crown, title: 'Premium por 7 días', description: 'Gratis' },
    { icon: Gift, title: 'Logros exclusivos', description: 'Desbloqueados' },
    { icon: Zap, title: 'Boost de XP x2', description: 'Activado' },
    { icon: Shield, title: 'Garantía', description: '30 días' }
  ];

  return (
    <section id="cta" ref={sectionRef} className="py-20 lg:py-32 bg-gradient-to-br from-primary-900 via-purple-900 to-secondary-900 relative overflow-hidden">
      {/* Fondo dinámico */}
      <div className="absolute inset-0">
        {/* Gradient Orbs */}
        <motion.div
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mix-blend-multiply filter blur-3xl opacity-30"
          animate={{ 
            scale: [1, 1.2, 1],
            x: [0, 100, 0],
            y: [0, -50, 0]
          }}
          transition={{ duration: 20, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-gradient-to-r from-pink-500 to-yellow-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30"
          animate={{ 
            scale: [1, 1.3, 1],
            x: [0, -80, 0],
            y: [0, 60, 0]
          }}
          transition={{ duration: 25, repeat: Infinity, delay: 5 }}
        />

        {/* Floating Elements */}
        {[...Array(30)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -100, 0],
              opacity: [0, 1, 0],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 3 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 5,
            }}
          />
        ))}

        {/* Lightning Effects */}
        <motion.div
          className="absolute top-10 right-20 text-yellow-400 text-2xl"
          animate={{ 
            rotate: [0, 15, -15, 0],
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          ⚡
        </motion.div>
        <motion.div
          className="absolute bottom-20 left-16 text-yellow-400 text-xl"
          animate={{ 
            rotate: [0, -20, 20, 0],
            scale: [1, 1.3, 1],
            opacity: [0.4, 1, 0.4]
          }}
          transition={{ duration: 2.5, repeat: Infinity, delay: 1 }}
        >
          ⚡
        </motion.div>
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
            <Timer className="w-5 h-5" />
            <span>¡100% Gratuito y Open Source!</span>
            <Sparkles className="w-5 h-5" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-4xl lg:text-7xl font-display font-bold text-white mb-6"
          >
            ¿Listo para
            <br />
            <span className="text-primary-300">
              Transformar tu Vida?
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-xl lg:text-2xl text-gray-300 max-w-4xl mx-auto leading-relaxed mb-8"
          >
            Únete a miles de estudiantes que ya están viviendo la revolución del aprendizaje.
            <br />
            <strong className="text-primary-400">¡Tu aventura académica épica comienza hoy!</strong>
          </motion.p>

          {/* Countdown Timer */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="flex justify-center items-center space-x-4 mb-8"
          >
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl px-6 py-4 border border-white/20">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-400">72</div>
                <div className="text-sm text-gray-300">Horas</div>
              </div>
            </div>
            <div className="text-white text-2xl">:</div>
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl px-6 py-4 border border-white/20">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-400">15</div>
                <div className="text-sm text-gray-300">Minutos</div>
              </div>
            </div>
            <div className="text-white text-2xl">:</div>
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl px-6 py-4 border border-white/20">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-400">30</div>
                <div className="text-sm text-gray-300">Segundos</div>
              </div>
            </div>
          </motion.div>
        </motion.div>

        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Side - Benefits & Features */}
            <motion.div
              initial={{ opacity: 0, x: -100 }}
              animate={isInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 1 }}
              className="space-y-8"
            >
              {/* Premium Features Grid */}
              <div className="grid grid-cols-2 gap-4">
                {features.map((feature, index) => {
                  const IconComponent = feature.icon;
                  
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 30 }}
                      animate={isInView ? { opacity: 1, y: 0 } : {}}
                      transition={{ delay: 0.6 + index * 0.1, duration: 0.6 }}
                      className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 text-center"
                      whileHover={{ scale: 1.05, y: -5 }}
                    >
                      <motion.div
                        className="w-12 h-12 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-3"
                        animate={{ 
                          boxShadow: [
                            "0 0 0 0 rgba(168, 85, 247, 0.7)",
                            "0 0 0 20px rgba(168, 85, 247, 0)",
                            "0 0 0 0 rgba(168, 85, 247, 0)"
                          ]
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        <IconComponent className="w-6 h-6 text-white" />
                      </motion.div>
                      <h3 className="text-white font-bold text-sm mb-1">{feature.title}</h3>
                      <p className="text-primary-400 text-xs font-semibold">{feature.description}</p>
                    </motion.div>
                  );
                })}
              </div>

              {/* Benefits List */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.8 }}
                className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10"
              >
                <h3 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
                  <Star className="w-6 h-6 text-yellow-400" />
                  <span>Lo que obtienes hoy:</span>
                </h3>
                
                <div className="space-y-3">
                  {benefits.map((benefit, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={isInView ? { opacity: 1, x: 0 } : {}}
                      transition={{ delay: 0.9 + index * 0.1 }}
                      className="flex items-center space-x-3"
                    >
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, delay: index * 0.2 }}
                      >
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                      </motion.div>
                      <span className="text-gray-300">{benefit}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>

              {/* Social Proof */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 1 }}
                className="flex items-center justify-center space-x-6 text-center"
              >
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary-400">10,000+</div>
                  <div className="text-gray-400 text-sm">Estudiantes Activos</div>
                </div>
                <div className="w-px h-12 bg-white/20"></div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary-400">4.9⭐</div>
                  <div className="text-gray-400 text-sm">Valoración Media</div>
                </div>
                <div className="w-px h-12 bg-white/20"></div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary-400">95%</div>
                  <div className="text-gray-400 text-sm">Mejoran sus Notas</div>
                </div>
              </motion.div>
            </motion.div>

            {/* Right Side - Sign Up Form */}
            <motion.div
              initial={{ opacity: 0, x: 100 }}
              animate={isInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 1, delay: 0.3 }}
              className="relative"
            >
              {!isSubmitted ? (
                <motion.div
                  className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 lg:p-12 border border-white/20 shadow-2xl"
                  whileHover={{ scale: 1.02 }}
                >
                  {/* Form Header */}
                  <div className="text-center mb-8">
                    <motion.div
                      className="w-20 h-20 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-4"
                      animate={{ 
                        rotate: [0, 10, -10, 0],
                        scale: [1, 1.1, 1]
                      }}
                      transition={{ duration: 3, repeat: Infinity }}
                    >
                      <Rocket className="w-10 h-10 text-white" />
                    </motion.div>
                    
                    <h3 className="text-2xl lg:text-3xl font-bold text-white mb-2">
                      ¡Comienza Gratis Ahora!
                    </h3>
                    <p className="text-gray-300">
                      Sin tarjeta de crédito. Cancela cuando quieras.
                    </p>
                  </div>

                  {/* Form */}
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={isInView ? { opacity: 1, y: 0 } : {}}
                      transition={{ delay: 1.2 }}
                    >
                      <label className="block text-white font-semibold mb-2">
                        Tu Email (para empezar la aventura)
                      </label>
                      <motion.input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="tu-email@ejemplo.com"
                        className="w-full px-6 py-4 bg-white/20 backdrop-blur-xl border border-white/30 rounded-2xl text-white placeholder-gray-300 focus:outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-400/50 transition-all duration-300"
                        whileFocus={{ scale: 1.02 }}
                        required
                      />
                    </motion.div>

                    <motion.button
                      type="submit"
                      disabled={isLoading || !email}
                      className="w-full py-5 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-2xl font-bold text-lg shadow-xl hover:shadow-2xl transition-all duration-300 flex items-center justify-center space-x-3 disabled:opacity-50 disabled:cursor-not-allowed"
                      whileHover={{ scale: 1.02, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                      initial={{ opacity: 0, y: 20 }}
                      animate={isInView ? { opacity: 1, y: 0 } : {}}
                      transition={{ delay: 1.3 }}
                    >
                      {isLoading ? (
                        <>
                          <motion.div
                            className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full"
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity }}
                          />
                          <span>Creando tu aventura...</span>
                        </>
                      ) : (
                        <>
                          <Rocket className="w-6 h-6" />
                          <span>¡Comenzar mi Transformación!</span>
                          <ArrowRight className="w-6 h-6" />
                        </>
                      )}
                    </motion.button>
                  </form>

                  {/* Trust Signals */}
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={isInView ? { opacity: 1 } : {}}
                    transition={{ delay: 1.4 }}
                    className="mt-6 text-center"
                  >
                    <div className="flex items-center justify-center space-x-4 text-sm text-gray-400">
                      <div className="flex items-center space-x-1">
                        <Shield className="w-4 h-4" />
                        <span>100% Seguro</span>
                      </div>
                      <div className="w-px h-4 bg-gray-600"></div>
                      <div className="flex items-center space-x-1">
                        <Users className="w-4 h-4" />
                        <span>+10k estudiantes</span>
                      </div>
                      <div className="w-px h-4 bg-gray-600"></div>
                      <div className="flex items-center space-x-1">
                        <Trophy className="w-4 h-4" />
                        <span>Garantizado</span>
                      </div>
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
                    �
                  </motion.div>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 lg:p-12 border border-white/20 shadow-2xl text-center"
                >
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.3, type: "spring" }}
                    className="w-24 h-24 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6"
                  >
                    <CheckCircle className="w-12 h-12 text-white" />
                  </motion.div>
                  
                  <h3 className="text-3xl font-bold text-white mb-4">
                    ¡Bienvenido a Acadify! 🎉
                  </h3>
                  
                  <p className="text-gray-300 mb-6">
                    Revisa tu email para activar tu cuenta y conocer a Rutilio.
                    ¡Tu aventura académica épica está a punto de comenzar!
                  </p>
                  
                  <motion.div
                    animate={{ 
                      y: [0, -10, 0],
                      rotate: [0, 5, -5, 0]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="text-6xl mb-4"
                  >
                    �
                  </motion.div>
                  
                  <p className="text-primary-400 font-semibold">
                    Rutilio te está esperando... 🚀
                  </p>
                </motion.div>
              )}
            </motion.div>
          </div>
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 1.5 }}
          className="text-center mt-16"
        >
                              <p className="text-gray-400 text-sm mb-4">
            ¿Tienes preguntas? Contáctanos en <span className="text-primary-400">hola@acadify.com</span>
          </p>
          <div className="flex justify-center items-center space-x-2 text-gray-500 text-xs">
            <span>Términos y Condiciones</span>
            <span>•</span>
            <span>Política de Privacidad</span>
            <span>•</span>
            <span>Soporte 24/7</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default CTASection;