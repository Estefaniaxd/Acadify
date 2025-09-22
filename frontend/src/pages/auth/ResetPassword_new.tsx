import { useState, ChangeEvent, FormEvent, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import axios from 'axios'
import formatApiError from '../../utils/formatApiError'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  FiEye, FiEyeOff, FiLock, FiCheckCircle, FiAlertCircle, FiMail, 
  FiArrowRight, FiShield, FiKey, FiRefreshCw 
} from 'react-icons/fi'
import { HiShieldCheck } from 'react-icons/hi'

export default function ResetPassword() {
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [errors, setErrors] = useState<{[key: string]: string}>({})
  const [globalError, setGlobalError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [focusedField, setFocusedField] = useState<string | null>(null)
  const [touched, setTouched] = useState<{[key: string]: boolean}>({})
  const navigate = useNavigate()
  const location = useLocation()

  // Validaciones en tiempo real
  const validateField = (field: string, value: string): string => {
    switch (field) {
      case 'email':
        return !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value) ? 'Email inválido' : ''
      case 'code':
        return value.length < 6 ? 'El código debe tener al menos 6 caracteres' : ''
      case 'password':
        if (value.length < 10) return 'La contraseña debe tener al menos 10 caracteres'
        const hasUpper = /[A-Z]/.test(value)
        const hasLower = /[a-z]/.test(value)
        const hasDigit = /[0-9]/.test(value)
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(value)
        if (!hasUpper || !hasLower || !hasDigit || !hasSpecial) 
          return 'Debe contener mayúscula, minúscula, número y carácter especial'
        return ''
      case 'confirm':
        return value !== password ? 'Las contraseñas no coinciden' : ''
      default:
        return ''
    }
  }

  const updateField = (field: string, value: string) => {
    switch (field) {
      case 'email': setEmail(value); break
      case 'code': setCode(value); break
      case 'password': setPassword(value); break
      case 'confirm': setConfirm(value); break
    }
    
    // Validar en tiempo real
    const error = validateField(field, value)
    setErrors(prev => ({ ...prev, [field]: error }))
    
    // Si es confirmar contraseña, también validar cuando cambie la contraseña
    if (field === 'password' && confirm) {
      const confirmError = validateField('confirm', confirm)
      setErrors(prev => ({ ...prev, confirm: confirmError }))
    }
  }

  // Prefill desde query params
  useEffect(() => {
    const qp = new URLSearchParams(location.search)
    const correo = qp.get('correo_institucional')
    const codigo = qp.get('reset_code')
    if (correo) setEmail(correo)
    if (codigo) setCode(codigo)
  }, [location.search])

  function validate() {
    const newErrors: {[key: string]: string} = {}
    
    if (!email) newErrors.email = 'El email es obligatorio'
    else newErrors.email = validateField('email', email)
    
    if (!code) newErrors.code = 'El código es obligatorio'
    else newErrors.code = validateField('code', code)
    
    if (!password) newErrors.password = 'La contraseña es obligatoria'
    else newErrors.password = validateField('password', password)
    
    if (!confirm) newErrors.confirm = 'Confirma tu contraseña'
    else newErrors.confirm = validateField('confirm', confirm)
    
    setErrors(newErrors)
    return Object.values(newErrors).every(error => !error)
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!validate()) return
    
    setGlobalError('')
    setLoading(true)
    
    try {
      await axios.post(
        '/auth/reset-password',
        {
          correo_institucional: email,
          reset_code: code,
          new_password: password
        },
        {
          withCredentials: true,
          timeout: 10000,
          headers: { 'Content-Type': 'application/json' }
        }
      )
      setSuccess(true)
      setTimeout(() => navigate('/login'), 3000)
    } catch (err: any) {
      if (err.response && err.response.data) {
        setGlobalError(formatApiError(err.response.data))
      } else {
        setGlobalError('Error al restablecer la contraseña. Intenta de nuevo.')
      }
    } finally {
      setLoading(false)
    }
  }

  // Componente de campo personalizado
  const FormField = ({ 
    icon: Icon, 
    label, 
    field, 
    type = 'text', 
    placeholder, 
    isPassword = false,
    showPasswordToggle = null
  }: {
    icon: any
    label: string
    field: string
    type?: string
    placeholder: string
    isPassword?: boolean
    showPasswordToggle?: boolean | null
  }) => {
    const value = field === 'email' ? email : field === 'code' ? code : field === 'password' ? password : confirm
    const isVisible = showPasswordToggle !== null ? showPasswordToggle : false
    
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className="space-y-2"
      >
        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
          {label}
        </label>
        <div className="relative group">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <motion.div
              animate={{
                color: focusedField === field ? '#3b82f6' : '#9ca3af'
              }}
              transition={{ duration: 0.2 }}
            >
              <Icon className="w-5 h-5" />
            </motion.div>
          </div>
          
          <input
            type={isPassword ? (isVisible ? 'text' : 'password') : type}
            className={`w-full pl-12 ${isPassword ? 'pr-12' : 'pr-4'} py-4 rounded-2xl border-2 text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 bg-gray-50/80 dark:bg-gray-700/80 backdrop-blur-sm transition-all duration-300 focus:outline-none focus:ring-0 ${
              focusedField === field
                ? 'border-blue-500 bg-white dark:bg-gray-700 shadow-lg shadow-blue-500/20'
                : errors[field]
                ? 'border-red-400 bg-red-50 dark:bg-red-900/20'
                : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
            }`}
            value={value}
            onChange={(e) => updateField(field, e.target.value)}
            onFocus={() => setFocusedField(field)}
            onBlur={() => {
              setFocusedField(null)
              setTouched(prev => ({ ...prev, [field]: true }))
            }}
            placeholder={placeholder}
            autoComplete={field === 'email' ? 'username' : isPassword ? 'new-password' : 'off'}
          />
          
          {isPassword && (
            <motion.button
              type="button"
              className="absolute inset-y-0 right-4 flex items-center text-gray-400 hover:text-blue-600 transition-colors duration-200"
              onClick={() => field === 'password' ? setShowPassword(!showPassword) : setShowConfirm(!showConfirm)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              {isVisible ? <FiEyeOff className="w-5 h-5" /> : <FiEye className="w-5 h-5" />}
            </motion.button>
          )}
          
          {/* Indicadores de validación */}
          <AnimatePresence>
            {touched[field] && !errors[field] && value && (
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0 }}
                className={`absolute inset-y-0 ${isPassword ? 'right-12' : 'right-4'} flex items-center`}
              >
                <FiCheckCircle className="w-5 h-5 text-emerald-500" />
              </motion.div>
            )}
            {errors[field] && (
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0 }}
                className={`absolute inset-y-0 ${isPassword ? 'right-12' : 'right-4'} flex items-center`}
              >
                <FiAlertCircle className="w-5 h-5 text-red-500" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        {/* Mensaje de error */}
        <AnimatePresence>
          {errors[field] && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-sm text-red-600 dark:text-red-400 flex items-center gap-2"
            >
              <FiAlertCircle className="w-4 h-4" />
              {errors[field]}
            </motion.p>
          )}
        </AnimatePresence>
      </motion.div>
    )
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
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-100 dark:from-gray-900 dark:via-indigo-900/20 dark:to-purple-900/20">
      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-40 -right-40 w-96 h-96 rounded-full"
          style={{
            background: 'linear-gradient(135deg, rgba(147, 51, 234, 0.4) 0%, rgba(168, 85, 247, 0.3) 50%, rgba(236, 72, 153, 0.2) 100%)',
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
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-purple-300/30 rounded-full"
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
        {success ? (
          // Pantalla de éxito
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center p-12 rounded-3xl bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl border border-white/50 dark:border-gray-700/50 shadow-2xl"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-6"
            >
              <HiShieldCheck className="w-10 h-10 text-white" />
            </motion.div>
            <h2 className="text-3xl font-black text-gray-900 dark:text-white mb-4">
              ¡Contraseña restablecida!
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Tu contraseña ha sido actualizada correctamente. Te redirigiremos al login en unos segundos.
            </p>
            <motion.div
              className="w-12 h-12 border-4 border-emerald-200 dark:border-emerald-700 border-t-emerald-600 dark:border-t-emerald-400 rounded-full mx-auto"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            />
          </motion.div>
        ) : (
          // Formulario principal
          <>
            {/* Logo / Título flotante */}
            <motion.div
              animate={floatingAnimation}
              className="text-center mb-8"
            >
              <motion.div
                className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-700 shadow-xl mb-4 relative overflow-hidden"
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <HiShieldCheck className="w-8 h-8 text-white" />
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
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-3xl font-black text-gray-900 dark:text-white mb-2"
              >
                Restablecer Contraseña
              </motion.h1>
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="text-gray-600 dark:text-gray-300 text-sm"
              >
                Crea una nueva contraseña segura para tu cuenta
              </motion.p>
            </motion.div>

            {/* Formulario */}
            <form onSubmit={handleSubmit} className="relative">
              <div className="relative p-8 rounded-3xl bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl border border-white/50 dark:border-gray-700/50 shadow-2xl overflow-hidden">
                {/* Efectos de fondo del formulario */}
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/5 via-purple-600/5 to-transparent dark:from-indigo-400/10 dark:via-purple-400/10" />
                
                <div className="relative z-10 space-y-6">
                  <FormField
                    icon={FiMail}
                    label="Correo electrónico"
                    field="email"
                    type="email"
                    placeholder="tu.email@ejemplo.com"
                  />
                  
                  <FormField
                    icon={FiKey}
                    label="Código de verificación"
                    field="code"
                    placeholder="Ingresa el código recibido"
                  />
                  
                  <FormField
                    icon={FiLock}
                    label="Nueva contraseña"
                    field="password"
                    placeholder="Crea una contraseña segura"
                    isPassword={true}
                    showPasswordToggle={showPassword}
                  />
                  
                  <FormField
                    icon={FiShield}
                    label="Confirmar contraseña"
                    field="confirm"
                    placeholder="Confirma tu nueva contraseña"
                    isPassword={true}
                    showPasswordToggle={showConfirm}
                  />

                  {/* Indicador de seguridad de contraseña */}
                  <AnimatePresence>
                    {password && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="p-4 rounded-2xl bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600"
                      >
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                          Requisitos de contraseña:
                        </p>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          {[
                            { check: password.length >= 10, label: 'Mín. 10 caracteres' },
                            { check: /[A-Z]/.test(password), label: 'Mayúscula' },
                            { check: /[a-z]/.test(password), label: 'Minúscula' },
                            { check: /[0-9]/.test(password), label: 'Número' },
                            { check: /[!@#$%^&*(),.?":{}|<>]/.test(password), label: 'Símbolo especial' },
                            { check: password === confirm && confirm, label: 'Coinciden' }
                          ].map((req, idx) => (
                            <motion.div
                              key={idx}
                              initial={{ opacity: 0, scale: 0.9 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: idx * 0.1 }}
                              className={`flex items-center gap-2 ${
                                req.check ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-400 dark:text-gray-500'
                              }`}
                            >
                              {req.check ? (
                                <FiCheckCircle className="w-3 h-3" />
                              ) : (
                                <div className="w-3 h-3 rounded-full border border-current" />
                              )}
                              <span>{req.label}</span>
                            </motion.div>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Error global */}
                  <AnimatePresence>
                    {globalError && (
                      <motion.div
                        initial={{ opacity: 0, y: -10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -10, scale: 0.95 }}
                        className="p-4 rounded-2xl bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm font-medium flex items-center gap-3"
                      >
                        <FiAlertCircle className="w-5 h-5 flex-shrink-0" />
                        <span>{globalError}</span>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Botón de envío */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                  >
                    <motion.button
                      type="submit"
                      disabled={loading}
                      className="relative w-full py-4 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white font-bold text-lg shadow-xl overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
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
                            Restableciendo...
                          </>
                        ) : (
                          <>
                            <FiRefreshCw className="w-5 h-5" />
                            Restablecer Contraseña
                            <motion.div
                              className="group-hover:translate-x-1 transition-transform duration-200"
                            >
                              <FiArrowRight className="w-4 h-4" />
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
                    className="text-center"
                  >
                    <motion.a
                      href="/login"
                      className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors duration-200 inline-flex items-center gap-2"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Volver al login
                    </motion.a>
                  </motion.div>
                </div>
              </div>
            </form>
          </>
        )}
      </motion.div>
    </div>
  )
}