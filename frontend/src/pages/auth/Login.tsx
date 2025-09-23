import React, { useState, ChangeEvent, FormEvent } from 'react'
import axios from 'axios'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../context/ToastContext'
import { useNavigate } from 'react-router-dom'
import formatApiError from '../../utils/formatApiError'
import { motion, AnimatePresence } from 'framer-motion'
import { FiEye, FiEyeOff, FiUser, FiLock, FiShield, FiCheckCircle, FiAlertCircle, FiMail, FiArrowRight } from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'

export default function Login() {
  const { login } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [otp, setOtp] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [otpRequired, setOtpRequired] = useState(false)
  const [otpMessage, setOtpMessage] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [remember, setRemember] = useState(false)
  const [accepted, setAccepted] = useState(false)
  const [touched, setTouched] = useState<{[key:string]:boolean}>({})
  const [focusedField, setFocusedField] = useState<string | null>(null)

  function validate() {
    if (!identifier || !password) return 'Todos los campos son obligatorios.'
    if (!accepted) return 'Debes aceptar el tratamiento de datos.'
    return ''
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const err = validate()
    if (err) return setError(err)
    setError('')
    setLoading(true)
    
    try {
      const payload: any = { identifier, password, remember }
      if (otpRequired && otp) payload.otp_code = otp
      const res = await axios.post(
        '/auth/login',
        payload,
        { 
          withCredentials: true,
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      )
      // Si login exitoso, guardar tokens y redirigir
      if (res.data.access_token) {
        login(res.data.access_token)
        setError('')
        
        // Notificación bonita de éxito
        toast.success(
          '¡Bienvenido de vuelta!', 
          'Sesión iniciada correctamente. Te redirigiremos a tu dashboard.',
          3000
        )
        
        // Determinar a qué dashboard redirigir basado en el rol del usuario
        setTimeout(() => {
          // Si tenemos información del usuario en el token, podemos usar esa info
          // Por ahora, redirigimos a un dashboard general
          navigate('/dashboard')
        }, 1500)
      } else if (res.data.status === 'otp_required') {
        setOtpRequired(true)
        setOtpMessage(res.data.message || 'Se requiere código OTP')
      }
    } catch (err: any) {
      if (err.response) {
        if (err.response.status === 401) {
          setError('Credenciales incorrectas')
        } else if (err.response.status === 423) {
          setError('Cuenta bloqueada por intentos fallidos')
        } else if (err.response.data) {
          setError(formatApiError(err.response.data))
        } else {
          setError(`Error del servidor: ${err.response.status} - ${err.response.statusText}`)
        }
      } else if (err.request) {
        setError('No se pudo conectar al servidor. Verifica que el backend esté corriendo en http://127.0.0.1:8000')
      } else {
        setError(`Error: ${err.message}`)
      }
    } finally {
      setLoading(false)
    }
  }

  // Animaciones para los elementos
  const containerVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
        ease: "easeOut",
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: "easeOut" }
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
  <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 dark:from-gray-900 dark:via-purple-900/20 dark:to-indigo-900/20 pt-16 pb-16 md:pt-24 md:pb-24">
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-40 -right-40 w-96 h-96 rounded-full"
          style={{
            background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.4) 0%, rgba(147, 51, 234, 0.3) 50%, rgba(79, 70, 229, 0.2) 100%)',
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
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.4) 0%, rgba(147, 51, 234, 0.3) 50%, rgba(168, 85, 247, 0.2) 100%)',
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
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-violet-300/30 rounded-full"
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
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-10 w-full max-w-md mx-auto px-6"
      >
        {/* Logo / Título flotante */}
        <motion.div
          animate={floatingAnimation}
          className="text-center mb-8"
        >
          <motion.div
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600 to-purple-700 shadow-xl mb-4 relative overflow-hidden"
            whileHover={{ scale: 1.1, rotate: 5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <HiSparkles className="w-8 h-8 text-white" />
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
          <motion.h1
            variants={itemVariants}
            className="text-3xl font-black text-gray-900 dark:text-white mb-2"
          >
            ¡Bienvenido de vuelta!
          </motion.h1>
          <motion.p
            variants={itemVariants}
            className="text-gray-600 dark:text-gray-300 text-sm"
          >
            Inicia sesión para continuar tu aventura de aprendizaje
          </motion.p>
        </motion.div>

        {/* Formulario principal */}
        <motion.form
          onSubmit={handleSubmit}
          variants={itemVariants}
          className="relative"
        >
          {/* Contenedor del formulario con glassmorphism */}
          <div className="relative p-8 rounded-3xl bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl border border-white/50 dark:border-gray-700/50 shadow-2xl overflow-hidden">
            {/* Efectos de fondo del formulario */}
            <div className="absolute inset-0 bg-gradient-to-br from-violet-600/5 via-purple-600/5 to-transparent dark:from-violet-400/10 dark:via-purple-400/10" />
            
            <div className="relative z-10 space-y-6">
              {/* Campo de identificador */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2, duration: 0.6 }}
              >
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2" htmlFor="identifier">
                  Usuario o Email
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <motion.div
                      animate={{
                        color: focusedField === 'identifier' ? '#8b5cf6' : '#9ca3af'
                      }}
                      transition={{ duration: 0.2 }}
                    >
                      <FiUser className="w-5 h-5" />
                    </motion.div>
                  </div>
                  <input
                    id="identifier"
                    type="text"
                    autoComplete="username"
                    className={`w-full pl-12 pr-4 py-4 rounded-2xl border-2 text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 bg-gray-50/80 dark:bg-gray-700/80 backdrop-blur-sm transition-all duration-300 focus:outline-none focus:ring-0 ${
                      focusedField === 'identifier'
                        ? 'border-violet-500 bg-white dark:bg-gray-700 shadow-lg shadow-violet-500/20'
                        : touched.identifier && !identifier
                        ? 'border-red-400 bg-red-50 dark:bg-red-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                    value={identifier}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setIdentifier(e.target.value)}
                    onFocus={() => setFocusedField('identifier')}
                    onBlur={() => {
                      setFocusedField(null)
                      setTouched({ ...touched, identifier: true })
                    }}
                    required
                    placeholder="Ingresa tu usuario o email"
                  />
                  {/* Indicador de validación */}
                  <AnimatePresence>
                    {touched.identifier && identifier && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0 }}
                        className="absolute inset-y-0 right-4 flex items-center"
                      >
                        <FiCheckCircle className="w-5 h-5 text-emerald-500" />
                      </motion.div>
                    )}
                    {touched.identifier && !identifier && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0 }}
                        className="absolute inset-y-0 right-4 flex items-center"
                      >
                        <FiAlertCircle className="w-5 h-5 text-red-500" />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>

              {/* Campo de contraseña */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3, duration: 0.6 }}
              >
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2" htmlFor="password">
                  Contraseña
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <motion.div
                      animate={{
                        color: focusedField === 'password' ? '#8b5cf6' : '#9ca3af'
                      }}
                      transition={{ duration: 0.2 }}
                    >
                      <FiLock className="w-5 h-5" />
                    </motion.div>
                  </div>
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    className={`w-full pl-12 pr-12 py-4 rounded-2xl border-2 text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 bg-gray-50/80 dark:bg-gray-700/80 backdrop-blur-sm transition-all duration-300 focus:outline-none focus:ring-0 ${
                      focusedField === 'password'
                        ? 'border-violet-500 bg-white dark:bg-gray-700 shadow-lg shadow-violet-500/20'
                        : touched.password && !password
                        ? 'border-red-400 bg-red-50 dark:bg-red-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                    value={password}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                    onFocus={() => setFocusedField('password')}
                    onBlur={() => {
                      setFocusedField(null)
                      setTouched({ ...touched, password: true })
                    }}
                    required
                    placeholder="Ingresa tu contraseña"
                  />
                  <motion.button
                    type="button"
                    className="absolute inset-y-0 right-4 flex items-center text-gray-400 hover:text-violet-600 transition-colors duration-200"
                    onClick={() => setShowPassword(!showPassword)}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {showPassword ? <FiEyeOff className="w-5 h-5" /> : <FiEye className="w-5 h-5" />}
                  </motion.button>
                  {/* Indicador de validación */}
                  <AnimatePresence>
                    {touched.password && password && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0 }}
                        className="absolute inset-y-0 right-12 flex items-center"
                      >
                        <FiCheckCircle className="w-5 h-5 text-emerald-500" />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>

              {/* Campo OTP (si es requerido) */}
              <AnimatePresence>
                {otpRequired && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.4 }}
                  >
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2" htmlFor="otp">
                      Código OTP
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <FiShield className="w-5 h-5 text-violet-500" />
                      </div>
                      <input
                        id="otp"
                        type="text"
                        inputMode="numeric"
                        pattern="[0-9]*"
                        maxLength={6}
                        className="w-full pl-12 pr-4 py-4 rounded-2xl border-2 border-violet-300 dark:border-violet-600 text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 bg-violet-50/80 dark:bg-violet-900/20 backdrop-blur-sm transition-all duration-300 focus:outline-none focus:ring-0 focus:border-violet-500 focus:bg-white dark:focus:bg-violet-900/30"
                        value={otp}
                        onChange={(e: ChangeEvent<HTMLInputElement>) => setOtp(e.target.value)}
                        required
                        placeholder="Código de 6 dígitos"
                      />
                    </div>
                    {otpMessage && (
                      <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-sm text-violet-600 dark:text-violet-400 mt-2 flex items-center gap-2"
                      >
                        <FiMail className="w-4 h-4" />
                        {otpMessage}
                      </motion.p>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Opciones adicionales */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.6 }}
                className="flex items-center justify-between"
              >
                <motion.label
                  className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300 cursor-pointer select-none group"
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={remember}
                      onChange={() => setRemember(!remember)}
                      className="sr-only"
                    />
                    <motion.div
                      className={`w-5 h-5 rounded-lg border-2 flex items-center justify-center transition-all duration-200 ${
                        remember
                          ? 'bg-violet-600 border-violet-600 text-white'
                          : 'border-gray-300 dark:border-gray-600 group-hover:border-violet-400'
                      }`}
                      whileTap={{ scale: 0.9 }}
                    >
                      <AnimatePresence>
                        {remember && (
                          <motion.div
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0 }}
                          >
                            <FiCheckCircle className="w-3 h-3" />
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  </div>
                  Recordarme
                </motion.label>
                
                <motion.a
                  href="/recover"
                  className="text-sm font-medium text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300 transition-colors duration-200"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  ¿Olvidaste tu contraseña?
                </motion.a>
              </motion.div>

              {/* Checkbox de aceptación */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5, duration: 0.6 }}
              >
                <motion.label
                  className="flex items-start gap-3 text-xs text-gray-500 dark:text-gray-400 cursor-pointer select-none group"
                  whileHover={{ scale: 1.01 }}
                >
                  <div className="relative mt-0.5">
                    <input
                      type="checkbox"
                      checked={accepted}
                      onChange={() => setAccepted(!accepted)}
                      className="sr-only"
                      required
                    />
                    <motion.div
                      className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all duration-200 ${
                        accepted
                          ? 'bg-violet-600 border-violet-600 text-white'
                          : 'border-gray-300 dark:border-gray-600 group-hover:border-violet-400'
                      }`}
                      whileTap={{ scale: 0.9 }}
                    >
                      <AnimatePresence>
                        {accepted && (
                          <motion.div
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0 }}
                          >
                            <FiCheckCircle className="w-2.5 h-2.5" />
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  </div>
                  <span>
                    Acepto el{' '}
                    <motion.a
                      href="/legal/TratamientoDatos"
                      className="text-violet-600 dark:text-violet-400 underline hover:text-violet-700 dark:hover:text-violet-300 transition-colors"
                      target="_blank"
                      rel="noopener noreferrer"
                      whileHover={{ scale: 1.05 }}
                    >
                      tratamiento de datos
                    </motion.a>
                  </span>
                </motion.label>
              </motion.div>

              {/* Mensaje de error */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    className="p-4 rounded-2xl bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm font-medium flex items-center gap-3"
                  >
                    <FiAlertCircle className="w-5 h-5 flex-shrink-0" />
                    <span>{error}</span>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Botón de envío */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6, duration: 0.6 }}
              >
                <motion.button
                  type="submit"
                  disabled={loading}
                  className="relative w-full py-4 rounded-2xl bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 text-white font-bold text-lg shadow-xl overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
                  whileHover={!loading ? { scale: 1.02, y: -2 } : {}}
                  whileTap={!loading ? { scale: 0.98 } : {}}
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
                        Iniciando sesión...
                      </>
                    ) : (
                      <>
                        Iniciar Sesión
                        <motion.div
                          className="group-hover:translate-x-1 transition-transform duration-200"
                        >
                          <FiArrowRight className="w-5 h-5" />
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
                transition={{ delay: 0.7, duration: 0.6 }}
                className="text-center"
              >
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  ¿No tienes cuenta?{' '}
                  <motion.a
                    href="/register"
                    className="font-bold text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300 transition-colors duration-200"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Regístrate gratis
                  </motion.a>
                </p>
              </motion.div>
            </div>
          </div>
        </motion.form>
      </motion.div>
    </div>
  )
}