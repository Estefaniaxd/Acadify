import { useState, ChangeEvent, FormEvent } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import formatApiError from '../../utils/formatApiError'


export default function Register() {
  const [rol, setRol] = useState('estudiante') // Solo estudiante o docente
  const [email, setEmail] = useState('')
  const [nombres, setNombres] = useState('')
  const [apellidos, setApellidos] = useState('')
  const [tipoDocumento, setTipoDocumento] = useState('')
  const [numeroDocumento, setNumeroDocumento] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [success, setSuccess] = useState(false)
  const [lastAction, setLastAction] = useState('idle')
  const navigate = useNavigate();

  function validate() {
    if (!username || !nombres || !apellidos || !tipoDocumento || !numeroDocumento || !email || !password || !confirm) return 'Todos los campos son obligatorios.'
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return 'Email inválido.'
    if (password.length < 6) return 'La contraseña debe tener al menos 6 caracteres.'
    if (password !== confirm) return 'Las contraseñas no coinciden.'
    return ''
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const err = validate()
    if (err) return setError(err)
    setError('')
    setLoading(true)
    setLastAction('sending')
    try {
      const payload: any = {
        username,
        nombres,
        apellidos,
        tipo_documento: tipoDocumento,
        numero_documento: numeroDocumento,
        password,
        rol,
        correo_institucional: email,
      };
      console.log('Register payload:', payload)
      await axios.post(
        '/auth/register',
        payload,
        {
          withCredentials: true,
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      console.log('Register response received')
      setSuccess(true)
      setLastAction('sent')
      setTimeout(() => navigate('/login'), 2000)
    } catch (err: any) {
      console.error('Register error:', err)
      if (err.response && err.response.data) {
        setError(formatApiError(err.response.data))
      } else if (err.message) {
        setError(err.message)
      } else {
        setError('Error al registrar. Intenta de nuevo.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="min-h-screen flex flex-col justify-center p-10 bg-white dark:bg-[#0b0b0b] rounded-2xl shadow-lg w-full max-w-2xl mx-auto border border-gray-200 dark:border-gray-800">
      <h2 className="text-3xl font-bold text-primary mb-8 text-center">Registro</h2>
      {success ? (
        <div className="text-green-600 text-base mb-6 text-center">Registro exitoso. Redirigiendo al login...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="text-lg font-semibold mb-2 text-primary">Datos personales</h3>
              <div className="mb-4">
                <label className="block text-sm mb-1" htmlFor="nombres">Nombres</label>
                <input id="nombres" type="text" className="w-full px-3 py-2 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]" value={nombres} onChange={(e: ChangeEvent<HTMLInputElement>) => setNombres(e.target.value)} required />
              </div>
              <div className="mb-4">
                <label className="block text-sm mb-1" htmlFor="apellidos">Apellidos</label>
                <input id="apellidos" type="text" className="w-full px-3 py-2 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]" value={apellidos} onChange={(e: ChangeEvent<HTMLInputElement>) => setApellidos(e.target.value)} required />
              </div>
              <div className="mb-4">
                <label className="block text-sm mb-1" htmlFor="tipo_documento">Tipo de documento</label>
                <select
                  id="tipo_documento"
                  className="w-full px-3 py-2 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]"
                  value={tipoDocumento}
                  onChange={e => setTipoDocumento(e.target.value)}
                  required
                >
                  <option value="">Selecciona...</option>
                  <option value="cc">Cédula de ciudadanía (cc)</option>
                  <option value="ti">Tarjeta de identidad (ti)</option>
                  <option value="ce">Cédula de extranjería (ce)</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm mb-1" htmlFor="numero_documento">Número de documento</label>
                <input id="numero_documento" type="text" className="w-full px-3 py-2 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]" value={numeroDocumento} onChange={(e: ChangeEvent<HTMLInputElement>) => setNumeroDocumento(e.target.value)} required />
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2 text-primary">Datos de acceso</h3>
              <div className="mb-4">
                <label className="block text-sm mb-1" htmlFor="username">Nombre de usuario</label>
                <input id="username" type="text" className="w-full px-3 py-2 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]" value={username} onChange={(e: ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)} required />
              </div>
              <div className="mb-4">
                <label className="block text-sm mb-1" htmlFor="rol">Rol</label>
                <select id="rol" className="w-full px-3 py-2 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]" value={rol} onChange={e => setRol(e.target.value)}>
                  <option value="estudiante">Estudiante</option>
                  <option value="docente">Docente</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm mb-1" htmlFor="email">Email</label>
                <input id="email" type="email" autoComplete="username" className="w-full px-3 py-2 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]" value={email} onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)} required />
              </div>
              <div className="mb-4">
                <label className="block text-sm mb-1" htmlFor="password">Contraseña</label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    className="w-full px-3 py-2 pr-10 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]"
                    value={password}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    tabIndex={-1}
                    onClick={() => setShowPassword(v => !v)}
                  >
                    {showPassword ? (
                      <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268-2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
              <div className="mb-4">
                <label className="block text-sm mb-1" htmlFor="confirm">Confirmar contraseña</label>
                <div className="relative">
                  <input
                    id="confirm"
                    type={showConfirm ? 'text' : 'password'}
                    autoComplete="new-password"
                    className="w-full px-3 py-2 pr-10 rounded border focus:outline-primary bg-gray-50 dark:bg-[#18181b]"
                    value={confirm}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirm(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    tabIndex={-1}
                    onClick={() => setShowConfirm(v => !v)}
                  >
                    {showConfirm ? (
                      <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268-2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
          {error && <div className="mb-3 text-red-600 text-base text-center">{error}</div>}
          <label className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 cursor-pointer select-none mt-2">
            <input type="checkbox" required className="accent-primary w-4 h-4 rounded" />
            Acepto el <a href="/legal/TratamientoDatos" className="underline text-primary dark:text-purple-300 ml-1" target="_blank" rel="noopener noreferrer">tratamiento de datos</a> y el <a href="/legal/Consentimiento" className="underline text-primary dark:text-purple-300 ml-1" target="_blank" rel="noopener noreferrer">consentimiento informado</a>
          </label>
          <div className="text-xs text-gray-500 mt-2 text-center">debug: {lastAction}</div>
          <button type="submit" className="w-full py-3 rounded-lg bg-primary text-white text-lg font-semibold hover:bg-primary/90 transition-colors mt-4" disabled={loading}>
            {loading ? 'Registrando...' : 'Registrarse'}
          </button>
        </>
      )}
    </form>
  )
}
