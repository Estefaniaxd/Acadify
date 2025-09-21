
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Mail, 
  Phone, 
  MapPin, 
  Facebook, 
  Twitter, 
  Instagram, 
  Linkedin, 
  Youtube,
  Send,
  Heart,
  Star,
  Crown,
  BookOpen,
  ArrowUp,
  Book,
  Users,
  Shield,
  ExternalLink
} from 'lucide-react';

const Footer: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isSubscribed, setIsSubscribed] = useState(false);

  const handleNewsletterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    setIsSubscribed(true);
    setEmail('');
    setTimeout(() => setIsSubscribed(false), 3000);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const socialLinks = [
    { icon: Facebook, href: '#', label: 'Facebook', color: 'hover:text-blue-400' },
    { icon: Twitter, href: '#', label: 'Twitter', color: 'hover:text-sky-400' },
    { icon: Instagram, href: '#', label: 'Instagram', color: 'hover:text-pink-400' },
    { icon: Linkedin, href: '#', label: 'LinkedIn', color: 'hover:text-blue-600' },
    { icon: Youtube, href: '#', label: 'YouTube', color: 'hover:text-red-500' }
  ];

  const footerLinks = {
    product: [
      { name: 'Características', href: '#features', external: false },
      { name: 'Gamificación', href: '#gamification', external: false },
      { name: 'Testimonios', href: '#testimonials', external: false },
      { name: 'Precios', href: '#pricing', external: false },
      { name: 'API Developers', href: '#', external: true }
    ],
    company: [
      { name: 'Sobre Nosotros', href: '#about', external: false },
      { name: 'Nuestro Equipo', href: '#team', external: false },
      { name: 'Carreras', href: '#careers', external: false },
      { name: 'Blog', href: '#blog', external: false },
      { name: 'Prensa', href: '#press', external: false }
    ],
    support: [
      { name: 'Centro de Ayuda', href: '#help', external: false },
      { name: 'Contacto', href: '#contact', external: false },
      { name: 'Status del Sistema', href: '#status', external: true },
      { name: 'Reportar Bug', href: '#bug-report', external: false },
      { name: 'Sugerencias', href: '#feedback', external: false }
    ],
    legal: [
      { name: 'Términos de Servicio', href: '#terms', external: false },
      { name: 'Política de Privacidad', href: '#privacy', external: false },
      { name: 'Cookies', href: '#cookies', external: false },
      { name: 'GDPR', href: '#gdpr', external: false },
      { name: 'Licencias', href: '#licenses', external: false }
    ]
  };

  const stats = [
    { icon: Users, number: '10,000+', label: 'Estudiantes Activos' },
    { icon: Book, number: '500+', label: 'Cursos Disponibles' },
    { icon: Star, number: '50,000+', label: 'Logros Desbloqueados' },
    { icon: Crown, number: '95%', label: 'Mejoran sus Notas' }
  ];

  return (
    <footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-black relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute top-0 left-1/4 w-96 h-96 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-full mix-blend-multiply filter blur-3xl opacity-10"
          animate={{ 
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
          }}
          transition={{ duration: 20, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-0 right-1/4 w-80 h-80 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full mix-blend-multiply filter blur-3xl opacity-10"
          animate={{ 
            scale: [1, 1.3, 1],
            x: [0, -30, 0],
          }}
          transition={{ duration: 25, repeat: Infinity, delay: 5 }}
        />
        
        {/* Subtle stars */}
        {[...Array(20)].map((_, i) => (
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
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 3,
            }}
          />
        ))}
      </div>

      <div className="container mx-auto px-6 relative z-10">
        {/* Newsletter Section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="py-16 border-b border-gray-700"
        >
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="mb-8"
            >
              <div className="flex justify-center items-center space-x-3 mb-4">
                <motion.div
                  animate={{ rotate: [0, 10, -10, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="text-4xl"
                >
                  😺
                </motion.div>
                <h2 className="text-3xl lg:text-4xl font-bold text-white">
                  ¡Mantente al día con Rutilio!
                </h2>
                <motion.div
                  animate={{ rotate: [0, -10, 10, 0] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 1 }}
                  className="text-4xl flex justify-center"
                >
                  <BookOpen className="w-10 h-10 text-primary-400 dark:text-accent-neon-green" />
                </motion.div>
              </div>
              <p className="text-xl text-gray-300 max-w-2xl mx-auto">
                Recibe tips de estudio, novedades de Acadify y consejos exclusivos de Rutilio directamente en tu email.
              </p>
            </motion.div>

            <motion.form
              onSubmit={handleNewsletterSubmit}
              className="flex flex-col sm:flex-row gap-4 max-w-lg mx-auto"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <motion.input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu-email@ejemplo.com"
                className="flex-1 px-6 py-4 bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-400/50 transition-all duration-300"
                whileFocus={{ scale: 1.02 }}
                required
              />
              <motion.button
                type="submit"
                disabled={isSubscribed}
                className="px-8 py-4 bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-2xl font-semibold hover:shadow-xl transition-all duration-300 flex items-center justify-center space-x-2 disabled:opacity-50"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {isSubscribed ? (
                  <>
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="text-green-400"
                    >
                      ✓
                    </motion.div>
                    <span>¡Suscrito!</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>Suscribirme</span>
                  </>
                )}
              </motion.button>
            </motion.form>

            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="text-sm text-gray-400 mt-4"
            >
              No spam, solo contenido valioso. Cancela cuando quieras.
            </motion.p>
          </div>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="py-16 border-b border-gray-700"
        >
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const IconComponent = stat.icon;
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="text-center"
                  whileHover={{ scale: 1.05 }}
                >
                  <motion.div
                    className="w-16 h-16 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl flex items-center justify-center mx-auto mb-4"
                    animate={{ 
                      boxShadow: [
                        "0 0 0 0 rgba(139, 92, 246, 0.4)",
                        "0 0 0 20px rgba(139, 92, 246, 0)",
                        "0 0 0 0 rgba(139, 92, 246, 0)"
                      ]
                    }}
                    transition={{ duration: 2, repeat: Infinity, delay: index * 0.5 }}
                  >
                    <IconComponent className="w-8 h-8 text-white" />
                  </motion.div>
                  <div className="text-3xl font-bold text-white mb-2">{stat.number}</div>
                  <div className="text-gray-400 text-sm">{stat.label}</div>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Main Footer Content */}
        <div className="py-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Company Info */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="lg:col-span-2 space-y-6"
          >
            <div className="flex items-center space-x-3">
              <motion.div
                className="w-12 h-12 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl flex items-center justify-center"
                whileHover={{ scale: 1.1, rotate: 5 }}
              >
                <span className="text-2xl font-bold text-white">A</span>
              </motion.div>
              <div>
                <h3 className="text-2xl font-bold text-white">Acadify</h3>
                <p className="text-gray-400 text-sm">Transformando el futuro educativo</p>
              </div>
            </div>

            <p className="text-gray-300 leading-relaxed">
              Acadify revoluciona la educación a través de la gamificación y la inteligencia artificial. 
              Junto a Rutilio, convertimos cada lección en una aventura épica que transforma vidas.
            </p>

            {/* Contact Info */}
            <div className="space-y-3">
              <motion.div 
                className="flex items-center space-x-3 text-gray-300"
                whileHover={{ x: 5 }}
              >
                <Mail className="w-5 h-5 text-primary-400" />
                <span>hola@acadify.com</span>
              </motion.div>
              <motion.div 
                className="flex items-center space-x-3 text-gray-300"
                whileHover={{ x: 5 }}
              >
                <Phone className="w-5 h-5 text-primary-400" />
                <span>+506 1234-5678</span>
              </motion.div>
              <motion.div 
                className="flex items-center space-x-3 text-gray-300"
                whileHover={{ x: 5 }}
              >
                <MapPin className="w-5 h-5 text-primary-400" />
                <span>San José, Costa Rica</span>
              </motion.div>
            </div>

            {/* Social Links */}
            <div className="flex space-x-4">
              {socialLinks.map((social, index) => {
                const IconComponent = social.icon;
                
                return (
                  <motion.a
                    key={index}
                    href={social.href}
                    aria-label={social.label}
                    className={`w-10 h-10 bg-gray-800 rounded-xl flex items-center justify-center text-gray-400 transition-all duration-300 ${social.color}`}
                    whileHover={{ scale: 1.1, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <IconComponent className="w-5 h-5" />
                  </motion.a>
                );
              })}
            </div>
          </motion.div>

          {/* Footer Links */}
          {Object.entries(footerLinks).map(([category, links], categoryIndex) => (
            <motion.div
              key={category}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: categoryIndex * 0.1 }}
              className="space-y-4"
            >
              <h4 className="text-white font-semibold text-lg capitalize mb-6">
                {category === 'product' ? 'Producto' :
                 category === 'company' ? 'Empresa' :
                 category === 'support' ? 'Soporte' : 'Legal'}
              </h4>
              <ul className="space-y-3">
                {links.map((link, linkIndex) => (
                  <motion.li key={linkIndex}>
                    <motion.a
                      href={link.href}
                      className="text-gray-400 hover:text-white transition-colors duration-300 flex items-center space-x-2"
                      whileHover={{ x: 5 }}
                    >
                      <span>{link.name}</span>
                      {link.external && <ExternalLink className="w-3 h-3" />}
                    </motion.a>
                  </motion.li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Bottom Bar */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="py-8 border-t border-gray-700 flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0"
        >
          <div className="flex items-center space-x-2 text-gray-400">
            <span>© 2024 Acadify. Hecho con</span>
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              <Heart className="w-4 h-4 text-red-400 fill-current" />
            </motion.div>
            <span>en Costa Rica</span>
          </div>

          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-gray-400 text-sm">
              <Shield className="w-4 h-4 text-green-400" />
              <span>SSL Seguro</span>
            </div>
            
            <div className="flex items-center space-x-2 text-gray-400 text-sm">
              <Star className="w-4 h-4 text-yellow-400" />
              <span>ISO 27001</span>
            </div>

            <motion.button
              onClick={scrollToTop}
              className="p-2 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors duration-300"
              whileHover={{ scale: 1.1, y: -2 }}
              whileTap={{ scale: 0.95 }}
              aria-label="Volver arriba"
            >
              <ArrowUp className="w-5 h-5" />
            </motion.button>
          </div>
        </motion.div>

        {/* Floating Rutilio */}
        <motion.div
          className="fixed bottom-8 right-8 z-50"
          animate={{ 
            y: [0, -10, 0],
            rotate: [0, 5, -5, 0]
          }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          <motion.div
            className="w-16 h-16 bg-gradient-to-r from-primary-600 to-secondary-600 dark:from-primary-neon dark:to-accent-neon-green rounded-full flex items-center justify-center shadow-xl dark:shadow-lg dark:shadow-primary-neon/50 cursor-pointer"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={scrollToTop}
          >
            <ArrowUp className="w-6 h-6 text-white" />
          </motion.div>
          
          {/* Tooltip */}
          <motion.div
            className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white px-3 py-2 rounded-lg text-sm whitespace-nowrap opacity-0 hover:opacity-100 transition-opacity duration-300"
            initial={{ opacity: 0, scale: 0.8 }}
            whileHover={{ opacity: 1, scale: 1 }}
          >
            ¡Rutilio te lleva hacia arriba!
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
          </motion.div>
        </motion.div>
      </div>
    </footer>
  );
};

export default Footer;