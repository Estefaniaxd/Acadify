import React from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

export default function Footer() {
  const currentYear = new Date().getFullYear()
  
  const socialLinks = [
    {
      name: 'GitHub',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
        </svg>
      ),
      href: 'https://github.com/estefaniaxd/acadify'
    },
    {
      name: 'Discord',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.196.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
        </svg>
      ),
      href: '#'
    },
    {
      name: 'Twitter',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
        </svg>
      ),
      href: '#'
    }
  ]

  const quickLinks = [
    { label: 'Acerca de', href: '/about' },
    { label: 'Términos', href: '/terms' },
    { label: 'Privacidad', href: '/privacy' },
    { label: 'Contacto', href: '/contact' }
  ]

  return (
    <motion.footer 
      className="relative mt-20 bg-gradient-to-br from-[#0a0712] via-[#1a1330] to-[#2a1a3a] text-white overflow-hidden border-t border-white/10 shadow-2xl"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
      viewport={{ once: true }}
    >
      {/* Efectos de fondo */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
      <motion.div 
        className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-purple-500 to-purple-900"
        initial={{ scaleX: 0 }}
        whileInView={{ scaleX: 1 }}
        transition={{ duration: 1.5, ease: 'easeInOut' }}
        viewport={{ once: true }}
      />

      <div className="relative container mx-auto px-6 py-16">
        {/* Sección principal */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 mb-12">
          {/* Logo y descripción */}
          <motion.div 
            className="space-y-6"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            viewport={{ once: true }}
          >
            <div className="flex items-center gap-3">
              <motion.div
                className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary via-purple-500 to-purple-900 flex items-center justify-center shadow-lg"
                whileHover={{ scale: 1.05, rotate: 5 }}
                transition={{ type: 'spring', stiffness: 300 }}
              >
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-white">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 6v6l4 2"/>
                </svg>
              </motion.div>
              <div>
                <h3 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-primary via-purple-400 to-purple-300">
                  Acadify
                </h3>
                <p className="text-sm text-gray-300">Aprende • Juega • Potencia</p>
              </div>
            </div>
            <p className="text-gray-300 leading-relaxed">
              Plataforma educativa gamificada que transforma el aprendizaje en una experiencia divertida y efectiva. 
              Únete a miles de estudiantes que ya están revolucionando su educación.
            </p>
            <div className="flex gap-4">
              {socialLinks.map((social, index) => (
                <motion.a
                  key={social.name}
                  href={social.href}
                  className="w-11 h-11 rounded-xl bg-white/10 hover:bg-primary/20 flex items-center justify-center transition-all duration-300 border border-white/10 hover:border-primary/30 group"
                  whileHover={{ scale: 1.1, y: -3, rotateY: 15 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, scale: 0 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 + (index * 0.1), duration: 0.4, type: 'spring', stiffness: 200 }}
                  viewport={{ once: true }}
                  target="_blank"
                  rel="noopener noreferrer"
                  title={social.name}
                >
                  <motion.div
                    className="text-gray-300 group-hover:text-primary"
                    whileHover={{ rotate: [0, -10, 10, 0] }}
                    transition={{ duration: 0.6 }}
                  >
                    {social.icon}
                  </motion.div>
                </motion.a>
              ))}
            </div>
          </motion.div>

          {/* Enlaces rápidos */}
          <motion.div 
            className="space-y-6"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h4 className="text-lg font-bold text-white mb-4">Enlaces rápidos</h4>
            <div className="space-y-3">
              {quickLinks.map((link, index) => (
                <motion.div
                  key={link.label}
                  initial={{ opacity: 0, x: -10 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + (index * 0.1), duration: 0.4 }}
                  viewport={{ once: true }}
                >
                  <Link 
                    to={link.href}
                    className="text-gray-300 hover:text-primary transition-colors duration-300 hover:translate-x-1 inline-block group"
                  >
                    <span className="border-b border-transparent group-hover:border-primary transition-all duration-300">
                      {link.label}
                    </span>
                  </Link>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Estadísticas o CTA */}
          <motion.div 
            className="space-y-6"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h4 className="text-lg font-bold text-white mb-4">¡Únete ahora!</h4>
            <p className="text-gray-300 mb-6">
              Comienza tu viaje de aprendizaje gamificado y descubre todo tu potencial.
            </p>
            <Link to="/register">
              <motion.button
                className="w-full px-6 py-4 rounded-xl bg-gradient-to-r from-primary to-purple-700 text-white font-semibold shadow-lg hover:shadow-primary/25 border border-primary/50 transition-all duration-300"
                whileHover={{ scale: 1.02, y: -2, boxShadow: '0 20px 40px rgba(139,92,246,0.4)' }}
                whileTap={{ scale: 0.98 }}
              >
                Crear cuenta gratis
              </motion.button>
            </Link>
            <div className="grid grid-cols-2 gap-6 pt-6">
              <motion.div 
                className="text-center p-4 rounded-xl bg-white/5 border border-white/10"
                whileHover={{ scale: 1.02, y: -2 }}
                transition={{ type: 'spring', stiffness: 200 }}
              >
                <motion.div 
                  className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-400"
                  initial={{ opacity: 0, scale: 0.5 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.5, duration: 0.6, type: 'spring' }}
                  viewport={{ once: true }}
                >
                  10K+
                </motion.div>
                <div className="text-sm text-gray-400 mt-1">Estudiantes activos</div>
              </motion.div>
              <motion.div 
                className="text-center p-4 rounded-xl bg-white/5 border border-white/10"
                whileHover={{ scale: 1.02, y: -2 }}
                transition={{ type: 'spring', stiffness: 200 }}
              >
                <motion.div 
                  className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-primary"
                  initial={{ opacity: 0, scale: 0.5 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.6, duration: 0.6, type: 'spring' }}
                  viewport={{ once: true }}
                >
                  500+
                </motion.div>
                <div className="text-sm text-gray-400 mt-1">Cursos disponibles</div>
              </motion.div>
            </div>
          </motion.div>
        </div>

        {/* Línea divisoria */}
        <motion.div 
          className="h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent mb-8"
          initial={{ scaleX: 0 }}
          whileInView={{ scaleX: 1 }}
          transition={{ duration: 1, ease: 'easeInOut' }}
          viewport={{ once: true }}
        />

        {/* Footer bottom */}
        <motion.div 
          className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          viewport={{ once: true }}
        >
          <div className="text-gray-300">
            © {currentYear} <span className="font-semibold text-primary">Acadify</span> — Proyecto open source con ❤️
          </div>
          <div className="flex items-center gap-6 text-gray-400">
            <span>Licencia MIT</span>
            <span>•</span>
            <span>Hecho con React & FastAPI</span>
          </div>
        </motion.div>
      </div>
    </motion.footer>
  )
}
