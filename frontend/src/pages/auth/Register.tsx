import { useState, ChangeEvent, FormEvent } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import formatApiError from '../../utils/formatApiError'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, ArrowLeft, ArrowRight, CheckCircle, CreditCard, Eye, EyeOff, FileText, GraduationCap, Lock, Mail, Shield, Sparkles, User, Users } from "lucide-react";;



interface FormData {
  rol: string
  email: string
  nombres: string
  apellidos: string
  tipoDocumento: string
  numeroDocumento: string
  username: string
  password: string
  confirm: string
}

interface ValidationErrors {
  [key: string]: string
}

// Componente de campo personalizado fuera del componente principal
const FormField = ({
  icon: Icon,
  label,
  field,
  type = 'text',
  placeholder,
  options,
  isPassword = false,
  formData,
  errors,
  focusedField,
  showPassword,
  showConfirm,
  updateField,
  setFocusedField,
  setTouched,
  setShowPassword,
  setShowConfirm
}: {
  icon: any
  label: string
  field: keyof FormData
  type?: string
  placeholder: string
  options?: { value: string; label: string }[]
  isPassword?: boolean
  formData: FormData
  errors: ValidationErrors
  focusedField: string | null
  showPassword: boolean
  showConfirm: boolean
  updateField: (field: keyof FormData, value: string) => void
  setFocusedField: (field: string | null) => void
  setTouched: (fn: (prev: { [key: string]: boolean }) => { [key: string]: boolean }) => void
  setShowPassword: (show: boolean) => void
  setShowConfirm: (show: boolean) => void
}) => {
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    updateField(field, e.target.value)
  }

  const handleFocus = () => {
    setFocusedField(field)
  }

  const handleBlur = () => {
    setFocusedField(null)
    setTouched(prev => ({ ...prev, [field]: true }))
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-2"
    >
      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
        {label} <span className="text-red-500">*</span>
      </label>
      <div className="relative group">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <motion.div
            animate={{
              color: focusedField === field ? '#8b5cf6' : '#9ca3af'
            }}
            transition={{ duration: 0.2 }}
          >
            <Icon className="w-5 h-5" />
          </motion.div>
        </div>

        {options ? (
          <select
            className={`w-full pl-12 pr-4 py-4 rounded-2xl border-2 text-gray-800 dark:text-gray-100 bg-gray-50/80 dark:bg-gray-700/80 backdrop-blur-sm transition-all duration-300 focus:outline-none focus:ring-0 ${focusedField === field
              ? 'border-violet-500 bg-white dark:bg-gray-700 shadow-lg shadow-violet-500/20'
              : errors[field]
                ? 'border-red-400 bg-red-50 dark:bg-red-900/20'
                : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
              }`}
            value={formData[field]}
            onChange={handleInputChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
          >
            <option value="">{placeholder}</option>
            {options.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        ) : (
          <input
            type={isPassword ? (field === 'password' ? (showPassword ? 'text' : 'password') : (showConfirm ? 'text' : 'password')) : type}
            className={`w-full pl-12 ${isPassword ? 'pr-12' : 'pr-4'} py-4 rounded-2xl border-2 text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 bg-gray-50/80 dark:bg-gray-700/80 backdrop-blur-sm transition-all duration-300 focus:outline-none focus:ring-0 ${focusedField === field
              ? 'border-violet-500 bg-white dark:bg-gray-700 shadow-lg shadow-violet-500/20'
              : errors[field]
                ? 'border-red-400 bg-red-50 dark:bg-red-900/20'
                : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
              }`}
            value={formData[field]}
            onChange={handleInputChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder={placeholder}
          />
        )}

        {isPassword && (
          <motion.button
            type="button"
            className="absolute inset-y-0 right-4 flex items-center text-gray-400 hover:text-violet-600 transition-colors duration-200"
            onClick={() => field === 'password' ? setShowPassword(!showPassword) : setShowConfirm(!showConfirm)}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            {(field === 'password' ? showPassword : showConfirm) ?
              <EyeOff className="w-5 h-5" /> :
              <Eye className="w-5 h-5" />
            }
          </motion.button>
        )}

        {/* Indicadores de validación */}
        <AnimatePresence>
          {formData[field] && !errors[field] && (
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
              className={`absolute inset-y-0 ${isPassword ? 'right-12' : 'right-4'} flex items-center`}
            >
              <CheckCircle className="w-5 h-5 text-emerald-500" />
            </motion.div>
          )}
          {errors[field] && (
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
              className={`absolute inset-y-0 ${isPassword ? 'right-12' : 'right-4'} flex items-center`}
            >
              <AlertCircle className="w-5 h-5 text-red-500" />
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
            <AlertCircle className="w-4 h-4" />
            {errors[field]}
          </motion.p>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function Register() {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState<FormData>({
    rol: 'estudiante',
    email: '',
    nombres: '',
    apellidos: '',
    tipoDocumento: '',
    numeroDocumento: '',
    username: '',
    password: '',
    confirm: ''
  })
  const [errors, setErrors] = useState<ValidationErrors>({})
  const [globalError, setGlobalError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [success, setSuccess] = useState(false)
  const [focusedField, setFocusedField] = useState<string | null>(null)
  const [touched, setTouched] = useState<{ [key: string]: boolean }>({})
  const navigate = useNavigate()

  const totalSteps = 3

  // Validaciones en tiempo real
  const validateField = (field: string, value: string): string => {
    switch (field) {
      case 'nombres':
        return value.length < 2 ? 'El nombre debe tener al menos 2 caracteres' : ''
      case 'apellidos':
        return value.length < 2 ? 'Los apellidos deben tener al menos 2 caracteres' : ''
      case 'email':
        return !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value) ? 'Email inválido' : ''
      case 'username':
        return value.length < 3 ? 'El usuario debe tener al menos 3 caracteres' : ''
      case 'numeroDocumento':
        return value.length < 6 ? 'Número de documento inválido' : ''
      case 'password':
        if (value.length < 6) return 'La contraseña debe tener al menos 6 caracteres'
        return ''
      case 'confirm':
        return value !== formData.password ? 'Las contraseñas no coinciden' : ''
      case 'tipoDocumento':
        return !value ? 'Selecciona un tipo de documento' : ''
      default:
        return ''
    }
  }

  const updateField = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))

    // Validar en tiempo real solo si el campo no está vacío
    if (value.trim()) {
      const error = validateField(field, value)
      setErrors(prev => ({ ...prev, [field]: error }))
    } else {
      // Limpiar errores si el campo está vacío
      setErrors(prev => ({ ...prev, [field]: '' }))
    }

    // Si es confirmar contraseña, también validar cuando cambie la contraseña
    if (field === 'password' && formData.confirm) {
      const confirmError = validateField('confirm', formData.confirm)
      setErrors(prev => ({ ...prev, confirm: confirmError }))
    }
  }

  const validateStep = (stepNumber: number): boolean => {
    const stepErrors: ValidationErrors = {}

    switch (stepNumber) {
      case 1:
        if (!formData.nombres) stepErrors.nombres = 'Los nombres son obligatorios'
        else stepErrors.nombres = validateField('nombres', formData.nombres)

        if (!formData.apellidos) stepErrors.apellidos = 'Los apellidos son obligatorios'
        else stepErrors.apellidos = validateField('apellidos', formData.apellidos)

        if (!formData.tipoDocumento) stepErrors.tipoDocumento = 'Selecciona un tipo de documento'
        if (!formData.numeroDocumento) stepErrors.numeroDocumento = 'El número de documento es obligatorio'
        else stepErrors.numeroDocumento = validateField('numeroDocumento', formData.numeroDocumento)
        break

      case 2:
        if (!formData.username) stepErrors.username = 'El usuario es obligatorio'
        else stepErrors.username = validateField('username', formData.username)

        if (!formData.email) stepErrors.email = 'El email es obligatorio'
        else stepErrors.email = validateField('email', formData.email)
        break

      case 3:
        if (!formData.password) stepErrors.password = 'La contraseña es obligatoria'
        else stepErrors.password = validateField('password', formData.password)

        if (!formData.confirm) stepErrors.confirm = 'Confirma tu contraseña'
        else stepErrors.confirm = validateField('confirm', formData.confirm)
        break
    }

    setErrors(stepErrors)
    return Object.values(stepErrors).every(error => !error)
  }

  const nextStep = () => {
    if (validateStep(step) && step < totalSteps) {
      setStep(step + 1)
    }
  }

  const prevStep = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!validateStep(3)) return

    setGlobalError('')
    setLoading(true)

    try {
      const payload = {
        username: formData.username,
        nombres: formData.nombres,
        apellidos: formData.apellidos,
        tipo_documento: formData.tipoDocumento,
        numero_documento: formData.numeroDocumento,
        password: formData.password,
        rol: formData.rol,
        correo_institucional: formData.email,
      }

      await axios.post('/auth/register', payload, {
        withCredentials: true,
        timeout: 10000,
        headers: { 'Content-Type': 'application/json' }
      })

      setSuccess(true)
      setTimeout(() => navigate('/login'), 3000)
    } catch (err: any) {
      if (err.response && err.response.data) {
        setGlobalError(formatApiError(err.response.data))
      } else {
        setGlobalError('Error al registrar. Intenta de nuevo.')
      }
    } finally {
      setLoading(false)
    }
  }

  // Componente de campo personalizado
  const renderFormField = (props: {
    icon: any
    label: string
    field: keyof FormData
    type?: string
    placeholder: string
    options?: { value: string; label: string }[]
    isPassword?: boolean
  }) => (
    <FormField
      {...props}
      formData={formData}
      errors={errors}
      focusedField={focusedField}
      showPassword={showPassword}
      showConfirm={showConfirm}
      updateField={updateField}
      setFocusedField={setFocusedField}
      setTouched={setTouched}
      setShowPassword={setShowPassword}
      setShowConfirm={setShowConfirm}
    />
  )

  return (
    <div className="min-h-screen w-full flex items-center justify-center relative overflow-hidden py-20 md:py-24">
      {/* Fondo de página completo */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-100 dark:from-neutral-950 dark:via-emerald-950/30 dark:to-teal-950/20" />

      {/* Elementos decorativos de fondo */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-40 -right-40 w-96 h-96 rounded-full"
          style={{
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.4) 0%, rgba(34, 197, 94, 0.3) 50%, rgba(59, 130, 246, 0.2) 100%)',
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
            background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.4) 0%, rgba(16, 185, 129, 0.3) 50%, rgba(34, 197, 94, 0.2) 100%)',
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
            className="absolute w-2 h-2 bg-emerald-300/30 rounded-full"
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
        className="relative z-10 w-full max-w-2xl mx-auto px-6"
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
              <CheckCircle className="w-10 h-10 text-white" />
            </motion.div>
            <h2 className="text-3xl font-black text-gray-900 dark:text-white mb-4">
              ¡Registro exitoso!
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Tu cuenta ha sido creada correctamente. Te redirigiremos al login en unos segundos.
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
            {/* Header con progreso */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-8"
            >
              <motion.div
                className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-700 shadow-xl mb-4 relative overflow-hidden"
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <GraduationCap className="w-8 h-8 text-white" />
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

              <h1 className="text-3xl font-black text-gray-900 dark:text-white mb-2">
                Únete a Acadify
              </h1>
              <p className="text-gray-600 dark:text-gray-300 text-sm mb-6">
                Crea tu cuenta y comienza tu aventura de aprendizaje
              </p>

              {/* Indicador de progreso */}
              <div className="flex items-center justify-center space-x-4 mb-4">
                {[1, 2, 3].map((stepNumber) => (
                  <div key={stepNumber} className="flex items-center">
                    <motion.div
                      className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all duration-300 ${stepNumber === step
                        ? 'bg-gradient-to-br from-emerald-600 to-teal-700 text-white shadow-lg'
                        : stepNumber < step
                          ? 'bg-emerald-600 text-white'
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                        }`}
                      animate={{ scale: stepNumber === step ? 1.1 : 1 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      {stepNumber < step ? <CheckCircle className="w-5 h-5" /> : stepNumber}
                    </motion.div>
                    {stepNumber < totalSteps && (
                      <div className={`w-12 h-1 mx-2 rounded-full transition-all duration-300 ${stepNumber < step ? 'bg-emerald-600' : 'bg-gray-200 dark:bg-gray-700'
                        }`} />
                    )}
                  </div>
                ))}
              </div>

              <p className="text-sm text-gray-500 dark:text-gray-400">
                Paso {step} de {totalSteps}
              </p>
            </motion.div>

            {/* Formulario */}
            <form onSubmit={handleSubmit} className="relative">
              <div className="relative p-8 rounded-3xl bg-white/95 dark:bg-neutral-900/95 backdrop-blur-2xl border-2 border-emerald-200/50 dark:border-emerald-800/50 shadow-2xl overflow-hidden">
                {/* Efectos de fondo del formulario */}
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-600/5 via-teal-600/5 to-transparent dark:from-emerald-400/5 dark:via-teal-400/5" />

                <div className="relative z-10">
                  <AnimatePresence mode="wait">
                    {/* Paso 1: Información Personal */}
                    {step === 1 && (
                      <motion.div
                        key="step1"
                        initial={{ opacity: 0, x: 50 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -50 }}
                        transition={{ duration: 0.5 }}
                        className="space-y-6"
                      >
                        <div className="text-center mb-6">
                          <User className="w-12 h-12 text-emerald-600 mx-auto mb-2" />
                          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                            Información Personal
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            Cuéntanos un poco sobre ti
                          </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {renderFormField({
                            icon: User,
                            label: "Nombres",
                            field: "nombres",
                            placeholder: "Ingresa tus nombres"
                          })}
                          {renderFormField({
                            icon: User,
                            label: "Apellidos",
                            field: "apellidos",
                            placeholder: "Ingresa tus apellidos"
                          })}
                          {renderFormField({
                            icon: FileText,
                            label: "Tipo de documento",
                            field: "tipoDocumento",
                            placeholder: "Selecciona...",
                            options: [
                              { value: 'cc', label: 'Cédula de ciudadanía (CC)' },
                              { value: 'ti', label: 'Tarjeta de identidad (TI)' },
                              { value: 'ce', label: 'Cédula de extranjería (CE)' }
                            ]
                          })}
                          {renderFormField({
                            icon: CreditCard,
                            label: "Número de documento",
                            field: "numeroDocumento",
                            placeholder: "Número de identificación"
                          })}
                        </div>

                        {/* Selector de rol */}
                        <div className="space-y-3">
                          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
                            ¿Cuál es tu rol?
                          </label>
                          <div className="grid grid-cols-2 gap-4">
                            {[
                              { value: 'estudiante', label: 'Estudiante', icon: GraduationCap, color: 'from-emerald-500 to-teal-600' },
                              { value: 'docente', label: 'Docente', icon: Users, color: 'from-violet-500 to-purple-600' }
                            ].map((rol) => (
                              <motion.button
                                key={rol.value}
                                type="button"
                                onClick={() => updateField('rol', rol.value)}
                                className={`relative p-4 rounded-2xl border-2 transition-all duration-300 ${formData.rol === rol.value
                                  ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
                                  : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                                  }`}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                              >
                                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${rol.color} flex items-center justify-center mx-auto mb-2`}>
                                  <rol.icon className="w-6 h-6 text-white" />
                                </div>
                                <p className="font-semibold text-gray-900 dark:text-white text-sm">
                                  {rol.label}
                                </p>
                                {formData.rol === rol.value && (
                                  <motion.div
                                    initial={{ opacity: 0, scale: 0 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="absolute top-2 right-2"
                                  >
                                    <CheckCircle className="w-5 h-5 text-emerald-600" />
                                  </motion.div>
                                )}
                              </motion.button>
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {/* Paso 2: Credenciales */}
                    {step === 2 && (
                      <motion.div
                        key="step2"
                        initial={{ opacity: 0, x: 50 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -50 }}
                        transition={{ duration: 0.5 }}
                        className="space-y-6"
                      >
                        <div className="text-center mb-6">
                          <CheckCircle className="w-12 h-12 text-emerald-600 mx-auto mb-2" />
                          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                            Credenciales de Acceso
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            Define cómo accederás a tu cuenta
                          </p>
                        </div>

                        <div className="space-y-6">
                          {renderFormField({
                            icon: User,
                            label: "Nombre de usuario",
                            field: "username",
                            placeholder: "Elige un nombre de usuario único"
                          })}
                          {renderFormField({
                            icon: Mail,
                            label: "Correo electrónico",
                            field: "email",
                            type: "email",
                            placeholder: "tu.email@ejemplo.com"
                          })}
                        </div>
                      </motion.div>
                    )}

                    {/* Paso 3: Contraseña */}
                    {step === 3 && (
                      <motion.div
                        key="step3"
                        initial={{ opacity: 0, x: 50 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -50 }}
                        transition={{ duration: 0.5 }}
                        className="space-y-6"
                      >
                        <div className="text-center mb-6">
                          <Shield className="w-12 h-12 text-emerald-600 mx-auto mb-2" />
                          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                            Protege tu Cuenta
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            Crea una contraseña segura para tu cuenta
                          </p>
                        </div>

                        <div className="space-y-6">
                          {renderFormField({
                            icon: Lock,
                            label: "Contraseña",
                            field: "password",
                            placeholder: "Crea una contraseña segura",
                            isPassword: true
                          })}
                          {renderFormField({
                            icon: Lock,
                            label: "Confirmar contraseña",
                            field: "confirm",
                            placeholder: "Confirma tu contraseña",
                            isPassword: true
                          })}
                        </div>

                        {/* Política de privacidad */}
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.3 }}
                          className="p-4 rounded-2xl bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600"
                        >
                          <label className="flex items-start gap-3 text-xs text-gray-600 dark:text-gray-400 cursor-pointer select-none">
                            <input
                              type="checkbox"
                              required
                              className="mt-1 w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500"
                            />
                            <span>
                              Acepto el{' '}
                              <a href="/legal/TratamientoDatos" className="text-emerald-600 dark:text-emerald-400 underline hover:text-emerald-700 dark:hover:text-emerald-300" target="_blank" rel="noopener noreferrer">
                                tratamiento de datos
                              </a>{' '}
                              y el{' '}
                              <a href="/legal/Consentimiento" className="text-emerald-600 dark:text-emerald-400 underline hover:text-emerald-700 dark:hover:text-emerald-300" target="_blank" rel="noopener noreferrer">
                                consentimiento informado
                              </a>
                            </span>
                          </label>
                        </motion.div>
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
                        className="mt-6 p-4 rounded-2xl bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm font-medium flex items-center gap-3"
                      >
                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                        <span>{globalError}</span>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Botones de navegación */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="flex items-center justify-between mt-8"
                  >
                    {step > 1 ? (
                      <motion.button
                        type="button"
                        onClick={prevStep}
                        className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <ArrowLeft className="w-4 h-4" />
                        Anterior
                      </motion.button>
                    ) : (
                      <div />
                    )}

                    {step < totalSteps ? (
                      <motion.button
                        type="button"
                        onClick={nextStep}
                        className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-700 text-white font-bold shadow-xl hover:shadow-2xl transition-all duration-300"
                        whileHover={{ scale: 1.02, y: -2 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        Siguiente
                        <ArrowRight className="w-4 h-4" />
                      </motion.button>
                    ) : (
                      <motion.button
                        type="submit"
                        disabled={loading}
                        className="relative flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 text-white font-bold text-lg shadow-xl overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
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
                          className="relative flex items-center gap-3"
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
                              Creando cuenta...
                            </>
                          ) : (
                            <>
                              <Sparkles className="w-5 h-5" />
                              Crear Cuenta
                            </>
                          )}
                        </motion.div>
                      </motion.button>
                    )}
                  </motion.div>

                  {/* Botón de Google OAuth */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5, duration: 0.6 }}
                    className="mt-6"
                  >
                    {/* Separador */}
                    <div className="relative flex items-center justify-center my-6">
                      <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-gray-300 dark:border-gray-600"></div>
                      </div>
                      <div className="relative px-4 bg-white dark:bg-neutral-900">
                        <span className="text-sm text-gray-500 dark:text-gray-400">O continúa con</span>
                      </div>
                    </div>

                    <motion.button
                      type="button"
                      onClick={() => {
                        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
                        window.location.href = `${apiUrl}/auth/google/login`;
                      }}
                      className="flex items-center justify-center gap-3 w-full px-4 py-3 rounded-2xl border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200 font-medium text-gray-700 dark:text-gray-200 shadow-sm hover:shadow-md"
                      whileHover={{ scale: 1.02, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <svg className="w-5 h-5" viewBox="0 0 24 24">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                      </svg>
                      Continuar con Google
                    </motion.button>
                  </motion.div>

                  {/* Enlaces adicionales */}
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6 }}
                    className="text-center mt-6"
                  >
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      ¿Ya tienes cuenta?{' '}
                      <motion.a
                        href="/login"
                        className="font-bold text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors duration-200"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        Inicia sesión aquí
                      </motion.a>
                    </p>
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