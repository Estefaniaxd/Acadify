import React, { useState, ChangeEvent, FormEvent } from 'react'
import axios from 'axios'
import { useAuth } from '../../context/AuthContext'
import formatApiError from '../../utils/formatApiError'
import { motion, AnimatePresence } from 'framer-motion'
import { FiEye, FiEyeOff, FiUser, FiLock, FiShield, FiCheckCircle, FiAlertCircle, FiMail, FiArrowRight } from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'

export default function Login() {
  const { login } = useAuth()
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
        alert('Login exitoso')
        // Aquí puedes redirigir a dashboard o recargar
        window.location.href = '/dashboard'
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
    <div className="min-h-screen flex flex-col relative overflow-hidden bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 dark:from-gray-900 dark:via-purple-900/20 dark:to-indigo-900/20">
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
        className="relative z-10 w-full max-w-md mx-auto px-6 flex-1 flex items-center justify-center"
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
          className="relative w-full"
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
        <div>
          <label className="block text-sm mb-1 font-semibold text-gray-700 dark:text-gray-200" htmlFor="password">Contraseña</label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              className={`w-full px-4 py-3 pr-12 rounded-lg border-2 focus:ring-2 text-lg bg-white dark:bg-[#23232b] text-gray-800 dark:text-gray-100 border-primary/30 dark:border-purple-400/30 focus:outline-none focus:ring-primary/40 ${touched.password && !password ? 'border-red-400' : ''}`}
              value={password}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
              onBlur={() => setTouched({ ...touched, password: true })}
              required
              placeholder="Tu contraseña"
            />
            <button type="button" className="absolute inset-y-0 right-3 flex items-center" tabIndex={-1} onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}>
              {showPassword ? (
                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" /></svg>
              ) : (
                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
              )}
            </button>
          </div>
        </div>
        {otpRequired && (
          <div>
            <label className="block text-sm mb-1 font-semibold text-gray-700 dark:text-gray-200" htmlFor="otp">Código OTP</label>
            <input
              id="otp"
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              maxLength={6}
              className="w-full px-4 py-3 rounded-lg border-2 focus:ring-2 text-lg bg-white dark:bg-[#23232b] text-gray-800 dark:text-gray-100 border-primary/30 dark:border-purple-400/30 focus:outline-none focus:ring-primary/40"
              value={otp}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setOtp(e.target.value)}
              required
              placeholder="Código de autenticación"
            />
            <div className="text-xs text-gray-500 mt-1">{otpMessage}</div>
          </div>
        )}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer select-none">
            <input type="checkbox" checked={remember} onChange={() => setRemember(!remember)} className="accent-primary w-4 h-4 rounded" />
            Recordarme
          </label>
          <a href="/recover" className="text-sm text-primary hover:underline">¿Olvidaste tu contraseña?</a>
        </div>
        <label className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 cursor-pointer select-none mt-2">
          <input type="checkbox" checked={accepted} onChange={() => setAccepted(!accepted)} className="accent-primary w-4 h-4 rounded" required />
          Acepto el <a href="/legal/TratamientoDatos" className="underline text-primary dark:text-purple-300 ml-1" target="_blank" rel="noopener noreferrer">tratamiento de datos</a>
        </label>
        {error && <div className="text-red-600 text-sm text-center font-semibold bg-red-50 dark:bg-red-900/30 px-4 py-2 rounded-xl shadow">{error}</div>}
        <button
          type="submit"
          className="w-full py-3 rounded-2xl bg-gradient-to-r from-primary to-purple-600 text-white font-extrabold text-lg shadow-xl hover:scale-105 transition-transform drop-shadow-xl border-2 border-primary/30 dark:border-purple-400/30 mt-2"
          disabled={loading}
        >
          {loading ? 'Ingresando...' : 'Ingresar'}
        </button>
        <div className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
          ¿No tienes cuenta? <a href="/register" className="text-primary dark:text-purple-300 underline font-semibold">Regístrate gratis</a>
        </div>
      </form>
    </section>
  )
}
