import React, { useState, ChangeEvent, FormEvent } from 'react'
import axios from 'axios'
import { useAuth } from '../../context/AuthContext'
import formatApiError from '../../utils/formatApiError'


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

  return (
    <section className="min-h-screen flex items-center justify-center bg-gradient-to-br from-white via-[#f3f0ff] to-[#f7f7fb] dark:from-[#18181b] dark:via-[#18181b] dark:to-black py-12">
      <form onSubmit={handleSubmit} className="w-full max-w-md mx-auto p-10 rounded-3xl shadow-2xl bg-white/90 dark:bg-[#18181b]/90 border border-gray-100 dark:border-gray-800 backdrop-blur-xl flex flex-col gap-6">
        <h2 className="text-3xl font-extrabold text-primary dark:text-purple-200 mb-2 text-center">Iniciar sesión</h2>
        <p className="text-gray-600 dark:text-gray-400 text-center mb-2 text-sm">Accede a tu cuenta para continuar aprendiendo y jugando.</p>
        <div>
          <label className="block text-sm mb-1 font-semibold text-gray-700 dark:text-gray-200" htmlFor="identifier">Usuario o Email</label>
          <input
            id="identifier"
            type="text"
            autoComplete="username"
            className={`w-full px-4 py-3 rounded-lg border-2 focus:ring-2 text-lg bg-white dark:bg-[#23232b] text-gray-800 dark:text-gray-100 border-primary/30 dark:border-purple-400/30 focus:outline-none focus:ring-primary/40 ${touched.identifier && !identifier ? 'border-red-400' : ''}`}
            value={identifier}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setIdentifier(e.target.value)}
            onBlur={() => setTouched({ ...touched, identifier: true })}
            required
            placeholder="Tu usuario o correo electrónico"
          />
        </div>
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
          Acepto el <a href="/privacidad" className="underline text-primary dark:text-purple-300 ml-1" target="_blank" rel="noopener noreferrer">tratamiento de datos</a>
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
