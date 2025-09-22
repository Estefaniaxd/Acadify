import { useState, ChangeEvent, FormEvent, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import axios from 'axios'
import formatApiError from '../../utils/formatApiError'
import { useNavigate } from 'react-router-dom'

export default function ResetPassword() {
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const navigate = useNavigate()

  function validate() {
    if (!email || !code || !password || !confirm) return 'Todos los campos son obligatorios.'
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return 'Email inválido.'
    // Reglas del backend: >=10, 1 may, 1 min, 1 dígito, 1 especial
    if (password.length < 10) return 'La contraseña debe tener al menos 10 caracteres.'
    const hasUpper = /[A-Z]/.test(password)
    const hasLower = /[a-z]/.test(password)
    const hasDigit = /[0-9]/.test(password)
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password)
    if (!hasUpper || !hasLower || !hasDigit || !hasSpecial) return 'La contraseña debe contener mayúscula, minúscula, número y carácter especial.'
    if (password !== confirm) return 'Las contraseñas no coinciden.'
    // Puedes agregar validaciones de seguridad aquí
    return ''
  }

  // Prefill desde query params
  const location = useLocation()
  useEffect(() => {
    const qp = new URLSearchParams(location.search)
    const correo = qp.get('correo_institucional')
    const codigo = qp.get('reset_code')
    if (correo) setEmail(correo)
    if (codigo) setCode(codigo)
  }, [location.search])

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const err = validate()
    if (err) return setError(err)
    setError('')
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
          headers: {
            'Content-Type': 'application/json'
          }
        }
      )
      setSuccess(true)
      setTimeout(() => navigate('/login'), 2000)
    } catch (err: any) {
      if (err.response && err.response.data) {
        setError(formatApiError(err.response.data))
      } else {
        setError('Error al restablecer la contraseña. Intenta de nuevo.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-8 bg-white dark:bg-[#0b0b0b] rounded-lg shadow w-full max-w-md mx-auto">
      <h2 className="text-2xl font-semibold text-primary mb-4">Restablecer contraseña</h2>
      {success ? (
        <div className="text-green-600 text-sm mb-4">Contraseña restablecida correctamente. Redirigiendo al login...</div>
      ) : (
        <>
          <div className="mb-4">
            <label className="block text-sm mb-1" htmlFor="email">Email</label>
            <input id="email" type="email" autoComplete="username" className="w-full px-3 py-2 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]" value={email} onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)} required />
          </div>
          <div className="mb-4">
            <label className="block text-sm mb-1" htmlFor="code">Código recibido</label>
            <input id="code" type="text" className="w-full px-3 py-2 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]" value={code} onChange={(e: ChangeEvent<HTMLInputElement>) => setCode(e.target.value)} required />
          </div>
          <div className="mb-4">
            <label className="block text-sm mb-1" htmlFor="password">Nueva contraseña</label>
            <div className="relative">
              <input id="password" type={showPassword ? 'text' : 'password'} autoComplete="new-password" className="w-full px-3 py-2 pr-10 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]" value={password} onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)} required />
              <button type="button" className="absolute inset-y-0 right-0 pr-3 flex items-center" tabIndex={-1} onClick={() => setShowPassword(v => !v)}>
                {showPassword ? (
                  <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" /></svg>
                ) : (
                  <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268-2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                )}
              </button>
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-sm mb-1" htmlFor="confirm">Confirmar contraseña</label>
            <div className="relative">
              <input id="confirm" type={showConfirm ? 'text' : 'password'} autoComplete="new-password" className="w-full px-3 py-2 pr-10 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]" value={confirm} onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirm(e.target.value)} required />
              <button type="button" className="absolute inset-y-0 right-0 pr-3 flex items-center" tabIndex={-1} onClick={() => setShowConfirm(v => !v)}>
                {showConfirm ? (
                  <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" /></svg>
                ) : (
                  <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268-2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                )}
              </button>
            </div>
          </div>
          {error && <div className="mb-3 text-red-600 text-sm">{error}</div>}
          <button type="submit" className="w-full py-2 rounded bg-primary text-white font-semibold hover:bg-primary/90 transition-colors" disabled={loading}>
            {loading ? 'Restableciendo...' : 'Restablecer contraseña'}
          </button>
        </>
      )}
    </form>
  )
}
