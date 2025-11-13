import { useState, ChangeEvent, FormEvent } from 'react'
import axios from 'axios'
import formatApiError from '../../utils/formatApiError'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, ArrowLeft, ArrowRight, CheckCircle, Key, Mail, Send } from "lucide-react";



export default function RecoverPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)
  const [focusedField, setFocusedField] = useState<string | null>(null)
  const [touched, setTouched] = useState(false)

  function validateEmail(email: string): string {
    if (!email) return 'El email es obligatorio'
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return 'Email inválido'
    return ''
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const emailError = validateEmail(email)
    if (emailError) return setError(emailError)
    
    setError('')
    setLoading(true)
    
    try {
      await axios.post(
        '/auth/forgot-password',
        { correo_institucional: email },
        {
          withCredentials: true,
          timeout: 10000,
          headers: { 'Content-Type': 'application/json' }
        }
      )
      setSent(true)
    } catch (err: any) {
      if (err.response && err.response.data) {
        setError(formatApiError(err.response.data))
      } else {
        setError('Error al enviar la solicitud. Intenta de nuevo.')
      }
    } finally {
      setLoading(false)
    }
  }

  const floatingAnimation = {
    y: [0, -10, 0],
    transition: {
      duration: 3,
      repeat: Infinity,
      ease: "easeInOut"
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center relative overflow-hidden py-20 md:py-24">
      {/* Fondo de página completo */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 dark:from-neutral-950 dark:via-blue-950/30 dark:to-purple-950/20" />
      
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-40 -right-40 w-96 h-96 rounded-full"
          style={{
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.4) 0%, rgba(147, 51, 234, 0.3) 50%, rgba(168, 85, 247, 0.2) 100%)',
            filter: 'blur(60px)'
          }}
          animate={{
            scale: [1, 1.3, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full"
          style={{
            background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.4) 0%, rgba(59, 130, 246, 0.3) 50%, rgba(147, 51, 234, 0.2) 100%)',
            filter: 'blur(60px)'
          }}
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [360, 180, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        
        {/* Partículas flotantes */}
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-blue-300/30 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -100, 0],
              opacity: [0, 1, 0],
              scale: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 3 + 2,
              repeat: Infinity,
              delay: Math.random() * 2,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative z-10 w-full max-w-md mx-auto px-6"
      >
        {/* Logo / Título flotante */}
        <motion.div
          animate={floatingAnimation}
          className="text-center mb-8"
        >
          <motion.div
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 shadow-xl mb-4 relative overflow-hidden"
            whileHover={{ scale: 1.1, rotate: 5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <Key className="w-8 h-8 text-white" />
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
              animate={{
                x: ['-100%', '200%'],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatDelay: 3,
                ease: "easeInOut"
              }}
            />
          </motion.div>
        </motion.div>

        {/* Contenido principal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="relative"
        >
          <div className="relative p-8 rounded-3xl bg-white/95 dark:bg-neutral-900/95 backdrop-blur-2xl border-2 border-blue-200/50 dark:border-blue-800/50 shadow-2xl overflow-hidden">
            {/* Efectos de fondo del formulario */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 via-indigo-600/5 to-transparent dark:from-blue-400/5 dark:via-indigo-400/5" />
            
            <div className="relative z-10">
              <AnimatePresence mode="wait">
                {sent ? (
                  // Pantalla de éxito
                  <motion.div
                    key="success"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.5 }}
                    className="text-center space-y-6"
                  >
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                      className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center mx-auto"
                    >
                      <Send className="w-10 h-10 text-white" />
                    </motion.div>
                    
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 }}
                      className="space-y-4"
                    >
                      <h2 className="text-2xl font-black text-gray-900 dark:text-white">
                        ¡Correo enviado!
                      </h2>
                      <div className="space-y-3 text-sm text-gray-600 dark:text-gray-300">
                        <p>
                          Si el email <strong className="text-blue-600 dark:text-blue-400">{email}</strong> está registrado, 
                          recibirás instrucciones para restablecer tu contraseña.
                        </p>
                        <p>
                          Revisa tu bandeja de entrada y sigue el enlace para continuar.
                        </p>
                      </div>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.6 }}
                      className="space-y-4"
                    >
                      <motion.a
                        href={`/reset-password?correo_institucional=${encodeURIComponent(email)}`}
                        className="inline-flex items-center gap-3 px-6 py-3 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-700 text-white font-bold shadow-xl hover:shadow-2xl transition-all duration-300"
                        whileHover={{ scale: 1.02, y: -2 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Key className="w-5 h-5" />
                        Ir a restablecer contraseña
                        <ArrowRight className="w-4 h-4" />
                      </motion.a>
                      
                      <div className="text-center">
                        <motion.a
                          href="/login"
                          className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors duration-200 inline-flex items-center gap-2"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <ArrowLeft className="w-4 h-4" />
                          Volver al login
                        </motion.a>
                      </div>
                    </motion.div>
                  </motion.div>
                ) : (
                  // Formulario de recuperación
                  <motion.div
                    key="form"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.5 }}
                    className="space-y-6"
                  >
                    <div className="text-center">
                      <motion.h2
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-2xl font-black text-gray-900 dark:text-white mb-2"
                      >
                        ¿Olvidaste tu contraseña?
                      </motion.h2>
                      <motion.p
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-gray-600 dark:text-gray-300 text-sm"
                      >
                        No te preocupes, te ayudaremos a recuperar el acceso a tu cuenta
                      </motion.p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                      {/* Campo de email */}
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2, duration: 0.6 }}
                      >
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                          Correo electrónico
                        </label>
                        <div className="relative group">
                          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <motion.div
                              animate={{
                                color: focusedField === 'email' ? '#3b82f6' : '#9ca3af'
                              }}
                              transition={{ duration: 0.2 }}
                            >
                              <Mail className="w-5 h-5" />
                            </motion.div>
                          </div>
                          <input
                            type="email"
                            autoComplete="username"
                            className={`w-full pl-12 pr-4 py-4 rounded-2xl border-2 text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 bg-gray-50/80 dark:bg-gray-700/80 backdrop-blur-sm transition-all duration-300 focus:outline-none focus:ring-0 ${
                              focusedField === 'email'
                                ? 'border-blue-500 bg-white dark:bg-gray-700 shadow-lg shadow-blue-500/20'
                                : error
                                ? 'border-red-400 bg-red-50 dark:bg-red-900/20'
                                : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                            }`}
                            value={email}
                            onChange={(e: ChangeEvent<HTMLInputElement>) => {
                              setEmail(e.target.value)
                              if (error) setError('')
                            }}
                            onFocus={() => setFocusedField('email')}
                            onBlur={() => {
                              setFocusedField(null)
                              setTouched(true)
                            }}
                            required
                            placeholder="Ingresa tu correo electrónico"
                          />
                          
                          {/* Indicadores de validación */}
                          <AnimatePresence>
                            {touched && !error && email && (
                              <motion.div
                                initial={{ opacity: 0, scale: 0 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0 }}
                                className="absolute inset-y-0 right-4 flex items-center"
                              >
                                <CheckCircle className="w-5 h-5 text-emerald-500" />
                              </motion.div>
                            )}
                            {error && (
                              <motion.div
                                initial={{ opacity: 0, scale: 0 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0 }}
                                className="absolute inset-y-0 right-4 flex items-center"
                              >
                                <AlertCircle className="w-5 h-5 text-red-500" />
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                        
                        {/* Mensaje de error */}
                        <AnimatePresence>
                          {error && (
                            <motion.p
                              initial={{ opacity: 0, y: -10 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -10 }}
                              className="mt-2 text-sm text-red-600 dark:text-red-400 flex items-center gap-2"
                            >
                              <AlertCircle className="w-4 h-4" />
                              {error}
                            </motion.p>
                          )}
                        </AnimatePresence>
                      </motion.div>

                      {/* Información adicional */}
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="p-4 rounded-2xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800"
                      >
                        <div className="flex items-start gap-3">
                          <Mail className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                          <div className="text-sm text-blue-700 dark:text-blue-300">
                            <p className="font-medium mb-1">¿Qué sucederá después?</p>
                            <ul className="space-y-1 text-xs opacity-90">
                              <li>• Te enviaremos un código de verificación</li>
                              <li>• Podrás crear una nueva contraseña</li>
                              <li>• Tu cuenta estará protegida</li>
                            </ul>
                          </div>
                        </div>
                      </motion.div>

                      {/* Botón de envío */}
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                      >
                        <motion.button
                          type="submit"
                          disabled={loading || !email}
                          className="relative w-full py-4 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white font-bold text-lg shadow-xl overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
                          whileHover={!loading && email ? { scale: 1.02, y: -2 } : {}}
                          whileTap={!loading && email ? { scale: 0.98 } : {}}
                        >
                          {/* Efecto de brillo */}
                          <motion.div
                            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                            animate={{
                              x: loading ? ['-100%', '200%'] : '-100%',
                            }}
                            transition={{
                              duration: 1.5,
                              repeat: loading ? Infinity : 0,
                              ease: "easeInOut"
                            }}
                          />
                          
                          <motion.div
                            className="relative flex items-center justify-center gap-3"
                            initial={false}
                            animate={loading ? { opacity: 0.7 } : { opacity: 1 }}
                          >
                            {loading ? (
                              <>
                                <motion.div
                                  className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                                  animate={{ rotate: 360 }}
                                  transition={{
                                    duration: 1,
                                    repeat: Infinity,
                                    ease: "linear"
                                  }}
                                />
                                Enviando instrucciones...
                              </>
                            ) : (
                              <>
                                <Send className="w-5 h-5" />
                                Enviar instrucciones
                                <motion.div
                                  className="group-hover:translate-x-1 transition-transform duration-200"
                                >
                                  <ArrowRight className="w-4 h-4" />
                                </motion.div>
                              </>
                            )}
                          </motion.div>
                        </motion.button>
                      </motion.div>

                      {/* Enlaces adicionales */}
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="text-center space-y-3"
                      >
                        <motion.a
                          href="/reset-password"
                          className="block text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors duration-200"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          ¿Ya tienes el código? Restablecer contraseña
                        </motion.a>
                        
                        <motion.a
                          href="/login"
                          className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors duration-200 inline-flex items-center gap-2"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <ArrowLeft className="w-4 h-4" />
                          Volver al login
                        </motion.a>
                      </motion.div>
                    </form>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  )
}